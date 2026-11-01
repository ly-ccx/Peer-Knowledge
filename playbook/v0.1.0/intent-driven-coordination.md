# 意图驱动协调与目标闭环：四个工作包

创建时间：2026-11-01
最后更新：2026-11-01

状态：Accepted / 四包源码实施与自测完成（交付分支，2026-11-01）。[实际回执](intent-driven-coordination-self-test.md) 分列源码检查、一次文件复测与未执行的真实模型/发布验收。用户的后续授权覆盖代码实现与自测，不包含安装、发布或自动合并。唯一架构决策入口：[ADR 117](../../knowledge/decisions/117-intent-driven-coordination-and-goal-closure.md)。

## 1. 目标、基线与顺序

目标：主 Bot 持续持有用户原始目标，能在调查、执行、核验和交付之间自主推进；只有有来源的目标完成/撤回才能结清根责任。独立任务不被局部故障拖住。

源码审查基线 Peer-Agent `5dffbd4b4ced0bb841c9e879debd50b8bb081b9c`；知识整合基线 `10707b62945cf47d7080cfb9161b166f07ffae23`。它们是定位依据，不是实施冻结或验收候选。实际实施从届时已整合主线建立隔离分支，重新核对符号、协议版本和在途改动；保护其他工作树、生产数据及运行实例。

| 工作包 | 级别/规模 | 前置 | 主要交付 |
| --- | --- | --- | --- |
| IC-01 意图与责任契约 | A / M | ADR 117 批准实施；完成主线/版本/冲突核对 | Protocol、纯 kernel/reducer、追加式存储契约及兼容；不激活新关闭语义 |
| IC-02 统一判断与目标收尾 | A/B / L | IC-01 已在交付分支提交推送并交接 | 主 Bot 处置、原目标覆盖、持续承接与 typed 关闭；事实视图最小可用接入 |
| IC-03 交付与失败隔离 | A/B / L | IC-02 已在交付分支提交推送并交接 | 消息/签收独立回执、按 work 补偿调度及故障范围 |
| IC-04 决策事实与进展治理 | A/B / L | IC-03 已在交付分支提交推送并交接 | 完整 DecisionFrame、统一进展观察、全链路用例及最终验收准备 |

依赖严格为 **IC-01 → IC-02 → IC-03 → IC-04**；四包在同一隔离交付分支依次整合、独立提交推送与交接，前包提交后方可进入后包，不自动合并发布分支。最终验收是 IC-04 的退出后门禁，不另设第五个实现包。

开工必读：代码仓 AGENTS.md；本仓产品北极星、架构治理；ADR 117；ADR 88/91/93/94/95/110/111/112/113；[执行手册](../project-agent-implementation-handbook.md)。旧卡中的日常测试退出规则服从当前代码仓 Validation Scope。

在途 ADR 116/SC 仅在实施时核实合入与授权状态。IC 不实现第二套 Session Control 或资源账本；若其已合入，按正式 Interface 适配。共享 schema、版本门槛、Supervisor 与停止/恢复 seam 必须串行整合，不能从未提交草案声称已获得能力。

## 2. 全包共同边界

- 能力链、主 Bot 只读、Bot 当前权限、真实人工门、预算、unknown 和原生 checkpoint 不变；模型判断不成为权限或 Evidence。
- 复用 Conversation、GoalPlan、coordination-v2 journal/blob/派生索引；不新增任务/意图/交付数据库或本机目录。
- 协议对象在 protocol；领域规则在共享 kernel；Desktop/TUI 只装配和消费。不向 Runner、Supervisor、main 或大 React Surface 堆业务。
- 每包必须增加有意义的契约/恢复用例并审阅，但日常只做源码、内容和 diff 审阅。未运行不得填 passed；提前执行需用户对当前任务明确要求。
- 新 UI 不是本方案交付前提。确需改变投影/文案/恢复入口时先读体验、motion、transition 标准，更新相关矩阵；产品回归留到发布门禁。
- 代码提交与知识提交分别归属两仓，commit 后同轮 push；不把知识复制到代码仓，不自动合并 PR 或纳入新版本。

## 3. IC-01：意图与责任契约

**目标**：把输入解释、原目标、覆盖判断和下一步责任表达为可校验、可恢复的既有协调记录；与子任务验收分层。

