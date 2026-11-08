# ADR 124：遗留停止义务的受控核实与跟进退役

创建时间：2026-11-07
最后更新：2026-11-08（用户在 Peer-Agent PR 297 手测通过后确认「要」：待核实不对用户开放。退役仍写内部索引 `disposition=indexed` / `obligation_indexed`，留给诊断、支持和以后核对。Desktop、TUI 和工作面板不再展示「待核实」分区、列表、徽章或注意提示。证据、停稳回执、占用、`user_panel` 授权和主 Bot 工具边界不变）
状态：Accepted（2026-11-07 20:03 Asia/Shanghai，用户阅读全文后明确回复「那就落实124」，授权按本文实施。2026-11-08 Asia/Shanghai 修订用户可见性，状态仍为已接受）。Peer-Agent PR 297 仍未合并。接受和那次手测都不等于版本已发布，也不等于现场记录已经离开「正在停止」。
级别：A（停止回执、跟进投影、资源占用、授权与审计契约），B（主 Bot 工具、任务列表、协作 Agent 与聊天卡片接线），C（同源文案）

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[架构治理](../architecture/20-architecture-governance.md)、[人机交互契约](../specifications/peer-human-agent-interaction-contract.md)、ADR [91](91-project-bot-autonomous-coordination.md)、[92](92-scoped-permission-inheritance.md)、[101](101-bot-owned-access-policy.md)、[102](102-unified-task-lifecycle-projection.md)、[110](110-follow-up-responsibility-and-current-list.md)、[116](116-session-control-and-resource-settlement.md)、[119](119-user-stop-cognition-admission-and-settlement.md)、[120](120-runtime-facts-disposition-and-resource-wait.md)。

本文已于 2026-11-07 20:03（Asia/Shanghai）接受，并授权按本文实施。2026-11-08（Asia/Shanghai）的可见性修订替代此前把索引放进用户界面的写法；修订后的规则见第 4.3 节、第 6.2 节和第 8.3 节。下文“必须”是这次实施的约束。ADR 110、116、120 的已接受条款继续有效，只有第 13 节点名的展示规则按本文收窄。ADR 119 仍是未接受提案；接受本文不接受它的其余条款。本知识变更不修改 Peer-Agent，不合并、不发版、不读写真实用户计划、账本或会话。

## 1. 决策摘要

遗留取消要能被解释和处理。处理的含义是：主 Bot 用正式工具读到结构化证据，宿主向用户展示未知项和可选动作，用户点名授权后，跟进离开“正在停止”和当前执行列表，这些条目从用户的跟进和任务列表消失。执行是否已结束、外部调用结果、资源能否交给下一次执行，仍分别保留。

