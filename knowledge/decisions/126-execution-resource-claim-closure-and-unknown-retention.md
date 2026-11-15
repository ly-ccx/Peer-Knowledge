# ADR 126：执行资源 claim 的受控闭包、unknown 保留与隔离逃生

创建时间：2026-11-09
最后更新：2026-11-15（正式转为 Accepted，与 ADR 127 配套生效；对齐克隆交回边界与格式门槛说明；2026-11-09 曾由 ADR 125 改号为 ADR 126）
状态：Accepted（2026-11-15 用户确认与 ADR 127 一并转为正式接受契约；源码实施与发布验收按实际候选证据另记）
级别：A（执行资源、停止/闭包契约、授权与证据边界、持久化格式）；实施包含 B 级宿主/协议/迁移与 C 级界面表达。

2026-11-09 / 2026-11-15：[ADR 127](127-unknown-outcome-reconciliation-and-delegated-resolution.md)（已接受）扩展本文 §5.3 / §5.4 的授权模型（用户按项目 + Bot 主体委托 `ask / bot_verified` 两档收口；原提案的 `auto` 档在评审中取消）；本文的闭包、`RetainedUnknown`、计划镜像、隔离 clone 逃生和证据机制正式生效。

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[架构治理](../architecture/20-architecture-governance.md)、[委托运行时](../architecture/project-agent-delegation-runtime.md)、[人机交互契约](../specifications/peer-human-agent-interaction-contract.md)、ADR [91](91-project-bot-autonomous-coordination.md)、[92](92-scoped-permission-inheritance.md)、[101](101-bot-owned-access-policy.md)、[110](110-follow-up-responsibility-and-current-list.md)、[116](116-session-control-and-resource-settlement.md)、[119](119-user-stop-cognition-admission-and-settlement.md)、[120](120-runtime-facts-disposition-and-resource-wait.md)、[124](124-legacy-stop-obligation-controlled-resolution.md)、[127](127-unknown-outcome-reconciliation-and-delegated-resolution.md)。

本文修正 ADR 116 与 ADR 124 的**永久占用边界**，不推翻它们的其他条款：

- ADR 116 §6.2/§6.3 的 claim、hold、停稳回执与账本顺序继续有效；区别是“登记进程已死且无活体/句柄”时，unknown 从“目录 hold”改为“RetainedUnknown 记录”，不再永久阻挡同目录的新写入。
- ADR 124 的授权卡、知悉、跟进退役、死亡证明和 `release_resource` 拒绝规则继续有效；区别是新增一个**逐 claim**的受控闭包动作，并且它只由用户在宿主卡片上确认，不由模型或 `force` 参数触发。
- ADR 120 的资源等待闭环继续有效；新增“资源等待不得写成 work 终态”的实现要求。

## 1. 问题与现场证据

2026-11-09，一台已安装桌面端在新建任务时显示：

> 暂不能写入：此前操作结果未确认

任务一直停在“排队中”。现场核对结果如下（只记录结构事实，不保存私有任务正文和机器绝对路径）：

1. 同一项目根目录的设备资源账本上有 **3 条** `reconciling` claim。最早一条来自约 10 天前一个已取消的 PR 审查任务，从约 8 天前起一直占用目录；另两条来自其它早期取消任务。
2. 最早那条 claim 保留了一笔 `bash` 调用的未知结果：work budget 仍有 `uncertainDispatches`，但对应进程、句柄和 runner 都已不存在；期间用户在同一目录正常提交过多次。
3. 两条旧取消的 control 是 `unproven: true`、`reconciling`、没有 `stopReceipt`，`unknownCalls` 为空。它们原本可以在“无未知、无句柄”时结清，但 `session-cancellation.recover` 把“两边都是空数组”当成“没有变化”而永久跳过。
4. 协调 journal 里的 `sessionControl` 优先于 GoalPlan 镜像被读取。只修计划镜像时，journal 的旧 control 会在下一次对账重新把 claim 加回 `reconciling`；实测在数秒内复活。
5. 被拦下的任务在协调层已经是 `blocked_system / fatal`。资源等待被记成 work 终态，即使后来释放了目录，该任务也不会自动恢复。
6. 产品没有可点的释放/闭包入口：`nextAction: 'reconcile_execution_outcome'` 只有文案，`release_resource` 被 ADR 124 明确拒绝。按已接受规则，用户只能退役跟进，目录仍不可写——也就是**永久失去这个项目目录的写能力**。

