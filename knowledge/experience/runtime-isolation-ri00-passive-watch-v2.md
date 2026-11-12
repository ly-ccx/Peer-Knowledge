# RI-00：等待阶段不调用V8统计的长观察v2

日期：2026-11-13。状态：诊断候选与资格验证已完成，待实际接续；RI-00未闭合，不开始产品重构。沿用`00-adr-map.md`、ADR96与Proposed ADR128，C级诊断，不改产品边界。

[C1](runtime-isolation-ri00-long-watch.md)在109.55分钟后因明确的观察器缺陷停止：V8普通heap/space统计会释放主线程线性分配区，code统计还可完成sweeping。原始记录全部保留；这些影响不是旧30–40ms的归因，不能用低自计CPU证明状态无影响。v2仍使用原应用进程，严禁重启、强制GC、改VM参数、取堆快照或改个人任务。

## 1. Module与接口

| Module | Interface与事实归属 | 依赖、队列、恢复 |
|---|---|---|
| Persistent Probe | 自然root/根外Evidence只记录线程与进程CPU、时钟、首遍同步栈、源stat/输出SHA、观察到的GC；schema=`passive-cpu-v2`；自然heap字段为null，不伪装成最新缓存 | 自然入口、renew、take、ACK、停止和被动VM摘要均不得调用`getHeapStatistics/getHeapSpaceStatistics/getHeapCodeStatistics`；仍有普通JS分配/栈/GC observer成本，不声称绝对零扰动；原结果/receiver/异常保持 |
| Controlled Sampler | 原main-A8→参照8→main-B8、PMCs/原生校准、旧GC/64MiB/极差/CPU判据保持 | 明确为主动测量：根前后原heap统计会释放LAB，只有受控读允许；初始及两次确认使用同一程序，不将其称为无分配干预。取栈前不再额外读取code统计；复用最后受控heap摘要并带来源时钟 |
| Natural Sentinel | 同一schema/输出/索引/12遍行数身份；每位置5点，至少6位置、平均增量≥2ms且≥8%、连续3根，或根≥2秒，只产生取证信号 | v2不采新生代大小，不声称GC/代际状态严格配对；仅按已观察major/incremental事件筛位置，缺少事件不证明没有GC。与C1指纹不混用；密集残差确认门不放宽 |
| Source Epoch Observer | 源真相仍由三Store canonical、目标coordination canonical/当前指针及revision决定；缓存只决定何时重核验 | 六个owned watcher：三Store递归、coordination-v2递归、coordination根非递归、`.read-models`非递归（只关心当前指针）；不遍历fenced/recovery库存。单个dirty位、首末时钟及计数合并；事件只唤醒，不能产生业务查询或执行事实 |
| Source Refresh | 初始、变化通知、最长10分钟审计、每次受控夹测前后强制完整inventory+revision | 稳定等待不再30秒扫8千文件或读取参照业务数据；30秒只续租与OS身份。事件丢失可能造成失效发现延迟，夹测强制核验拒绝跨数据结论；原始通知不是逐写入内容日志。不将缓存当权威来源 |
| Campaign Budget Carry | 只从此前已停止/恢复/关端口且ACK差额为0、成本字段完整的真实capture receipt扣减预算；失败观察若满足这些条件仍可扣减接续，失败不能被抹除；保存原回执SHA、主进程PID/OS birth、产品摘要；不继承旧参照/指纹/基线 | 累计上限：实际main读体60秒、main及参照各探针5秒/校准3秒、控制器30秒、归档1.5GiB、现场活动观察4小时。已知补充VM见证CPU另外扣探针预算。剩余实际main读体不足40秒或活动观察不足15分钟、控制器不足1秒等拒绝新窗口；实际应用替换或产物不符拒绝；维修/资格验证空窗明确记录 |

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
