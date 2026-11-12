# RI-00：等待阶段不调用V8统计的长观察v2

日期：2026-11-13。状态：诊断候选与资格验证已完成，实际同进程接续已按累计预算收尾；RI-00未闭合，不开始产品重构。沿用`00-adr-map.md`、ADR96与Proposed ADR128，C级诊断，不改产品边界。

[C1](runtime-isolation-ri00-long-watch.md)在109.55分钟后因明确的观察器缺陷停止：V8普通heap/space统计会释放主线程线性分配区，code统计还可完成sweeping。原始记录全部保留；这些影响不是旧30–40ms的归因，不能用低自计CPU证明状态无影响。v2仍使用原应用进程，严禁重启、强制GC、改VM参数、取堆快照或改个人任务。

## 1. Module与接口

| Module | Interface与事实归属 | 依赖、队列、恢复 |
|---|---|---|
| Persistent Probe | 自然root/根外Evidence只记录线程与进程CPU、时钟、首遍同步栈、源stat/输出SHA、观察到的GC；schema=`passive-cpu-v2`；自然heap字段为null，不伪装成最新缓存 | 自然入口、renew、take、ACK、停止和被动VM摘要均不得调用`getHeapStatistics/getHeapSpaceStatistics/getHeapCodeStatistics`；仍有普通JS分配/栈/GC observer成本，不声称绝对零扰动；原结果/receiver/异常保持 |
| Controlled Sampler | 原main-A8→参照8→main-B8、PMCs/原生校准、旧GC/64MiB/极差/CPU判据保持 | 明确为主动测量：根前后原heap统计会释放LAB，只有受控读允许；初始及两次确认使用同一程序，不将其称为无分配干预。取栈前不再额外读取code统计；复用最后受控heap摘要并带来源时钟 |
| Natural Sentinel | 同一schema/输出/索引/12遍行数身份；每位置5点，至少6位置、平均增量≥2ms且≥8%、连续3根，或根≥2秒，只产生取证信号 | v2不采新生代大小，不声称GC/代际状态严格配对；仅按已观察major/incremental事件筛位置，缺少事件不证明没有GC。与C1指纹不混用；密集残差确认门不放宽 |
| Source Epoch Observer | 源真相仍由三Store canonical、目标coordination canonical/当前指针及revision决定；缓存只决定何时重核验 | 六个owned watcher：三Store递归、coordination-v2递归、coordination根非递归、`.read-models`非递归（只关心当前指针）；不遍历fenced/recovery库存。单个dirty位、首末时钟及计数合并；事件只唤醒，不能产生业务查询或执行事实 |
| Source Refresh | 初始、变化通知、最长10分钟审计、每次受控夹测前后强制完整inventory+revision | 稳定等待不再30秒扫8千文件或读取参照业务数据；30秒只续租与OS身份。事件丢失可能造成失效发现延迟，夹测强制核验拒绝跨数据结论；原始通知不是逐写入内容日志。不将缓存当权威来源 |
| Campaign Budget Carry | 只从此前已停止/恢复/关端口且ACK差额为0、成本字段完整的真实capture receipt扣减预算；失败观察还须满足§8的已知完整成本准入，失败不能被抹除；保存原回执SHA、主进程PID/OS birth、产品摘要；不继承旧参照/指纹/基线 | 累计上限：实际main/参照读体各60秒、main及参照各探针5秒/校准3秒、控制器30秒、归档1.5GiB、现场活动观察4小时。已知补充VM见证CPU另外扣探针预算。剩余实际main读体不足40秒或活动观察不足15分钟、控制器不足1秒等拒绝新窗口；实际应用替换或产物不符拒绝；维修/资格验证空窗明确记录 |

所有数据保留私有目录，公开只给脱敏计量和摘要。源归档继续独立worker30秒硬截止/128MiB堆、1MiB散列缓冲和SQLite一致备份；不复现原inode/writer fence。C1归档计入累计预算，不能靠重开诊断器重置预算。

## 2. 顺序与异常