**必读**：ADR 117 §3—6、§9—11；ADR 91 来源/CAS/epoch；ADR 111 最新监督存储门槛；ADR 113 引用保留与内容寻址。

**允许修改（相对 Peer-Agent）**：

- `packages/protocol/src/delegation-coordination.ts`、必要的既有 delegation/agent-supervision 类型及出口、邻近用例。
- `packages/runtime-node/src/project-agent/coordination-kernel.mjs`、`work-coordination.mjs`、`work-delta.mjs`、现有协调 store/index/schema 的必要适配及邻近用例。
- 必需的深 kernel 模块可新增，须证明承接了校验/转换/重放职责；不得只做转发。存储 scope 变化才涉及 `data-store.mjs` 登记。

**实现要点**：

1. 冻结 InputDisposition、IntentInterpretation、GoalCoverageAssessment、WorkDisposition 与来源/引用身份。每条 input 单独有处置；跨 work 引用保留范围。
2. 区分 expectedWorkRevision、goalRevision、operationId、executionEpoch；同 ID 同内容幂等、异内容拒绝。模型不能指定宿主 lifecycle、版本或权限。
3. 冻结 `coordinate_work` query/assessment 扩展及 DecisionFrame 公共形状；无子任务 work 可查询。此包不提前暴露未实现的模型动作。
4. journal 先写事实及待办，后执行 adapter；派生索引可重建。活跃责任/待交付/恢复引用列入既有保留根。
5. 按实际最新格式登记 minimumReader/Writer/Executor，不预占数字，不降低其他包门槛；旧 writer 拒绝新事实。legacy 只追加可证明的来源，不重开历史完成记录。

**必须补用例**：身份/跨 Bot/来源伪造、每输入处置、同 ID 冲突、双 CAS、语义判断非授权、阶段签收非根完成、缺覆盖/旧版本拒绝关闭、日志重放/索引丢失、写入中断、blob 引用保留、旧 reader/writer/manifest 恢复门槛。

**退出条件**：类型、真值归属、状态转换和兼容矩阵完整；新记录可经原存储读取/重放；旧运行分支行为保持兼容，新关闭语义尚未启用；必要用例已编写并审阅。

**交接物**：精确代码提交、接口/事件清单、版本登记、兼容开关/准入条件、未运行检查、IC-02 可调用的纯 kernel 入口。

## 4. IC-02：统一判断与目标收尾

**目标**：一次意图中的调查结果可以签收，原目标仍自动推进；回合结束留下明确责任去向。

**必读**：ADR 117 §4—6；ADR 93/110 的 followUp；ADR 111 的问题承接、回复交付和已返回结果返修。

**允许修改**：

- `project-agent/runner-coordination.mjs`、`coordination-lifecycle.mjs`、`repair-ownership.mjs`、`repair-custody.mjs`、`continuation-custody.mjs`、`reported-wait.mjs` 及邻近用例（均在 `packages/runtime-node/src/`）。
- 既有 Delegation Provider/tool-specs/描述源及生成描述、`agent-turn-plan.mjs`、必要 kernel/Protocol；`runner.mjs` 只接内核结论与保存现场。
- 原核验/交付 seam 的目标覆盖绑定及只读 verifier adapter；`packages/system-context/src/sources/project-agent-source.mjs`、`project-roster-source.mjs` 和现有资源文本。
- Desktop/TUI 的现有 turn executor 仅作必要接线；Supervisor 不新增语义业务。

**实现要点**：

1. 主 Bot 在原回合内解释输入，讨论/问答轻量结束，持续委托持久记录。不增加独立分类模型或每轮核验。
2. `continue/wait/return/blocked_system/withdraw` 提交到同一 kernel；公开回复只表示表达。无合法处置时按原预算有限修正，再明确阻塞；原生 yield 继续保存原责任，不强迫输出总结。
3. 对新契约 work 移除“关联 session 全 accepted/cancelled 即 fulfilled”的充分条件；根据当前目标覆盖、真实交付/签收及无未决义务提交唯一关闭回执。
4. 先签收调查、后续再安排实现时仍持有原目标资格。已消费事件的后续由持久待办/决定引用承接，不伪造新用户消息，不放宽普通 wake 范围。
5. 复用已有核验覆盖；不足时在准备交还前走原只读复核 seam，保持版本、模型、预算、权限及 Evidence 规则。子任务已签收可以退出子列表，根责任不伪装成该子任务重新 running。
6. 保留工作 Agent 局部自治；真实工作问题先由父 Bot 处理。用户修订、停止、unknown 与人工门优先；同一当前目标最多一个有效协调承接方。
7. 提供足够支持本包的最小 DecisionFrame；提交时回读当前状态，不能只根据回合开始时空 roster 放行无源任务结果 fallback。

