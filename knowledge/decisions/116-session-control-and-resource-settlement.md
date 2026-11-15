# ADR 116：任务控制、执行停稳与资源交接

创建时间：2026-11-01
最后更新：2026-11-08（文末确认 ADR 124 的可见性修订不改变本文的释放条件。未合并草稿不是已发布运行时）

2026-11-03 契约澄清：Session Control 统一拥有子执行停稳与 unknown 作用域。SessionTakeover 不得在 applied 停止回执之外把主 Bot 自己仍在执行的协调 metadata 调用算成子任务 unknown。误挂 awaiting_outcome 的接管可凭原操作的当前停止证明恢复；另一操作、新 generation、历史撤回或助手文字不能替代该证明，真实未知 shell 仍保留目录保护。接管仍 stopping 时，原生恢复的 prepare 与 commit 必须返回 coordination_reconciliation_required，不能先覆盖 control 或创建新 generation，再遗留未完成接管与撤销中的绑定。依据、边界及分阶段验证结果见[故障分析](../../playbook/v0.1.0/agent-wait-recovery-closure.md)。不改变持久化结构或最低版本。

存量兼容补充：旧宿主已经形成“原接管 awaiting_outcome、原停止回执空 unknown、后来的 native resume 已 applied、当前 queued 新 generation 仍被原 mandate 撤销准入”的组合时，单纯拒绝再次 resume 不能恢复原责任。共享 Runtime 只在原 proposal 仍由该 session 的当前 takeover 持有、没有竞争中的未完成操作、同目标 active mandate、原绑定仍撤销且未重绑、真实 canonical resume 锚点、原 stop → resume.priorStopReceiptId 链完整、worker 从未开始（零执行回合且无开始事件）、无 live/unknown/未结束句柄时准入一次兼容停止。该判断由独立的事实校验 Module 完成，不从闲置状态或时间推断停止，也不以历史对象的枚举顺序判断哪个 proposal 仍有责任。

兼容停止使用原 Session Control 的 pause/barrier/settlement，为当前 generation 建立新的有界空 unknown 停稳回执，不重写旧回执或伪造原工具结果。原 transition 通过该匹配当前身份、以 coordination-recovery:<原operationId> 绑定的回执重新进入 stopping，随后原 takeover 端口恢复原任务并绑定原 proposal 的新 epoch。租约、goalRevision、停止、人工门及资源准入继续逐次重检；重复冷恢复不重复启动，同目录其他真实 unknown 保护继续阻止执行。使用既有记录格式及控制对象，不提高门槛或新增模型工具，不以此自动操作当前个人任务。

排队准入必须先消费当前协调绑定事实：binding 仍被撤销或对应 transition 未完成时，在资源预留和 plan.phase=running 之前返回 coordination_reconciliation_required。不能先将任务选中、预留资源，再把可预期的协调等待写成 execution_resource_owner_changed/failed。该查询使用现有轻量 lifecycle facts，避免在队列与状态投影中反复复制整个工作预算和检查点。
状态：Accepted / Implemented in source（2026-11-01；实现者内容/diff 自审，发布验收未执行，运行中的应用未升级）
级别：A（控制、准入、恢复和持久化契约），B（调度、事件和共享宿主），C（状态表达）。

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[架构治理](../architecture/20-architecture-governance.md)、ADR [85](85-project-agent-hosts-inputs-and-surfaces.md)、[91](91-project-bot-autonomous-coordination.md)、[96](96-task-execution-responsiveness.md)、[102](102-unified-task-lifecycle-projection.md)、[110](110-follow-up-responsibility-and-current-list.md)、[111](111-project-agent-duplex-supervision-and-continuity.md)、[112](112-runtime-module-and-loading-boundaries.md)、[113](113-checkpoint-content-addressed-storage-and-retention.md)。[实施卡](../../playbook/v0.1.0/session-control-and-resource-settlement.md)。

## 1. 决策

由共享 Session Control Module 统一暂停、取消、接管和恢复；调度器消费明确的资源占用与停止回执，不再扫描 `cancellation/takeover/phase/status` 猜占用。GoalPlan 继续持有目标、结果和验收真值；coordination-v2 保存执行控制及停稳事实；设备本地资源账本持有跨项目的占用和交接事实；Protocol 的 `decideLifecycle` 仍是唯一产品生命周期出口。

三件事分别成立：**用户是否还委托、执行体是否已停稳、资源是否能交给下一执行者。** 撤回可以结束跟进责任；历史结果未知继续保留；可能冲突的资源保护不会因退出列表消失。

深化 ADR91 的 Session Lifecycle seam，不另建 Task 表、调度服务、权限系统或工具执行通道。

## 2. 已核对的问题

源码基线 Peer-Agent `5dffbd4b4ced0bb841c9e879debd50b8bb081b9c`；知识基线 Peer-Knowledge `10707b62945cf47d7080cfb9161b166f07ffae23`。本节是源码/现场只读核对，不是测试或发布验收。

