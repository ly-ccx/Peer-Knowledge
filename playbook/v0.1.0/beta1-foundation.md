# beta.1 地基（`0.1.0-beta.1`）

创建时间：2026-09-26
最后更新：2026-09-26

> 主题：执行不依赖窗口、待批准不丢、项目有稳定身份、模型按角色分工；为项目代理准备契约与基座。  
> 用户可见：关窗后台任务照跑；重启后中断的待批准任务可以继续；「模型分工」设置；视觉复核自动选能看图的模型。  
> 开关：本版新增开发者开关 `developer.projectAgentMode`（默认关），但不挂任何行为。  
> 通用退出条件见 `README.md` §6。

并行关系：

```text
串行（同改执行路径 / main.mjs）：B1-01 → B1-02 → B1-03 → B1-04 → B1-09 → B1-10
可并行：B1-05 → B1-06（B1-03 依赖 B1-06）；B1-07；B1-08；B1-11（依赖 B1-05）；B1-12
```

---

## B1-01 TurnSink 与 CollectingSink

- **级别**：B（纯重构，行为不变）。**规模**：S。**依赖**：P0-1。
- **目标**：把「回合事件接收体」从鸭子类型的 `webContents` 收拢成显式契约，Explorer / Verifier 先迁过去。
- **必读**：分层文档 §3（L1 执行宿主）。
- **代码锚点**：
  - `apps/desktop/electron/main/main.mjs` `createCollectingWebContents()`（约 1036–1060），被 `runExplorer`（约 1384–1427）、`runVerifier`（约 1429–1474）使用。
  - `apps/desktop/electron/main/llm-chat-service.mjs` `wrapWebContentsForRuntimeEvents`（约 462 起）：adapter / loop 只调用 `send`。
  - `apps/desktop/electron/main/automation-runner.mjs` `createBackgroundWebContents()`（4–11）。
- **允许改动**：新建 `apps/desktop/electron/main/agent-host/turn-sinks.mjs` 与 `turn-sinks.test.mjs`；`main.mjs`（删函数、改 import 与调用）；`automation-runner.mjs`（改用 `createCallbackSink`，行为不变）。
- **不许改动**：`llm-chat-service.mjs`、`chat-runtime/*`、`packages/runtime-node`。
- **实现要点**：
  - `TurnSink` 契约（写成 JSDoc typedef）：必须有 `send(channel, payload)`；可选 `isDestroyed()`（缺省视为 `false`）。调用方不得依赖 `id`、`on`、`session` 等 Electron 专有成员。
  - `createCollectingSink()`：与原 `createCollectingWebContents()` 行为逐字一致——收集事件、累积 `chat:stream:delta` 的 `content`、识别 `chat:stream:done / error / aborted` 为终态；提供 `getText()`、`getEvents()`（返回副本）、`getTerminal()`。
  - `createCallbackSink(onEvent)`：等价于 automation 的 `createBackgroundWebContents`，`isDestroyed()` 恒为 `false`。
- **必须新增的测试**：`turn-sinks.test.mjs`：文本累积；三种终态识别；`getEvents` 返回副本；callback sink 转发事件；`isDestroyed` 缺省。
- **退出条件**：`main.mjs` 净减行；`goal-runner*.test.mjs`、`automation-runner.test.mjs`、`desktop-host-visual-review.test.mjs` 与桌面端完整测试通过。

---

## B1-02 BroadcastSink、AgentTurnExecutor、无窗口推进、`turnProfile`、脚本化回合执行器

- **级别**：B（执行路径变化，需写架构影响）。**规模**：M。**依赖**：B1-01。
- **目标**：Goal 回合不再依赖主窗口；所有后台回合经同一个执行器；为后续测试提供不调用真实模型的脚本化执行器。
- **必读**：分层文档 §3.1、§3.3；ADR 22（流重连）；ADR 85 背景。
- **代码锚点**：
  - `main.mjs` `getRunnerWebContents()`（880）、`window-routing.mjs` `getMainWindowWebContents`；`runGoalTurn`（1287–1381，无窗口时返回 `blocked: 'No renderer window is available for Goal Runner'`）；`broadcastToAllWindows()`（547–878 簇内）。
  - `llm-chat-service.mjs` `sendMessage`（1062–1098，23 个参数）；`activeStreams`（61）；`streamRecord` 创建处（约 1231）。