**必须补用例**：原委托含实现的“调查 accepted → 下一 wake 实现”；只要方案不写入；轻量问答不建 GoalPlan；一次输入影响两个明确目标；查询不新开任务；augment/revise/replace 的区别；子结果均结束但目标未覆盖；撤回不算 fulfilled；迟到结果/旧核验不关闭新版本；父答不消费人工门；原生 yield/重启保留同一责任；无处置/伪完成不能静默关闭；同事件不重复派发。

**退出条件**：从输入到目标关闭只有一个结构化处置出口；上述阶段推进不依赖工具调用顺序；原恢复分支仍可读旧记录但不签发新权限；当前 UI followUp 来源不变；必要用例已编写并审阅。

**交接物**：目标/回合/子任务责任映射、完整时序、授权来源与待办身份、复用/新增核验条件、legacy 行为、未运行检查及 IC-03 的交付依赖。

## 5. IC-03：交付与失败隔离

**目标**：单项结果的签收补偿或局部判断失败，不阻止同 Bot 独立输入；故障不能导致假交付或重复副作用。

**必读**：ADR 117 §7、§10；ADR 94 recovered/silentWait；ADR 95 的分支失败/显式预算；ADR 111 的回复来源和恢复。

**允许修改**：`reply-delivery.mjs`、`reply-failure-facts.mjs`、`runner-coordination.mjs`、`recovery-policy.mjs`、`circuit-breaker.mjs`、既有 work reducer/store 与邻近用例；Runner pump/kick/重试预约仅调度适配；已有 Provider/模型健康 seam、原签收回调的窄 adapter。必要 Protocol 回执字段属于本包 A 级范围。

**实现要点**：

1. 原 journal 分别记录 canonical 消息提交与签收补偿，保留旧 `reply_delivered` 综合条件及 recovered 判定；消息存在不等于 accepted。
2. 同 work 维持必要有序性，补偿按稳定 ID、源版本和退避调度。移除单个 pending delivery 对整个 pump 的阻塞；新独立输入与其他有效待办保有执行机会。
3. 无进展/非法处置限制问题 work/attempt；Provider 真实不可用约束依赖该渠道的请求；租约/权威存储故障仍阻止相关宿主。复用现有健康与模型路由，不建第二套账号回退或自动换配置。
4. 签收调用失败、返回未知和来源失效分别保留回执；先查既有 acceptance/结果事实再补偿，不重放 Worker 或外部写入。消息已经公开则保留历史及更新说明。
5. 有未知结果时只解除无冲突工作的调度，不擅自释放相关资源保护。消费已合入的 Session Control/Resource Admission Interface，未合入时明确 Adapter 限制。

**必须补用例**：消息提交前/后、签收前/后、综合回执前 crash；持续失败的 accept 回调期间新独立问题得到准入；同 work 顺序与跨 work 公平；来源变更失效；重复提交无重复回复/签收；局部无进展不熔断另一目标；同 Provider 真故障仍限流；无可用模型与硬预算不额外通知请求；旧 prepared/delivered/recovered 可读；租约丢失/日志损坏不继续写入。

**退出条件**：故障影响范围可从回执解释；补偿没有全项目队首阻塞；原错误历史、签收及 unknown 语义不变；必要用例已编写并审阅。

**交接物**：交付/签收状态表、重试及崩溃窗口、旧回执映射、Provider/工作/宿主故障边界、当前限制与未运行检查。

## 6. IC-04：决策事实与进展治理

**目标**：主 Bot 在有界事实视图中选择下一步；无进展保护使用稳定事实，同时允许有依据的探索。

**必读**：ADR 117 §8—12；ADR 95/112；当前 System Context 与模型路由合同。

**允许修改**：`project-facts.mjs`、`event-mapper.mjs`、`watchdog.mjs`、`continuation-policy.mjs`、协调失败归一化及其邻近用例；现有 roster/工作事实 Source、Protocol 投影与 shared exports；可新增承接真实选择/归一化职责的 `decision-frame` 或 `progress-policy` 深 Module。Runner/Supervisor 只替换消费端，不新增一套中心策略。

