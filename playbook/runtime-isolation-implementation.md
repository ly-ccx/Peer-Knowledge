# 本地运行时隔离实施包

创建时间：2026-11-11
最后更新：2026-11-13
状态：待 ADR128 评审的实施计划；没有产品实现已完成的暗示。

决策：[ADR128](../knowledge/decisions/128-local-runtime-isolation-and-bounded-query-contract.md)。总体设计：[逻辑 Module、依赖与完整链路](../knowledge/architecture/local-agent-system-blueprint.md)。调查：[响应性架构审查](../knowledge/experience/desktop-runtime-responsiveness-architecture-audit.md)。本文件不创建新的执行权限、生命周期策略或存储真源。

## 1. 固定交付规则

以步骤的实际入口/事实源/状态迁移为单位交付，不按“拆出几个文件”计数。每个阶段说明将退出的旧入口，必须覆盖正常、拒绝、失败、超时、取消、崩溃、迟到和已有状态恢复。实验数据使用隔离根；不安装/重启日用应用，不拿个人任务试错。

源码实现、确定性验证、真实模型/平台验证、已有状态恢复和发布验收分别登记。每天做阶段内验证；发布时才执行合并所有 PR 的完整候选与全产品门禁。Stage 之间不能用未经证实的“已流畅”作依赖。

## 2. 阶段与退出条件

按用户本轮要求，重构前先完成[详细设计v1](../knowledge/specifications/runtime-isolation/README.md)及其自上而下审查，不再把设计细节留到各阶段临时决定。总体方向、ADR接受、设计自审闭合、运行验收仍分别记录；把旧业务整体搬到新进程不满足RI-03。

| 阶段 | 入口与交付 | 主要既有 Module | 退出条件 |
|---|---|---|---|
| RI-00 基线与预算 | 将一次交互关联到 IPC 等待、处理、查询、Store 与发送；记录 15/30 秒周期；保留全部 >50ms 段及未知差值 | `slow-timer-probe`、IPC owner、既有 perf/product harness | 同一候选的可重现坏基线；测量自身成本单列；无 profiler 真实交互对照可重复 |
| RI-01 查询职责 | PendingGrant 空结果不 hydrate session；Badge/TaskSummary/Report 分离；Evidence 按键索引；移除列表中业务修复；覆盖runner roster微任务和预测snapshot初始准备对深列表的依赖 | Application Service、Bot Directory、SessionSupervisor、GoalPlanEvidence、TaskOverview、Runner Coordination、Input Prediction Host | 原坏基线先红；结果语义一致；scope/版本/字节/复杂度可观测；只读测试禁止 canonical 写；历史缺核验不补 passed；调度不以UI Query作执行事实，预测不扩大115准入 |
| RI-02 查询进程 | typed Query Protocol、独立 Query Service、订阅 cursor/失效、main 异步客户端；产品入口逐项迁移 | IPC/preload、Session Service、Query Scope、projection reader、interaction reader | 实际 Electron utility bridge；重建/排队/崩溃不回 main 扫全文；迟到/卸载/重连不污染窗口；生产不再调用旧同步查询 |
| RI-03 Runtime 进程 | 将已有本地引擎移入唯一执行宿主；命令/回执/流式协议与受限平台 Adapter；Desktop/TUI 共享入口 | composition root、TurnSink、AgentTurnExecutor、RuntimeHost、SessionControl、HostLease、Provider/Vault/Browser adapters | 无第二执行器/双 writer；模型与能力链一致；授权、取消、未知效果、断线/重启对账真实桥接通过 |
| RI-04 异常与兼容 | 每条已迁移路径的故障注入；旧数据/旧 writer/跨宿主/部分提交；删除过渡入口 | Store/fence、提交 worker、资源账本、输入/inbox、subscription owner | 原有卡住数据的隔离副本恢复；不抹 unknown/历史/Evidence；后续任务正常准入；兼容阻塞有明确受支持出口 |
| RI-05 产品与平台 | 最终同规模混合负载、真实模型、原生输入滚动、签名打包与平台验证 | existing product/perf/upgrade/release harness | 既有性能阈值不降；所有异常尖峰有归属；矩阵与产品包审查完成；独立性/未跑范围真实列出 |

每个阶段应拆成单一可审阅 PR；涉及新的权威数据、跨 Store 原子性或工具/权限政策时先回 ADR，而不是扩展当前卡。代码在 Peer-Agent，知识与门禁定义在 Peer-Knowledge。不要把整个 Runtime 移到新文件后宣称 RI-03 完成。

