# ADR 111：主 Bot 双向监督、可靠续接与上下文连续性

> 2026-11-01 后续提案：[ADR 117](117-intent-driven-coordination-and-goal-closure.md) 在本文双向监督与工作责任上，拟统一输入处置、原目标覆盖、下一步承接及 DecisionFrame。工作问题仍使用原 requestId/revision/replyTo 和执行回执，父答不消耗人类请求；不增加重复监督者、不重放原生已完成工具。新增记录版本须高于实施时已合入的门槛，不覆盖本文最低读写/执行版本。提案 Proposed、未实施，本文 Accepted 契约及历史回执继续有效。

创建时间：2026-10-28
最后更新：2026-11-01（关联 ADR 117 后续提案）

状态：Accepted；2026-10-28 已接入本批源码实现，尚未发布验收。代码范围与限制见[实施记录](../../playbook/v0.1.0/code-structure-refactoring.md)。这不是已安装版本的能力声明。

级别：A（通信、控制、上下文与存储契约），B（协调、恢复、任务事件与宿主调度）。

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[治理基线](../architecture/20-architecture-governance.md)、[设计理念与模块架构](../architecture/25-duplex-supervision-and-continuity.md)、[实施文档](../../playbook/v0.1.0/duplex-supervision-implementation.md)。

## 1. 决策与适用范围

用户把目标交给主 Bot 后，主 Bot 持续承担目标范围内的协调责任。子 Agent 的中断、普通执行失败和工作疑问进入主 Bot 的跟进流程，不能仅以一次异常返回结束整件工作。是否恢复、补充信息、调整方法或安排接手由模型判断；可靠投递、版本校验、执行准入、停止与恢复事实由本地宿主保证。

本设计将“双工”定义为：执行期间，事件可向主 Bot 上行，信息与控制可向工作会话下行，双方无需等待整件任务结束才能通信。它不是对某个名为“Codex 双工模态”的官方功能的断言，也不要求模型请求天然支持任意时刻插话。适配器不支持活跃回合注入时，在下一安全边界接纳；需要停止的控制走结构化停止路径。

主 Bot 保持读取与协调角色。接管表示承担跟进、回答工作问题、发出受约束的控制或安排新的执行 attempt，不表示主 Bot 获得项目写入、Shell 或绕过 PermissionGrant 的能力。保留既有主 Bot → 工作会话 → 临时 Explorer/Verifier 层级，不开放递归派工或任意跨 Bot 寻址。

## 2. 研究依据与当前缺口

源码观察来自 Peer-Agent 工作区，HEAD 为 `b6e8fe88c90fc56677a404c641c0978da6a64f92`，分支为 `PeerAgent/tui-desktop-goal-contract-shared`，存在未提交改动。观察不等于该提交或已安装 RC28 已包含全部行为。实施前必须重新确认基线与依赖。

| 已有机制或缺口 | 代码锚点（相对代码仓） | 本决策处理方式 |
| --- | --- | --- |
| 独立会话、父子消息、问题回答后恢复已存在 | `packages/runtime-node/src/project-agent/agent-communication.mjs`、`goal-runner-host.mjs` | 扩展原通信契约，不重做 Agent 平台 |
| 工作消息在回合上下文装配时读取；排队回执不足以说明已续跑 | `agent-communication.mjs`、`packages/runtime-node/src/project-agent/prompts/delegation/send_agent_message.md` | 分开持久化、观察、准入与生效事实 |
| 修复入口主要收集 `waiting_agent`；failed/interrupted 与责任投影未完全同源 | `packages/runtime-node/src/project-agent/repair-ownership.mjs`、`packages/protocol/src/task-overview.ts` | 调度与界面消费唯一 followUp 判定 |
| `request_user_input` 进入用户等待，普通工作问题缺少结构化父代理路由 | `packages/runtime-node/src/goal-runner.mjs`、`agent-communication.mjs` | 新增父代理决策请求；保留真实人工请求 |
| 接手、目标版本、协调授权、执行 epoch 与资源分道已存在 | `session-takeover.mjs`、`coordination-lifecycle.mjs`、`execution-scheduler.mjs` | 补充连续性与回执，不建立第二套控制器 |
| 持久协调日志与增量读取已有设计/在途实现 | [ADR 104](104-progressive-interaction-and-coordination-storage.md) | 复用其存储 seam，不按每次查询重写完整 ledger |

以上是结构性缺口分析，不是对某次现场失败或整个应用卡顿的唯一根因归因。本 ADR 约束新增协调开销，不代替性能问题的测量与修复。

