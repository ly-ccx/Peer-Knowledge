# RI-00：完整块顺序对照执行与收据

创建时间：2026-11-14
最后更新：2026-11-14

## 执行前契约

沿[244根封存拆解及完整顺序设计](runtime-isolation-ri00-e3-cadence-variation.md)与[冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-pair-order-budget-20261114.json)执行。A为target完整块→conditioning完整块，B相反，两边块内每根额外等待150ms；预热仍为每host8根、不加等待timer。完整块含10个原根和3次块末hash，旧暖段15ms/归一化返回2ms、两个raw返回2ms、实际间隔及同号四效应门不改。

本轮C级诊断实现沿用Accepted ADR `96-task-execution-responsiveness.md`的事实/恢复约束及Proposed `128-local-runtime-isolation-and-bounded-query-contract.md`的RI-00前置门，不更改产品契约或接受Proposed重构。按engineering-principles技能读取唯一本机工程总纲，不复制正文。

固定执行器候选`c4738164`只新增顺序controller、纯结果Module与本实验adapter。共享原owned host、传输层Profiler拒绝、单槽队列、durable reader、原块读取与费用预留，旧150/0执行器不改写。controller独占调度/准入，probe/queue独占root事实与ticket，journal负责先fsync后ACK，result只消费固定事实；生产Store/实际Peer不变。

每块以global journal写入并fsync complete-block-start，十根及三hash全部完成后写complete-block-end，再允许下一块；保留同controller单调时钟及journal序号，不跨host减row时钟。结果核对每块角色、10根/3hash、边界序号与时间先后，逐块9个实际间隔≥150ms、每个target对比的间隔中位差≤5ms；远端label始终cadence-root。raw用户中位的一个或两个真实锚点共同导出用户/内核/合计、余部及全根I/C；conditioning参加处理，不冒充未受处理参考。全根PMC与相同GC签名配对仅作补充，逐遍指令不补0。

原F0拒绝即消耗target槽，只继续另一原定target；处理前以完成F0预留80根、24hash、全部审计/间隔/返回/清理，floor CPU61500ms/hash1200ms/wall241500ms，controller剩余5000ms。普通暖/返回失败仍保留固定四格（原预算允许时），未知请求只查原id，归档失败保留原件，取消/source/owner/birth/预算异常停止准入并有界恢复自有host。CDP先关闭再exit，不覆盖晚到owner。hash费用同时核对host最终native累计值，避免未知RPC漏计；费用登记不能在fsync前抛错丢弃原行。

执行前绑定须串起同一干净候选、完整source、原report/journal/audit/计划SHA、生产Module及8534文件+空fence、同候选测试和真实队列接缝。测试、接缝、binding各由父进程等待退出后以RUSAGE_CHILDREN记录完整费用（含子git、输出与fsync返回），准备费用带入20秒controller/aux，另保留原5秒准备关闭reserve，不只用写报告前的CPU快照。

## 独立接缝验证额度（执行前冻结）

本节在专用Inspector资格进程首次启动前提交。固定1次Node Inspector资格进程，内部两个逻辑host/store/queue，不增加目标子进程，零Electron，零产品数据，零Profiler线上命令。沿真实序列化installer、transport、durable reader及共享complete-block/cell代码，固定A、B各一个cell共4块40根，加4根故障/恢复读取，共44根合成fixture；12次原native hash，实际44根和CPU/字节都核对，不当性能资格。

资格上限wall30秒（25秒停止准入，父进程35秒硬退出保护），fixture读体CPU合计2秒、每个probe沿原5秒、每个native沿原3秒限制，journal1MiB、资格输出2MiB；合成验证及完整准备CPU同时受正式20秒aux余量约束。测试用fixture及原mock Profiler测试不占实验Electron槽。预定场景：Profiler在wire前拒绝；真实A与B块/角色/hash结束先后及150ms间隔；fsync失败保留原ticket、恢复同原件不重读；request应答丢失查询同id；原读错误归档与后续准入；两个owner/queue/notice/端口恢复。故障接缝注入与真实随机断连分别标注。

