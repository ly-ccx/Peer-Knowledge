# beta.3 可日用、默认开启（`0.1.0-beta.3`）

创建时间：2026-09-26
最后更新：2026-09-26

> 主题：项目代理从「能跑」到「好用」，并成为所有 beta 用户的默认界面。  
> 用户可见：需要你冒泡、插话、引用限定范围、按需披露与复核、主动性与今日小结、记忆进上下文与自动提取；旧工作区变机器人、旧会话进历史；经典界面开关；快捷对话 / Appshot / 搜索 / 托盘接入机器人。  
> 进入条件：beta.2 在真实项目上日用满一个版本周期；ADR 80 / 81 / 84 / 85 仍为 Accepted（期间如有修订已回写）。  
> 开关：B3-10 合入前仍受 `developer.projectAgentMode` 控制；合入后改为用户设置 `projectAgent.shell`。  
> 通用退出条件见 `README.md` §6（第 4 条「开关关闭零变化」在 B3-10 合入后改为「经典界面零变化」）。

并行关系：

```text
B3-01 ─┐
B3-02 → B3-03
B3-04
B3-05
B3-06 → B3-07
B3-08
B3-09 → B3-10 → B3-11
（除标注的箭头外均可并行；注意 README §4 热点文件冲突表）
```

---

## B3-01 需要你冒泡

- **级别**：A（运行时契约 §6、ADR 85 决策 3）。**规模**：M。**依赖**：B2-15、B1-03。
- **目标**：任务里需要用户做决定的三类事——批准、提问、计划批准——都冒泡到机器人对话与列表角标；在对话里或任务现场任一处解决，两处同时生效；重启后 `stale` 的批准可以一键「批准并继续」。
- **代码锚点**：`approval-store.mjs`（B1-03）；`card-projection.mjs`（B2-08）；`permission-gate.mjs`；`goal-runner.mjs` `resume()`；`ChatSurface` 里的 `PermissionGateStrip`（只读参照，不改）；`event-mapper.mjs`（B2-05）。
- **允许改动**：`card-projection.mjs`、`reply-composer.mjs` 与测试；`permission-gate.mjs`（一次性授权）；`session-supervisor.mjs`（计划批准）；`project-agent-application-service.mjs`（`decide-approval` 处理 `stale`）；渲染层 `project-agent/conversation/CardView.tsx` 与状态。
- **实现要点**：
  - 批准卡：显示能力、摘要、风险等级、任务名；按钮「允许」「本任务内都允许」「拒绝」；映射到已有授权时长（`once` / `task` / `denied`）。
  - 提问卡：任务 `request_user_input` 的问题与选项；回答经 `submit-input(answerTo)` → 代理用 `message_session(intent: 'answer')` 转交（代理不在线时由运行时直接投递并记 `user_intervened`，保证不因代理故障卡住）。
  - 计划批准：机器人档案新增 `planApproval: 'never' | 'writes' | 'always'`（默认 `never`）；需要时任务以 `awaiting_approval` 创建，生成计划批准卡（显示计划要点与完成标准）。
  - 两处同解：卡片与任务现场的权限条共享同一 `approvalId`；任一处决定后另一处 300 ms 内更新。
  - `stale` 批准：「批准并继续」→ 预置一次性授权（`capabilityId + argsDigest`，30 分钟内有效，只用一次）→ 恢复任务；恢复后同一调用到达时直接放行，不同参数仍然询问。
  - 冒泡送达：需要你事件一律 `interrupt`（不受主动性档位影响，静音也送达）。
- **必须新增的测试**：三类卡片生成；两处同解；一次性授权只匹配同一调用、只用一次、过期失效；计划批准路径；静音时需要你仍推送。
- **退出条件**：测试通过；真实运行一次重启后「批准并继续」的录屏或截图。

---

## B3-02 插话与处置

