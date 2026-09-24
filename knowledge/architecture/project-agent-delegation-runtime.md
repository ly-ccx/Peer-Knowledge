# 项目代理委托运行时

创建时间：2026-09-24
最后更新：2026-09-24

> 状态：Draft（随 ADR 80 评审）  
> 级别：A 级运行时契约  
> 关联决策：`knowledge/decisions/80-project-agent-delegation-model.md`  
> 关联产品稿：`design/product/project-agent-workbench.md`  
> 关联文档：
> - `knowledge/architecture/20-architecture-governance.md`
> - `knowledge/architecture/19-system-prompt-context-architecture.md`
> - `knowledge/decisions/35-mode-scoped-tool-projection.md`
> - `design/product/goal-mode-multi-agent-orchestration-plan.md`
> - `knowledge/architecture/task-lifecycle-and-acceptance-flow.md`

---

## 0. 一句话

项目代理是一条常驻 Conversation，以 `project_agent` 模式运行，只拿到只读工具和调度工具；它开出的任务是子 Conversation + GoalPlan，由现有 Goal Runner 推进；任务的状态变化以结构化事件回到项目代理的收件箱，由 `ProjectAgentRunner` 唤醒代理跑一轮。

---

## 1. 运行主体与深度

| 主体 | 载体 | 生命周期 | 能力 | 能开什么 |
|---|---|---|---|---|
| 项目代理 | Conversation，`role: 'project_agent'`，每个 Workspace 一条 | 常驻，随项目存在 | 只读 + 调度（§4） | 任务；只读临时子 agent |
| 任务 | Conversation，`role: 'work_session'`，`parentConversationId` 指向项目代理 | 从开出到验收 / 取消；验收后仍可追问 | 现有 Goal 模式工具集，受 PermissionGrant 约束 | 任务内临时子 agent（Explorer / Verifier） |
| 临时子 agent | 无持久 Conversation（`ephemeral: true`，与现有 Explorer 一致） | 一次运行 | 按 profile，默认只读 | 不能开任何东西 |

深度限制由调度 Provider 在执行层校验：调用方 Conversation 的 `role` 不是 `project_agent` 时，`spawn_session` 返回结构化 `depth_limit` 失败。模式投影层也不会把调度工具投影给 `work_session` 与临时子 agent。两层都拦，不依赖 prompt。

---

## 2. 协议对象

落点：`packages/protocol/src/delegation.ts`。以下是形状草案，字段名以实现评审为准。

```ts
type WorkSessionStatus =
  | 'starting'        // Conversation 已建，GoalPlan 尚未持久化
  | 'awaiting_approval' // 计划待用户批准
  | 'running'
  | 'needs_user'      // 权限 / 决策 / 补充信息
  | 'result_ready'    // 机器完成，待验收
  | 'accepted'        // 用户已验收（resultAcceptance 已写）
  | 'cancelled'
  | 'failed';

interface WorkSession {
  sessionId: string;            // = 子 conversationId
  projectAgentConversationId: string;
  workspacePath: string;
  title: string;                // = 当前 GoalPlan.title
  planId: string | null;
  status: WorkSessionStatus;    // 投影值，真源是 GoalPlan + 权限队列
  spawnedAt: string;
  spawnedByToolCallId: string;  // 项目代理那次 spawn_session 的 Tool Call
  isolation: 'none' | 'worktree';
}

interface SessionReport {
  sessionId: string;
  planId: string | null;
  status: WorkSessionStatus;
  summary: string;              // 任务侧生成的摘要，只是说明，不是证据
  evidenceRefs: string[];       // 必须能在 EvidenceIndex / 计划持有引用里解析
  criteriaProgress: { passed: number; total: number };
  needsUser?: {
    kind: 'permission' | 'decision' | 'plan_approval' | 'input';
    pendingRequestId: string;   // 指向 main 里已有的待处理请求，不复制一份
    prompt: string;
  };
  failureReason?: string;
}

type DelegationEvent =
  | { type: 'session_spawned'; session: WorkSession }
  | { type: 'session_progress'; sessionId: string; report: SessionReport }
  | { type: 'session_needs_user'; sessionId: string; report: SessionReport }
  | { type: 'session_result_ready'; sessionId: string; report: SessionReport }
  | { type: 'session_ended'; sessionId: string; report: SessionReport }
  | { type: 'user_intervened'; sessionId: string; messageId: string };
```