**实现要点**：

1. DecisionFrame 保留当前意图、版本、剩余要求、相关结果/问题、payload 错误类别、事件身份、真实人类门、unknown 和合法动作/拒绝原因。
2. 按当前输入/事件作用域选择，超过 24 个 session 时仍保留所涉旧目标；截断有明确事实和回查/分页引用。不能全量回放历史、注入私有思考、凭据或外部指令。
3. 只经原 L7 Source 准入，L1 保持稳定规则。视图过期后执行仍重检；既有 query 为恢复入口，不让“可用动作”成为第二份权限。
4. 统一新观察、已接纳动作、目标推进的记录。失败 key 不含自由 reason 表述；恢复/换人/重启不清零，合法新方法有事实依据。
5. 回合、操作、watchdog 共同消费事实而分别处理切片/准入/停滞；保留无默认累计硬上限与真实费用，不用 maxIntentSteps 限制正常推进。
6. 清理被新内核替代的重复收尾逻辑和提示词补丁，保留稳定规则及可诊断错误；不将重构扩大为整个聊天/GoalRunner 重写。

**必须补用例**：payload 失败明细进入有界事实视图；缺源/截断可回查；旧目标不被无关新任务挤出；跨 Bot 与秘密排除；reason/UUID/时间/重启不刷新失败；新调查事实可推进；重复只读观察不续租；同 goal 新修订保留实际用量；无变化零模型轮询；显式预算优先；四包组合恢复和目标关闭唯一性。

**退出条件**：可从一个 DecisionFrame 和一条处置记录解释“为什么做下一步/为什么等/为什么交还”；没有并行维护的第二份任务/权限/进展真值；四包必要用例齐备并审阅；所有尚未运行的验证明确列出。

## 7. 最终验收标准（届时执行）

| 故事 | 必须证明的结果 |
| --- | --- |
| A1 先调查，能修就修 | 调查阶段签收后根责任仍 active；没有新用户消息也能唯一启动原范围修复；最终才 fulfilled |
| A2 只分析/只给方案 | 不自动写入或形成执行委托；普通问答不创建 GoalPlan、无额外分类请求 |
| A3 用户补充/纠正/独立新任务 | 来源逐条可查；相关目标及时修订，旧 epoch 不开始失效操作，无关任务继续 |
| A4 工作 Agent 问题和技术失败 | 父 Bot 优先处理；真实权限/人工确认未被 Agent 答复消费；普通方法无需人反复说继续 |
| A5 签收补偿持续失败 | 不伪造 accepted/recovered；独立输入在补偿尚未成功前获得准入；无重复副作用 |
| A6 无进展与探索 | 改写 reason、重启、换执行者不清零；有依据的替代方法可推进；不因单 work 故障封锁整个 Bot |
| A7 崩溃与迟到 | 各持久步骤可恢复；零丢失已接纳输入、零重复已知副作用；旧结果不关闭新目标 |
| A8 意图与签收分层 | 子任务 accepted 可退出子列表，根剩余要求仍有承接；根关闭不伪造子任务签收或停止回执 |
| A9 事实视图与上下文 | 相关事件身份/错误不丢；截断可见且可检索；外部内容不提升指令，无跨 Bot 材料 |
| A10 版本与回滚 | 旧 writer 拒绝新格式；重建保留最高门槛；旧已完成记录不重开；未知调用不重放 |

验收分层：先协议/纯 kernel 与生产 Module 集成，再隔离数据根的真实模型多阶段委托、插话、父子问答、失败和重启；UI 有变化时完成标准产品包全图人工智能审阅与 verify；最后安装包/升级和跨宿主适配。分别报告受控认知、真实模型、源码/安装版、平台、辅助技术及独立审阅边界。

可量化底线：每条已接纳输入有来源与处置；每个当前目标最多一个有效协调承接者；根关闭同版本最多一次；失效 epoch 新派发为零；同一稳定操作无重复已知副作用；无变化不调用模型。记录新输入准入、阶段签收、后续派发、交付/签收和根关闭时间，不凭空承诺固定响应秒数。

