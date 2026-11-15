# ADR 104：交互优先读取与协调日志增量存储

创建时间：2026-10-22
最后更新：2026-10-28（历史分叉、安全恢复与旧 writer 屏障补充）
状态：Accepted（2026-10-22 用户明确要求按方案实施并跑完整回归；保留现有任务、对话与证据，不影响当前运行实例。实施及验收事实另记。）
级别：A（持久化格式、恢复契约、上下文准入），B（共享 Runtime、Conversation Store、IPC 与加载状态）。

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[治理基线](../architecture/20-architecture-governance.md)、[System Context](../architecture/19-system-prompt-context-architecture.md)、ADR 80、85、86、88、91、94、95、97、98、99、101、102、103。
实施卡：[交互优先与大日志恢复](../../playbook/v0.1.0/progressive-interaction-and-coordination-storage.md)。

## 1. 决策目标与现场依据

用户要求保留现有任务、对话和 Evidence，从根上解决日志写放大、大日志恢复及对话加载失败；主 Bot 日常只需要用户交互，子任务执行链作为按需调查和恢复路径。

本轮只读诊断确认：安装版 RC24 的某项目 coordination.jsonl 为 848,647,853 字节，8,593 条有效 JSON 记录；其中同一 work 的 7,155 条全量快照占 839,187,385 字节。该工作跨五个执行会话，累计模型请求 1,491 次、工具调用 2,282 次。其单条快照从 765 字节增长到 225,777 字节；反复序列化的 budget.observations 占 664,855,359 字节，progressFacts 占 147,825,737 字节。以上是存储统计，不把全部请求判作无效循环，也不把累计 Token 当作计费结论。

错误链已复现：CoordinationJournalReader 首次把整个文件转成字符串 → ERR_STRING_TOO_LONG → ProjectFacts.cards 失败 → BotDirectory.readConversation 失败 → renderer 隐藏消息列表。原父对话文件约 3.4 MiB，357 行 JSON 全部可解析。

当前代码并未默认向主 Bot 模型发送所有子任务正文。Desktop executeTurn 已在父历史中筛选 user_input、agent_reply 和兼容旧消息；但筛选前仍读取完整父历史。现有恢复视图也是读完整 checkpoint 后才投影。Roster 的截取发生在完整任务投影之后。这些“先全量读取，再过滤”的入口必须前移到查询边界。

## 2. 不变量与本次修订范围

1. 模型负责认知，本地负责能力与恢复，界面只表达；一条 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence 链不变。
2. Conversation、GoalPlan、Evidence、Tool Result、PermissionGrant 的原身份、内容、引用与签收语义保留。协调记录不是第二套任务真值，派生索引不是授权真值。
3. 主 Bot 默认历史是用户输入、主 Bot 已公开回复及真实交互决定；既有项目指令、记忆、能力规则仍按原 Context Source 准入。子任务轨迹、预算去重集合、全部协调历史和 Provider 原生检查点不自动进入模型。
4. 主 Bot 仍接收本轮相关结果/异常/问题的最小事实信封，包含真实任务身份、状态版本、来源和检索引用；否则无法履行既有委托责任。普通进度沿原静默策略处理，不每次唤醒模型。
5. 宿主恢复必要的权威状态，与模型读取什么是两个边界。少喂模型不能减少执行前的租约、目标版本、PermissionGrant、未知副作用和签收校验。
6. ADR95 的持续执行政策保留。不通过恢复固定总轮数、清空用量、删除任务或 Evidence 解决存储问题。
7. 本 ADR 拟替换 ADR98 中“协调持久化格式不变”的局部约束，引入版本化增量格式与可重建索引；ADR98 的查询范围、严格失效、真实性能及权限边界继续有效。ADR86 的旧批读 Interface 保持兼容，但不再是日常交互分页入口。
8. ADR97 的原生 reasoning/Tool Result 配对和单一续接责任不变。选中具体 attempt 后，恢复仍加载它所需的完整可靠检查点；公开交互摘要不能替代原生恢复状态。

## 3. 渐进读取的五种视图

以下是数据视图，不是新的 System Context 层。展示缓存、模型事实和执行准入不能相互代替。

| 视图 | 内容 | 何时读取 | 默认禁止的读取 |
| --- | --- | --- | --- |
| Interaction | 用户与主 Bot 的公开交流、真实问答/批准记录、引用、附件元数据 | 打开对话、普通用户回合 | 子会话正文、协调 journal、native checkpoint、Evidence 正文 |
| Work summary | 本轮相关或页面可见任务的状态、下一行动权、问题、结果摘要和版本引用 | 用户问进展、相关结果/异常事件、可见任务卡 | 无关项目、全部历史计划、完整任务报告和执行轨迹 |
| Session report | 单一任务当前报告、验证结论、标准、交付物和 Evidence refs | 审核结果或打开指定任务详情 | 递归拉取全部后代和全部尝试 |
| Trace | 指定 session/attempt 的分页过程、调用和结果引用 | 用户/模型明确调查某个问题 | 自动展开全项目历史 |
| Evidence / recovery checkpoint | 指定证据正文；或具体执行所需的受保护检查点 | 取证工具；或宿主实际恢复选中的 attempt | 页面首屏、普通聊天回合、全任务预加载 |

普通回合以当前输入及引用选取交互窗口；超出窗口的历史保留可检索引用。需要压缩时沿既有 anchored continuity / Context Epoch 机制，摘要只导航，不替代原始交互、Evidence 或 Tool Result。不得将旧输入截断后当作从未发生，也不得漏掉仍生效的用户边界和待答问题。

结果事件信封只提供当前相关任务的 title、sessionId、workId、anchorMessageId、sourceRevision/observationRevision、状态/行动权、简短结果或异常、reportRef/evidenceRefs。目标授权和真实用户输入的 source refs 保留；事实不会因被放入信封而取得用户指令效力。