- **允许改动**：`agent-host/turn-sinks.mjs`（加 BroadcastSink）；新建 `agent-host/agent-turn-executor.mjs` 与测试；新建 `packages/runtime-node/src/testing/scripted-turn-executor.mjs` 与测试（并在 runtime-node 的包导出里加 `./testing` 子路径）；`main.mjs`（只改调用）；`llm-chat-service.mjs`（只加 `turnProfile` 参数并写入 streamRecord）；`window-routing.mjs`（若 `getRunnerWebContents` 不再被使用则删除对应导出与测试）。
- **不许改动**：provider loop、`tool-orchestrator.mjs`、`permission-gate.mjs`（B1-03 负责）。
- **实现要点**：
  - `createBroadcastSink({ getWindows })`：把事件发给所有未销毁的受信任主窗口；没有窗口时丢弃。事实已在 streamRecord（文本、segments）与会话持久化里，窗口打开后按 ADR 22 `reattach` 认领。
  - `createAgentTurnExecutor({ llmChatService })` 暴露 `runTurn({ turnProfile, sink, ...sendMessageArgs })`：内部只做参数整理后调用 `sendMessage`，返回原 outcome。Goal 回合用 BroadcastSink；Explorer / Verifier 用 CollectingSink。
  - `runGoalTurn` 删除「没有窗口就 blocked」分支。
  - `turnProfile`：`sendMessage` 新增的**唯一**参数，形状 `{ role, workspaceId?, sessionId?, modelSelection? }`；本卡只使用 `role`，取值 `'user_chat' | 'goal_runner' | 'explorer' | 'verifier' | 'visual_verifier' | 'automation'`（后续卡追加 `'project_agent' | 'work_session' | 'memory_curator' | 'objective_probe'`）。写入 `streamRecord.turnProfile`，`listActiveStreams` 投影里带 `role`。
  - `createScriptedTurnExecutor(script)`：与 `AgentTurnExecutor.runTurn` 同签名；按脚本逐轮返回文本 delta、工具调用（经注入的 `executeTool` 回调执行，真实走 Provider 链时由测试自己接）、终态；用于 runtime-node 与主进程的集成测试。
- **必须新增的测试**：
  - 没有任何窗口时 Goal Runner 完成一轮（注入空窗口列表）；有窗口时所有窗口都收到事件。
  - `turnProfile.role` 写入 streamRecord 并出现在 `listActiveStreams`。
  - 脚本化执行器：多轮、工具调用、三种终态。
- **退出条件**：上述测试通过；Goal / Explorer / Verifier / Automation 回归全绿；交接报告附「架构影响」（执行路径不再依赖窗口；`sendMessage` 新参数）。

---

## B1-03 待批准持久化与重连

- **级别**：A（ADR 85 决策 3）。**规模**：M。**依赖**：B1-02、B1-06。
- **目标**：需要用户批准的请求有持久记录；窗口重开能恢复权限卡；重启后中断的请求不再无声消失；没有审批人的临时回合不再挂住。
- **必读**：ADR 85 决策 3；ADR 73（中断挂起）；运行时契约 §6。
- **代码锚点**：
  - `chat-runtime/permission-gate.mjs`：`pendingPermissionRequests`（288）、`registerPendingPermission`、三处 `webContents.send('chat:stream:permission-request', …)`（365 / 408 / 471）、`settlePermissionRequest`、`settleStreamPermissionRequests`；`automationCapabilityDecision`（269）。
  - `llm-chat-service.mjs` `reattach()`（1967–2014）、`abort()`（1931）、`resolvePermissionGrant`。
  - `ipc/register-chat-ipc.mjs` 的 `chat:stream:reattach`、`chat:stream:list-active`；`ipc/register-settings-ipc.mjs` 的 `permission:approve / deny`（52–53）。
  - 渲染层：`chat/hooks/useConversationStreamRouter.ts`（`permission-request` 路由）、`chat/state/conversationStore.ts`（`pendingPermission`）、`ChatSurface.tsx` 约 1540 的 `chatStreamReattach` 调用、`preload/contracts/bootstrapPreloadApi.ts`（155–188）。
  - `packages/runtime-node/src/goal-runner.mjs` 的中断 / 恢复（`resume()` 1555–1609）。
- **允许改动**：
  - 新建 `packages/runtime-node/src/project-agent/approval-store.mjs` 与测试（本卡先做通用部分，按 `workspaceId` 分文件；没有 `workspaceId` 的会话写 `project-runtime/_unscoped/approvals.jsonl`）。
  - `packages/runtime-node/src/data-store.mjs`：登记 `projectRuntime`（`project-runtime/`，scope：device）。
  - `permission-gate.mjs`：注册 / 结算时写持久记录；新增 `listPendingPermissions({ streamId?, conversationId? })`；settle 事件广播给所有窗口；识别「无审批人」的 sink。
  - `llm-chat-service.mjs`：`reattach()` 快照增加 `pendingPermissions`。
  - `agent-host/turn-sinks.mjs`：CollectingSink 标记 `approver: 'none'`。
  - `main.mjs`（只改装配：启动时调用 `approvalStore.markStaleOnStartup()`，并把受影响的 GoalPlan 标为中断）。
  - 渲染层：流路由与 conversationStore 中恢复权限卡的逻辑及其测试；`bootstrapPreloadApi.ts` 类型。
