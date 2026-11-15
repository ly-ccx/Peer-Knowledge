# ADR 117：意图驱动的协调判断、持续责任与目标闭环

创建时间：2026-11-01
最后更新：2026-11-03

2026-11-03 契约澄清：见 [RC35 等待与接管闭环故障](../../playbook/v0.1.0/agent-wait-recovery-closure.md)。已有宿主准入的结构化静默等待独立收尾，既不累计也不清零无进展次数，不写失败、交付或完成；具体等待对象持久化，原 Intent 保持 active。接管只消费 Session Control 的停止证明，不另扫父 work 预算；原操作的当前 applied 空 unknown 停止回执可恢复误挂 transition，但必须严格匹配完整执行身份并经原端口重检目标、真人门、用户停止及租约。该等待不产生下一回合执行授权，不删除合法处置门禁，不变更存储、能力、权限或 Evidence。当前源码修复仅经内容/diff 审阅，未运行测试或发布验收。

状态：Accepted / 四包源码实施与自测完成（交付分支，2026-11-01）。代码 `3c7ef152`，实际检查、一次文件复测及未覆盖范围见[实施回执](../../playbook/v0.1.0/intent-driven-coordination-self-test.md)。尚未合并、安装或发布；真实模型、安装版与发布产品验收仍待执行。

级别：A（协调协议、目标关闭、上下文准入及存储兼容），B（Runner、交付、失败隔离和进展策略）。产品表面若需调整，另按 C 级体验流程处理。

产品依据：[产品理念与价值对齐](../../design/product/peer-product-alignment.md)。工程依据：[架构治理](../architecture/20-architecture-governance.md)、[System Context](../architecture/19-system-prompt-context-architecture.md)。

关联：[ADR 88](88-project-agent-execution-continuity.md)、[91](91-project-bot-autonomous-coordination.md)、[93](93-verification-continuity-and-repair-ownership.md)、[94](94-reply-attempts-silent-wait-and-recovery.md)、[95](95-progress-driven-execution-policy.md)、[110](110-follow-up-responsibility-and-current-list.md)、[111](111-project-agent-duplex-supervision-and-continuity.md)、[112](112-runtime-module-and-loading-boundaries.md)、[113](113-checkpoint-content-addressed-storage-and-retention.md)。实施入口：[IC-01—IC-04](../../playbook/v0.1.0/intent-driven-coordination.md)。

## 1. 目标与范围

用户关心的是意图进入后如何被理解、如何分配判断权、何时继续推进以及何时交还。外部渠道只改变输入来源，不是本决策的主轴。

主 Bot 持有用户目标、约束、优先级与跨任务关系；工作 Agent 在已准入范围内自主解题；宿主维护来源、版本、执行、等待、恢复及责任交接；核验提供结果是否成立的依据。保留主 Bot → 工作会话 → 临时 Explorer/Verifier 层级。

本决策深化现有协调内核，不新增任务表、常驻意图 Agent、自由群聊、固定业务工作流、独立授权系统或第二个执行器。模型选择下一步，代码约束合法边界。普通讨论和轻量问答无需建立 GoalPlan，也不强制增加模型调用。

```mermaid
flowchart TD
    I[用户输入与任务事实] --> F[当前目标与相关事实视图]
    F --> M[主 Bot 语义判断]
    M --> K[既有协调内核：校验并持久化处置]
    K -->|继续、修订、返修| E[现有 Supervisor 与 GoalRunner]
    E --> F
    K -->|等待| W[具体等待对象与唤醒条件]
    W -->|条件变化| F
    K -->|准备交还| V[结果核验及原目标覆盖]
    V -->|仍有缺口| F
    V -->|满足条件| D[结果交付与既有签收]
    D --> C[关闭对应根协调责任]
```

## 2. 核对基线与证据边界

源码基线：Peer-Agent `5dffbd4b4ced0bb841c9e879debd50b8bb081b9c`。知识整合基线：Peer-Knowledge `10707b62945cf47d7080cfb9161b166f07ffae23`。以下来自源码和现有用例的静态阅读，不是故障复现、模型质量评测或发布验收。

