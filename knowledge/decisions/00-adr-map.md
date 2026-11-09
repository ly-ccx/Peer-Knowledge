# ADR 检索与修订索引

创建时间：2026-11-09
最后更新：2026-11-09

本 checkout 原无 `00-adr-map.md`，2026-11-09 按主题检索现有 decisions 后补建索引；同日增补 ADR 47 / 109 行。此表目前只覆盖“公开过程与正式回复交接”及其直接约束，不是全部 ADR 清单；未列主题仍须在本目录按文件名/主题搜索。编号存在重复时按完整文件名定位。

Accepted 表示决定已接受，不表示实现、安装包或发布验收通过。单文件中的 Proposed 修订不能继承该文件原条款的 Accepted 状态；草案接受时必须记录日期、替代范围与验证计划，再开始实现。

| 主题 / ADR 文件 | 已接受边界 | 本次修订 / 状态 |
|---|---|---|
| [80-project-agent-delegation-model.md](80-project-agent-delegation-model.md) | 结果分层披露、送达策略、依据任务事实的重复报告抑制 | 保持；ADR87 的展示身份去重不能绕过 reportFactKeys 准入 |
| [85-project-agent-hosts-inputs-and-surfaces.md](85-project-agent-hosts-inputs-and-surfaces.md) | 宿主/多入口、真实流式预览、停止、持久正式消息交接 | 2026-11-09：ADR87 修订已接受（A 级）：公开 delta 归过程、正文由 canonical 回复承接、新契约禁纯文本 fallback；旧记录与既有 fallback 语义只读保留 |
| [87-user-turn-live-process-presentation.md](87-user-turn-live-process-presentation.md) | 有界、脱敏公开过程与工具预览，历史来源与非 Evidence 边界 | 2026-11-09：D1–D11 经用户接受（A 级）：过程叙述与正式交付分离；实施自接受后开始，V01–V17 待验证，结果回填 D10 |
| [94-reply-attempts-silent-wait-and-recovery.md](94-reply-attempts-silent-wait-and-recovery.md) | 回复尝试、静默等待、失败与实际恢复相互独立 | 保持；ADR87 草案不得以过程折叠掩盖未交付、停止或未知状态 |
| [99-authoritative-reply-receipts-and-model-recovery.md](99-authoritative-reply-receipts-and-model-recovery.md) | 完整本地工具回执、canonical 正式回复与恢复；UI 预览非交付权威 | 保持；ADR87 草案的答案预览与正式接管沿此门禁 |
| [100-actionable-attention-and-question-lifecycle.md](100-actionable-attention-and-question-lifecycle.md) | 原生问题、授权、人工完成检查及 Attention 来源 | 保持；过程身份不自动创建/解决问题或权限，关键动作不隐藏 |
| [106-project-agent-duplex-supervision-and-continuity.md](106-project-agent-duplex-supervision-and-continuity.md) | 工作责任、身份、历史/协调事实所有者与连续性 | 保持；多次合法交付不被 workId 合并，正文交接不结束工作责任 |
| [47-workbench-multi-resource-tabs.md](47-workbench-multi-resource-tabs.md) | 能力入口与资源会话分层；Files 为导航器不建标签 | 2026-11-09：决策一第 4 条在资源窗口范围内被 ADR 109 替代（A 级，用户选定）；其余条款保持 |
| [109-resource-window-directory-tabs.md](109-resource-window-directory-tabs.md) | 资源窗口目录为一等资源标签；辅助导航面板保留；状态机隔离；最近描述符仅事实提示 | 2026-11-09：Accepted（方向经用户确认）；实施与验证按其「验证要求」执行 |

本次只修订既有 ADR87，不占用新 ADR 编号。源码与验收记录仍在对应代码仓/实施回执中维护；本索引不另建执行或验收真源。