不变量：

1. `WorkSession.status` 是投影，不单独持久化；由 GoalPlan 状态、`resultAcceptance`、权限待处理队列计算。计算函数放在 protocol，与 `projectGoalPlan` 同层，便于 Desktop / TUI 共用。
2. `SessionReport.summary` 只能以 Tool Result 或事件事实进入项目代理上下文，不能进入 `L0`–`L6`。
3. `needsUser.pendingRequestId` 引用的是同一个待处理请求。无论用户在代理对话还是任务里批准，解决的都是同一条请求。

---

## 3. 调度能力

新增 `LocalDelegationProvider`，放在 `apps/desktop/electron/main/runtime-gateway/local-delegation-provider.mjs`，参照 `local-goal-provider.mjs`。纯逻辑（校验、事件映射、深度限制）下沉到 `packages/runtime-node`，TUI 共用。

| 工具 | capabilityId（草案） | 作用 | 副作用与授权 |
|---|---|---|---|
| `spawn_session` | `local.delegation.spawn_session` | 开任务：建子 Conversation，写入首条用户意图，走现有 intake 创建 GoalPlan | 只创建会话与计划，不执行本地能力；按 `goal-create` 同类处理，self-grant，记 Evidence |
| `message_session` | `local.delegation.message_session` | 给任务追加指令或纠偏，作为该任务里的一条用户侧消息，标注来源为项目代理 | 同上 |
| `cancel_session` | `local.delegation.cancel_session` | 取消任务：停 Runner，GoalPlan 进 `cancelled` | 不删分支 / worktree；删除仍走现有二次确认 |
| `list_sessions` | `local.delegation.list_sessions` | 列出本项目任务与投影状态 | 只读 |
| `get_session_report` | `local.delegation.get_session_report` | 取一条任务的 `SessionReport` | 只读 |
| `spawn_subagent` | `local.delegation.spawn_subagent` | 开只读临时调研子 agent，复用 Explorer 执行路径，结果作为 Tool Result 返回 | 只读 profile；预算受 §5 约束 |

`spawn_session` 输入：

```ts
{
  title: string;
  goal: string;                  // 交给任务的完整意图
  successCriteria: string[];     // 可为空，但产品上要求代理尽量给出
  boundaries?: string[];
  requiresApproval: boolean;     // true → 计划先进用户批准卡
  isolation?: 'auto' | 'none' | 'worktree'; // auto：已有其他写仓库任务在跑时用 worktree
  contextRefs?: string[];        // 代理已读过的文件 / 调研报告引用，交给任务作为事实上下文
}
```

用户提问复用现有 `request_user_input`（`local.interaction.request_user_input`），不新增 `ask_user`。

---

## 4. `project_agent` 模式投影

按 ADR 35 的机制新增 `project_agent` 模式，与 `explorer` 一样是**严格白名单**：只有显式声明 `availableInModes` 含 `project_agent` 的工具才会投影。

白名单：

- 只读：`list_files`、`read_file`、`search_files`、`goal_get_plan`
- 调度：§3 全部
- 交互：`request_user_input`
- 可选只读网页：`batch_search` / `web_fetch`，需要评审是否把外网读取算作代理职责

明确不投影：`edit_file`、`write_file`、`bash`、`goal_create_plan`、`goal_update_task`、`request_explorer`、有副作用的 MCP / 浏览器 / 桌面控制 / Automation 提案。

执行层兜底：`permission-gate` 对 `project_agent` 模式下的任何写类 `permissionPolicy.kind` 直接拒绝并记 Evidence，防止投影配置漂移。

---

## 5. `ProjectAgentRunner`

落点：`packages/runtime-node/src/project-agent-runner.mjs`，Desktop 与 TUI 共用。它对项目代理的作用，相当于 Goal Runner 对单个 GoalPlan 的作用。

### 5.1 收件箱与唤醒