| 已有机制 | 代码锚点（相对 Peer-Agent） | 判断 |
| --- | --- | --- |
| 持久输入、独立 ID、消费与执行确认 | `packages/runtime-node/src/project-agent/input-queue.mjs` | 保留 |
| 用户优先、安全点让出、原生检查点 | `packages/runtime-node/src/project-agent/runner.mjs`、`apps/desktop/electron/main/agent-host/agent-turn-executor.mjs` | 已有实际执行路径 |
| 协调来源、CAS、goalRevision、executionEpoch | `packages/runtime-node/src/project-agent/coordination-kernel.mjs` | 保留授权和当前性检查 |
| 双向工作问题、等待父答、保护真实人工门 | `packages/runtime-node/src/project-agent/agent-communication.mjs`、`agent-supervision-communication.mjs` | 沿 ADR 111 复用 |
| 技术责任、返修接回与统一 followUp | `packages/protocol/src/task-overview.ts`、`packages/runtime-node/src/project-agent/repair-ownership.mjs`、`repair-custody.mjs` | 不能描述为尚无主动推进 |
| 子任务核验、有限返修、签收 | `packages/runtime-node/src/goal-runner.mjs`、`project-agent/acceptance.mjs` | 保留原闸门 |

| 缺口 | 可确认的源码行为 | 影响及置信边界 |
| --- | --- | --- |
| 原目标关闭偏向子任务状态 | `coordination-lifecycle.mjs:lifecycleOf` 在关联 session 全 accepted/cancelled、无待完成 transition 时返回 fulfilled；`coordination-lifecycle.test.mjs` 有对应用例 | 先签收调查、下一 wake 再安排实现的合法多阶段流程可能丧失协调资格；不是所有调查都会失败，具体运行未复现 |
| 回合结束缺少统一语义处置 | `continuation-policy.mjs` 对非 yielded 默认 delivered，再由 `runner-coordination.mjs`、`repair-ownership.mjs`、`reported-wait.mjs` 修正 | 已有补偿，但讨论答复、阶段交付与原目标完成没有统一记录 |
| 故障影响面偏大 | `reply-delivery.mjs` 串行追加消息与 accept；`runner.mjs:pump` 有 pending delivery 即退出；`circuit-breaker.mjs` 为 workspace 级失败计数 | 签收补偿可能挡同 Bot 独立输入，局部判断失败可能扩大为整个 Bot 的准入拒绝 |
| 默认决策事实不完整 | `event-mapper.mjs` 将失败明细写入 payload；`project-roster-source.mjs:normalizeEvent` 不保留这些字段 | 默认 L7 摘要不足，原始事实仍在，模型可经工具补查 |
| 无进展判据分散 | 回合事实指纹、协调失败的自由文本 reason 完全相等、watchdog 同因失败分别计数 | 判据存在局限；误停或空转的实际频率未测量 |

上述缺口不是放宽授权、删除核验或增加默认累计上限的理由。

## 3. 真值归属与不变量

1. Conversation 持有公开输入/回复；GoalPlan 持有子任务目标、执行结果、核验与签收；现有 coordination work/日志持有原始委托的解释、处置与持续协调责任。不得复制一份 Task 完成状态。
2. 子任务 accepted 证明其自身结果已按原政策签收，不单独证明原始委托已满足。根协调责任 fulfilled 不反向签收子任务、不释放执行资源。
3. 模型解释、目标覆盖判断与方法选择都是有来源的认知记录，不是用户原话、权限、Tool Result 或 Evidence。宿主能验证引用、身份和版本，不能用 schema 证明模型理解正确。
4. 每条用户输入保留独立处置；新修订有当前 canonical 输入来源。引用限定范围，无关目标继续推进。普通 wake 不从历史文本创造新目标。
5. 回复、回合、执行片段、阶段结果与根责任分别收尾。用户停止当前回复不等于撤回委托；撤回仍走既有控制入口。
6. 持续责任不等于无条件运行。真实人工门、明确暂停/取消、未知副作用、显式预算、租约和存储不可用继续阻止相关执行。
7. 所有模型发起的能力仍经 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。Renderer 只消费事实投影，主 Bot 保持只读与协调能力模式。