- **不许改动**：`ChatSurface.tsx` 的功能代码（只允许在已有 reattach 回调里多读一个字段，若必须改动超过 10 行，停下提交边界变更请求）；provider loop。
- **实现要点**：
  - 记录形状 `PendingApproval`（类型由 B1-07 定义；B1-07 未合入时先在本卡本地 JSDoc 定义，合入后改为引用）：`approvalId`（= 权限请求的 `toolCallId`）、`workspaceId | null`、`conversationId`、`streamId`、`planId | null`、`capabilityId`、`summary`（沿用 permission call 的展示文本，经脱敏）、`riskLevel`、`argsDigest`（参数的 sha256）、`createdAt`、`state: 'open' | 'approved' | 'denied' | 'expired' | 'stale'`、`decidedAt?`、`decidedBy?: 'local_ui' | 'policy'`。
  - 追加写（jsonl，一行一个状态变化），读取时按 `approvalId` 折叠为最新状态；文件超过 5 MB 时压缩为只含 open / stale 的快照。
  - `reattach()` 快照：`pendingPermissions: [{ toolCallId, streamId, call }]`，只含 `open`。
  - 所有窗口都收到 `chat:stream:permission-settled`；任一窗口批准都生效（已有 IPC 不变）。
  - CollectingSink（`approver: 'none'`）的回合遇到需要询问的权限：立即拒绝，原因 `ephemeral_no_approver`，并写入 Evidence 可见的拒绝原因；不注册 pending。
  - 启动时：所有 `open` 记录转 `stale`；对应 GoalPlan 若仍处于执行中，按 ADR 73 标为 `interrupted`，中断原因 `approval_interrupted`；用户用已有的「继续」恢复后，回合重新发起工具调用，会再次询问（一次性授权直接批准 `stale` 项留给 B3-01）。
  - 普通会话（无 GoalPlan）的 `stale` 记录只标记，不做恢复。
- **必须新增的测试**：
  - approval-store：追加 / 折叠 / 压缩 / 启动转 stale / 重复写幂等。
  - `reattach` 快照包含待处理权限，结算后消失。
  - 两个窗口都收到 `permission-settled`；从另一个窗口批准有效。
  - CollectingSink 回合遇到询问立即拒绝，回合不挂起（给超时断言）。
  - 启动时 open → stale，对应 GoalPlan 变为 `interrupted` 且原因正确。
  - 渲染层：由快照恢复权限卡（纯函数测试）。
- **退出条件**：测试通过；手动验证：让 Goal 任务停在权限请求上 → 关窗 → 重开窗，权限卡还在；强退应用 → 重开，该任务显示为中断、可以继续。交接报告附架构影响（新存储、IPC 快照扩展）。

---

## B1-04 Goal Runner 装配移出 `main.mjs`

- **级别**：B（纯移动）。**规模**：M。**依赖**：B1-03。
- **目标**：把 Goal Runner、Explorer、Verifier、视觉复核的装配收进独立宿主服务，为模型分工与项目代理腾出落点。
- **代码锚点**：`main.mjs` 1192–1486：`goalRunner = createGoalRunner({...})`（1270）整段，以及只被它使用的 `buildGoalRunnerMessage`、`buildGoalRunnerReminder`、`buildExplorerMessage`、`buildExplorerContext`、`buildExplorerReminder`、`buildVerifierMessage`、`parseExplorerReport`、`collectExplorerEvidenceRefs`（1084–1101）等（移动前用 `rg` 确认没有其他调用方）。`createGoalRunnerAssistantPlaceholder`、`mapGoalTurnOutcome` 已在 `goal-runner-message-persistence.mjs`，只改 import。
- **允许改动**：新建 `apps/desktop/electron/main/agent-host/goal-runner-host.mjs` 与测试；`main.mjs`。
- **不许改动**：任何逻辑。本卡 diff 应当只有「剪切 + 粘贴 + 依赖注入」。
- **实现要点**：导出 `createDesktopGoalRunnerHost(deps)`，依赖全部显式注入（`goalPlanStore`、`conversationStore`、`agentTurnExecutor`、`broadcast`、`llmChatService`、worktree / branch adapters、`desktopPreviewProvider`、`visualReview`、`resolveConversationModelProviderId`…），返回 `{ goalRunner, explorerRunner, verifierRunner }`。
- **必须新增的测试**：`goal-runner-host.test.mjs`：用假依赖 + 脚本化执行器跑通一次 `runGoalTurn`、一次 `runExplorer`、一次 `runVerifier`。
- **退出条件**：`main.mjs` 至少减少 200 行；Goal、Explorer、Verifier、视觉复核、Automation 回归全绿。

---

## B1-05 设置 schema 版本与迁移框架

