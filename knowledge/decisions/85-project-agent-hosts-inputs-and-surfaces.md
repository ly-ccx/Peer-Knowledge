# 85. 项目代理的宿主、输入与多入口（0.1.0 落地边界）

创建时间：2026-09-26
最后更新：2026-09-26（P0-2 评审通过）

## 状态

Accepted（2026-09-26，P0-2）。实现未开工。四项选择维持：受管文件夹 `~/Peer/<名字>/`；远程可看、可发消息，批准只在电脑上；桌面与 TUI 用宿主租约；未归属旧会话进「我 → 历史对话」。

时限按本文执行，不另开一轮：租约心跳 5 秒、20 秒未心跳视为失效；同一项目的事件 2 秒合并成一次唤醒；`stale` 批准不自动重放，用户点「批准并继续」后只对同一 `capabilityId + argsDigest` 放行一次，30 分钟内有效。

## 级别

A 级。新增跨进程运行边界（宿主租约、持久输入队列、持久待批准），改变系统通知的来源、后台任务的工具投影与远程入口的能力范围，并修订 ADR 80 / 81 / 84 中与代码现状不符的落地条款。

## 关联

- `knowledge/decisions/80-project-agent-delegation-model.md`（项目代理、任务、签收、送达）
- `knowledge/decisions/81-project-agent-memory-system.md`（`workspaceId`、记忆存储）
- `knowledge/decisions/84-bot-list-shell.md`（机器人列表壳、受管文件夹）
- `knowledge/decisions/74-deployment-surfaces-and-local-storage.md`（部署面与本机存储）
- ADR 75（远程只读预检；知识库中缺少该 ADR 文件，代码侧为 `packages/protocol/src/remote-access.ts`、`apps/gateway/src/remote-task-router.mjs`，规格见 `design/product/remote-access-simple-implementation.md` 与 `playbook/remote-access-handoff.md`）
- `knowledge/decisions/71-l2-playwright-external-browser.md`、`70-l1-browser-action-surface.md`
- `knowledge/decisions/73-goal-interruption-suspension-vs-failure.md`
- `design/product/v0.1.0-release-plan.md`（0.1.0 版本计划）

## 背景（2026-09-26 在 `main` a087988c 上核对的代码事实）

| 事实 | 位置 |
|---|---|
| 桌面与 TUI 共用 `~/.peer-agent/goal-plans`，各自有 Goal Runner，没有任何跨进程锁或租约 | `packages/runtime-node/src/goal-plan-store.mjs`、`apps/tui/src/goal-runner-adapter.ts` |
| 待处理权限只存在主进程内存里（`pendingPermissionRequests`），请求只发给发起回合的那个 `webContents`；重启即丢；`reattach()` 快照不含待处理权限 | `apps/desktop/electron/main/chat-runtime/permission-gate.mjs`、`llm-chat-service.mjs` |
| Automation 的权限策略从不询问：未预授权的一律拒绝 | `permission-gate.mjs` `automationCapabilityDecision` |
| Explorer / Verifier 用内存收集器当 `webContents`；遇到需要询问的权限时，请求发进收集器、无人应答，回合会挂住 | `main.mjs` `createCollectingWebContents()` |
| 内嵌浏览器操控（L1）驱动的是用户眼前 Workbench 面板里的 `<webview>`，依赖渲染进程上报 `webContentsId` | `runtime-gateway/local-browser-control-provider.mjs` |
| 任务完成系统通知按 GoalPlan 状态跃迁触发（completed / failed / waiting_user / interrupted） | `task-notification-policy.mjs`、`task-notification-broker.mjs` |
| 工作区以绝对路径为主键，条目只有 `{ path, name, addedAt, linkedFolders }`；任何写回都会按这四个字段重新规范化，丢掉未知字段 | `workspace-application-service.mjs` |
| 远程访问里已经有 `workspaceId`：手工配置的字符串，作为远程委托白名单 | `remote-access-controller.mjs`、`packages/protocol/src/remote-access.ts` |
| 远程能力只有只读的 `task.read`（读 GoalPlan） | `apps/gateway/src/remote-task-router.mjs`、`runtime-gateway/remote-goal-read.mjs` |
| 首启会自动创建 `~/PeerAgent` 并注册为默认工作区 | `main.mjs` `getDefaultWorkspacePath`、`workspace-application-service.mjs` |
| 设置没有 schema 版本与迁移机制，只有顶层浅合并 | `settings-store.mjs` |
| Electron 41 自带 Node 24.15，`node:sqlite` 可用且支持 FTS5 trigram（中文子串检索通过）；Bun 1.4.2 同样支持 `node:sqlite` + FTS5 | 本机实测 |