## 4. Module 与 Interface

### 4.1 Conversation Store 的 Interaction Reader

在现有 packages/conversation-store 内增加存储级公开交互查询，保留旧完整历史 API 给取证和选定执行恢复。

概念 Interface：

```ts
readInteractionPage({ conversationId, before?, limit, byteBudget }): InteractionPage
readInteractionContext({ conversationId, inputIds, quoteRefs, tokenBudget }): InteractionContext
readProcessPage({ conversationId, turnId, before?, limit, byteBudget }): ProcessPage
```

三者返回来源版本、稳定游标、hasMore 和结构化 availability。游标按 canonical 追加顺序和消息身份生成，不用时间戳代替顺序；到引用锚点的跳转可直接定位，不从最新页逐页扫描到目标。

公开交互派生索引包含可见消息、公开正文片段、原记录字节定位、input/disposition/quote 关联和公开卡片锚点。不能只建 offset 索引却为读一条公开回复反序列化包含整个 rounds 的巨行。新增公开交互在 canonical commit 后增量投影；崩溃后的缺口按 commit version 重建。流式 sidecar 排除、provisional tail、contentRevision、终态替换及附件准入沿原契约。

首屏建议 50 条，同时受 256 KiB 响应预算约束；单条超预算用正文分片和附件/产物引用继续读取，原文不删除。兼容旧 kind 缺失的用户/助手消息，不将 agent_turn 的内部文本提升成公开回复。处置标记从结构化处置回执索引取得，首屏不加载 agent_turn.rounds 推导。

索引缺失时，在 worker 分块重建当前父会话；可先扫描尾部构造有界公开窗口，再在后台补全旧页，不能先等待协调恢复。遇到公开消息巨行或多行跨块时正确组装，不从半个 UTF-8 字符或 JSON 片段发布内容。持续冲突返回 rebuilding/version_changed，稳定损坏返回明确错误，不制造成功空页。

### 4.2 Coordination Store 的增量事件与查询

扩展既有 Coordination Store，内部由 Legacy Adapter 与 v2 Adapter 承担格式差异。消费者使用命令与查询 Interface，不继续调用全量 read().works 做所有事情。

```ts
commitCoordinationEvent(event, ownership): DurableReceipt
readWorkHead(workId): WorkHead
readRecoveryCandidates({ parentConversationId, cursor?, limit }): CandidatePage
readCurrentMandate(workId): MandateFacts
readOperationReceipt(operationId): ReceiptState
readPendingDispatches(workId): DispatchFacts
readDeliveryState(replyId): DeliveryFacts
readAuditPage({ workId?, attemptId?, cursor?, limit, byteBudget }): AuditPage
```

WorkHead 只持有聚合用量、当前状态、当前进展窗口/摘要、待决调用和引用；不包含累计 observation IDs、所有已处理事件、全部旧 attempt 或完整调用结果。恢复候选目录含用户输入时间、到期 reservation、未处理事件和 checkpointRef 等必要小字段，不为排序打开检查点。

已有 store.read()/readSnapshot() 保留为显式诊断/兼容入口，逐步移出主 Bot 日常、卡片、预算 Guard 和恢复候选选择。Implementation 的事件提交、幂等、租约、版本及索引一致性集中在一个 Module，不能把 JSON/SQLite 的切换摊给各个调用者。

### 4.3 Project Facts 与上下文查询

在既有 Project Facts / SessionSupervisor 查询 Seam 提供按相关任务的 summary、单任务 report、指定过程和可见卡片查询。复用 ADR98 Query Scope 和 Catalog，限制先作用于候选索引，再构建内容；不能先 Supervisor.list 全量 hydrate 后 slice。

Renderer 读取 Interaction 不调用 ProjectFacts.cards。任务卡和恢复动作独立读取，并携带当前来源版本与可用性。原子语义的状态元组继续来自 ADR102 生命周期判定；界面不自行拼一个“正在运行”。

主 Bot 的 executeTurn 改用 readInteractionContext；本轮任务信封由相关性查询供给既有 project-roster Context Source，仍只进 L7_CONTINUITY，不调整既有系统层顺序。用户问跨任务总览时允许读取有界名册和分页查询；用户要求调查指定任务时才读取报告、过程及 Evidence。本轮 selected attempt 已取得的可靠 Tool Results 可作为其执行连续性保留，不强迫每次重新取证。

复用 get_session/get_verification_detail、过程详情和 Evidence Provider。需要补分页参数或新能力时，必须先定义 protocol、Manifest、Projection、PermissionGrant 和 Evidence 返回，不在 prompt source、renderer 或 IPC 临时执行文件读取。

## 5. 增量持久化的具体设计

### 5.1 事实源、文件与索引

保留旧 coordination.jsonl 和原 checkpoints；v2 在同一 project-runtime/<workspaceId>/ 内新增 versioned manifest 与分段事件文件。原受保护检查点、GoalPlan、Conversation 和 Evidence 正文不迁入数据库。

建议路径（实施时登记 DATA_STORE_ENTRIES 的目录语义）：

```text
project-runtime/<workspaceId>/
  coordination.jsonl                  # 旧 v1 原文，激活后不再追加
  coordination-v2/manifest.json       # 版本、generation、legacy anchor、分段链
  coordination-v2/segments/<id>.jsonl # 有界增量事件，已封段保留
  checkpoints/<content-hash>.json     # 沿用原生受保护检查点与大对象引用
cache/read-models/
  coordination/<workspaceId>.sqlite  # 可重建的当前状态与精确回执索引
  interactions/<conversationId>.sqlite
```

projectRuntime 继续为 device；readModels 新登记为 cache。派生库的记录不得进入 portable 导出；导出已有 Conversation 和 Evidence 的规则不因本方案放宽。使用现有 node:sqlite / SQLite Seam，不增加依赖或顶层 package。

