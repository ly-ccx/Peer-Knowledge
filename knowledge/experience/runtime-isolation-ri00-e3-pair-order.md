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
