# 85. 项目代理的宿主、输入与多入口（0.1.0 落地边界）

创建时间：2026-09-26
最后更新：2026-10-04（补充对话流式与停止边界）

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
- `knowledge/decisions/75-remote-read-preflight.md`（远程只读预检，已按代码补记）
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
12. **自定义头像图片只通过受限的展示接口进入渲染层。** 档案仍只持有相对图片引用 `avatar.<ext>`，不保存绝对路径或数据 URL。桌面主进程按已登记的 `workspaceId` 查档案，并从该项目目录读取其头像；只接受已保存的 PNG、JPEG、WebP，大小不超过 1 MiB。渲染层通过专用只读 IPC 取得有界的 `data:` URL，用于显示图片，不传入文件路径，也不能借这个接口读取任意本机文件。更换头像仍走现有的本机文件选择与档案更新通道；头像身份不改变代理能力、权限或 Evidence。
13. **头像运行表情只读真实状态。** 当前桌面宿主持有的项目代理 runner 将 `idle / thinking / waiting_provider / error` 作为临时只读状态附在机器人列表项上，状态变化沿现有 `project-agent:changed` 通知刷新，不另建能力执行或权限通道。没有本进程 runner 时状态为未知，不由渲染层猜测为正在思考。`needsYou` 继续来自卡片、批准和任务投影；回复到达、悬停、点击的短暂表情是渲染层事件，不能冒充运行状态或 Evidence。状态不写入档案，也不改变代理决策。

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

## RC-03 诊断导出边界（2026-10-02，Accepted）

负责人已授权自主完成所有 RC 修复和自测。本节在代码实现前确定新的 IPC/元数据边界（A级）；装配与投影实现为 B级。诊断是用户发起的本机可观测性操作，不能改变租约、输入消费、批准、调度或探测状态，也不向模型投影工具。

- `project-agent:diagnostics`只授予已登记 main 窗口顶层 frame 与精确本地 origin；Quick Chat、Popover、远程均拒绝。协议请求只选择读取/导出，不能提供文件路径、工作区路径或任意文件名；scope 来自当前已登记机器人。
- 可移植诊断 Module 投影每个机器人的租约持有方、输入深度与游标、收件箱游标/最近 200 事件、待批准、调度槽位与排队、目标/Watch 状态、最近 20 次代理回合耗时/结果。深投影只允许固定枚举/数字/经校验时间，标识与文本以长度+SHA256 表示；绝对路径、正文、工具参数/结果、凭据、原错误文本永不进入导出。工作区自身路径投影为`.`，范围内的引用仅保留相对路径；范围外路径不导出。
- 数据来自既有 store/host 的只读快照，不调用 consume、commit、recover、reconcile、reserve 或模型。没有宿主/旧记录缺少时间字段时返回明确 unknown/null，不能估算或冒充已测量。损坏来源以固定错误码标注，不能返回携带路径/正文的异常 message。
- 从本版开始，既有`agent_turn`消息的 meta 追加可选`diagnosticTiming`：startedAt/finishedAt/durationMs/outcome。在同一代理作业内实测，包含该作业中的模型重试，结果限 done/error/preempted；不改写已有历史，不把回合完成当用户签收/Evidence。已处置且没有可写消息的作业不会生成虚假的持久完成事实。
- 桌面 Adapter 由 main 原生保存对话框选择目标，先脱敏投影后原子写单个 JSON；取消不写，失败保留原目标，不返回原始错误。renderer 仅显示脱敏投影/结果，不使用 fs 或权限真值。输出不是新的自动存储目录；现有数据登记不变。

验证：真实来源含密钥模式/绝对路径/原文的恶意夹具、损坏源、旧回合缺字段、200/20 边界、原状态文件与游标校验和不变；IPC 合法 main 与外来窗口/frame 拒绝；保存取消/失败/原子写；真实 Electron 导出脱敏样本。


## RC03 只读注册表补充（2026-10-02，Accepted）

诊断自审发现 Registry.get/list 在注册表损坏时会备份并修复，这不符合诊断只读合同。新增 Registry.diagnosticSnapshot：每次读取及完整验证原文件，缺失返回空数组，损坏抛出固定 CORRUPT_REGISTRY；不备份、不修复、不创建目录、不更新内存身份。返回条目副本。原 get/list/sync 的恢复行为保持。Desktop 诊断只从该快照与只读 active profile ID 交集读取项目；注册表损坏投影 PROJECTS_UNAVAILABLE，导出本身不得触发修复。原 resolveConversationId 已有只读 profile 查询可沿用。

