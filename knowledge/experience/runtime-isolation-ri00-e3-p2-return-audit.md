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
