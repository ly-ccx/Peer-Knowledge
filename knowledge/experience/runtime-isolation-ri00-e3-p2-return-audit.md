# RI-00 P2：封存返回预算审计、同候选P0与新三宿主对照

2026-11-14。本轮按用户明确新授权，依次执行封存预算覆盖核对→锁同一candidate的P0B→冻结新P2预算→固定3宿主。原P失败与未用槽作废不改写，不增加失败替代宿主，不重构。已过00-adr-map.md、Accepted 96-task-execution-responsiveness.md、Proposed 128-local-runtime-isolation-and-bounded-query-contract.md；C级独立诊断，产品运行/授权/Evidence/存储/System Context边界不动。

## 执行前发现与明确调度

此前预留40根是ON-target/ON-reference/OFF-return-target/OFF-return-reference各10根，另预留三个末尾语义审计，顺序正确。36次150ms只覆盖4×9块内等待；块间尚无显式150ms，原“全部相邻根”文字与实现不完全一致。P2明确每块开始固定等待150ms，加9次块内等待，所有mode/所有role相同：返回总40次等待6000ms。warm仍固定每host8根，无新增根。

预算从完成且通过原门的完整OFF两块20根估计，包含所有clock和dense首点，不按GC挑点；冷预热实际花费留在spent，不能乘成所有未来暖根。读CPU预留40×max(750ms,已封存OFF最大根CPU×1.5)+3×500ms语义审计。wall另取CPU/wall两类读体估计的较大者，再列40×150ms等待、24000ms hash RPC余量、30000ms Profiler/counter setup-stop余量、5000ms控制器余量和原90000ms清理。所有预测均为明确的准入计划假设，不能保证未知未来工作耗时；实际每读/异常/超额保留并停止。

hash总帽2秒CPU/12次剩余调用需有完整余量，Profiler原每target setup-stop CPU≤1秒、session wall≤10秒、读体wall≤6秒，控制器/aux原20秒及准备关闭5秒不变。新预算仍3 Electron/2同时/零替换、读体CPU90秒/墙钟15分钟、144根/3语义审计、原15ms/2ms/10%门及1ms interval。先验证精确边界拒绝、缺少余量拒绝、逐动作与封存成本映射，之后同候选P0B。

P0B独立固定1 Node/6场景/9根，沿用90秒/8秒fixture读CPU/10秒controller/32MiB/16MiB profile，不承接旧P0或P未用槽；[执行前P0B预算](../../playbook/evidence/runtime-isolation-ri00-e3-p0b-budget-20261114.json)。P2机器预算必须在P0B通过后写入具体candidate、P0B原SHA、覆盖审计SHA并提交推送，才启动Electron。P0B失败不追加Node；P2失败不补Electron。实际Peer不附着/重启。