1. 先证明C1已恢复，Inspector拒绝连接，原应用OS birth未变。启动v2 owned参照和新探针；探针摘要固定后不热改。
2. Source watcher在初始inventory前安装；活动根替换时重建owned watcher，记录该变化，不继续信任旧inode。unknown filename作dirty；watcher error/事件计数上限/根消失均失败停止，不静默降级。总事件上限100,000，队列不保存无限文件名；每次完整刷新消化当时已知dirty，刷新期间新事件保留到下一轮。
3. 初始受控快态与自然指纹后的第二次夹测仍保持；没有快态也能取证，但标记entry-unqualified。等待阶段自然调用与批次取回均不调用三类V8统计getter。
4. 自然触发后两次无profiler密集夹测；数据身份/原判据不合格仍明确保存取证，源改变则冻结，不拿不同数据拼差额。再做bare/detailed、双profile和无profiler复验；额外code统计禁止用于现场捕获链。
5. 90秒失联租约、原硬watchdog、先落盘后ACK、CPU/元数据/磁盘准入继续生效。恢复不覆盖晚到owner，不以重放查询处理超时。无效检查点清零连续计数；方法、binding、owned句柄及实际端口必须收尾核验，应用保留。
6. 两窗口间的空窗、探针替换及旧参照退出保留；不能将C1快态和v2慢点直接拼成同一测量方案的形成证据。只有v2自己的合格快态、自然前史、两次有效密集对照及实际机制回放才能推进G2。

## 3. 实现前验收定义

- 用owned Node及真实Electron监视三类V8 getter调用；自然root、根外读、通知、renew/take/ACK/VM摘要/stop全部为零；受控阶段明确非零且仍返回原heap字段。不能只做静态字符串检查。
- 新schema自然信号无需heap值；旧schema维持原规则，schema切换失效。GC/身份/连续计数、预算、取证/确认分离和全部失败路径复验。
- Source observer：稳定30秒续租不全树刷新；事件、指针、canonical、未知filename、周期审计、root替换、刷新中到达新事件、watcher错误/计数上限与close验证；夹测前后force刷新不走缓存。忽略lease和SQLite物理维护不能忽略canonical/revision变化。
- Carry：累计扣减、补充CPU、预算耗尽、OS birth/产物/回执不符及旧结果缺字段均拒绝；旧基线不可继承。实际长观察不得人工加CPU或用fixture节奏替代归因。
- owned完整生产图只验证观察器与恢复，不是现场形成证据。新归档在现场观察结束后做只读回放，核对输出与读图；避免回放CPU干扰正在观察的进程。

本文件不承诺一个观察窗口必然遇到慢化；未捕到目标或观察有缺口时保持unknown，不能将观察器修正当成产品性能修复。

预算是已定义读体、探针和long-watch控制阶段的CPU准入累计，不冒充全部进程启动/清理、Inspector序列化及OS边界成本的绝对硬实时封顶；C1这些未独立计量的边界仍是成本缺口，不能按零补齐。同步操作最后一次越界保留实际值并退出。


## 4. 实现及资格收据

候选`63750ee03f4987e2213aa54c9acc56b0d4ecfc84`已提交推送；104项诊断测试、12个变更MJS语法、architecture/UI及diff通过。真实Electron通过Inspector安装同一序列化探针，监视三类getter，natural/根外/通知/renew/take/ACK/VM摘要/stop均为零；受控读仍调用原heap接口。控制器死亡恢复验证继续通过。

[资格与回放回执](../../playbook/evidence/runtime-isolation-ri00-passive-v2-qualification-20261113.json)保留c2a与最终c2b。c2b完整生产只读图33个自然根、28个策略入口、32/22次main/参照受控读，main12.604928秒、控制器980.254ms；六个source watcher均关闭，零记录丢失/读取失败/源写拒绝，源/输出/代码身份一致。两次fast门因校准/暖段状态未通过，仍为entry-unqualified，不能叫性能负例。fixture专用5秒节奏不用于actual。代码审查另修正rebind部分close失败的owned资源账本，并覆盖恢复重试；没有把不确定关闭记成零资源。

C1的8535项归档已经owned COW复制后实际回放3次：均23个session、3859次getPlan、12遍/831192条Evidence，投影SHA与C1相同；协调revision6713，零读取失败/源写拒绝。原归档、回放副本全量内容与原manifest匹配，manifest摘要也与原capture绑定。首次因猜错Electron路径未启动任何查询，失败保留；依赖解析路径重试通过。这里只闭合查询数据回放，不证明旧VM状态或writer fence。

接续从C1累计预算扣减，剩余活动观察7,827,034ms、main读体47,566.284ms、控制器11,798.818ms、归档1,026,578,587字节；已知补充见证CPU也扣探针预算。新实际窗口必须单独建立快态，不能继承C1参照。产品源仍b05b7af，RI-01/重构未开始；实现者自审，不称独立或发布验收。