| 事实 | 代码锚点（相对代码仓的 `packages/runtime-node/src/project-agent/`） | 缺口 |
|---|---|---|
| `occupying` 在终态检查前令 takeover stopping 占写名额 | `execution-scheduler.mjs` | 已取消任务仍能挡队列 |
| 取消完成保留旧 takeover；接管异步尾部发现 cancellation 就退出 | `session-cancellation.mjs`、`session-takeover.mjs` | 两条局部流程留下永久 stopping |
| takeover 的 pending Promise 仅在进程内 Map | `session-takeover.mjs` | Promise 消失不等于操作完成 |
| 隔离规划与调度分别判断谁是写者 | `isolation-planner.mjs`、`execution-scheduler.mjs` | 同一现场得出不同占用结论 |
| 已有 epoch、取消回执、unknown、用户撤回和统一投影 | `execution-ownership.mjs`、`session-facts.mjs`、`coordination-kernel.mjs` | 应收敛事实，不能另建脚本绕过 |

现场旧任务 cancelled、取消回执 completed，却保留 takeover stopping；新任务仅有 queued，无 Worker 执行记录。对现有计划做生产 `inspect` 的只读调用，返回 write_slot，阻塞者正是旧任务。远端 PR 已合并只是背景事实，不能证明本机执行已停。文档不保存私有任务正文或用户机器绝对路径。

仅把终态判断提前会让“终态已写、工具仍活跃”的任务提前放出资源，因此不作为完整修复。

## 3. 不变量

1. 每个 session 只有一个当前控制操作；旧操作保留历史但无当前调度权。
2. 先耐久记录意图并关闭新执行准入，再中断、等待和收口。请求停止不等于停止完成。
3. 终态、取消标记、无 live token 都不能单独证明资源可释放；实际活体和未结清执行优先保护。
4. 取消覆盖接管时必须明确终结旧接管，不以删除历史字段掩盖竞争。
5. 用户撤回沿 ADR110 §7：受管执行停后可结清委托，不要求无限追溯历史；不清 unknown、预算、Evidence 或未来冲突保护。
6. 接管保留 session/plan、目标、成果、预算和核验义务；改变执行代次。目标身份改变才 replace。
7. 旧 epoch 不能新派发或推进当前目标。迟到结果属于原历史，不能释放新执行者资源或证明新结果通过。
8. 每个阻塞有依据、范围、责任和下一步。无变化不调用模型；确定性收尾和队列恢复归宿主。
9. 所有能力仍走 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。调度许可、停止回执和用户撤回都不等于工具权限或验收。

## 4. Module 与真值归属

| Module | Interface 与职责 | 不承担 |
|---|---|---|
| GoalPlan | 目标、成功标准、阶段结果、核验、签收 | 从持久 running 猜活体 |
| Coordination Kernel | mandate、goalRevision、TaskTransition 的协调意图 | 工具是否实际停稳 |
| Session Control | `request / reconcile / readFacts`；当前操作、停止屏障、停稳和交接回执 | 语义规划、任意项目写入、批准权限 |
| Resource Admission（深化 Scheduler） | `inspect / reserve / activate / settle`；设备本地资源账本提供原子占用，Scheduler 决定公平排序 | 猜验收、直接杀进程 |
| Provider / Executor | 真实执行句柄、取消能力、结果与提交回执 | 决定目标是否仍有效 |
| HostLease / Writer Fence | 当前宿主及持久写者身份 | 证明旧外部进程已停 |
| Protocol Lifecycle | 输出唯一 status/actionRight/followUp 和资源阻碍 | 由界面生成执行事实 |
| Desktop/TUI/CLI | 同源表达和既有 typed command | 自建锁、取消器或恢复算法 |

Session Control 的 Depth 是让调用方不再理解 abort、idle、unknown、epoch 和跨记录写入顺序。取消器/接管器逐步成为入口，Supervisor 只装配；不把复杂度搬进新的大 TaskManager。

## 5. 控制操作与竞争

### 5.1 一份控制真源

同一 coordination-v2 日志增加 `SessionControlOperation`。它是执行控制记录，不是第二份任务状态。每个 session 通过预期版本 CAS 更新当前操作；GoalPlan 的 cancellation/takeover 成为可修复兼容镜像，新消费者不从镜像重建第二份真值。

| 字段 | 契约 |
|---|---|
| operationId/requestDigest/revision | 幂等和 CAS；同 ID 不同参数拒绝 |
| workspaceId/parentConversationId/sessionId/planId | 宿主核实作用域，模型不能签发 |
| kind | pause/cancel/takeover/resume；replace 组合取消与原有新任务创建 |
| authorityRef/coordinationOperationRef? | 当前用户控制来源或有效 mandate 决策；可关联原 TaskTransition |
| expectedExecution/targetExecution? | 旧绑定和拟接手绑定；goalRevision/executionEpoch。legacy 用经校验的计划版本引用，不造 mandate |
| phase | recorded → draining → reconciling → settled；无需对账可 draining → settled |
| outcome/supersededBy/nextAction | settled 明确 applied/superseded/rejected；未收口给结构化原因和依据 |
| stopReceiptRef/resourceSettlementRefs | 真正停稳与资源处置，不是接收请求的回执 |

TaskTransition 保留目标修订、替代关系和协调进度，引用控制操作，不再自己运行第二套停止流程。控制 settled 不等于任务成功：takeover applied 后仍可能 queued，实际 started 和 executionEffect 分别记录。

直接用户取消 legacy session 可以没有 mandate，沿原入口核对来源，不因此生成新的执行授权。自动接管/恢复仍必须有有效 mandate。模型不能用维护名义取消无关任务。