这不是“某个操作仍在运行”或者“权限没有授予”。这是资源账本把**历史未知**当成了**当前写者**，并且没有终止条件。

## 2. 目标与非目标

### 2.1 目标

- 有死亡证明且无未知调用/未结束句柄的遗留停止，能被宿主自动结清并释放 claim，不依赖用户点按钮。
- 有未知调用、但登记进程已死且无活体/句柄的遗留记录，用户能在看到具体 unknown 与后果后，授权**逐 claim 闭包**：目录恢复可写，unknown 作为 `RetainedUnknown` 保留，不标成功、不重放、不删除。
- 不愿承担闭包风险的用户有一条不释放原锁的逃生路径：在独立克隆中继续工作。
- claim 闭包在重启和 journal 重建后仍然有效，不会被旧 control 重新加锁。
- 资源等待保持为可恢复的排队事实，不写成 work 终态。
- 所有动作仍走宿主授权、协调日志、设备账本和 Evidence 边界；模型文字、`force`、完全访问档位都不能替代用户确认。

### 2.2 非目标

- 不把 unknown 调用标记为成功、失败、已回滚或“没有发生”。
- 不重放未知调用；不自动重试、不自动回滚外部副作用。
- 不释放仍然 `live` 的执行、仍有未结束句柄的执行、远端未被围栏的外部效果，或无法确定资源范围的冲突。
- 不新增第二套任务系统、全局解锁按钮、文件级锁或跨设备资源同步。
- 不修改 ADR 124 的“知悉未知项”“退役跟进”“日常界面不展示待核实分区”等规则。
- 不把一次性数据修复当作产品路径；现场修复只用于恢复用户当前环境。

## 3. 核心判断：claim 保护的是并发写者，不是历史墓碑

ADR 116 的 claim 解决两个问题：

1. **并发互斥**：同一目录同时只有一个写执行者。
2. **未知保护**：不知道旧调用是否写入了目录时，不让另一个写者悄悄覆盖。

当登记进程已被证明死亡、没有未结束句柄、也没有任何 live 执行时，第 1 个问题已经不存在：没有写者会再写。第 2 个问题剩下的是“旧写入可能已经落地”这一**历史数据事实**；它影响用户对文件状态的判断，但不影响“是否还能安全地让新任务写这个目录”。

继续保留目录 claim 不能修复历史，只会让用户永久无法使用该目录。正确做法是把历史未知从“资源锁”降级为“证据记录”，并在用户明确知悉后结束 claim。这个区分是本文与 ADR 124 §1.5 的分歧点，也是本文要求修订该条的原因。

安全性由以下条件守住：

- 只对**登记进程已死**或**长期不可证且用户明确确认**的 claim 开放；
- 只对**无 live 执行、无未结束句柄**的 claim 开放；
- 只对**本机数据根**开放；远端未围栏效果与 `live` 执行一律拒绝；跨宿主未证明的本地 legacy 记录只允许用户确认闭包；
- 闭包是**逐 claim** 的，不是全局开关；
- 闭包不产生“成功”事实，unknown 调用原样保留。

## 4. 现有事实与代码缺口

代码基线为 Peer-Agent 开发线（2026-11-07 前后）。实施前必须按当时主线重新定位；下列锚点只说明问题位置，不是本轮验收证明。

| 现有行为 | 代码锚点（代码仓相对路径） | 缺口 |
| --- | --- | --- |
| claim 生命周期与 blocker | `packages/runtime-node/src/project-agent/execution-resources.mjs` 的 `inspect`/`reserve`/`protect`/`settle`/`reconcile` | `settle` 遇到非空 `unknownCalls` 一律保持 `reconciling`；`reconcile` 只导入保护，不释放旧 claim |
| 停止屏障与 control | `session-control.mjs` 的 `begin`/`drain`/`settle` | `unproven` 的旧停止在宿主代次变化后无法完成 drain；`withdrawal` 只结清 control，不释放 claim |
| 取消巡检 | `session-cancellation.mjs` 的 `recover` | `awaiting_outcome` 且 `evidenceCalls` 与 `unsettledExecution` 都是 `[]` 时被 `continue` 永久跳过 |
| control 真源 | `coordination-storage-v2.mjs` 的 `sessionControls` / `sessionControlHeads`；`readSessionControl` | 运行时优先读 journal，GoalPlan 只是镜像；只改镜像会被旧 control 覆盖 |
| 资源等待 | `execution-scheduler.mjs` 的 `inspect`/`select`；`session-supervisor.mjs` 的 `promote` | 启动被资源拒绝后，work 可能被记成 `blocked_system / fatal`，而资源释放后没有自动恢复 |
| 协议与表达 | `packages/protocol/src/session-control.ts` 的 `ExecutionResourceBlocker`；Renderer `drawerState.ts`、`CoordinationDetails.tsx` | `nextAction` 只有文案，没有宿主动作；没有闭包授权卡 |
| 已接受规则 | ADR 116 §6.2/§6.3、ADR 124 §1.5/§6.2 | unknown 转 hold 后仍永久阻挡；`release_resource` 没有成功路径 |

