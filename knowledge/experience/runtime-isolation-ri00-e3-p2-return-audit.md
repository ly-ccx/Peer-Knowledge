# RI-00 P2：封存返回预算审计、同候选P0与新三宿主对照

2026-11-14。本轮按用户明确新授权，依次执行封存预算覆盖核对→锁同一candidate的P0B→冻结新P2预算→固定3宿主。原P失败与未用槽作废不改写，不增加失败替代宿主，不重构。已过00-adr-map.md、Accepted 96-task-execution-responsiveness.md、Proposed 128-local-runtime-isolation-and-bounded-query-contract.md；C级独立诊断，产品运行/授权/Evidence/存储/System Context边界不动。

## 执行前发现与明确调度

此前预留40根是ON-target/ON-reference/OFF-return-target/OFF-return-reference各10根，另预留三个末尾语义审计，顺序正确。36次150ms只覆盖4×9块内等待；块间尚无显式150ms，原“全部相邻根”文字与实现不完全一致。P2明确每块开始固定等待150ms，加9次块内等待，所有mode/所有role相同：返回总40次等待6000ms。warm仍固定每host8根，无新增根。

预算从完成且通过原门的完整OFF两块20根估计，包含所有clock和dense首点，不按GC挑点；冷预热实际花费留在spent，不能乘成所有未来暖根。读CPU预留40×max(750ms,已封存OFF最大根CPU×1.5)+3×500ms语义审计。wall另取CPU/wall两类读体估计的较大者，再列40×150ms等待、24000ms hash RPC余量、30000ms Profiler/counter setup-stop余量、5000ms控制器余量和原90000ms清理。所有预测均为明确的准入计划假设，不能保证未知未来工作耗时；实际每读/异常/超额保留并停止。

hash总帽2秒CPU/12次剩余调用需有完整余量，Profiler原每target setup-stop CPU≤1秒、session wall≤10秒、读体wall≤6秒，控制器/aux原20秒及准备关闭5秒不变。新预算仍3 Electron/2同时/零替换、读体CPU90秒/墙钟15分钟、144根/3语义审计、原15ms/2ms/10%门及1ms interval。先验证精确边界拒绝、缺少余量拒绝、逐动作与封存成本映射，之后同候选P0B。

P0B独立固定1 Node/6场景/9根，沿用90秒/8秒fixture读CPU/10秒controller/32MiB/16MiB profile，不承接旧P0或P未用槽；[执行前P0B预算](../../playbook/evidence/runtime-isolation-ri00-e3-p0b-budget-20261114.json)。P2机器预算必须在P0B通过后写入具体candidate、P0B原SHA、覆盖审计SHA并提交推送，才启动Electron。P0B失败不追加Node；P2失败不补Electron。实际Peer不附着/重启。

## 封存覆盖审计与同候选P0B已通过；P2执行前冻结

候选`fce27eb2`，89项聚焦测试及architecture/UI/diff通过。零产品读取的覆盖CLI先验证旧P原SHA，再按四个具名role展开封存完整OFF块，得到40根/12hash/40等待；读CPU31500ms、hash CPU1200ms、墙钟186500ms预留包含返回/间隔/清理。读/校准/控制器/wall四类精确边界通过，短1微秒均拒绝。封存OFF重复展开只核对覆盖及成本包络，不声称已观察ON或未来性能。所有实际原冷读CPU留在spent，旧失败原报告不改。

同candidate及完整诊断source指纹的P0B固定1 Node，六场景/9根完成：正常clock交集宽0.704083ms，异常后0.797624ms；bodyCPU601.654ms，wall890.543ms。start丢应答0根，body失败1根，stop丢应答/派发拒绝各2根，真实stop/disable及禁用响应、恢复后正常准入均核对。原注入错误保留，非现场故障或Electron profile资格。

[新P2机器预算](../../playbook/evidence/runtime-isolation-ri00-e3-p2-budget-20261114.json)在这些检查通过后冻结，并绑定candidate、完整instrument指纹、P0B原报告SHA及覆盖审计SHA。新3槽独立，不能沿用旧P弃用槽。原3宿主/144根/90秒CPU/15分钟wall/1ms/15ms/2ms等帽均未增加；每mode按target块→reference块且每根前等待150ms。OFF入场拒绝则结束该target并按固定序列继续下一target；未知RPC、恢复不明或每target Profiler控制预算超限则整次封存，不追加业务读，可能留下未执行段并原样报告。普通计时门失败保留OFF返回，不扣开销、不挑点。

## P2实际结果：三宿主固定执行结束，整体性能资格拒绝

运行producer始终为`fce27eb2`，覆盖审计、P0B、P2的candidate与完整instrument指纹相同，预算在P0B通过后提交冻结。新3个Electron槽全部使用、最大同时2个、无替换。24个固定预热根加8个已执行块×10根，共104个Supervisor根；另3次末尾Evidence语义审计。目标1按原OFF入场失败分支结束，所以其ON/返回段没有执行，不把未执行段写成阴性。目标2完成了完整OFF→ON→OFF。

| 目标与mode | target/reference暖兼容点 | target/reference暖极差(ms) | 判定 |
|---|---|---|---|
| target1 OFF | 6 / 7 | 15.377 / 8.224 | 原15ms门拒绝，零Profiler |
| target2 OFF | 6 / 7 | 9.395 / 8.762 | 入场通过 |
| target2 ON | 7 / 7 | 13.584 / 11.932 | 图/源/PMC/metadata/校准及暖门通过 |
| target2 OFF返回 | 7 / 7 | 13.811 / 16.283 | reference原15ms门拒绝 |

