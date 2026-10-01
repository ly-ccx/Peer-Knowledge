# B4-04 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-04 项目目标存储与工具。负责人授权自行完成全部 B4、必要接入、修复和合入。

## 分支与提交
- 分支：PeerAgent/pa/b4-04-objectives
- 基线：dev 8d607ea3（B4-08 已合入）
- 提交：1ce016fe persist governed project objectives and task links

## 改了什么
- ObjectiveStore / ObjectiveService / localized tool schema：便携定义与追加观察；版本、幂等、作用域；真实当前 canonical 用户授权、代理提议确认、真实信号和任务 Evidence 达成。
- DelegationProvider / Supervisor / live port：七个目标工具经既有 Manifest/Projection/Call/Grant/Evidence，objectiveId 实际保存并绑定任务，独立任务身份。
- Typed project-objectives IPC、catalog/preload/clientApi：设置点击先落真实用户动作事实，重试不覆盖后续改动，无租约/经典拒绝写入。
- 目标页：自定义 Dropdown、紧凑状态/计划/最近和下次观察/预算与任务入口；任务到目标导航；保留旧 Automation。

## 与卡片的偏差
ADR 82 Accepted，高于卡片旧 successCondition/trigger 草图；每次观察均保存，无变化只不进 Inbox。必要路径先写配套知识 PR #13 的实施契约。maxTokensPerDay 在真正硬限实现前拒绝，不能接受后忽略。无新增依赖，main.mjs 未改。

## 验证
- pnpm build、pnpm typecheck、pnpm architecture:check、desktop ipc:check、git diff --check 通过。
- Runtime 完整 912 通过；Desktop 完整 5190 通过、0 失败、5 既有跳过；Protocol 原生完整 173 通过。
- 生产宿主 / LocalToolHost 的集成：真实输入创建、UI 权限事实、重试与后续修改、跨项目/伪造拒绝、Goal 绑定、默认确认签收后实际 Evidence 达成；经典/无租约无写入。
- 最初白名单快照因新增七个工具失败，已更新明确预期并完整回归；未删除断言/新增 skip。
- [代码 #82](https://github.com/ly-ccx/Peer-Agent/pull/82) 的双平台 CI 和 Review 待完成；真实模型/UI/发布验收留 B4-R，测试使用脚本模型。

## 架构影响
A 级 ADR 82 与配套知识 #13 先审。目标为跨任务计划，GoalPlan 仍是执行与签收单位。授权真值集中在 ObjectiveService，Renderer 仅提交 typed 命令；沿既有 portable projects 根，不另立存储边界或执行路径。

## 文档偏差
配套知识 #13 与数据子路径清单同步；旧 Automation 与目标并存。背景检查留 B4-05、自主回合及提议卡留 B4-06。

## 未完成与后续
Review/CI 后按已获授权合入，继续 B4-05、B4-06、B4-R；Beta4 未发布。
