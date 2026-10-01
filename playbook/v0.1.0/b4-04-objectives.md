# B4-04 项目目标实施契约与 ADR 82 开工评审

创建时间：2026-10-01
最后更新：2026-10-01

## 授权与基线
负责人明确授权自行完成全部 B4、必要路径、修复和合入。A 级，开工前本次技术评审将 ADR 82 转 Accepted；用户已选定目标/只读观察/三档自主方向，无新增产品方向。代码分支 `PeerAgent/pa/b4-04-objectives`，从最新 dev 开；B4-08 热点合入后再改 tool-specs/Host。知识单独分支同名。

## 评审结论
- ProjectObjective 为跨任务计划，GoalPlan 仍是执行/证据/签收单位；不是新父任务表。
- Schedule 使用既有 AutomationSchedule，后台调度复用共享内核但不复用 AutomationDefinition；每次观察持久化，无变化只不进 Inbox。这两项按 ADR 82 高于卡片。
- 单值硬权限真值在 host。agent_proposal 以 paused + pendingConfirmation 保存，用户确认后才 active；创建、升自主档位、恢复需要实际当前 canonical user_input 或持久化的用户界面命令。旧消息、引用/工具/目标摘要不能授权。模型不能自行设 confirmed 或 autoAccept。
- achieved 必须有该目标的实际通过信号与相关已完成/签收任务 Evidence，文字描述不算；用户可以重新打开。所有引用检查 workspace/objective 归属。
- 后台观察仅 observe Grant，通过 Provider→Manifest→Projection→Call→Grant→Evidence。report_only/propose/act 限制按宿主实际回合来源继承，不能通过省略 objectiveId 绕过。外部操作仍 confirm。
- 日自动任务与日探测预算及项目每小时 60 探测硬限。可选 maxTokensPerDay 在真实硬限接入前拒绝配置，不接受后忽略；Beta4 不宣传已支持 token 配额。此可选字段的保守拒绝不改变默认探测/任务预算合同。

## B4-04 边界
- 协议补齐 ADR 的 outcome/successSignals/milestones/typed watches/budget 与观察、任务关联、IPC 请求/响应；沿用旧 objectives.ts 名称，明确旧 schedule 字符串/trigger 为旧协议草图，没有已落盘目标需要迁移。successCondition 卡片别名不另立第二个真值。
- ObjectiveStore 在 portable projects/<id>/objectives 下原子定义与追加观察，校验、版本/来源、作用域、查改暂停恢复、相关 sessionIds 与持久幂等。存储只有目标，不持有模型执行。
- 新 ObjectiveService 深模块集中当前用户授权、目标归属、状态变更、证据达成、任务绑定；DelegationProvider 在既有能力链 dispatch 目标方法，避免扩大中心业务；新增工具 prompt 与白名单。
- 桌面装配沿 live port 接入服务；新 typed `project-objectives:*` IPC、preload/clientApi/capability interface/catalog 与 registrations。有界 UI 命令先持久化真实用户动作事实，再改变授权；Renderer 只提交结构化命令。
- ObjectivesTab 紧凑显示状态、达成样子、里程碑/任务、最近/下次检查、预算、自主档位，使用现有自定义 Dropdown/SVG；旧 Automation 区保留。任务清单与目标互链。
- 日预算计数、探测幂等与运行时诊断沿 device projectRuntime 注册子路径；B4-04 不启动后台探测，B4-05 接 Recovery/watch/stop seam，B4-06 接最终自主执行限制与卡片。

## 必要路径
原卡 ObjectiveStore/工具定义/Provider/白名单/data-store/IPC/ObjectivesTab/i18n；补 protocol objectives/delegation/project 与导出、ObjectiveService+测试、objective-tool-specs schema/validator（从中心 tool-specs 导入）、runtime exports、Host/project-facts/live port/LocalToolHost装配、typed preload/clientApi/API methods/IPC catalog生成、tools prompts、BotProfileDrawer/TasksTab/drawerState与样式及聚焦/集成测试。main.mjs 净增不超过零；不加依赖。路径以 rg 确认实际位置。

## 退出验证
纯存储/原子重启/幂等/作用域/坏配置；无锚点、旧锚点、非用户提权拒绝；代理提议确认；状态与真实信号/Evidence；目标/任务互链；typed IPC/UI命令真实事实；经典/无租约无后台写；完整受影响包和 build/typecheck/architecture/ipc；PR Review/双平台 CI。