- **级别**：B。**规模**：S。**依赖**：P0-1。
- **目标**：设置有版本号；需要改写已有数据的变更通过可重复、可回退的迁移完成。
- **代码锚点**：`apps/desktop/electron/main/settings-store.mjs`（浅合并、无版本）；`settings-application-service.mjs`；`packages/runtime-node/src/data-store.mjs`（`migrateFromLegacy`）；TUI 读设置的位置（`rg "settings.json" apps/tui/src`）。
- **允许改动**：新建 `packages/runtime-node/src/settings-migrations.mjs` 与测试；`settings-store.mjs`（加载时调用迁移）；TUI 读设置处（同样调用，保证两端一致）。
- **实现要点**：
  - `SETTINGS_MIGRATIONS = [{ version: 1, up(settings, ctx) { … } }, …]`，`runSettingsMigrations({ settings, ctx, now })` 返回 `{ settings, applied: number[], backupPath? }`。
  - v1：只写 `schemaVersion: 1`。
  - 迁移前把原文件复制为 `settings.json.bak-v<旧版本>-<ISO 时间>`（同目录，最多保留 5 份，按时间删最旧）；写入用临时文件 + 原子改名。
  - `schemaVersion` 高于当前代码认识的版本（用户从新版降级）：不迁移、不回写 `schemaVersion`，正常读取已知字段。
  - 任一步抛错：保持原文件不变，记录诊断日志，本次运行按旧版本数据继续。
  - 默认值不写迁移（读取时计算）。
- **必须新增的测试**：新文件升到 v1；重复执行幂等；备份数量上限；高版本文件不被改写；迁移抛错时原文件不变；TUI 与桌面读到同一结果。
- **退出条件**：测试通过；桌面与 TUI 完整测试通过。

---

## B1-06 项目注册表与稳定 `workspaceId`

- **级别**：A（ADR 81 决策 12、ADR 85 决策 6）。**规模**：M。**依赖**：B1-05。
- **目标**：每个工作区有不随改名、移动、降级而变化的 `workspaceId`；远程委托与本机共用这个身份。
- **必读**：ADR 85 决策 6；ADR 81 决策 12。
- **代码锚点**：
  - `workspace-application-service.mjs`：投影（35–42）、`ensureDefaultWorkspace`（90–112）、`addWorkspace`（131 起）、`updateWorkspace`、`setPrimaryFolder`（会改 `path`）、`removeWorkspace`。
  - `runtime-gateway/remote-access-controller.mjs`（`workspaceId` 26 / 43–48 / 119–132）、`setup-remote-access.mjs`。
  - `register-workspace-ipc.mjs`；渲染层工作区类型（`rg "linkedFolders" apps/desktop/renderer/src --type ts`）。
- **允许改动**：新建 `packages/runtime-node/src/project-registry.mjs` 与测试；`data-store.mjs`（登记 `projects`，scope：portable）；`settings-migrations.mjs`（v2）；`workspace-application-service.mjs` 与测试；`remote-access-controller.mjs`、`setup-remote-access.mjs` 与测试；工作区 IPC 投影与渲染层类型（只加 `id` 字段）。
- **实现要点**：
  - 注册表 `projects/registry.json`：`{ schemaVersion: 1, projects: [{ workspaceId, path, realPath, createdAt, previousPaths: [], remoteAlias?: string }] }`；原子写。
  - `ensureForPath(path)`：先按 `realPath` 精确匹配，再按 `path` 匹配，都没有才生成 UUID v4；`recordMove(workspaceId, newPath)`：旧路径进 `previousPaths`。
  - 迁移 v2：为 `settings.workspaces` 每项确定 id，写回 `workspaces[].id`（缓存）；远程设置的旧 `workspaceId` 若不是注册表里的 id，记为当前活动工作区的 `remoteAlias`。
  - 工作区投影与 IPC 返回 `id`；`setPrimaryFolder` 调用 `recordMove`；`removeWorkspace` 不删注册表条目（历史与记忆仍然挂在 id 上）。
  - 旧版本写回丢失 `workspaces[].id` 后：下次加载按 path 从注册表取回原 id（不生成新的）。
  - 远程：`workspaceIds` 缺省时用当前工作区 id；准入同时接受 id 与 alias。
  - 不按路径相似度猜 id；文件夹搬家后的重新关联留接口 `relinkWorkspace(workspaceId, newPath)`，本卡不做界面。
- **必须新增的测试**：旧设置迁移生成 id；重复加载 id 不变；改名 id 不变；`setPrimaryFolder` 后 id 不变且 `previousPaths` 记录；模拟旧版本写回丢字段后恢复同一 id；远程 alias 准入；注册表损坏时的处理（备份损坏文件、从 settings 缓存重建）。
- **退出条件**：测试通过；桌面、runtime-node 完整测试通过。

---

## B1-07 协议契约与纯函数