## 5. 决策

### 5.1 两类结清，一条逃生

| 场景 | 判定 | 动作 |
| --- | --- | --- |
| 完整 `recorder` 证明登记进程已死，`unknownCalls` 为空，无未结束句柄，`executionOwnership !== live` | `recorder_dead_clear` | 宿主沿现有 `drain`/`settle` 写真实回执并释放 claim；不需要用户操作 |
| 完整 `recorder` 证明已死，仍有 `unknownCalls` 或登记缺失，无句柄、无 live | `recorder_dead_with_unknown` | 宿主出示闭包卡片；用户可确认 `close_claim_retaining_unknown`，否则 claim 保持 |
| 没有完整 `recorder`，但租约代次已轮换、无 live、无句柄，且用户明确确认 | `legacy_recorder_unproven` | 只允许用户授权的闭包；不自动、不按时间推断死亡 |
| 远端未围栏、`live`、未结束句柄 | 对应拒绝类 | 闭包拒绝；保留 claim 与现有诊断 |
| 用户拒绝闭包风险 | 任意可闭包类 | 提供“在独立克隆中继续”；原 claim 不动 |

“独立克隆”指宿主管理的完整 clone（独立对象库和 `.git`），不是共享 `.git` 的 worktree。它只作为不释放原锁的逃生路径，不改变原 claim、unknown 或历史；任务输出通过分支/补丁交回（不得复用 ADR 68 / 79 中已淘汰的默认直写 / 静默 `AUTO_MERGE` 交回），发布/合并仍走原有授权（ADR 80 决策 7–8）。

### 5.2 受控闭包对象

新增设备账本与协调日志对象 `ExecutionClaimClosure`。它是资源处置回执，不是任务状态、不是停止证明、不是权限授予。

| 字段 | 契约 |
| --- | --- |
| `closureId` | 宿主生成，稳定幂等 |
| `claimId` / `claimRevision` | 闭包绑定当前 revision；旧 revision 不能闭包新 claim |
| `resourceRef` | 该 claim 的规范资源；一次只闭包一个资源 |
| `execution` | `planId`/`sessionId`/`executionEpoch`/`goalRevision` |
| `unknownCalls` | 排序后的工具调用 id；原样保留，不写结果 |
| `unknownRegistry` | 是否存在“没有派发登记”的缺口；存在时卡片必须显示 |
| `recorderProof` | `verified_dead`（含 bootId/pid/pidStart/hostId）或 `legacy_user_confirmed` |
| `authorityRef` | 用户卡片授权 id；model/force/full_access 不在此列 |
| `scope` | `managed_execution` + 本机数据根 |
| `receipt` | `applied` / `replayed` / `rejected`，附拒绝码 |
| `at` | 宿主时钟 |

闭包成功后：

- claim 进入 `released`，`evidenceCalls` 保留，另记 `closureId`、`releasedUnknownCalls`、`releasedAt`；
- 生成 `RetainedUnknown` 记录：工具调用 id、原执行身份、资源、未见结果的事实、闭包授权引用；它与闭包同一账本事务提交，并由 journal 闭包事件引用；它不参与 `inspect` 冲突判断；
- **不再保留目录 hold**。`RetainedUnknown` 只阻止“同一 operation/toolCallId 的重放”，不阻止新的无关写入；
- 任务详情、诊断和支持材料可以展示 `RetainedUnknown`；日常任务列表不新增“待核实”分区（沿 ADR 124 §8.3）。

### 5.3 授权与卡片