```text
任务侧事实变化（GoalPlan store 变更 / 权限队列变化 / Runner 终态）
  → DelegationEventMapper 映射成 DelegationEvent
  → 写入该项目代理的收件箱（持久化，重启可恢复）
  → ProjectAgentRunner 判断是否唤醒
      · 用户正在和代理对话、代理回合进行中 → 只入箱，本轮结束后再处理
      · 空闲 → 合并去抖窗口内的事件，唤醒代理跑一轮
  → 代理本轮看到收件箱快照（§7 roster source），决定：
      汇报用户 / 继续调度 / 向用户提问 / 什么都不说
```

唤醒规则：

| 事件 | 是否唤醒 | 说明 |
|---|---|---|
| `session_needs_user` | 立即 | 代理把卡片递给用户，可附带自己的判断 |
| `session_result_ready` | 立即 | 代理汇报结果，附验收卡 |
| `session_ended`（failed / cancelled） | 立即 | 代理决定重试、换方案或告诉用户 |
| `session_progress` | 不单独唤醒 | 只更新 roster 快照；长时间无进展由 §5.3 处理 |
| `user_intervened` | 不唤醒 | 下次代理回合时作为事实可见 |

代理被唤醒的回合不伪造用户消息：触发内容作为 runtime reminder + roster 快照注入，写入代理对话的是代理自己的助手消息与卡片。

### 5.2 并发与预算

- 每个项目并发运行的任务上限默认 3，可配置，硬上限 6。
- 两条以上会写仓库的任务同时运行时，后开的任务强制 `isolation: 'worktree'`（复用改造阶段 D 的隔离路径）；主工作区脏时拒绝开出并返回结构化原因。
- 代理自发唤醒（非用户触发）有频率上限，防止事件风暴烧 token。
- 项目代理的 `spawn_subagent` 共享 Explorer 的并发配额与预算。

### 5.3 停滞检测

任务在 `running` 下超过阈值没有新的叶子 Evidence 或状态变化，Runner 产生一条合成的停滞事件唤醒代理。代理可以 `message_session` 纠偏或告诉用户。复用现有 `blockerAudit` 指纹，不另起一套。

### 5.4 取消与恢复

- 用户取消项目代理的当前回合，不影响任务继续运行。
- 应用重启：收件箱持久化；任务由现有 Goal Runner 恢复逻辑（ADR 73 中断 ≠ 失败）接管；项目代理在下次空闲时处理积压事件。

---

## 6. 权限冒泡

```text
任务内 Tool Call 需要授权
  → 现有 permission-review 产生待处理请求（真源在 main）
  → 任务对话照常出现权限卡
  → DelegationEventMapper 产生 session_needs_user（pendingRequestId 指向同一请求）
  → 项目代理对话渲染同一请求的卡片
  → 用户在任一处批准 / 拒绝 → 同一请求被解决 → 两处卡片同步收起
```

规则：

1. 项目代理不能批准、拒绝或改写任何权限请求。调度工具没有这类参数。
2. 任务的授权上限不超过用户对该项目已授予的范围；`spawn_session` 不接受任何扩大权限的参数。
3. 计划批准（`requiresApproval: true`）走同一路径，`kind: 'plan_approval'`，批准对象是任务的 GoalPlan。
4. 远程 / 手机入口批准时同样解决同一请求，不另开通道。

---

## 7. Evidence

- 每次调度 Tool Call 产出 Evidence：谁（项目代理对话）、何时、开了 / 改了 / 取消了哪条任务、带了什么意图。
- `SessionReport.evidenceRefs` 必须可解析；不可解析的引用在报告里标 `unresolved`，代理与界面都不能把它当证据。
- 项目代理的助手消息不是证据。验收卡只读任务 GoalPlan 的关闭闸门结果。
- 临时子 agent 的报告沿用 Explorer 的 `allowedEvidenceRefs` 校验。

---

## 8. System Context

| 来源 | 层 | 内容 | 注入条件 |
|---|---|---|---|
| `project-agent-source` | `L1_AGENT` | 角色契约：只读 + 调度；什么时候直接回答、什么时候开任务；不替用户做判断；汇报必须引用任务报告 | `mode === 'project_agent'` |
| `project-roster-source` | `L7_CONTINUITY` | 本项目任务快照：标题、投影状态、需要你项、最近报告摘要、收件箱积压 | 同上；只注入快照，不注入任务全文 |
| `project-memory-source` | `L7_CONTINUITY` | 项目级长期记忆（分期 P4） | 同上；未验证的经验不进入 |
| 现有 `project-instructions-source` | `L3_INSTRUCTIONS` | 项目 AGENTS.md 等 | 不变 |