- **级别**：A（契约）。只加类型与纯函数，不接线。**规模**：L（可按文件拆成 B1-07a delegation / b memory + model-routing / c project + objectives 三个 PR）。**依赖**：P0-1。
- **目标**：0.1.0 全部跨层对象与决策函数一次定型，后续卡只引用。
- **必读**：运行时契约 §2（含 2.4–2.7）、§3、§5.1.1；记忆架构文档 §4；ADR 82 §1–§3；ADR 83 §1–§5；ADR 84；ADR 85。
- **代码锚点**：`packages/protocol/src/index.ts`（聚合导出）；旧 `packages/protocol/src/memory.ts`（`WorkingMemory*` / `MemoryWiki*`，全仓无业务引用，先 `rg "WorkingMemory|MemoryWiki"` 确认）；`packages/protocol/src/task-overview.ts` `projectGoalPlan`；`packages/protocol/src/acceptance-close-gate.ts`；`packages/runtime-node/src/goal-runner.mjs` `evaluateVerificationGate`（589–601）。
- **允许改动**：新建 `packages/protocol/src/delegation.ts`、`model-routing.ts`、`project.ts`、`objectives.ts` 与各自测试；重写 `packages/protocol/src/memory.ts` 与测试；`packages/protocol/src/index.ts`（追加导出）；新建 `packages/runtime-node/src/project-agent/verification-verdict.mjs` 与测试。
- **类型清单**：
  - `delegation.ts`：`WorkSessionStatus`（`queued | starting | running | waiting_user | verifying | result_ready | accepted | failed | cancelled | superseded`）、`WorkSession`、`SessionReport`（含 `keyFindings`、`changedFiles`、`evidenceRefs`）、`DelegationOrigin`（`anchorMessageId`、`inputId`、`surface`、`memorySnapshotId`、`objectiveId?`、`modelSelection`、`parentSessionId?`、`depth`）、`DelegationEvent`（`eventId` 确定性、`kind`、`sessionId`、`at`、`payload`）、`AgentReplyMeta`（`replyTo[]`、`sources[]`、`verdictRef?`、`memoryUsed[]`、`memoryLearned[]`、`surfacing`）、`MessageDisposition`（`answered | merged | stopped | superseded | parallel | queued | out_of_scope`）、`VerificationVerdict`（`passed | failed | partial | unverifiable`，`independentVerifier`、`verifierModel`、`sameFamilyAsWorker`、`checks[]`、`evidenceRefs[]`）、`AcceptancePolicy`（`auto | confirm`）、`AcceptanceDecision`（`acceptedBy: 'policy' | 'user'`、`reasons[]`）、`SurfacingDecision`（`interrupt | message | digest | silent` + `reason`）、`ProjectInput`、`PendingApproval`、`HostLease`。
  - `memory.ts`：`MemoryKind`（`fact | preference | decision | procedure | responsibility`）、`MemoryTrust`（`verified | stated | inferred`）、`MemoryItem`（`id`、`scope: 'project' | 'user'`、`workspaceId?`、`kind`、`text`、`trust`、`sourceRefs[]`、`pinned`、`status: 'active' | 'forgotten' | 'expired' | 'conflicted'`、`confirmedCount`、`createdAt`、`lastUsedAt?`、`expiresAt?`）、`MemoryEpisode`、`MemorySnapshot`（`snapshotId`、`itemIds[]`、`createdAt`）。
  - `model-routing.ts`：`ModelTier`（`strong | fast | economy | vision`）、`ModelRole`（`project_agent | session_worker | explorer | verifier | visual_verifier | memory_curator | objective_probe | compactor`）、`RoleSetting`（`{ mode: 'tier', tier } | { mode: 'fixed', modelProviderId } | { mode: 'auto', pool: string[] }`）、`ModelRoutingSettings`（`tiers`、`roles`、`verifierPreferDifferentFamily`、`dailySpendCapUsd?`）、`ProjectModelPolicy`（`scope`、`overrides`）、`ModelSelectionSnapshot`（ADR 83 §5 原样）、`ModelResolution`（成功或 `{ ok: false, reason, missing }`）。
  - `project.ts`：`ProjectRegistryEntry`、`BotAvatar`（`{ kind: 'generated', shape, color } | { kind: 'image', ref }`）、`BotProfile`、`BotRowState`（`needsYou: number`、`unread: number`、`running: number`）、`BotListItem`、`BotListFilter`（`{ query?, needsYouOnly? }`）。
  - `objectives.ts`：`ProjectObjective`、`ObjectiveAutonomy`（`report_only | propose | act`）、`WatchTrigger`（`schedule | git | file | ci`）、`ObjectiveWatch`、`WatchObservation`（`digest` 用于变化判定）。