## 3. 迁移调用图

第一组覆盖：`useObligationGrants → list-obligation-grants`、`tray.refreshBadge → directory.list`、Bot list/get、当前任务和报告。它们覆盖本次已知放大；只能通过有界读模型迁到 Query Service，不能复制当前完整 Supervisor into query process 后停止优化。

第二组覆盖：会话窗口/preview/引用、搜索、TaskOverview、资源工作台、Memory/Objective/诊断等读取。已有 Session Service 契约直接保留；每组列清 canonical source、响应字节、索引键与损坏/重建结果。只搬第一页不能保留历史加载时的全量主线程回退。

第三组覆盖：用户输入、主 Bot/子 Agent 回合、工具执行、审批、停止、核验、交付、恢复、跨宿主接管和目标巡检。迁移复用相同 kernel、Provider 和 Store；OS 专属操作才桥回 main。命令不得使用展示读模型做最终授权。

过渡期间，未迁移写路径继续由原 owner 执行；已迁移项目由同一租约/fence 独占，不能 shadow 写。开关只能控制装配，不能让同一数据根两套宿主同时推进。

## 4. 可观察验收样本

| 目标 | 状态/事实来源 | 用户控制与恢复 | 验证 |
|---|---|---|---|
| 长历史下持续输入/读旧消息 | draft、scroll intent、InteractionWindow revision | IME 不提交半成品；上滚不被后台更新拖回 | 原生输入/滚轮、焦点、阅读锚点和连续帧 |
| 授权列表与角标及时准确 | 原审批/义务记录与 PendingGrant/Badge projection | 暂不可用可重试；陈旧决定 CAS 冲突后刷新 | 空列表/很多历史/审批变更/过期/断线 |
| 慢查询时仍能停止 | 原命令接收回执与 Session Control 屏障 | 明确区分收到请求、排空、停稳/unknown | 重建满载时取消、迟到结果、资源交接 |
| 宿主故障后继续工作 | 输入 operation/receipt、writer fence、canonical commit | 重连补读；未知效果进入既有对账 | kill Query/Runtime/worker，旧状态恢复后新任务准入 |
| 结果可信 | 原 Tool Result、Evidence、核验和 acceptance | 查询不产生成功；失败可定位和恢复 | 故障/重复提交/旧 epoch/磁盘满/无核验历史 |

触及产品状态时再更新对应交互/动效/过渡矩阵，静态设计不勾实施验收。当前未修改产品组件，不把矩阵改成“已实现”。

## 5. 固定测量矩阵

基线与候选必须记录 source HEAD/dirty、安装或源码、协议/索引版本、DPR/窗口、机器/平台、负载身份、缓存冷热、模型、采样器、运行时长与失败尝试。旧候选结果不自动沿用到新合并源。

- 空闲、15 秒轮询、30 秒巡检、事件风暴、200 Bot 冷/热、原历史规模、10 倍无关历史分别测量。
- 查询同时记录 queue/CPU/I/O/serialize/send 的时间、读取字节、hydrate/normalize 次数、返回字节与内存峰值；不能只量 Promise 入队时间。
- main、Runtime 控制、Query、worker 的 CPU/主循环分别记录，不能以 main CPU 降低代替总成本下降。
- 并行任务、核验返回、大历史终态提交、主动取消、服务重启、平台回调迟到必须在连续交互窗口中出现。
- 任何 >500ms 输入或主循环峰值仍失败；>50ms 应用工作段逐项解释；不删除失败样本，不更换较小数据，不用百分位通过掩盖 max。
- 合成负载、本地真实历史副本、真实模型任务、签名包和各平台分别给结果。未覆盖的项目保持未验证，不能交给用户安装试验后再判定。

## 6. 本轮收据