1. 取消意图、执行活性、结果确定性、资源占用责任、展示跟进是五件不同的事。停掉新的执行准入，只说明旧调用不再被这条绑定新派发。停止跟进只说明当前列表不再把它当作进行中的工作，并把处置写入内部索引。两件事都不产生“已取消”或“结果成功”。
2. 已有停稳回执、活动执行和资源账本继续是真源。本文新增的是义务分类、授权退役跟进，以及一条内部审计索引。处置是 `indexed`，跟进原因是 `obligation_indexed`。索引留给诊断、支持和以后核对。Desktop、TUI 和工作面板不向用户展示它。新字段在第 3 节标明；在对应实现写入之前，不把这些字段补进旧记录。
3. 能证明本机、同一次启动、登记进程已死，并且没有未结调用和未结束句柄时，沿现有 Session Control 收尾。证明不了的记录保持原计划状态和原占用。用户可以授权停止跟进；宿主把该条写入内部索引，并从用户的跟进和任务列表去掉。
4. 只读核实、请求授权、执行授权后的退役分成三件工具。主 Bot 可以调用，不能自己签发授权，也不能用 `force` 一类参数合并这些动作。完全访问档位不代替这次确认。授权只来自 `user_panel`。
5. 资源释放仍只发生在现有停稳回执结清账本的路径上。本文不新增释放工具，不接受“用户愿承担风险所以放开目录”。退役不写 `stopReceipt`。
6. [Peer-Agent PR 297](https://github.com/ly-ccx/Peer-Agent/pull/297) 仍是未合并的实现。2026-11-08 用户确认已手测通过当时的头，随后要求去掉面向用户的「待核实」。该 PR 不能写成已发布，也不能写成用户机器上的原进程已被证明死亡。阅读范围见第 9.2 节。

## 2. 问题、目标与非目标

### 2.1 现场与归因边界

用户在 Peer Desktop rc38 中取消三条任务后，界面长期停留在“正在停止”。聊天里的主 Bot 反复请求取消，工具返回 `execution_stop_unconfirmed`，随后仍用文字声称已经停下，并建议用户重启。

这些聊天句子是已经发生的表达，不是执行证据，也不是停稳回执。本轮没有打开用户的计划文件、协调日志或设备资源账本，因此本文不记录那三条的 sessionId、路径或正文，也不判断那三个进程现在是否还在。

代码核对的固定基线是 Peer-Agent 开发线 `cb7e14c965c9102d49252e5a362457770ea51d14`（`PeerAgent/dev/0.1.0`，2026-11-07）。知识库编号核对的是 `origin/main` `3402e83`。PR 297 的头是 `a8d8d8ba80fc550caed0e06fd969435e80f8a1df`，基线也是上述 `cb7e14c`，状态为打开且未合并。

### 2.2 目标

- 主 Bot 能对遗留停止记录做一次有范围的只读核实，并把未知项原样告诉用户。
- 用户能对点名的计划、执行和控制操作授权“退役跟进”。授权之后，该条从任务列表、跟进列表和协作 Agent 的当前列表消失。执行结果仍未确认，资源不释放。内部索引保留，供诊断、支持和以后核对。
- 同一条记录上的未知调用、未结束句柄和目录占用继续阻止重放和冲突写入。
- 新产生的取消从登记时就带上可核对的本机进程身份。身份齐全且义务已空时，现有关闸可以自己收尾。身份不齐全的旧记录不补写身份。
- 重启、再次取消和重复退役都幂等，并且能在崩溃后从日志恢复。

### 2.3 非目标

- 不把这三条或任何缺少证据的记录自动收成 `cancelled`。
- 不证明、不假设 rc38 那三个原进程已经死亡。
- 不新增第二套任务系统、全局锁管理、文件级锁或跨设备执行同步。
- 不向用户开放「待核实」分区、列表、徽章或注意提示，也不为此新增设置页或另一套任务心智模型。
- 不新增 Shell、文件写入、MCP 或“替用户查进程”的维护通道。核实只读本机已经登记的控制、租约、执行所有权和资源账本。
- 不回滚外部副作用，不删除历史会话、预算、Evidence、未知调用数组或工具结果。
- 不改模型的目标理解。自然语言“停止”仍走现有取消入口；它不会被解释成退役跟进或释放资源。
- 不实施 ADR 119 的整套认知代次。本文只避免新工具把未确认停止重新交给模型循环。
- 本知识变更不修改 Peer-Agent。运行时由代码仓按本文实施；交付前，已安装版本仍是旧行为。

## 3. 术语、既有事实与本文对象

### 3.1 五个概念

| 概念 | 回答的问题 | 现有真源 | 本文是否新造真源 |
| --- | --- | --- | --- |
| 取消意图 | 这条执行绑定是否已禁止新的派发 | `delegationOrigin.cancellation` 与 `SessionControlOperation` | 否 |
| 执行活性 | 本进程现在有没有活体执行 | `executionOwnership`：`live` / `ended` / `unknown` | 否。另给登记进程补一个本机身份元组，只用于新记录 |
| 结果确定性 | 已登记的外部调用和句柄有没有结清 | `uncertainDispatches`、`pendingTools`、资源句柄、`StopBarrierReceipt.unknownCalls` | 否。授权只追加“用户已知悉这些未知项”的审计，不改原数组 |
| 资源占用责任 | 哪个目录或 Git 范围仍被保护 | 设备资源账本的 claim / hold | 否。退役跟进不改 claim 状态 |
| 展示跟进 | 当前任务列表和协作 Agent 是否还把它算作进行中 | `decideFollowUp` | 是。新增处置 `indexed` 与原因 `obligation_indexed`，并新增内部审计索引。日常界面不展示这条索引 |

停止接收新执行，是取消意图已经写入。旧调用是否结束，要看活性和结果确定性。跟进退役，只改变展示跟进。三项可以同时为真：新派发已关闭、旧结果仍未知、当前列表已经不再展示。

### 3.2 已有字段和状态

开发线 `cb7e14c` 上已经存在，本文沿用：

| 事实 | 位置 | 含义 |
| --- | --- | --- |
| 取消登记 | [`session-cancellation.mjs` L51–L63](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-cancellation.mjs#L51-L63) | 写入 `phase: 'stopping'`，把计划置为 `paused`，并先关掉 runner 泵 |
| 停稳回执 | 同文件 [L65–L108](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-cancellation.mjs#L65-L108)；[`session-control.mjs` L111–L143](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-control.mjs#L111-L143) | 只有 `drain` 返回的 `stopReceipt` 才能进入 `settle`。未知调用且没有用户撤回时停在 `reconciling`。`applied` 且回执通过后置条件后，计划才是 `cancelled`，跟进离开当前列表 |
| 无回执即失败 | [`session-cancellation.mjs` L111–L113](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-cancellation.mjs#L111-L113) | `drain` 抛出的 `execution_stop_unconfirmed` 原样返回，`cancellationPending` 仍为真 |
| 关闸拒绝 | [`session-control.mjs` L81–L96](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-control.mjs#L81-L96) | 见 3.3 的布尔结构。拒绝会把 `nextAction` 写成该错误，阶段进入 `reconciling` |
| 重复巡检 | [`session-cancellation.mjs` L127–L132](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-cancellation.mjs#L127-L132) | `recover` 对仍不是“未知集合已稳定的 `awaiting_outcome`”的取消再次调用 `request` |
| 投影仍是正在停止 | [`session-control.ts` L80–L83](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/protocol/src/session-control.ts#L80-L83)；[`task-overview.ts` L772–L784](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/protocol/src/task-overview.ts#L772-L784) | `reconciling` 只有带着非空 `unknownCalls` 的回执才投影成 `awaiting_outcome`（文案“执行结果待核实”）。没有回执时投影成 `stopping`（文案“正在停止”） |
| 当前列表 | [`task-overview.ts` L534–L550](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/protocol/src/task-overview.ts#L534-L550) | 停止状态若没有 `cancellationPhase === 'completed'` 且非活体，`followUp` 为 `bot` / `stop_unconfirmed` / 在当前列表 |
| 执行所有权 | [`session-facts.mjs` L41–L55](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-facts.mjs#L41-L55) | 活体只来自本进程 token 或句柄。runner 落盘终态才是 `ended`。重启后的 `running` 是 `unknown`。注释写明空 token 不是已结束 |
| 宿主纪元 | [`runtime-host.mjs` L137–L141](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/runtime-host.mjs#L137-L141)；[`work-coordination-store.mjs` L34 与 L114](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/work-coordination-store.mjs#L34) | `writerEpoch()` 返回租约的 `hostId:acquiredAt`。只有租约函数缺失时，控制记录才退回 `legacy-host:${process.pid}` |
| 租约文件 | [`host-lease.mjs` L180–L189](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/host-lease.mjs#L180-L189)、[L249–L253](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/host-lease.mjs#L249-L253)、[L295–L301](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/host-lease.mjs#L295-L301) | 当前租约含 `hostId`、`pid`、`acquiredAt`。接手或释放会换掉或删除 `host.lease`，不保留旧持有者档案 |
| 资源结清 | [`execution-resources.mjs` L199–L220](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/execution-resources.mjs#L199-L220) | 未结束句柄使结清抛出 `execution_stop_unconfirmed`。注释写明交接认停稳回执，不认过期宿主的 PID |
| 另一套宿主行 | [`resource-edit-storage.mjs` L32–L35 与 L96–L106](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/resource-edit-storage.mjs#L32-L106) | 资源编辑表 `host_owner` 只有当前一行。这里的 ESRCH 只涉及资源编辑写入者，不证明任务执行已结束 |
| 现有工具 | [`tool-specs.mjs` L128–L157](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/tool-specs.mjs#L128-L157) | 模型能 `control_work`、`cancel_session`、`list_sessions`、`get_session`。没有只读义务核实，也没有在授权后退役跟进的工具 |
| 控制操作形状 | [`session-control.ts` L34–L54](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/protocol/src/session-control.ts#L34-L54) | 有 `hostEpoch`，没有独立的 `hostPid`、启动标识或进程起始时刻 |
| 已结清必须有回执 | [`session-control-kernel.mjs` L55](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-control-kernel.mjs#L55) | `settled` + `applied` 且种类不是 `resume` 时，缺少 `stopReceipt` 会被拒绝 |
| 格式门槛 | [`session-control-kernel.mjs` L19](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-control-kernel.mjs#L19)；[`coordination-storage-v2.mjs` L167](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/coordination-storage-v2.mjs#L167) | 控制事件的 `minimumExecutorVersion` 只接受 7 或 9。存储已认识的读者门槛最高写到 9 |

ADR 110 已接受的规则是：未确认停止和未知事实留在当前列表，责任在 Bot。ADR 110 §7 允许在受管执行已经停稳后撤回委托，未知历史保留，但那条路以停稳回执为前提。ADR 116 已接受：终态字符串、空 token、租约丢失和 PID 都不能单独释放资源。ADR 120 已接受：停止确认来自 Session Control，模型不负责把停止说成已经确认。

### 3.3 开发线上的拒绝结构

`drain` 在匹配到旧回执之前，用下面这个条件拒绝继续关闸（`&&` 先于 `||`）：

```text
((hostEpoch 存在且与当前 writerEpoch 不同且没有 stopReceipt) || unproven)
  && 所有权不是 ended
  && 不是已核对的旧取消完成
  && 不是已核对的旧接管空闲
  && 不是保留的恢复栅栏
→ execution_stop_unconfirmed
```

`unproven` 在 [`session-control.mjs` L59–L60](https://github.com/ly-ccx/Peer-Agent/blob/cb7e14c965c9102d49252e5a362457770ea51d14/packages/runtime-node/src/project-agent/session-control.mjs#L59-L60) 为真的典型组合是：曾经可能派发过，当前所有权是 `unknown`，没有旧的完成证明，也没有已绑定的回执。rc38 这种只留下 `hostId:acquiredAt` 的记录，在新租约下两条子句都能成立。第一次拒绝会写下 `nextAction`。只要事实摘要不变，下次 `drain` 在更早的分支直接重抛同一个 `nextAction`。取消镜像却仍是 `stopping`，投影因此继续显示“正在停止”，`recover` 会再进一次。

这条循环是开发线的当前行为。它没有用户可操作的“核实后退役”入口。

### 3.4 本文确定、尚未写入代码的对象

以下名称已经由本文确定。Peer-Agent `cb7e14c` 里还没有这些工具和字段。未合并的 PR 297 后来有一份草稿，见第 9.2 节；已发布运行时在该 PR 合并之前仍不能调用这些名字。2026-11-08 的可见性修订还没有进入那份草稿：

| 名称 | 种类 |
| --- | --- |
| `inspect_execution_obligation` | 只读工具，能力 `local.delegation.inspect_execution_obligation` |
| `request_obligation_authorization` | 展示授权卡，不改义务、计划、占用或未知数组。能力 `local.delegation.request_obligation_authorization` |
| `resolve_execution_obligation` | 有副作用工具，只执行已经确认的退役或知悉。能力 `local.delegation.resolve_execution_obligation` |
| `ExecutionObligationDisposition` | 协调日志事件，不是新的任务 |
| `followUp.reason = obligation_indexed` | 投影原因 |
| `recorder` | 新取消记录上的本机进程元组：`bootId`、`pid`、`pidStart`、`hostId`、`acquiredAt` |
| 能力 `execution_obligation_v1` | 首次写入处置或授权事件前，把读者、写者和执行者门槛升到 11 |

门槛 10 留给尚未接受的 ADR 119 所预留的 `user_stop_cognition_admission_v1`。本文不占用 10。若实施时主干已经使用 11 或更高，先改本节再写第一笔新事件，实际取值是当时已用门槛的下一个整数。

## 4. 分类、状态与转换

分类由宿主在只读核实和每次对账时重算。同一事实重算得到同一类。分类结果可以写入审计，但不是第二个生命周期。

### 4.1 分类

| 类 | 判定 | 自动行为 | 用户可授权的动作 |
| --- | --- | --- | --- |
| `barrier_in_progress` | 控制阶段是 `recorded` 或 `draining`，还没有稳定的拒绝摘要 | 保持“正在停止”。继续现有关闸，直到回执或稳定拒绝 | 无。退役会被拒绝 |
| `managed_stop_settled` | 已有匹配当前执行身份的 `stopReceipt`，控制 `settled/applied`，所有权不是 `live` | 沿 ADR 110：无未知则离开当前列表；有用户撤回则委托退出并保留未知历史 | 无额外动作。重复取消返回现有回执 |
| `recorder_dead_clear` | 第 7 节的本机死亡证明成立，所有权不是 `live`，未知调用为空，未结束句柄为空 | 宿主对账走现有 `drain` / `settle`，写成真实回执后再释放对应 claim。模型不调用结算 | 无。结算不是授权工具的动作 |
| `recorder_dead_with_unknown` | 死亡证明成立，但仍有未知调用或未结束句柄 | 写成带这些未知身份的停稳回执，claim 进入 `reconciling`，不释放，不重放，计划不标成功 | 可退役跟进。释放仍不开放 |
| `legacy_recorder_unproven` | 没有完整 `recorder` 元组。包括 rc38 的 `hostId:acquiredAt`、没有 PID，以及不能同时核对启动标识和进程起始时刻的旧记录 | 停止无新事实的重复 `recover`。投影改为“执行结果待核实”。不补 PID，不写回执，不改 `plan.status`，claim 保持 | 先知悉“进程未证明，且没有登记不等于没有外部效果”，再退役跟进。不可据此自动收成已取消 |
| `remote_unobserved` | 401、超时、本进程没有 token、租约到期或重启，且没有第 7 节的死亡证明 | 与 `legacy_recorder_unproven` 相同，并在证据里写明这些信号各自缺什么 | 可退役跟进。这些信号单独不构成死亡 |
| `external_effect_unknown` | 存在 `uncertainDispatches`、未结束句柄，或旧记录根本没有派发登记 | 占用保持。缺失登记写成 `dispatch_registration_absent`，意思是“没有登记”而不是“没有副作用” | 退役前必须知悉列出的身份；没有身份可列时，也必须知悉“登记缺失” |
| `recorder_alive` | 本机元组核对为同一进程仍在 | 继续关闸。从索引里把已退役条目拉回当前列表 | 拒绝退役和知悉，直到活性变化 |
| `cross_host_unproven` | `hostEpoch` 与当前 `writerEpoch` 不同，且死亡证明不成立 | 归入遗留未证明。不把别的机器或下一次租约的 PID 拿来比较 | 与遗留未证明相同 |

一条记录可以同时是 `legacy_recorder_unproven` 和 `external_effect_unknown`。响应里用 `classes` 数组，不用一个总状态把它们压扁。

「执行结果待核实」只作为确认前、条目仍在当前列表时的既有状态文案。确认之后不再用这个名字给用户一个可打开的分区，规则见第 8.3 节。

`draining` 的 claim 表示关闸仍在进行，可能还有写入。`reconciling` 的 claim 表示已有未解除的风险。稳定拒绝后，本文允许投影离开“正在停止”，但 claim 仍停在原来的 `draining` 或 `reconciling`，直到真实回执把它结清或转成 ADR 116 的 hold。退役跟进不把 `draining` 改成 `released`。

### 4.2 转换

```text
取消登记
  → barrier_in_progress（正在停止，claim=draining）
      → 本机死亡证明且义务已空 → 现有关闸 → managed_stop_settled（已取消，claim 按回执释放）
      → 本机死亡证明且仍有未知 → recorder_dead_with_unknown（执行结果待核实，claim=reconciling）
      → 稳定拒绝且不能证明死亡 → legacy_recorder_unproven / remote_unobserved（执行结果待核实，claim 不变）
            → 用户授权退役跟进 → 内部索引记为 obligation_indexed，并从用户的跟进和任务列表消失（计划状态不变，claim 不变）
            → 之后观察到 recorder_alive 或 executionOwnership=live → 处置改为 suspended，回到当前列表
      → 已索引之后，若后来的证据使现有关闸得以写回执 → 回执优先，投影改为 stop_confirmed 或 user_withdrawn，索引条标记 superseded
```

活体优先于索引。人类门和真实人工请求优先于索引。已签收结果保持原事实，不进入退役。

### 4.3 索引与资源的关系

离开当前列表的唯一新原因是 `obligation_indexed`。它表示跟进已退役。它不表示 `stop_confirmed`、`user_withdrawn`、`settled` 或执行成功。

资源准入继续只读 claim / hold。`followUp.inCurrentList === false` 不是释放条件。新的同目录执行仍得到原来的 blocker。blocker 可以带上 `obligationId`，供准入和诊断引用。blocker 不把义务伪装成一个正在运行的会话标题，也不把用户带进「待核实」列表。

`indexed` 是内部审计索引。它不可过期，也不按时间删掉。删掉索引、只改界面，会使后来的执行把仍需保护的目录看成空闲，因此不采用。诊断、支持和以后的核对读取这条索引。若另有诊断或开发表面要读它，那个表面是内部表面，供诊断、支持和以后核对使用。本文不新增设置页，也不规定那张表面的屏幕。

已索引的条目不再占用“当前任务”和“当前协作 Agent”的名额，避免未知项永远挤在进行中列表里。日常界面不给这条索引单独的计数、徽章或注意提示。

## 5. 工具合同

三件工具都走现有能力链：Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant / 本次授权记录 → Evidence 或审计。它们不读取工作区文件，不启进程，不发网络请求。

调用者身份由宿主注入，不由模型参数提供：`workspaceId`、`parentConversationId`、主 Bot 的 `agentConversationId`、表面 `desktop` 或 `tui`、本次 `toolCallId`。模型若多传这些字段，宿主忽略参数里的值并用注入值覆盖；两者冲突则拒绝 `authorization_scope_mismatch`。Worker、Verifier、Explorer 的投影不包含这三件工具。`peer exec` 和无头脚本不能调用 `resolve`，也不能用 `--yes` 跳过授权卡。

`full_local`、Ask、会话级许可和旧的 PermissionGrant 都不确认退役。授权只来自第 6 节的授权记录。

### 5.1 只读核实

工具名：`inspect_execution_obligation`。

参数：

| 字段 | 约束 |
| --- | --- |
| `sessionIds` | 可选，1 至 20 个。与 `obligationIds` 至少有一个 |
| `obligationIds` | 可选，1 至 20 个 |
| `detail` | `summary` 或 `evidence`。默认 `summary` |

宿主把范围限制在当前主 Bot 的 workspace 与父会话。越界 id 返回该条 `out_of_scope`，不把其他 Bot 的记录混进成功列表。空范围返回 `obligation_scope_empty`。

返回每条：

| 字段 | 内容 |
| --- | --- |
| `sessionId` / `planId` / `operationId` / `obligationId` | 稳定身份。`obligationId` 由 workspace、session、plan、operation 四个字符串的规范连接做 SHA-256，前缀 `obl_`，即使尚未写入处置也先算出 |
| `classes` | 第 4 节的类 |
| `cancelIntent` | `open` 或 `settled`，以及控制 `phase` / `revision` |
| `liveness` | `live` / `ended` / `unknown` / `recorder_alive` / `recorder_dead` / `recorder_unproven` |
| `outcome` | `clear`、`unknown_calls`、`open_handles`、`registration_absent` 的组合，只含调用 id 和句柄 id |
| `resource` | `claimId`、`revision`、`state`、`resourceKind`。模型载荷不含完整路径；用户卡片使用资源账本已经展示给用户的标签 |
| `followUp` | 当前投影 |
| `gaps` | 机器可读缺口码 |
| `evidenceRevision` | 下面规范投影的 SHA-256 |
| `observedAt` | 宿主时钟 |
| `livenessFreshness` | 固定为 `advisory`。核实时刻的活性不能被稍后的工具调用拿来结算 |
| `allowedActions` | 该条现在允许放进授权卡的动作 |
| `refusalPreview` | 若现在调用 resolve 会得到的拒绝码；空数组表示动作本身可用，仍要授权 |

`evidenceRevision` 覆盖：控制 `operationId` 与 `revision`、`nextAction`、有无回执、claim 的 id/revision/state、未知调用 id 的排序列表、句柄 id 与状态、`executionOwnership`、`hostEpoch` 是否等于当前 `writerEpoch`、`recorder` 是否完整、死亡证明是否成立。不覆盖标题、聊天正文和工具参数。

核实不写日志、不改计划、不改账本、不弹授权卡。重复调用没有副作用。它免去第二次确认，但仍受租约和父会话范围约束。

### 5.2 请求授权

工具名：`request_obligation_authorization`。

参数：`evidenceRevision`，以及 1 至 20 条 `{ sessionId, operationId, actions[] }`。`actions` 只允许 `retire_follow_up`、`acknowledge_unknown` 和 `restore_follow_up`。传入 `release_resource`、`force` 或其他字符串时，整次请求拒绝 `action_unavailable`，不展示卡片。

宿主在展示前重新读取。`evidenceRevision` 不一致则拒绝 `evidence_stale`，不使用模型随口编写的风险说明。对每一条重算 `allowedActions`。仍在关闸、登记进程仍存活、或所有权为 `live` 的条目不进入卡片，并在返回里带 `barrier_in_progress`、`recorder_alive` 或 `execution_still_running`。其余条目照常出示。全部条目都不可授权时，不展示卡片。`restore_follow_up` 只对当前处置已经是 `indexed` 的条目可用；否则该条返回 `not_indexed`。

卡片由宿主渲染。正文来自重新读取的证据：每条的类、缺口、占用是否继续、会不会被标成已取消。退役跟进的后果用第 6.2 节的句子。正文不得把「待核实」写成确认后的去处。模型在聊天里的解释可以同时存在，宿主卡片不引用那段文字当事实。

这个工具不创建已确认授权，不修改义务。它只创建 `pending` 授权请求。用户关闭卡片或按 Escape，请求变为 `revoked`。

### 5.3 执行已确认的处置

工具名：`resolve_execution_obligation`。它只执行授权里已经确认的 `acknowledge_unknown`、`retire_follow_up` 或 `restore_follow_up`。

参数：

| 字段 | 约束 |
| --- | --- |
| `grantId` | 宿主签发的授权 id。模型只能回填授权卡交给它的那个 id |
| `idempotencyKey` | 调用方提供的 16 至 128 字节可见字符串。宿主另算规范键，见下 |
| `items` | 1 至 20 条，必须与授权里的条目和动作一致 |

规范幂等键是 SHA-256，输入为按 `sessionId`、`operationId`、`action` 排序后的规范 JSON：`grantId`、条目、动作、授权当时绑定的 `evidenceRevision`。调用方的 `idempotencyKey` 不匹配时拒绝 `authorization_mismatch`，避免同一授权被改写成另一次动作。

宿主在项目 writer 内逐条重读。一条一个事务，所以批量可以部分成功。单条事务同时写入：处置事件、该条授权消耗、审计。三者缺一则该条回滚。先写处置再从列表投影里消失；投影只读处置，因此不会出现“列表已经没有、日志没有责任”的窗口。

资源账本不在这个事务里修改。若崩溃发生在事务提交之后、界面事件之前，下次列表查询以日志为准，事件按稳定 id 补送。

每条结果是 `applied`、`replayed` 或 `rejected`。已成功的条目保持成功。失败条目带拒绝码，授权的那一行不消耗，用户可以只为失败条目重新核实和重新确认。

同一规范键的重复调用返回第一次的逐条结果，不追加第二笔处置，不再次暂停计划，不调用 runner。

### 5.4 拒绝码

| 码 | 含义 | 是否改状态 |
| --- | --- | --- |
| `out_of_scope` | workspace 或父会话不匹配 | 否 |
| `lease_unavailable` | 当前宿主没有该项目租约 | 否 |
| `session_not_found` | 范围内没有该 session | 否 |
| `obligation_scope_empty` | 没有给任何 id | 否 |
| `too_many_items` | 超过 20 | 否 |
| `evidence_stale` | 核实版本与现在的证据不同 | 否 |
| `revision_conflict` | 控制或 claim 的 revision 与授权绑定的不同 | 否 |
| `action_unavailable` | 动作不在允许集合，含任何释放或 force | 否 |
| `barrier_in_progress` | 关闸尚未稳定拒绝 | 否 |
| `recorder_alive` / `execution_still_running` | 仍可能有本机执行 | 若先前已索引，追加 `suspended` 并回到当前列表 |
| `unknown_not_acknowledged` | 有未知调用、句柄或登记缺失，授权却没有 `acknowledge_unknown` | 否 |
| `authorization_required` | resolve 没有对应的已确认授权 | 否 |
| `grant_pending` / `grant_expired` / `grant_revoked` / `grant_consumed` | 授权未生效或已不能再用 | 否 |
| `grant_not_found` | id 不存在 | 否 |
| `authorization_mismatch` | 条目、动作、版本或幂等键与授权不一致 | 否 |
| `authorization_scope_mismatch` | 模型试图指定另一个 workspace、父会话或 Bot | 否 |
| `already_settled` | 已有生效回执 | 否，返回现有投影 |
| `not_indexed` | 恢复跟进时当前处置不是 `indexed` | 否 |
| `not_main_bot` | 子执行角色调用 | 否 |

`release_resource` 没有成功码。出现这个动作就走 `action_unavailable`。

### 5.5 防过期读

核实返回的活性和 `evidenceRevision` 只说明那一次读取。`resolve` 在写事务里重算死亡证明、所有权、未知集合和 revision。事务内的结论与授权绑定期不一致，则该条 `revision_conflict` 或 `evidence_stale`。

死亡证明的 `kill(pid, 0)` 或起始时刻比较只发生在这个事务或宿主对账的临界区内，不采用核实响应里的旧结论。本提案不要求跨进程的分布式事务。协调日志是处置真源；资源库保持 ADR 116 的顺序：先有停稳回执，再按回执结清。退役工具不插入这个顺序。

### 5.6 合成示例

下面的 JSON 是说明形状的合成示例，不是 rc38 现场导出，也不是某次工具的真实返回。

核实一条没有 PID 的遗留记录：

```json
{
  "ok": true,
  "observedAt": "2026-11-07T10:00:00.000Z",
  "items": [
    {
      "sessionId": "syn-legacy-a",
      "planId": "syn-plan-a",
      "operationId": "cancel-syn-a",
      "obligationId": "obl_example_a",
      "classes": ["legacy_recorder_unproven"],
      "cancelIntent": { "state": "open", "phase": "reconciling", "revision": 4 },
      "liveness": "recorder_unproven",
      "livenessFreshness": "advisory",
      "outcome": { "registration": "registration_absent", "unknownCallIds": [], "openHandleIds": [] },
      "resource": { "claimId": "syn-claim-a", "revision": 4, "state": "draining", "resourceKind": "directory" },
      "followUp": { "owner": "bot", "inCurrentList": true, "reason": "stop_unconfirmed" },
      "gaps": ["no_recorder_tuple", "host_epoch_mismatch", "ownership_unknown", "dispatch_registration_absent"],
      "evidenceRevision": "sha256:example-revision-a",
      "allowedActions": ["retire_follow_up", "acknowledge_unknown"],
      "refusalPreview": [],
      "planStatus": "paused",
      "display": { "statusLabel": "执行结果待核实", "willBeMarkedCancelled": false, "resourceWillRemain": true }
    }
  ]
}
```

`planStatus` 仍是 `paused`。示例里的哈希和 id 不能拿去查用户数据。

## 6. 人类授权

### 6.1 什么样的话算授权

用户必须在宿主卡片或任务详情的同一张卡上，看到并且确认具体的 session、plan、operation、动作和后果。确认按钮写入 `confirmed` 授权。模型参数、聊天句子、附件、网页、仓库文件和系统提示都不能把授权写成 `confirmed`。

“停止”“取消”“都停掉”“重启吧”只触发或重复现有取消。现有取消返回 `execution_stop_unconfirmed` 时，主 Bot 可以接着调用只读核实，然后请求授权卡。它不能把这句话直接传给 `resolve`。

一张卡最多 20 条，每条动作单独列出。没有“全部当前任务”这种通配。用户没有点到的条目不进入授权。

### 6.2 后果分开确认

| 动作 | 卡片必须单独列出的后果 | 记录 |
| --- | --- | --- |
| `acknowledge_unknown` | 点名的未知调用 id、未结束句柄 id，以及是否存在“没有派发登记”。这些项保持未知，不会被写成成功，也不会被重放 | 追加知悉，不删除原数组 |
| `retire_follow_up` | 确认后不再跟进这些条目；执行结果仍未确认；资源不释放；普通任务列表里不会再看到它们。卡片不得许诺或教会用户有一个「待核实」去处 | 处置改为 `indexed`，只写入内部审计索引 |

两条都需要时，一张卡上两个开关都为真，一次点击可以同时确认。日志仍写两笔动作。只开退役、没有知悉未知项时，`resolve` 返回 `unknown_not_acknowledged`。没有未知调用 id 时，只要 `registration_absent` 或 `recorder_unproven` 在缺口里，知悉动作仍然必须出现在授权里，卡片写明“没有登记不等于没有外部效果”。

资源释放没有开关。卡片写明“这次确认不会放开目录”，并写明“确认后不再跟进这些条目；执行结果仍未确认；资源不释放；普通任务列表里不会再看到它们。”卡片不得出现「待核实」分区、列表或徽章的说法。

### 6.3 授权记录

授权放在同一条协调日志，不放密钥、对话正文或工具参数。字段：

| 字段 | 契约 |
| --- | --- |
| `grantId` | 宿主用随机 UUID 生成。模型猜中或从文件里抄一个不存在的 id，得到 `grant_not_found` |
| `status` | `pending` → `confirmed` → 按条目 `consumed`；或 `revoked` / `expired` |
| `items` | session、operation、动作、绑定期的 `evidenceRevision`、控制 revision、claim revision |
| `principal` | `workspaceId` + `parentConversationId`。不写操作系统用户名 |
| `audience` | 主 Bot 的 `agentConversationId`。面板直接确认时 audience 为空，actor 记 `user_panel` |
| `confirmedAt` / `expiresAt` | 点击时写入。有效期 15 分钟。选择 15 分钟是为了让用户看完三条记录，同时避免一张旧卡在下一次修订后仍能使用。模型不能续期 |
| `revokedAt` | 关闭、Escape、或点击时发现证据已变 |

点击时宿主再次比较 `evidenceRevision`。已经变化则不确认，卡片改显示新证据。过期、撤销、或 resolve 时 revision 不一致，都使该条授权失效。已提交的处置不被事后的关闭按钮撤销；要回到当前列表，必须另一次授权，动作是 `restore_follow_up`。恢复跟进只把处置改回 `current`，不重放工具，不释放资源。恢复不依赖用户打开一条「待核实」列表。用户明确点名某一条、要求放回跟进时，主 Bot 再请求同一张授权卡；该条原详情若仍打开，面板也可以确认。本文不新增索引入口或设置页。

已撤销或过期的授权在重启后仍是撤销或过期。日志重放不允许把 `revoked` 播放成 `confirmed`。

### 6.4 主 Bot 的边界

主 Bot 可以：核实、请求宿主出示卡片、在工具结果里拿到 `grantId` 之后调用 resolve、向用户解释卡片上的缺口。

主 Bot 不可以：把 `confirmed` 写进参数、引用自己刚生成的句子当授权、在完全访问下跳过卡片、用子 Agent 调用 resolve、把 `execution_stop_unconfirmed` 说成已停止、把确认后的去处说成「待核实」。实现时，回复合成要拒绝“已取消 / 已停止”这类控制声明，除非当前投影来自真实回执。这个检查只覆盖义务和取消结果，不把 ADR 119 的整套控制摘要提前算作已接受。

面板上的按钮走同一个 `resolve` 函数，actor 为 `user_panel`。没有正在进行的模型回合也可以退役。这样即使用户不信任聊天里的说法，仍有一条宿主入口。这条入口是仍在当前列表或原详情上的授权卡。确认之后不再有「待核实」页。

## 7. 安全证据

### 7.1 本机登记进程

新的取消在 `begin` 时写入 `recorder`，缺一不可：

| 字段 | 来源 | 缺少时 |
| --- | --- | --- |
| `bootId` | 当前操作系统启动标识。Linux 使用 boot_id；macOS 使用 boottime 的秒和微秒。取不到就记 `null` | 死亡证明不可用 |
| `pid` | 登记这次取消的宿主进程 | 死亡证明不可用 |
| `pidStart` | 该 PID 的进程起始时刻。Linux 用 starttime；macOS 用进程开始的秒和微秒 | 死亡证明不可用 |
| `hostId` / `acquiredAt` | 当时的租约 | 只作审计，单独不证明死亡 |

死亡证明只在本机数据根上判断。`bootId` 为空时不可用。复制到另一台机器的数据根不在这个保证内，边界与 ADR 116 相同。启动标识是随机值，不能排成“上一次”。

| 启动标识 | 进程判断 |
| --- | --- |
| 与当前启动相同 | 只在这个命名空间里看 PID。进程不存在，或 PID 还在但起始时刻与 `pidStart` 不同：登记进程已不在。起始时刻相同：`recorder_alive`。不读 PID 时，证明不成立 |
| 与当前启动不同 | 不再读取当前命名空间里的那个 PID。记录中的本地登记进程不视为 `recorder_alive`。这只说明该次启动的本地进程不在本次启动里 |

两种情况下，还要同时满足 `executionOwnership !== live`。未知调用和未结束句柄按第 4 节决定是直接结清，还是留下 `reconciling`。它们不因为登记进程已不在就消失。

只看到 ESRCH、只看到 PID 被复用、或只看到 `host.lease` 里曾经有过 PID，都不满足。不同机器的 PID 空间不能比较。`hostId:acquiredAt` 里的数字不是 PID，禁止用正则从 `hostEpoch` 里提取。

`legacy-host:${pid}` 是开发线在没有 `writerEpoch` 时的退路。它没有 `bootId` 和 `pidStart`。本文不把这条退路提升为死亡证明。

### 7.2 不能当成结束的信号

| 信号 | 可以说明什么 | 不能说明什么 |
| --- | --- | --- |
| HTTP 401 | 这次观察没有被授权 | 远端调用没有开始，或已经结束 |
| 超时 | 本机在期限内没有看到完成 | 远端工作已经停止 |
| 本进程 token 为空 | 这个进程现在没有活体登记 | 重启前的进程或远端调用已经结束 |
| 租约到期或文件被换掉 | 当前写者变了 | 旧进程已被杀死。接手会替换 `host.lease`，旧进程可能还在 |
| 用户重启应用 | 新进程要重新分类 | 旧的外部副作用已经消失 |
| 操作系统重启且没有 `bootId` | 什么都不能新推断 | 旧记录因此变成已取消 |
| 资源编辑表的 ESRCH | 资源编辑的当前写入行可以换主 | 任务执行或外部调用已经结束 |
| 聊天里说“已经停了” | 曾经生成过这句说明 | 停稳、释放或成功 |

未知的跨宿主纪元保持 `cross_host_unproven`。没有远端围栏 token 的外部调用保持 `remote_effect_unfenced`，可以知悉，不能释放。未结束句柄继续使现有 `settle` 失败。同一资源上的其他 claim 仍按现有顺序竞争。已经送出的外部动作不能由退役撤销。

证据里缺字段就保持缺字段。实现不得为了让死亡证明成立去补写 `bootId` 或 PID。

## 8. 执行流程、界面与三条合成记录

### 8.1 主路径

1. 用户说停止，或记录已经是历史取消。宿主只做现有取消或对账。
2. 结果若是稳定的 `execution_stop_unconfirmed`，投影为“执行结果待核实”，当前列表暂时保留。这一步不要求模型参与。
3. 主 Bot 调用只读核实，用缺口码解释，不补充未返回的事实。
4. 主 Bot 请求授权卡，或用户从详情自己打开同一张卡。无授权则到此为止。
5. 用户确认后，Bot 或面板调用 resolve。
6. 同一投影让该条离开任务列表、跟进列表和协作 Agent 的当前列表，并刷新聊天里的宿主卡片。宿主同时写入内部索引。日常界面不刷新出一个义务索引。
7. 主 Bot 若再生成文字，只能复述该次工具结果。与投影冲突的“已取消”不作为控制事实。文字也不把确认后的去处说成「待核实」。

无授权时，宿主不自动退役，不自动释放，不自动重放。

界面沿用现有 Frost 卡片、确认表和任务分组，不另做一套颜色或动画。Escape 撤销未确认授权。减少动效时卡片直接出现在终态。后台刷新不抢焦点、不清草稿、不把阅读位置拉走。实施时再更新交互矩阵和动效矩阵的源码状态；本文不把它们标成已实现。确认后的界面规则见第 8.3 节。本文不因这条索引给交互矩阵或动效矩阵增加「待核实」分区。

### 8.2 三条遗留记录的合成走查

场景设定：新宿主的租约是 `syn-host-now:2026-11-07T09:40:00.000Z`。三条都是 `paused`，取消镜像曾经长期停在 `stopping`，控制阶段在稳定拒绝后是 `reconciling`，`nextAction` 为 `execution_stop_unconfirmed`，没有 `stopReceipt`，没有 `recorder`，所有权是 `unknown`。这是 rc38 形状的合成，不是那三台真实记录。

| 记录 | 额外事实 | 核实分类 | 授权前列表 | 允许的授权 |
| --- | --- | --- | --- | --- |
| `syn-legacy-a` | 没有未知调用 id，没有句柄。claim `syn-claim-a` revision 4，`draining` | `legacy_recorder_unproven`，缺口含 `dispatch_registration_absent` | 当前任务和当前协作 Agent 都在，文案“执行结果待核实” | 知悉登记缺失 + 退役跟进 |
| `syn-legacy-b` | `uncertainDispatches` 含 `syn-call-b`。claim `syn-claim-b` revision 6，`reconciling` | 再加 `external_effect_unknown` | 同上 | 知悉 `syn-call-b` + 退役跟进 |
| `syn-legacy-c` | 句柄 `syn-handle-c` 状态不是 `ended`。claim `syn-claim-c` revision 4，`draining` | 再加未结束句柄 | 同上 | 知悉该句柄 + 退役跟进 |

主 Bot 一次核实三条，`evidenceRevision` 假设为 `sha256:example-batch`。它请求一张卡，三条都包含两个动作。宿主重读后出示卡片。用户确认。

resolve 的合成结果：

```json
{
  "ok": true,
  "grantId": "grant_example_batch",
  "items": [
    {
      "sessionId": "syn-legacy-a",
      "operationId": "cancel-syn-a",
      "result": "applied",
      "disposition": "indexed",
      "followUp": { "owner": "none", "inCurrentList": false, "reason": "obligation_indexed" },
      "planStatus": "paused",
      "stopReceipt": null,
      "claim": { "claimId": "syn-claim-a", "revision": 4, "state": "draining" },
      "replayedTools": []
    },
    {
      "sessionId": "syn-legacy-b",
      "operationId": "cancel-syn-b",
      "result": "applied",
      "disposition": "indexed",
      "followUp": { "owner": "none", "inCurrentList": false, "reason": "obligation_indexed" },
      "planStatus": "paused",
      "unknownCallIds": ["syn-call-b"],
      "claim": { "claimId": "syn-claim-b", "revision": 6, "state": "reconciling" },
      "replayedTools": []
    },
    {
      "sessionId": "syn-legacy-c",
      "operationId": "cancel-syn-c",
      "result": "rejected",
      "code": "revision_conflict",
      "followUp": { "owner": "bot", "inCurrentList": true, "reason": "stop_unconfirmed" },
      "planStatus": "paused",
      "claim": { "claimId": "syn-claim-c", "revision": 5, "state": "draining" }
    }
  ]
}
```

第三条在确认后、写入前被一次对账把 claim revision 从 4 改成 5，因此拒绝。前两条保持已退役。第三条留在当前列表。三条的 `plan.status` 都不是 `cancelled`。三条 claim 都没有 `released`。没有工具被重新执行。

用户只对第三条重新核实并确认。第二次 resolve 成功后，当前任务、跟进和当前协作 Agent 都不再有这三条。内部索引有三条，处置为 `indexed`，跟进原因为 `obligation_indexed`。Desktop、TUI 和工作面板没有「待核实」分区、列表、徽章或注意提示。同目录的下一条执行 `inspectResources` 仍不被允许。blocker 带上对应 `obligationId`，供准入和诊断引用，不打开用户列表。

再次 `cancel_session` 返回当前义务摘要和 `replayed: true`，不增加 abort，不把文案打回“正在停止”。宿主重启后重放日志，内部索引还在，占用还在，原工具仍不重放，日常列表里仍然没有这三条。

若其中一条在索引之后被观察到 `executionOwnership = live`，该条处置变为 `suspended`，回到当前列表，claim 不动。这个合成不把任何一条观察成死亡。

另外一条 `syn-draining` 若仍处于 `draining` 且没有稳定 `nextAction`，核实的 `allowedActions` 为空，请求授权返回 `barrier_in_progress`。它用来约束“关闸还在进行时不能退役”，不是第四条用户现场记录。

### 8.3 确认后的可见性

2026-11-08（Asia/Shanghai），用户在 Peer-Agent PR 297 的手测通过后说「要待核实我觉得就不应该对用户开放」，并明确回复「要」。自该时刻起，用户可见性按下面五条执行。状态仍是 Accepted。这一节替代此前把索引放进工作面板、并允许用户从「待核实」打开该条的写法。

- 用户在授权卡上以 `user_panel` 确认之后，宿主仍写入 `disposition=indexed`，跟进原因为 `obligation_indexed`。这条索引留下，供诊断、支持和以后核对。
- Desktop、TUI 和工作面板的日常界面不展示「待核实」分区、列表、徽章或注意提示。确认后的条目从用户的跟进和任务列表消失。用户不因此获得一套新的任务心智模型。
- 授权卡不许诺、不教会用户有一个「待核实」去处。卡片说明：确认后不再跟进这些条目；执行结果仍未确认；资源不释放；普通任务列表里不会再看到它们。
- 原会话若本来就在聊天记录里，仍是那次会话。确认不给它加上「跟进已转入待核实」一类标签，也不把它收进新的任务列表。计划不标成已取消。缺口、占用和不写 `stopReceipt` 都留在内部索引。
- 证据、不写 `stopReceipt`、不释放 claim、只接受 `user_panel` 确认、以及三件工具只给主 Bot，都保持第 5 至第 7 节。诊断或开发表面如果以后读取这条索引，它是内部表面。本文不新增设置页，也不规定那张表面的屏幕。

确认前，仍留在当前列表上的稳定拒绝继续使用既有文案「执行结果待核实」。这是当前列表里的状态。确认之后，该条离开列表，这个文案不再当作它的去处。

## 9. 旧记录、兼容与 PR 297

### 9.1 旧字段

原 `cancellation`、`executionControl`、`hostEpoch`、`unproven`、预算、未知数组、句柄和 Evidence 都保留。迁移不生成 `recorder`，不把空的 `hostPid` 填成 0 或当前进程号，不把 `stopping` 直接改成 `cancelled`。

自动可重复的部分，在取得宿主权之后每次对账都可以做：

- 按第 4 节重分类。
- 事实摘要未变且 `nextAction` 已是 `execution_stop_unconfirmed`、`execution_outcome_unknown` 或 `reconcile_execution_outcome` 时，不再次进入会重复 abort 的 `recover`。
- 这种稳定拒绝投影为“执行结果待核实”。控制阶段仍是 `reconciling` 时，现有 `awaiting_outcome` 镜像可以用来驱动这句已有文案。
- 真正的 `draining` 仍显示“正在停止”。

需要用户确认的部分只有知悉、退役跟进和恢复跟进。自动分类不代替确认。

重复取消、重复 resolve 和进程重启使用同一操作 id 与规范幂等键。已索引的记录不被再次取消打回 `stopping`。已有真实回执的记录保持回执，不被新分类改掉。

### 9.2 PR 297 的位置

[PR 297](https://github.com/ly-ccx/Peer-Agent/pull/297) 在 2026-11-07 仍是打开的未合并拉取请求，头提交 `a8d8d8ba80fc550caed0e06fd969435e80f8a1df`。三个提交的实际分工：

| 提交 | 已读到的提交说明 | 与本文的关系 |
| --- | --- | --- |
| [`c9e38573`](https://github.com/ly-ccx/Peer-Agent/commit/c9e3857391be343f6673b033ce8214cc137de4ba) | 给新的停止记录写 PID；该 PID 不存在、且没有活体、未知调用和未结束句柄时，才走现有关闸 | 方向是“新记录留下进程号”。只凭 ESRCH 和裸 PID 弱于第 7 节，不能原样接受。它不覆盖没有 PID 的 rc38 记录 |
| [`a8fc27fb`](https://github.com/ly-ccx/Peer-Agent/commit/a8fc27fb4bbcaca4b148138c780a68c969f19237) | 修正列表夹具的 runner 状态类型 | 不负责加入 PID。先前若把这个哈希说成 PID 实现，与提交内容不符 |
| [`a8d8d8ba`](https://github.com/ly-ccx/Peer-Agent/commit/a8d8d8ba80fc550caed0e06fd969435e80f8a1df) | 没有 PID 的遗留记录在稳定拒绝后投影成“执行结果待核实”，并停止无效重试；不发明 PID，不释放，不标已取消 | 与第 9.1 节的自动一半重合。该提交自己的测试仍要求 `followUp.inCurrentList === true`，claim 仍是 `draining`。离开当前列表不在这个提交里 |

以上是 2026-11-07 对头 `a8d8d8ba` 的阅读。当时的三个提交还没有义务工具，该头的测试仍要求留在当前列表。

2026-11-08 再读时，[PR 297](https://github.com/ly-ccx/Peer-Agent/pull/297) 仍打开且未合并，头为 `59e411577492d4e02cf4565d84dd53bc7c2702df`。PR 说明写着三件义务工具已经接上，工作面板另有「待核实」索引。用户确认对这个实现的手测已经通过，随后确认该索引不对用户开放。

继续这条未合并分支时，保留稳定拒绝后停止空转、第 7 节的死亡证明，以及不从 `hostEpoch` 提取 PID。义务工具可以留在这条分支上。面向用户的「待核实」分区、列表、徽章和注意提示要去掉；确认后仍写内部索引。接受本文不要求合并该 PR。手测通过不证明现场原进程已死，也不等于 2026-11-08 的可见性修订已经写进代码。

### 9.3 版本、降级与中间故障

只改投影、不写新事件的自动分类，可以留在现有格式 9。它不改变释放规则。

第一笔 `execution_obligation` 或授权事件写入前，门槛升到 11，并让控制 reducer 接受 11 而继续读 7 和 9。旧宿主打不开这个写门槛：拒绝执行和继续写入。只读路径若做不到，就显示“需要更新后才能继续处理这条跟进”。旧宿主不能把该条显示成已取消，不能因为它不认识新原因就把它从已有历史里丢掉，也不能自己画出「待核实」分区。

降级不删除处置、不降低门槛。回滚使用仍能读取这些事件的构建。已经 `revoked` 或 `expired` 的授权在回滚后的重放里保持失效，不能因为旧代码不认识状态就变成确认。

中间状态：

| 窗口 | 恢复 |
| --- | --- |
| 授权仍是 `pending`，进程退出 | 超过 15 分钟变为 `expired`。未确认不生效 |
| 用户已确认，resolve 未开始 | 未过期则可继续；过期则失效 |
| 单条事务未提交 | 该条保持原跟进和原占用 |
| 单条已提交，界面事件丢失 | 查询看到 `indexed`。若补送界面事件，只补这次确认的结果，不补「待核实」列表 |
| 批量中途崩溃 | 已提交的条目保留；未提交的在同一幂等键下重试，版本变了则 `revision_conflict` |
| 索引之后出现活体 | 追加 `suspended`，回到当前列表 |

## 10. 持久化与审计

不新增数据库和存储目录。处置、授权和审计是 coordination-v2 的新事件种类，资源账本仍是占用的唯一真源，GoalPlan 仍是计划和验收的真源。

审计每条含：actor（`main_bot` 或 `user_panel`、表面、`agentConversationId`、`toolCallId`）、principal（workspace、父会话、`grantId`）、动作与范围、前后控制 revision、前后 claim id/revision/state、证据投影的 SHA-256、缺口码、拒绝码、未知义务 id。不存对话正文、工具参数、密钥、操作系统用户名。路径不复制进审计；需要看目录时从原 claim 读，claim 本身仍按 ADR 116 保存资源身份。

`acknowledge_unknown` 只追加“这些 id 已被知悉”的引用。`uncertainDispatches` 和句柄状态保持原样，因此未来执行仍不能把它们当成成功或重新派发。

列表投影读取最新处置。处置不存在时行为与今天相同，失败时留在当前列表。不允许先改列表缓存、以后再补日志。

未决处置和未释放 claim 纳入现有保留集合，不被普通检查点清理或 TTL 删掉。

## 11. 备选方案

| 方案 | 取舍 |
| --- | --- |
| 继续重复 `cancel_session` | 开发线上已经如此。稳定事实下只反复得到 `execution_stop_unconfirmed`，界面仍可停在“正在停止” |
| 让用户重启应用 | 重启换掉租约和本进程 token，不产生回执，也不处理没有 PID 的旧记录 |
| 直接改数据库或把计划改成 `cancelled` | 会把未知执行写成已结束，随后的资源对账可能放掉仍需保护的目录 |
| 只把行从界面隐藏，同时删掉索引 | 若准入也看跟进投影，会造成误释放；若索引不存在，后来的执行会把仍需保护的目录看成空闲 |
| 向用户展示「待核实」分区 | 2026-11-07 的正文曾把索引放进工作面板。2026-11-08 手测之后，用户确认不对用户开放。索引留在内部；日常界面不展示分区、列表、徽章或注意提示 |
| 所有未知永远留在当前列表 | 这是 ADR 110 今天的失败关闭。它避免误释放，但使用户无法把已经解释过的遗留项从进行中列表移走。本文只在授权后移动展示，不取消失败关闭的默认 |
| 增加 `force` 或“我接受风险，放开目录” | 一个布尔值会同时绕过死亡证明、未知调用和授权。本文拒绝单独的释放工具 |
| 本文的核实、授权和退役 | 多了授权记录、门槛 11 和内部索引。旧记录可以被解释，并在授权后从进行中列表消失；占用和未知事实留在内部索引 |

残余风险：没有死亡证明的目录会继续被占住，直到将来真的有停稳回执。复制到另一台机器的数据根仍可能让启动标识失去意义，这与 ADR 116 已写明的设备边界相同。远端没有围栏的调用在知悉之后依然可能晚到；晚到结果只进原历史，不释放新 claim，不重开已退役的委托。

## 12. 分期与验收

### 12.1 分期

| 期 | 内容 | 完成标准 |
| --- | --- | --- |
| S0 | 本文 | 2026-11-07 20:03（Asia/Shanghai）接受并授权实施。2026-11-08 修订用户可见性。本知识变更不交付 S1–S4 的代码 |
| S1 | 自动分类、停止无新事实的重试、稳定拒绝显示“执行结果待核实” | 使用现有字段。当前列表和占用仍在。单独完成 S1 不算用户目标已完成 |
| S2 | 只读核实与授权卡，卡片不能确认成副作用 | 主 Bot 和面板都能看到同一份证据。卡片不把「待核实」写成去处 |
| S3 | 知悉、退役、恢复、内部索引、审计；确认后列表与协作 Agent 去掉该条 | 合成的三条无 PID 记录离开当前列表，内部索引仍在并挡住目录。Desktop、TUI 和工作面板没有「待核实」分区、列表、徽章或注意提示 |
| S4 | 新取消写入 `recorder`，只有第 7 节证明才自动走现有关闸 | 不回填旧记录。这是以后少产生同类遗留，不是这次三条记录的修复 |

S3 是“旧记录可处理”的最低完成线。S4 不能替代 S3。

建议落点，供实施时对照，不是本轮修改：

| 期 | 相对代码仓的位置 |
| --- | --- |
| S1 | `session-cancellation.mjs` 的 `recover`，`session-control.ts` 的相位投影，`task-overview.ts` 的现有文案 |
| S2–S3 | `tool-specs.mjs`、delegation provider、协调日志新事件。Desktop 与 TUI 只接授权卡，并把已退役条目从当前列表去掉；工作面板不增加「待核实」分区 |
| S4 | `session-control.mjs` 的 `begin` 与 `drain`。`execution-resources.mjs` 的释放条件保持“必须有回执” |

### 12.2 验收矩阵

自动化使用合成夹具，从 rc38 的形状构造：`hostEpoch` 为 `hostId:acquiredAt`，无 `recorder`，所有权 `unknown`，取消已登记，无停稳回执。夹具不读取用户目录。

| 编号 | 场景 | 必须证明 |
| --- | --- | --- |
| L01 | 三条合成记录：无调用、有未知调用、有未结束句柄 | 核实分类如第 8.2 节；没有一条被写成 `cancelled` 或补上 PID |
| L02 | 未知外部调用与句柄 | 知悉后原数组还在；退役后不重放；claim 不释放 |
| L03 | 没有派发登记 | 缺口为 `dispatch_registration_absent`；不把它说成未执行 |
| L04 | 本机死亡证明且义务已空 | 现有关闸写出回执并按回执结清；模型工具没有释放参数 |
| L05 | PID 仍是同一 `pidStart` | `recorder_alive`，拒绝退役 |
| L06 | PID 存在但 `pidStart` 不同，或 ESRCH，且元组完整、义务已空 | 只由宿主对账结算，不由模型直接改状态 |
| L07 | 另一台机器的 PID、或从 `hostEpoch` 提取数字 | 不构成死亡证明 |
| L08 | 401、超时、空 token、租约到期、应用重启 | 分类为未观察或未证明，claim 仍在 |
| L09 | 旧 `hostEpoch` 与当前租约不同 | `cross_host_unproven`，不补写当前 PID |
| L10 | `draining` 与已稳定 `reconciling` 混合 | 前者 `barrier_in_progress`；后者才可进入授权 |
| L11 | 活体与已索引并发 | 追加 `suspended`，当前列表恢复该条，占用不动 |
| L12 | 授权拒绝、过期、Escape 撤销 | resolve 失败且无处置 |
| L13 | 确认后 revision 变化 | 该条 `revision_conflict`，其他条可保留已成功结果 |
| L14 | 同一幂等键重复、再次取消、重启、对已索引条目 `restore_follow_up` 后再退役 | 重复调用不第二笔处置；恢复只把该条放回当前列表，不重放、不释放；重启后内部索引与占用按日志恢复 |
| L15 | 批量中途崩溃 | 已提交条保持；未提交条可安全重试 |
| L16 | 客户端拿着旧 `evidenceRevision` | 不确认、不写入 |
| L17 | 任务列表、跟进、协作 Agent、Desktop、TUI、工作面板、聊天宿主卡 | 确认后这些日常表面同时去掉已退役条；没有「待核实」分区、列表、徽章或注意提示；内部索引仍是 `indexed` / `obligation_indexed`；没有表面显示“已取消” |
| L18 | 完全访问、子 Agent、无头 `--yes`、聊天里粘贴 grantId | 都不能确认或扩大范围 |
| L19 | 旧宿主读取门槛 11 | 不执行新事件，不把记录显示成已取消 |
| L20 | 已撤销授权在回滚构建里重放 | 不能变成 `confirmed` 或重新退役 |

自动化能证明合成输入上的分类、拒绝、幂等、事务和投影。它不能证明用户机器上的原进程已经死亡，也不能代替候选上的界面核对。

按 2026-11-08 修订后的本文，手测要在含该修订的候选上，用导入的合成数据或同等形状的夹具完成：核实三条；卡片写明确认后不再跟进、执行结果仍未确认、资源不释放、普通任务列表里不会再看到它们，并且不出现「待核实」去处；确认后日常列表没有这些条目，Desktop、TUI 和工作面板也没有「待核实」分区、徽章或注意提示；同目录新执行仍被拒绝；重启后内部索引和占用还在。手测报告要写明没有编辑用户的原始记录。真实 rc38 数据是否呈现同一形状，只能由用户在自己的机器上对照。

2026-11-08 用户确认的 PR 297 手测，发生在这次可见性修订之前。那次通过不把工作面板上的「待核实」留成产品表面，也不把修订后的界面记成已经落地。

成功标准是：旧形状的记录能被说明，并且能在授权后离开进行中列表；未知和占用仍留在内部索引。用户不获得一个新的「待核实」去处。只让将来的新取消不再卡住，不算完成。

## 13. 与已有决定的边界

本文已接受，并据此收窄 ADR 110 的一处展示规则：在存在有效 `indexed` 处置、且没有活体和人工门时，`decideFollowUp` 返回 `obligation_indexed`，`owner` 为 `none`，从而离开当前列表。保护性事实仍先判断。`stop_confirmed` 与 `user_withdrawn` 的含义不变。未知事实和资源保护不因为离开列表而消失。没有有效 `indexed` 处置时，ADR 110 仍要求未确认停止留在当前列表。该收窄要等运行时实现交付后才改变已安装行为。

2026-11-08 再收窄同一处展示：离开当前列表之后，条目不进入用户可见的「待核实」分区。`obligation_indexed` 只写入内部审计索引。Desktop、TUI 和工作面板不展示该索引，也不给它徽章或注意提示。证据、不写 `stopReceipt`、不释放 claim、只接受 `user_panel`、工具只给主 Bot，都不因这次可见性修订改变。

ADR 116 的释放条件不变。本文不增加强制解锁，并把“PID 不可靠”落实成第 7 节的元组；只对元组齐全的新记录开放自动关闸。

ADR 119 仍是未接受提案。它草案里的“不增加工具通道”与本文的三件工具冲突。已接受的处理只把工具限制在只读核实、出示卡片和授权后的跟进处置，不增加 Shell 或第二个任务系统。这只收窄 119 的那一句草案，不接受 119 的其余条款，也不占用它预留的门槛 10。119 仍待单独审阅。

ADR 120 的“模型不确认停止”保持。核实工具返回缺口；resolve 不写停稳回执。`handling` 在资源仍被保护时仍是宿主责任，不因为 Bot 调用了核实就把模型叫回来轮询。

ADR 91、92、101 的授权主体不变。本次卡片是一次控制确认，不写入 Bot 的访问档位，也不被访问档位代替。

## 14. 审阅状态

2026-11-07：在知识库 `origin/main` `3402e83` 上确认 123 之后的空号是 124，缺号 2–14、19、20、23、107 未回填。代码事实来自 Peer-Agent `cb7e14c965c9102d49252e5a362457770ea51d14` 的文件内容，以及 PR 297 三个未合并提交的补丁。没有读取用户的运行数据。

同日 20:03（Asia/Shanghai）：用户阅读全文后明确回复「那就落实124」。本文自该时刻起为已接受，并授权按本文实施。当时只同步知识库里的接受状态。运行时实现不在该次变更中；不合并、不发版、不改现场记录。没有运行 Peer-Agent 的测试、构建或产品回归。接受不等于那三条记录已经离开“正在停止”。

2026-11-08（Asia/Shanghai）：用户确认 Peer-Agent PR 297 的手测已经通过，随后说「要待核实我觉得就不应该对用户开放」，并明确回复「要」。本文据此修订用户可见性，状态保持 Accepted。确认后仍写 `disposition=indexed` 与 `obligation_indexed`，索引留给诊断、支持和以后核对。日常界面不再展示「待核实」分区、列表、徽章或注意提示。授权卡改为说明：确认后不再跟进这些条目；执行结果仍未确认；资源不释放；普通任务列表里不会再看到它们。证据、不写 `stopReceipt`、不释放 claim、只接受 `user_panel`、工具只给主 Bot，均保持。不新增设置页。这次只改知识库。再读 PR 297 时它仍未合并，当时的头是 `59e411577492d4e02cf4565d84dd53bc7c2702df`。那次手测不把面向用户的「待核实」留成产品表面，也不等于修订后的界面已经落地。没有运行 Peer-Agent 的测试、构建或产品回归，没有改现场记录。