- **级别**：A（ADR 80 决策 7）。**规模**：M。**依赖**：B2-07。
- **目标**：任务进行中用户随时插话；代理自主决定是回答、并入进行中的任务、停止、取代、并行开新任务还是排队；每条用户消息都显示处置结果。
- **必读**：分层文档 §5.4、§8.3；运行时契约 §2.6。
- **代码锚点**：`delegation-provider.mjs`（`message_session`）；`goal-message-router.mjs`（`correction` 路由）；`projectMessageDispositions`（B1-07）。
- **允许改动**：`delegation-provider.mjs`、`tool-specs.mjs`、`session-supervisor.mjs` 与测试；`tools/prompts/delegation/*.md`；`project-agent-source.mjs`（规则补充）；渲染层 `UserBubble.tsx` 与状态。
- **实现要点**：
  - `message_session` 支持 `intent: 'answer' | 'amend'`：`amend` 作为「来自项目代理转达：用户说……」写入任务子会话，经 `goal-message-router` 的纠正路由在下一回合开始时生效；任务在等待用户时则直接作为回答。
  - 处置由运行时从本回合的工具调用推导（`projectMessageDispositions`），模型不能直接写处置：回答（只有 `post_reply`）/ 并入（`message_session amend`）/ 停止（`cancel_session`）/ 取代（`spawn_session` 带 `supersedes`，B4-03 前只停旧开新）/ 并行（`spawn_session`）/ 排队（`spawn_session` 进入排队）。
  - 用户气泡下显示处置标记，点击跳到对应任务。
  - 用户回合进行中又来新输入：当前回合结束后立刻开下一回合处理新输入；如果新输入明确要求「停」（由代理判断），代理在下一回合调用 `cancel_session`。
- **必须新增的测试**：每种处置的推导；`amend` 投递时机（运行中 / 等待中）；来源标注；标记显示。
- **退出条件**：测试通过；真实运行「并入」与「停止」各一次。

---

## B3-03 引用限定范围（AnchorScopeResolver）