2026-11-14 余部与计量开关：[冻结设计](../knowledge/experience/runtime-isolation-ri00-fr1-observer-control-design.md)、[预算](evidence/runtime-isolation-ri00-fr1-observer-control-budget-20261114.json)、[结果与边界](../knowledge/experience/runtime-isolation-ri00-fr1-observer-controls.md)、[逐格收据](evidence/runtime-isolation-ri00-fr1-observer-control-results-20261114.json)。封存259µs拆为窗口前/后201/58，428µs拆为首子前/子间/末子后/无子58/167/58/145，均为原始与新增计量混合CPU。候选ae1e37ad通过一次4项资格与同源绑定，唯一真实Electron一读/零记录器完成24格ABBA/BAAB；空载拓扑B−A为+0.353/+0.2875ms，取栈+0.014/+0.049ms，编码−0.0875/−0.048ms且OFF返回漂移−0.051/−0.070ms，不能称无干扰或回减旧失败。所有格≤0.523ms只代表本操作控制未超2ms；记录器未重验、现场不准入、30–40ms机制未知。控制CPU17.728ms、完整子树4657.556ms、完整返回wall4201.305833ms、输出604288B，预算内；只读源未变，宿主退出/值释放/guard恢复，实际开发版未连接/重启。诊断owned47另手动开发版1共48，已知读CPU下界649752.173ms加旧未知，全部原失败保留、剩余额度0，不重构。

2026-11-14 真实Electron分段：[冻结设计](../knowledge/experience/runtime-isolation-ri00-fr1-electron-stage-design.md)、[预算](evidence/runtime-isolation-ri00-fr1-electron-stage-budget-20261114.json)、[启动前绑定](evidence/runtime-isolation-ri00-fr1-electron-stage-intake-20261114.json)、[实测与口径](../knowledge/experience/runtime-isolation-ri00-fr1-electron-stages.md)、[正式收据](evidence/runtime-isolation-ri00-fr1-electron-stage-results-20261114.json)。生产者fffc0576固定一宿主/2读/1根，219段、526时钟与27 self窗口精确重放；新计费2.367496ms=CPU2.187+plan wall0.180496，2ms门失败，CLI exit1，不能回填历史2.387。具名取栈CPU区段0.569、输出JSON/UTF8合计0.364、散列0.063ms（均含边界）；55原时钟wall上界0.268957、新边界242次0.275997，非精确时钟CPU、不重复加或扣。CPU余部0.259及粗簿记0.428保留未知。31项、离线3项及原件重放通过只代表计量完整；原方法/绑定/ACK/端口恢复，实际开发版未附着/未重启。读CPU2298.181ms、完整子树4171.590ms、wall3542.705750ms均在预算；诊断owned46另加手动开发版1，共47，已知读CPU下界647764.608ms加旧未知。无替换/Profiler/现场/重构，诊断剩余额度0。

2026-11-14 FR1记录器修理：[实际失败、三个受限诊断与停止边界](../knowledge/experience/runtime-isolation-ri00-fr1-recorder-repair.md)、[原件结果](evidence/runtime-isolation-ri00-fr1-repair-results-20261114.json)、[用户追加一槽及耗尽](evidence/runtime-isolation-ri00-fr1-compact-qualification-proposal-20261114.json)。eb1de652/d166929f/追加授权63bd98bd首根分别2.587551/2.336985/2.387123ms，均超2ms；当前24项及无损栈重放通过不冒领功能或现场资格。完整当前向量+脚本表使13次栈签名77437→10637B，仍不能换算CPU改善；普通Node时钟组仅约0.034ms/12，不能作为超额主因。原始失败/恢复/37条全ACK保留，功能余量0，未再加实例，当前开发版未附着/未重启，现场0读0参照。诊断owned45另加用户手动开发版1，共46受控启动；已知读CPU下界645466.427ms与旧C未知保留。下次须先取得真实宿主分段成本证据，当前不采现场、不重构。

2026-11-14 FR1实现与唯一功能槽：[失败分解及恢复边界](../knowledge/experience/runtime-isolation-ri00-fr1-qualification.md)、[启动前绑定](evidence/runtime-isolation-ri00-fr1-qualification-intake-20261114.json)、[正式失败收据](evidence/runtime-isolation-ri00-fr1-qualification-results-20261114.json)。候选39636570的20项单元/数据检查通过，记录器/触发控制器/同候选binder/现场入口已实现；唯一owned槽第一根自计2.253846ms超原2ms门而停止，CLI exit1，实际2/12次读，其余场景未到达，不追补。保守计费含0.215846ms计数wall上界，单列后线程CPU小段仍2.038ms，不能把计费当净增或产品根因。两批23条连续记录/当时父链核对，原方法/handlers/binding/ACK及端口恢复；完整租约/堵塞/Profiler/控制器宿主验证未完成。读CPU2462.825ms、完整子树3667.884ms及返回wall3085.534583ms保留；累计owned42、已知读CPU下界637581.814ms另加旧C未知。实际Peer未附着/未重启、零业务查询/参照；现场不准入，门和原失败不改写，机制未知，不重构。