## RC 验证补齐：快捷聊天窗口准入（2026-10-02，Accepted）

真实Electron验证发现B3-11机器人快捷聊天已调用project-agent:list和project-agent:submit-input，但catalog未授予quick-chat角色，导致列表与发送被拒绝。按既有产品入口补齐这两个通道的quick-chat角色；这属于A级窗口准入修复，负责人已授权自主收口全部RC，未引入新能力/工具/IPC。主进程仍以已注册窗口、顶层frame和精确本地origin为准，renderer的URL或role字符串不构成授权真源。

快捷窗口只获机器人目录及输入提交权限；档案修改/删除、任务批准、证据读取、诊断仍为主窗口专属。settings:get仍不开放，沿已有settings:get-sync获取最新只读设置，公开getSettings保持Promise契约。quick-chat-popover角色不继承机器人通道。输入surface为quick_chat，经原inputQueue→租约宿主→Capability/PermissionGrant/Evidence链，成功回执仅代表持久化。

验证必须覆盖合法QuickChat列表/实际输入消费、陌生窗口/子frame/错误origin拒绝、Popover拒绝、批准等通道拒绝，并在真实Electron smoke中不出现角色拒绝日志。

## RC 对话流式投影与停止边界（2026-10-04，Accepted）

负责人明确要求恢复真实流式、精细参照 ChatGPT 的整个交互，沿既有全部 RC 修复自主推进授权。本节在实现前确定 A 级协议与停止语义，实施卡为 `rc-chat-streaming.md`。

- ProjectAgentRunner 在本机持有有界、短暂的 ProjectAgentActivity。身份包含 workspaceId、conversationId、turnId、单调 revision、输入锚点；阶段、可见文本草稿、实际工具调用的名称/进行或结束状态来自同一 TurnSink。内部 reasoning 不进入正文；工具参数、结果、路径、权限与 Evidence 不进入这个摘要。只对用户回合展示正文草稿；静默/小结/自动唤醒仍按原送达策略。
- 普通文本使用真实 delta；post_reply 的 text 使用提供方已有工具参数进度 seam 解码完整 JSON 字符串前缀。它是生成中的预览，不是 Tool Result、签收或任务成功。失败校验或 suppressed 立即撤掉对应草稿。正式回复继续通过 ReplyComposer 和既有能力/权限/Evidence 链；不改变提示、校验或重复事实治理。没有流式参数的提供方仍可展示真实等待/工具状态，不能对完整回复做假的逐字动画。
- `project-agent:activity` 推送有界快照，最多每 50ms 一次，开始/终态立即刷新。`read-conversation` 返回可选活动快照供窗口重开/机器人切换接续；推送与分页以 revision 合并，终态与持久 turn 交接后去掉预览，避免重复。逐片事件不触发目录、任务、记忆或历史文件重读，不向旧 chat 流式监听器暴露完整代理工具参数。宿主丢失/关闭立即清理，不持久化进行中草稿。
- `project-agent:stop-response` 是主窗口专属命令，精确匹配 workspaceId + turnId 和本机有效租约，只 abort 当前用户回复。重复或过期停止不得影响下一回合、其他机器人、子任务、批准或能力权限。停止保存实际 agent_turn（含已经发生的工具结果）及明确的 agent_stopped 系统卡；部分文字标作未完成，不附任务成功/验收标记。停止不是提供方错误，不触发熔断；输入执行游标完成，重启不自动重放。用户可显式重新生成，沿已有 retry 入口，只允许最新停止/失败回合，新的回合用新的 turnId。
- Renderer 只表达这些事实：发送/收件回执在正文下方；生成中的段落与 SVG 工具提示在消息流内；正文到达就替代初始等待；输入框保留草稿且支持 IME/换行；生成时可停止。靠近底部才跟随，回看时保持位置并提供 SVG 回到最新入口，主动发送可回到底部。引用无左侧强调线、消息无光晕。工具进行中不得称已完成，正式过程/Evidence 控件在正式回复后出现。

验证覆盖首片早于完成、增量 JSON/转义/分片 unicode、校验失败/抑制、空文本/重试、停止竞态/租约/新输入/重启游标、切换和重连乱序、完成交接无重复、回看位置、真实窗口等待/流式/工具/停止/失败/长 Markdown。不能只用完整回复截图宣布流式已验证。
