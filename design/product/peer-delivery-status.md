# Peer 交付状态清单

创建时间：2026-09-15
最后更新：2026-10-02（D10：rc.2已预发布，安装复杂任务及GPT61待收口）

> 状态：本地证据盘点；不是发布认证，也不批准新的能力或权限。
> 规划顺序以 [产品路线图](peer-product-roadmap.md) 为准；本文维护交付事实和下一项所需证据。

## 1. 基线与状态口径

本次区分 **未实现、未集成、未验收、文档过期**。这些标签可以并存，不是互斥的完成等级。

- **未实现**：所引用方案明确留下的增量；不能因当前分支没有文件就断言所有分支都没做。
- **未集成**：已有实现证据，但未进入本次核对的开发线；不自动授权合并。
- **未验收**：已有实现或测试记录，但目标场景的证据不足；不等于所有测试都未执行。
- **文档过期**：文档状态落后于代码或与分支基线不一致；应修订状态，不能重复开发。

检查范围：知识库 `e71cbd955c9f003805e1c3e74607456f2193a7ad` 加本地未提交复盘；代码 `dev/0.0.14` 的 `a43078609b274e1ba616111cab02985e11966096`，`VERSION=0.0.13`。本地保存的 `origin/PeerAgent/remote-access` 指向 `0e43f14ed8a96b171eb60be2c7a76b737ae7b332`。本次没有 fetch/pull、联网核查 Release/npm、重跑测试或启动产品。

**证据边界**：代码存在 ≠ 进入当前开发线 ≠ 真实验收通过 ≠ 对外发布可用。历史测试记录只证明文档记载过测试；本轮没有重现。远端跟踪引用是本地快照，不保证是远端最新状态。下面“未验收”均限于所列场景和可见记录，不否定未收集到的外部证据。

## 2. 近期交付盘点