## 决策

1. **每个项目一个宿主租约。** 租约文件 `project-runtime/<workspaceId>/host.lease`（`DATA_STORE_ENTRIES.projectRuntime`，scope：device），内容 `{ hostId, surface: 'desktop' | 'tui', pid, appVersion, acquiredAt, heartbeatAt }`。
   - 获取：独占创建临时文件后原子改名；已有租约且心跳未过期（默认 20 秒）则获取失败。持有方每 5 秒刷新心跳。
   - 只有持有租约的一方运行该项目的 `ProjectAgentRunner`、`SessionSupervisor`、`ExecutionScheduler`、`WatchRunner`，以及属于该项目任务（`role: work_session`）的 Goal Runner 推进。普通会话（非任务）的 Goal 不受影响。
   - 两端的 Goal Runner 都通过 `canRunPlan` 检查：任务计划只在持有租约时推进。
   - 不抢占：持有方正常退出时释放；心跳过期视为失效，另一方可以接手，并按「重启恢复」顺序（分层文档 §7.6）恢复。用户可以在非持有端执行显式「接管」，持有方在下一次心跳时让出。
2. **所有入口的用户输入走持久输入队列。** 桌面界面、快捷对话、TUI、远程入口提交给机器人的消息，一律写成 `ProjectInput { inputId, workspaceId, surface, text, anchorRefs, quoteRefs, attachmentRefs, createdAt }`，追加到 `project-runtime/<workspaceId>/input-queue.jsonl`。
   - 只有宿主消费：按顺序把输入写入机器人对话（用户消息），唤醒代理回合，推进游标。`inputId` 幂等，重复提交不产生两条消息。
   - 非宿主端通过会话存储的变更通知读取结果，不直接写机器人对话。
   - 桌面界面也走这条路（IPC → main → 输入队列），不另开「界面直接写对话」的通道。
3. **待批准项持久化。** 任务里需要用户批准的请求写成 `PendingApproval { approvalId, workspaceId, sessionId, planId, toolCallId, streamId, capabilityId, summary, riskLevel, argsDigest, createdAt, state }`，存 `project-runtime/<workspaceId>/approvals.jsonl`。
   - 执行仍由内存中的 permission-gate 负责；持久记录是事实与展示来源。
   - 回合所在的流已经不在（重启、崩溃、中断）时，记录转为 `stale`；用户批准 `stale` 项时，按 ADR 73 恢复该任务，并附带只对同一 `capabilityId + argsDigest` 生效一次的授权。
   - 0.1.0 只接受本机决策：桌面主进程与作为宿主的本机 TUI。远程入口只显示「需要在电脑上批准」。
   - Explorer / Verifier 等没有审批人的临时回合：遇到需要询问的权限时立即拒绝，原因 `ephemeral_no_approver`，不再挂起。
4. **系统通知只来自送达策略。** 机器人模式下，任务的 GoalPlan 状态跃迁不再直接触发系统通知（`task-notification-broker` 跳过 `role: work_session` 的计划）；系统通知只在 `decideSurfacing` 判定为 `interrupt` 时发出。托盘角标等于所有机器人「需要你」之和。
5. **后台任务不投影内嵌浏览器。** `work_session` 回合的工具投影排除 L1 内嵌浏览器操控（它依赖可见的 Workbench `<webview>`），需要浏览器时使用 L2 外部浏览器（ADR 71）。桌面预览截图与视觉复核在主进程执行，保留。L1 只用于前台的经典会话。
6. **`workspaceId` 是唯一的项目身份，本机与远程共用。**
   - 真源是 `projects/registry.json`（`DATA_STORE_ENTRIES.projects`，scope：portable）：`[{ workspaceId, path, createdAt, previousPaths[] }]`。`settings.workspaces[].id` 只是缓存。
   - 读取时缺 id：先按 path 在注册表里找，找不到才生成。这样旧版本写回设置丢掉 id 之后，再升级也能拿回原来的 id。
   - 远程委托的 `workspaceIds` 就是本机 `workspaceId`。旧的手工远程 `workspaceId` 字符串保留为该工作区的 `remoteAlias`，远程请求同时接受 id 与 alias，新配置只写 id。