117项聚焦测试初检通过。最初两个单元fixture因12份n/12的二进制浮点加和而使“恰好10”精确断言失败，原日志保留；改为可精确表示的分配输入并保持精确断言，所有性能门、真实输入与8ms判据不改。单元fixture的首点离群也保持root/Evidence/余部与实际间隔自洽；不把合成数据叫现场或机制证据。

原设计预算仍保留runnable:false历史状态；只有同候选资格与技术绑定通过后才领取正式三Electron槽。授权来自用户本次明确执行指令。不会重开实际Peer，不启现场窗口、不重构。正式结果随后按原件封存，资格失败不转成可用性能结论。


## 原接缝资格：功能通过，输出预算失败

[原失败收据](../../playbook/evidence/runtime-isolation-ri00-e3-order-seam-failure-20261114.json)保留c4738164原件。专用Node按固定44根、4块及12hash完成，六场景和实际A/B顺序/间隔、owner/queue恢复通过，Profiler线上命令0；wall7492.619ms，完整子进程CPU516.179ms。但report为3416276B，加journal500622B及两个3B fixture共3916904B，超过执行前2MiB输出帽，**资格判失败**。原Node槽已消费，未追加Node或启动Electron。

原因是报告把含完整record.batch.rows的reader返回值，同时经executed及target/conditioning字段重复序列化。原report的passed仅覆盖内部功能检查，父输出预算检查拒绝；不得用该内部布尔值冒称资格通过。所有原文件和费用保留。

修正候选1c053c56把完整事实唯一保存在journal，报告仅引用host/ticket、边界、实际间隔与校准；显式在写report前判断2MiB，binding还必须验证父进程的实际输出字节门。用原始封存cell离线回放，40个引用均能回指原journal，投影总输出522907B；两个投影测试通过，原性能门和精确断言不改。该离线回放不是新Inspector资格。

修正后的执行器还把原失败的unit1870.565ms与seam516.179ms合计2386.744ms准备CPU和旧输出保留字节计入同一原20秒aux/128MiB帽，不清零或删文件腾额。修正候选的完整119项同候选聚焦测试通过，原一次2MiB失败仍保留；额外专用Node资格和生产数据绑定尚未执行，三个正式Electron槽仍全数未用。

额外一次Node资格已通过文本问题请求明确授权，收到答复前保持待定，不自行追加。若获授权，只有新候选1次、仍44合成根/30秒/2秒fixture读CPU/1MiB journal/2MiB总输出/零Profiler和零Electron；累计Node资格将如实记为2次（原失败1+新1），不伪称原一次额度内。正式三宿主/所有原性能门/预算不变，旧失败不转绿。


## 追加一次Node资格授权（运行前记录）

用户已明确答复“授权一次仅Node重验”。仅对修正候选1c053c56追加1次专用Node资格，仍44合成根、30秒wall、2秒合成读CPU、1MiB journal、2MiB总输出，零Profiler/零Electron；原一次失败与费用不改写。本次通过数据绑定后，继续此前已明确授权的固定三Electron ABBA/BAAB，双方150ms、原性能门及所有预算不变。原119项同候选测试回执复用，不重复跑测试或借用原Node槽。

## 修正候选的同候选资格与执行绑定

追加一次Node资格依授权完成，旧失败保持。1c053c56的119项测试、真实44根/12hash/4完整块六场景、顺序/间隔、原ticket恢复与两owner恢复通过；原2MiB输出帽和30秒/2秒读CPU帽未放宽，Profiler线上命令0。累计专用Node2次（失败1+新成功1），无额外目标子进程或Electron。

[执行前绑定收据](../../playbook/evidence/runtime-isolation-ri00-e3-order-binding-20261114.json)绑定同一干净candidate、全部诊断source、原report/journal/audit/design、unit/seam及完整退出费用、生产Module与8534内容文件/空fence。准备累计CPU5885.057ms、保留输出4564063B，包含原失败2386.744ms及旧原件，带入同一20秒aux与128MiB上限；准备/关闭另预留原5000ms。数据/源/语义与冻结身份相同。