表中省略目录的 `.mjs` 文件均位于 `packages/runtime-node/src/project-agent/`。

## 3. 与既有决策的关系

- [ADR 89](89-independent-agent-delegation-and-communication.md)、[ADR 91](91-project-bot-autonomous-coordination.md)：保留独立执行、协调授权与取消接手；细化消息是否唤醒、何时被观察、何时实际生效。
- [ADR 93](93-verification-continuity-and-repair-ownership.md)、[ADR 94](94-reply-attempts-silent-wait-and-recovery.md)、[ADR 99](99-authoritative-reply-receipts-and-model-recovery.md)：回复完成不解除未完成工作的责任；恢复必须有宿主事实。
- [ADR 97](97-reasoning-replay-and-continuation-custody.md)：保留 Provider 原生续接与 reasoning replay 边界；工作笔记、提示摘要不能冒充原生 checkpoint。
- [ADR 100](100-actionable-attention-and-question-lifecycle.md)：真实 `request_user_input` 仍由用户显式回答；新增的父代理工作问题不计入用户待办。不得把历史用户问题静默重分类。
- [ADR 102](102-unified-task-lifecycle-projection.md)、[ADR 110](110-follow-up-responsibility-and-current-list.md)：保留唯一生命周期/followUp 出口；补充可信中断来源。只有明确用户暂停才走“等待用户恢复”，技术中断不能只凭 paused 字符串退出当前责任。
- [ADR 103](103-verification-settlement-and-progress.md)：恢复和换窗不重置停滞治理与核验义务。
- [ADR 104](104-progressive-interaction-and-coordination-storage.md)：新增记录进入既有增量日志与索引；缓存不成为责任真值。

ADR 100–104 的实现基线按当前开发线核对；ADR 110 作为本批监督所需的共享责任投影前置决策一并提交。引用不表示对应能力已通过发布验收。本文只调整明确列出的细节，不覆盖其他授权、验收与停止规则。

## 4. 三个维度分别建模，同一事实共同投影

| 维度 | 权威来源 | 回答的问题 |
| --- | --- | --- |
| 执行生命周期 | GoalPlan、Conversation、实际执行/停止/接手记录 | 当前有没有执行、为何停下、是否完成？ |
| 跟进责任 | 上述事实经 ADR 102/105 的唯一投影 | 现在由 Bot、用户还是无人继续处理？ |
| 操作处置 | 带稳定 ID 的消息、控制与恢复回执 | 某次投递或恢复请求到哪一步？ |

不增加可独立改写的“监督任务状态”。ProjectWorkReceipt 继续记录协调工作的事实与进展，不能从主 Bot 的一句回答推断整个 work 已交付。存在开放问题、未决副作用、未完成恢复或核验责任时，不得仅因本轮回复结束写出责任已收口。

新增 `InterruptionFact` 由宿主产生，绑定 task/session、goalRevision、attempt、executionEpoch、来源引用和发生时间。至少区分用户显式暂停/取消、Provider 故障、宿主交接、lease 丢失、工具失败、预算耗尽和未知来源；另记停止是否确认、是否存在未决副作用。模型和附件不能伪造中断来源。

历史数据缺来源时保留 unknown 与 Bot 排查责任，不据此自动续跑，也不倒推成用户主动暂停。真实人工请求、活动执行与未决停止的优先级仍按 ADR 110 保护性事实处理。

## 5. 双向通信：持久投递与执行控制分离

扩展现有 `AgentMessage`，以稳定 messageId、发送者、接收者、工作绑定、来源与可选 replyTo 为基础，新增明确的投递意图：

| 投递意图 | 空闲目标 | 运行目标 |
| --- | --- | --- |
| `mailbox_only` | 持久入箱，不启动回合 | 下一可用上下文边界读取 |
| `ensure_turn` | 持久入箱，并登记待准入的唤醒意图 | 下一安全边界读取；保留待处理义务，直到宿主确认已覆盖该消息 |

投递意图不是启动授权。宿主仍检查有效 mandate、目标版本、父子关系、停止状态、权限、预算与 lease。普通消息不得绕过用户暂停；旧消息不因默认值变化获得新唤醒能力。旧有父代理回答自动恢复路径迁入显式意图，保持原有准入限制。

每条消息在持久提交时分配接收方序号。回合装配记录其实际纳入的序号/ID；工具安全点是否支持进一步纳入由 Provider adapter 声明。回合进行中到达且未被纳入的消息，保留到下一回合。不得仅凭“当前正在运行”就消费唤醒意图。