日志是协调事实源，SQLite 是日志的可重建物化投影；不是日志和数据库两套可独立写入的真值。数据库可以被重建，但从 canonical 记录重建完成以前，不得把空表当作没有权限、没有待决写入或可以重复派发。现有 openSqlite 的损坏后创建空库行为不能直接用作恢复成功。

### 5.2 事件形状与防止再次写放大

事件 envelope 包含 schemaVersion、generation、workspaceId、seq、epoch、operationId、workId/attemptId、kind、payload、前序锚点和校验摘要。由宿主分配顺序和身份，模型不能提供执行权威。每个事件必须有确定的 reducer 和错误规则。

按原运行语义记录 usage_observed、model_request_reserved、tool_dispatch_reserved、tool_settled、attempt_checkpointed、attempt_finished、work_transitioned、progress_observed、event_handled、reply_prepared/delivered、mandate/transition 变化等小事件。一条事件可包含同一原子变更所需的多个小字段，不能拆散“去重收据 + 用量增量”的原子语义。优先沿原 semantic Interface 输出事件，禁止任意 JSON Patch 修改权限、签收或执行版本。

- usage_observed 每次只记录一次稳定 observationId、原始来源引用与用量增量。精确已记账集合保存在可重建的 receipts 索引，不再嵌入每条 WorkHead。重复 observationId 返回原回执，不写一个新的完整 work，也不重复计费。
- 工具派发与结果结算仅写该 toolCallId 的变化和真实 Tool Result/Evidence 引用。未知结果保留 unknown，不靠记录一个 checkpoint 当作成功。
- progress_observed 保存稳定事实身份和窗口增量；沿 ADR95/103 判断新进展，时间、随机 ID 和请求计数不算新进展。进展窗口可以有界，但历史事实仍留在事件归档。
- 原生检查点沿现有 content hash 去重；事件只写 checkpointRef。大 payload 先落不可变对象、fsync，再提交引用它的事件；失败留下的未引用对象不自动清理现有任务材料。
- 明确无语义变化的重复保存不追加事件。工具准入、用量预留、取消、reply_prepared 和 delivered 等关键持久化边界不允许用 debounce 延迟确认。
- 新增元数据事件建议硬上限 64 KiB，超过则拆为可验证引用或返回结构化错误；不能截掉 Tool Result/Evidence。段按约 32 MiB 轮转，已封段只读保留。轮转限制单文件，不宣称历史总存储恒定。

固定大小的新观察只增加固定数量事件与索引项；总协调元数据随真实事件量近似线性增长，不随“累计历史 × 保存次数”增长。全量状态导出仅显式诊断使用；不得每隔固定事件数重新保存整个历史 receipts 数据库形成新的二次写放大。

### 5.3 提交顺序与崩溃一致性

1. 在既有 workspace 单写者/lease 下核对 epoch、目标版本、当前调用和政策；索引须追到当前可信日志 head。
2. 先持久化事件依赖的大对象；按 operationId 判断精确重试，再把事件追加至活动段并 fsync。
3. 同一 SQLite transaction 应用 reducer 的最小变更、精确回执及 appliedSeq/segmentOffset/headHash；成功后返回 durable receipt 并发布通知。
4. 日志已持久而数据库提交失败时，不向执行器返回可以重新派发的普通失败。返回带 operationId 的 durable_pending_projection；先重放已落盘事件并查询原回执，再继续。恢复不能再次调用模型、工具或外部系统来重建索引。
5. fsync 之前崩溃、fsync 之后/索引之前、索引之后/应答之前、reply_prepared/Conversation append/onReplied 之间分别注入崩溃测试；保留现有跨存储的可恢复提交协议，不假称跨文件或外部副作用具备 SQLite 原子事务。

重复请求与乱序 request completion 使用精确集合和来源身份，不能只用“最后一个 requestIndex”去重，也不能用有误判的集合结构承担预算、派发或回复送达真值。

## 6. 大日志恢复与旧数据演进

### 6.1 首次重建与正常启动

Legacy Adapter 用字节分块、UTF-8 流式解码及跨块行边界读 v1；验证 schema、连续 revision、文件身份和尾部完整性，绝不整文件 toString/split。本次 809 MiB 是大文件而非巨型单行，必须作为完整生产夹具覆盖。超出声明单记录上限的旧记录显式报告 record_too_large，保留原文并交给专用离线恢复，不偷偷丢行或截短。

纯解析/reducer/索引重建在 worker 分片执行，支持进度、取消和断点；不执行能力，不占 renderer，也不把同步大循环挪到 Electron main。只对选中项目/会话重建；其他项目不连带扫描。

现有预算 Guard 与 Store 有同步调用约束，不能把 read() 直接换成返回 Promise 而遗漏执行时序。启动/重建放在宿主显式 readiness 异步边界；worker 生成暂存投影并核对来源后发布，ready 之后由短时同步索引查询满足既有命令边界。源码若需要把某条命令异步化，必须连同所有调用者、取消和错误顺序一起修改并测试，不混用两种返回形态。S1 即引入只读 v1 派生投影，S3 再让 v2 事件维护同一查询 seam；迁移期 Guard 的旧数据语义不变。

有有效派生库时，启动校验 generation、schema、文件身份、已封段摘要及活动段已应用前缀锚点，重放 appliedSeq 后的尾部。封段使用单写者不可变约束和文件版本检测，受影响或来源不明时重校验；不能每次启动为验证摘要再次扫描整个历史。严格审计另有全量校验入口。活动段换文件、同长度改写、缺段或 revision gap 均拒绝发布“已恢复”。

无有效索引时，一次后台线性重建可慢，Interaction 必须独立可用。该项目的写命令在其权威恢复完成前返回 recovery_pending；不冻结其他已就绪项目。已有对话可查看，新输入可沿原 InputQueue 持久接收并明确排队，不虚构已经处理。