最初方案文档阶段仅做内容/diff 审阅；后续已明确授权四包实施与自测，实际结果见[自测回执](intent-driven-coordination-self-test.md)。其他普通实施仍补用例但不自动运行；发布版本/RC 时按代码仓 AGENTS.md 先清点并审阅合入所有开放 PR，冻结最终组合候选后执行完整 build/test/type/architecture/IPC 与完整产品回归，推 tag 前再次确认开放 PR 为空。用户另行明确要求提前验证时，仅记录实际授权与覆盖，不把早期小候选结果当最终发布验收。

## 8. 每包交接与当前记录

每包交接必须列出：代码/知识提交、Interface 与职责变化、来源和版本、幂等/恢复/回滚、实际改动范围及偏差、已补用例、已运行和未运行检查、下一包真实前置及阻塞。不能以“代码已写”或旧 CI 声称验收通过。

2026-11-01：ADR 117、四包任务卡及关联 ADR 的 Proposed 衔接说明已编写；只做内容/diff 审阅。四包均未开始，未改变 Peer-Agent 代码、运行实例、生产任务或发布安排。

2026-11-01 后续授权：用户要求四包全部实施并自测，覆盖本方案必要验证；历史“仅文档”记录保留。IC-01 实施基线、版本冻结和职责见 ADR117 §13。验证结果另行追加，不预填通过。

### IC-01 实施交接（2026-11-01）

代码提交 `420d90f0`（`codex/adr117-intent-coordination`）：Protocol 新增意图、逐输入处置、覆盖、责任处置、关闭和 DecisionFrame 契约；纯 intent kernel 校验输入/事件/持久决定来源、Bot 范围、work/goal 双 CAS、操作幂等与关闭条件。通过原 coordination-v2 的 journal/blob 与 objects 派生索引持久化 `intent_assessed` / `intent_closed`，不新增目录、数据库或权限真值。关闭由宿主核对真实交付、当前版本核验及无未决义务；模型覆盖陈述本身不构成核验。

新事实 minimumReader/Writer/Executor 为 8；本分支支持 2–6 与 8，显式拒绝尚未集成的 ADR116 格式 7。后续合并必须整合两套 reducer，不因数字较大声称兼容。启用新事实前先持久升级 head/manifest；索引重建保留最高门槛，legacy writer 保持拒写。当前尚未接入模型动作或改变既有 runtime 关闭行为，交给 IC-02。

用户明确授权自测。本机 Node 25.9.0：protocol/runtime-core/runtime-sdk/runtime-node 依赖链构建通过；新 kernel/生产存储恢复与原 v2 存储用例共 20 项通过，新用例单独复核 4 项通过；`git diff --check` 通过。覆盖来源伪造、双版本、同 ID 冲突、持久继续来源、阶段未完成、交付/核验不足、索引丢失、版本保留/拒写及既有存储崩溃窗口。未执行真实模型、多阶段 Runner、安装包/升级、UI 或跨平台验收；上述不是发布验收。

### IC-02 实施交接（2026-11-01）

代码提交 `ab84f7e8`：原 `coordinate_work` 新增 work 查询与 assess，宿主签发 operationId；新委托带 `intentSchemaVersion=1`，沿用格式 8，旧 mandate 保持历史语义。新增 intent-lifecycle 深 Module 承接逐输入解释、版本化 wait/continue/return/withdraw 及根核验、关闭；Runner 只消费处置、保存恢复现场和给予一次有预算的纠正机会。无委托讨论不强制创建 GoalPlan 或意图记录。阶段签收与根关闭分层；无新事件的下一阶段使用已持久 continue 的决定来源，不能把旧用户输入伪装为新授权。停止、人工门、unknown 和签收权限不变。

`intent_reviewed` 通过原只读 verifier 运行与上下文 adapter 生成，不新增分类/逐轮 reviewer。只有当前核验确实覆盖原输入和要求时复用；否则在交还前核验 canonical 输入与全部根要求。覆盖陈述、公开回复和工具操作已登记均不等于完成；关闭须同时绑定当前核验及 delivered 综合回执。L1 添加稳定规则，L7 原 roster Source 接入最小事实 frame，完整有界选择与诊断在 IC-04。

Node 25.9.0 依赖链构建通过。新组合用例证明“调查 accepted → 消费事件 → 持久继续 → 无新用户输入派发实现 → 实际交付/签收后唯一根关闭”，并验证无子任务查询、伪造 wait、轻量讨论和核验上下文。连同原 kernel/lifecycle/Runner/回合及 Context 用例首轮 85 项通过；补强 journal 关闭证明后复核 64 项通过；源码/diff 审阅通过。核验认知使用受控 port，尚未真实模型或安装版验收。IC-03 前置已就绪；待交付全局阻塞和局部失败计入全局熔断仍留给下一包，未宣称已修复。

