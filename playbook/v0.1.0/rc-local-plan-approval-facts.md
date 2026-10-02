# RC补修：本地计划批准事实传递

2026-10-02，Accepted。负责人已授权自主完成全部功能及自测修复。A级：修复本地批准事实的持久投影与Verifier事实准入；先更新ADR80和运行时契约，再实现。

## 真实失败

实际rc.2 / 默认GPT6 Astra双写任务均修改正确，并附新鲜read_file或Bash检查。A核验失败理由同时包含：要求的编辑/检查任务未拆分，以及缺本地批准历史。后者确有实现遗漏：两个ApprovalStore都已approved/local_ui，GoalPlan.approval为空，Verifier Source只投影目标/叶子/标准。两种原因必须分列；不能因此宣布A成功、签收或合回。见evidence/rc2-installed-complex-astra-failed-20261002.json及rc2-local-plan-approval-diagnostic-20261002.json。

## 边界

- 复用既有GoalApproval，不新增存储字段、能力、IPC、依赖或权限。真实本地批准先写ApprovalStore，监督者从自己的store回读同workspace/session/plan/conversation绑定的approved/local_ui记录，冻结confirmationId/decidedAt/decidedBy到GoalPlan.approval，再启动/排队。
- 新共享local-plan-approval Module收拢记录绑定和闭合投影。open/stale/denied/expired、政策或文字声明、外工作区/会话/计划记录不能成为人工批准。写盘失败不得启动。已批准且尚待准入的重放应能完成崩溃窗口恢复；排队/暂停/取代与能力授权门继续保持。
- GoalPlan.approval是已发生的计划准入事实，保留重启与ApprovalStore压缩后的历史。不是PermissionGrant、工具执行Evidence或结果签收，不参与核验报告工具引用白名单。
- ApprovalStore压缩保留已批准plan_approval的折叠记录，避免决定刚落盘即被压缩删除导致无法回读/崩溃恢复；普通已终结工具批准保持原压缩规则，不新增存储目录或参数。
- Verifier既有Source将有限批准字段加入L7事实brief；没有字段明确unknown，不从running或助手声称推测批准。经典计划已有GoalApproval兼容。任务已有goal_get_plan可读该事实，不另增工具或提示来源。
- 旧已批准且记录已被压缩的计划保持unknown，不补造历史。测试失败中的任务拆分要求保留，另跑明确对应产品目标的新鲜完整流程；不能修改旧证明。

## 允许改动

- 新packages/runtime-node/src/project-agent/local-plan-approval.mjs及.test.mjs。
- packages/runtime-node/src/project-agent/session-supervisor.mjs及.test.mjs。
- packages/runtime-node/src/project-agent/approval-store.mjs及.test.mjs：仅保留已批准计划的折叠历史。
- apps/desktop/electron/main/project-agent/project-agent-application-service.mjs及.test.mjs。
- apps/tui/src/project-agent/tui-project-host.ts及.test.ts。
- packages/system-context/src/sources/verifier-source.mjs及src/verifier-source.test.mjs。
- apps/desktop/electron/main/agent-host/goal-runner-host.test.mjs、packages/runtime-node/src/goal-plan-store.cache.test.mjs，验证实际上下文/重启历史；若无需修改生产GoalPlanStore，保持既有接口。
- 本卡、ADR80、运行时契约、RC自测/手册/当前交付状态与真实证据。

不改main.mjs、GoalPlanStore生产实现、协议字段、工具提示/投影、Provider授权、核验/签收/合回闸门，不改原用户数据。已发布rc.2/tag/资产不移动；后续新RC单独发布卡。

## 测试与退出条件

先红测试复现已批准任务GoalPlan缺历史、Source缺准入事实及Desktop/TUI先启动后落盘。覆盖绑定/无批准拒绝/写失败/批准重放/排队与暂停保留，实际store重启与压缩后事实不丢、两宿主冻结顺序、Source仅事实层及未知状态、核验工具引用白名单不放宽。focused、受影响包全测试、build/typecheck/architecture与两平台CI通过。真实源码双任务完整独立核验/来源汇报/签收/单独授权合回；新不可变候选再实际安装复验。GPT61机器人空输出仍另列，不将本修复宣传为其根因。