### 5.2 身份

hostEpoch 是现有写者代次；executionEpoch 是执行绑定代次；attemptId 是实际执行片段；operationId 是控制操作。PID 不是可靠拥有者身份。停止只针对 expectedExecution 及其受管后代；释放同时核对 claimId、旧代次和 revision，旧 finally 不能释放新 claim。

源码契约补充：同一 coordination binding 的合法暂停/恢复不重签 mandate；执行身份携带可选 `generation`，由已登记 resume 控制的 operationId 产生。Worker/Verifier/Explorer 的宿主 turn profile 冻结该身份，真实派发同时核对它与当前计划，不让旧回调读取新绑定后冒充新回合。它是执行代次，不是新的权限或模型上下文来源。

### 5.3 竞争裁决

| 竞争 | 规则 |
|---|---|
| 同一请求重复到达 | 同一操作继续未完成阶段，返回当前回执，不重建任务 |
| 取消与接管 | 同一旧绑定取消胜出；同一日志提交标旧接管 superseded、封新绑定。若新绑定已启动，取消需重新覆盖并停稳当前绑定 |
| 接管 A 尚未完成又有合法 B | CAS 接受新意图，A superseded；已发出的停止继续收尾，只有 B 可获得新绑定 |
| 用户暂停与自动续跑 | 用户暂停保持；旧事件不能解除，需合法用户恢复 |
| 签收后纠正 | 保留原签收；新纠正关联原工作，不改历史为从未完成 |
| 丢租约 | 旧宿主封新派发和业务写回；新所有者接管收尾，原结果只沿可验证历史回执入口返回 |

较新时间戳不是授权；“最新意图”只在来源、范围和预期版本合法时成立。旧 resume 不能复活已取消委托。

superseded 只终结旧操作的决策权，不证明旧执行已停；当前取消/接管继续承担同一旧绑定的 drain 责任。旧操作迟到的真实停止观测可以按原身份补入事实，不能自行重新绑定、释放当前资源或恢复执行。已经 applied 的历史操作不追改为 superseded；新控制引用实际当前绑定。

## 6. 资源模型

### 6.1 三类资源

- **计算**：既有 coordination/work 回合名额；等人/父代理时释放；保持现有协调保障、总并发和 Provider 限流。
- **执行目录**：同一规范目录写入互斥，只读准入限额不变；worktree 经宿主核实才算隔离。
- **副作用保护**：未结清调用可能影响的目录、Git 共享状态或外部对象。引用既有能力范围，不让模型猜路径；无法证明细范围时保守保护原资源。

v1 不做文件级锁或全能分布式锁。不同 workspaceId 指向同一目录必须冲突；宿主通过既有 filesystem/Git seam 核实规范身份、符号链接、别名和目录替换。worktree 不隔离共享 refs、远端发布或外部账户，这些继续受既有能力范围和冲突约束。

### 6.2 占用与保护

设备本地 Resource Admission 账本记录 claimId、resourceRef、session/plan、executionEpoch、hostEpoch、用途、来源、revision 和状态：

```text
reserved → active → draining → released
    └──────────────→ reconciling → released
```

reserved 在 Runner start 前耐久提交，防止候选同时看到空闲；启动失败只有证明未 dispatch 才可直接释放。active 表示有资源使用资格，不表示此刻在调用模型。等人/父代理默认保留目录 claim，防止修改现场被另一任务破坏；计算名额已释放。若以后允许等待时交目录，必须新增停稳、版本保存和重准入契约。

draining 保护旧执行仍可能触及的资源；reconciling 保留尚未解除的风险。没有按 TTL 自动释放；超时只触发一次确定性核查或给出阻碍。

旧执行 claim 安全收尾后，历史 unknown 对应的保护可转为 `ResourceHold`：原 dispatch、resourceRef、原因、处理归属和解除依据。hold 由原 unknown 事实派生，不创建工具结果真值；旧 claim 结清和 hold 建立同一资源账本事务，没有无保护空窗。单纯“历史未核实”不当作活跃写者。

### 6.3 交接表

| 事实 | 资源结论 |
|---|---|
| 只有 cancelled/completed 字符串 | 不足以释放 |
| 只有没有 live token，尤其重启后 | unknown，需核对 attempt/句柄 |
| 匹配停稳回执，且无相关 live/unknown | 可以结清 claim，文件保留不等于占锁 |
| 用户撤回完成、历史结果未知 | 受管回合的计算名额释放；旧执行 claim 按停稳事实结清；相关 hold 保留 |
| worktree cleanup 失败 | 单独保留实际清理资源/句柄，不能占无关主目录；失败可诊断 |
| 账本 released 但同代真实 live | 一致性故障，阻止冲突准入并核对，不盲信旧记录 |

Scheduler、IsolationPlanner 和 Runner 准入共享同一资源事实。inspect 无副作用；reserve 重检当前控制/依赖/版本，再在设备账本事务内核对资源 revision 和冲突后提交，不能拿过期 inspect 当许可。start 前仍重检控制和宿主当前性。队列继续沿原优先级/老化规则，不将资源分离变成全局 FIFO 阻塞。

### 6.4 为什么需要设备级原子账本