## 4. 输入解释与原始意图契约

在既有 work 中加法保存 `InputDisposition` 与 `IntentInterpretation`，不建立全局 Intent 表。名称为接口草案，IC-01 冻结实际 Protocol 定义。

| 记录 | 必需内容 | 约束 |
| --- | --- | --- |
| InputDisposition | inputId、所属 Bot、目标 work 引用、讨论/回答/委托/补充/修订/撤回关系、理由、decisionRef | 一次可理解多条输入，但逐条保存身份与处置；一条输入可影响多个明确目标 |
| IntentInterpretation | 原始/修订输入引用、当前期望结果、约束/非目标、未决问题、目标版本、要求与来源的映射 | 是模型解释；不能覆盖原始文本或自动批准新能力 |
| GoalCoverageAssessment | 当前目标版本、要求与已绑定子结果/核验/Evidence 的覆盖关系、剩余要求、不确定性、判断来源 | 不把摘要或路径当执行证据，不另造 resultAcceptance |

对同一意图的补充或修订绑定原 work；独立委托建立独立 work。查询进展不重建任务，提供线索不自动扩大范围，讨论/建议不自动升级为执行。用户要求“先分析，能修就修”可以形成明确的连续委托；“只给方案，先不要改”保留执行限制。

意图记录由主 Bot 原回合产生，不增加独立分类模型。简单回答沿原发送路径保存最小处置即可；有持续委托时才保存持续责任。语义目标修订由宿主单调增加 goalRevision；观察和回合处置不无故递增目标版本。

## 5. 判断接口与持续处置

深化既有 `coordinate_work`：query 可按合法 workId 查询尚无子任务的当前工作，也可由 sessionId 解析绑定；新增结构化 assessment/disposition 提交分支，复用 Delegation Provider 与协调 kernel，不另造工具执行端口。具体 discriminant 在 IC-01 冻结。

提交包含 operationId、来源输入/事件/既有决定引用、expectedWorkRevision、expectedGoalRevision、模型判断及下一步处置。两个 revision 分工：work revision 防止协调记录覆盖，goalRevision 防止对过期目标执行；不得混用 journal 的全局序号。

| 处置 | 宿主必须确认的承接事实 |
| --- | --- |
| continue | 已准入协调操作，或同目标下持久且唯一的 runnable 后续；“我会继续”不是承接事实 |
| wait | 具体 session/问题/资源/恢复记录及版本、唤醒来源；用户等待必须引用真实请求 |
| return | canonical 回复引用、当前版本的目标覆盖判断、必要子任务核验/签收及无未决义务 |
| blocked_system | 真实失败类别、影响范围、保留责任、可查询的解除条件或诊断入口 |
| withdraw | 当前真实用户来源、原控制/停止回执；不删除未知历史结果或伪造成功 |

模型提交的 assessment 字段不能签发后续执行权限；本次协调元数据能力调用仍经过既有 PermissionGrant，项目执行另经对应能力准入和授权。内核先验证并耐久记录处置意图，既有 adapter 再完成派发、修订、返修、等待或交付。recorded 与 applied 分开：return 意图可先引用已准备的回复，只有实际交付及必要签收回执满足后才能关闭根责任，不能要求“先已送达才能登记发送意图”形成循环。副作用按既有稳定操作身份补偿，不宣称跨 Conversation/GoalPlan/日志的原子事务。

事件 handled 表示责任已由持久 work 接走，不表示目标完成。事件已消费而后续仍待推进时，使用已准入决定引用与稳定的宿主待办身份恢复；不能重新冒用旧输入为“新用户请求”，也不能要求每次继续都有新的外部事件。只唤醒仍有效的有界待办，不定期调用模型询问没有变化的目标。

原生执行切片让出时可沿用上一份未尽责任和完整 checkpoint；无需强迫模型在每次安全点输出总结。正常协调收尾需要合法处置；缺失时在原预算内至多一次修正，仍缺失则保留系统阻塞，不推定 fulfilled。普通无委托问答继续允许原有轻量答复；资格在提交时根据当前事实判断，不能只看回合开始时的空 roster。