目标2相对reference的三个兼容中位差依次−1.4185、−1.955、−3.572ms。开销公式为+0.54025ms，但OFF返回漂移为−2.1535ms，绝对值超过原2ms门，且返回reference暖极差超过15ms；因此**不能把0.54025ms当作已获资格的Profiler低干扰开销**。没有删除点、放宽门、扣除开销或新进程追绿。运行没有工具异常，失败来自原资格门；原报告passed=false保留。

返回预算实际准入时保留31500ms读CPU、1200ms hash CPU、186500ms wall，剩余读CPU57066.178ms、hash1732.453ms、wall855981ms，足以按预测进入完整返回段。全部已执行块按相同schedule等待：80次显式150ms等待，最短实测150.034ms。该次确实完成返回/三次语义审计与正常清理，不把预测准入替代实际证据。

## 首次取得完整Electron逐遍profile结构

只在target2 ON启动一次1ms Profiler。setup窗口主线程CPU691.516167ms，stop窗口2.735792ms，合计694.251958ms，低于原每target1秒帽；这是控制窗口CPU，不能称Profiler某个函数的精确self成本。session wall6671.684ms，10根读体wall4254.797ms，分别低于10秒/6秒帽；start/stop/disable、原件保存与恢复均确认。

真实起止marker各取得317/311个样本；profile→performance交集宽1.633037ms，profile→hrtime宽1.634954ms，hr→performance桥宽0.001751ms，均不超过2ms。8个dense根共96个逐遍跨度，最少15个确定样本，超过原每比较遍10个样本门；保留8个整根、96遍及104个互不重叠余部段，共208个跨度与完整父链。**结构门通过，性能门仍拒绝；不合并这两个结论。**

owned控制读取中的业务父链为Supervisor.list→会话投影presentSession/project→humanGateOf→acceptanceFacts→hostFacts/factsFor/evidenceRecords→readEvidenceIndex；其中有normalizeEvidenceIndexRecord→normalizeOptionalString/normalizeStringArray，以及retainInteractiveEvidence→parseInteractiveArtifactRef分支。完整frame/source映射和原profile私有封存，脱敏收据只给代码相对路径/函数链和SHA，不上传个人路径。它不是实际用户入口或自然慢状态调用链。

96遍合计的抽样wall估计为2234.369746ms；其中427.932726ms（19.1528%）落在GC/program/匿名叶帧，单列未知份额。可映射脚本叶帧中，readEvidenceIndex约525.983ms、normalizeEvidenceIndexRecord约524.582ms、parseInteractiveArtifactRef约334.540ms、normalizeOptionalString约178.437ms。它们是exclusive叶帧的抽样wall估计，不能换成函数精确CPU、指令份额或剩余30–40ms的因果贡献；可映射脚本叶帧也不排除V8把opaque native工作记在调用帧。原profile与每个样本父链均保留，不将inclusive父节点再加一次。

## 拒绝点的封存审查与证据边界

目标1 OFF的极值为277.131→292.508ms，整根GC签名minor11→12；返回reference为267.540→283.823ms，整根minor同为11，但逐遍minor签名分别在6/9个跨度出现，完整逐遍签名仍不同。两例都不能称同完整GC反事实；相同整根次数也不证明GC CPU成本相同。该次16.283ms是新的拒绝点，不替代旧K的16.182ms/2.49%或现场30–40ms形成证据。数据仍不足以唯一说明暖极差或返回漂移的物理原因。

本轮没有取得同一进程自然快→慢形成，也没有对该机制做反事实复现。已有profile只可用于结构定位，不能因为首次取得热点就提前进入重构或把P2性能门写成通过。

## 封存、恢复与交付

[结果收据](../../playbook/evidence/runtime-isolation-ri00-e3-p2-results-20261114.json)绑定新预算、覆盖/P0B/P2原SHA与相同运行source、profile、拒绝点补充及恢复审计。三Electron和P0B Node正常退出，四个实际诊断端口拒绝连接，owner/method/binding/队列恢复，未ACK和保留字节为零；guard拒写、读取失败与metadata错误均为零。8534内容文件+空fence逐项SHA一致，生产Module身份不变，实际Peer未附着/重启且原进程存活、无诊断监听。

本轮读取CPU50.217580秒（含3次语义审计），hash CPU0.531338秒，wall69.614秒，controller/aux含5秒准备关闭reserve为6.178564秒，profile169385字节，均在新预算内；读体与控制窗口、外部审计成本分别列账，不声称所有进程CPU均被精确计量。累计实际E3 owned Electron由29增加到32，已知产品读CPU下界402.814389秒，旧C未知成本继续unknown；旧P弃用槽与原失败均未复用/改判。

89项聚焦测试在运行candidate通过，architecture/UI/diff通过。运行结束后`6ca58871`只修正离线覆盖CLI的显示标签为row.label，并以同一旧封存数据重放验证；原覆盖、P0B及P2原件不修改，资源总量不变，没有再次运行P0B/P2。自审；可查询PR workflow/status为空，不称CI绿；完整build/产品回归、真实模型及安装release验收未跑。

本次固定三槽campaign已按规则结束，整体资格拒绝。后续首先使用已封存暖段/返回差额和profile结构厘清下一项可证伪因素，不原样补跑或降低门；没有新现场窗口，RI-00未闭合，重构未开始。