2026-11-14 取证策略复审：[多轮失效结构与FR1现场首见证提案](../knowledge/experience/runtime-isolation-ri00-evidence-strategy.md)、[11份收据/8组返回审计](evidence/runtime-isolation-ri00-evidence-strategy-audit-20261114.json)、[新策略与预算](evidence/runtime-isolation-ri00-field-first-witness-plan-20261114.json)。CAD曾两个F0通过仍有6暖段/返回失败；最新8组raw返回GC锚点均变，target1/B Evidence−8.867而余部+8.170ms，不能当整查询改善。C2仅1入口/129包络，不能代表全操作覆盖。提出一现有进程/零参照零主动读/全前缀与当时父链/外部堵塞触发，30分钟现场含90秒清理、3分钟准备；无覆盖10分钟止，最多2事件、一次事后profile不补录首慢根。原15ms/G2及所有失败保持；新预算待实施执行、机制复现额度0，工具就绪不算根因。实际owned41及旧未知成本不变，无新采样/重构。

2026-11-14 校准排布执行封存：[同候选、实际位置/间隔及返回失败](../knowledge/experience/runtime-isolation-ri00-e3-calibration-placement.md)、[启动前绑定](evidence/runtime-isolation-ri00-e3-calibration-placement-execution-binding-20261114.json)、[正式收据](evidence/runtime-isolation-ri00-e3-calibration-placement-results-20261114.json)。候选55675ca5通过143项及唯一一次Node接缝；固定3宿主ABBA/BAAB完成184根/16块/57native，144真实间隔168.403～217.282ms、校准位置及全PMC重放通过，但返回超2ms，诊断invalid，CLI exit1。A两块未复现坏基线、B两块仍超15ms，五处原暖门失败保留，不能称排布支持或有效反证。读CPU83.054305秒、native1.273902秒、正式完整返回118.503626秒，预算未超；4专用端口/原件/队列/语义恢复。实际owned41、已知读CPU下界635.118989秒及旧C未知保留，无替换/Profiler/现场/重构。

2026-11-14 84根F0拆解：[五暖段、逐遍/余部与工作/速率及新校准排布诊断](../knowledge/experience/runtime-isolation-ri00-e3-order-variation.md)、[审计收据](evidence/runtime-isolation-ri00-e3-order-variation-results-20261114.json)、[新独立预算](evidence/runtime-isolation-ri00-e3-calibration-placement-budget-20261114.json)。3 target/2 conditioning，两个极差为先高后低，不能冒称形成；进入minor位置用户差5.740～13.951ms、同计数保留4.817～9.998ms，余部抵消1.387～7.009ms。全根指令−0.362554%～+0.718436%、T/C代理+1.010319%～+4.181081%，不归为物理频率或GC CPU。保留14个同GC时序配对，最大用户+13.650ms而root I仅+0.064111%。下一轮仅移动每块原3 SHA：块末/既有150ms窗前index2/5/8，诊断F0波动，不产生F0或现场资格，15ms逐块判定保持；新3槽/184根/57native/200秒读CPU/15分钟正式及120秒准备冻结不可直接执行。22项聚焦及84根CLI通过，本轮零新读/宿主/Profiler；实际38槽、552.064684秒已知下界及旧C未知保持，重构门不变。

2026-11-14 完整块顺序执行封存：[执行器/同候选绑定/Node失败与恢复/实际结果](../knowledge/experience/runtime-isolation-ri00-e3-pair-order.md)、[正式收据](evidence/runtime-isolation-ri00-e3-order-results-20261114.json)。修正候选1c053c56的119项聚焦及用户额外授权一次Node资格通过，原2MiB超帽失败保留；准备累计5885.057ms含旧失败。正式原3槽均使用，两target因F0暖极差21.155/15.738/19.053及6.902/20.205/15.598ms拒绝，84根/6块/18hash，处理0格，不能称完整ABBA/BAAB或顺序阴性。实际F0块边界/54间隔169.067～198.655ms、84原始外窗PMC和raw/归一化分量审计闭合；正式读体41.274209秒、wall57.599175秒，3宿主/5端口及源/语义/队列恢复通过。实际owned38、已知读CPU下界552.064684秒及旧C未知保留；无替换/Profiler/现场，重构门不变。

