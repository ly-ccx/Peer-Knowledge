# 62. Automation Runtime 与持久化边界

创建时间：2026-08-04

状态：Accepted

级别：A 级（新增长期调度、持久化、独立权限、后台执行与 Evidence 契约）

关联：

- `design/product/automation-scheduled-agent-product-design.md`
- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/decisions/16-skill-call-lifecycle.md`
- `knowledge/decisions/21-pending-task-resume.md`
- `knowledge/decisions/27-workspace-switch-and-cross-workspace-running.md`

## 背景

Automation 不是定时向 Renderer 注入一条聊天消息。它需要在窗口关闭后持续调度，在重启与唤醒后恢复，保存每次 Run 的事实快照，并在无人值守时仍遵守：

```text
Capability Provider
  -> Manifest
    -> Runtime Projection
      -> Tool Call
        -> PermissionGrant
          -> Evidence
```

若 Scheduler、授权或 Run 状态由 Renderer 持有，窗口销毁会丢失事实；若 Automation 另建工具执行路径，则会绕过 Runtime Projection、PermissionGrant 与 Evidence。

## 决策

### 1. 领域对象

跨层契约由 `@peer-agent/protocol` 的 `automation.ts` 定义：

- `AutomationDefinition`：长期、可版本化的调度定义；
- `AutomationSchedule`：结构化规则与 IANA 时区；
- `AutomationGrant`：独立于 Conversation access level 的长期授权上限；
- `AutomationRun`：一次触发的不可复用执行事实；
- `AutomationRunSnapshot`：Run 创建时冻结的 Definition/Grant/模型/工作区事实；
- `AutomationRunReceipt`：结果、Evidence、Diff、验证与用量；
- IPC input/result/event：Renderer 只通过协议对象访问领域服务。

Definition 与 Run 分离。修改 Definition 不得修改已创建 Run；Run 继续使用自己的快照。

### 2. 进程职责

#### Desktop 主进程

拥有：

- Automation Definition 与 Run 持久化；
- `nextRunAt` 计算与幂等 reconciliation；
- 应用启动、电脑唤醒、系统时间变化后的恢复；
- 全局暂停、并发和连续失败策略；
- Fresh Conversation 创建；
- Automation Grant 到现有 permission gate 的映射；
- Worktree 生命周期；
- Run Receipt、Attention 和通知发布。

#### Renderer

只拥有：

- Automation Center、创建/编辑/确认、Overview/Runs/Receipt 表达；
- 用户输入草稿；
- 对 IPC 结果的临时查询和筛选状态；
- 通过结构化命令请求 create/update/pause/run/cancel/retry/approve。

Renderer 不直接使用 `fs`、`child_process`、Git 或计时器作为调度事实。

#### Protocol

拥有跨层类型、状态枚举、输入输出和事件形状。Electron transport channel 名由 Desktop channel catalog 管理，但 payload/result 必须引用 Protocol。

### 3. 持久化

统一数据根仍为 `~/.peer-agent/`，通过 `DATA_STORE_ENTRIES` 注册：

```text
automations/definitions.json
automations/runs/<runId>.json
automations/runtime.json
automations/worktrees/<runId>/...
```

其中：

- Definition 为 portable 业务配置，但路径、设备授权与 runtime 状态是 device-bound；
- P0 为避免把设备路径和长期授权错误导出，整个 Automation store 先按 device scope 注册；
- 后续跨设备同步必须增加显式的 portable projection，不直接复制当前目录；
- 所有 JSON 使用 schema version、原子写与损坏隔离；
- `automationId + scheduledAt` 是计划触发幂等键。

### 4. Scheduler

Scheduler 是主进程 Module，不以长 `setTimeout` 作为唯一事实源。Store 中的 `nextRunAt` 与已消费幂等键是事实；timer 只是唤醒优化。

每次启动、唤醒、时间变化和定义更新都执行 reconciliation：

1. 读取 active Definition；
2. 根据时区和 Schedule 计算计划点；
3. 应用 missed policy；
4. 检查幂等键和 overlap；
5. 原子创建 Run；
6. 更新下一次运行。

P0 missed 默认 `run_latest`，overlap 默认 `skip`，不回放全部积压。

### 5. Runner

Automation Runner 是现有 Chat/Goal Runtime 的调用方，不是新的 Agent Runtime：

1. 创建绑定目标 workspace 的 Fresh Conversation；
2. 将 Automation Run binding 作为治理上下文传入；
3. 复用 `llmChatService.sendMessage` 与 provider encoder；
4. 工具仍经 Runtime Projection、local tool host、permission gate 和 Evidence；
5. Run 订阅流终态并投影 Receipt；
6. Conversation 后续人工消息不反写已终结 Receipt。

### 6. 权限

Automation Grant 不继承创建会话的 `full_local` 或一次性审批。

P0：

- `observe`：自动允许受治理的读取能力；写操作进入 deny/ask；
- `work_in_workspace`：只在本 Run Worktree 内允许本地写和测试构建；
- 外部写、push/merge/deploy、特权和破坏性操作不自动允许；
- `Allow once` 只生成当前 Run、当前 tool call 的 PermissionGrant；
- 扩大未来授权必须更新 Definition 并重新确认。

权限事实保存在主进程 Store，Renderer 状态不是真相源。

### 7. Worktree

Git 写入 Run 使用单独 Worktree Adapter。Runner 只依赖小接口：

```text
prepare(run) -> executionWorkspace
collect(run) -> diff/evidence
retainOrCleanup(run)
apply(run) -> explicit user action
```

Adapter 负责调用 Git。不得在 Scheduler、Renderer 或 Chat Runtime 添加 `capabilityId`/Git 分支特判。

### 8. Attention 与通知

Automation Run 的 waiting/failed/completed 事件投影到既有 Attention/notification 语义，复用 `attentionVersion` 和阅读回执。系统通知只负责提醒；Run Store 是事实源。

点击回流携带 `automationId + runId`，等待输入时再携带 `conversationId`。

### 9. IPC

Automation IPC 由独立 `register-automation-ipc.mjs` 所有，通过统一 `register-all` 生命周期注册和清理。通道加入 canonical channel catalog 并限制为 main window。

禁止：

- 在 `main.mjs` 散落多个 `ipcMain.handle('automation:*')`；
- Renderer 拼装持久化记录；
- 用 assistant 文本冒充 Run 完成或 Evidence；
- 为 Automation 另建直接 shell/file/MCP 执行路径。

## 失败与恢复

- Store 写入失败：不创建不可追踪 Run；
- Conversation 创建失败：Run 进入 blocked/failed 并保存原因；
- 主进程重启时 running Run：根据活动流重附着；无法重附着则标记 interrupted，不伪造 succeeded；
- Workspace/credential/capability 失效：preflight blocked，用户修复后创建新 Retry Run；
- 有变更的失败/取消 Worktree：保留到用户明确处理。

## 后果

正面：

- 窗口关闭不会丢失调度事实；
- 所有本地能力仍经过统一权限与 Evidence 链；
- Definition、Run、Conversation 和 Receipt 边界可审计；
- UI、Scheduler、Runner、Worktree 可分别测试和替换。

代价：

- P0 需要独立 Store、Scheduler、Runner、Worktree Adapter 和 IPC Module；
- 需要处理重启、唤醒、流重附着和损坏恢复；
- 不能通过 Renderer timer + 自动发送消息快速拼接。

## 验收

- Protocol 类型检查通过；
- Automation store 在统一 data root 注册；
- IPC 归独立 owner 且通过 caller policy；
- 定时与手动 Run 使用同一 Runner；
- 工具调用仍产生 PermissionGrant 与 Evidence；
- 修改 Definition 不改变旧 Run；
- Renderer 无本地执行与权限真相。