仅在各项目 coordination 日志里保存 claim 不够：不同 workspaceId、不同 Desktop/TUI 进程可能指向同一目录，各自持有有效项目租约，却同时认为目录空闲。因此拟增加设备 scope 的 `project-runtime/execution-resources.sqlite`，复用现有 SQLite adapter；它是资源占用真源，**不是 Task/Goal 或权限真源**。各项目日志只保存 claim 引用和交接操作，不再保存一份可独立裁决的占用副本。

最小表为资源身份、claim/hold、稳定操作回执及待交付资源事件。一次事务检查全部所需资源并一起 reserve，冲突时全部不取，避免持有 A 等 B 的锁环；只存 claim 即可解释的身份和依据，不复制工具正文或凭证。DB busy 有界重试后返回资源存储忙，不调用模型或先执行再补账。

任务启动可预知的目录资源先申请；工具选定后才知道的附加范围必须在 dispatch 前准入，不能因已有目录 claim 直接扩权。扩容冲突时不在持有部分资源的状态下无限等待：返回结构化冲突，由控制路径停稳、保存现场、释放可交出的占用后，以完整资源集合重新排队；unknown 对应 hold 不能为此解除。跨资源动作仍逐次核对权限，调度资源集合不是能力许可。

这里不存在跨项目日志/GoalPlan/SQLite 的分布式原子事务。采用保守、幂等顺序：先在账本 reserve，再记录项目引用，全部成立才 dispatch；停稳事实先耐久提交项目日志，再以其身份/revision 在账本原子 release/转 hold；最后补项目镜像。中途崩溃最多留下保守占用，恢复按稳定 operationId 对账，不出现先释放后补停止证明的空窗。账本提交后丢响应，先查询同操作回执，不重复 reserve。

资源释放及通知 outbox 同事务提交。进程内通知走现有事件入口；跨进程由已有宿主 pulse 对排队资源的 compact revision 去重检查和补送，不新增周期模型调用或重复扫描完整项目历史。多个资源同时请求时按稳定顺序检查；不同项目的排队候选仍使用原优先级/老化与稳定顺序竞争。

资源拥有权保证限于支持本契约、共享同一设备数据根的 Peer Runtime；外部编辑器、独立数据根和不支持该契约的任意旧二进制不在互斥保证内。已知不兼容旧宿主占用相关项目时拒绝接手，不能用数据库锁假称已停止它。Provider 自身的全局并发/远端互斥继续各归原契约。

## 7. 唯一停止屏障

1. **record + fence**：耐久记录当前意图并禁止旧代次新 dispatch；提交后才回接收回执。同进程先关闭执行泵，持久化失败保持 fail closed，不启动新任务。
2. **signal**：结构化取消传播给 Worker、Verifier、Explorer、受管工具和排队许可。人工问题按原生命周期关闭/失效，不代用户回答。
3. **drain**：等待 Runner 与 Scheduler idle、Provider 句柄收尾；沿 ADR96 terminal barrier 提交已得到的文本/Tool Result。abort Promise 返回不能独自证明停稳。
4. **reconcile**：结合 canonical dispatch、真实 attempt、句柄和 Evidence 区分结束、仍运行、结果未知。不读模型文字、PR 合并状态或计时器猜成功。
5. **settle**：CAS 写匹配旧绑定的 StopBarrierReceipt，按 §6.4 结清资源账本，再完成控制和 GoalPlan 镜像；中途失败保持可诊断的待收口责任，不丢已提交事实。
6. **promote**：处置提交后发送稳定资源事件、幂等推进队列；候选版本改变重取事实，不重放原工具。

StopBarrierReceipt 引用操作/执行身份、fence、受管执行 idle、Provider handle 处置、terminal commit、unknown 集合及 scope、结论和时间。它证明的范围必须明确：受管执行停止不等于外部效果回滚或消失。

Provider 只能中断请求、不能确认外部异步工作停止时，相应保护保留。缺少可靠范围则保守保护原资源；缺少句柄/查询 adapter 时列为能力缺口，不能宣称已可确认。查询和补偿仍经能力主链，不私启进程或后台脚本。

等待超时不写 settled、不放锁、不无限重发取消。保存待确认项和合法 nextAction；同事实核查无进展后等实际事件/合法人工动作，不周期调用模型。

fence 与工具派发有明确线性化点：同一执行绑定的 admission gate 串行化停止与派发登记。fence 之前已登记但尚在传输中的调用算 in-flight，必须取消/收尾或确认未 dispatch；之后的旧代次调用一律拒绝。不能用“尚未收到工具响应”假称工具未执行，也不能宣称能撤销已交给外部系统的动作。

适用本契约的执行器必须在真实 dispatch 前耐久登记意图，结果落盘后结算；只有这种顺序下，恢复才能将“无登记、无句柄且 start 尚未提交”解释为未执行。旧记录缺此保证时保留 unproven，不用缺记录补造未执行事实。

## 8. 端到端行为