新增 `AgentCommandReceipt` 是操作回执，不是另一个任务生命周期。它分别记录：

- delivery：持久入队；后续可记录 `observedInContext`，仅表示已纳入某次模型输入，不保证模型理解或服从。
- admission：恢复/控制请求 pending、admitted 或 rejected，以及宿主拒绝原因。
- effect：pending、applied、unknown 或 rejected；只有对应的执行开始、停止确认、版本接纳等事实才能支持 applied。

没有请求执行控制的纯信息消息，其 admission/effect 标记为不适用，不制造永久待恢复义务。开放问题是否已解决另依请求事实判定，不能因消息已被观察就自动关闭。

回执绑定 operationId、messageId/requestId、expectedGoalRevision、target attempt/epoch 和事实引用。消息入队失败不得返回成功；收到 accepted/queued 不得渲染“已经继续执行”。宿主可以证明答案进入上下文，不能凭此声称答案已正确落实。

新监督信封与唤醒 outbox 以同一既有协调日志提交单元持久记录。先持久化后通知；至少一次投递，按 operationId/目标版本去重。崩溃发生在入箱后、唤醒前，重启应恢复待准入义务；发生在启动后、回执前，先核对实际 attempt，禁止盲目再启动。

## 6. 工作问题先交主 Bot，真实人工决定保持人工归属

新增 `AgentDecisionRequest` 是现有父子消息的结构化载荷，不是通用审批对象。字段包含 requestId/revision、问题、可选稳定 optionId 列表、单选/多选/自由回答约束、相关材料引用、阻塞范围和目标版本。模型提出回答对象建议，最终 responder 与请求类别由宿主验证。

| 请求类别 | 默认责任 | 处理 |
| --- | --- | --- |
| 原目标范围内的方法选择、资料理解、工具替代或普通失败处置 | 主 Bot | 消费项目上下文，提交结构化答案或安排修复 |
| 主 Bot 也缺少的用户偏好、实质目标歧义、超出现有授权的范围/预算决定 | 用户 | 主 Bot 汇总为绑定原 requestId 的一个明确请求 |
| 权限批准、人工完成检查、政策强制验收 | 现有人工/政策入口 | 只引用其原生记录，不能用 Agent answer 代替批准 |

答案包含 answerId、requestId、expectedRequestRevision、选项 ID/正文与来源。宿主对 requestId 做一次有效解决的条件提交；迟到、重复、旧版本答案保留回执但不再次改变当前决策。不允许先关闭问题后丢失恢复义务。

父代理可以将问题升级为真实用户请求；升级沿用关联身份与原始问题，不生成两条并行待答事项。实际用户请求仍通过既有结构化回答动作解决，不能从无关主会话文本猜测已回答。问题已答而续跑失败时，责任转回 Bot 恢复，不再要求用户重复回答。

工作 Agent 的工具输出、问题正文、选项与笔记均属事实/工作上下文。它们不能要求主 Bot 忽略系统规则、冒用用户身份或授予权限。

## 7. 主动恢复必须保留停止意图、副作用与预算边界

| 可信事实 | 宿主/主 Bot 的处置 | 自动开始执行的条件 |
| --- | --- | --- |
| 明确用户暂停或取消 | 保留用户意图；主 Bot 可报告、核对停止 | 新的有效用户输入或原有明确政策允许恢复 |
| 临时 Provider/传输故障，副作用已知且可安全续接 | 先用既有有界技术恢复；耗尽后交主 Bot 调整 | 原 mandate、预算、版本与原生续接规则仍有效 |
| 工作方法失败或需要选择 | 子 Agent 有界自修复后，请主 Bot 决策 | 主 Bot 发出受约束的补充/恢复/接手操作 |
| 工具 dispatch 结果未知、旧执行可能仍活跃 | 先 reconcile，必要时等待结果或执行受控停止 | 不能凭重试次数、超时或文字判断可重放 |
| lease 丢失、宿主切换 | 原宿主失去写入权；新宿主恢复责任账 | 完成 lease/epoch fencing 并核对旧副作用 |
| 预算耗尽或权限被拒绝 | 按现有政策保留阻塞和明确归属 | 新增的合法预算/批准事实；换模型、换窗不能绕过 |
| 主 Bot 回合失败或重启 | 本地保留问题、事件和恢复 outbox | 按既有退避与上限重试；不启动另一个无限监督 Agent |

