# RI-00：150ms/0ms 固定三宿主对照

## 执行前冻结

沿用[前轮封存拆解与可证伪设计](runtime-isolation-ri00-e3-p2-variation.md)及[原冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-cadence-budget-20261114.json)，不修改任何资源帽、暖段15ms门、返回2ms门、方向或匹配规则。候选`cf0cc39108fbf1b2d1169d823a62be385b6c3957`实现固定三槽、ABBA/BAAB、原F0夹测、完整四格预留和失败后封存；F0失败占槽，仅继续另一原定target，不补进程。

[执行前绑定收据](../../playbook/evidence/runtime-isolation-ri00-e3-cadence-binding-20261114.json)串联干净candidate、完整诊断source、原P2/拆解/动作图、生产Module、原始fixture内容manifest、同候选测试与真实Inspector接缝报告。8534个内容文件与1空fence逐项SHA核对。98项聚焦Node测试通过，使用mock的旧Profiler测试不向Inspector发送Profiler命令。

接缝在独立Node验证进程内部打开Inspector，零Electron、不增加专用目标子进程；固定24次合成读取和6项场景通过：Profiler命令在线路前拒绝、A/B真实单槽与逐根归档、fsync失败后同原件恢复、请求应答丢失后查同id、原读错误归档并恢复后续准入。wall 2131.634ms，实际Profiler命令0，owner恢复。合成读不构成性能或现场资格。

执行器使用相同共享块调度与durable reader；远端label始终`cadence-root`，阶段/arm仅在controller归档，B不创建0ms timer。每根完整保留用户、内核、合计CPU、全根PMC及逐层数据、GC签名与原始counter边界；逐块只从同host的9个row.start−前row.end核对实际间隔，不把B请求等待0称为实际0。Profiler在传输层硬拒绝；正式运行有任何尝试也判恢复不合格。每格校准同时对照F0的两个已冻结anchor（均须10%内），不据结果选择anchor。

恢复保持先fsync、再ACK，未知request仅查同ticket；清理先断CDP、再退出自有host，启动失败也走有界清理。启动前绑定与接缝CPU计入controller准备成本，运行累计读体/hash/controller预算不会按格清零；处理前完整返回段、间隔、校准与清理预留不够则不进入B。实际Peer未附着或重启，现场与重构均不启动。

本节与绑定收据在首次Electron启动前提交。预算的`runnable:false`保留为历史设计状态，由本次单独技术绑定补齐先决条件，不改写旧文档或旧失败。正式结果随后原样封存；执行结构通过不能冒称低干扰或剩余残差归因。
