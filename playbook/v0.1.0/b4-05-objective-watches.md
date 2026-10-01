# B4-05 持续观察实施契约

创建时间：2026-10-01
最后更新：2026-10-01

## 基线与授权
A 级，ADR 82 已 Accepted。负责人授权全部 B4、必要接入、修复和合入。独立调度/探测内核先实施；B4-04 #82 完成 Review/CI 合入后才接共享 Host/协议/工具。整卡一个 PR，不拆 05a/05b。

## 调度与事实
抽出共享 SchedulerKernel 的定时对账/错过 run_latest/重叠 skip 判断，Automation 使用同一内核且既有行为测试保持。目标不创建 AutomationDefinition 或新会话；设备 watch-state 保存下一次/上次定时、幂等执行、预算与降级诊断。恢复阶段 watch 先装配再放行回合；启动/恢复/时钟变化/配置变化对账。

按 ADR 82 每次实际检查都追加 observation；changed=false 只不进 Inbox，高于卡片“没有变化什么都不做”。changed=true 沿 objective_signal 事件交 SurfacingPolicy。“CI 挂了才告诉我”显式 failure_only 通知策略由当前用户语义/typed watch 配置保存；健康首次观察也存 Evidence，但不唤醒。一般首次观察仍是变化。

## 能力与安全
确定性检查作为本地观察 Provider：Manifest→Runtime Projection→Tool Call→observe PermissionGrant→实际 ToolResult/Evidence，Grant 校验有效目标/项目租约/只读探测白名单。单独的 probe adapter 只接受宿主固定 git/文件哈希/gh run list 参数，不转交任意 shell。生产进程子命令无 shell，超时/取消等待进程真实退出。文件真实路径限定工作区、拒绝 symlink 越界/绝对/.. 路径，有界读取；fs.watch 忽略 .git、node_modules、构建目录并 5 秒防抖。git 每 60 秒检查；CI 缺 gh/auth 时显示不可用原因并保留失败事实，其他目标继续。

agent probe 复用既有 Explorer 临时回合路径和 objective_probe 省档路由，readonly Projection 与运行时能力闸独立于模型提示；实际工具 Evidence 与观察关联。暂停/归档/删除/经典/丢租约时 abort，等待真实工具终止，不释放未结束任务槽。

预算计数与幂等在 device projectRuntime/<workspaceId>/objectives/，目标每天探测数与项目滚动一小时 60 次硬限；预约在执行前落盘，重启不重置。相同 scheduledAt 重试幂等，已执行不重复探测；未完成检查保留失败事实并按实际恢复策略处理。暂不声称 maxTokensPerDay 可用（B4-04 拒绝该配置）。

目标事件回合携带宿主决定的 objectiveIds，工具无法靠省略 objectiveId 绕过 report_only/propose。B4-05 的自动唤醒先保持禁止自动任务的护栏，B4-06 再接 act 配额、提议卡和用户确认；当前真实用户输入优先，旧目标 anchor 不授权新增工作。

## 必要路径
原卡 WatchRunner/各 probe/Automation scheduler/event-mapper；补共享 scheduler-kernel、观察 Provider/Evidence store/设备状态内核、runtime exports、协议 watch 通知策略/事件字段、ObjectiveStore 校验与 typed views、Host recovery/watch/stop 装配及深模块 desktop probe-turn、已有 readonly mode gate/projection/临时 Explorer 路径与 permission-gate 的 objective_probe 类型能力闸（独立于 full-access/缓存；只授予受限项目文件读取，拒绝 shell/写入/外部能力）、AgentTurnExecutor 支持实际回合来源、DelegationProvider 防省略护栏、i18n/目标页降级与用量。更新 data-store 注释和发布清单注册子路径。无新依赖；main.mjs 净增≤0。

## 退出验证
共享内核和完整 Automation 回归；真实 Git/文件变化及 symlink 越界；定时错过/重叠/幂等重启；不变化不唤醒、失败通知策略；预算/租约/经典/暂停/真实取消；CI 可用与缺 auth 降级；readonly agent tool Gate/Grant/Evidence；完整受影响包、build/typecheck/architecture/ipc、Review 与双平台 CI；使用真实 gh 只读查询运行一次“CI 挂了才告诉我”，脚本模型不替代真实模型发布验收。