闭包在 `ask` 档只来自宿主卡片（在 `bot_verified` 档则按 [ADR 127](127-unknown-outcome-reconciliation-and-delegated-resolution.md) §5.4–§5.6 在用户预授权策略下由宿主校验证据后签发），两者均不来自模型参数：

- 卡片逐条列出：涉及目录、原任务、claim 年龄、未知调用 id、是否登记缺失、闭包后 unknown 仍保留、不会重放、不会标成功、目录将恢复可写；如可得，附该目录自未知调用以来的本地变更摘要（只读提示，不是证据，也不自动判定安全）；
- 一次最多 20 条；每条独立确认；
- 授权有效期 15 分钟；证据变化则作废（沿 ADR 124 的授权模型）；
- `full_local`、Ask、会话许可、旧 PermissionGrant、`force` 参数都不能替代；
- 模型只能请求出示卡片和复述回执，不能写 `confirmed`。

拒绝码至少包括：`live_execution`、`open_handle`、`remote_effect_unfenced`、`cross_host_unproven`、`claim_revision_stale`、`authorization_required`、`authorization_mismatch`、`scope_mismatch`、`already_released`、`not_closeable`。

### 5.4 自动结清与巡检修复

1. `session-cancellation.recover`：仅当 `unsettledExecution(plan).length > 0` 时才跳过 `awaiting_outcome`；空集走现有 `drain`/`settle`，生成 `unknownCalls: []` 的回执。
2. 启动对账：设备账本先按 ADR 124 分类；`recorder_dead_clear` 立即结清，不等用户；其余只出示诊断/闭包卡。
3. `execution-resources.reconcile`：对已闭包的 claim 不得 `protect` 回 `reconciling`；闭包记录必须写入协调 journal，不能只写在派生 SQLite。
4. journal 重建后，闭包结果必须从 journal 恢复；旧 control 不能覆盖闭包。实现时按主线实际占用提升最低 reader/writer/executor 门槛到 `> 11` 的下一个可用整数（主线 ADR 124 已占用 `11`，未接受的 ADR 119 所占 `10` 已作废且不得复用；也不得在 PR 297 / 306 等候选合并前把未合入版本当作已发布事实）。

> 补充（2026-11-15，与 ADR 127 对齐）：按已接受的 [ADR 127](127-unknown-outcome-reconciliation-and-delegated-resolution.md)，闭包确认除 `ask` 档下由 `user_panel` 卡片逐条确认外，还可在用户预先委托的 `bot_verified` 策略档下，由主 Bot 请求对账探针后交宿主校验证据与风险包络并签发受控收口；两者共用 `RetainedUnknown`、计划镜像、死亡证明与审计边界，`auto` 档保持取消。

### 5.5 资源等待不是终态

- `execution_resource_unavailable` / `resource_protection` / `coordination_reconciliation_required` 只产生排队或 blocked 的资源等待事实，不写 `work.end = fatal`。
- 队列恢复在同一 task/session 内进行；不要求用户重建任务。
- 资源释放或闭包提交后，宿主按稳定 id 唤醒队列；不周期调用模型、不重复扫描全部历史。
- 若等待超过可解释范围，展示具体 blocker、年龄、原任务和下一步；不得把资源等待说成任务失败。

### 5.6 启动与界面

| 事实 | 表达 | 可用动作 |
| --- | --- | --- |
| 旧 claim 仍 `reconciling`，owner 已死且 unknown 为空 | “正在结清此前的执行记录” | 无；宿主自动完成 |
| 旧 claim 有 unknown，owner 已死 | “暂不能写入：此前操作结果未确认”，附目录、原任务、time | 查看此前任务；已核对并释放；在新副本中继续 |
| 旧 claim 无法证明死亡 | 同上，附“未证明”说明 | 仅用户确认闭包，或在新副本中继续 |
| live/句柄/远端未围栏 | 保持保护 | 查看、等待真实停止；不显示释放 |

闭包确认后，项目目录恢复可写；unknown 仍在原任务详情与 `RetainedUnknown` 中；界面不得出现“已成功”“已回滚”或“没有影响”的断言。

## 6. 与 ADR 116 / 124 的修订关系

