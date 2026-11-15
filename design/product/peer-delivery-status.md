# Peer 交付状态清单

创建时间：2026-09-15
最后更新：2026-10-23（RC26、在途 PR 与新体验规范；旧 D1–D9 盘点改作历史）

> 状态：来源与交付事实盘点，不替代发布认证。排序见[路线图](peer-product-roadmap.md)，当期工作见[改造计划](peer-product-renovation-plan.md)。

## 1. 当前基线和证据等级

- 稳定版 `v0.0.18`，最新预览 [v0.1.0-rc.26](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.26)，发布标签 `3583d06a971f16bcf8f0b23090bc452f2b21e08a`。
- 本地开发目录 `cb2f5695ea164fec7a291570c27c640217c98f1b` 是试用组合，不是 RC26 的发布源码；远端开发线为 `3583d06a`。
- 代码 PR197–200 仍 open，#199 draft；知识 PR67 draft。PR197/199/200 最新 head 已在本地组合；#198 仅含旧 `c8423eb2`，未含当前 head `86eb3fbb`。
- 新规范及两仓 AGENTS 已分别推送 `19454d4` / `347e5550`，尚在独立分支；用户指定规范已用于本次规划，不能说两仓主线已经合入。
- 本轮读取仓库、PR/Release 状态、规范和发布记录，并做静态源码观察；没有运行测试、启动应用、截图审计或重新验收发布包。

**证据等级分开：**源码可见、PR已提交、远端已合并、发布记录已验、对外已发布、本轮重新实测。它们不能互相代替。Accepted ADR 也不证明其实现/验收状态；旧“未开工”标签不能否定后来发布记录。

当前权威发布依据为[固定 RC26 记录](https://github.com/ly-ccx/Peer-Knowledge/blob/43fece5fde940d60009158382450b0a5533374c5/playbook/v0.1.0/rc26-candidate.md)，不是本轮重复执行的报告。

## 2. 当前产品交付与缺口

| ID / 事项 | 当前分类与事实 | 下一项收口 | 对应计划 |
|---|---|---|---|
| D10 项目代理壳 | Beta与RC已有实现/发布；RC26连续公开回复、任务核验详情与统一窗口面已有记录；GA未完成 | 维护现有闭环，不重新实施原型A/机器人壳 | E01、E04–E08 |
| D11 授权与生命周期 | 主Bot权限主体/子任务继承、单一生命周期投影和核验收口已有交付依据 | 跨列表/对话/详情消费者一致性；失效、撤回、拒绝、取消语义 | E04 |
| D12 长历史与恢复 | ADR104/105渐进读取、增量日志、可迁移证明已有RC25/26记录 | 保持有界查询、完整备份与未知执行保护；真实覆盖单独记录 | E12 |
| D13 草稿与未确认输入 | **静态确认的恢复缺口**：BotComposer随workspace重建，pending/failed在切换时清空；失败后已有重试，不能泛称全部发送失败丢失 | 先确定草稿/待发恢复责任；新增持久路径先ADR | E02 |
| D14 IME/键盘/焦点/滚动 | 现有composition保护、focus scope与scroll policy存在；未按新规范做全面实机覆盖 | 共享事件优先级、跨层Escape、用户视口和焦点控制 | E03、E05、E06 |
| D15 统一部件与动效 | Frost/token/共享设置/集中keyframes已存在，新规范已形成；全部调用处符合率未知 | 沿触及路径收敛状态与降级，不从文档宣布全部达标 | E07–E10、E14 |
| D16 多入口与在途修复 | 0.1.0已有TUI/CLI/远程面；PR198最新头未进本地组合，PR197/200在途；ADR106/#199仍待评审集成 | 精确head对齐、修复接入与能力边界审查；远程批准继续回电脑 | E01、E08、E11 |
| D17 发布/真实日用覆盖 | RC26记录组合门禁、240图自审/Verify、隔离官方包恢复；本轮未重跑 | 真模型代表性、原生blur、Win/Linux交互安装、读屏、七天日用及用户GA决定 | E13 |
| D18 新规范与计划集成 | 规范分支已推送；当前计划为本轮新修订 | 纳入各仓集成基线，保留其他在制文件 | E00 |

## 3. 当前执行顺序

事实与在途对齐 → 输入/恢复与可信决定 → 视口/焦点 → 共享组件与日用入口 → 最终候选验证。具体允许范围、依赖、分级和发布退出条件统一见 [E00–E14](peer-product-renovation-plan.md)。

普通开发/文档只做内容与diff审阅；不自动运行定向或全量测试、构建/类型/架构/IPC、截图/交互回归。用户明确要求时提前执行；发布前完整门禁仍强制。原有测试手册的逐次要求不得覆盖最新AGENTS。

## 4. 历史 D1–D9（2026-09-15，禁止直接作为当前缺陷/票）

以下保留原盘点，代码基线是 `dev/0.0.14` / `a4307860`、`VERSION=0.0.13`；这不是2026-10-23的现状认证。D1/D6/D7所述“未验收”只限当时收集范围，后续候选已有新的验证记录。D2–D5/D8的专题增量要先核对现行代码/契约再立卡，不整体合入旧远程分支；D9版本描述已由本文§1覆盖。

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

## 5. 回写规则

每次更新写日期、代码SHA、PR/候选/发布身份、实际场景及证据等级。实现、集成、发布与验证分别记录。源码静态缺口不叫实机已复现，旧失败不直接叫当前回归；证据不足写待核对。

本轮保留其他未提交的架构、决策、回归规程与任务目录改动；不将它们随本次计划提交。未执行产品回归、安装/重启、合并或发布，也未改变权限/存储/系统上下文契约。