任务侧：`spawn_session` 的 `goal` / `boundaries` 作为该任务首条用户意图与 GoalPlan 字段进入，不作为系统指令；`contextRefs` 作为附件类事实上下文。

项目代理对话常驻，压缩必须可用：复用现有 compaction 管线，roster 快照每轮重新生成，不进压缩摘要。

---

## 9. 存储

| 数据 | 落点 | 说明 |
|---|---|---|
| 项目代理 Conversation | conversation-store，`role: 'project_agent'` | 每个 Workspace 最多一条；懒创建 |
| 项目代理 id | Workspace 设置 `projectAgentConversationId` | 找不到时重建，不猜 |
| 任务 Conversation | conversation-store，`role: 'work_session'` + `parentConversationId` | 复用划词子会话已有的父子字段形态 |
| 收件箱 | `~/.peer-agent` 下按项目的 JSONL | 只存事件引用，不复制报告正文 |
| GoalPlan / Evidence | 不变 | |

`role` 缺省视为历史会话：迁移时不改写，界面归为该项目的「历史任务」。

---

## 10. IPC 与 Renderer 投影

- 新增 `delegation:list` / `delegation:changed`，payload 是 `WorkSession[]`，由 main 聚合；renderer 不自行扫描 GoalPlan 判断状态。
- `taskOverview` 聚合增加按项目分组与 `projectAgentConversationId`，用于侧栏角标。
- 卡片（开出任务 / 需要你 / 待验收）绑定 `sessionId` 与 `pendingRequestId`，交互调用已有的批准 / 验收 IPC，不新增绕过 main 的动作。

---

## 11. 与现有模块的关系

| 现有模块 | 用法 |
|---|---|
| `runtime-node` `createGoalRunner` | 原样作为任务的执行引擎 |
| Explorer / Verifier（`main.mjs` `explorerRunner` / `verifierRunner`） | 原样留在任务内；`spawn_subagent` 复用 Explorer 执行路径 |
| `local-goal-provider` | 任务内不变；`spawn_session` 通过 intake 路径创建 GoalPlan，不在调度 Provider 里复制计划逻辑 |
| `permission-review` | 真源不变，只新增事件映射 |
| conversation-store 划词子会话 | 父子字段形态复用 |
| 阶段 D worktree 隔离 | 并行写仓库任务复用 |
| `task-overview-aggregator` | 增加项目维度 |
| `remote-access` | 远程入口对接项目代理对话 |

`main.mjs` 已超过四千行，项目代理的组合逻辑放在独立的 `project-agent-application-service.mjs`，`main.mjs` 只做装配。

---

## 12. 测试清单

- `project_agent` 模式只投影白名单工具；写类工具不可见；执行层兜底拒绝写类调用。
- `work_session` 调 `spawn_session` 返回 `depth_limit`；临时子 agent 看不到调度工具。
- `spawn_session` 创建子 Conversation、父子关系、GoalPlan；`requiresApproval` 时进入 `awaiting_approval`。
- 并行写仓库任务第二条起强制 worktree；主工作区脏时拒绝。
- 任务权限请求产生 `session_needs_user`，两处批准解决同一请求。
- 代理没有任何批准权限的入口。
- `session_result_ready` 唤醒代理；代理文本不影响 `resultAcceptance`。
- 收件箱持久化，重启后积压事件被处理且不重复汇报。
- 停滞检测产生唤醒；唤醒频率上限生效。
- 用户直接在任务里发消息产生 `user_intervened`，任务 Goal 生命周期不受代理干扰。
- 历史会话（无 `role`）迁移后可见且不被改写。

---

## 13. 未决问题

1. 项目代理是否允许只读网页（`batch_search` / `web_fetch`）。
2. 项目代理与任务是否默认用不同模型（代理用快模型）。需要看 Provider 绑定是否支持按 `role` 取默认。
3. 纯问答超出只读工具能力时（例如需要跑一次测试才能回答），是开一条轻量任务，还是让代理回答「需要开任务」并请用户确认。
4. TUI 的呈现：TUI 是否也以项目代理为默认对话，还是保留直接任务入口。