| 原条款 | 本文处理 |
| --- | --- |
| ADR 116 §6.2：unknown 转 `ResourceHold`，继续按保守范围保护 | 保留 hold 作为“无法证明死亡/仍有句柄”的保守状态；新增“已证明死亡 + 无句柄”的闭包出口，unknown 转 `RetainedUnknown` |
| ADR 116 §6.3：只有匹配停稳回执才能结清 claim | 自动结清仍要求回执；用户授权闭包是**第二种**结清依据，必须记录 `authorityRef` 与 `recorderProof`，不是停稳回执的替代证明 |
| ADR 124 §1.5 / §6.2：不新增释放工具，不接受“用户愿承担风险所以放开目录” | 修订为：在死亡证明/长期不可证、无 live、无句柄、逐 claim 用户确认的前提下，允许闭包；仍拒绝 `force`、全局解锁和无证据释放 |
| ADR 124 §4.1 `recorder_dead_with_unknown`：claim 保持 | 改为“默认保持；用户可授权闭包”。任务列表仍不展示待核实分区 |
| ADR 120：资源等待闭环 | 增补“资源等待不得写 work 终态；释放/闭包后自动唤醒队列” |

## 7. 迁移与兼容

1. 首次启用新格式前，封新写准入，扫描已有 claim：完整死亡证明 + 空 unknown → 自动结清；完整死亡证明 + unknown → 生成闭包候选；遗留无证明 → 生成候选并标注不可自动。
2. 不删除旧 claim、unknown 数组、Evidence、预算或会话；闭包只追加记录。
3. 客户端展示旧记录时继续用现有 blocker；新格式启用后旧 writer 必须拒绝执行，不能“忽略新字段继续写”。
4. 降级前封新准入；闭包记录保留；旧构建不得把已闭包 claim 重新投影为可写，也不得重新加锁。
5. 现场一次性修复（直接改账本/读模型）只能用于恢复用户环境，必须在诊断中标注，不作为产品行为；产品路径是本文的受控闭包。

## 8. 实施拆分

| 卡片 | 内容 | 依赖 |
| --- | --- | --- |
| EC-01 | Protocol：`ExecutionClaimClosure`、blocker `nextAction`、拒绝码、journal 事件与版本门槛 | 无 |
| EC-02 | 运行时：`recover` 空集结清、启动对账自动结清、闭包后不被 re-protect、journal/镜像一致性 | EC-01 |
| EC-03 | 设备账本：闭包事务、`RetainedUnknown`、同 operation 重放拒绝、幂等与 revision 绑定 | EC-01 |
| EC-04 | 授权：宿主卡片、用户确认、15 分钟有效期、审计；模型只能请求不能确认 | EC-03 |
| EC-05 | 隔离逃生：宿主管理 clone、独立 `.git`、任务绑定与交回 | EC-03 |
| EC-06 | 队列：资源等待不写终态、释放/闭包后唤醒、任务内恢复 | EC-02 |
| EC-07 | UI：banner/详情、三个动作、文案、键盘/焦点/读屏、reduced-motion 静态终态 | EC-04、EC-05 |
| EC-08 | 迁移/诊断：存量分类、候选列表、支持导出、格式门槛与回退 | EC-02、EC-03 |
| EC-09 | 验证：单元、恢复、崩溃窗口、双宿主、真实产品回归 | 全部 |

实施顺序按依赖串行；不得把闭包、队列和 UI 合并成一个大 PR。按仓库规则，普通开发只做内容/diff 审阅，测试与产品回归留到发布候选。

## 9. 验收与反例

1. 完整死亡证明 + 空 unknown：宿主自动写回执并释放；重启、journal 重建后不复锁；新任务可写。
2. 完整死亡证明 + unknown：未授权时保持保护；用户确认闭包 → claim 释放、unknown 仍在、同一 toolCallId 重放被拒、新的无关写入允许、无成功断言。
3. 用户拒绝闭包：claim 不动；可改用独立 clone 继续；原任务与 unknown 不变。
4. `live` 执行、未结束句柄、远端未围栏：闭包一律拒绝，且不因重复点击变成成功；跨宿主未证明的 legacy 记录只允许用户确认闭包。
5. 遗留无 `recorder`：不自动闭包；卡片明确“未证明死亡”；只有用户确认才可闭包。
6. 资源等待：任务保持可恢复的 queued/blocked 资源状态；释放后自动恢复；不出现 `work.end = fatal`。
7. 两条 claim 同目录：闭包一条不释放另一条；另一条仍按自己的证据处理。
8. journal 与计划镜像不一致：以 journal 为准；闭包后启动对账不重新加锁。
9. 只读任务不因写 claim 被挡；写任务在闭包后可正常 reserve/activate。
10. 审计：授权 id、claim revision、unknown 列表、recorderProof、闭包时间可从日志重建；删除历史或改未知数组即失败。
11. 崩溃窗口：闭包事务提交后、UI 刷新前重启 → 以日志为准，不出现“界面已解锁、日志仍锁”或反向窗口。
12. 产品表达：不出现“强制解锁”“已成功”“已回滚”；闭包按钮只在有至少一个可闭包 claim 时出现；减少动效下仍有完整静态终态。

