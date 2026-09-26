# beta.2 骨架（`0.1.0-beta.2`，开发者开关后）

创建时间：2026-09-26
最后更新：2026-09-26

> 主题：项目代理能跑通「一句话 → 锚定开任务 → 事件回流 → 回复 → 策略代签」，并有机器人列表、对话、档案三件套界面。  
> 开关：所有用户可见行为受 `developer.projectAgentMode` 控制；关闭时界面、行为、存储写入与 beta.1 完全一致（每张卡都要有测试证明）。  
> 进入条件：beta.1 已发布；ADR 80、81、83、84、85 为 Accepted。  
> 通用退出条件见 `README.md` §6。

并行关系：

```text
B2-01 → B2-03 ─┐
B2-02 ─────────┼→ B2-04 → B2-07 → B2-08 → B2-09
B2-05 ─────────┤            ↑
B2-06 ─────────┘            │
B2-10 ──────────────→ B2-11 ┘（B2-11 依赖 B2-07 的输入形状）
B2-04 → B2-12 → B2-13 → B2-14 / B2-15 / B2-16（三张可并行）
B2-07 → B2-17
```

代理对话中的消息种类（本阶段定型，界面与运行时共用）：

| `kind` | 谁写 | 界面 |
|---|---|---|
| `user_input` | 输入队列消费者（B2-06） | 右侧气泡，带处置标记 |
| `agent_reply` | ReplyComposer（B2-08） | 左侧气泡，带回复条、标记、卡片 |
| `system_card` | ReplyComposer（由投影生成，如待批准、需要确认） | 左侧卡片 |
| `agent_turn` | 代理回合的内部记录（工具调用与结果） | 默认不显示；档案「代理过程」可展开（B3-04） |

---

## B2-01 `project_agent` 模式：投影白名单 + 执行硬闸

- **级别**：A。**规模**：M。**依赖**：B1-07。
- **目标**：代理回合只能看到并执行「读 + 调度 + 记忆 + 目标 + 自身设置」类工具；写类能力无论投影是否漏网，执行时一律拒绝。
- **必读**：ADR 80 决策 2；运行时契约 §3；ADR 35（模式隔离）。
- **代码锚点**：
  - `packages/runtime-core/src/projection.ts` `isRuntimeToolAvailableInMode`（81）：无 `modeScopes` 的工具只在 `chat / plan / goal` 可见——`project_agent` 默认看不到，保持这个「默认严格」。
  - `apps/desktop/electron/main/tools/*-tool-definitions.mjs` 的 `availableInModes`；`tools/runtime-projection-tool-materializer.mjs` `manifestFromTool`（79–104）；`llm-chat-service.mjs` `buildRuntimeTools({ mode })`（103–116）。
  - `chat-runtime/projected-tool-executor.mjs`（执行入口，`extraProviders` 约 310）；`chat-runtime/goal-mode-gate.mjs` `evaluateGoalModeGate`（321 起；对未知模式在 393 默认放行）。
  - Explorer 严格白名单的现有写法（`tool-registry.test.mjs` 281–283 断言 explorer 只投影 `list_files / read_file / search_files / batch_search`）。
- **允许改动**：`legacy-local-tool-definitions.mjs`、`search-tool-definitions.mjs`（只给只读工具的 `availableInModes` 加 `'project_agent'`）；新建 `packages/runtime-node/src/project-agent/mode-policy.mjs` 与测试（`PROJECT_AGENT_ALLOWED_CAPABILITIES` 与判定函数的唯一定义，TUI 在 B5-01 复用）；新建 `chat-runtime/project-agent-mode-gate.mjs` 与测试（桌面执行闸，调用 `mode-policy`）；`projected-tool-executor.mjs`（执行前调用新闸门）；`goal-mode-gate.mjs`（`project_agent` 分支：任何副作用拒绝）；`llm-chat-service.mjs`（接受 `mode: 'project_agent'`，不加参数）；`tool-registry.test.mjs`。
- **不许改动**：写类工具、Shell、浏览器、MCP、Skill 的 `availableInModes`（它们不能出现在 `project_agent`）。
- **实现要点**：
  - 代理可见的只读工具：`list_files`、`read_file`、`search_files`、`batch_search`。不含 Shell、Web、浏览器、MCP、Skill、桌面预览。
  - 后续卡片追加的代理工具：调度（B2-03）、记忆（B2-10）、主动性与模型偏好（B3-05）、目标（B4-04）。每张卡都要把自己的 capabilityId 加进 `mode-policy.mjs` 的 `PROJECT_AGENT_ALLOWED_CAPABILITIES`（后续卡「允许改动」里写的「`project-agent-mode-gate.mjs`（白名单追加）」都指这个文件）。
  - 执行硬闸：`turnProfile.role === 'project_agent'` 或 `mode === 'project_agent'` 时，capabilityId 不在白名单 → 拒绝，原因 `project_agent_capability_denied`，写 Evidence；permission-gate 在该模式下对文件写、Shell、浏览器类 kind 兜底拒绝。
  - 代理回合的 `accessLevel` 固定按 `restricted_local` 处理（只读不询问），不受用户全局访问级别影响。
- **必须新增的测试**：投影只含白名单；把一个写工具临时加进 `project_agent` 的 `availableInModes`（测试内构造）时执行仍被硬闸拒绝；MCP / Skill 工具在该模式不可见；只读工具可执行；开关关闭时投影零变化。
- **退出条件**：测试通过；交接报告列出最终白名单。

---

## B2-02 `work_session` 回合画像