## 5. 实际接续入场（不是结束回执）

[启动回执](../../playbook/evidence/runtime-isolation-ri00-passive-v2-startup-20261113.json)：v2已接回原应用PID/OS birth，未重启。首点main-A250.096/参照263.306/main-B252.077ms，相对差−13.210/−11.229ms，符合原快态；第二点参照兼容暖段极差16.760ms超过15ms，拒绝该夹测，没有反复补采追绿。保留首个合格快态，但自然指纹未被两个合格快点夹住，阶段诚实标记entry-unqualified；不是“无任何快态”。后续只能用本窗口合法基线与两次有效无profiler夹测判断，不用C1填补。

main累计主动读体12.253496秒；源/参照/探针固定，等待阶段实际自然记录的heap为null、新生代大小不采，不把缓存摘要当当前堆。该启动回执不证明剩余残差形成或停止恢复；最终结果须待实际窗口收尾后另封存。代码及生产读图在观察期间冻结，不运行竞争性性能工作。


## 6. 受控读与自然包络的重入（不可当自然停顿）

[时段/CPU回执](../../playbook/evidence/runtime-isolation-ri00-v2-diagnostic-nesting-20261113.json)显示，17:47:35 UTC归档的自然调用包络为1099.568ms、线程CPU1098.763ms，其中存在两段完全包含的受控读，CPU合计729.699ms；一段位于第6遍Evidence跨度内，另一段在第10/11遍之间。原始时钟与子读CPU均保留，不能把inclusive自然包络或其单遍峰值当成纯业务成本。算术余量369.064ms仍包含未单列的诊断边界及状态影响，不是无探针对照。

这是Inspector受控求值重入既有应用调用的直接记录，不解释旧30–40ms。这些点出现在主动bootstrap/checkpoint阶段；等待阶段不主动读取业务。最终回执必须标注可见受控读/校准的重叠，单列不可比较包络，不删除原点或用扣减值制造自然快态。控制阶段的输入/输出、GC、PMC及暖段门继续按原值判断；不把混合包络作为新自然多秒证据。当前运行候选不热改。


## 7. 实际C2收尾与证据总账

[完整C2回执](../../playbook/evidence/runtime-isolation-ri00-passive-v2-c2-20261113.json)绑定实际运行候选`63750ee03f4987e2213aa54c9acc56b0d4ecfc84`，不是后续诊断修补候选。17:47:24.632—19:56:26.519 UTC，收据墙钟129.03145分钟，long-watch活动128.95059分钟，按有界截止退出。原应用OS birth相同，未重启；owned参照和控制器已退出，六个watcher关闭/零存活，方法/binding恢复，实际Inspector两次拒绝连接，另一次收尾外部连接亦拒绝。原产品工作树干净，产品/诊断/源摘要未变，读取失败/拒写/元数据错误/丢失/ACK差额均为零。

归档129个自然包络、策略输入128个，原始时钟无重复；唯一可见受控重入包络仍保留并标记，没有删除或按扣减CPU改造。其余128个包络的主线程CPU中位434.0065ms、最大444.881ms、wall最大448.065667ms；这是既有坏基线的描述，仍明显占用交互主线程，不是性能修复或无探针对照。对最终自然指纹的事后描述为124个包络8个可用位置、4个包络7个可用位置，零单根慢化信号、零连续信号、零≥2秒包络；该统计不重放实时静默/学习/冷却顺序，不声称堆状态等价或满足G2密集门。

只有入场两点：第一点合格快态，第二点因参照极差拒绝；后面没有为了追绿反复夹测。32/22次main/参照受控读，main读体12.253496秒，main探针自计231.289ms、校准321.470ms，long-watch控制器5.537818秒；控制器预算越界0。等待段未追加主动业务读取，也未补充VM getter/强制GC/参数干预；没有自然触发episode/profile。没有结束时补一个密集快点，因此不能推断整个窗口的密集CPU始终快。自计CPU不包含全部Inspector/OS边界成本，也不证明零状态影响。

源observer共18次完整核验、259次缓存命中，6128个按owner/pointer白名单忽略的通知（不逐项保存名称，不声称重建全部写入），零accepted变化/未知filename/错误；夹测前后及收尾force核验均保留。新归档8535项中8534个内容文件逐一SHA/size核验，一项只保留空fence目录；manifest与C1已实际回放的归档逐项完全相同，manifest摘要匹配。故无需再启动新宿主跑性能负例；数据身份可连接到§4的三次真实生产图回放，但原inode、writer fence及VM状态仍不由此重建。