2026-11-14 244根封存拆解：[六处暖段及两处A返回、完整块顺序设计](../knowledge/experience/runtime-isolation-ri00-e3-cadence-variation.md)、[审计收据](evidence/runtime-isolation-ri00-e3-cadence-variation-results-20261114.json)、[新独立顺序预算](evidence/runtime-isolation-ri00-e3-pair-order-budget-20261114.json)。六极差中minor进入位置用户差10.362～12.866ms、同计数保留位置3.068～6.503ms且余部抵消，不能称全是GC CPU；两A漂移保留−2.622/+4.594ms，BAAB全根归一化+20.100ms含余部+15.842。参考同GC锚点另有用户+11.237ms与指令−0.050220%，不冒称稳定对照。下一轮仅换完整目标/条件块先后，两边150ms，固定ABBA/BAAB、raw主指标及全部原门/更严返回门；新3槽/244根/200秒读CPU/15分钟含完整241500ms预留floor已冻结不可直接运行，需同候选runner与接缝绑定。本轮零新读/宿主/Profiler，18项聚焦及244根CLI审计通过；实际35槽、510.790475秒已知下界及旧C未知不变，现场/机制与重构门不变。

2026-11-14 150/0固定三槽已封存：[完整结果与CPU/PMC口径](../knowledge/experience/runtime-isolation-ri00-e3-cadence.md)、[结果收据](evidence/runtime-isolation-ri00-e3-cadence-results-20261114.json)。3宿主/244根/四格ABBA及BAAB完整执行，Profiler0；实际间隔A/B中位171.391/20.808ms，处理检查通过。六块暖极差超15ms，A返回−2.622/+4.594ms超2ms，故不合格；四个用户B−A描述值+0.956/+3.347/+9.821/+6.818ms不用于因果或合格阴性。读体107.976秒、wall148.784秒，恢复与源/输出核对通过，无替换；累计owned35、已知读CPU下界510.790475秒及旧C未知保留，现场/机制证据门与重构冻结不变。

2026-11-14 150/0执行前绑定：[执行器、同候选数据与接缝验证](../knowledge/experience/runtime-isolation-ri00-e3-cadence.md)、[绑定收据](evidence/runtime-isolation-ri00-e3-cadence-binding-20261114.json)。98项聚焦测试及真实Node Inspector接缝通过，零Electron/零Profiler线上命令；原三宿主ABBA/BAAB与预算不变，正式结果随后封存。

2026-11-14 P2封存拆解：[两处暖极差、返回漂移及新单变量设计](../knowledge/experience/runtime-isolation-ri00-e3-p2-variation.md)、[审计收据](evidence/runtime-isolation-ri00-e3-p2-variation-results-20261114.json)、[150/0等待预算](evidence/runtime-isolation-ri00-e3-cadence-budget-20261114.json)。15.377/16.283ms已拆成逐遍与全根工作/速率记账；16.283ms对应全根指令仅+0.010757%，不等于物理频率证据。−2.1535ms用户漂移由target−2.1755、reference−0.022组成，内核变化相抵后合计+0.352ms，不能换门追认通过。下一轮零Profiler，仅target额外等待150/0，固定ABBA/BAAB、原F0/15ms/2ms门，3宿主/244根/200秒读CPU/15分钟预算已冻结但不可直接执行，需绑定runner候选；本轮零新读取/宿主，原P2失败与现场/机制门不变。

2026-11-14 P2：[返回覆盖、同候选P0B与固定三宿主实测](../knowledge/experience/runtime-isolation-ri00-e3-p2-return-audit.md)、[新预算](evidence/runtime-isolation-ri00-e3-p2-budget-20261114.json)、[结果收据](evidence/runtime-isolation-ri00-e3-p2-results-20261114.json)。覆盖40根/12hash/40等待/清理审计通过后，fce27eb2的P0B六场景通过，新预算再冻结；三宿主无替换、104根/69.614秒结束。target1原15.377ms入场拒绝；target2完整OFF/ON/OFF，1ms profile三时钟宽1.633ms/96遍最少15样本，结构门通过，但返回reference16.283ms与差额漂移2.1535ms拒绝性能资格。0.540ms开销公式不能当合格结果。所有owner/进程/端口/副本恢复，累计实际owned32；未采到现场形成或机制，不重构。

