# RI-00：同一现场进程的快慢转换与原生 CPU 续证

日期：2026-11-12。接续[授权启动续证](runtime-isolation-ri00-startup-followup.md)，[逐点回执](../../playbook/evidence/runtime-isolation-ri00-thread-transition-20261112.json)。本轮只增加诊断与证据，没有产品性能修复，没有重启现场应用，也没有开始 RI-01 或重构。

后续：[授权深栈启动与机制干预](runtime-isolation-ri00-startup-topchain.md)已捕到首次Evidence的完整托盘计数入口，完成3对额外指令干预、5分钟自然观察和窗口后夹测。下文“等待下一次安全退出”的状态保留为当时记录，最新采样已执行一次，不代表整个RI-00已闭合。

## 同进程转换，区分受控入口与自然入口

所有现场窗口属于同一安装进程，索引固定为69266行，受控查询返回23条、每次12遍归一化/831192行，索引内容和受控返回投影摘要在各组内一致。本轮未重新逐次计数getPlan，不把前轮3859次计数冒充本轮新测结果。私有原始记录保留，公开回执不包含进程ID、用户路径、scope或数据原文。

第一组受控完整查询在密集段为452.337–462.338ms线程CPU，探针间隔14.5秒后为475.850/502.289/480.602ms，随后密集段447.018–454.270ms。502.289ms点主线程约88.85亿条指令，密集段约81.8–82.1亿；能效核CPU仅0.057ms。它不能用单遍索引读点的核迁移解释。

补齐GC事件交付后，同进程第二组间隔点495.592/460.161/492.294ms，快段与恢复段各点完整保留。不能把14.5秒探针间隔当作充分慢化条件，更不能声称应用在此期间真的空闲。

增加有界应用入口记录后，第三组实际轮询为509.574–513.068ms墙钟，其后约765–772ms的受控查询CPU为458.928–464.361ms。另有一个应用入口首点1781.907ms墙钟、1779.177ms线程CPU、1502.548ms归一化用户CPU；原值保留，尚不能解释该首点为何异常，也不把它称为新的多秒事件。应用入口继续正常轮询，既未暂停，也未用受控读取替代自然读点。

第四组直接为自然查询取外围主线程硬件计数窗口，三个自然根CPU为510.125/493.527/501.678ms，归一化用户CPU321.171/315.629/322.714ms；其它线程CPU275.455/285.835/276.391ms。相同scope已验证。主线程外围窗口指令约88.80/87.44/87.14亿，密集受控段约81.8–82.1亿。外围比根自身多7.054/2.408/2.672ms主线程CPU，原值不裁零，不能把外围指令全部算入根。

这些实际窗口显示额外指令与额外后台CPU；不能把整个差额写成等待、频率降低或能效核执行。自然入口的第2/3点开始前新生代已为64MiB，仍有额外成本，因此“新生代收缩”也不能单独解释全部点。

第五组同时采原生栈，自然与受控投影摘要逐点一致。原生采样明显增加墙钟等待，不将该组作为无采样性能验收，也不把它与历史430ms机械相减。

## 核计数与 GC 计量修正