| 证据事项 | 当前可证明 | 不能据此宣称 |
|---|---|---|
| 原3.949秒 | 原始行保存，缺父调用与CPU栈已明确登记 | 事后补造原事件归因 |
| 首次Evidence顶层链 | 原授权启动记录的27帧同步与异步装配入口已补齐，产物匹配 | 这条链解释旧密集CPU差额 |
| 数据及完整读图 | 同源manifest、23会话/3859 getPlan/12遍831192条Evidence及输出三次回放一致 | 新宿主重建旧VM状态或慢化形成 |
| 自然周期额外CPU | 已有实际栈/PMCs及配对干预支持的独立证据保留 | 周期回收成本替代剩余密集残差 |
| 旧密集30–40ms | 旧正向线程CPU差额保存；缺形成前史，旧N缺processCPU/PMCs不能补录 | 用当前未触发或重开变快倒推旧原因 |
| 本轮C2 | 同一应用身份下低干扰等待、完整自然包络、无覆盖/无丢失、恢复完成 | 未发生的快→慢转换或残差机制 |

C1与C2合计活动预算接近4小时；继续接续仍须扣已用成本，剩余时长不足新窗口15分钟准入，main余读体也不足40秒新窗口准入。不能重开采样器清零重跑。下一轮若获新的明确观察预算，应覆盖自然实际使用，并重新建立本方案内的合格快态；这些收据之间的维修与结束空窗不可拼成完整形成前史。RI-00的G2仍需同一进程自然慢化、两次合格无profiler密集对照及实际机制回放，RI-01/产品重构继续冻结。

收尾核验保留了两个工具失败：最初将ps日期文本与Mach birth直接比较产生无效false，随后用原native counter同PID比对通过；首次归档核验调用本机Python不支持的hashlib.file_digest，在首个文件完成前失败，改用1MiB流式SHA、相同归档/期望值全量通过。未将工具失败当成应用退出或源损坏，也未弱化断言。

## 8. 观察后接续准入审查（先于修补）

实际C2完整成功，不受本节缺陷影响。审查发现旧`captureBudget`仅凭恢复字段和ACK差额零，可能允许包含Inspector/RPC超时或断线的失败回执接续；若仍有未计量的在途读，零字段不能证明真实成本完整。另发现缺失`mainCpuMs`可经NaN比较漏过差额核验。两者违背既有“未知成本拒绝”要求，不改变产品或架构边界。

后续诊断修补须：成功回执的ok/空failures一致；失败只准入明确source watcher error、匹配failed原因且observer已closed/零live/零closeFailures，仍满足所有既有主/参照恢复和成本条件；RPC超时/断线、混合/未知错误及不完整observer拒绝，即使ACK为零。acknowledged mainCpuMs必须有限非负。先保留失败测试，再修实现；本轮实际结果始终绑定63750ee，不用后续候选冒领现场验证。


观察后修补候选`ca684d70060d35d9974f9b539315bd3e0395286a`已提交推送：[准入回归回执](../../playbook/evidence/runtime-isolation-ri00-budget-admission-20261113.json)。原实现下保留8项中5通过/3失败，再修实现；最终预算/长观察/源observer共21项通过，语法/diff通过。真实C1成功回执在最终候选仍产生与C2入场完全相同的剩余预算；真实C2回执进一步自动接续被`capture_budget_remaining_insufficient`拒绝，没有重置。零ACK的RPC超时/断线/混合错误、ok与failures矛盾、失败回执缺失observer、已提供却未关闭/损坏的observer及未知ack CPU均拒绝；无observer的旧成功回执保留兼容，已知watcher失败的完整恢复可扣减接续。实际C2封存摘要未变，ca684d7未拿来冒领现场采样或新性能结果。

关联PR workflow/status查询均为空，不称绿色CI。C级诊断，沿用`00-adr-map.md`、`96-task-execution-responsiveness.md`和仍Proposed的`128-local-runtime-isolation-and-bounded-query-contract.md`，现行边界不动。文档/JSON/链接/隐私/diff为实施者自审；未做新的真实模型、安装、产品交互或发布验收。运行中的原应用及个人任务保留，当前无本轮活动探针/owned参照/控制器。