## 6. 原目标关闭与阶段自治

对采用新契约的 work，取消 `all sessions accepted/cancelled → fulfilled` 的充分条件。子任务依旧独立签收、退出子任务当前列表；主 Bot 仍可能持有原目标的后续责任。

根责任关闭必须同时满足：当前目标版本的要求已经覆盖；必要子任务结果与引用版本有效；没有本目标仍未处理的工作问题、控制转移、未知 dispatch、真人门或已准入后续；关联结果已实际交付并完成既有必要签收；宿主成功提交关闭回执。部分取消不能被当作被取消要求已经完成；整个委托撤回走 cancelled/withdraw，不写 fulfilled。

准备交还时，优先复用已绑定、确实覆盖原要求的既有核验。覆盖不足时，经既有只读 Verifier seam 做一次目标覆盖复核，沿配置、预算、能力链与版本检查；不为每次观察新增核验调用。语义判断失败返回具体剩余要求，仍由主 Bot 选择方法；已发生结果和签收历史保留。复核判断不是用户验收或工具权限。

工作 Agent 自主选择范围内的方法、局部实现和普通返修。主 Bot 负责目标修订、跨任务关系、不可沿用的错误方向和最终覆盖；不强制 worker 每一步请求父 Bot。既有核验返修、任务接手和工作问题仍走 ADR 111，不因新增原目标责任再创建监督者。

## 7. 交付和故障隔离

在原交付日志中分别记录消息提交回执与签收补偿回执：消息是否已追加、签收是否待办/成功/不适用/失败、来源版本、稳定操作身份和下一次重试依据。沿原 outbox/日志持久化，不新增交付数据库。

旧 `reply_delivered` 的综合语义保持兼容：只有消息提交及必要签收达到原完成条件才写入；不能将“消息存在”自动解释为任务已签收或旧回复错误已 recovered。新回执允许宿主继续处理独立输入，而相关 work 仍等待补偿。若来源变更，原消息保留，追加失效/更新事实，不删除已发生的公开表达。

同 work 的有序交付与目标关闭依赖保留；一项 prepared/settlement_pending 不再令整个项目 pump 退出。失效租约、权威日志损坏等全局安全故障仍可停止宿主。每个待交付项有独立错误、重试预约和恢复入口，失败项不能无限占用协调名额，也不能因无关 work 运行而遗失补偿。

| 故障范围 | 处置 |
| --- | --- |
| 单 work 的重复失败/无进展/不合法处置 | 限制该目标或 attempt，保留原责任；独立输入仍可处理 |
| Provider/账号/渠道故障 | 复用现有路由与健康准入，影响实际依赖该渠道的请求；不能擅自换模型或账号 |
| 单操作 unknown | 保留相应执行及资源保护，先对账；不阻止不冲突工作 |
| 租约/权威存储不可用 | 停止相关宿主写入/派发，给出宿主可证明的不可用事实 |

无可用模型或显式预算耗尽时不额外调用模型生成通知。隔离故障不代表承诺模型离线时仍能回答；接收/排队回执与真实处理分开表达。

## 8. 决策事实视图与进展治理

`DecisionFrame` 是从现有 work、GoalPlan、followUp、监督请求及操作回执派生的只读视图，不是新真值。优先选择当前输入/事件关联目标，包含：当前意图及来源、目标/工作版本、剩余要求、相关结果、开放问题、原始错误类别及必要 payload、真实人工门、未知副作用、已尝试方法、可用动作及拒绝原因。

保留事件 ID、输入 ID、源版本和检索引用；有大小/条数上限、稳定分页或回查入口，显式标注遗漏。不能以无关新任务挤掉本次事件对应的旧目标；不把 payload 原样无限塞进提示词，不带私有思考或凭据。通过既有 project-roster L7 Source 准入，L1 只放稳定角色规则。视图是观察快照，执行前仍回读权威事实。

统一 `ProgressObservation` 的含义：新观察、已接纳动作、要求覆盖增加/阻塞解除分别记录。不同工具结果不自动等于目标推进；有价值的调查可以产生新证据，不能要求每次读取都完成一项要求。