## 10. 未决问题

1. 是否给闭包设置最小等待期（例如至少一次宿主代次轮换或 24 小时）。本文不建议按时间自动闭包；时间只用于展示和人工判断。
2. 闭包是否允许主 Bot 请求卡片，还是只允许用户在任务详情确认。本文建议两者都可，但确认 actor 必须是 `user_panel`。
3. `RetainedUnknown` 的保留期与导出格式；本文要求不自动删除，具体保留策略留给存储与支持流程。
4. 独立 clone 的存储位置、清理责任和结果交回方式；需要与隔离工作区、交付和发布流程对齐。
5. 跨设备数据根、远端 Provider 未围栏效果是否永远不可闭包；本文持保守立场，需后续 ADR 讨论。

## 11. 变更记录

- 2026-11-09：创建。基于一次已安装桌面端的真实长时间阻塞现场，提出 claim 闭包、unknown 保留、隔离逃生及资源等待修正；待用户评审后再进入代码实施。
- 2026-11-09（晚）：知识库主线新增 ADR 125「资源窗口目录标签」，本文由 ADR 125 改号为 ADR 126；内容与实施收据不变，代码 PR 与图谱同步更新。

## 12. 实施收据（2026-11-09，源码 draft）

代码分支 `codex/execution-resource-claim-closure` 基于 `PeerAgent/dev/0.1.0`（rc.40），[Peer-Agent PR #306](https://github.com/ly-ccx/Peer-Agent/pull/306) 仍为 draft。以下只说明源码交付，不代表已合并、已安装、已发布或已验收。

| 提交 | 内容 |
| --- | --- |
| `a93b0b2d` | Protocol 闭包类型、`closeClaim`、`RetainedUnknown`、obligation `close_claim`、空 unknown 回收、dead-recorder 自动结清 |
| `665cc7ad` | 计划镜像 `executionClaimClosure`、重建后不复活、withdraw 失败不再写 `fatal` |
| `7217a4df` | 授权卡释放标记、后果文案、按钮与提示词 |
| `5b50dc99` | 任务详情「已核对，请求释放写锁」、宿主 IPC、retained unknown 展示 |
| `cba3780c` | 闭包授权卡绑定 bot 会话 |
| `9a677ebe` | 任务详情闭包请求的宿主测试 |
| `1116c086` | 修正 system-context 模板字符串里的反引号（TUI build 失败） |
| `88c21673` | blocker `closeClaimAvailable`、只在实际可闭包时显示按钮、闭包收据回退展示 unknown |
| `fe905198` | 跟进已退役但 claim 仍在时，仍允许请求释放 |

以下为源码自审与聚焦测试，不是独立审查或产品验收：

- 聚焦测试：`execution-resources` 23、`execution-obligation` 3、`session-cancellation` 1、`session-control` / kernel / grant 19、调度与资源等待 44、`intent-lifecycle` / `runtime-disposition` 27、`drawerState` 25、`CoordinationDetails` 3、`ObligationGrantCard` 2、application service 35、IPC / obligation bridge / card electron 8、protocol 335。
- `@peer-agent/protocol`、`@peer-agent/runtime-node`、`@peer-agent/desktop` typecheck 通过；`runtime-node`、`tui` build 通过；`ipc:check` 通过（409 channels / 443 preload operations）。
- CI run `42547320802` 在 macOS 与 Ubuntu 通过（提交 `88c21673`）；CI run `42552035897` 在 macOS 与 Ubuntu 通过（提交 `fe905198`）。

未完成（2026-11-09 候选基线）：独立 clone 逃生、独立 journal 闭包事件与版本门槛、存量迁移/诊断、完整 release 门禁与桌面/产品回归。本文已于 2026-11-15 与 ADR 127 一并转为 Accepted 契约；源码合并与发布验收仍按实际交付候选独立核算。