本节和绑定收据在正式第一个Electron启动前提交；三个槽仍0使用。后续只运行原定固定三个宿主，不因F0或性能失败补slot，运行中不改源码/预算/判据。原预算runnable:false作为历史设计记录保留，由本技术绑定补齐执行先决条件，不更改旧事实。


## 正式三槽结果：两次F0拒绝，未执行顺序处理

[正式收据](../../playbook/evidence/runtime-isolation-ri00-e3-order-results-20261114.json)保存执行producer `1c053c5672d23c9848f29e012ada72417128bf0d`，原报告SHA `490683f6dd4e35018e9e9714d0afae5d7dca54d3a2ea0722b20e1c69b119beb4`。conditioner及两个target恰好三个原定Electron槽均已使用，未替换；每个host8预热+本轮两个F0夹测共6块/60根，合计84根、48个metric点、18次hash、3次语义审计。无处理格/主效应对比，不能称完整ABBA/BAAB处理已执行，更不能当顺序效应阴性。

两个target的source/PMC/graph validation及metadata/hash校准均通过，calibration ratio分别0.995680/0.991539及1.001971/1.004121；**原暖段极差门拒绝**。target1三块兼容暖极差21.155/15.738/19.053ms均>15；target2为6.902/20.205/15.598ms，后两块>15。均按原original-F0-fast-bracket-rejected封存，未执行处理前80根预留或任一A/B格，没有用预算余量追加进程或抽绿点。executionCompleted表示冻结的准入/退出流程结束，controlsQualified=false与CLI exit1保留，执行错误列表空，不混为工具崩溃。

### raw与归一化CPU及完整根外窗PMC

以下沿原兼容暖Evidence用户中位的联合锚点报告；奇数一个实际根、偶数两个根等权。各分量在原精度下可加；表格保留3位小数可能有0.001ms舍入差。首metric根和不兼容根保留但不入原统计。I/C是对应完整根的外部主线程窗口，不是Evidence逐遍指令。原行、counter before/after、GC签名及逐层PMC都在私有报告/journal保存。

| 计划序列/F0块/角色 | 兼容暖点 | 原极差ms | Evidence 用户/内核/合计ms | 全根 用户/内核/合计ms | 全根外窗 I/C 十亿 |
| --- | --- | --- | --- | --- | --- |
| ABBA/0/target | 6 | 21.155 | 292.075 / 4.055 / 296.129 | 405.143 / 33.527 / 438.670 | 8.260351 / 1.724615 |
| ABBA/1/conditioning | 7 | 15.738 | 286.534 / 1.223 / 287.757 | 391.425 / 29.403 / 420.828 | 8.257901 / 1.658410 |
| ABBA/2/target | 7 | 19.053 | 278.390 / 0.611 / 279.001 | 393.722 / 28.239 / 421.961 | 8.121635 / 1.656117 |
| BAAB/0/target | 5 | 6.902 | 271.392 / 1.767 / 273.159 | 373.243 / 28.412 / 401.655 | 8.117712 / 1.588095 |
| BAAB/1/conditioning | 7 | 20.205 | 276.264 / 3.220 / 279.484 | 379.481 / 30.331 / 409.812 | 8.220870 / 1.625642 |
| BAAB/2/target | 7 | 15.598 | 273.350 / 1.632 / 274.982 | 386.761 / 29.961 / 416.722 | 8.161819 / 1.631811 |

F0 target−居中conditioning的派生分量如下，仅用于保存用户要求的归一化口径。原F0在暖极差失配时返回deltas=null，下面描述值不替换这个原门事实，不把F0块重命名成A/B格，也不把conditioning视为已证明稳定的参考。

| 计划序列/F0差额 | Evidence 用户/内核/合计ms | 全根 用户/内核/合计ms |
| --- | --- | --- |
| ABBA/前T−C | 5.541 / 2.832 / 8.372 | 13.718 / 4.124 / 17.842 |
| ABBA/后T−C | -8.144 / -0.612 / -8.756 | 2.297 / -1.164 / 1.133 |
| BAAB/前T−C | -4.872 / -1.453 / -6.325 | -6.238 / -1.919 / -8.157 |
| BAAB/后T−C | -2.914 / -1.588 / -4.502 | 7.280 / -0.370 / 6.910 |