重复失败使用宿主可核对的 work/目标版本、操作类别、错误类别及相关对象身份；reason 改写、UUID、时间、重启、换执行者不清零。模型声称“换方法”不能单独刷新额度；新材料或可行替代以来源与实际操作记录支撑。启发式无法证明方法一定有效，需保留诊断与语义质量验收。

回合、协调操作和 watchdog 共用归一化事实，各自仍负责切片、操作及停滞唤醒；不简单合并为一个全局失败次数。保留 ADR 95 的无默认累计硬上限及显式预算，禁止新增 maxIntentSteps 等隐蔽累计截止。主动性来自未完成且有依据的责任，不来自反复轮询。

## 9. Module、持久化与并行工作边界

| Module / Seam | Interface 与 Depth | 实施方向 |
| --- | --- | --- |
| 协调 Kernel | 验证并提交输入处置、目标解释、覆盖判断、下一步及关闭；维护来源/CAS/唯一承接 | 深化原 kernel/reducer，不堆入 Runner 或 Supervisor |
| Decision Frame | 按目标选择事实、保留错误和版本、返回合法动作与回查入口 | 深化 project facts/roster Source，减少调用方拼接 |
| Runner Adapter | 接收唤醒、让出、保存原生现场、消费内核决定 | `runner-coordination` 收敛重复收尾，Runner 只执行循环 |
| Reply Delivery | 同 work 有序提交、签收补偿、幂等恢复和局部调度 | 原交付 Module；accept 继续调用原权威端口 |
| Progress Policy | 归一化失败与观察、作用域、重复判定 | 现有 continuation/watchdog/coordination adapter 共用 |

新记录复用 coordination-v2 journal/blob 与派生 SQLite。Conversation、GoalPlan、原 Evidence 和权限库不迁成新存储；不新增本机目录。涉及内容寻址、保留/回收时遵守 ADR 113：活跃责任、待交付和恢复引用必须成为保留根，不能 GC 掉仍有作用的事实。

并行设计接口：2026-11-01 已发现另一工作树在途的 ADR 116“任务控制与资源交接”及 SC 工作包；它不属于上述已合入知识基线。117 不定义停止屏障、资源账本或 claim 释放算法。实施开工时核对其合入状态：如已合入，只消费其 Session Control/Resource Admission 事实；如未合入，使用当前接口 Adapter 并明确能力限制。共享 Protocol、coordination schema、Supervisor 的修改需串行整合；任何版本号不得与其他工作包抢占。文档存在不代表在途能力已可用。

## 10. 兼容、恢复与回滚

1. 只有有来源的新记录启用新关闭语义。旧 accepted/fulfilled/取消、原始消息和执行事实不批量重开或改写；历史摘要不能补造执行委托。
2. 活跃 legacy work 先按既有 mandate 与来源解析范围；仅可添加有依据的解释，无法确定时保持 legacy/unknown，可查询或提出具体范围问题。不能以兼容为由扩大授权，亦不能要求用户重复批准已有明确范围。
3. IC-01 根据届时 manifest/head、minimumReader/Writer/Executor 和所有已合入协议冻结版本矩阵；新增事实要求不能兼容读取时严格提高门槛，不在本文预占数字。旧 writer 拒绝写入新活跃工作；重建/manifest 丢失不能降低门槛。
4. 迁移为追加式、幂等、可中断恢复。分别覆盖决定记录、待办入队、真实派发、消息追加、签收和关闭前后崩溃；对账已知结果，unknown 写入不重放。
5. 回滚先停止新语义准入、安置未决责任与交付，保留记录和版本门槛；不删除字段让旧程序强行接管。根责任未关闭不代表已取消的子任务可以复活。

## 11. 对应 ADR 的衔接