- **纯函数清单（protocol）**：`projectWorkSession(plan, conversationMeta)`、`projectMessageDispositions(messages, events)`、`decideAcceptance({ verdict, policy, session, userOverride })`、`decideSurfacing({ event, proactivity, foreground, quietHours, needsYou })`、`resolveRoleModel({ role, catalog, routing, projectPolicy, taskOverride, requestPreference, workerModel })`、`projectBotListItem({ profile, lastMessage, sessions, approvals, readCursor })`、`sortBotList(items)`（按最近活动倒序，需要你优先不打乱时间序——需要你只影响筛选与角标，不影响排序）、`filterBotList(items, filter)`、`generateAvatar(workspaceId)`（确定性形状 × 颜色）、`diffWatchObservation(prev, next)`。
- **纯函数（runtime-node）**：`computeVerificationVerdict(plan, evidenceIndex, hostAuthority)`：内部复用 `evaluateVerificationGate`，只认宿主事实，不认模型自述。
- **必须新增的测试**：运行时契约 §12 与记忆文档 §15 中所有「纯函数可测」的条目；`projectWorkSession` 与 `projectGoalPlan` 对同一 GoalPlan 的结论一致；`decideSurfacing` 覆盖运行时契约 §5.1.1 规则表每一行；`decideAcceptance` 覆盖每个 confirm 原因；`resolveRoleModel` 覆盖能力过滤、范围过滤、不同源复核、自动池外拒绝、空集报错与缺失说明；`sortBotList` / `filterBotList`；`generateAvatar` 确定且 1000 个随机 id 中形状 × 颜色组合分布均匀。
- **退出条件**：`node --test packages/protocol/src/*.test.ts`、`pnpm --filter @peer-agent/runtime-node test`、`pnpm typecheck` 通过；运行时代码没有调用这些新函数（`rg` 证明）。

---

## B1-08 SQLite 驱动与全文索引基座

- **级别**：B。**规模**：S。**依赖**：P0-1。
- **目标**：给记忆与搜索提供不新增依赖的本机全文索引，桌面（Electron）与 TUI（Bun）共用。
- **代码锚点**：现有 `node:sqlite` 用法 `packages/runtime-node/src/remote-binding-store.mjs`、`remote-receipt-store.mjs`。
- **事实**：Electron 41（Node 24.15）与 Bun 1.4.2 的 `node:sqlite` 都支持 FTS5 `tokenize='trigram'`（中文子串检索已实测）；测试环境 Node ≥ 22.18 同样可用。
- **允许改动**：新建 `packages/runtime-node/src/sqlite/open-sqlite.mjs`、`fts-index.mjs` 与测试；`data-store.mjs`（登记 `memoryIndex`，`cache/memory-index/`，scope：cache）。
- **实现要点**：
  - `openSqlite(file, { readonly })`：`DatabaseSync`；`journal_mode=WAL`、`busy_timeout=3000`；目录不存在时创建；文件损坏（打开或 `PRAGMA quick_check` 失败）时改名为 `.corrupt-<时间>` 并新建。
  - `createFtsIndex({ db, name })`：一张内容表（`id TEXT PRIMARY KEY, body TEXT, meta TEXT, updated_at`）+ 一张 FTS5 表（`tokenize='trigram'`）；`upsert(id, body, meta)`、`remove(id)`、`search(query, { limit })`、`rebuild(iterable)`、`count()`。
  - trigram 需要至少 3 个字符：查询去空白后少于 3 个字符时改用内容表 `LIKE` 扫描（带 `limit`）；混合查询按空白切词，每个词分别处理后取交集。
  - 所有 SQL 用参数绑定；FTS 查询串转义双引号并整体加引号，避免 FTS 语法注入。
- **必须新增的测试**：中文 / 英文 / 混合查询；2 字中文查询走 LIKE；特殊字符不报错；重建后结果一致；损坏文件自动隔离重建；在 Bun 下也能跑（TUI 测试里加一个 smoke 用例）。
- **退出条件**：runtime-node 与 TUI 测试通过。

---

## B1-09 ModelRouter 接入执行路径与用量维度

- **级别**：A（ADR 83）。**规模**：M。**依赖**：B1-04、B1-07；ADR 83 Accepted。
- **目标**：Explorer / Verifier / 视觉复核按角色解析模型；视觉复核不再因任务模型不能看图而失败；复核优先不同源；用量按角色与项目记账。
- **必读**：ADR 83 全文；ADR 30（Provider 恢复）；ADR 25（用量账本）。
- **代码锚点**：
  - `conversation-model-binding.mjs` `resolveConversationModelProviderId`（10–27）。
  - `agent-host/goal-runner-host.mjs`（B1-04 之后）中 Explorer / Verifier / 视觉复核的 `modelProviderId` 解析。
  - `runtime-gateway/desktop-visual-review.mjs` `requireVisualReviewProvider`（31–33）。
  - `llm-config-store.mjs`（已接入模型、`supportsVision`、`contextWindow`、`reasoningEffortValues`）；`provider-channels.mjs`（`capabilities.vision / toolUse`，约 1631）；`provider-adapters/models-dev-registry.mjs`（62–70）。
  - `chat-runtime/provider-recovery-broker.mjs`（故障切换候选）。
  - `usage-request-log.mjs`（63–83 记录形状）、`usage-stats.mjs`。