- **级别**：A（ADR 80、83、85 决策 5）。**规模**：M。**依赖**：B1-03、B1-09、B1-12。
- **目标**：任务回合使用开任务时冻结的模型与记忆快照；不投影 L1 内嵌浏览器；需要批准的请求进入持久待批准并带上项目与任务身份。
- **代码锚点**：`agent-host/goal-runner-host.mjs`（B1-04）的 `runGoalTurn` / `runExplorer` / `runVerifier`；`tools/browser-tool-definitions.mjs`（L1）、`tools/external-browser-tool-definitions.mjs`（L2）；`llm-chat-service.mjs` 中 `buildRuntimeTools` 的 `projectionOptions`；`approval-store.mjs`（B1-03）。
- **允许改动**：`agent-host/goal-runner-host.mjs`；新建 `agent-host/work-session-profile.mjs` 与测试；`tools/index.mjs`（`projectionOptions` 支持 `excludeCapabilityPrefixes`）；`llm-chat-service.mjs`（从 `turnProfile` 读取 `excludeCapabilityPrefixes` 与 `modelSelection`，不加参数）；`permission-gate.mjs`（登记待批准时从 `turnProfile` 取 `workspaceId`、`sessionId`）。
- **实现要点**：
  - 判定：GoalPlan 带 `delegationOrigin` 即为任务；其回合 `turnProfile = { role: 'work_session', workspaceId, sessionId, modelSelection, memorySnapshotId, excludeCapabilityPrefixes: ['local.browser.'] }`（前缀以 L1 实际 capabilityId 为准，执行时 `rg` 确认）。
  - 模型：执行用 `modelSelection.worker`，Explorer / Verifier / 视觉复核用快照里对应角色；快照缺失（旧计划）时退回 B1-09 的解析。
  - 待批准：记录带 `workspaceId`、`sessionId`、`planId`，写入 `project-runtime/<workspaceId>/approvals.jsonl`。
  - 经典界面里的普通 Goal 行为不变。
- **必须新增的测试**：任务回合投影不含 L1、含 L2；使用快照模型（修改会话模型后任务仍用快照）；待批准记录带项目与任务身份；普通 Goal 投影与模型解析不变。
- **退出条件**：测试通过。

---

## B2-03 调度 Provider 与工具