| 原决策 | 本决策交付分支的实施衔接 | 必须保留 |
| --- | --- | --- |
| ADR 88 / 91 | 原目标解释、阶段签收与根关闭、typed disposition | 来源、预算、CAS、epoch、取消/恢复及唯一能力链 |
| ADR 93 / 110 | 子任务责任与根责任分层；已签收阶段退出子列表不消除原目标 | 唯一 followUp、真实人工门、历史结果和 Evidence |
| ADR 94 | 分列消息提交/签收补偿，使局部故障不挡独立输入 | silentWait、原 recovered 证据条件及旧回执语义 |
| ADR 95 | 统一进展观察及局部失败范围 | 无默认累计上限、真实预算与未知用量 |
| ADR 111 / 112 | 统一根责任处置入口和当前事实视图，减少事后拼接 | 结构化工作问题、双向执行回执、原生续接和模块所有权 |

本决策按 §13 获准实施，实际交付分支接口见 §14；关联 ADR 已同步实施衔接。原 Accepted 决策的历史验收仍保留原候选和范围，不由本次源码自测改写。

## 12. 实施、验收与当前状态

四包依赖为 **IC-01 → IC-02 → IC-03 → IC-04**。每包的文件边界、必补用例、退出条件、交接与最终验收见实施入口；不得跨包并行修改同一协议和协调内核，也不将任务卡当作代码实施授权。

最终必须证明：调查阶段签收后仍能在原目标内继续；讨论不升级执行；用户修订及时约束旧执行；技术问题先由 Bot 消化；真实人工门保留；局部交付失败不挡独立输入；同因失败不能靠改写理由清零；重启/迟到结果不丢责任或重复副作用；原目标最终仅关闭一次且有当前版本依据。

最初文档阶段仅完成内容、交叉引用与 diff 审阅；后续授权见 §13。普通日常工作仍服从代码仓 Validation Scope，当前四包则有用户明确的自测授权。版本/RC 前仍须对届时最终组合候选执行完整门禁。真实模型、安装包、辅助技术与独立审阅分别记录，不能用受控传输用例冒充。


## 13. 2026-11-01 实施授权与 IC-01 接口冻结

用户明确授权 IC-01 至 IC-04 全部实施及自测，无需逐包重复确认。代码隔离分支从开发线 `0f68f281` 建立；原工作树及运行实例保留。四包在同一交付分支按独立提交顺序整合，前包提交并推送后进入后包；不自动合并到发布分支。

本轮自测授权覆盖必要的单元/生产 Module 集成、构建、类型/架构/IPC 检查和本方案行为验收；实际命令与范围逐包记录。真实模型、安装包及辅助技术覆盖需分别举证，不能由脚本通过推定。

IC-01：在现有 work 上保存 intentCoordination，单独的协调判断 revision 用于 expectedWorkRevision；预算/计量更新不改变该 revision，避免模型读取版本后因 beforeTool 记账立即 CAS 失效。goalRevision 仍来自宿主 mandate；无 mandate 的问答/解释使用 0，不因此创建执行授权。稳定 operationId 回执进入既有日志的 intentDecisions 派生 bucket。新事实使用格式门槛 8；在途 ADR116 使用 7，未整合其 reducer 时不宣称支持 7。存储格式仍为 coordination-v2，不增加数据库或目录。最低版本必须由 durable head、回放和 manifest 重建共同保留。

## 14. 四包实现后的接口与恢复边界

以下是实现冻结记录，取代前文的接口草案命名；完整命令、候选身份和覆盖另见[实施回执](../../playbook/v0.1.0/intent-driven-coordination-self-test.md)。

