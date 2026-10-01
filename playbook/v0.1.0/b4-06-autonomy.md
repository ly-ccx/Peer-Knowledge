# B4-06 自主档位实施契约

创建时间：2026-10-01
最后更新：2026-10-01

## 基线与授权
A 级，ADR 82。B4-05 代码 #83 已合入 dev efb9ec9b，知识 #14 已合入 main f6bf183。负责人已授权自行完成全部 B4、必要路径、Review 修复、合入及发布，无需重复确认。

## 权限与事实
report_only 在运行时拒绝目标任务。propose 与达到限额的 act 保存冻结任务意图并投影真实「开始 / 暂不」卡；只有当前 canonical 用户输入的 answerTo 匹配卡片且肯定同意，才沿既有 DelegationProvider→Supervisor 开任务。批准任务使用冻结意图，模型不能借批准换工作。暂停、改档、改目标、丢租约、经典模式后陈旧提议不授权任务。

act 自动开任务必须来自 Host 的 objective_signal、实际成功探测 Evidence、同项目活动目标。省略 objectiveId 时只允许唯一宿主目标，多个目标须明确指定。旧原始用户锚点仅引用，不是新增任务授权；当前用户输入优先。自动任务低优先级，每个目标每个 UTC 日最多 min(3, configured budget) 次，执行前持久化预约；同一事实批次只能创建一个任务，重启、重试不重复计数或创建。失败创建保守保留预约，真实 GoalPlan 的 objectiveActionId 用于恢复链接；连续三个目标任务失败后降为提议。

签收默认 confirm。只有目标上的显式当前用户自动签收同意，保存 canonical approval anchor，Host 验证真实用户事实后才允许 auto；独立核验与外部/破坏性操作规则仍适用。模型不能靠 autoAccept 或摘要授权。

## 存储与上下文
设备 project-runtime/<workspaceId>/objectives/actions-state.json 保存提议、冻结输入、事实幂等键、每日预约和实际 session 链接，原子写、损坏 fail closed；不导出或跨设备迁移。便携目标保留 autoAccept 与真实批准锚点，锚点缺失时无效。L1 经已有 ContextSource 增加档位规则；L7 只投影实际目标/观察/待批准动作，模型文本不是权限或证据。

## 必要路径
原卡 Source、DelegationProvider、acceptance、card-projection；补深 ObjectiveActionKernel/持久状态及测试、ObjectiveService/Store/tool schema、SessionSupervisor/GoalPlan origin 幂等、typed protocol/Source 事实、Desktop Host/watch/facts 装配、已有回答入口与目标 typed 设置/SVG 自定义控件/i18n。发布清单与 data-store 登记设备子路径。无新增 IPC、工具、依赖，main.mjs 净增≤0。

## 退出验证
三档真实 Provider/Service 行为；伪造与省略身份、陈旧/跨项目/失败探测拒绝；提议冻结/当前点击/否定/重启；每日三次、跨日、并发与幂等恢复；默认 confirm 与显式自动签收；L1/L7；完整 build、typecheck、architecture、IPC、受影响包测试、Review 与最终 macOS/Ubuntu CI。