- **允许改动**：新建 `packages/runtime-node/src/model-router.mjs` 与测试（桌面与 TUI 共用的适配：把本机模型目录转换成 `resolveRoleModel` 的输入）；`agent-host/*`；`settings-application-service.mjs`（`modelRouting` 读写，默认值在读取时计算）；`usage-request-log.mjs`、`usage-stats.mjs`（加字段与按角色聚合）；`provider-recovery-broker.mjs`（候选过滤）；`llm-chat-service.mjs` 只允许从 `turnProfile.modelSelection` 读取模型，不加参数。
- **实现要点**：
  - 默认值（读取时计算，不写迁移）：只有一个可用模型时四档都指向它、所有角色跟随档位——行为与今天完全一致。多个模型时：`strong` = 当前默认模型；`fast` / `economy` 默认也指向它，直到用户在 B1-10 设置里改；`vision` = 第一个 `supportsVision` 的模型（没有则为空）。
  - 普通会话继续走 `resolveConversationModelProviderId`，不受影响；普通会话的上下文压缩在 0.1.0 保持跟随会话模型，`compactor` 角色只作用于项目代理体系（B2 起）。
  - Goal 任务（经典界面里的 Goal）：执行仍用会话模型；Explorer 用 `explorer` 角色；Verifier 用 `verifier` 角色并优先不同 Provider 家族（家族按 `providerType` / `groupId` 判定，写成纯函数）；视觉复核用 `visual_verifier`，只在能看图的候选里选；全都没有时返回结构化原因（「没有能看图的模型」），不再抛 `visual-review-vision-unavailable`。
  - 故障切换只在该角色过滤后的候选里切。
  - 用量记录新增 `role`（取 `turnProfile.role`）与 `workspaceId`（有则写）；聚合器支持按 role 分组；旧记录没有字段时归入 `unknown`。
  - 角色日花费上限（ADR 83）：本卡只做计算与超限判定的纯函数与记账，超限时对非必达角色返回 `spend_cap_reached`，界面提示放 B1-10。
- **必须新增的测试**：单模型行为不变（Explorer / Verifier / 视觉复核拿到的模型与改动前一致）；多模型时各角色解析；视觉复核自动选能看图的模型；没有可用视觉模型时的结构化失败；不同源复核与同源退回标注；故障切换不越出候选；用量带 role；花费上限判定。
- **退出条件**：测试通过；一次真实运行：任务模型不能看图、另接一个能看图的模型，视觉复核成功，截图记录附在交接报告。

---

## B1-10 「模型分工」设置页

- **级别**：B。**规模**：M。**依赖**：B1-09。
- **目标**：用户可以配置档位（主模型 + 备选）、角色（跟随档位 / 固定 / 自动 + 池）、复核是否优先不同源、每个角色的日花费上限；用量页可按角色查看。
- **代码锚点**：`apps/desktop/renderer/src/app/components/SettingsPage.tsx`（分组：个人 / AI / 开发 / 连接 / 应用 / 归档）；`LlmSettingsPanel.tsx`（2265 行，**不许加代码**）；用量面板组件（`rg "usage" apps/desktop/renderer/src/app/components -l`）；`ipc/register-settings-ipc.mjs`；`bootstrapPreloadApi.ts`；`packages/i18n/src/index.ts`。
- **允许改动**：新建 `apps/desktop/renderer/src/app/components/settings/ModelRoutingPanel.tsx`、同目录的 `modelRoutingPanelState.ts`（纯函数）与测试；`SettingsPage.tsx`（在 AI 分组加 `routing` 分区，只加一项）；新 IPC `model-routing:get / update / preview`（进 catalog）；用量面板加「按角色」切换；i18n（`modelRouting.*`，中英文）。
- **实现要点**：
  - 上半部分档位表：每档主模型下拉 + 备选（可排序）；能力不满足的模型在下拉里置灰并写原因（例：视觉档只能选能看图的）。
  - 下半部分角色表：8 个角色，每行显示当前解析结果（调用 `model-routing:preview`，由 main 计算）；「自动」时出现模型池多选。
  - 「复核优先不同源」开关，默认开。
  - 只有一个模型时，顶部显示一句「只有一个模型时，所有工作都用它」，表格只读。
  - 读写全部经 main；渲染层不保存真值。
- **必须新增的测试**：IPC 通道测试；面板状态纯函数（能力置灰、单模型只读、池校验）；i18n 键中英文完整；`LlmSettingsPanel.tsx` 行数不变（源码契约测试）。
- **退出条件**：`ipc:check` 与桌面完整测试通过；中英文截图附在交接报告。

---

## B1-11 开发者设置分区与 `projectAgentMode`

