# B4-01 ExecutionScheduler 实施边界

创建：2026-10-01。目标版本：0.1.0-beta.4。分支：`PeerAgent/pa/b4-01-execution-scheduler`。

## 授权与基线
负责人已授权合入代码 #75/#76、知识 #5/#7 后继续 B4-01；四个 PR 已合入。以更新后的开发线实施本卡。依据 Accepted ADR 80 的调度决策；ADR 82 仍为 Proposed，负责人指定本卡不等于接受项目目标决策，不实施 B4-04 至 B4-06。

## 模块契约（A 级，先于代码）
- ExecutionScheduler 只控制准入、排队与回合租约，不执行工具，不决定权限、核验或签收。Plan/DelegationOrigin 与 resultAcceptance 为任务及依赖真源。
- 原地写槽每项目 1、只读槽 2；真实 worktree 写任务不占原地写槽。不能仅凭模型 isolation 参数绕过写槽；B4-02 之前不新增创建 worktree 能力。
- 全局 AgentTurnExecutor 回合上限默认 4，settings.projectAgent.concurrency 为 1–8 的整数。一次宿主 runTurn 为租约单元，内部提供方恢复不重复取槽；正常返回、抛错、取消均归还。等待租约取消时不调用提供方。高优先级不突破上限。
- high > normal > low；同级按持久化入队时间与稳定次序 FIFO。等待满 30 分钟提升一级（low→normal、normal→high），不无限提升。Provider 回合每次结束归还并重新排队，不能为一个长任务保留模型槽。
- dependsOn 全部 accepted 才放行。依赖仅允许当前项目的已存在任务；缺失拒绝，失败/取消/不可恢复中断转 waiting_user，不默认继续。已完成但未签收不得当作依赖成功。
- 排队次序写入已登记 device 根 project-runtime/<workspaceId>/scheduler.json，原子替换；重启从 Plan 重建运行计数、校验队列，只保存排序事实而不复制权限/签收真值。旧或损坏队列可由 Plan 的 createdAt 重建，不保留进程内回合租约。
- 派发与晋升先写入 Plan 槽位预留，再启动 Runner；不 await 整个任务生命周期，避免串行锁把并行变回串行。批准、取消、终态和签收都触发调度重算；依赖签收可唤醒另一项目的巡检但不会越项目放行。
- WorkSession 的 queuedBehind 只来自宿主，保存被等待任务的 id/title；Renderer 显示排队原因，不推导槽位。档案里的全局并发项明确标注所有机器人共享，沿现有 settings API 保存，不增加 IPC。

## 允许路径补齐提案
原卡已有 scheduler、supervisor、goal-runner-host、设置、档案和 i18n。落实全局回合与类型需要补齐：
- runtime-node/src/index.ts（导出）、project-agent/digest.mjs 及测试（并发设置归一化）；projectRuntime 根已登记，无新顶层数据项。
- protocol/src/delegation.ts 与测试（排队事实）；renderer 的 TasksTab.tsx/相关状态测试（表达排队）。
- desktop agent-host/agent-turn-executor.mjs 与测试（租约 finally 归还）；project-agent/project-agent-host.mjs 与集成测试（共享 scheduler 装配/读取设置）。不改 main.mjs。
- 既有 spawn priority 已暴露：tool-specs.mjs 与测试仅收敛为 high/normal/low，工具提示的同一已登记 adapter 同步说明；不新增工具。
此路径补齐需按手册 §9 由负责人确认；确认前仅准备已有允许范围内的模块与测试。

## 验证与退出
必须覆盖项目/全局上限、只读与写任务并行、真实 worktree 判定、优先级与防饿死、依赖未签收/成功/失败、重启 FIFO、异常/取消归还、等待取消不执行、同一任务不重复启动、宿主生产装配和设置保存。完整 build、typecheck、architecture、受影响包测试与双平台 CI，通过后交接 PR，不自行合并。
