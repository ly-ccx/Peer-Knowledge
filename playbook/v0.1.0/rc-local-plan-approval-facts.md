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

## 本机门禁与当前状态

代码1d73ac694306f08331b642dc29ce45441cf4bb00已推送，PR105。四项红测试复现；修复后focused119/119（含host verifier12），TUI host10/10；最终build/typecheck/architecture和pnpm test全部通过。Desktop5297项中5292通过/原5skip＋AST1、runtime1012、TUI753、system-context35，20项升级矩阵保持。没有增加skip、修改预算或原用户数据。CI36963764691 macOS/Linux进行中。

真实源码默认Astra双任务已冻结两条actual local_ui批准，均已得到新鲜工具证据及TaskRunner Verifier passed；最终独立host核验、来源汇报、用户签收和合回仍在本次流程中，不能提前记整体Pass。已失败的安装Astra分解要求仍保留，本次新任务验收对应两项实际文件目标及编辑后检查，未要求额外任务树形状。新安装候选仍待发版/复验，总RC未Ready。

最终PR105两平台CI36963764691均SUCCESS，2026-10-02T04:25:13Z合入6bdbaf8c5ccfd8b1da625465a1051d76cbb684de。源码、CI临时merge88901d73和交付merge Git tree均69ae658500025e56d37bb5926a67cc0d985f88d3。实际两平台源窗口9壳/11可访问性/7诊断、0页面错误与owned退出通过；Mac列表93.28/搜索99.8/Received162.6ms，Linux31.56/57.2/117.8ms均在原100/150/300预算。UI cognition为脚本夹具，见[evidence/rc-local-approval-ci-binding-20261002.json](evidence/rc-local-approval-ci-binding-20261002.json)。

首轮全Astra真实源码：两任务及最终host独立核验通过，但项目代理随后真实空响应，未完成本轮来源汇报，因此未签收/合回，保留[首轮失败](evidence/rc-local-approval-source-first-failed-20261002.json)。同一已批准持久夹具恢复，项目代理改用已配置Luna，冻结worker/verifier仍Astra；通过新canonical用户输入重新独立核验与两来源汇报、用户签收和单独授权合回。原项目仅a.txt/b.txt，精确内容正确；无本次Retry，owned退出与凭据副本清除。[恢复通过](evidence/rc-local-approval-source-recovery-passed-20261002.json)。这是源码/有模型配置切换的恢复证明，不是首次无干预或安装包全流程通过。原用户默认Astra未改，GPT61机器人空输出也未解决。后续新RC安装复验仍须完成，GA不发布。