| 流程 | 时序与结果 |
|---|---|
| 用户取消/撤回 | 校验 canonical user_input 与对象 → 停止屏障 → 终结旧接管 → 取消 completed/资源处置 → 唯一投影退出跟进。有 unknown 时沿 ADR110 保存 withdrawal/user_withdrawn/evidenceCalls/preserveArtifacts，历史不清账，相关 hold 不变 |
| 原任务换执行者/返修 | 有效 mandate → takeover → 停稳旧执行 → 持久交接包/反馈 → 无阻碍后同 session 新 epoch → reserve/queued → actual start。保留预算、失败统计和核验义务；旧核验不证明新执行通过 |
| 目标替换 | 原 TaskTransition 先停错误方向，再创建关联替代者；旧资源可交接才启动。创建失败不复活错误方向，不宣称跨外部服务原子 |
| 正常结束 | 片段结束释放计算；任务继续用目录时保留 claim。最终执行/核验停稳且记录提交后按原 handoff 义务结清，成果保留不占锁，返修/合回重新 reserve |
| 明确暂停 | 停稳、保存现场、释放可释放资源；恢复重新核实目录版本、依赖和权限，不假设暂停期间无人修改 |
| 失败 | 同样核对活体和 unknown；不因 failed 字符串放锁，不把一次 Run 失败等同目标失效 |

自动纠偏没有当前用户撤回来源时，继续原 awaiting_outcome 保护。接管反馈持久接收、执行者观察、修复已应用沿 ADR111 分别记录，不混成成功。已签收历史保持原事实。

## 9. 重启、崩溃与多宿主

恢复顺序：校验 HostLease/Writer Fence → 校验最低版本 → 还原控制/claim/hold → 核对 GoalPlan 镜像、句柄和未结清 dispatch → 补确定性缺失步骤 → 按资源开放准入。

| 崩溃窗口 | 恢复 |
|---|---|
| 停止意图未落盘 | 无耐久接收回执；同请求身份重试，先核对当前事实 |
| fence 已提交，signal 未发 | 从原控制继续停止，不重发原任务 |
| 已 signal，停稳未记 | 查询实际句柄/终态提交；缺事实保持 reconciling |
| stop receipt 已落盘，资源未结清 | 账本保守占用；按原证明和 operationId 继续结清，不重复执行 |
| 资源已结清，镜像未写 | 资源账本和原停稳事实优先，幂等补镜像 |
| 资源已处置，promote 未送 | 稳定 ID 补送；启动时也对账一次队列 |
| reserve 后 start 前 | 证明未 dispatch 才释放/重准入；无法证明先核对 |
| 新 epoch 已绑定，旧 finally 到达 | 不得改当前控制/claim；旧结果只进旧历史 |

租约过期不证明旧工具已停；PID 复用、系统重启、孤儿进程、外部异步工作按原 Provider 句柄核实。进程内 token 为空不是结束证明。没有查询能力保留有范围的 unknown。

恢复只影响相关资源，不为一个旧任务冻结所有项目；无法确定范围则保护原工作区并解释依据。事件至少一次投递、稳定 ID 去重，恢复原操作而非重开工作。watchdog 检查真实未收口阶段和缺失交付，不按周期问模型进度。

## 10. 产品表达与控制

沿主对话一名 Agent 一行、当前任务和按需详情表达，不新增调度管理首页。

| 事实 | 第一层表达 | 责任与操作 |
|---|---|---|
| 尚未获得资源 | 已排队，等待某任务释放当前目录 | Bot；可查看 blocker、取消本任务 |
| 已接收停止，尚未停稳 | 正在停止，已阻止新操作 | Bot；查看待收尾项，不说已取消 |
| 旧接管被取消替代 | 历史记接管已终止 | 不再独立占待办或成为假 blocker |
| 用户撤回完成，历史 unknown | 委托已撤回；有历史结果未确认 | 退出当前跟进，保留原调用入口 |
| 新任务被历史 hold 挡住 | 暂不能写入：此前操作结果未确认 | 新任务 owner=bot；查看范围和核对进度 |
| 接管已登记，未启动 | 已安排接手，排队中 | Bot；不冒充执行或修复成功 |
| 停止无法确认/丢租约 | 尚不能确认执行已停止 | 系统阻碍；原接管/诊断入口，只有真实决定才交用户 |

既有 queueReason/queuedBehind 扩为带 discriminator 的 blocker：任务依赖、活动资源拥有者、历史保护、恢复阻碍分别引用 ID/版本/依据。hold 不塞成假 session 标题；inspect 与界面消费同一结论。

followUp 与 resourceProtection 是两个维度。已撤回任务 followUp=none 仍可有历史 hold；处理义务绑定原控制/恢复记录，新冲突任务引用它，不制造重复监督者或额外人工待办。没有无条件“强制解锁”按钮；允许沿既有能力核对、取消自己的排队工作、在已有范围内选择隔离执行。

体验契约：目标是停止/接手后真实可继续，事实来自本机控制、执行、资源与原授权/验收；失败保住现场并给出合法恢复。后台不抢焦点、不清草稿、不重新贴底、不切走用户看的任务。状态行保持 sessionId；沿 Frost/PeerIcon/共享动效，reduced-motion 仍有完整静态终态。实施时更新交互和 UI/动效/过渡矩阵；设计文件不代填已实现/已验收。

## 11. 遗留收敛、格式与回退

对 `cancelled + cancellation.completed + takeover.stopping`，先核对取消的权威依据、旧绑定/操作、后续绑定、live、unknown 和宿主 fence。可证明停止和取消覆盖时，追加旧接管 superseded 与资源处置，幂等补镜像、自动推进队列；不要求用户重新委托。