### IC-03 实施交接（2026-11-01）

代码提交 `35aa41fd`：`ReplyDeliveryReceipt` 与原 journal 新增 `reply_committed`、`reply_settlement_started/failed`、`reply_settled`；只有综合条件满足才写原 `reply_delivered`，recovered 仍消费这个综合事实。受保护 v2 使用格式 8；未启用 owned writer fence 的旧 v2 及 legacy 保持原交付映射，不能在无 fence 时偷开新格式。

交付 Module 按稳定 message/settlement ID 保序，独立记录错误、阶段与持久 retryAt。待签收 Promise 在进程内保留唯一实例，长等待不占主 Bot 执行 lane；完成后回到既有 work 恢复 seam。重启只经原幂等宿主签收回调读取已发生的 acceptance/memory/handoff 事实后补偿，不重放 Worker。单 work 的失败与 Provider/租约/权威日志故障分开，原熔断文件增加配置渠道作用域，不建第二套路由或自动换模型。原停止/unknown/资源保护保持；ADR116 的资源适配尚未整合。

Node 25.9.0 构建通过；Runner、原连续性/存储/熔断及新隔离组合 74 项通过，核验继续身份及既有 recheck 复核 15 项通过。新用例覆盖持续失败和一直未返回的签收期间独立输入准入、同 work 保序、跨 work 推进、退避重建、canonical/acceptance/settled 三个中断窗口、租约丢失保留 pending、局部失败不熔断、配置渠道切换不丢输入及旧渠道失败持久化。中断通过受控故障注入；尚未声明真实模型、安装包、跨平台或发布验收通过。审阅补强了根核验请求身份：根要求/版本纳入 native checkpoint 来源，避免错误复用子阶段核验现场。IC-04 前置已就绪。


### IC-04 实施交接（2026-11-01）

代码提交 `3c7ef152`，已推送交付分支；精确 tree/commit 与结果统一见[自测回执](intent-driven-coordination-self-test.md)。新增 DecisionFrame、progress-policy、intent-reply-bindings 与 runner-reply-lifecycle 深 Module：分别承接有界事实选择和回查、稳定进展/错误归一化、真实回复与原目标关系、交付后的责任和小结恢复。Runner/Coordinator 只接结论和现场；未新增 Renderer 状态、数据库、能力执行入口或 Context Source。

DecisionFrame 默认 24 KB，优先当前事件涉及的旧目标，保留剩余要求、错误 payload、真实问题、unknown、动作及拒绝原因；sessions/输入处置/长输入和事件可按版本分页或回查。进展区分 observed/admitted/advanced，宿主返回的对象身份与稳定错误类别参与判断，请求参数里的新 ID、reason、UUID、时间、换执行者或重启不刷新失败。模型只能引用本 work 的物理失败事实；认知阻塞单独表达，不假造 Provider 故障。

组合审阅补强实际 Composer 回复绑定、多根分别 CAS、旧结果的同目标复用、新用户问题必须回答、暂存小结的原件回执与来源失效、跨 Bot 的工作/输入/事件/交付/重试归属。抽出交付后生命周期，使原 Coordinator 不继续堆积业务。

TUI 真实组合用例暴露并修正了原生现场身份适配及判断跨 yield 的承接：仅在匹配模型、当前 work/goal/decision 和可证明的保护检查点上延续；新语义推理、目标修订、失败或模型切换需要自己的判断。真实交付和 root closure 仍经原事实链，不将 native continuation 变成未来 wake 的执行授权。用例经过实际文件读取、Evidence、子任务核验、一次根目标核验、回复/签收及 fulfilled，认知来源仍为受控 Provider。

完整构建、类型和架构/IPC 检查通过，全部测试脚本已执行；最终候选 Desktop 一项凭据 helper 超时按仓库规则独立复测一次通过，另报告 5 项跳过，详见回执。真实模型、安装版、跨平台、辅助技术、独立审阅和发布产品验收仍单列，不借源码自测补填通过。格式 7/ADR116 的 Session Control 与资源账本尚未整合，保持 §2 的正式接口交接要求。