7. **机器人数据不写进 `settings.workspaces`。** 机器人档案存 `projects/<workspaceId>/profile.json`：`{ displayName, avatar, managed, agentConversationId, proactivity, modelPolicy, createdAt, updatedAt }`。修订 ADR 84「后果」中「工作区条目增加 `displayName` / `avatar` / `managed`」的表述，原因是决策 6 所述的写回丢字段。
8. **远程入口（0.1.0 范围）。** 在 ADR 75 的预检链上新增四种操作：`project.list`、`project.conversation.read`（分页）、`project.session.read`、`project.input.submit`（纯文本，≤ 4000 字，不带附件）。
   - 委托新增能力位 `allowProjectRead`、`allowProjectMessage`，默认关闭，在桌面「远程」设置里按机器人勾选。
   - 远程消息进入决策 2 的输入队列，`surface: 'remote'`，并写入由此派生任务的 `DelegationOrigin.surface`，便于追溯。
   - 网关仍然只中转：不持有事实、不排队、不重放；设备离线时直接返回 `DEVICE_OFFLINE`。
9. **TUI 入口。** 在已绑定机器人的文件夹里运行 `peer`，默认打开该机器人的对话；`peer bots` 与 `/bots` 列出机器人；当前目录没有机器人时提示绑定。租约空闲时 TUI 作为宿主运行，否则作为客户端。
10. **首启与迁移（修订 ADR 84）。**
    - 受管文件夹根目录保持 `~/Peer/`（可配置）。
    - 机器人模式下首启不再自动创建 `~/PeerAgent`。已存在的 `~/PeerAgent` 工作区按普通「绑定已有文件夹」迁移为机器人。
    - 有工作区的旧会话进入对应机器人档案 → 任务 → 历史对话；没有工作区的旧会话进入「我 → 历史对话」。历史对话只读，原文件不改写。
    - 「交给机器人继续」：以该历史对话为背景快照（复用划词子会话的继承背景机制），由选定机器人开一条任务。
    - 设置中保留「经典界面」开关，贯穿 0.1.x，最早在 0.2.0 移除。
11. **降级兼容。** 0.1.0 只新增字段与文件，不改写旧会话 jsonl；设置迁移前备份；0.0.18 读取 0.1.0 写过的数据不能崩溃（有测试证明）。降级后再升级，项目身份、记忆与目标不丢（依赖决策 6）。

## 被修订的条款

| 原条款 | 修订 |
|---|---|
| ADR 84 后果：工作区条目增加 `displayName`、`avatar`、`managed` | 改为 `projects/<workspaceId>/profile.json`（决策 7） |
| ADR 84 决策 6：受管文件夹 `~/Peer/<名字>/` | 保留；补充首启不再自动建 `~/PeerAgent`（决策 10） |
| ADR 81 决策 12：稳定 `workspaceId` | 保留；真源为注册表，与远程委托共用（决策 6） |
| ADR 81：记忆索引用 SQLite FTS5 | 保留；确定用运行时自带的 `node:sqlite`（Electron 与 Bun 均可用），不新增原生依赖，中文检索用 trigram 分词 |
| ADR 80：需要你冒泡（运行时契约 §6） | 补充持久待批准与 `stale` 恢复（决策 3） |
| ADR 80 决策 9：送达策略 | 补充系统通知的唯一来源（决策 4） |
| 旧落地计划第 5 阶段：TUI 与远程入口接入 | 纳入 0.1.0，范围按决策 8、9 |

## 后果

- 新增存储：`projects/`（portable）、`project-runtime/`（device）；都要登记 `DATA_STORE_ENTRIES`。
- Goal Runner 的 `canRunPlan` 成为租约检查点；桌面与 TUI 都要接。
- 输入队列让「谁在运行」与「从哪里说话」解耦：远程、TUI、快捷对话复用同一条路径，不需要各写一套。
- 持久待批准让「需要你」在重启后仍然存在，代价是批准 `stale` 项要走一次任务恢复。
- 远程入口第一次有写操作（发消息），但写的只是「说一句话」；执行、授权、证据仍在本机。

## 不做什么

- 不做远程批准、远程附件、网关离线排队。
- 不做两端同时运行同一项目，也不静默抢占租约（心跳过期除外）。
- 不把机器人档案或记忆写进 `settings.json`。
- 不在后台任务里驱动用户眼前的内嵌浏览器。