- **级别**：C。**规模**：S。**依赖**：B1-05。
- **目标**：设置页有开发者分区；开关 `projectAgentMode` 可读写；分区预留项目代理诊断位置。
- **代码锚点**：`ipc/register-settings-ipc.mjs` 的 `developer-settings:get | update | reset | diagnostics`；`settings-application-service.mjs:78–91`（开发者设置实际存在 `settings.json` 的 `developer` 键）；`packages/runtime-node/src/data-store.mjs` 的 `developerSettings` 条目（文件未被使用）；`packages/i18n` 已有 `developer.*` 键。
- **允许改动**：新建 `apps/desktop/renderer/src/app/components/settings/DeveloperPanel.tsx` 与状态纯函数、测试；`SettingsPage.tsx`（开发分组加 `developer` 分区）；`bootstrapPreloadApi.ts` / `clientApi.ts`（把已有 `developer-settings:*` 接进类型化接口）；新建 `apps/desktop/renderer/src/app/state/useDeveloperFlag.ts`；i18n。
- **实现要点**：
  - 真值位置固定为 `settings.json` 的 `developer.projectAgentMode`（布尔，默认 `false`）；在交接报告写明 `DATA_STORE_ENTRIES.developerSettings` 未被使用，是否删除由负责人决定（本卡不删）。
  - 分区内容：开关一个；「项目代理诊断」占位区块（显示「未启用」）。
  - 本卡不加任何行为：开关打开后界面与行为不变。
- **必须新增的测试**：默认值、读写、重置；开关打开前后界面无差异（源码契约：`App.tsx` 未读取该开关）。
- **退出条件**：测试通过。

---

## B1-12 子会话原语：`role`、`parentConversationId`、列表过滤

- **级别**：A（会话契约）。**规模**：M。**依赖**：P0-1。
- **目标**：会话有角色与父子关系；任务子会话与机器人对话在经典界面默认不出现在列表与搜索里；划词子会话改用同一原语。
- **必读**：运行时契约 §2.4；分层文档 §4.1 第 3 步；ADR 85 决策 10。
- **代码锚点**：`packages/conversation-store/src/index.mjs`：`createConversation`（752–781）、`createSelectionChild`（808–852）、`listSelectionChildren`（856）、`listConversationsByWorkspace`（674–700）、`listConversations`、`searchConversations`（713–745）；`inherited-background.mjs`（8–59）；`background-snapshot-store.mjs`；`index.d.ts`；`apps/desktop/electron/main/selection-side-chat-service.mjs`；TUI `conversation-persistence.ts`（读会话列表处）。
- **允许改动**：conversation-store 源码、类型声明与测试；`selection-side-chat-service.mjs` 改调新原语；TUI 列表调用处（传过滤参数，行为不变）。
- **实现要点**：
  - 会话 meta 新增：`role?: 'project_agent' | 'work_session'`（缺省 = 普通会话）、`parentConversationId?`、`workspaceId?`、`delegation?: { sessionId, anchorMessageId, inputId }`。
  - `createChildConversation({ parentConversationId, role, anchorMessageId, snapshotPolicy, title, workspacePath, workspaceId, mode, modelProviderId })`：快照由 main 按运行时事实捕获（沿用 `buildInheritedBackground`），覆盖到锚点为止。
  - `createSelectionChild` 改为调用 `createChildConversation`（`role` 缺省），外部行为与持久化格式保持兼容（`selectionOrigin` 字段保留）。
  - 列表与搜索新增参数 `roles?: ('default' | 'project_agent' | 'work_session')[]`，缺省只返回 `default`——经典界面零变化；新壳显式传入需要的角色。
  - `listChildren(parentConversationId, { role })`。
- **必须新增的测试**：划词子会话全部回归；新原语创建、快照到锚点为止、role 与父子关系持久化；列表 / 搜索缺省不返回任务子会话与机器人对话；显式 `roles` 返回；旧数据（无 role）按 default 处理。
- **退出条件**：conversation-store、桌面、TUI 完整测试通过。

---

## B1-R 发布 `0.1.0-beta.1`

- **执行**：负责人或指派。**依赖**：B1 全部合入。
- **步骤**：版本计划 §10 通用检查单，外加：
  1. **changelog 支持 beta 通道**（首次发 beta 时必须做）：`scripts/build-changelog.mjs` 的 `parseVersion`（约 95）与文件名过滤（约 115）接受 `v<x.y.z>-(alpha|beta|rc).<n>.md`，`channel` 取 `beta`；清单 `channels` 增加 `beta`，`latest.beta` 指向最新 beta；`scripts/build-changelog.test.mjs` 补用例；`docs/changelog` 页面若按通道展示，beta 标注「预发布」。
  2. README / README.zh-CN 增加 beta 标记行：`beta channel **\`0.1.0-beta.1\`**` / `beta 通道 **\`0.1.0-beta.1\`**`（正式版标记保持 `0.0.18`）。
  3. `release-notes/v0.1.0-beta.1.md`：新增（后台推进、待批准不丢、模型分工、视觉复核自动选模型）、变化、已知限制（项目代理未开放）、降级说明（可装回 0.0.18，数据兼容）。
  4. 证据：版本计划 §12.1 beta.1 一行全部附上。
- **退出条件**：GitHub prerelease 生成；beta 通道用户可更新；版本计划 §5.2 更新。