同一目标内的恢复保留 work/task/GoalPlan 身份。原 attempt 仍有效且可原生续接时可继续该 attempt；重新执行或更换执行者使用新的 attempt，并按控制契约推进 executionEpoch。一次新模型回合不自动等于新 attempt。目标改变时使用新的 goalRevision，真正替代任务按 ADR 91 关联承接关系。换执行者不是伪造旧执行成功。

接手按既有 TaskTransition 执行：记录意图 → 禁止旧版本新增不适用的操作 → 停止/等待安全边界 → 核对未决副作用 → 绑定新 attempt → 真实启动 → 回执。旧 epoch 的迟到输出保留历史，不得改变当前执行与问题归属。不能在等待子 Agent 或模型网络请求时长期持有项目提交锁。

技术恢复、主 Bot 修复、停滞治理共享原工作预算和计数。本文不增加无限重试，也不把当前实现中的重试次数当作永久标准。

## 8. 上下文连续性：换窗不换责任

| 对象 | 用途 | 不承担的责任 |
| --- | --- | --- |
| ContinuityHint | 当前目标版本、决策、未完成工作及可检索引用的短交接 | 不取代 Tool Result、Evidence 或权限事实 |
| WorkNotes | Agent 主动维护的工作笔记，带作者、版本和来源 | 不成为系统指令、用户授权或跨会话长期记忆 |
| History | 可检索的 canonical 消息、事件、工具结果与事实引用 | 不默认全量装入提示词；检索命中仍须受范围限制 |
| Provider checkpoint / continuation | Provider 适配器允许的原生续接 | 不能由文字摘要伪造；不保证跨 Provider 可移植 |
| Evidence | 本地能力执行与核验的事实依据 | 不因摘要声称“完成”而自动生成 |

工作 token/成本预算与 ContextWindowBudget 分离：前者约束整项工作的消耗，后者控制一次上下文准入。新窗口、压缩、模型切换不得重置工作预算、已答问题、未决控制、未知副作用与跟进责任。

连续性交接由宿主先固化窗口边界、历史游标与开放义务引用，再让模型生成可审阅的摘要；模型摘要失败时仍可从 canonical 事实恢复最小上下文。对缺失、过期或冲突的笔记先检索核实，不把最后一段自然语言当作唯一任务状态。

Hint/Notes/历史检索通过既有 System Context Source 的事实层准入，遵守 [System Context 架构](../architecture/19-system-prompt-context-architecture.md)。不因参考实现把 Hint 放在 DeveloperMessage，就在 Peer 新增高权限注入路径。Prompt 基线 `ContextEpoch`、物理执行 epoch 与上下文窗口 ID 分别建模，不复用一个计数器。

## 9. 存储、并发与恢复契约

继续以 Conversation、GoalPlan、ProjectWorkReceipt 和现有协调日志为权威记录，不新增独立监督数据库或任务树。新增信箱、请求、操作、窗口与笔记记录注册到既有 coordination-v2 存储 Module：

- 公开用户/助手消息仍由 Conversation 持有。新增监督信封、决策请求/解决及投递回执由协调日志持有；正文可用不可变 blob 引用，Conversation 中只保存带源引用的展示/检索投影，不二次签发消息身份。既有 AgentMessage 保持原 Conversation 来源，经兼容 adapter 读取，不要求改写历史。每个事实只有一个 canonical 所有者。
- 设备侧 projectRuntime 保存本地控制与恢复记录；不偷偷写入 portable 项目长期记忆，也不把 device lease 或权限事实跨设备复制。
- portable Conversation 若携带设备侧监督记录的引用，跨设备缺源时须明确显示来源不可用；展示副本不能重建执行授权、开放义务或自动续跑。监督状态的跨设备迁移不在本批范围内。
- 不可变笔记/大正文先写 blob，再提交引用事件；孤儿 blob 可按既有保留政策回收，已引用内容不能因索引重建而丢失。
- 回答、笔记修订与控制提交使用 expectedRevision/epoch 和当前 lease。派生索引可重建；promptSnapshots/cache 不得成为开放问题与恢复义务的唯一存储。
- 控制和事实事件先持久化；高频展示 delta 可合并/丢弃过时版本，关键问题、授权、停止、失败与结果不能丢。
- 分页读取以稳定游标、大小上限与读版本保证一致性。一次只加载决策所需事实，禁止每次观察回读全量消息和 ledger。

