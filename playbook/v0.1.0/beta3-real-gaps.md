# Beta3 真实验收缺口补修

创建/更新：2026-10-01

## 卡片
负责人在真实验收交接后授权继续修复三个 P1：重复等价派发、文件 Evidence 披露、熟悉项目完成到签收及 verified 记忆。A 级，沿用 Accepted ADR 80 / 81 / 85。仅本卡，不发版或启动 Beta4。

## 分支与依赖
- 两仓分支 `PeerAgent/pa/beta3-real-gaps`。
- 修复在已验收候选代码 `6a4c5ecd`、知识 `9ebb9a5` 上推进；前置代码 PR #75 / 知识 PR #5 尚未合入。此次继续授权针对候选补修，知识 PR 采用依赖分支作为临时 base；代码 PR 最初采用依赖分支，但仓库 CI 仅监听 main/dev，故转到 PeerAgent/dev/0.1.0 并重新打开触发 CI。代码 PR 暂含 #75 的前置提交，前置先合入再审本卡；不自行合并。此为手册开发线开分支与依赖先合入要求的明确交接偏差，验收不冒充主线结果。
- 原始证据见知识 PR #6 与 `beta3-real-acceptance.md`。

## 契约与实现要点
1. 对结构化自动标准，派发身份由项目/父会话、用户锚点集合、任务种类、只读属性、验收操作参数、依赖及 supersedes 确定；标题、brief、标准描述/id 的措辞不产生新任务。没有自动标准时保留原严格请求幂等。不同标准、不同锚点或显式 supersedes 不合并；旧记录从持久化 Plan 重建匹配，不批量迁移。不得用模糊文本相似度推断权限或任务等价。
2. 成功 read_file/list_files/search_files 的已有 Provider Tool Result 在既有 EvidenceIndex 追加限长、脱敏的 `bodyPreview`（kind=file、text、truncated）；仅从真实执行结果采集，不采信 assistant/goal wrapper 声明。正文披露使用执行时快照，不重新读取当前文件；历史无快照记录保留 NOT_FOUND。不得索引取消、失败或伪证据正文。核验器沿既有 user 事实输入接缝接收本计划叶子/标准引用的索引快照（总正文最多 12000 字符），明确为非可信指令的执行事实，不提升到系统层；passed 报告必须含可归属索引快照或本轮真实 Tool Result 的引用，缺失/伪造按现有一次格式修复处理。
3. Goal completed 的事实必须唤醒项目代理，不要求先有由 settle 产生的 verdict。该事件只说明有结果待核验/汇报，不证明签收。事件幂等以稳定完成时间及最新 runner verifier 终态修订标识；完成标识先于核验落盘时，核验终态另唤醒一次，不因后续 acceptance/updatedAt 更新重复唤醒。
4. 代理对话中针对已完成、尚未关联交付的用户锚点回复，必须引用相应 session，宿主返回缺失引用及当前状态，沿用 statusClaims 校验；不把模型正文当来源。正式独立核验仍走 verify_session，缺少独立核验不允许 policy 签收；针对 result_ready 的交付回复若独立核验缺失，返回 verification_required 让模型沿既有工具补核验。回复落盘后才签收；人工标准及 confirm 策略仍走用户确认。开始执行时的回复不算已交付，只有引用相应 session 且持久化状态为 result_ready/accepted 的回复才算。
5. 熟悉项目 verified 记忆只来自已关联回复、真实核验结论及可解析 Evidence；来源集合中无法读取的 wrapper 引用不进入 verified 记忆，完全无可读取来源时不写记忆。真实的 project_agent 画像在 memory Provider 通过既有嵌套 toolContext 准入，worker 仍不能写记忆；宿主保留的 lifecycle-research 锚点只代表熟悉项目请求，不能被 memory_remember 用来把文件事实写成 stated；来源事实不能自动变成 stated 或指令。所有记忆继续经过现有准入与撤销机制。

## 允许改动
- `packages/runtime-node/src/project-agent/session-supervisor.mjs`、新派发身份 Module 及对应测试。
- `packages/runtime-node/src/project-agent/watchdog.mjs`、`event-mapper.mjs` 及测试。
- `packages/runtime-node/src/project-agent/reply-composer.mjs`、`delegation-provider.mjs` 及测试；`packages/runtime-node/src/memory/memory-provider.mjs` 及测试。
- `packages/runtime-node/src/goal-plan-store.mjs`、`packages/protocol/src/goal.ts` 及对应测试：仅 Evidence 正文快照契约/索引归一化。
- `apps/desktop/electron/main/chat-runtime/tool-orchestrator.mjs` 及测试：仅成功文件工具 Evidence 采集接缝；允许新建相邻 `file-evidence-preview.mjs` 及测试。
- `apps/desktop/electron/main/project-agent/evidence-presenter.mjs`、`project-facts.mjs`、`reply-composer-port.mjs`、`project-lifecycle-effects.mjs`、`desktop-integration.test.mjs` 及对应测试；`project-agent-host.mjs` 只作必要装配，不新增独立执行逻辑。
- `packages/system-context/src/sources/project-agent-source.mjs` 及测试，既有 `tools/prompts/delegation/post_reply.md`：规则沿用已登记 Source/adapter。
- `apps/desktop/electron/main/agent-host/goal-runner-host.mjs`、`verifier-report.mjs` 及测试，允许新建相邻 verifier-evidence Module 及测试：仅既有核验 user 事实输入、快照限长与报告引用准入，不更改 Goal pump/权限或制造 completion Evidence。
- 本卡与 `knowledge/architecture/project-agent-delegation-runtime.md`，脱敏复跑证据 `playbook/v0.1.0/evidence/beta3-real-gaps-*`。

## 不许改动
main.mjs 净增 0；无 sendMessage 新参数、IPC、新存储路径、新依赖、发版文件或 UI 布局重做。不放宽权限、人工 DoD、签收策略或记忆身份。确认面板布局另卡。

## 必须新增测试与退出条件
先红后绿：跨回合/重启同标准不同措辞重放、不同锚点/标准/supersedes不合并；成功文件读取/列表/搜索的脱敏限长快照可披露，失败/取消与 wrapper 不伪造；completed 无 verdict 唤醒只一次；漏引用结果拒绝、普通问答不受影响；熟悉项目实际完成事件→核验→关联回复→签收/确认→verified记忆及查撤恢复；嵌套 project_agent 画像通过但 worker 拒绝。定向、受影响包、typecheck、architecture、build、CI通过，隔离真实模型复跑三场景、清理拥有的实例与凭据。未满足项明确列出，不伪造 Beta3 全面完成。

## 实现交接
待实施。
