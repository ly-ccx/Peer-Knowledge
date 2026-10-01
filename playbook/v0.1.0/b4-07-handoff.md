# B4-07 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-07 熔断、取消级联、重启恢复。

## 分支与提交
- `PeerAgent/pa/b4-07-recovery`
- 代码 `f2a6d3214cea0124db04b072d698db79c49fe41b`，基线 dev `46c2af0e`。
- 代码 [#80](https://github.com/ly-ccx/Peer-Agent/pull/80)。

## 改了什么
- CircuitBreaker 持久化五个失败完整回合、十分钟开路与单次半开；内部重试不重计，抢占不算失败；手动与到期恢复。恢复失败状态和卡片写入间隙，不调用模型。
- Recovery 深模块统一七阶段就绪屏障，隔离项目错误与 device 诊断；Goal、Scheduler、Runner 共享准入，等待全局槽位后重新检查。
- InputQueue 保存独立执行确认；canonical agent_reply.replyTo 修复确认间隙；同 inputId 去重，强杀遗留锁按 PID 存活检查收回。
- 取消共享轮次里的 Explorer/Verifier、等待工具结算并清理；完成结果受保护，失败依赖变为用户决策。删除先停项目、释放租约并提交归档/清理进度，再清理目录；清理失败可续做，归档保存失败恢复准入。归档不再取得租约。
- 后续真实回合替代旧不可用卡时，投影收起旧重试操作并保留历史。

## 与卡片的偏差
路径及存储边界已先写 [实施契约](b4-07-recovery.md)，依据负责人全 B4 授权推进。原卡 B 级，输入执行 cursor 新边界按 A 级治理；ADR 80/85 Accepted。无新依赖、工具或 IPC；main.mjs 净增零。

## 验证
- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、Desktop `ipc:check`、`git diff --check`：通过。
- runtime-node 完整套件：892 通过，0 失败/跳过。
- desktop 完整套件：5182 通过，0 失败，5 既有跳过。
- 实际 fork 子进程并 SIGKILL：lease/inputs/inbox/queue/tasks/watch/digest 七阶段，以及 input_written/task_created/reply_written 三间隙；十个重启场景与未中断基线共 11 测试全部通过，每场景一条用户输入、一个任务、一条回复。
- 夹具采用真实临时磁盘、HostLease、ConversationStore、Scheduler、生产 Goal host/Executor/Provider/Grant/Evidence；模型为脚本执行器。测试租约一秒，强杀后等待过期；不代表生产租约即时接管。
- 缺失熔断卡片、旧重试卡、排队期间失去准入三回归先失败后通过；其余屏障、取消/删除、经典界面/归档/无租约聚焦覆盖通过。
- Protocol 173 通过；Review 补修后的 build/typecheck/architecture 与完整受影响包再次通过。
- 首提交双平台 CI 36835997612 已通过；当前补修提交双平台 [CI 36836813306](https://github.com/ly-ccx/Peer-Agent/actions/runs/36836813306) 运行中，合入前必须完成。

## 架构影响
输入送达与执行分账，canonical reply 与 Plan 仍为执行事实真源；新状态位于已登记的 projectRuntime device 存储。BotProfile 可选 deletionCleanup 保存已授权删除的剩余清理步骤。恢复、取消与卡片走现有治理接缝；旧 jsonl 不重写。

## 文档偏差
分层文档旧失败阈值/恢复顺序已按 Accepted ADR 与 B4-07 对齐。知识写入 companion repo。

## 未完成与后续
目标停止扩展口留 B4-04/05。本卡 CI/Review 完成后合入；继续 B4-08 与项目目标卡、发布卡。Beta4 尚未发布；真实模型/打包/UI 证据不由脚本场景替代。