### 6.2 v1 → v2 激活流程

1. 开发/验收只使用隔离副本；不直接修改、迁移或重启当前日常实例。
2. 新版宿主取得原 lease，在安全点阻止新的该项目写入；记录旧文件身份、大小、终止 revision、hash 和恢复游标。现有任务、输入、结果及未知派发均不清零。
3. 只读扫描原文件到已验证的完整边界，构建新投影和 migration manifest。v1 work 快照的累计计数是覆盖语义，绝不能逐条相加；所有 observation/operation/delivery 去重身份精确保留。
4. 逐 work 对账：状态、累计用量/未知标记、mandate/goalRevision、待决工具、未消费事件、送达收据、任务关系、检查点和 Evidence refs 一致。原文件 hash 不变；不是“成功读到末尾”就算迁移成功。
5. fsync 新文件与目录后原子发布 v2 generation/legacy anchor 激活回执。v1 原文件原位保留、停止追加；后续仅写 v2 增量。重启从已激活 generation 继续，重复迁移不得新增任务、重算费用或重放副作用。
6. 激活前失败：删除/隔离未激活的派生临时物即可重试，原数据不变。激活后失败：从保留的 v1 前缀 + v2 事件重建，不能切回旧 v1 最后状态继续执行。

文件末尾不完整、内部损坏、源文件持续被改写分别给出结构化状态；沿既有“原文备份 + 验证完整前缀 + 持久恢复回执”的修复原则，不隐式跳过内部损坏。只确认截断尾不会恢复未知副作用。

### 6.3 版本与降级

manifest 声明 minimumReaderVersion/minimumWriterVersion；所有支持此契约的 Desktop/TUI 宿主在写入前检查。不能为兼容旧版本长期双写全量 v1，否则会原样恢复写放大。

旧二进制不认识新 fence，不能仅靠新 manifest 保证其拒绝接管。因此不承诺 v2 激活后任意降级可安全续跑。版本交付必须说明：停止所有宿主后使用兼容修复版；若未来要求旧格式执行兼容，另做经过对账的完整反向导出/迁移。不得把保留下来的旧 v1 文件当作最新可执行状态。

## 7. 对话加载与故障隔离

沿现有 typed IPC 提供 Interaction、可见卡片、任务摘要和过程详情的独立查询；必要参数/返回字段先进入 Protocol 和 preload 合同。无需新通道的先扩展原通道；不把任意 include 参数暴露成文件路径入口。

页面状态按 messages、cards、workSummary、details 分开：

- Interaction 首屏先发布。协调恢复失败只让相应任务卡显示“状态暂不可用/正在恢复”，不清空或隐藏已有消息。
- 刷新失败保留上一成功页和滚动位置，显示可重试状态；旧任务事实若展示必须标明版本/更新时间，不能作为当前状态或可执行准入。
- 首次没有成功页时显示加载失败和重试；不能用空消息列表冒充成功。旧页加载失败只影响旧页，主输入和当前已读内容可继续操作。
- 同一 section 最多一个在途和一个待刷新标记，局部重试、跨 Bot 迟到丢弃、卸载取消沿 ADR98。事件成功提交后才推进游标，不能因坏卡片吞掉最终结果或人工问题。
- 详情失败有自己的错误和原始引用；用户可以继续阅读交互，再选择查看该任务/过程/证据。

任务状态不可用时，取消/批准/继续等动作由命令端当前事实决定是否可执行；展示旧按钮不能放行，错误卡片也不能替代 PermissionGrant 或人工决定。

## 8. 验收门槛

### 8.1 保留与一致性

- 原 Conversation、GoalPlan、检查点及 Evidence 文件逐份 hash 与 ID/refs 对账；每条任务保持原身份，状态/验收不被导入过程修改。
- v1 与 v2 reducer 在相同逻辑操作后的 work、预算、未知派发、mandate、delivery、事件消费和恢复候选等价。重复用量、并发完成和重启保持精确计数。
- 取消/暂停/显式预算/权限拒绝/未知副作用/损坏检查点不被恢复流程解除；有效任务从原可靠检查点继续，已完成写入和已投递回复不重放。

### 8.2 读取与规模

- 对话首屏与主 Bot 的日常上下文准备路径，instrumented 子会话正文、历史 journal 回放、checkpoint 与 Evidence 正文读取次数均为 0；允许读取父会话交互索引及当前必要的权威小字段。宿主在命令提交边界核对当前 head、追赶尚未应用的尾部和落盘回执单独计量，不冒充模型加载历史，也不允许因此恢复全历史扫描。
- 加载一个任务只读取该任务的摘要/报告；打开一个 attempt 只读该过程页；点击 Evidence 只读对应正文。加入十倍无关历史不扩大这些查询的返回量与深层读取集合。
- 809 MiB 脱敏等价夹具与至少 1 GiB 生成日志冷重建成功；增量读取无整文件字符串和全量 structuredClone。重建附加内存目标：worker <256 MiB、main <64 MiB；硬件/基线 RSS 单列。极端单行独立测试并报告支持边界。
- 有有效索引时最近交互首屏 p95 <500ms；日常热 Interaction 查询 p95 <50ms。一 GiB 冷重建耗时、实际读字节、最大事件循环停顿单列实测，不把后台工作尚未结束算作执行已恢复。
- 生成相同形状的 1,000/10,000 次请求与工具事件；v2 协调元数据体积增长不超过 12 倍，固定 metadata 事件 p99 目标 <8 KiB、硬上限 64 KiB。检查点/真实 Evidence 的增长单独列出，不能通过不保留它们降低指标。
- 重启有效投影时读取量随未应用尾部和当前候选增长；不扫描所有封段、终态工作和无关子链。

### 8.3 故障与产品

