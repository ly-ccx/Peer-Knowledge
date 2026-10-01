# B4-07 熔断与恢复实施契约

创建时间：2026-10-01
最后更新：2026-10-01

## 授权、基线与分级

负责人已授权自行推进全部 B4、必要接入、验证、Review 与合入。基线为 B4-03 代码 `46c2af0e`、知识 `b65068b`。B4-07 原卡 B 级；输入已送达与已执行必须分别记账，补齐既有 cursor 的执行确认属于存储边界，因此本实施按 A 级治理。对应 ADR 80、85 均 Accepted。分支 `PeerAgent/pa/b4-07-recovery`。

## 熔断边界

每项目代理连续五个失败的完整回合后打开十分钟。提供方内部重试不重复计数，用户抢占/主动中止不算失败，成功重置。状态在已登记 device 范围 `project-runtime/<workspaceId>/circuit-breaker.json` 原子保存；重启不能重置开路时限。开路不调用模型、不自动唤醒；新输入仍持久入队。可手动半开试一次，成功闭合、失败重新开路；到期只放一个恢复试运行。沿现有 agent_unavailable 决策卡与重试入口表达，不创建旁路能力。

## 恢复接口与顺序

Recovery 深模块对每项目串行、并发调用合并，其他项目独立：

1. 获取或确认宿主租约。
2. 输入队列消费者写 canonical 用户消息并推进送达 cursor；恢复未完成执行的已送达输入。
3. 按收件箱 cursor 重放事实，不先确认消费。
4. ExecutionScheduler 从 Plan 重建本项目排队；不启动模型或 Goal。
5. Goal Runner 按 ADR 73 对本项目进行中的计划恢复 checkpoint；此阶段只恢复状态，暂不启动泵。
6. 激活项目 Watch。
7. 激活项目小结计时。

全部完成后才开放项目执行准入，恢复正在进行的 Goal、晋升队列、执行输入/唤醒。Goal Host、Scheduler、Supervisor 共用 readiness 门，防止旧 main 启动恢复先跑委托任务。经典 Goal 沿原恢复入口，委托 Goal 由项目恢复入口负责；main.mjs 仅替换原装配行，净增不超过零。失去租约/经典界面/归档项目撤销就绪与自动维护。单项目阶段失败落 device `project-runtime/<workspaceId>/recovery.json` 诊断，其他项目继续。

输入 cursor 新增执行确认，送达与执行不可混为同一事实；成功完成后确认对应队列输入。若在回复写入后、执行确认前崩溃，从 canonical agent_reply 的实际 replyTo 还原已回复事实；不能把 agent_turn、不可用卡、模型文字当执行成功。旧消息和 jsonl 不改写，旧输入队列记录可重放；重复任务沿既有 spawnIdentity，回复沿 canonical 输入确认去重。当前进程 mailbox 不重复入队同一 inputId。

## 取消与删除

取消中止该 Plan 的全局回合租约（含 worker、Explorer、Verifier），暂停并等工具结算后走既有隔离清理；失败/取消依赖仍沿既有 waiting_user 决策卡。已完成待验收/已签收不能被取消覆写。删除机器人先校验和确认受管目录，再取消进行中的全部任务、停止 Runner/Watch/小结/目标扩展口并释放租约，最后交既有 lifecycle 移除/归档。失败保留结构化结果以便重试；不碰真实用户数据。

## 必要路径

原卡 circuit-breaker/recovery/runner/session-supervisor/project-agent-host；既有 input-queue、HostLease 的归档档案过滤、ExecutionScheduler、Goal Runner 与 Goal Host 恢复门；application service/bot-lifecycle 的删除与重试接缝；main.mjs 原租约/装配/恢复行替换；data-store projectRuntime device 登记说明；runtime-node 导出；project-facts/card-projection 的不可用卡事实与相关聚焦/生产集成测试、强杀子进程测试夹具。无新依赖、无新 IPC、无新工具；目标停止接口由 B4-04/05 接入。

## 验证与已发现文档偏差

分层文档 §7.4 的“三条同指纹任务”和 §7.6 的旧顺序与 Accepted ADR 80/当前 B4-07 不符，按已批准的卡片/ADR 对齐为五次代理回合与以上七阶段。补熔断持久/手动与到期关闭、取消 Explorer/Verifier 和失败依赖、已完成保护、删除顺序、经典/无租约、每项目错误隔离、每阶段真实 kill -9 后恢复一致性，以及 affected package 全套、build/typecheck/architecture/ipc 与当前提交双平台 CI。强杀仅针对测试创建的子进程，数据仅临时目录；脚本执行器不称为远程模型证据。