新 schema 必须有版本与读写兼容策略。旧记录缺新字段时采用保守读取，不改写历史为新的停止/回答事实。禁止旧 writer 在无法保留新字段时继续写同一活跃工作；降级必须先关闭新自动唤醒并安置未决责任，不能靠删记录恢复兼容。

WorkNotes 的写入是受限的运行时工作状态能力，目标仅为本工作笔记，不授予项目文件写权限。主 Bot 是否可调用须在 Provider Manifest、Projection 与本地政策中显式定义，不能仅凭“内部笔记”名称绕过只读角色或权限检查。

## 10. 运行与表达约束

宿主负责事件接收、耐久性与触发条件，模型只在新用户输入、开放决策、可处置失败、关键完成或治理阈值等有意义事件上运行。进度 token 不逐个唤醒主 Bot；使用既有协调/工作执行分道，容量为 1 时保留交替推进与安全让出，不另建无限轮询。

用户默认在主对话获得汇总：谁在执行、谁负责下一步、是否真需用户决定。细节按需展开。当前列表与计数消费同一 followUp；用户 Attention 只计真实可操作的人工事项。后台恢复不抢焦点、不改变草稿或阅读位置。新增状态表达实施时必须登记既有体验矩阵，不在本 ADR 引入第二套视觉体系。

## 11. 代价、非目标与落地顺序

接受的代价是更多带版本的协议与耐久记录，以及消息和执行回执的分离；换来的 Leverage 是所有宿主共享可靠通信、连续责任与可核对恢复。把这些能力集中在现有存储、投影与控制 seam，避免各界面和各 Provider 重复实现。

原设计交付不包含运行时改动；2026-10-28 后续实施已按用户授权接入，见实施记录。继续不新增后台常驻模型、不接入长期记忆整理、不移植 Codex 内部代码，也不把源码改动当作现场卡顿已经解决。实施顺序为：单一责任投影 → 可靠信箱与唤醒 → 父代理问题 → 受控恢复/接手 → 工作上下文 → 多宿主与表达，具体入口、退出条件和发布用例见实施文档。

## 12. 参考材料与可信度