| Interface / 真值 | 实现与约束 |
| --- | --- |
| `InputDisposition` / `IntentAssessment` | Protocol 的逐输入字段为 `inputId/kind/reason`；Bot、work、来源、双 revision 与 decisionRef 由包络和宿主回执关联，不在每条解释里复制权限。简单讨论沿原 Conversation/work 回复回执完成，不强制建立 Intent 或 GoalPlan，也不增加分类请求。 |
| `intentCoordination` | 既有 work 上保存解释、覆盖、当前处置、核验及关闭；`intentDecisions` 是原 journal 的派生 bucket。`intent_assessed/reviewed/closed` 追加事实，不建立第二套任务状态。Covered 要求必须引用实际来源版本及非空 Evidence 引用，仍须通过宿主核验。 |
| 当前输入 / 事件 / 持久继续 | 当前 canonical 来源或同一 active mandate 的持久 continue 可以承接下一阶段。`decisionTurnId` 由宿主签发；同一已准入回合重判处置仍可沿该回合的原来源承接，不因工具顺序丢资格。离开该回合的 wait/return 不因此变成未来唤醒授权，停止/目标版本与执行授权继续重检。 |
| `return.replyRef` / `IntentReplyBinding` / `ReplyGoalScope` | query 返回宿主预留引用，正式 `post_reply` ID 由原 Composer 生成；宿主从当前判断和真实引用结果绑定实际 canonical 消息。同一回复可关联多个明确目标，但各目标分别 CAS 关闭，不借用对方子任务范围。旧目标版本的回复不能关闭新目标。 |
| 原生 yield 的判断承接 | 只有宿主恢复了匹配渠道、模型与 family 的完整原生检查点，且保护的上一 outcome 确为 yielded、非失败/停止/预算阻塞，当前 work/goal/decision 仍一致时，才在内部 job 保存 `resumedIntentDecisionRef`。后续切片可沿这份判断绑定实际回复，仍由当前核验、真实签收与 kernel 关闭；不重写模型判断或生成新执行权限。普通安静 wake、目标修订、模型切换及失败恢复不能借用该标记。TUI 原生现场携带 providerId/model/modelFamily，由原 encoder Adapter 保留格式，缺少可证明身份的旧现场不强行复用。 |
| 根核验与既有结果复用 | 首次准备交还时复用可证明覆盖原输入/要求的当前核验，否则调用原只读 Verifier seam；根要求/版本纳入请求身份，不复用子阶段的 native checkpoint。已经交付的同版本结果可在安静 wake 复用；新用户问题仍需自己的回复。公开文本、model assessment 或新 Evidence ID 均不能替代核验/签收。 |
| `ReplyDeliveryReceipt` | canonical commit、settlement started/failed/applied、原 `reply_delivered` 分列。原综合回执与 recovered 语义保持。签收 Promise 在进程内唯一；不持有主 Bot 执行 lane；重启读取原幂等 acceptance/memory/handoff 事实后补偿，不重放 Worker。退避由原日志保存，按 work 保序并隔离独立输入。 |
| deferred / aggregate | `reply_deferred/held` 在原 delivery bucket 保存小结待办，先日志后原 digest queue；稳定 ID 去重覆盖 hold 两侧中断。实际小结投递并签收后才记录 `reply_aggregated` 和 canonical aggregate receipt，原暂存消息不伪装成已公开。绑定从 journal 原件导出，digest 文件只提供引用；来源失效留失效事实并重新读取结果，不强制打断用户。 |
| 故障与进展 | 单 work 无进展/非法判断不进入 Provider 熔断；原熔断文件按已配置渠道分域，不自动换渠道。物理故障代码须匹配本 work 的实际 recovery/失败 transition；无方法可选用 `intent_decision_unresolved` 表达认知阻塞，不冒充系统故障。有活跃工作或真人门则应等待。`progress-policy` 共用 observed/admitted/advanced、稳定错误类别和对象身份；查询/失败的对象身份须来自宿主返回事实，不能靠请求参数里的新 ID、reason、时间、随机回执或换执行者续租。没有新增默认累计步数上限。 |
| `DecisionFrame` | 原 L7 roster Source 消费只读投影，默认上限 24 KB；当前事件相关旧目标优先，保留身份、源版本、剩余要求、真实问题、unknown 与动作拒绝原因；历史 passed 与当前 review.current 分开。sessions/inputs/诊断可分页或按 ID 回查，明确遗漏；历史输入读取不变成新授权，不返回原始附件内容、凭据或私有思考。 |

领域实现位于 `packages/runtime-node/src/project-agent/intent-coordination-kernel.mjs`、`intent-lifecycle.mjs`、`intent-reply-bindings.mjs`、`runner-reply-lifecycle.mjs`、`decision-frame.mjs`、`progress-policy.mjs`；Runner/Coordinator 仅接入结论与现场。类型仍在 Protocol，L1 放稳定规则，Provider encoder、权限与 Evidence 链不改归属。