- 注入协调读取失败、缺索引/损坏/落后、磁盘满、写后应答丢失、进程强杀、部分尾、内部损坏、跨进程 append/rename/同长度改写及旧 writer 竞争。
- 消息可读、草稿不丢、局部错误可重试；未知状态不显示为正常执行；真正人工等待和最终回复不会被过滤。
- 按实施卡跑定向、受影响包完整、typecheck、architecture、IPC 与跨 Desktop/TUI 集成；UI 变更按 product-regression 完整 Capture → 逐图 AI 审查 → Verify。明确审查是否独立，以及真实模型、安装版、无障碍覆盖边界。

## 9. 实施落点与验证边界（2026-10-22）

用户已明确批准实施。代码在隔离工作树验证后按文件增量回写 Peer-Agent，保留原有未提交修改；不重启、替换或安装当前运行实例，不在真实数据根激活 v2。

- Conversation Store 增加 `readInteractionPage`、`readInteractionContext` 与 `readInteractionProcess`。公开交互索引放在 `cache/read-models/interactions/<store namespace>/`；worker 对当前父会话流式建索引，随后增量追尾。界面分页发生在可见交互集合上，主 Bot 的 Desktop/TUI 模型准备走公开交互查询。公开进展与处置回执保留薄投影，私有 rounds 不入默认页；显式打开过程时按 canonical 记录字节位置读取对应回复与 turn。
- 模型历史当前保留全部公开用户输入/正式回复，交由原上下文机制处理，不新增启发式窗口以静默遗忘用户边界。§4 的 tokenBudget、超大公开正文分片和独立 audit/process 轮次分页仍是后续扩展 Interface，本轮不宣称这些概念 API 已全部落地；当前单 canonical 记录上限 64 MiB，界面按最多100条公开交互分页、另带关联薄投影，过程读取粒度为一个选定turn。
- 主 Bot 的 turn roster 先按 work/session/输入锚点选取最多 24 个计划摘要，不构造子链报告或读取子会话正文。命令端仍保留权威生命周期核对，摘要不授权执行。项目指令、记忆、能力与权限仍沿原 Context Source/Projection 链。
- Desktop/TUI 模型装配必须保留交互查询已准入的旧版公开 user/assistant 消息；缺少 kind 不代表内部过程。不得在宿主再次仅按新 kind 过滤，静默丢弃旧用户约束。私有 turn/round 的排除由统一交互查询负责；真实模型入参回归同时断言旧用户/助手交互保留、私有过程不进入请求。
- Coordination Store 在原 Store 内提供 v1/v2 Adapter。v2 分段 journal、哈希链、持久 head、来源版本和 lease 检查共同约束恢复；小更新写差量，usage 精确去重单独索引，不在 WorkHead 或每次事件中复制累计 observations。语义无变更不写新记录。超出 60 KiB 的真实事件内容放到 content-addressed blob，journal 保留 hash/bytes 引用，回放校验原文。
- 协调派生库放在每个项目 runtime 下的 `.read-models/coordination-<cacheId>.sqlite`（`coordination-current.json` 指向当前缓存代），属于本机可重建缓存，旧 reader 不会把它当 canonical。该布局让当前 Store 的所有权、原文、分段和重建发布保持在同一个 Module seam；缓存可以删除后重建，不能将其缺失解释为空状态。
- 首次恢复等待 worker 完成后才开放 Guard 的同步查询；索引只在完整校验后发布。canonical fsync、head 持久化之后 SQL 提交失败，返回 `durable_pending_projection`。半截尾先 fsync 原文备份与恢复 intent，再替换有效前缀、重建并追加恢复回执；内部损坏、缺失已提交日志、hash 不符或旧 writer 改写均失败关闭。
- 消息、任务卡、过程详情独立读取；任务卡失败不隐藏对话，刷新失败保留最近成功消息，首次失败明确显示错误，提供重新读取入口。进程结束/超时有明确错误，不无限等待 worker。
- Worker 从 canonical reducer 源生成自包含代码，生产构建重生成；Node/Electron 与 Bun 单文件编译产物均使用同一实现，避免发布后 URL 指向不可用源文件。

最终串行实测：848,647,853 字节（约809 MiB）/8,593 条原日志副本完整最终状态（9 个 work）与 v1 reducer 深比较一致；冷索引回放约2.439秒，完整诊断读取约3.10毫秒，20ms心跳最大额外延迟约2.17毫秒，结束时进程总RSS约245 MiB。1 GiB合成日志6,858个快照，冷回放约2.937秒，热work查询平均0.201毫秒，心跳p99额外延迟约2.10毫秒、最大2.36毫秒，结束时进程总RSS约275 MiB。这是整个Node进程的结束时RSS，不是worker独占/峰值或新增内存；未清空OS文件缓存。早期并行验证负载下的15.24秒/227ms样本保留在本地回执，不作为最终串行指标。

固定形状 usage 事件 1,000 次为 347,172 字节，10,000 次为 3,488,174 字节，增长 10.05 倍；最大 metadata 记录 386 字节，p99 349 字节。精确 tokens 为 10,000。该指标覆盖 usage journal，不外推为所有工具载荷或整盘物理写入量；SQLite、head、检查点和 Evidence 单列，不以删除证据换指标。

已测：进程在日志 fsync 后、SQL 提交前 SIGKILL；同一用量回执不重复计数，未知派发不自动重做；缺索引/损坏派生库重建；缺失持久分段拒绝执行；尾部损坏保留原文备份；大 payload 原文恢复与 hash 损坏拒绝。窗口与全仓回归已通过，源码已按文件增量回写日常代码仓；205 张截图的实现者自审及原仓库 verify 均通过。最终 Node 7,906 通过/5 跳过、Bun 764 通过，完整构建与类型/架构/IPC 检查通过。精确回执、源码指纹、覆盖边界见配套实施卡 §6。当前安装版、真实云模型、读屏与跨平台发布不在本轮通过结论内。