| ID / 事项 | 分类与当前事实 | 下一项收口证据 | 出处 |
| --- | --- | --- | --- |
| D1 Agent 真实产物验证 | **未验收**：已有 Goal、Verifier 与修复阶段；启动正确版本、进入状态、截图交互、修复重验的稳定端到端闭环尚未证明。不能简单归因为缺少 visual 类型 | 先完成一个真实 UI 场景及缺陷修复、旧证据失效、权限阻塞场景；网页与桌面分别留证 | [自主交付复盘](agent-outcome-verification-and-autonomous-delivery-review.md)、[质量评审方案](goal-quality-review-repair-loop.md) |
| D2 远程简化接入 S1/S2 | **未实现（新方案）／未集成（旧功能线）**：交接记录及本地功能分支仍为钥匙串身份；identity.json 迁移及新浏览器扫码授权不是旧绑定复用测试已覆盖的能力。当前版本说明排除远程访问 | 核对最新功能线后，按 S1 身份迁移、S2 授权协议分期实施与验收；保留原身份、绑定及权限边界 | [简化方案](remote-access-simple-implementation.md)、[交接](../../playbook/remote-access-handoff.md)、[版本说明](https://github.com/ly-ccx/Peer-Agent/blob/a43078609b274e1ba616111cab02985e11966096/release-notes/v0.0.13.md) |
| D3 上下文栏 P0 | **未集成**：环境、后台进程、产出三区已有 `0e43f14e`；当前开发线没有该提交及对应 UI/投影文件。不能按“从零未实现”排期 | 先确认产品交付线及依赖，再按批准范围集成并验收；不是整条远程分支自动合并 | [方案及实施记录](task-context-rail.md)、[实现提交](https://github.com/ly-ccx/Peer-Agent/commit/0e43f14ed8a96b171eb60be2c7a76b737ae7b332) |
| D4 上下文栏隐藏轮询 | **文档／版本待对齐**：文档称可见性门已修复，本地功能线仍按会话存在启用；尚不能断言远端漏修 | 刷新并核对权威版本、可见性条件及回归测试，再判断是待集成还是文档超前 | [约束记录](task-context-rail.md)、[本地功能线对应版本](https://github.com/ly-ccx/Peer-Agent/blob/0e43f14ed8a96b171eb60be2c7a76b737ae7b332/apps/desktop/renderer/src/workbench/views/TaskContextRailView.tsx) |
| D5 上下文栏 P1/P2 | **未实现／待设计**：网页查阅聚合、会话技能/MCP 过滤、来源语义、进展摘要仍为后续分期 | 先确定数据来源和语义；摘要涉及 Context Source 准入，不先造展示字段 | [P1/P2](task-context-rail.md) |
| D6 ACP | **未验收（真实外部接入）／文档过期**：当前代码及版本说明已有 ACP，不能沿用 ADR 的未实现描述；测试记录不等于编辑器兼容性认证 | 真实编辑器与云模型下的响应、工具批准/拒绝、取消、断连证据；平台覆盖逐项记录 | [ADR 76](../../knowledge/decisions/76-peer-acp-agent.md)、[实现与验证限制](https://github.com/ly-ccx/Peer-Agent/blob/a43078609b274e1ba616111cab02985e11966096/apps/tui/ACP.md) |
| D7 后台运行面板 | **未验收（完整生产 UI）**：有 fixture 截图、几何和生命周期测试记录；文档明确完整产品界面的人工视觉验收未完成 | 真实 ChatHeader、会话导航、重开与停止反馈、布局验收；不要重复把 fixture 绿灯写成生产面验收 | [后台运行设计及验收限制](background-runtime-product-design.md) |
| D8 Browser 后续能力 | **未实现（明确延期范围）**：持久 Profile、受控 attach、下载/对话框治理不能由临时隔离会话代替 | 按 ADR 分期评审能力、权限和证据，不直接移除现有拒绝逻辑 | [ADR 71](../../knowledge/decisions/71-l2-playwright-external-browser.md) |
| D9 版本、Linux 包装及 keep-alive | **文档过期／验收与发布待核实**：当前历史已有 keep-alive 修复、Linux 包装及 v0.0.12 stamp；不再列为“未开始”。本次不认证安装包、更新链或线上发布 | 运行验收、CI 产物及线上渠道分别补证，不由 commit 标题推定已发布 | [keep-alive](https://github.com/ly-ccx/Peer-Agent/commit/3a1c57a7f069867cb577e6cd624b0a66bdcea27c)、[Linux 包装](https://github.com/ly-ccx/Peer-Agent/commit/d2a61a735ae80b8cdc9d0621f0671faee4c7a6e5)、[v0.0.12 stamp](https://github.com/ly-ccx/Peer-Agent/commit/52086dff046a7ea1703ebd7c53c96de9fa262fe6) |

| D10 项目代理壳 / 机器人列表（ADR 80–85，目标版本 0.1.0） | Beta1–5已实现，RC1及RC2已预发布。PR99–104均通过两平台CI并合入；rc.2固定be65fb73，Release36960577284全成功。20项源码矩阵、完整回归、9壳/11可访问性/7诊断通过；实际macOS签名公证、六次安装轮换、归档与npm CLI默认助手读文件/回复通过。多入口复验通过（实际安装Desktop＋源码TUI后端＋本机远程网关夹具，非实体手机/生产OIDC）；严格安装双任务仍失败。Astra两文件和新鲜证据正确，A因计划拆分及缺批准历史被核验拒绝，未签收/合回；批准事实补修中。GPT61机器人仍空响应，尚未Ready。GA仍等负责人195用例、6流程、七天日用及明确批准。 | 完成安装复杂任务和多入口复验，定位GPT61机器人空响应。Windows/Linux交互安装、实体手机、生产账户与负责人七天日用仍需补验。 | [版本计划](v0.1.0-release-plan.md)、[Beta5交接](../../playbook/v0.1.0/b5-r-handoff.md)、[RC卡](../../playbook/v0.1.0/rc-release.md)、[自测报告](../../playbook/v0.1.0/rc-self-test-report.md)、[全面测试手册](../../playbook/v0.1.0/acceptance-test-guide.md) |

## 3. 近期顺序与非目标

1. **对齐交付线与状态**：D3/D4/D9 先区分已有代码和缺少证据；避免重做。刷新远端、合并分支和发布不在本轮执行范围。
2. **验证真实 UI 自主闭环**：D1 先收一个端到端样本，再决定通用化；不以新增工具数或 Goal 数衡量进展。
3. **补现有功能验收**：D7 与 D6 分别补真实产品、真实外部接入证据。
4. **按既定分期推进增量**：D2、D5、D8；涉及身份、权限、摘要语义等未决事项先评审。该顺序不覆盖产品理念或 ADR。

不是本轮交付：Agent 代码修改、分支集成、真实 UI/ACP 测试、远端刷新、Release/npm 核验、提交推送、任何权限或账号决策变更。远程简化方案与既有部署身份原则若有冲突，仍需在其权威文档评审，不由状态盘点裁决。

## 4. 回写规则

每项更新记录日期、代码 SHA、分支或构建身份、实际场景及证据。只有实际执行的验收才写“通过”；代码集成与发布单独记录。原文已过期而本轮未修改时，在本表保留差异，不替它宣称修订完成。

本轮保留此前未提交的自主交付复盘及 Agent 规划导航，不修改其内容。知识库的本地文件不是跨机已同步成果；是否提交与推送另行执行并记录。