旁路libproc按unique kernel thread ID连接PROC_PIDLISTTHREADIDS、PROC_PIDTHREADID64INFO和PROC_PIDTHREADCOUNTS，只取确认的CrBrowserMain；性能级名称由系统读取，ABI长度、单调性、Mach timebase及独立CPU负载已验证。进程总指令仍不能当主线程指令。接口依据[Apple recount](https://github.com/apple-oss-distributions/xnu/blob/main/doc/observability/recount.md)、[线程计数结构](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/proc_info_private.h)与[unique ID实现](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/proc_info.c)。只读OS计数，没有向应用加载原生代码、改变优先级或功耗策略。

外围20ms采样用Python与控制器时钟交集校准，并另核对控制器与应用hrtime偏差区间；绝不直接假定Python monotonic与Node hrtime共用起点。每个自然根只选择保证在起点前和终点后的计数快照，保留窗口外CPU、前后余量及计数可用性。

单遍索引曾记录23.921→26.761→23.229ms、相近约5.33亿指令，中点能效核约5.947ms，相邻快点接近零。此处核计数仍有效；但此前用GC observer的0排除GC过强，撤回该排除判断。后续CPU profile在部分GC observer为0的点仍观察到GC采样。CDP可经Chromium调用而未排空Node事件交付，控制器等待20ms不是observer交付确认。现改为停观察前等待两个owned Node check turn，隔离及现场续采末段GC已有记录；这也不冒称覆盖所有VM回收工作。

CPU profile按具名时钟标记校准，归一化中的GC采样平均约27–29ms（快段）与40ms（间隔段）；根GC平均约38–39ms与46ms。其余采样增量分布在reader、normalizer等栈，不能只按GC暂停时长填满残差，也不能将采样self time拼成精确CPU账。

## 分开的原生配对，确认现场分配/标记路径

为避免把被剥离二进制的近邻导出名误认成实际函数，下载[Electron v41.7.1官方符号](https://github.com/electron/electron/releases/expanded_assets/v41.7.1)，校验发布页与SHASUMS的SHA256，并与安装Framework的Mach-O UUID严格匹配。只按Breakpad FUNC地址区间解析，不用nearest-public-symbol补缺。整窗1355个Framework地址解析1343个；六个分窗1282个解析1275个，剩余保留unknown。原生JIT地址没有据此变成JS具名函数，不称完整逐指令账。

随后分别对3个自然轮询及暖读后的3个单次受控查询采1秒原生窗口；每个自然窗口仅含1个同scope应用根，每个快窗口没有夹入自然查询。自然根CPU为518.876/520.348/519.183ms，快根461.355/466.094/466.018ms；归一化用户CPU分别321.574/318.238/322.126ms与286.906/281.603/291.178ms。6点索引/投影摘要相同，没有重启、参数控制或强制GC。此组有原生采样，绝对CPU与墙钟不代替前面的无原生采样基线。

自然三点均有28次minor、1次incremental、1次major GC事件在根区间内；快点各11次minor，没有记录到major/incremental事件。自然开始前新生代1–1.5MiB，快点64MiB。major暂停分别10.494/7.552/8.561ms；minor暂停自然41.299/44.529/44.283ms，快点41.717/38.612/52.884ms。原值表明仅按暂停相加不能解释完整约53–59ms CPU差，亦不把快点暂停更长的负向差删去。

按线程树去除嵌套重复后，三个自然主线程窗口分别采到3/3/0个分配推进增量标记栈样本、1/4/3个标记写屏障样本、5/4/5个mark-compact样本；三个快窗口上述类别均未采到，scavenge仍存在。这里是样本数，不把sample标称1ms直接乘成毫秒：实际采样频率和暂停存在扰动，也不能将包含根前后闲段的整窗栈精确归到根内每条指令。

匹配符号后的实际链包含 `Runtime_AllocateInYoungGeneration → HeapAllocator::AllocateRawSlowPath → 分配/回收重试`，以及 `IncrementalMarking::AdvanceOnAllocation → Observer::Step → IncrementalMarking::Step`、`WriteBarrier::MarkingFromCode`、`ConcurrentMarking::RunMajor`。它与同步根内major/incremental事件、额外主线程指令和后台CPU互相印证：当前自然轮询慢段确实进入与密集快段不同的分配/标记/回收周期。不是仅有隔离VM日志，也不是只看暂停时长。

该证据解释了为什么“相同12遍归一化”不保证相同CPU成本，并将一部分隐藏成本绑定到真实主线程分配/标记路径；它尚未逐项分清全部CPU份额，也不能回填已退出旧进程独有的密集30–40ms上下文残差。此前隔离关闭memory reducer/固定growth没有稳定改善绝对延迟的负例继续有效，不因本次采到标记路径便改写为“关GC即可修复”。架构治理仍须约束全量读取、重复归一化、事实owner和执行位置，不能用VM开关取代。

## 启动顶层链：找回的部分与尚缺的部分

重新检查原始授权启动记录，前4次plan文件读取的8帧栈没有截断，真实链为：

`composition root 的 then 回调 → root.start → recovery-and-appearance.start / startRecoveryAndAppearance → goalRunner.recoverContextCheckpoints → GoalPlanStore.getPlan → readJson`。

composition root与main、goal-runner文件在既有939文件安装/源码比对中相同，本轮又核对源码摘要没有变化。相同实现将该then回调接在app.whenReady之后，并以includeDelegated:false调用恢复；这两项来自源码核对，app.whenReady本身不是原始栈帧。root.start到恢复读取是已记录的实际调用链。

首次Evidence文件读取仍是另一段真实栈：`humanGateOf → acceptanceFacts → hostFacts → readSessionFacts → SessionVerification.facts → factsFor → evidenceRecords → readEvidenceIndex → readJsonl`。2086次plan文件读发生在该首次索引前，并不证明上述恢复入口就是索引读取的父调用；不能把两段栈无证据拼接。原记录10帧截断以上的连接已丢失。

启动采样器已扩为临时64帧并原样恢复Error.stackTraceLimit，可选采异步父链，沿inline parent和parentId解析、有界失败，不把截断当完整链。两个owned Electron不同读取顺序canary通过，零源写拒绝/读失败，恢复和端口关闭通过。它们仅验证采样器，未冒充现场启动归因。用户已另行授权下一次30秒启动采样，但明确要求等其通知已安全退出后再启动；当前应用继续保留，尚未执行第二次启动。

## 本轮边界与交付

C级诊断。沿用00-adr-map、96-task-execution-responsiveness、98-large-history-execution-responsiveness、104-progressive-interaction-and-coordination-storage、112-runtime-module-and-loading-boundaries、115-input-prediction-and-draft-boundary、121-desktop-session-windowing-contract及128-local-runtime-isolation-and-bounded-query-contract。现行运行时、权限、Evidence、System Context、存储及IPC边界未移动，ADR128仍Proposed。RI-00门不放宽，原3.949秒缺失父调用/CPU栈仍作为历史证据缺口，不以新进程、隔离或合成实验补造。

诊断候选`3a420d4d0b04c4f2605fb0991a78546f7ce700e0`已提交并推送。Node25.9.0下68项聚焦测试、5个MJS语法、Python AST、architecture/UI与diff检查通过。最终owned Electron完整查询/500us时钟profile canary通过，输入与投影一致、零读失败/源写拒绝；新版深栈/异步父链的双顺序canary也通过。新增probe独立watchdog在控制器丢失时恢复owned方法，明确超时失效，不覆盖晚到owner；相应测试通过。自动CI没有返回run/status，不称绿色。内容、数据身份、链接、隐私与diff为实现者自审，不称独立审查；没有安装修复候选、模型/工具派发、实际应用堆快照、VM GC/优化参数改变或完整产品/发布验收。

当前材料没有宣称旧进程独有的密集30–40ms残差已全部解释；启动索引上层链仍等用户安全退出后的授权采集，RI-00不提前关闭。