### 实际顺序与间隔审计

纯封存审计CLI `audit-e3-pair-order.mjs`于采样结束后以分析candidate `59288562d453c0ffdd5568d23ceff8e661579cc7`新增，不冒称原执行candidate含此审计。六块实际F0先后均target→conditioning→target；以原global journal核对start/end序号、同controller时钟、10个原ticket及最后一根后3次hash的实际落盘记录，全部闭合。真正A/B顺序处理格为0，因此没有B格间隔或A/B间隔差可验证，空集合不算通过。

六块54个同host相邻row.start−前row.end实际间隔169.067～198.655ms，全部≥150ms；未跨host减row时钟。对全部84根按host+ticket连接原报告/journal，原行逐项相同，前后birth一致；从原始逐线程/层counter重算84个外窗PMC与原值全部一致且专属。各根output/源/23 sessions/3859 plan/12×69266行符合冻结图，不用整根或合计CPU替代暖Evidence用户门。

### 预算、恢复与累计账本

读体含3次末尾语义审计41274.209ms/200000ms；其中84根用户37171.633、内核3738.706、合计40910.339ms，末尾审计363.870ms。Evidence十二遍累计用户24415.568、内核441.291、合计24856.859ms，余部用户12756.065、内核3297.415ms；各作用域算术闭合。84个整根外窗指令累计779648645418、周期160824671230，均保留逐层原值，不能拿这些全根计数填成逐遍指令或物理频率。

正式hash CPU403.575ms/4000ms，wall57599.175ms/900000ms；controller自身2716.727ms、counter EOF累计127.472ms、准备5885.057ms及原5000ms尾段reserve合计收费13729.261ms/25000ms（不同时间费用快照间的0.005ms差额保留）。journal3138839B/32MiB，含原失败准备的全部保留输出10227541B/128MiB，未知成本gap=false。没有为读数不合格削减清理、删除失败或转用旧slot。独立离线审计Node完整子进程CPU72.203ms另列，不倒填正式墙钟。

三个Electron exit0；owner/method/binding及单槽恢复，未ACK/retained0，读失败/拒写/metadata丢失0。3个正式Inspector和原/新2个专用Node Inspector共5个实际端口均拒绝连接，原/新Node均退出；实际Peer本轮零附着/重启。三末尾审计各69266行且语义SHA一致，8534内容文件+1空fence逐项SHA与生产Module身份均未变。正式Profiler wire及拒绝尝试均0，新资格只在wire前断言拒绝1次，未启动Profiler，无新增native计数库。

执行candidate119项聚焦与新Node真实接缝通过，采样后CLI对原F0/result原门、所有边界/实际间隔、CPU与PMC原始计数核对通过，syntax/diff/引用一致性通过；实施者自审，分析candidate CI查询无workflow/status，不称绿色CI。未跑产品完整build/release/模型或新现场。

本轮E3实际owned从35到38，已知产品读CPU下界510790.475+41274.209=552064.684ms，旧C未知成本继续保留。专用Node累计2次（原输出预算失败1、用户明确授权的新成功1），原2MiB失败不改判。固定三个正式槽已结束，未新增/替换。新的完整块顺序因素本轮尚未获得处理数据；后续只能先用封存事实继续查资格波动，不能原样重跑或把没有处理当反证。RI-00仍缺现场自然同进程快到慢及机制复现，原3.95秒缺口保持，不开始重构。


## 后续离线拆解

[84根五处F0暖段超门、工作量/执行速率及新校准排布设计](runtime-isolation-ri00-e3-order-variation.md)保留本轮五失败与0处理；只读原件，不新增宿主或读取。新设计专门诊断暖段统计，不授予原F0或现场资格，不将本轮重命名为成功顺序对照。