1. [OpenAI Codex App Server](https://developers.openai.com/codex/app-server/)：双向请求/通知、turn steer/interrupt 与交互请求。说明协议能力，不证明 Peer 已有相同实现。
2. [Responses multi-agent guide](https://developers.openai.com/api/docs/guides/responses-multi-agent)：消息、follow-up、等待与中断的区别；其托管执行环境不是 Peer 本地能力链。
3. [Steering guide](https://developers.openai.com/api/docs/guides/steering)：输入接纳与安全边界，不能撤销已经发出的工具副作用。
4. 飞樰，《深度解析 Codex Harness 架构及其全新上下文压缩记忆体系的设计思路》，千问 AI 平台，2026-10-27；用户提供的 13 页 PDF，[原文入口](https://mp.weixin.qq.com/s/IM-zakQ9Bnog54NdYiJSqA)。通信/循环见第 3–8 页，上下文与记忆见第 9–12 页。文章自述为个人理解，本文只借鉴其分层思路，不把 fork 数量、阈值、Hint 大小或内部实现当作官方保证。

初始设计交付只做内容与 diff 审阅。此后用户明确授权完成实现、自测并提 PR；实际构建、测试及隔离产品回归以[实施回执](../../playbook/v0.1.0/code-structure-refactoring.md)为准，不能从设计本文推断已经运行或通过。


## 2026-10-28 实施契约冻结

- 协议归 `protocol/agent-supervision.ts`，包括问题/答案、投递/准入/效果回执、准备中的 ContextWindowRecord、WorkNoteRevision 和任务详情的 AgentSupervisionReport。模型只提供普通问题/选项/答案与预期版本，身份、responder、用户回答引用、epoch 和执行效果由宿主产生。
- 复用 coordination-v2 的 journal、blob 和派生 SQLite。物理事件封装仍为 storageVersion 2；首次写新监督事实前，manifest 保持 schema 2，minimumReader/minimumWriter 升到 5，head 保留该门槛以支持 manifest 丢失恢复。旧二版写入者拒绝新 manifest；不改写旧记录。笔记完整事件先落内容寻址不可变 blob，再提交其引用。
- 原 Conversation 信封仍可读取；新记录的 Conversation 镜像仅用于兼容展示。新契约扩展要求有效协调绑定，不能悄悄退回旧适配器。新投递从 canonical 信箱读取；未进入实际 Source 的消息不写 observed，不随整批事件被确认；有界纳入优先排队消息，并沿现有工作续接补齐。
- 原生用户提问使用 `post_reply.question.agentRequestId/expectedRequestRevision` 关联。准备原生回复与升级原请求在同一 journal 事务内。转交用户答案必须关联当前真实 user_input 的 answerTo；旧原生卡已关闭时可经宿主校验重新关联同一请求，不能以此代答或产生 PermissionGrant。
- resume 沿原 TaskTransition/SessionTakeover/GoalRunner 运行，保留任务、材料、预算与核验义务。命令发出但结果未确认时记录 unknown，恢复不盲目重放；实际绑定回合结束产生 executionAttemptRef 和效果回执。用户停止、未知副作用与真实人工门槛仍受保护。
- working-context Provider 的四个工具仅操作本工作运行时笔记、受限历史和交接准备记录，主 Bot 没有因此获得项目写入或 Shell。Notes/Hint 经 L7 factual Source 准入。prepare_context_handoff 明确返回 prepared/providerWindowChanged=false；实际压缩/换窗仍归现有 Provider encoder/checkpoint，不伪造原生续接，也不重置预算。跨设备缺源明确失败；本批不实现监督状态跨设备复制。


### 候选迁移与明确自测授权（2026-10-28）

用户要求继续完成、自测通过并提 PR，本任务的构建、测试、类型/架构/IPC 与隔离产品/性能回归获得明确授权。交付迁移到开发线 e0c87d2d 的独立 checkout，原 dirty 工作区保持原样。

当前开发线已经采用 schema/storageVersion 2、最小读写版本 3/4 和物理旧 writer fence。本批保留这些保护，监督要求最小 reader/writer 5，取代早期基线下的 schema 3 草案。durable head、回放及维护恢复必须保持最高所需版本，不允许恢复时降低监督记录门槛。

原工作区有尚未完整进入开发线的 ADR 110 followUp 投影。本批只采用监督所需的共享投影与消费者及相关测试，并将该前置决策一并提交；其他在途布局/文案改动不纳入。授权不包括合并 PR、发布、安装或重启用户当前应用。

可靠投递的有界读取须先按 recipient 的 pending 索引、sequence 升序取得最早未观察的 ensure_turn 消息，再补最近历史。仅对最近 50 条结果排序不能保证公平性；120 条消息的回归必须证明旧消息逐批进入实际 Source，观察回执更新索引，删除派生索引后重放不恢复已观察义务。索引只投影原 journal 的 delivery 事实，不产生新的执行权限或成功回执。

## 12. 2026-10-29：监督闭环补齐

状态：Accepted（用户要求补齐本轮列出的监督缺口）；实现与验证状态另记，不能据此声明运行实例已具备能力。

### 12.1 返回结果的原任务返修

`coordinate_work(resume)` 在原目标有效 mandate 内允许继续尚未签收的 `completed` 计划；必须先检查真实人工门、用户停止、旧 epoch、活体与未决 dispatch。沿既有 takeover 的停止、等待、重新绑定与调度路径，保留 session/plan、成果、Evidence、预算和成功标准。已签收、已取消及人工门不得自动重开。返修反馈作为有身份的工作消息进入原事实上下文，不是系统指令。原核验与人工决定保留历史；旧执行的核验不得直接证明新执行通过。

### 12.2 跟进责任与协调记录对账

同一宿主在选择续接工作前，根据现有 `followUp` 对账自己的 `delivered` / 技术等待记录。只有存在原 checkpoint、关联 session 明确、没有人工等待、用户停止、历史隔离、未决 dispatch、活动 attempt 或另一个已有责任承接方时，才能重新唤醒原工作。不得创建重复监督者；不重放已完成 Provider 工具尾巴；无进展计数和预算保持。

### 12.3 未知结果与阻塞恢复

`awaiting_outcome` 的保护本身不是缺陷。核对只认宿主现有 Tool Result/Evidence、真实绑定 attempt 的完成记录和原操作身份；普通消息、模型判断或 `ownership=unknown` 不能消除未知副作用。恢复检查必须返回仍缺的事实和合法下一动作，不返回假成功。已确认的本机通信执行可修复迟到回执；没有权威结果的外部副作用继续阻塞并明确交还核对义务。协调日志中的 blocked/unknown 转移只有在实际前置事实改变后才可继续，不按固定次数或计时器盲重试。

### 12.4 历史承接、选项与停滞

旧任务先经当前用户输入与既有 coordinate_work 原生 adoption 建立 mandate，再绑定执行代次，后续使用相同结构化问题/回答和持久通信链。没有 mandate 的普通唤醒只能查事实和给承接提示，不从历史文本创建新权限。Agent 问题必须有稳定 requestId/revision/replyTo；答案入队后仍保存执行准入义务。主 Bot 无进展后保留原责任、错误和证据，报告具体缺口及可行恢复动作，不能要求用户重复已回答的问题或无界启动新监督 Agent。

### 12.5 验证与体验约束

用户目标是“一次委托由主 Bot 持续处理并交还”；状态来源仍是本地日志、GoalPlan、执行事实与统一生命周期投影。Desktop/TUI 共用宿主路径；不改输入、焦点、滚动或增加动效。补齐原任务返修、人工/停止拒绝、历史对账去重、问题已答后重启、执行未知保留、旧版本拒绝、无进展不循环等回归用例。按最新 Validation Scope，日常只做内容/diff 审阅，不运行测试/构建/产品回归；真实模型多轮监督、崩溃窗口和安装包验收须在发布前完成，不能用脚本用例代替。

### 12.6 格式与回退边界

返修语义以 TaskTransition `minimumExecutorVersion=3` 标记；既有 schema/storage 版本仍为 1/2，但首次写入返修、批量执行回执或未知状态对账引用前，将 minimumReaderVersion/minimumWriterVersion 提升到 6。格式提升幂等，普通监督写入不得把 6 降回 5；日志重建、缓存/manifest 丢失及历史恢复均保留最低版本。旧宿主必须拒绝继续写这批数据。`takeover.repair` 与新 epoch 同时参与语义核验及 host verification 内容身份；历史核验与 Evidence 不删除，但不能直接用于新返修验收。工作预算、范围和真实人工门不重置。

未知状态只有既有宿主 `reconciledDispatches` 中同一 plan、实际 attempt/toolCallId 且晚于阻塞的记录可以解除；转移记录 `reconciliationRef`，随后重新执行停止/idle/未知检查。其他工具的未知副作用没有权威结果时，明确保持 reconciliation_required/replayAllowed=false，并提供原结果核对动作，不承诺自动恢复。真实回合结束的通信命令按一次日志提交批量记 applied；提交前崩溃且没有其他执行凭据时仍保留 unknown，不捏造回执。

## 13. 2026-10-29：问题承接与单一 Agent 状态行

用户反馈：子任务把选项与“需要批准”写进结果正文，主 Bot 未及时交还；同一子任务又以开始、结果返回等多个活动行刷屏，开始图标持续跳动。

- 普通工作方法与选项先经既有 send_agent_message(question/decisionRequest) 交父 Bot，在同一个 requestId/revision 下回答；等待父答时不得只写一段报告文字再标完成。真正权限与人工门继续原路径。
- 已完成报告中的“需要批准”只是未验证工作内容，不制造人工门。主 Bot 必须对照原用户目标与宿主真实门槛，自行处理原授权内的选择；确需人决定时在主对话发出关联原输入的结构化问题。只读调研子目标不是用户整体实现目标，不能把自己的调研步骤变成额外批准。核验无变化时不得反复重跑相同检查来替代问题承接或结论交还。
- Desktop 主对话按 sessionId 合并活动通知，一名子 Agent 一行；在首次出现位置更新最新阶段，原始消息、事件和详情完整保留。显示和活动扫光以宿主当前 session 状态为准，历史 started 文字不能在当前核验/停止时继续冒充执行。
- 子 Agent 图标保持位置与形状，只在真实活动时使用共享 mask-shimmer 高光扫过；停止、等待、缺事实和 reduced-motion 时静态显示。无新权限、执行或 Evidence 来源；无焦点、输入、滚动或事件日志改写。

这是 A/B 级既有 Context Source 行为规则与 C 级表达收口；提示规则不能替代已有通信准入、人工门和核验。源码及用例按当前 Validation Scope 审阅，未运行与真实模型行为分别记载。

补充运行时不变量：某次父回合的 AgentCommandReceipt.effect=applied 只证明该执行回合处理过消息，不能把开放问题视为已回答。上下文读取额外按 parentConversationId 查询仍为 open/responder=parent 的原生问题，以 requestId 从 canonical 邮箱恢复，优先纳入有界上下文；即使旧消息已 observed/applied 或退出最近消息窗口，也持续保留到关联回答/取消/真实用户升级。该读取不创建请求、不改变权限、不把普通报告解析成问题。新增“已处理回合 + 60条后续消息 + 关联回答”回归用例，未运行。


### 13.1 隔离实测暴露的兼容缺口（2026-10-29）

“熟悉项目”等 lifecycle 任务可以没有 workId/mandate。监督报告须保留原 session/report 并返回 legacy_unbound，不用缺失 workId 查询协调 SQLite；缺少绑定不能制造 mandate 或执行权限。

Verifier/Explorer 的既有 ephemeral 回合不持久化独立 Conversation，conversationId 可以为空。Bot 权限继承继续使用本地 GoalPlan、workspaceId、planId、显式 sessionId 与完整未停止祖先链校验；通过现有 resolvePermissionPrincipal 后，只能从同一 GoalPlan 的真实 conversationId 开始核对持久祖先。仅 role=work_session 且 plan/session 精确绑定时允许此兼容映射。错误 session、不同工作区、伪造会话、停止、撤销及身份不完整仍拒绝，不回退全局 Full，不改变只读 Projection/PermissionGrant。

本次修复保留真实失败与 unknown dispatch 现场，不把新读取结果当作旧工具已经成功的凭据。旧未知操作继续沿原生核对/用户控制恢复。测试版启动成功不是监督验收；真实操作已发现上述失败，状态必须记为失败待修复。

只读监督查询在 Provider 边界发生已返回的本地异常时，必须产出结构化失败 Tool Result/Evidence，使当前调用正常结算；不能把查询异常升级为未知写入副作用。该处理仅覆盖已经声明为只读的查询，不吞掉写操作、控制操作或无返回的 dispatch；历史 unknown 不因此直接清账。


## 14. 2026-10-29：回复交付与原任务收尾闭环

用户实测：新用户“？”获得了主 Bot 重新读取目录后的普通文本答复，但原 lifecycle 子任务仍核验阻塞，当前任务卡保留。这不是新增子任务；后续回合的空任务名册、无源 fallback 与旧只读查询的 unknown 共同切断了原责任。

- 用户回合的有界 roster 除直接相关项，还纳入同一 Bot/parentConversation 的未决跟进摘要；唤醒仍只读本事件范围，不把整个历史重新唤醒。L7 继续提供事实（followUp owner/reason、blockedReason、原 anchor），不从短句“？”猜意图或创建 mandate，模型自行判断关联，独立目标保持独立。
- 有未决任务的用户回合必须走已有 post_reply 交付。模型普通最终文本只获得一次同预算内的结构化交付修正机会，规则经现有 L6 reminder，历史工具事实经既有 retryContinuity 进入；再次不交付则明确失败，不用 sources=[] fallback 冒充结果交付。不影响无任务的普通问答，也不自动替模型填 sources/statusClaims。
- 已投递且宿主校验过的 source 会成为本回复工作的跟进关系。回复不是完成：当前事实仍要求技术处理时继续原监督；只有真实复核、关闭闸门、已投递关联回复与既有 policy/user acceptance 全部满足，任务才退出当前列表。核验失败、人工门、用户停止和 unknown 外部副作用保持原保护。
- get_session/get_verification_detail 是固定的只读宿主观察。崩溃遗留 unknown 只有单一精确 dispatch、原回合 canonical 调用/原调度来源、同一 work/session、实际 attempt 已不活跃、宿主确认相同父子归属且无活动核验时可记 query_interrupted 对账；这只证明该观察已中断，不提供原 Tool Result、核验结论、授权或验收。写/控制调用及歧义一律不在此路径。记录沿已有 reconciledDispatches，schema/storage 与最小读写版本保持现行 6，扩展观察 outcome；旧宿主保留数据，不能把 query_interrupted 当作 verification_interrupted 来解除控制转移。
- 旧任务继续使用原 plan/session/Evidence 及核验入口，不能修改真实数据为假完成或靠隐藏卡片收尾。真实恢复效果另记实施回执。

现场同时发现旧核验已经有宿主 failed/completedAt 回执，但 continuation 仍是 requesting/formatAttempt=1。重新核验时，仅在非 tools 阶段、同一计划的终态核验回执晚于该 continuation 最后进展、且 runner 明确核验阻塞时，按已结束回合进入既有 completed recheck；保留累计请求/工具预算与旧失败记录，不重放旧 Provider 尾巴，不处理 tools/未知副作用阶段。该兼容由既有 continuation port 从真实事实推导，不按计时器重置额度。
