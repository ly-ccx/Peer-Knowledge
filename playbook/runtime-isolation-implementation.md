# 本地运行时隔离实施包

创建时间：2026-11-11
最后更新：2026-11-11
状态：待 ADR128 评审的实施计划；没有产品实现已完成的暗示。

决策：[ADR128](../knowledge/decisions/128-local-runtime-isolation-and-bounded-query-contract.md)。调查：[响应性架构审查](../knowledge/experience/desktop-runtime-responsiveness-architecture-audit.md)。本文件不创建新的执行权限、生命周期策略或存储真源。

## 1. 固定交付规则

以步骤的实际入口/事实源/状态迁移为单位交付，不按“拆出几个文件”计数。每个阶段说明将退出的旧入口，必须覆盖正常、拒绝、失败、超时、取消、崩溃、迟到和已有状态恢复。实验数据使用隔离根；不安装/重启日用应用，不拿个人任务试错。

源码实现、确定性验证、真实模型/平台验证、已有状态恢复和发布验收分别登记。每天做阶段内验证；发布时才执行合并所有 PR 的完整候选与全产品门禁。Stage 之间不能用未经证实的“已流畅”作依赖。

## 2. 阶段与退出条件

| 阶段 | 入口与交付 | 主要既有 Module | 退出条件 |
|---|---|---|---|
| RI-00 基线与预算 | 将一次交互关联到 IPC 等待、处理、查询、Store 与发送；记录 15/30 秒周期；保留全部 >50ms 段及未知差值 | `slow-timer-probe`、IPC owner、既有 perf/product harness | 同一候选的可重现坏基线；测量自身成本单列；无 profiler 真实交互对照可重复 |
| RI-01 查询职责 | PendingGrant 空结果不 hydrate session；Badge/TaskSummary/Report 分离；Evidence 按键索引；移除列表中业务修复 | Application Service、Bot Directory、SessionSupervisor、GoalPlanEvidence、TaskOverview | 原坏基线先红；结果语义一致；scope/版本/字节/复杂度可观测；只读测试禁止 canonical 写；历史缺核验不补 passed |
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

完成架构与决策审查，创建 ADR128 提案、实施包与审查报告；完成一次有限进程隔离可行性对照。首轮实验启动超时单独保留。没有更改 Peer-Agent 产品源码、运行安装或个人任务；没有运行模型/工具，也没有宣称当前卡顿已修复。后续实现以 ADR128 的具体评审和各阶段证据为准。