2026-11-14 P执行：[专用时钟/异常恢复与原P中止](../knowledge/experience/runtime-isolation-ri00-e3-p-profiler-qualification.md)、[机器收据](evidence/runtime-isolation-ri00-e3-p-results-20261114.json)。P0固定一个Node的6场景通过；P在首个OFF原门通过后被工具预算预测错误拒绝，2/3实际宿主、36根、零P profile，第三槽作废未补跑。冷预热2117.35ms被误乘40暖根，虚报128541ms预留；修正candidate仅离线回放/86聚焦测试，不改90秒或15/2ms门，不冒领原producer实测。累计实际owned Electron29、已知读CPU下界352.596809秒另加旧C未知。方法/队列/端口/8534副本恢复；未完成P，未捕到现场形成或机制，不重构。

2026-11-14续记：[384遍离线审计与C/D/E/M结果](../knowledge/experience/runtime-isolation-ri00-e3-controller-qualification.md)、[机器收据](evidence/runtime-isolation-ri00-e3-cdem-results-20261113.json)、[P独立冻结预算](evidence/runtime-isolation-ri00-e3-p-budget-20261113.json)。N未重跑或改判；C/D失败及C未知成本保留，E真实owned控制器F0/静默/首见证/F1/取消通过，M实际Peer一次随机端口附着、同栈装配/恢复且零业务读取通过。新7槽无替换，累计27；71聚焦测试通过，CLI封存384遍重放通过，CI无结果。P未执行、未启动现场窗口；仍缺现场同进程快到慢及机制复现，RI-00未闭合、重构未开始。

2026-11-13 N逐遍计数：[冻结方案及实际结果](../knowledge/experience/runtime-isolation-ri00-e3-pass-work.md)、[公开收据](evidence/runtime-isolation-ri00-e3-n-results-20261113.json)。固定3个owned启动已用完，32个ON生产根取得384遍指令/周期及root余部，与外部PMC核对通过，边界wall最大0.088ms；两target性能资格仍拒绝，未启Profiler或现场。21个按实际时间配对的同GC兼容点已能分开Evidence/余部新增工作与CPU变化，未重现旧2.49%或30–40ms形成。封存10ms profile的96逐遍窗口均缺足够样本。实际一次附着因固定端口错误失败；仅恢复实际随机端口，refusal且原进程存活，unknown主线程成本及46.239秒墙钟上界保留，修正候选不追补实际验证。42项聚焦测试/architecture/UI/diff通过不等于完整F控制器、实际装配或机制资格；RI-00与产品重构门不变。

2026-11-13 F0补充资格：[封存拆解与固定新预算](evidence/runtime-isolation-ri00-e3-f0-audit-20261113.json)、[入口producer实际资格](evidence/runtime-isolation-ri00-e3-entry-qualification-20261113.json)、[归档粒度对照](evidence/runtime-isolation-ri00-e3-drain-qualification-20261113.json)、[详细结论](../knowledge/experience/runtime-isolation-ri00-e3-qualification-followup.md)。18块115个兼容点揭示GC进入各调用边界的相位差及整根执行波动；同GC签名仍出现16.182ms差/整窗指令+2.49%，不能归因旧残差。K以精确8cfb68f0 sampler固定2 target+1参照，ABBA/BAAB不支持逐点排空的充分原因，不选绿点放行。A两个固定槽通过真实注册handler/Directory batch reader映射、原Promise/异常/父链/零重入和lease恢复；当前a59d067d纯信号策略以root/nested和root时钟修正盲区，7项测试及封存70包回放通过，没有追加产品调用。新增5个启动额度用完，K/A读体109.927044秒/墙钟216.951秒，全部owned及counter退出，源/输出/方法保持，F/R和产品重构仍未开始。原报告与新旧策略分别绑定，不修改原失败。

