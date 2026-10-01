# B4-05 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-05 WatchRunner 与触发器。负责人已授权完成全部 B4、必要接入、Review 修复和合入。

## 分支与提交
- 分支：PeerAgent/pa/b4-05-objective-watches
- 基线：dev 2172597a，B4-04 已合入。
- 提交：634057f0 feat(objectives): run governed durable readonly watches
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
- Runtime 931 通过；Protocol 173 通过。
- Desktop 首轮 5193 通过、2 失败、5 既有跳过；两个失败文件独立重试 145 全部通过，符合既有 CI 重试规则。最终改动相关集成 47 全部通过。
- 真实文件/目录哈希、fs.watch 防抖/暂停恢复/空闲不重复、真实 Git、真实进程取消、Evidence/Inbox 中断重试、每日/每小时预算与只读 Projection/Grant/Evidence 测试通过。
- 真实 gh 查询 CI 成功，failure_only 健康检查保存证据、0 唤醒、重复对账没有重复观察；证据已存知识仓。未使用模型，真实模型/UI 验收留 B4-R。
- 本 PR 的 Review 与双平台 CI 等待最终提交。

## 架构影响
A 级 ADR 82。观察能力沿 Manifest→Projection→Call→observe Grant→Evidence，预算/幂等在设备 projectRuntime 下；便携目标与全量观察留 projects。Renderer 只展示。自动观察回合来源由 Host 决定，B4-05 仍拒绝自动任务控制，B4-06 再接自主档位。

## 文档偏差
知识 #14 同步 ADR、清单与实际只读 CI 证据。健康首次观察必须留存，failure_only 不唤醒。

## 未完成与后续
Review/最终双平台 CI 后按授权合入；继续 B4-06 和 B4-R。Beta4 未发布。