- **级别**：A。**规模**：S。**依赖**：B3-02。
- **目标**：用户引用某条回复说话时，这句话的作用范围限定在那条回复涉及的任务；代理越界操作其他任务时被运行时拒绝。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/anchor-scope.mjs` 与测试；`delegation-provider.mjs`（校验）。
- **实现要点**：
  - 范围计算：`quoteRefs` / `replyTo` → 被引用消息 → 其 `sources` 与回复链上的 sessionId 集合；没有引用时范围 = 整个项目。
  - 本回合由带范围的输入触发时，`message_session` / `cancel_session` 指向范围外的任务 → `out_of_scope`（结构化错误，代理据此向用户确认）；`spawn_session` 不受限（新任务的锚点仍是这条输入）。
  - 处置标记 `out_of_scope` 显示「这句话针对的是『X』，没有影响其他任务」。
- **必须新增的测试**：范围计算（直接引用、回复链、无引用）；越界拒绝；新开任务不受限。
- **退出条件**：测试通过。

---

## B3-04 按需披露与复核

- **级别**：A（ADR 80 决策 8）。**规模**：M。**依赖**：B2-09。
- **目标**：代理默认只说结论；用户追问时给出验证细节与证据；用户要求时发起独立复核。
- **代码锚点**：`verification-verdict.mjs`；`goal-acceptance-report.mjs`；`GoalPlanPanel.tsx` 的证据列表（参照）；Verifier 的运行入口（`goal-runner-host.mjs`）。
- **允许改动**：`tool-specs.mjs`、`delegation-provider.mjs`（新增两个工具）与测试；`tools/prompts/delegation/*.md`；渲染层 `ReplyBubble.tsx`（证据芯片）、新建 `project-agent/drawer/AgentProcessView.tsx`（代理过程）。
- **实现要点**：
  - `get_verification_detail { sessionId }`：返回结论、逐项检查（名称、结果、证据引用）、执行与复核模型、是否同源、测试 / 命令输出摘要（截断到 2000 字，完整内容给证据引用）。
  - `verify_session { sessionId, focus? }`：用 `verifier` 角色发起一次独立复核（不同源优先），产生新结论事件；复核期间任务状态 `verifying`。
  - 证据芯片：点击在档案里打开证据（截图、命令输出、文件 diff）；证据内容由 main 读取，渲染层不直接读文件。
  - 代理过程：档案里可展开查看某条回复对应回合的工具调用与结果（`agent_turn`），只读。
- **必须新增的测试**：细节内容只来自宿主事实；复核产生新结论并更新卡片；证据读取经 IPC。
- **退出条件**：测试通过。

---

## B3-05 主动性与今日小结

- **级别**：A（ADR 80 决策 9）。**规模**：M。**依赖**：B2-17。
- **目标**：用户控制机器人多主动：全局档位、每个机器人覆盖（含静音）、安静时段；非紧急的事汇总成每天一次的小结。
- **必读**：运行时契约 §5.1.1 规则表；ADR 84 决策 8。
- **允许改动**：`decideSurfacing` 调用方（`reply-composer.mjs`、`project-agent-notifier.mjs`）；新建 `packages/runtime-node/src/project-agent/digest.mjs` 与测试；`tool-specs.mjs`、`delegation-provider.mjs`（`set_proactivity`）；`mode-policy.mjs`（白名单追加）；设置读写（`projectAgent.proactivity`、`projectAgent.quietHours`、`projectAgent.digestTime`）；渲染层设置分区与档案设置项；i18n。
- **实现要点**：
  - 档位：`quiet / low / standard / high`，默认 `standard`；每个机器人可覆盖或 `muted`。
  - 送达含义：`interrupt` = 进对话 + 未读 + 系统通知；`message` = 进对话 + 未读；`digest` = 暂存，进今日小结；`silent` = 只进对话，不计未读。需要你永远 `interrupt`。
  - 安静时段（默认关）内的 `interrupt` 降为 `message`，需要你除外。
  - 今日小结：每天 `digestTime`（默认 09:00，本地时间）由 runner 的定时邮箱触发一次唤醒回合，汇总暂存项；没有暂存项就不发；消息带「今天 09:00 · 今日小结」分隔标签。
  - `set_proactivity { level, anchorMessageId }`：只能在用户明确要求时调用（必须锚定 `user_input`），只改本项目。
  - 设置页新增「机器人」分区（通用分组下）：全局主动性、安静时段、小结时间；档案设置里是本机器人的覆盖。
- **必须新增的测试**：规则表每一行；静音与安静时段；小结的触发、合并与空跳过；`set_proactivity` 无锚点被拒。
- **退出条件**：测试通过。

---

## B3-06 记忆进上下文与记忆页（MM2）

- **级别**：A（ADR 81）。**规模**：M。**依赖**：B2-10、B2-11、B2-16。
- **目标**：项目简报与用户偏好稳定地进入代理上下文；开任务时的记忆快照进入任务上下文；用户能看、固定、撤销、恢复、导出记忆。
- **必读**：记忆架构文档 §4.2–§6。
- **允许改动**：`project-memory-source.mjs`、`work-session-origin-source.mjs` 与测试；`memory-store.mjs`（排序与预算）；新 IPC `project-memory:*`（进 catalog）；渲染层 `MemoryTab.tsx` 与状态、回复里的记忆芯片；i18n。
- **实现要点**：
  - 简报组成与排序：固定项 > 职责 > 最近使用的 `verified` 事实 > `stated` 偏好；预算 6000 字符（超出按排序截断，截断处注明「另有 N 条」）。
  - 任务上下文只放快照里的条目，不随后续记忆变化。
  - 记忆页：按种类 / 信任 / 状态筛选；固定 / 取消固定；撤销（可恢复）；编辑 = 撤销旧条目 + 写一条新的 `stated`；导出（JSON 与 Markdown，经 main 保存对话框）；本项目记忆开关；全局「使用记忆」与「从我的习惯里学偏好」开关（后者在 B3-07 生效）。
  - 芯片「参考了 N 条」「新记住 N 条」点开列出对应条目。
- **必须新增的测试**：排序与预算截断；快照不随后续变化；IPC 每个动作；关闭记忆后既不写也不用。
- **退出条件**：测试通过。

---

## B3-07 Memory Curator 与准入（MM3）

- **级别**：A（ADR 81）。**规模**：M。**依赖**：B3-06。
- **目标**：代理从对话与任务结果中自动提取记忆候选，经准入策略决定是否生效，并告诉用户新记住了什么。
- **必读**：记忆架构文档 §5；ADR 81 准入规则。
- **允许改动**：新建 `packages/runtime-node/src/memory/{curator.mjs, admission-policy.mjs, episodes.mjs}` 与测试；`runner.mjs`（触发点）；`reply-composer.mjs`（`memoryLearned`）。
- **实现要点**：
  - 触发：每个任务结束后；每累计 8 条用户输入后；同一项目最多 10 分钟一次；没有新材料就跳过。
  - 执行：`memory_curator` 角色（默认省档），临时回合 + CollectingSink，只读输入为这一段对话与任务报告（episode），输出结构化候选。
  - 准入：推断出的偏好要在 3 个不同 episode 中出现才生效；来自任务证据的事实需要证据引用才能是 `verified`；来自工具输出、网页、文件内容的「以后都这样做」一律不记；想放宽权限或跳过确认的内容不生效；命中敏感信息规则拒绝。
  - 生效的条目在下一条代理回复的 `memoryLearned` 里出现（「新记住 N 条」）。
  - 用户关闭「从我的习惯里学偏好」时只停推断偏好，事实提取照常。
- **必须新增的测试**：记忆文档 §15 中提取与防注入用例；3 次门槛；频率限制；关闭开关。
- **退出条件**：测试通过；真实运行一次「连续三次同类偏好后生效」的记录。

---

## B3-08 失败唤醒与停滞检测

- **级别**：B。**规模**：S。**依赖**：B2-07。
- **目标**：任务失败或卡住时代理会知道，并决定重试、换法、停掉或问用户。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/watchdog.mjs` 与测试；`event-mapper.mjs`（`stalled`）；`project-agent-source.mjs`（失败处理规则）。
- **实现要点**：
  - 停滞：任务 `running` 且 10 分钟没有进展事件、且没有待批准与提问 → `stalled`。
  - 失败：`failed` 事件带失败摘要（GoalPlan 中断原因、最后错误）。
  - 同一任务因同类原因失败 3 次后，代理规则要求停止自动重试并问用户。
- **必须新增的测试**：停滞判定（排除等待用户的情况）；失败摘要；三次上限。
- **退出条件**：测试通过。

---

## B3-09 旧数据迁为机器人与历史对话

- **级别**：A（ADR 85 决策 10）。**规模**：M。**依赖**：B2-12、B2-16。
- **目标**：老用户的每个工作区变成机器人；旧会话按工作区进入历史对话；没有工作区的旧会话进入「我 → 历史对话」；历史对话可以交给机器人继续。**不改写任何旧会话文件。**
- **代码锚点**：`conversation-store` `listConversationsByWorkspace`（674）与 B1-12 的 `roles` 过滤；`createChildConversation` 的快照；`ConversationResultView`（只读查看的现有组件）；`task-overview` 的 `projectGoalPlan`；Automation 列表 IPC。
- **允许改动**：`bot-lifecycle.mjs`（批量 `ensureBot`）；新建 `packages/runtime-node/src/project-agent/history-projection.mjs` 与测试；`project-agent-application-service.mjs` 与 IPC（`list-history`、`continue-history`）；渲染层 `TasksTab.tsx`（历史分组）、新建 `project-agent/HistorySheet.tsx`、`MeMenu.tsx`（历史对话入口）、`ObjectivesTab.tsx`（旧自动化只读列表）；i18n。
- **实现要点**：
  - 机器人：`settings.workspaces` 每一项 `ensureBot`；名字取工作区现有显示名；不自动熟悉项目——首次打开时显示「要我先熟悉一下这个项目吗？」卡片。
  - 历史对话：`role` 缺省、`workspacePath` 等于该机器人路径的会话（含归档？不含，归档仍在 设置 → 归档）；按更新时间倒序；只读查看复用 `ConversationResultView`。
  - 经典界面里仍在推进的 Goal（非任务）：照常运行；在任务页「经典任务」分组显示状态；它们的等待用户计入机器人的需要你数，点击打开原会话现场。
  - 「交给机器人继续」：选择机器人 → 提交一条输入（`historyRef: conversationId`）→ 代理开任务时用该历史对话做继承背景快照（B1-12 原语）。
  - 「我 → 历史对话」：`workspacePath` 为空的会话；同样可以交给某个机器人继续。
  - 旧自动化：目标页底部「自动化（旧）」只读列出该工作区的自动化，点击跳自动化中心。
  - 迁移前后对全部旧会话文件做校验和对比（测试里）。
- **必须新增的测试**：批量建机器人幂等；历史投影（含 / 不含归档、未归属）；交给机器人继续的快照内容；旧文件校验和不变；经典 Goal 的需要你计数。
- **退出条件**：测试通过；用负责人真实数据的副本（`dev:lab` 目录）跑一遍迁移，截图附在交接报告。

---

## B3-10 默认壳切换、经典界面开关、机器人模式首启

- **级别**：A（ADR 84、85 决策 10）。**规模**：M。**依赖**：B3-09。
- **目标**：所有 beta 用户默认进入机器人列表；可以随时切回经典界面；新用户首启走「接入模型 → 新建机器人」，不再自动创建 `~/PeerAgent`。
- **代码锚点**：`settings-migrations.mjs`（v3）；`App.tsx` 的壳分支（B2-14）；`workspace-application-service.mjs` `ensureDefaultWorkspace`（90–112）与调用方；首启与空状态（`BrandStartupLoader`、空会话「连接 AI 服务」CTA）；`GeneralPanel.tsx`。
- **允许改动**：`settings-migrations.mjs`；`App.tsx`（壳分支改读 `projectAgent.shell`）；`workspace-application-service.mjs`（`shell === 'bots'` 时不自动建默认工作区）；`GeneralPanel.tsx`（新增「界面」一项，只加这一项）；新建 `project-agent/onboarding/*` 与测试；i18n。
- **实现要点**：
  - 迁移 v3：`projectAgent.shell = 'bots'`；`developer.projectAgentMode` 此后不再读取（保留原值不删）；开发者分区的开关移除，换成说明文字。
  - 切换即时生效，不需要重启；切换不改任何数据。
  - 经典界面下：项目代理运行时照常推进已有任务；需要你仍然通知；点击通知弹出「切换到机器人界面查看」。
  - 机器人模式首启：没有模型 → 接入模型（跳设置 → providers）；有模型没有机器人 → 新建机器人（两条路）。
  - 升级用户：列表顶部一次性横幅「这是新的机器人列表；原来的会话在各机器人的档案 → 任务 → 历史对话；可以在 设置 → 通用 切回经典界面」，关闭后不再出现。
- **必须新增的测试**：迁移 v3 幂等；两种界面切换不写数据；首启不创建 `~/PeerAgent`；经典界面零变化（与 beta.2 关闭开关时对比）。
- **退出条件**：测试通过；全新安装与升级安装各截图一次。

---

## B3-11 全局入口适配

- **级别**：B。**规模**：M。**依赖**：B3-10。
- **目标**：快捷对话、Appshot、全局搜索、托盘、快捷键在机器人模式下都指向机器人。
- **代码锚点**：`quick-chat-window.mjs`（`createQuickChatWindowController`，173）与渲染层 `?window=quick-chat`；`appshot-delivery.mjs`、`appshot-service.mjs`；`ConversationSearchPalette.tsx`；`tray-controller.mjs`；快捷键注册（`rg "globalShortcut|accelerator" apps/desktop/electron/main -l`）。
- **允许改动**：上述文件（只加机器人模式分支）与测试；新建 `packages/runtime-node/src/project-agent/conversation-search-index.mjs` 与测试（B1-08 的索引，覆盖代理对话可见消息、任务标题、记忆）；`project-agent:search` 扩展；i18n。
- **实现要点**：
  - 快捷对话：顶部选择机器人（默认最近活动的机器人）；发送 = `submit-input`，`surface: 'quick_chat'`。
  - Appshot：投递目标为机器人；快照作为附件引用随输入进入，代理开任务时带入任务。
  - 搜索（⌘K）：机器人、消息、任务、记忆四类结果；点消息跳到该条并高亮；索引增量更新，可从源数据重建。
  - 托盘：菜单列出有需要你的机器人；角标 = 需要你总数。
  - 快捷键：⌘1…⌘9 切到前 9 个机器人，⌘N 新建，⌘⇧P 开关档案，⌘F 列表搜索；经典界面快捷键不变。先列出现有快捷键表（设置 → 快捷键的数据源），与现有冲突时保留现有绑定、换一个组合，并在交接报告列出最终表。
- **必须新增的测试**：各入口在机器人模式与经典模式下的分支；搜索索引增量与重建一致；性能（1 万条消息搜索 < 150 ms）。
- **退出条件**：测试通过。

---

## B3-R 发布 `0.1.0-beta.3`

- **步骤**：版本计划 §10 检查单。发布说明重点：默认界面变为机器人列表、如何切回、旧会话在哪里、降级说明。
- **证据**：版本计划 §12.1 beta.3 一行；负责人连续日用 5 天的问题清单与处理结果。
- **退出条件**：prerelease 生成；版本计划 §5.2 更新。