- **级别**：A。**规模**：L（可拆 B2-03a spawn / list / get / cancel，B2-03b message / post_reply）。**依赖**：B2-01。
- **目标**：代理能开任务、查任务、取消任务、给任务发话、发回复；每次调用都有 Tool Result 与 Evidence。
- **必读**：运行时契约 §3、§4；ADR 80 决策 3、7。
- **代码锚点**：`runtime-gateway/local-goal-provider.mjs`（Provider 写法）；`runtime-gateway/capability-provider-registry.mjs`（`register`，76–104）；`runtime-gateway/local-tool-host.mjs`（默认 providers 数组，57–70）；`tools/goal-tool-definitions.mjs`（`availableInModes` 与 schema 写法）；`tools/prompts/`（工具提示必须来自资源文件，`assertToolPromptsAreAssetBacked`）；`packages/runtime-core/src/goal-idempotency.ts`、`goal-idempotency-durable.ts`；`packages/runtime-node/src/tool-result-factory.mjs`（`createPermissionGrant`、Evidence）。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/delegation-provider.mjs` 与测试（Provider 本体放 runtime-node，TUI 作为宿主时复用，B5-01）；新建 `packages/runtime-node/src/project-agent/tool-specs.mjs`（工具名、输入 schema、capabilityId 的唯一定义，桌面与 TUI 共用）；新建 `runtime-gateway/local-delegation-provider.mjs`（两行再导出，照 `local-mcp-provider.mjs` 的写法）；新建 `tools/delegation-tool-definitions.mjs`（引用 `tool-specs`）与 `tools/prompts/delegation/*.md`；`local-tool-host.mjs`（注册）；`tools/index.mjs`（拼装）；`project-agent-mode-gate.mjs`（白名单追加）。
- **工具（全部只在 `project_agent` 可见）**：

| 工具 | 输入（要点） | 输出 |
|---|---|---|
| `spawn_session` | `anchorMessageIds[]`（≥ 1，必须是本对话的 `user_input`）、`title`（≤ 60 字）、`brief`（≤ 4000 字）、`successCriteria[]`（1–8 条）、`kind`（`code / research / docs / ui / ops / other`）、`readOnly`、`modelPreference?`（`{ modelProviderId?, reason }`）、`priority?`、`dependsOn?`（B4-01 生效）、`isolation?`（B4-02 生效） | `{ sessionId, status, queuedBehind? }` 或结构化错误 |
| `list_sessions` | `status?`、`limit?` | `WorkSession[]` 投影 |
| `get_session` | `sessionId`、`detail?: 'summary' \| 'report'` | 投影 + `SessionReport` |
| `cancel_session` | `sessionId`、`reason` | 新状态 |
| `message_session` | `sessionId`、`text`、`intent: 'answer'`（本卡只支持回答任务的提问；`amend` 等在 B3-02） | 投递结果 |
| `post_reply` | `replyTo[]`（主动消息可空，但须声明 `proactive: true`）、`text`（≤ 2000 字）、`sources?: sessionId[]`、`question?: { options: string[] }` | `{ messageId }` |

- **实现要点**：
  - capabilityId 前缀 `local.delegation.`；Provider 以自授权方式记录 PermissionGrant（`reason: 'project_agent_dispatch'`），因为调度本身不产生本机副作用；任务内的副作用仍走正常权限。
  - 深度限制：非 `project_agent` 回合调用 → `depth_limit`（投影层本就不可见，执行层再查一次）。
  - 幂等：键 = `sha256(turnId + toolCallOrdinal + name + canonical(input))`，用 runtime-core 的持久幂等账本；重放返回首次结果。
  - `spawn_session` 的执行委托给 SessionSupervisor（B2-04）；本卡只做校验、幂等、Evidence 与调用。
  - `post_reply` 委托给 ReplyComposer（B2-08）；本卡只做校验与转发。
  - 错误都是结构化 Tool Result（`anchor_not_found`、`anchor_not_user_input`、`model_unavailable`（附缺失说明）、`session_not_found`、`depth_limit`），供代理转述。
- **必须新增的测试**：运行时契约 §12 中白名单、深度、幂等、锚点校验相关条目；每个工具的成功与每种错误；Evidence 与 Grant 记录存在。
- **退出条件**：测试通过；提示文本全部在资源文件里（`architecture:check` 通过）。

---

## B2-04 SessionSupervisor

- **级别**：A。**规模**：M。**依赖**：B2-02、B2-03。
- **目标**：开任务 = 冻结选择 → 建子会话 → 写委托消息 → 建 GoalPlan → 排队 / 启动；取消与查询走同一个监督者。
- **必读**：分层文档 §4.1；运行时契约 §2.4；ADR 83 §5。
- **代码锚点**：`packages/runtime-node/src/goal-plan-store.mjs` `createGoalContract` / `createPlan`（2930 起）、`supersedeAwaitingDrafts`（2826，同会话单活跃）；`packages/runtime-node/src/goal-runner.mjs` `start` / `pause` / `resume`；`packages/conversation-store`（B1-12 的 `createChildConversation`）；`packages/runtime-node/src/goal-delivery-binding.mjs` `attachWorkspaceHeadBinding`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/session-supervisor.mjs` 与测试；`goal-plan-store.mjs`（只加 `delegationOrigin` 字段的读写与校验）。
- **实现要点**（`spawn` 顺序，任何一步失败都不留下半成品，已创建的子会话标记 `status: 'archived'` 并记录原因）：
  1. 校验锚点、深度、幂等（B2-03 已做，这里只信任传入的已校验输入）。
  2. 冻结：`resolveRoleModel` 解析 `session_worker`、`explorer`、`verifier`、`visual_verifier`（`kind: 'ui'` 时要求 worker 能看图）→ `ModelSelectionSnapshot`；记忆快照 `memorySnapshotId`（B2-10 合入前为 `null`）。
  3. 建子会话：`role: 'work_session'`、`parentConversationId` = 代理对话、`workspacePath`、`workspaceId`、`mode: 'goal'`、`modelProviderId` = worker、`delegation: { sessionId, anchorMessageId, inputId }`。
  4. 写第一条消息（用户角色，事实上下文，不是系统指令）：委托说明——目标、完成标准、锚点原文引用、约束（是否只读）。
  5. 建 GoalPlan：`successCriteria`；`activation: 'accepted_goal'`；只读任务的执行策略禁止写；`delegationOrigin` 完整写入；交付绑定按 ADR 79 跟随实时 HEAD，隔离默认 `none`（B4-02 接管）。
  6. 排队：本阶段每个项目最多 1 个 `running` 的任务，其余 `queued`（B4-01 替换为调度器）。
  7. 启动 Goal Runner；发 `session_started` 事件（B2-05）。
  - `cancel`：暂停 runner → 中止流 → GoalPlan `cancelled` → 子会话保留 → 事件 `cancelled`。
  - `list` / `get`：`projectWorkSession` 投影；`get` 的 `report` 由 GoalPlan 结果、验收报告、证据索引组装为 `SessionReport`。
- **必须新增的测试**（用脚本化执行器）：开任务全链路；模型不可用时不建任何对象；只读任务写入被拒；排队与出队顺序；取消；幂等重放不重复建；同会话单活跃约束不被触发（每个任务一个子会话）。
- **退出条件**：测试通过。

---

## B2-05 EventMapper 与项目收件箱

- **级别**：B。**规模**：M。**依赖**：B1-07。
- **目标**：任务侧的事实变化映射成 `DelegationEvent`，写进项目收件箱；至少一次投递 + 去重；为代理唤醒提供合并窗口。
- **必读**：分层文档 §5.1–§5.3。
- **代码锚点**：`goal-plan-store.mjs` 的变更通知（`onChange` / `.changes.jsonl`）；`approval-store.mjs`（B1-03）；`conversation-store` 的变更通知；`goal-runner.mjs` 的 runner 状态与 `runTrace`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/event-mapper.mjs`、`project-inbox.mjs` 与测试；`data-store.mjs`（`projectRuntime` 已由 B1-03 登记，这里只使用）。
- **实现要点**：
  - 事件种类：`session_started`、`progress`（只在叶子任务完成时，节流 30 秒）、`needs_user`（`approval` / `question` / `plan_approval`）、`result_ready`（验证结束，带结论）、`failed`、`cancelled`、`interrupted`、`user_intervened`（用户在任务现场直接介入）、`stalled`（B3-08 产生）。
  - `eventId = sha256(sessionId + kind + 版本号或 approvalId)`，同一事实只产生一个 id。
  - 收件箱 `project-runtime/<workspaceId>/inbox.jsonl` 追加写；`inbox-cursor.json` 只在代理唤醒回合**成功结束**后推进；重复 `eventId` 丢弃。
  - 合并：同一项目 2 秒窗口内的事件合成一批交给唤醒（窗口可配置）。
  - 文件超过 20 MB：把已消费且早于 7 天的事件归档为 `inbox-<日期>.jsonl.gz`。
- **必须新增的测试**：id 确定性；去重；游标只在成功后推进（失败回合后重放同一批）；合并窗口；归档后游标仍正确；进程重启后从游标继续。
- **退出条件**：测试通过。

---

## B2-06 输入队列与宿主租约

- **级别**：A（ADR 85 决策 1、2）。**规模**：M。**依赖**：B1-06。
- **目标**：所有入口的用户输入经持久队列进入机器人对话；每个项目只有一个宿主在运行。
- **代码锚点**：`packages/runtime-node/src/goal-runner.mjs` 的 `canRunPlan` 注入点；`agent-host/goal-runner-host.mjs`（桌面的 `canRunPlan`）；`apps/tui/src/goal-runner-adapter.ts`（TUI 的 `canRunPlan` 按当前会话归属）；`conversation-store` `appendMessage`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/input-queue.mjs`、`host-lease.mjs` 与测试；`goal-runner-host.mjs`（`canRunPlan` 接租约）；`apps/tui/src/goal-runner-adapter.ts`（任务计划一律不推进，直到 B5-01）；`main.mjs`（只改装配：退出前释放租约）。
- **实现要点**：
  - `submitInput(input)`：`inputId` 由提交方生成（UUID）；追加到 `input-queue.jsonl`；同一 `inputId` 第二次提交返回首次结果。
  - 消费者（只在宿主上）：按顺序读游标之后的输入 → 写入代理对话（消息 id 由 `inputId` 派生，重复写幂等）→ 推进 `input-cursor.json` → 通知 ProjectAgentRunner。
  - 租约：按 ADR 85 决策 1。一个进程内一个心跳定时器服务所有租约；`before-quit` 时释放；获取失败时本进程对该项目只做客户端。
  - `canRunPlan(plan)`：带 `delegationOrigin` 的计划只在持有该项目租约时返回 `true`；其他计划保持原逻辑。
  - beta.2 中桌面在开关打开且该项目有机器人时获取租约；TUI 在 B5-01 前从不获取，所以不会推进任务计划。
- **必须新增的测试**：队列幂等、顺序、崩溃后从游标恢复（写对话成功但游标未推进的情况不产生重复消息）；租约获取 / 心跳 / 过期接手 / 正常释放 / 两个进程竞争（用两个子进程测）；`canRunPlan` 对任务计划与普通计划的判定；TUI 不推进任务计划。
- **退出条件**：测试通过；交接报告附架构影响（新运行态文件、Goal Runner 推进条件变化）。

---

## B2-07 ProjectAgentRunner

- **级别**：A。**规模**：L（可拆 B2-07a actor 与邮箱，B2-07b 回合装配与失败处理）。**依赖**：B2-04、B2-05、B2-06。
- **目标**：每个项目一个单线程代理：用户输入触发用户回合，收件箱事件触发唤醒回合；用户输入可以抢占唤醒回合。
- **必读**：分层文档 §6.5–§6.8；ADR 80 决策 7。
- **代码锚点**：`agent-host/agent-turn-executor.mjs`（B1-02）；`packages/runtime-node/src/model-router.mjs`（B1-09）；`project-inbox.mjs`、`input-queue.mjs`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/runner.mjs`、`agent-turn-plan.mjs` 与测试；新建 `apps/desktop/electron/main/project-agent/project-agent-host.mjs`（桌面装配：为持有租约的项目创建 runner）。
- **实现要点**：
  - 邮箱三类：`user_inputs`（来自输入消费者）、`events`（来自收件箱的合并批）、`timers`（B3-05 小结、B4 目标）。同一时刻只跑一个回合。
  - 用户回合：把尚未回应的全部 `user_input` 一起交给代理；轮次上限 10、工具调用上限 20。
  - 唤醒回合：处理一批事件；轮次上限 6、工具调用上限 12。
  - 抢占：唤醒回合进行中来了用户输入 → 在下一个安全点（两次工具调用之间）中止唤醒回合，未处理的事件并入紧接着的用户回合；游标不推进。用户回合进行中来了新输入 → 排在当前回合之后（插话语义在 B3-02 细化）。
  - 回合参数：`mode: 'project_agent'`、`turnProfile.role: 'project_agent'`、模型 = `resolveRoleModel('project_agent')`、sink = BroadcastSink；上下文输入由 B2-11 的来源组装（`turnProfile.context`）。
  - 可见输出只有 `post_reply`：用户回合结束时若没有任何 `post_reply`，把最终文本作为回复挂到本回合所有输入上，并标 `fallback: true`；唤醒回合没有 `post_reply` 视为「不需要说话」（需要你类事件由 ReplyComposer 另行生成卡片，不依赖模型）。
  - 回合的工具调用与结果写为 `agent_turn` 消息，保证下一回合有连续上下文。
  - 失败：Provider 错误按 ADR 30 重试；仍失败时在对话里写 `system_card`「代理暂时不可用：原因」带「重试」；输入已写入对话，重试即重跑该回合。
  - 状态投影：`idle / thinking / waiting_provider / error`，供界面显示「思考中」。
- **必须新增的测试**（脚本化执行器）：用户回合 → 调用 `spawn_session` → 事件回流 → 唤醒回合 → `post_reply`；抢占；兜底回复；失败与重试；同一项目不并发两个回合；两个项目互不阻塞。
- **退出条件**：测试通过；真实模型跑通一次全链路（交接报告附对话截图）。

---

## B2-08 ReplyComposer 与卡片

- **级别**：A。**规模**：M。**依赖**：B2-07。
- **目标**：代理回复总是锚定、带可核对的标记；卡片只由运行时投影生成，模型不能伪造。
- **必读**：运行时契约 §2.5–§2.7；ADR 80 决策 7、8。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/reply-composer.mjs`、`card-projection.mjs` 与测试。
- **实现要点**：
  - `post_reply` 校验：`replyTo` 必须是本对话已有的 `user_input`（或 `proactive: true`）；`sources` 必须是本项目的 sessionId。
  - `AgentReplyMeta` 由运行时填：`replyTo`、`sources`、`verdictRef`（来源任务的最新结论）、`memoryUsed`（本回合上下文来源实际渲染的记忆 id，B2-11 提供）、`memoryLearned`（本回合 `memory_remember` 写入的 id）、`surfacing`（`decideSurfacing` 结果）。
  - 卡片种类（全部从投影生成）：`approval`（待批准）、`question`（任务提问，或代理 `post_reply.question` 的选项）、`confirm_result`（签收需要用户确认）、`readme_offer`（B2-12 空白机器人）、`agent_unavailable`（B2-07）。每张卡有稳定 `cardId` 与 `resolvedState`，同一事实只生成一张。
  - 卡片动作只调用已有 IPC：批准 / 拒绝 → `project-agent:decide-approval`；回答问题 → `project-agent:submit-input`（带 `answerTo: cardId`）；确认结果 → 签收接口（B2-09）。
- **必须新增的测试**：锚点校验；伪造 `sources` 被拒；标记与卡片全部可由投影重算；同一事实只一张卡；卡片解决后状态持久。
- **退出条件**：测试通过。

---

## B2-09 验证结论与策略签收

- **级别**：A（ADR 80 决策 8）。**规模**：M。**依赖**：B2-08。
- **目标**：任务结束后由运行时计算结论；满足策略时代签，否则变成「需要你确认」。
- **代码锚点**：`verification-verdict.mjs`（B1-07）；`goal-plan-store.mjs` 的 `resultAcceptance` 与 `goalPlansRevise`；`packages/protocol/src/acceptance-close-gate.ts`；`goal-acceptance-report.mjs`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/acceptance.mjs` 与测试；`goal-plan-store.mjs`（`resultAcceptance.acceptedBy` 字段）；`session-supervisor.mjs`（结束时调用）。
- **实现要点**：
  - 结论只认宿主事实（验证闸、证据索引、测试 / 命令结果），不认模型自述。
  - 签收策略来自机器人档案（默认 `auto`）。`confirm` 的原因：结论不是 `passed`；非只读任务改动文件超过 20 个；包含不可逆操作；用户在锚点消息里要求确认；本项目策略为 `confirm`。
  - 顺序：代理必须先发出引用该任务的回复，运行时才执行代签；代签写 `resultAcceptance { acceptedBy: 'policy', acceptedAt, verdictRef }`，经关闭闸门。
  - 不接受模型传来的任何「用户已同意」参数。
- **必须新增的测试**：每个 `confirm` 原因；回复之前不代签；代签写入字段完整；用户确认路径写 `acceptedBy: 'user'`。
- **退出条件**：测试通过。

---

## B2-10 记忆存储与基础工具（MM1）

- **级别**：A（ADR 81）。**规模**：M。**依赖**：B1-06、B1-08。
- **目标**：记忆能写、能查、能撤；jsonl 为真源，索引可重建。
- **必读**：ADR 81；记忆架构文档 §4、§9、§10。
- **代码锚点**：`packages/runtime-node/src/sqlite/*`（B1-08）；Shell 脱敏规则（`rg "redact" packages/runtime-node/src apps/desktop/electron/main -l` 定位 shell-redaction）。
- **允许改动**：新建 `packages/runtime-node/src/memory/{memory-store.mjs, memory-index.mjs, memory-redaction.mjs, memory-snapshot.mjs, memory-provider.mjs}` 与测试（Provider 本体在 runtime-node，供 TUI 复用）；`packages/runtime-node/src/project-agent/tool-specs.mjs`（追加记忆工具定义）；新建 `runtime-gateway/local-memory-provider.mjs`（再导出）、`tools/memory-tool-definitions.mjs`、`tools/prompts/memory/*.md`；`data-store.mjs`（登记 `userMemory`）；`project-agent-mode-gate.mjs`（白名单追加）。
- **实现要点**：
  - 存储：项目记忆 `projects/<workspaceId>/memory/items.jsonl`，用户偏好 `memory/items.jsonl`；追加写，按 id 折叠。
  - 工具（只在 `project_agent` 可见）：`memory_search { query, scope?, limit? }`、`memory_remember { text, kind, anchorMessageId?, pinned? }`、`memory_forget { id, reason }`。
  - 信任：带 `anchorMessageId` 且指向 `user_input` → `stated`；由 SessionSupervisor 用任务证据写入 → `verified`（必须有 `sourceRefs`）；其他情况本卡直接拒绝（`inferred` 与准入策略在 B3-07）。
  - 脱敏：命中密钥 / 令牌规则直接拒绝写入，返回原因；不写半截。
  - `forget` 只改状态为 `forgotten`，可恢复。
  - 快照：`createSnapshot(workspaceId)` 记录当时所有 `active` 条目 id，写 `projects/<id>/memory/snapshots.jsonl`，返回 `snapshotId`；SessionSupervisor 开任务时调用。
- **必须新增的测试**：记忆文档 §15 中存储、`stated` 判定、撤销恢复、索引重建、敏感信息相关条目；无锚点写入被拒；快照内容稳定。
- **退出条件**：测试通过。

---

## B2-11 上下文来源

- **级别**：A（System Context 顺序与准入）。**规模**：M。**依赖**：B2-07、B2-10。
- **目标**：代理回合与任务回合需要的上下文全部经注册的 Context Source 进入，层级正确。
- **代码锚点**：`packages/system-context/src/prompt-source-registry.mjs`（接口：`id`、`layer`、`observe()`、`render()`）；`prompt-assembler.mjs` `createDefaultPromptSourceRegistry`（79，continuity 在 102）；`sources/continuity-source.mjs`（L7 写法）；`sources/explorer-*` / `verifier-*`（按模式生效的写法）；`scripts/check-architecture-governance.mjs` `assertSystemContextProtocolContracts`。
- **允许改动**：新建 `packages/system-context/src/sources/{project-agent-source.mjs, project-roster-source.mjs, project-memory-source.mjs, work-session-origin-source.mjs}` 与测试；`prompt-assembler.mjs`（注册）；`packages/system-context/src/index.mjs`（导出）；`llm-chat-service.mjs`（把 `turnProfile.context` 传给 `assembleSystemContext`，不加参数）；治理脚本中该检查的锚点（仅当检查要求时）。
- **实现要点**：

| 来源 | 层 | 何时生效 | 内容 |
|---|---|---|---|
| `project-agent` | `L1_AGENT` | `role === 'project_agent'` | 代理的工作规则：只读 + 调度；回复必须用 `post_reply` 并锚定；写代码交给任务；不确定就问；不复述工具原文 |
| `project-roster` | `L7_CONTINUITY` | 同上 | 当前任务名册（状态、标题、最近事件、需要你）；本次唤醒的事件批 |
| `project-memory` | `L7_CONTINUITY` | 同上 | 项目简报（固定项 + 职责 + 高频事实）与用户偏好；返回实际渲染的记忆 id 给 ReplyComposer |
| `work-session-origin` | `L7_CONTINUITY` | `role === 'work_session'` | 委托来源摘要、锚点原文、冻结记忆快照条目、只读约束 |

  - 规则文本放资源文件；事实内容（名册、记忆、快照）只进 L7，不进 L0–L6。
  - 任务回合的 L6 模式提醒沿用 goal 模式。
- **必须新增的测试**：各来源只在对应角色生效；层级正确；记忆 id 回传；普通会话的系统上下文逐字不变（快照对比）。
- **退出条件**：测试通过；`architecture:check` 通过。

---

## B2-12 机器人档案、身份与生命周期

- **级别**：A（ADR 84、85 决策 7、10）。**规模**：M。**依赖**：B1-06、B2-04。
- **目标**：每个工作区对应一个机器人；机器人有名字与头像；新建支持绑定文件夹与受管文件夹；首次打开「熟悉项目」。
- **必读**：ADR 84；ADR 85 决策 7、10；产品稿 §1.1。
- **代码锚点**：`workspace-application-service.mjs`（`addWorkspace` 的目录选择、`removeWorkspace`）；`project-registry.mjs`（B1-06）；`packages/runtime-node/src/goal-delivery-binding.mjs` `resolveWorkspaceHead`（只读 git 信息）。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/bot-profile-store.mjs`、`bot-lifecycle.mjs`、`familiarize-template.mjs` 与测试；新建 `apps/desktop/electron/main/project-agent/managed-folder.mjs` 与测试。
- **实现要点**：
  - 档案 `projects/<workspaceId>/profile.json`（ADR 85 决策 7）；`ensureBot(workspaceId)` 懒创建档案与代理对话（`role: 'project_agent'`），幂等；开关关闭时不创建。
  - 名字默认取文件夹名，≤ 40 字；头像默认 `generateAvatar(workspaceId)`；「换一个」= 带盐重新生成；上传图片由 main 弹窗选择，只收 png / jpg / webp ≤ 1 MB，复制到 `projects/<id>/avatar.<ext>`。
  - 受管文件夹：名字去掉路径分隔符与控制字符，禁止 `.` / `..` 与系统保留名；根目录 `projectAgent.managedRoot`（默认 `~/Peer/`，不存在则创建）；重名追加 `-2`、`-3`…；创建后注册为工作区。
  - 熟悉项目：非空文件夹开一个只读任务（`kind: 'research'`），只用文件读取工具；git 信息由宿主用 `resolveWorkspaceHead` 等只读函数提供；产出写为 `verified` 记忆（带 `sourceRefs`），不确定的点由代理提问。
  - 空文件夹（只有点文件）：不开任务，代理直接问「这个机器人主要负责什么」；回答写 `stated` 职责记忆并固定；随后生成 `readme_offer` 卡，同意后开写 README 的任务。
  - 删除：从工作区列表移除（沿用 `removeWorkspace`）；档案标 `archived`（可恢复），不删记忆；受管文件夹需要二次确认，确认后移到系统废纸篓（不直接删除）。
- **必须新增的测试**：懒创建幂等；开关关闭不创建；头像确定性；名字清洗；重名序号；删除不删文件夹；受管文件夹二次确认后进废纸篓（注入假实现）；熟悉项目任务没有写能力；写入记忆 `verified` 且有证据；空白机器人的职责记忆 `stated` 且固定。
- **退出条件**：测试通过。

---

## B2-13 项目代理应用服务与 IPC

- **级别**：B。**规模**：M。**依赖**：B2-07、B2-12。
- **目标**：渲染层需要的全部数据与动作经一个应用服务、一组类型化 IPC 提供。
- **代码锚点**：`ipc/register-*-ipc.mjs` 的写法；`ipc/register-all.mjs`；`apps/desktop/electron/ipc/channels.mjs`；`apps/desktop/scripts/sync-ipc-catalog.mjs`；`bootstrapPreloadApi.ts`；`clientApi.ts`；`main.mjs` `registerDesktopIpcHost()`（2299–2617）。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/bot-directory.mjs` 与测试（列表、详情、读对话、任务、待批准、未读游标的数据汇集与投影，宿主无关；TUI 客户端与远程入口在 B5 复用）；新建 `apps/desktop/electron/main/project-agent/project-agent-application-service.mjs` 与测试（薄层：调用 `bot-directory`、输入队列、生命周期）；新建 `ipc/register-project-agent-ipc.mjs` 与测试；`register-all.mjs`；`channels.mjs`（按脚本流程）；`bootstrapPreloadApi.ts`；`clientApi.ts`；`main.mjs`（只加装配调用，同时删掉等量旧代码或把装配放进 `project-agent-host.mjs`，保证净增 ≤ 0）。
- **实现要点**：
  - 通道（版本计划 §8）：`project-agent:list`、`get`、`create`（`{ kind: 'bind' } | { kind: 'managed', name }`）、`update-profile`、`delete`、`submit-input`、`read-conversation`（分页，按 `kind` 过滤）、`list-sessions`、`get-session`、`cancel-session`、`list-approvals`、`decide-approval`、`mark-read`、`search`（本阶段搜名字、预览、任务标题）；事件 `project-agent:changed`（100 ms 防抖，带变化的 `workspaceId[]`）、`project-agent:conversation-changed`。
  - `BotListItem` 在 main 用 `projectBotListItem` 计算：最后一条可见消息预览（`agent_reply` / `user_input` / `system_card`，≤ 80 字）、时间、需要你数（未解决的批准 + 提问 + 确认）、进行中数、未读数（读游标之后的可见消息数；游标存 `project-runtime/<id>/read-cursor.json`）。
  - 开关关闭时：所有 `project-agent:*` 通道返回 `{ ok: false, code: 'PROJECT_AGENT_DISABLED' }`，不创建任何文件。
- **必须新增的测试**：每个通道；开关关闭时的拒绝与零写入；列表项计算；防抖。
- **退出条件**：测试通过；`ipc:check` 通过。

---

## B2-14 界面：机器人列表壳与新建机器人

- **级别**：B。**规模**：M。**依赖**：B2-13、B1-11。
- **目标**：开关打开后，应用主界面换成机器人列表壳；可以新建机器人。
- **必读**：ADR 84；产品稿 §2；demo `design/product/project-agent-demo.html`（交互参照，不是实现代码）。
- **代码锚点**：`App.tsx`（主布局 939–1182）；`WorkbenchContext.tsx`（宽度常量、拖拽写法）；`app/components/Drawer*`；`styles/tokens.css`、`styles/motion.css`；`ConversationSearchPalette.tsx`（搜索交互参照）。
- **允许改动**：新建 `apps/desktop/renderer/src/project-agent/{BotListShell.tsx, BotList.tsx, BotRow.tsx, BotAvatar.tsx, NewBotSheet.tsx, MeMenu.tsx}`、`project-agent/state/{botListState.ts, useBotList.ts}`、`project-agent/styles/*.css` 与测试；`App.tsx`（只加「开关打开 → 渲染 `BotListShell`」一个分支）；i18n（`projectAgent.list.*`）。
- **不许改动**：`Sidebar.tsx`、`GlobalWorkbenchPage`、`TaskOverviewPage`、`WorkbenchPanel` 的行为。
- **实现要点**：
  - 布局：左列 292 px（可拖 240–360，宽度存本机偏好）+ 主区；档案抽屉在主区右侧（B2-16）。
  - 列表行：头像 · 名字 · 预览 · 时间；右侧状态：需要你深色数字角标 / 未读小圆点 / 进行中转圈；按最近活动排序（`sortBotList`）。
  - 顶部：品牌、新建（+）、搜索框（输入即过滤，调用 `project-agent:search`）、「需要你 N」筛选。
  - 底部：「我」菜单——设置、自动化、能力（插件 / 技能 / MCP）、历史对话（B3-09 前隐藏）。
  - 新建：两条路（选文件夹 / 输入名字建空白机器人）；名字校验提示与 main 一致；创建后自动进入该机器人。
  - 键盘：上下选择、回车进入、`⌘N` 新建、`⌘F` 聚焦搜索；角标有可读文本。
  - 所有状态来自 IPC 投影；列表订阅 `project-agent:changed` 局部刷新。
- **必须新增的测试**：`botListState` 纯函数（排序、筛选、搜索合并、选中保持）；开关关闭时 `App.tsx` 走旧布局（源码契约）；`Sidebar.tsx` 行数不变。
- **退出条件**：测试通过；截图（空状态、多机器人、需要你筛选、新建两条路）附在交接报告。

---

## B2-15 界面：机器人对话

- **级别**：B。**规模**：L（可拆 B2-15a 消息列表与气泡，B2-15b 输入与引用）。**依赖**：B2-13。
- **目标**：与机器人的对话：锚定回复、处置标记、来源 / 结论 / 记忆标记、卡片、主动消息的时间分隔、输入与引用。
- **代码锚点**：`chat/thread/VirtualChatTurnList` 与 `virtualizeChatTurns`（虚拟列表参照）；Markdown 渲染组件（`rg "Markdown" apps/desktop/renderer/src/chat/components -l`）；`ComposerDraftControls`（草稿隔离写法参照）；`SelectionQuoteAction`（划词引用参照）；`conversationStore.ts`、`useConversationStreamRouter.ts`（只读复用，不改）。
- **允许改动**：新建 `project-agent/conversation/{BotConversation.tsx, BotMessageList.tsx, ReplyBubble.tsx, UserBubble.tsx, CardView.tsx, BotComposer.tsx, QuoteChip.tsx}`、`project-agent/state/{botConversationState.ts, useBotConversation.ts}` 与测试；i18n（`projectAgent.chat.*`）。
- **不许改动**：`ChatSurface.tsx`、`conversationStore.ts` 的现有行为。
- **实现要点**：
  - 数据：`project-agent:read-conversation` 分页（首屏 50 条，上滑加载更早）；订阅 `conversation-changed` 追加。
  - 只显示 `user_input`、`agent_reply`、`system_card`；`agent_turn` 不显示。
  - 回复气泡：回复条（点击滚动到锚点并高亮）、正文（Markdown）、标记芯片（来源 → 打开档案定位任务；结论；参考了 N 条记忆；新记住 N 条；送达方式）、卡片。
  - 用户气泡：处置标记（本阶段只有「已回复」；B3-02 补全）。
  - 时间分隔：相邻消息间隔超过 10 分钟、或主动消息，插入分隔（「今天 09:00 · 今日小结」这类标签来自消息元数据）。
  - 代理状态：`thinking` 时显示「思考中…」；不显示代理回合的内部文本。
  - 输入：回车发送、Shift+回车换行、输入法组合中不发送；发送即调用 `submit-input`（客户端生成 `inputId`），本地先显示为「发送中」，收到 `conversation-changed` 后替换；失败可重发（同一 `inputId`）。
  - 引用：选中回复里的文字 → 「引用」→ 输入框上方出现引用芯片，发送时带 `quoteRefs`。
  - 列表窗口化：超过 200 条时只渲染可视区附近。
- **必须新增的测试**：`botConversationState` 纯函数（分页合并、乐观发送替换、时间分隔、按 kind 过滤）；卡片动作只调用约定 IPC（源码契约）；`ChatSurface.tsx` 行数不变。
- **退出条件**：测试通过；截图附在交接报告。

---

## B2-16 界面：档案抽屉与任务现场

- **级别**：B。**规模**：M。**依赖**：B2-13。
- **目标**：按需滑出的档案：概况 · 任务 · 目标 · 记忆 · 设置；点「来源」定位任务现场。
- **代码锚点**：`app/components/Drawer*`（焦点管理与动效写法）；`App.tsx` 中「继续讨论」嵌套 Drawer 渲染 `ChatSurface` 的写法（任务现场的大窗口复用这个模式）；`GoalPlanPanel.tsx`（证据列表参照，只读复用）。
- **允许改动**：新建 `project-agent/drawer/{BotProfileDrawer.tsx, OverviewTab.tsx, TasksTab.tsx, SessionDetail.tsx, ObjectivesTab.tsx, MemoryTab.tsx, BotSettingsTab.tsx}`、`project-agent/state/drawerState.ts` 与测试；i18n（`projectAgent.drawer.*`）。
- **实现要点**：
  - 宽 380 px；窗口宽度 ≥ 960 px 时把对话区推开，否则覆盖；Esc 关闭并把焦点还给触发按钮；打开状态按机器人记住。
  - 概况：绑定文件夹（「在访达中显示」经 IPC）、项目简报（来自记忆）、在推进的任务、签收策略、对话模型。
  - 任务：分组（需要你 / 进行中 / 排队 / 已完成）；详情：状态、锚点、冻结的模型、结论、证据、最近进展；「打开现场」用嵌套 Drawer 打开子会话的 `ChatSurface`（沿用 App 已有模式，不改 `ChatSurface`）；在现场发的话记为 `user_intervened` 事件（B2-05）。
  - 目标：本阶段显示「目标将在后续版本开放」。
  - 记忆：本阶段只读列表（B3-06 补全操作）。
  - 设置：名字、头像（换一个 / 上传）、签收策略（自动 / 需要我确认）、模型范围与覆盖（读写 B1-09 的 `ProjectModelPolicy`）、删除机器人（受管文件夹二次确认）。
- **必须新增的测试**：`drawerState`（打开 / 定位 / 记忆打开状态）；设置项只经 IPC 写入；焦点归还（源码契约）。
- **退出条件**：测试通过；截图附在交接报告。

---

## B2-17 通知与托盘改由送达策略驱动

- **级别**：A（ADR 85 决策 4）。**规模**：S。**依赖**：B2-07。
- **目标**：机器人模式下系统通知只来自 `decideSurfacing`；任务 GoalPlan 不再直接发通知；托盘角标为需要你总数。
- **代码锚点**：`task-notification-broker.mjs`（`createTaskNotificationBroker`，40）；`task-notification-policy.mjs`（`decideTaskNotification`，228；`NOTIFIABLE_STATUSES`）；`task-notification-receipt-store.mjs`；`tray-controller.mjs`。
- **允许改动**：`task-notification-broker.mjs` 与测试（跳过带 `delegationOrigin` 的计划）；新建 `apps/desktop/electron/main/project-agent/project-agent-notifier.mjs` 与测试；`tray-controller.mjs`（开关打开时角标取需要你总数）。
- **实现要点**：
  - `interrupt` → 系统通知（标题 = 机器人名，正文 = 回复首句或卡片摘要，≤ 60 字）；点击打开该机器人对话并滚到该消息；按 `eventId` 去重（复用回执存储）；用户正在前台看这个机器人时不弹。
  - B3-05 之前主动性按「标准」档计算。
  - 开关关闭时，通知与托盘行为与 beta.1 一致。
- **必须新增的测试**：任务计划不触发旧通知；`interrupt` 触发一次且去重；前台同机器人抑制；开关关闭时旧行为不变。
- **退出条件**：测试通过。

---

## B2-R 发布 `0.1.0-beta.2`

- **步骤**：版本计划 §10 检查单；发布说明写明「项目代理需在 设置 → 开发者 打开」。
- **证据**：版本计划 §12.1 beta.2 一行：3 个真实项目各一次全链路；代理无法写文件的测试；熟悉项目记忆可查可撤；开关关闭零变化的测试。
- **退出条件**：prerelease 生成；版本计划 §5.2 更新。