共享 workspace 日志的自动恢复按 canonical work 的 parentConversationId 归属过滤：当前 Bot 不领取其他 Bot 的输入、工作、事件、重试预约或回复补偿。可证明归属的 legacy 记录继续兼容；未知归属不从文本猜测。原生 workspace 小结定时器沿既有宿主装配绑定目标会话；若聚合引用包含已知其他 Bot 原件，保留待办并返回 scope conflict，不偷移责任或清空对方待办。这不是新增跨 Bot 权限或自动迁移授权。

格式 8 是这四包的完整特性门槛；发布前不将包间提交当作独立可部署版本，也不向包间旧提交降级接管活跃数据。正式旧 reader/writer（本基线格式 2–6）拒绝新格式；重建保留 durable head/manifest 的最高门槛。历史 digest 接收可证明的旧写法，新判断使用字段顺序无关的内容摘要；无法证等时拒绝重放。ADR116 格式 7 仍未集成，资源等待返回明确 Adapter 不可用，不能宣称已具备资源账本或 Session Control 新能力。


## 15. RC32 与 ADR116 的组合契约（2026-11-01，实施中）

用户要求全部待合并 PR 共同发版，因此必须把 ADR116 的格式 7 与本决策的格式 8 串行整合后验证，不把两个分支的独立自测相加当作发布验收。

- 组合实现采用完整特性门槛 **9**，保留已有 2–8 的历史读取和各自真实 reducer，并在原 journal/派生存储同时承接 Session Control 与 Intent 记录。开始写入组合语义前按既有 head/manifest/reader/writer/executor 机制提升最低版本；重建保留最高门槛。旧 7 或独立 8 writer/executor 不得接管新的活跃格式 9 数据，不能仅把支持版本数字调大而缺 reducer。
- 旧格式 7 的 Session Control/资源账本恢复与旧格式 8 的 Intent 恢复各按原事实成立。8 在独立分支不含设备资源账本语义，不能因 `minimumWriter >= 7` 就推断它已建立资源存储；首次组合准入仍由 ADR116 的 legacy 导入/停稳/unknown 保护完成。真正已启用资源契约的 7/9 若缺失其设备账本，继续 fail closed，不通过重建空账本解锁。
- 根目标关闭、子任务签收和资源释放仍分别取原真源。Intent Adapter 不代行停止屏障，不从 return/fulfilled 推导 released；Session Control 也不从停稳推导目标已满足。保留旧执行代次、未知调用、Provider 句柄、用户暂停/取消、预算与原授权边界。
- 本轮不扩展模型可提交的资源等待引用：尚无正式 Adapter 的 `wait.resource` 仍明确返回不可用；已排队会话沿现有 session/资源事实与宿主事件继续。存在设备资源账本不等于模型可自行构造 claim 或资源资格，不能将此未开放入口包装为已实现能力。
- 验证必须覆盖 7/8 记录重开、9 的最低门槛/manifest 丢失重建/旧 writer 拒绝、控制与意图记录共存，以及最终组合候选的全量 build/test/type/architecture/IPC 和产品回归。组合源码已实现于代码 PR253：保留两类 reducer 与索引桶，显式写入格式 9；历史 7/8 重开、两类记录共存、manifest 丢失及 head 高于 manifest 的恢复用例已通过。格式 8 不被误认为已有资源账本，7/9 缺账本仍拒绝准入。最终组合版本的发布验收尚未完成，结果另记于发布回执；不修改个人数据或当前实例。

RC32 初始化顺序补修（代码 PR253，`b03a4711`）：任何首次启用联合格式 9 的写入口先通过既有 ExecutionResources 建立并检查设备账本，再发布协调格式门槛。Intent/回复写入不创建 claim 或执行授权；真正准入仍由原 Scheduler 的 legacy 导入和资源契约负责。真实格式 7 夹具包含账本，独立格式 8 可以没有账本；已激活 7/9 的账本遗失继续拒绝新建空库。首次 Intent 后账本 revision 为 0 且无 claim，删除账本并重开后拒绝继续准入、保留可读意图历史的用例通过；44 项相关桌面/意图/控制用例和 24 项意图/资源用例通过。它们是组合修复过程证据，最终 RC 联合候选另行全量验证。