2026-11-13此前E3实际Q/H：[功能资格与原失败](evidence/runtime-isolation-ri00-e3-qualification-20261113.json)、[固定六实例原始拒绝](evidence/runtime-isolation-ri00-e3-order-20261113.json)、[完整结论与准入](../knowledge/experience/runtime-isolation-ri00-formation-e3.md#9-本轮实际qh收据与现场准入结论)。首见证/单槽/异常及失联恢复覆盖通过；原第二实例bootstrap失败保留，剩余第三固定槽补齐功能，不替换第二例。Q连探索恰好5个启动、读体35.260555秒。H候选8cfb68f0按C1/T1、T2/C2、C3/T3执行，7个Electron共129.967秒、读体98.029707秒；六个target均在F0暖段极差超过15ms，C1另有校准失配，因此有效配对0/3、顺序处理0次。不能称六次机制阴性；不补进程、不改门、不进入F。源/代码/输出一致、恢复完成、原始失败封存；当时现场入口/信号适配器仍未资格验证，后续分层验证见上一段，RI-00及重构继续冻结。收尾journal总帽修正候选18552dfa没有重跑或冒领H。

2026-11-13此前E3设计：[读取顺序、首见证、反事实及新增预算](../knowledge/experience/runtime-isolation-ri00-formation-e3.md)、[封存审计与两次owned预检](evidence/runtime-isolation-ri00-e3-design-audit-20261113.json)。先以固定3对检验已有快态后改变读取顺序是否造成持续残差，再按实际新入口取证；现场用全12遍单根信号、heap-free首见证和busy仲裁，原G2门不降。owned预检量出低频profiler启动约530ms主线程CPU，故现场不提前profile；提前形成栈只在owned反事实中采。H最多25分钟，F最多30分钟/2事件/6夹测；快态后8分钟无新exposure提前停，不续跑同类负窗口。该设计收据时E3尚未实现/启动，实际进展见上一段，不将设计状态当当前执行结果。

2026-11-13实际C2已收尾：[长时合同及证据总账](../knowledge/experience/runtime-isolation-ri00-passive-watch-v2.md#7-实际c2收尾与证据总账)、[129包络完整回执](evidence/runtime-isolation-ri00-passive-v2-c2-20261113.json)。同一应用进程129.03分钟、main主动读体12.253496秒且只在入场夹测；等待无追加业务读，零丢失/ACK差额，方法/binding/watchers/实际端口恢复。排除唯一可见诊断重入后128包络CPU中位434.0065ms，未触发自然慢化；不据此解释旧30–40ms，也不推断全程密集快态。8534内容文件+空fence目录与已回放C1 manifest完全相同；本轮不再开新宿主跑性能负例。累计预算不足自动接续，G2仍需真实形成及机制回放，RI-01/重构冻结。

2026-11-13长时观察审计：[C1封存与干预缺陷](../knowledge/experience/runtime-isolation-ri00-long-watch.md)、[155根逐点回执](evidence/runtime-isolation-ri00-long-watch-c1-20261113.json)、[v2等待阶段无V8统计getter合同](../knowledge/experience/runtime-isolation-ri00-passive-watch-v2.md)。C1运行109.55分钟后因heap/space getter释放分配区的已知干预主动封存；方法/binding恢复、端口关闭、原应用进程保留。该数据不是纯自然负例，getter影响也不是30–40ms根因。v2先机械验证自然/取回/续租路径不调用三类getter，再以累计剩余预算继续；新探针/参照不继承C1快态，空窗明确记录，RI-01不开始。

2026-11-12密集残差专项：[同进程形成采样合同与结果](../knowledge/experience/runtime-isolation-ri00-dense-residual-capture.md)、[逐点回执](evidence/runtime-isolation-ri00-dense-residual-20261112.json)。固定实际进程、一个常驻只读参照和同一探针，0/7/14分钟夹测，连续保存自然前史；首点因参照极差拒绝基线，第7分钟建立快态，第14分钟仍快，未出现目标30–40ms残差。19.5分钟78个自然根、48/24次受控读，源/输出/工具身份一致，探针恢复、端口关闭。合成30ms触发只验证采样器；首轮Inspector失败保留并修正批次持有/确认。该负结果不解释旧密集残差，RI-00不闭合，RI-01与重构未开始。

2026-11-12再次授权启动续证：[首次Evidence完整顶层链、3对回收状态干预与5分钟自然窗口](../knowledge/experience/runtime-isolation-ri00-startup-topchain.md)、[回执](evidence/runtime-isolation-ri00-startup-topchain-20261112.json)。托盘初始化Badge计数经BotDirectory/批量Supervisor/核验触发首次Evidence，27帧同步栈和异步装配入口均已捕到；RI-01覆盖必须包括Shell启动回调，落在已有bot.badge→M12合同，不能只迁Renderer RPC。自然周期额外指令的3对干预及最后一个自然恢复快点已经补到，旧密集残差形成仍未证明；三轮夹测为负例而非历史归因。用户本次授权启动已执行，应用保留运行，探针和实际端口关闭，不开始RI-01或重构。

2026-11-12同进程续证：[现场转换、自然入口与原生分配标记配对](../knowledge/experience/runtime-isolation-ri00-thread-transition.md)、[逐点回执](evidence/runtime-isolation-ri00-thread-transition-20261112.json)。实际完整查询已有快→慢→快，直接自然查询的主线程指令与额外后台CPU已补到；3个自然窗口均有major/incremental与分配标记或写屏障栈，暖读后3点未采到这些栈。GC observer的零不再用于排除GC，原生样本数不换算成精确毫秒，不把全部残差写成暂停成本。启动恢复顶层链已找回，首次索引上层连接尚缺；用户已授权另一次启动，但须等明确安全退出通知。RI-00门不放宽，不开始RI-01或重构。

2026-11-12授权启动续证：[现场读取顺序、夹测、自然节奏与ABBA](../knowledge/experience/runtime-isolation-ri00-startup-followup.md)、[新回执](evidence/runtime-isolation-ri00-startup-20261112.json)。启动已执行一次，应用保留运行；新密集窗口无旧正向CPU差，项目页自然读取仍约500ms，计量开关未消除阻塞，同源隔离15秒读取也达到该量级。历史430ms与当前500ms不是同窗受控差，旧进程形成与首次索引顶层栈缺口仍保留；RI-00未闭合，不进入RI-01。

2026-11-12归一化续证：[CPU/堆/节奏对照](../knowledge/experience/runtime-isolation-ri00-normalization-cpu.md)、[逐点回执](evidence/runtime-isolation-ri00-normalization-20261112.json)。隔离15秒节奏的部分CPU增量已重复出现，完整幅度与实际main的密集剩余差额仍未闭合；自然资源、同源密集夹测、GC原因、缓存元数据、编译/分配状态的正反结果均保留。G2未通过，RI-01与重构不开始；不把VM开关、合成live set或单个500ms点当成根治方案。

2026-11-12用户重开后：[对照结果](../knowledge/experience/runtime-isolation-ri00-restart-control.md)、[新回执](evidence/runtime-isolation-ri00-restart-20261112.json)。无CPU/FS/JSON的新进程仍自然停顿6.57秒，runner读取入口新增turnFacts/readSlot的真实调用栈；同文件旧Path慢化不再出现，全真实源只读基线约430ms但现场仍约500ms，主要差额在Evidence归一化CPU段。UI host回调存在而provider为null，不能把GoalPlanStore端口缺失与host端口混为一谈。G2仍未完全闭合，RI-01与产品重构未启动；不自行放宽原门或把重开称为修复。

2026-11-12续证：[自然多秒窗口与剩余差额](../knowledge/experience/runtime-isolation-ri00-natural-followup.md)、[续证回执](evidence/runtime-isolation-ri00-natural-20261112.json)。自然5.417秒窗口已覆盖IPC/timer同步根及漏掉的runner roster微任务；同文件夹测定位长期main的Node Path/getPlan成本差额，触发原因尚未证实，RI-00保持未闭合。旧3949ms按用户要求保留历史证据缺口。RI-01新增上述两个已发现入口的覆盖要求；进入实现前必须按02/03/04逐项复审来源字段、版本、队列和恢复，不许把未知慢化写成既定原因或在实现时临时决定。

2026-11-12 RI-00更新：[调用链、冻结坏基线及未闭合项](../knowledge/experience/runtime-isolation-ri00-investigation.md)、[机器回执](evidence/runtime-isolation-ri00-20261112.json)。已纠正约190ms裸宿主漏Desktop核验依赖的对比口径；真实IPC突发可复现多秒阻塞。原3949ms触发仍未证实，现场剩余差异与完整真实交互门未闭合，RI-01及整体重构尚未开始。以下保留2026-11-11详细设计候选的历史收据，不把当时的“仅文档”描述套用到新诊断脚本。

完成总体设计与ADR128提案，随后按用户要求一次补齐七篇详细规格及411项路由，并完成[自上而下自审](../knowledge/experience/runtime-isolation-detailed-design-review.md)，R01–R26已回写；详细接口/owner/依赖/队列/恢复不再延期到实施。ADR128仍Proposed，产品重构未开始。

已有一次有限进程隔离可行性对照，首轮启动超时保留；本轮仅内容/差异/一致性检查，不跑代码测试。没有更改Peer-Agent产品源码、运行安装或个人任务；没有启动产品模型/能力执行，也没有宣称当前卡顿已修复。真实验证以详细设计D01–D18及各阶段证据为准，自审不算独立审查或发布验收。