### 派生库发布与持久性补充

每次重建发布独立 SQLite 文件名，并原子更新 `coordination-current.json`；旧连接的 WAL/事务只能接触旧文件。不能以同名替换数据库同时保留别的进程的打开连接。并发持有旧 SQLite 写事务、发布新代、再提交旧事务的生产 Store 用例验证新状态不受影响。

canonical 分段与 head 始终显式 fsync，才提交派生库事务。重建候选采用 WAL/FULL、完整 checkpoint 后发布；日常可重建投影采用 WAL/NORMAL，避免让可丢弃的缓存每次重复强制落盘。依据 [SQLite synchronous 规则](https://sqlite.org/pragma.html#pragma_synchronous)，WAL/NORMAL 保持事务原子与一致，断电可退回旧缓存提交；缓存的来源版本/offset/head 回执随同一事务提交，因此旧缓存必须追赶 canonical 尾部后才可使用，缺失/损坏则重建。这里不降低 canonical、权限、Evidence 或原始任务的持久性要求。不得改为 journal_mode=OFF 或把缓存当唯一回执。

TUI 公开交互轮询改为异步、合并在途请求并拒绝跨 Bot 迟到结果；可选卡片/摘要失败保持交互，界面保留最近成功消息并提供 `/latest` 重试。终端相关测试等待真实查询完成，不以固定 sleep 代替就绪条件。

### 空基线与 head 缺失

激活 v2 前也要持久化 revision=0（或已导入 v1 revision）的 head，然后发布 manifest。已有 v2 manifest 而 head 丢失必须拒绝读取/执行，不能在索引和分段同时缺失时把它当作新项目空库。首次激活在 head 与 manifest 之间中断时，从保留的 head generation 恢复，验证原文 revision/hash 后再发布；缺失 manifest 但仍有 v2 目录也不得退回 v1 读取路径。

### 渐进查询的交互身份

按 live turn ID 打开的详情在正式回复落盘后，应定向解析为当前公开 reply + 对应 turn，保持原过程的展示状态和可返回的消息锚点；不能因精确 ID 命中内部 turn 而丢失公开 reply。消息与卡片分开查询后，自由输入的问题关联与页面展示必须共用合并后的公开投影；重试保留同一个 answerTo，卡片不可用或已解决时不能偷偷绑定旧问题。宿主仍实时校验问题和输入，不把这份展示关联当作授权事实。

持久 head 同时保存并校验 `legacyVersion` 来源锚点；不能仅凭 revision/hash 相同就认定 legacy 基线相同。manifest 与缓存同时丢失后，若 legacy 文件被同 revision 改写，必须返回 `coordination_legacy_changed`，不能重建出新状态继续执行。激活时来源锚点取自已验证候选索引，并在持久 head/manifest 发布前重检；后续 head 沿用该固定锚点。该故障先以缺失预期拒绝的红测试复现，修复后纳入故障回归。

### Node / Electron / Bun 的 SQLite 后端（RC25 发布前修正）

双平台 CI 固定 Bun 1.2.17，不提供 `node:sqlite`；仅在较新 Bun 验证不足以证明发布兼容。统一 SQLite Connection Seam 的同步语句、行迭代、关闭与错误码 Interface：Node/Electron 使用 `node:sqlite`，Bun 使用原生 `bun:sqlite` Adapter，不改变 fsync、事务与恢复顺序。错误码归一化只支持既有 SQLITE_CORRUPT / NOTADB 判断，不把权限、空间或忙状态伪装为索引损坏。

Connection Implementation 由 runtime-node 的既有 sqlite Module 持有；Conversation Store 的本地 Adapter 与两个自包含 worker 在构建时从该单一源生成，不增加重型运行时依赖或第二份 SQLite 逻辑。生成内容随构建与源码指纹校验；独立包和 Bun 单文件编译产物均验证 worker 重建。保留流式 statement iterator，不用全量数组替代。发布验证使用 CI 同版 Bun 1.2.17，并保留首次 CI 失败回执。原生 Bun 接口参考[官方 SQLite 文档](https://bun.sh/docs/runtime/sqlite)，旧版本行为以实际二进制回归为准。

Bun 1.2 的未缓存 Statement 需显式 finalize 后才能严格关闭数据库。Adapter 为每次同步执行或行迭代持有独立句柄，结束后立即 finalize；连接关闭收束剩余句柄，不能为每条历史记录永久保留一个句柄。保留 Node 与 Bun 的事务回滚、只读错误码、损坏错误码及独立迭代契约测试。Node/Electron 的 worker 配置 192 MiB old-generation 上限；Bun 1.2 不支持该选项，因此仅使用既有有界行读取和 worker 超时，不宣称有等价的 Bun heap 硬限制。

真实父会话隔离副本：公开交互首次查询约27.73ms，100次热查询p95约1.11ms；模型历史25条公开用户输入/正式回复，私有turn为0，canonical文件SHA-256前后不变。10,000次usage回执串行持久化约137.4秒；该批量循环不作为UI延迟基准，fsync持久性未被降低。


## 2026-10-28 补充契约：迁移后旧日志分叉与受控恢复

用户授权：修复真实历史数据兼容、保全并核对两条日志、安全恢复、阻止旧 writer、明确错误反馈；不重跑已完成写入、不发布。级别 A（存储与恢复边界），B（恢复准入与状态投影）。本节补充既有失败关闭要求，不将冲突日志直接视为合法续写。

### 事实、身份与冻结

- manifest 的 legacyVersion 是原基线的物理身份，不能拿当前文件 token 替换。迁移后追加的旧日志和 v2 分段可以占用相同 revision，却包含不同事实。只按 revision 排序、拼接、重建或删除派生库均不能解决分叉。
- 维护首先生成独立、持久、带 SHA-256/字节数的原文保全包，包含两条日志、head/manifest、检查点、输入队列及必要的关联资料。在线只能只读核对；应用仍持有 host.lease 时禁止提交修复。备份自身的 lease 副本须显式移出后才可作离线候选。
- 每次核对绑定全部来源摘要；提交前再次校验。不接受变化后的来源、不跟随符号链接、不通过助手文字、时间先后或 UI 点击认定事实成功。旧基线缺 seal 时必须显式记录该证明限制，维护提交须绑定人工审阅的基线摘要，不自动补造历史完整性证明。

### 深 Module 与恢复发布

- 在既有 Coordination Store 旁提供离线维护 Interface：inspect 仅生成两分支的确定性回放与差异；recover 只消费绑定来源摘要、已审阅基线的计划，生成可审计候选。维护不是模型工具，不创建 PermissionGrant 或 Evidence，不调用 Provider、GoalRunner、执行器或外部写入。
- v2 分支须从 manifest 指定旧文件字节前缀开始，核对行边界、连续 revision、完整分段、payload 引用、哈希链与持久 head；旧尾单独从共同基线回放。禁止把带重叠 revision 的尾部直接喂进 v2 reducer。
- 对不冲突对象作三方合并；冲突的工作保留两个版本、输入归属、检查点、预算与已观察凭据。不能用较新时间、较大 revision、最大预算或偏好分支冒充一致性。所有历史未终结工作保持恢复阻塞，等待真实派发/交付对账；已送达、取消和 coalesced 不变成 runnable。未结算写入始终 unknown，禁止以恢复为名重放。
- 新 generation 的规范基线由既有 reducer 可验证的恢复事件承载，回执引用完整保全包和差异；原日志/分段字节保留。修复 intent 先 fsync，再发布路径屏障和 manifest；任何中断保持关闭，可凭 intent 幂等收尾，不可落回旧格式或自动执行。
- 输入持久接收与执行准入分别表达；恢复阻塞不能丢输入、伪造回复或显示一直生成。恢复动作不 consume/complete 用户输入、不自行签收任务、不推进模型。重新进入宿主恢复时，历史输入由原 work 归属与回执去重，冲突 work 的恢复准入独立拒绝。

### 旧 writer 的真实屏障

- 新代码的 legacy Adapter 在读、提交前均检查 v2/维护标记；新宿主在取得执行资格前检查最低可读/写版本。不能声称这些新增字段会约束已经发布的旧二进制。
- 完成受控恢复后，旧的 coordination.jsonl 路径改为目录屏障，规范基线放进新代只读基线文件；旧版按该固定文件路径 open/append 会被操作系统拒绝。原文复制到独立 inode，不让旧的已打开 descriptor 改写新基线。维护只能在无活动 lease 的离线副本进行，旧文件改名后的竞态/中断记录进 intent 并拒绝不一致提交。
- 新存储读取受保护的 manifest 位置，不绕回旧路径；旧读取失败不能当空项目。回退旧版本须用完整独立旧备份，不在已升级目录写入。

### 用户反馈与回归

状态事实使用共享协议投影：错误码、恢复阶段、是否可安全重试；主界面给“历史任务记录冲突，已暂停执行；消息已保存”，诊断保留具体原因。单纯重新读取与维护恢复分开，永久冲突不展示无效的“重试”作为修复操作。现有对话、草稿、焦点和阅读位置保留；不把原始错误/机器路径塞进正文。

回归须覆盖真实组合的脱敏 fixture：迁移后原文件追加37条、同revision不同记录、缺seal、598条v2增量与head、旧输入归属、已完成写入/未知派发；另覆盖前缀被修改、分段缺失/hash损坏、同名payload冲突、来源变化/符号链接、活动lease拒绝、修复各步骤中断与重入、旧进程路径append失败、恢复状态前后端投影与无空白回复。真实保全包仅留本机，绝不提交用户资料。日常仅运行用户本轮授权的恢复/相关定向回归；完整发布验证另行进行。

健康项目的实现补充：Runtime Host 在持有现有 lease 的 Store prepare 中安装同样的旧路径屏障（新空项目也覆盖），无需等到分叉才防护。健康基线经 SHA-256 证明相同字节的新 inode 保存；新物理锚点与原 head 的相同 revision/hash 在 `coordination-fence.json` 中绑定并幂等发布，原 head/manifest/seal 归档，不将物理身份重新绑定说成任务事实变化。发布未完成时 reader 拒绝；prepare 先恢复 intent，再读取/执行。分叉维护仍要求无 lease 的离线副本，不能沿健康迁移通道接纳改变的旧源。完整操作与证据见[协调历史恢复卡](../../playbook/coordination-history-recovery.md)。

## 2026-10-28 补充：用户可操作的恢复与安全续跑

状态：Accepted（用户明确要求完成根因修复、普通用户恢复与安全续跑；保留历史和成果，不重复执行已完成操作。本轮只开发，禁止运行测试或发布）。A：恢复准入、持久状态与协议；B：宿主交接、调度和 UI。

### Interface 与事实边界

- 沿既有项目租约管理同一数据目录的执行权。客户端显示占用实例类型和版本，提供显式接管动作；原宿主按既有 yield/drain 路径暂停、等待执行器空闲后释放。不得删活锁、以超时强抢、由 renderer 写锁或通过开发端口误判执行身份。
- 新 `ProjectRecoveryRequest/Result` 是主窗口专用 IPC，操作仅包括检查、保全恢复、复查续跑和保留成果结束旧执行。只接收 workspaceId、宿主生成的来源绑定 token，以及互斥的 workId/sessionId；不接收路径、候选内容、预算、权限、检查点或执行结论。恢复属于本地维护控制，不暴露为模型能力，不产生伪 Tool Result/Evidence。
- 独立 Recovery Service Module 负责计划、来源校验、幂等发布及安全分区；现有 Runtime Host 提供静默暂停/空闲屏障与租约 epoch。原离线恢复入口仍要求无 lease；宿主内维护必须在持有原租约、停止该项目调度且排空模型/子任务后执行，所有发布步骤反复核对相同租约。不解除其它实例持有的租约。
- 先保全两条原始日志、所有被引用的普通/原生检查点、输入队列与游标等关联控制资料，再按来源摘要发布恢复候选。原始资料、输入、已交付结果不移动到空白项目，不重写历史会话，不把人工选择变成已经执行成功。

### 安全分区与持久准入

- 恢复候选初始仍全局阻塞。新增追加式 `history_resume_admitted` 事实绑定原保全 fingerprint、当前 revision 和每个旧 work 的内容摘要；覆盖全部历史非终态 work，不接受遗漏、重复或对终态的改写。
- 只有无分支冲突、无重复输入归属、无未结算 dispatch/工具、无待送达回执、检查点内容地址和 job 身份核对通过的续跑才能恢复原工作。已完成工具结果必须完整保留；含工具的续跑还须有匹配的原生/Provider 检查点。原生检查点同样纳入哈希保全。
- 已交付/取消/coalesced 保持终态；等待用户仍保留等待语义。其它不确定 work 保持单独隔离，不再用全局屏障永久阻断无关新输入。原 inputBindings、anchorInputIds 和事件归属保持，不把旧输入重新当新指令。存在事件/送达/输入归属分支冲突时拒绝自动选择历史，保留阻塞和可读说明。
- 隔离同时在自动恢复选择、手动重试、调度器/工具执行和子任务恢复入口强制生效，不能仅靠 UI disabled 或提示词。关联子任务在没有可证明恢复依据时继续暂停；不因主对话准入而自动恢复它们。未知写入结果不重放、不当失败后自动重试。
- 用户可显式选择“保留成果并结束这次旧执行”：通过既有结构化取消路径收束相关子任务，再追加取消的 work 事实，保全所有报告、检查点、用量及两条历史。此动作不声称未知操作未发生，不标成成功，不重发原输入。无法确认暂停/取消完成时保持隔离。
- 维护中断可按相同来源 intent 继续；已发布但未准入的恢复可复查，不重复移动原始数据。来源变化、校验失败、租约丢失和停机不完整均保留可重试/可诊断状态，不清空资料或自动执行。

### 落地约束

- 原始只读候选仍使用 reader/writer 3；写入 `history_resume_admitted`、`history_work_retained` 或 `history_session_retained` 前原子提升至最低 reader/writer 4。已发布 v3 二进制必须先拒绝新日志，再谈读取或写入；健康项目不无故提升版本。原有物理路径屏障继续生效。
- 普通检查点按 workId 绑定内容地址；原生与子任务检查点按既有 workId:attemptId 绑定，不能套用父 work 的摘要种子。所有引用的检查点纳入保全；缺失或结果未知不会被伪造为可续跑。
- 准入同时持久保留两条分支的旧 input/event 归属，隔离历史待送达 reply、未完成 coordination operation 和全部尚需核对的子任务（包括不属于任何父 work 的任务、未确认验收或待合回的成果）。重复复查只更新历史隔离，不将之后的新任务/交接/回复纳入旧隔离。停等用户、暂停、预算等原状态在复查后仍保留。
- Runtime Host 的维护屏障拒绝旁路 restart，并等待已经开始的 sync/recovery 完成；真实 lease 不释放。停止旧执行的等待有明确失败出口，超时只表示仍未确认停止，不表示可以执行。普通 IPC 读历史、消息草稿和关闭详情不解除屏障。
- 隔离覆盖自动调度、队列等待后的派发、恢复/回复重试、旧事件唤醒、验收、交接及自动清理。恢复期间完成的日志尾部修复不得覆盖或丢弃 `lastRecovery` 的隔离事实。检查直接读合法日志前缀及来源摘要，不通过 `prepare()` 隐式修复日志；只有明确恢复动作才进入现有 Store 的尾部保全/修复流程。
- 用户结束旧执行前沿既有取消路径排空，并持久写下 `DelegationOrigin.retainedForRecovery` 或 cancellation.preserveArtifacts；后续清理继续遵守保留工作树的选择。未知派发、报告、预算回执和检查点仍在原处与保全包中，不转写成执行成功。
- `canContinue` 表示历史分区准入；`runtimeReady` 独立来自宿主是否就绪。界面不以准入回执冒充模型已开始回复。维护阶段通知经既有 changed 通道，完成后停止重复扫描，不轮询整份历史。

### 普通用户体验与本轮范围

聊天顶端提供明确的原因、下一步和“检查并恢复”入口；恢复详情默认用任务名称、可继续/等待核对/已保留的数量表达，原始错误码和本地备份位置按需查看。显示真实阶段（检查、保全、核对、完成/失败），不编造百分比。未确认前只检查；明确点击后才能变更本地历史。完成后明确区分对话可继续与仍隔离的旧任务，并允许复查或保留成果结束旧执行。关闭面板保留草稿、阅读位置和后台维护事实，不等于取消或清除维护。

开发交付只做源码和 diff 审阅；新增回归源码但不执行测试、构建、类型/架构/IPC 检查、UI 截图或真实数据恢复，不重启安装版，不发布。不将实现写成已经验收。

2026-10-29 修订：恢复入口改为只在有待处理事项时显示，IPC 新增绑定计划 token、不接收 id 列表的“全部结束旧执行”（`retain_all`），准入后的复查不再重做保全。本补充中的 IPC 操作清单与“检查并恢复”入口两处，以 [ADR 113 §4.6](113-checkpoint-content-addressed-storage-and-retention.md#46-恢复入口按需显示全部结束旧执行与准入后复查) 为准。
