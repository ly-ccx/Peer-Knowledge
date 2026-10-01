# B4-05 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-05 WatchRunner 与触发器。负责人已授权完成全部 B4、必要接入、Review 修复和合入。

## 分支与提交
- 分支：PeerAgent/pa/b4-05-objective-watches
- 基线：dev 2172597a，B4-04 已合入。
- 提交：517c5b4b（最终）；代码 dev 合入 efb9ec9b
- 代码 PR：#83；知识 PR：#14

## 改了什么
- 共享 SchedulerKernel 与 Automation 接缝；目标按最新错过时点检查、重叠跳过。
- WatchRunner、固定 Git/文件/gh adapter、观察 Provider/SDK/Evidence、设备预算与投递游标；真实取消等待进程结束。
- 宿主恢复/暂停/租约装配、临时只读 objective_probe 回合与能力硬闸；禁止 full-access/缓存绕过。
- 宿主 objective_signal 来源与实际观察 Evidence 决定通知，不能借旧用户锚点升级打扰；合法目标原始引用保留。
- 目标页显示实际探测用量、上次/下次检查和可读降级原因。

## 与卡片的偏差
ADR 82 要求每次实际检查均保存观察，changed=false 仅不进 Inbox。必要路径和设备子路径已先写知识 #14；无新依赖、无新 IPC、main.mjs 未改。agent probe 没有 token 硬限，B4-04 已拒绝 maxTokensPerDay 配置。

## 验证
- 完整 build、typecheck、architecture:check、IPC catalog、diff check 通过。
- Runtime 933 通过；Protocol 173 通过。
- Desktop 最终 5194 通过、1 个并行失败、5 既有跳过；失败文件独立重试 3 通过。首轮两个失败文件独立重试 145 通过；最终相关集成 47 通过。
- 真实文件/目录哈希、fs.watch 防抖/暂停恢复/空闲不重复、真实 Git、真实进程取消、Evidence/Inbox 中断重试、每日/每小时预算与只读 Projection/Grant/Evidence 测试通过。
- 真实 gh 查询 CI 成功，failure_only 健康检查保存证据、0 唤醒、重复对账没有重复观察；证据已存知识仓。未使用模型，真实模型/UI 验收留 B4-R。
- 最终 517c5b4b 的 CI 36846361589 双平台通过；三个 Review（aggregate completed 状态、实际任务结束状态、越界路径访问前硬拒绝）均红→绿并解决。
- 并行全仓构建曾遇到既有 conversation-store dist 清理竞态，串行全仓构建通过；B4-R 收口构建可靠性。

## 架构影响
A 级 ADR 82。观察能力沿 Manifest→Projection→Call→observe Grant→Evidence，预算/幂等在设备 projectRuntime 下；便携目标与全量观察留 projects。Renderer 只展示。自动观察回合来源由 Host 决定，B4-05 仍拒绝自动任务控制，B4-06 再接自主档位。

## 文档偏差
知识 #14 同步 ADR、清单与实际只读 CI 证据。健康首次观察必须留存，failure_only 不唤醒。

## 未完成与后续
代码 #83 已合入 dev efb9ec9b；继续 B4-06 和 B4-R。Beta4 未发布。