证据不足标 legacy-unproven，走同一停止屏障；不凭 cancelled/completedAt 批量签发停稳回执。本次现场只证明旧标记导致 write_slot，具体资源能否放行仍须新路径核对，设计不是现场解锁证明。所有修正追加，原 unknown、预算、失败、对话和 Evidence 不删除；不直接编辑生产 JSON。

控制事实沿已登记 projectRuntime 的 coordination-v2 journal/blob；新增设备资源 SQLite 必须登记 DATA_STORE_ENTRIES、设备 scope、schema、保留/备份和恢复责任。该存储边界变化是本 ADR 的明确提案，不能作为一个无文档缓存混入实现。

资源 DB 初建先封新写准入，在兼容宿主治理下扫描已有绑定/停止回执，建立可证的 claim、hold 或 unproven 保护，再开放相关资源。不依靠删除并重建 DB 解锁。DB 损坏/缺失/来源项目不可读时关闭受影响准入：资源身份无法界定则本设备 Peer 写准入保守关闭，保留只读诊断；由原日志和执行句柄恢复，不能恢复出伪 released。备份覆盖数据库及 WAL 的一致性，运行中不只复制主文件；跨设备复制该设备账本不产生资源资格。已释放历史按现有运行记录保留政策处理，未决 claim/hold 不被 TTL 或普通垃圾回收删除。

首次写新语义前提升最低 reader/writer/executor 能力。在现最低 6 基线上拟升 7，实施时核对主线占用，head/manifest/重建不能降门槛。旧宿主必须拒绝执行，不宣称忽略新字段即可安全兼容。

只读历史可以保留；未决控制、active claim 或 unknown 未安置前不降级执行。回退先封新准入、停稳并保留记录；不能切回旧 occupying 继续写或删字段降版本。坏引用/损坏日志 fail closed，阻断范围不超过可证明受影响的资源；无法界定时保守保护原工作区。

## 12. 取舍和交付边界

不采用终态直接放锁、删除 takeover 标记、清空队列、按 TTL 解锁、无限模型重试或要求用户重复取消。也不把全部 unknown 永久当全局锁；保护实际范围，不足时解释保守边界。

本批不含文件级锁、自动文件回滚、任意进程清理、跨设备执行同步或新模型协调器。代价是版本化控制/资源记录和恢复规则；收益是取消、接管、交接和诊断集中，调用方无需组合多套局部状态机。

实施依次为：契约与纯决策 → 停止屏障 → 资源准入统一 → 重启/遗留恢复 → 同源表达 → 最终候选验收。详见实施卡，包括安全、活性、崩溃和产品矩阵。

前一阶段只完成设计和内容/diff 审阅。随后用户明确授权完整实施；当前源码交付及未执行项见下节，发布门禁仍按 AGENTS.md。

## 13. 2026-11-01 源码实施收据

