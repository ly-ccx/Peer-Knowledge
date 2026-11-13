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

2026-11-13 E3实际Q/H：[功能资格与原失败](evidence/runtime-isolation-ri00-e3-qualification-20261113.json)、[固定六实例原始拒绝](evidence/runtime-isolation-ri00-e3-order-20261113.json)、[完整结论与准入](../knowledge/experience/runtime-isolation-ri00-formation-e3.md#9-本轮实际qh收据与现场准入结论)。首见证/单槽/异常及失联恢复覆盖通过；原第二实例bootstrap失败保留，剩余第三固定槽补齐功能，不替换第二例。Q连探索恰好5个启动、读体35.260555秒。H候选8cfb68f0按C1/T1、T2/C2、C3/T3执行，7个Electron共129.967秒、读体98.029707秒；六个target均在F0暖段极差超过15ms，C1另有校准失配，因此有效配对0/3、顺序处理0次。不能称六次机制阴性；不补进程、不改门、不进入F。源/代码/输出一致、恢复完成、原始失败封存；现场入口/信号适配器仍未资格验证，RI-00及重构继续冻结。收尾journal总帽修正候选18552dfa没有重跑或冒领H。

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