代码起始基线为 RC31 主线 `73ff763a`，已同步实施期间的新主线 `0f68f281`；交付提交 `6923cc9a`，[代码 PR252](https://github.com/ly-ccx/Peer-Agent/pull/252)，分支 `codex/session-control-resource-settlement`。知识分支 `codex/task-resource-lifecycle-design`。保留原代码工作区、知识仓其他改动和已运行实例，使用独立工作树实施。以下是源码实现者自审，independent=false；不是运行或发布验收。

| 卡片 | 已落地的 Interface / Implementation（代码仓相对路径） |
|---|---|
| SC-01 | Protocol `session-control.ts`；`session-control-kernel.mjs` 的操作身份、CAS、取消 supersede、匹配回执和不可变来源；coordination-v2/store/replay/fork/writer-fence 最低版本 7，按 session 索引读取；设备存储登记 |
| SC-02 | `session-control.mjs` 共用停止屏障，cancellation/takeover/continuity 接线；`execution-handles.mjs` 收集 Provider 原生句柄；Desktop/Node 普通与持久 Shell 接入，实际派发前重检权限、原代次与资源 |
| SC-03 | `execution-resources.mjs` 设备 SQLite 事务化 claim/保护/稳定回执/资源事件；Scheduler、IsolationPlanner、Runner 准入共用；`execution-scopes.mjs` 规范目录与 Git worktree 的 commondir；文件目标目录及 Shell cwd/共享 Git 范围在派发前准入 |
| SC-03 扩容 | `session-resource-contention.mjs` 把真实冲突转为同一停止屏障：持久完整需求、封旧派发、停稳并交目录、新代次重排；SQLite 保留需求，只有匹配结清回执可转绑。不持有 A 等 B，不周期调用模型重试；unknown 仍保护原范围 |
| SC-04 | 原取消来源按 canonical user_input 与 workspace/parent/session/plan 复核；旧 completedAt 与原取消契约可作为 legacy 适配依据，仍重新 drain；无来源/活体/句柄无法确认则 reconciling。显式追加 takeover superseded，保留原 unknown、预算、对话和成果；恢复按原操作幂等继续 |
| SC-05 | `controlPhasesForOrigin` 进入原 decideLifecycle；Desktop/TUI 共享资源 blocker，详情显示涉及目录并沿原入口查看此前任务；未新增焦点、草稿、滚动或动画所有者 |

停止等待有 30 秒默认诊断边界；到期只记录 `execution_stop_unconfirmed` 并保留保护，不签发停稳或释放资源。同一事实不重复发停止；实际句柄、回执或派发事实变化后再核查。回执绑定 claimId/revision/执行身份；同回执不同正文拒绝，旧代次/旧 revision 不能释放新 claim。正常任务结束也经过屏障收掉仍存活的持久 Shell，最终核验重新取得所需目录。

本次现场的新任务已有独立 worktree。新准入可以区分它与旧任务主目录；历史 unknown 不再冒充“仍在接管的任务”。这不证明共享 Git refs 或外部效果安全：Shell 仍须取得真实 commondir 范围，冲突则保存并重排。未提供可验证查询句柄的外部 Provider / 脱离受管句柄的异步对象，不在本批的停止确认保证内；保留既有 unknown 和保守原资源，不通过猜 PID、PR 合并、模型文字或 TTL 解锁。

已编写协议投影、kernel、journal 重开/格式门槛、双连接资源竞争、目录 alias、完整多资源申请、旧 receipt、后台句柄、停止 deadline、legacy 权威来源及真实旧形态/独立 worktree 队列恢复用例，并更新原调度夹具的真实目录和结清边界。生成式 storage worker 已从 canonical 实现重新生成；只做改动文件/嵌入源码的解析审阅和 diff 空白审阅。**未执行单元/集成测试、build、typecheck、architecture/IPC 或截图/交互回归**，不称任何用例已通过；SC-R 留待最终组合发布候选。

没有修改生产 JSON、清空未知调用、清理用户目录、安装、重启或发布。当前安装版和现场任务尚未因源码交付自动改变；新恢复逻辑在包含本变更的 Runtime 正常取得宿主权后运行。交互与 UI/动效/过渡矩阵同步记录源码状态，不继承历史 RC 的验收。


## 14. RC32 组合发布接口（2026-11-01，实施中）

与 ADR117 串行整合时，组合最低特性门槛升为 9，保留真实的格式 7 控制 reducer 与格式 8 意图 reducer，旧 writer/executor 对新活跃数据继续拒绝。完整约束见 [ADR117 §15](117-intent-driven-coordination-and-goal-closure.md#15-rc32-与-adr116-的组合契约2026-11-01实施中)。本文件的独立分支格式 7 收据保留为历史；设备账本、停止和 unknown 保护不因 Intent 根关闭而释放。组合验收尚未完成，不能继承两个分支各自的自测结论。


RC32 整合补充（代码 PR252）：恢复前先通过同一 Session Control 停止屏障，等待执行/Provider 句柄期间释放 supervisor writer，再回到 writer 条件提交停止回执与新执行代次；恢复不重新暂停已准备好的 runner。替换任务启动失败也必须结清其已持有的资源，不只修改任务状态。文件 Provider 在创建父目录前即重检资源范围，创建后在写入前再次重检权限与范围。有关本地用例已通过；不是对最终组合候选或已安装版本的验收。

联合格式 9 的首次启用顺序在代码 PR253 `b03a4711` 修正：先初始化并检查原设备资源账本，再发布 9 的协调门槛，防止普通 Intent/回复先启用格式后导致首次任务被缺账本保护拦截。已有 7/9 数据缺账本仍 fail closed，不把已遗失状态当作首次初始化；导入、claim、停止与 unknown 保护的归属不变。详见 ADR117 §15 的补修收据。

## 15. 停止收尾活性补修（2026-11-02）

本次修复沿用既有控制、资源账本及回执契约。旧取消不只包含 canonical user withdrawal：旧宿主在 abort、runner idle、scheduler idle 后写下的取消完成审计，也可作为 legacy 停稳适配来源。必须同时匹配 cancellation 的请求/完成时序、同一计划的 `session-cancellation` 完成审计时间与原因，且完成后无新的执行/绑定变化；单个 completed 字符串、时间戳或模型自述仍不足。接纳来源后仍重新关闭准入、停止受管句柄并等待 idle；不清 unknown，不以此生成工具成功或新的执行授权。

停止等待超时是诊断边界，不取消仍在进行的 drain。实际等待随后完成且当前操作、执行身份、宿主权仍匹配时，耐久提交停稳回执并唤醒原取消/接管收尾；迟到的旧操作不能写当前操作。恢复缓存必须包含这些新事实，不因同一 nextAction 永久忽略已完成的停止。接管遇到停止屏障未完成时保留可恢复操作，不把暂时超时变成永久拒绝；新目标/人工门/取消仍优先。

资源导入不得在有效 stopReceipt 之后反复重写保护 revision，使原回执永远过期。匹配回执先重放账本结清，真实活体、未结束句柄和 unknown 仍保留保护。内容/diff 自审及新增回归用例不等于发布或安装版验收。

旧 takeover 的适配另有严格前提：原计划的结构化 `turn_started/turn_completed(done)` 必须成对、最后一次独立核验已有宿主 `verification verdict` 提交，随后只有同一 takeover 请求及暂停/控制写入，没有新回合、准入、绑定或执行代次。新屏障只停稳并暂停旧意图，结清后显式退休遗留 takeover，不重跑 Worker、不代替用户恢复旧工作。缺任一事实仍保留可定位保护。相同 unknown hold 的重复结清不得刷新 revision 制造假进度。

## 16. 成功派发回执与排队自阻塞恢复（2026-11-02）

RC34安装后现场确认：父回合已有登记的 `spawn_session` 成功Tool Result及completed协调操作，派发期间预算attempt曾留pendingTools；资源导入把该父回合调用当成新子任务的未知执行，为尚无Runner的queued任务建立reconciling claim。后续attempt已退役且预算pending已清除，旧claim仍未随之结清，重启仅把它显示为owner_changed。RC34的通用截图/测试通过不能替代该真实队列出口验收。

本补充为A级既有恢复事实契约扩充、B级宿主与调度修复；不改变能力、权限、Evidence真源、System Context或存储边界，不增加执行入口、数据库或格式最低版本。沿既有work预算增加typed `settledDispatches`，只记已核对调用的身份、登记Evidence引用、协调operation、目标版本/执行代次、子session及时间；不是新Tool Result、目标成功或验收。

仅对闲置父attempt的spawn_session或该attempt已退役后遗留的同源claim做确定性恢复：同时匹配原dispatch/turn、work/parent、已登记且同capability的Evidence索引、规范agent_turn中同引用的完整成功结果、已completed的parallel协调操作及replacementSessionId/目标版本。对于attempt已退役的claim，必须从其原toolCallId沿登记Evidence精确找到规范turn，并额外匹配claim的session、目标版本和执行代次；不能借用其他任务的成功回执。助手正文、截断预览、索引孤立记录、缺失/模糊结果、其他工具、活跃attempt或来源变化均不能结清。保留原历史和用量，不重放工具、不重新创建子任务；最后一项pending消除后可退役已无活体的attempt，未观测的用量仍为unknown。

queued自阻塞的资源收口仍走Session Control和原StopBarrierReceipt。只处理无Runner、无接管/取消、无实际活体或未结束句柄，且已核对派发回执与当前session/executionEpoch/goalRevision严格相同的既有任务。重新检查当前租约与控制，封准入、确认runner/scheduler/handles idle、取得unknown集合为空的真实停稳回执，再由资源账本幂等结清；未匹配的历史unknown仍保护原范围。不能因queued、无PID、时间或任务终态直接删除claim。新回执仅恢复原任务准入，不产生新mandate或授权、不签收成果。

运行中有活体的父协调attempt，其未返回metadata调用不属于子执行代次的unknown集合；父协调仍受原模式能力白名单与自己的回执/预算约束，子执行自己的pending调用继续保守保护。已失去活体的父attempt仍须完整回执对账，不能按role直接清除。

恢复先对账已登记派发回执，再导入/核对资源；运行中相同事实也可在原宿主修复周期处理。缺少证据继续失败关闭并给具体原因，不做全设备强制解锁。发布门禁须加入该真实形状的冷恢复：一次派发、原任务身份/历史保留、同目录后续准入、无重放、未知shell与无关保护保留；同时实际安装版确认原队列有执行进展后才交付修复。

## 17. RC35 现场目标变化与验收分层（2026-11-02）

§16的原queued现场已在最终联合源码上通过隔离冷恢复：规范历史、登记Evidence、协调存储、停止屏障与普通supervisor使同一原任务进入执行器恰好一次，没有重放派发。执行器入口为受控记录，不是一次真实模型执行或任务验收。

验证期间本机原目标已通过产品被取消。较新的用户取消优先，不能为了满足“原任务推进”观察而重新启动已取消任务。候选宿主启动后实际核对当前Plan、停止回执及设备资源账本：取消completed、runner/scheduler idle、unknownCalls为空、原claim released，同目录没有未释放占用；当前一致性账本副本上的原调度准入允许新执行。这不修改个人任务事实或创建新任务。正式安装版复核另记在 [RC35回执](../../playbook/v0.1.0/rc35-candidate.md)，不能将隔离回放或源码准入升级成已安装执行进展。

另一目录的历史Shell调用仅有合成的cancelled_outcome_unknown及缺少退出状态的旧本地材料，不能推断未执行或成功；原范围保护继续保留。本轮不以它制造工具成功、空unknown集合或全设备强制解锁。该现场收据没有改变§16的事实门槛、能力和授权边界。

最终RC35正式签名安装版已启动并持有原项目租约和新鲜心跳；安装后再次核对上述取消、停止回执、原claim released和同目录未释放占用为0，对当前账本副本的新执行准入仍通过。原任务的较新取消决定保持，没有为验收复活旧任务。发布资产、包内7处修复摘要、备份与安装范围见 [安装回执](../../playbook/v0.1.0/evidence/rc35-installation.json) 和 [发布回执](../../playbook/v0.1.0/evidence/rc35-publication.json)；不是一次原任务真实模型执行或完整安装版UI验收。

## 后续（2026-11-07，ADR 124 已接受；释放条件不变）

[ADR 124](124-legacy-stop-obligation-controlled-resolution.md) 已接受并授权实施。它增加只读核实和授权后退役跟进，并要求新的取消登记带上本机启动标识、PID 与进程起始时刻。资源释放仍只走本文的停稳回执。PID、空 token、租约更换和终态字符串仍然不能单独结清 claim，也不存在强制解锁。死亡证明以 ADR 124 第 7 节的元组为准，只作用于实现交付之后的新记录。

2026-11-08 的可见性修订不改变本段。确认后退役仍不写停稳回执，也不释放 claim。索引不对用户开放的规则见 ADR 124 第 8.3 节。未合并的 Peer-Agent PR 297 不是已发布运行时。
