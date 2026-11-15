# ADR 文档图谱

创建时间：2026-11-06
最后更新：2026-11-15（全量跨 ADR 一致性对齐：同步 87 篇修订至 2026-11-15；将 ADR 126 与 ADR 127 一并转为 Accepted 并保留 `ask` / `bot_verified` 两档、`auto` 取消；补齐 `48 / 59 / 104 / 108` 四组重号消歧、三层模型切换边界、`work_session` L2 Playwright 网页隔离、ADR 0001 fail-closed 凭据收口、ADR 115 `input_prediction` 账本隔离、`15–18 / 42 / 67` 及多篇部分取代口径，以及 `77 / 104-visibility / 113 / 119 / 123` 的 Proposed 与特性门槛重编；在目录同步 `126 / 127` 与在途远端占用号清单）

> 这是 `knowledge/decisions/` 的索引，不是一条新的架构决定。
> 基线是知识库 `origin/main` 的 `7600b00`（`merge commit 923fb71` 合入后于 2026-11-15 完成全量跨 ADR 对齐）。
> 编号 `48`、`59`、`104`、`108` 各有两篇（见下文重号表）；正文与交叉引用必须带文件名或约定简名，禁止裸写号数。

本页只记录文件里写明的状态、日期和替代关系。页头写了接受，只说明这篇决定曾被接受，不说明对应实现已经发布验收。

## 知识库分层

ADR 是知识库五层中的决策层。产品方向和架构治理各自保留权威；2026-10-23 起，体验冲突以规范层为准。同一篇 ADR 里，后写的「后续」只改它点名的条款。

| 层 | 位置 | 回答的问题 |
|---|---|---|
| 架构 | `knowledge/architecture/` | 系统怎么分，哪条链不能旁路。治理基线是 [20-architecture-governance.md](../architecture/20-architecture-governance.md) |
| 决策 | `knowledge/decisions/` | 某一次边界怎么定。A 级改动先改这里，再改代码 |
| 规范 | `knowledge/specifications/` | 体验、动效和交互怎么做 |
| 产品 | `design/product/`、`design/visual/` | 路线和版本计划。方向以 [peer-product-alignment.md](../../design/product/peer-product-alignment.md) 为准 |
| 执行与现场 | `playbook/`、`knowledge/experience/` | 怎么落地、怎么回归、出过什么问题 |

决策目录内部不再按主题分文件夹。编号大致按写入时间排列。读某一条时，先看文件名，再看页头状态，再看文末「后续」。

## 编号

- 2026-11-07 按 `origin/main` `3402e83` 重数：本图谱之外有 **110** 个决策文件、**105** 个编号。缺号为 `2`–`14`、`19`、`20`、`23`、`107`（`0001` 不占 `1`）。
- 2026-11-09 按 `origin/main` 重数：图谱之外为 **114** 个决策文件、**110** 个编号（含 `48` / `59` / `104` / `108` 四组同号双篇），已计入 ADR 126 / 127。
- 2026-11-15 基于 `923fb71`（同步 `origin/main` `7600b00`）复核：本图谱之外仍为 **114** 个决策文件、**110** 个独立编号（`0001` + `15`–`127`；缺失 `2`–`14`、`19`、`20`、`23`、`107` 严禁回填或复用，历史悬空 `ADR 23` 引用已清理）。

同一个编号有两篇时，引用必须带文件名或如下约定简名：

| 编号 | 约定简名 / 文件 | 当前状态 |
|---|---|---|
| 48 | `ADR 48-cli` / [48-cli-first-class-release.md](./48-cli-first-class-release.md) | Accepted（阶段一 + npm 安装面已落地；ADR 108-cli 收窄自动更新） |
| 48 | `ADR 48-provider` / [48-provider-model-options.md](./48-provider-model-options.md) | Accepted（渠道模型选项与裁剪基线） |
| 59 | `ADR 59-appshots` / [59-appshots-capability-boundary.md](./59-appshots-capability-boundary.md) | Accepted（P0a Appshots 能力边界） |
| 59 | `ADR 59-browser` / [59-browser-panel-reveal-capability.md](./59-browser-panel-reveal-capability.md) | Accepted（Browser reveal；`work_session` 受 ADR 66 / 72 / 85 / 109 收窄） |
| 104 | `ADR 104-visibility` / [104-bot-capability-visibility.md](./104-bot-capability-visibility.md) | **Proposed（未接受）**；已清理外部未合入 `ADR 107` 引用 |
| 104 | `ADR 104-progressive` / [104-progressive-interaction-and-coordination-storage.md](./104-progressive-interaction-and-coordination-storage.md) | Accepted（交互优先读模型与协调日志增量存储；统一 §9 路径口径） |
| 108 | `ADR 108-bot` / [108-bot-reply-document-preview.md](./108-bot-reply-document-preview.md) | Accepted（展示容器部分已由 ADR 109 / ADR 114 取代） |
| 108 | `ADR 108-cli` / [108-cli-basic-shell-commands.md](./108-cli-basic-shell-commands.md) | Accepted（实现未发布验收；收窄 ADR 48-cli 与 ADR 61） |

### 在途远端分支占号与重编规则（2026-11-15 核对）

以 `origin/main`（`7600b00`）为比较基线，下列远端分支已占用号或存在重号冲突：

- **已占用新号 `128`–`131`**：
  - `origin/codex/local-runtime-isolation-architecture`：占用 `128`（`128-local-runtime-isolation-and-bounded-query-contract.md`）。
  - `origin/codex/native-rust-cli`：占用 `129`–`131`（`129-native-rust-cli-and-ratatui.md`、`130-bounded-cli-memory-and-transcript.md`、`131-native-cli-contract-storage-and-recovery.md`）。
- **重号冲突（合入 `main` 前必须重编至 `132+`）**：
  - `origin/docs/persistent-shell-session`：`66-persistent-shell-session.md`、`67-read-file-line-range.md` 与现行 `66` / `67` 重号，合入前必须重编至 `132+`。
  - `origin/docs/adr-123-tool-result-spill`：`123-oversized-tool-result-local-spill.md` 与现有 `123` 重号，合入前必须重编至 `132+`。
- **后续新增编号与特性门槛规则**：
  - 新立 ADR 从 `132+` 顺延编号；[ADR 104-visibility](./104-bot-capability-visibility.md) 原提及的 Bot 专属自定义指令后续若单独定案，亦从 `132+` 新立编号（不再使用未合并的 `ADR 107`）。
  - 持久化 / 格式兼容门槛代次 `6`–`11` 已被主线历史与 ADR 124 占用（未接受的 ADR 119 拟占 `10` 已作废且不得复用）；包括 [ADR 113](./113-checkpoint-content-addressed-storage-and-retention.md)、[ADR 123](./123-main-bot-unnoticed-memory.md)、[ADR 126](./126-execution-resource-claim-closure-and-unknown-retention.md) 在内的后续特性门槛统一使用 `> 11`（即 `12+`）的下一个未占用整数。

## 已写明的替代和作废

只有正文明确写出替代、收窄或作废范围的，才记在这里。

| 文件 | 变更日期 | 写明的变化与替代关系 |
|---|---|---|
| [`15-plugin-skill-mcp-system.md`](./15-plugin-skill-mcp-system.md) | 2026-11-15 | 草案保留主链；云端 `SkillDefinition` 已被 [ADR 58](./58-local-skill-scope-and-workspace-mounting.md)/[ADR 16](./16-skill-call-lifecycle.md) 取代，Shell `allow` `wildcard` 已被 [ADR 49](./49-cancel-path-hard-sandbox.md)/[92](./92-scoped-permission-inheritance.md)/[101](./101-bot-owned-access-policy.md) 废止，Desktop 单一 `<userData>` 存储路径已被 [ADR 74](./74-deployment-surfaces-and-local-storage.md)/[85](./85-project-agent-hosts-inputs-and-surfaces.md) 取代 |
| [`16-skill-call-lifecycle.md`](./16-skill-call-lifecycle.md) | 2026-11-15 | 本地能力链与 `scope.cwd` 规则有效；「宙斯客户端 / Cloud CEO Gateway」主语已作废 |
| [`17-local-context-compaction.md`](./17-local-context-compaction.md) | 2026-11-15 | 草案的 `0.75/0.95` 阈值与 `user` 消息交接块已被 [Architecture 19](../architecture/19-system-prompt-context-architecture.md) 与 [ADR 55](./55-shared-system-context-assembler.md)/[56](./56-provider-observed-context-accounting.md)/[57](./57-canonical-conversation-history-projector.md) 取代 |
| [`18-claude-code-style-file-edit-plan.md`](./18-claude-code-style-file-edit-plan.md) | 2026-11-15 | 历史计划草案：§1–§12 统一文件工具已被 [ADR 51](./51-unified-desktop-cli-file-tools.md) 吸收，§13 工具参数流式进度已被 [ADR 29](./29-tool-arg-progress-streaming.md) 独立定案 |
| [`21-pending-task-resume.md`](./21-pending-task-resume.md) | 2026-11-15 | 收窄适用至经典单会话 `/restart`；Project Agent 多工作持久化恢复与双工监督已由 [ADR 88](./88-project-agent-execution-continuity.md)/[104-progressive](./104-progressive-interaction-and-coordination-storage.md)/[111](./111-project-agent-duplex-supervision-and-continuity.md) 承接 |
| [`22-stream-reattach-on-reload.md`](./22-stream-reattach-on-reload.md) | 2026-11-15 | 隐藏思考回传渲染层与单活跃流假设已被 [ADR 85](./85-project-agent-hosts-inputs-and-surfaces.md)/[87](./87-user-turn-live-process-presentation.md)/[121](./121-desktop-session-windowing-contract.md) 部分取代 |
| [`27-workspace-switch-and-cross-workspace-running.md`](./27-workspace-switch-and-cross-workspace-running.md) | 2026-11-15 | 跨项目并发投影与侧栏可见性已由 [ADR 80](./80-project-agent-delegation-model.md)/[84](./84-bot-list-shell.md)/[85](./85-project-agent-hosts-inputs-and-surfaces.md) 扩展承接 |
| [`31-mcp-connection-management.md`](./31-mcp-connection-management.md) & [`32-mcp-authentication.md`](./32-mcp-authentication.md) | 2026-11-15 | Cloud Gateway 主路径与 Electron `<userData>/mcp/servers.json` 单宿主假设已被跨宿主 `<dataRoot>` `mcp-registry` 取代；`file-fallback` 明文凭据降级被明确废止，统一并入 [ADR 0001](./0001-cross-platform-credential-vault.md) `peer-credential-helper` |
| [`33-per-message-turn-duration.md`](./33-per-message-turn-duration.md) | 2026-11-15 | `conversations:replace-messages` 全量写回假设在活跃对话与 Project Bot 主链路中已被宿主增量 `append` 取代 |
| [`34-conversation-delete-goal-plan-cascade.md`](./34-conversation-delete-goal-plan-cascade.md) | 2026-11-15 | 硬删除适用范围收窄至经典空闲对话；0.1.0 须服从资源锁与 unknown 义务约束 |
| [`40`](./40-embedded-browser-and-agent-control.md)/[`46`](./46-conversation-bound-browser-tabs.md)/[`59-browser`](./59-browser-panel-reveal-capability.md)/[`66`](./66-browser-headless-fallback-execution.md)/[`72`](./72-l1-default-web-entry.md) | 2026-11-15 | L1 内置 `<webview>`（`browser_*`）适用于经典前台会话、独立浏览窗与资源窗口标签（含 ADR 109 / 125）；0.1.0 Project Bot `work_session` 已按 [ADR 71](./71-l2-playwright-external-browser.md) / [ADR 85](./85-project-agent-hosts-inputs-and-surfaces.md) 剥离 L1 并固定使用 L2 Playwright + [ADR 38](./38-web-search-fetch-provider.md) `web_fetch` |
| [`41-rename-goal-mode-to-plan-mode.md`](./41-rename-goal-mode-to-plan-mode.md) | 2026-11-15 | `plan` wire 迁移有效；「Runner 独占 goal」与 §5 早期选型对比表已被 2026-07-03 B2-b 修订推翻 |
| [`42-context-display-vs-trigger-accounting.md`](./42-context-display-vs-trigger-accounting.md) | 2026-11-15 | **Superseded**：整体口径已被 [ADR 52](./52-unified-next-request-context-accounting.md) 与现行 [ADR 56](./56-provider-observed-context-accounting.md) 取代 |
| [`47-workbench-multi-resource-tabs.md`](./47-workbench-multi-resource-tabs.md) | 2026-11-15 | 决策一第 4 条（目录不建标签）在资源窗口标签条范围内被 [ADR 125](./125-resource-window-directory-tabs.md) 替代；兼容 ADR 118 `interactive` |
| [`48-cli-first-class-release.md`](./48-cli-first-class-release.md) | 2026-11-15 | 「CLI 自动更新可缓做」条款由 [ADR 108-cli](./108-cli-basic-shell-commands.md) 收窄（仅保留无人值守安装，显式 `peer update` 由 `108-cli` 规定） |
| [`49-cancel-path-hard-sandbox.md`](./49-cancel-path-hard-sandbox.md) | 2026-11-15 | 跨工作区操作规则已被 [ADR 90](./90-local-image-capability-and-product-review.md)/[92](./92-scoped-permission-inheritance.md)/[101](./101-bot-owned-access-policy.md)/[106](./106-readonly-git-and-delegation-capability-admission.md) 部分取代 |
| [`52-unified-next-request-context-accounting.md`](./52-unified-next-request-context-accounting.md) | 2026-07-25 | 本地估算作为当前权威值的决策已被 [ADR 56](./56-provider-observed-context-accounting.md) 取代 |
| [`64-workbench-source-highlight-without-monaco.md`](./64-workbench-source-highlight-without-monaco.md) | 2026-11-15 | 流式开块按帧全树高亮被 [ADR 121](./121-desktop-session-windowing-contract.md) P1 延迟高亮取代；只读源码前提在 [ADR 109](./109-resource-reference-preview-and-artifact-collaboration.md) R9/R10 用户显式编辑范围放宽 |
| [`67-task-shell-workbench-radar.md`](./67-task-shell-workbench-radar.md) | 2026-11-15 | **Superseded in default 0.1 shell**：默认 0.1 外壳已切换至 [ADR 80](./80-project-agent-delegation-model.md) 与 [ADR 84](./84-bot-list-shell.md)，仅保留为经典壳层历史对照 |
| [`68`](./68-goal-delivery-mode-contract.md) / [`69`](./69-handoff-triage-classifier.md) | 2026-11-15 | Project Bot 模式下默认 `direct` 写回、无确认直落与静默 `AUTO_MERGE` 已被 [ADR 80](./80-project-agent-delegation-model.md) 决策 7–8 取代，并受 [ADR 116](./116-session-control-and-resource-settlement.md)/[127](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) 资源锁约束 |
| [`83`](./83-model-routing-by-role.md) / [`99`](./99-authoritative-reply-receipts-and-model-recovery.md) | 2026-11-15 | 三层切换契约明确：[ADR 30](./30-provider-recovery-broker.md) 负责同模型重试；ADR 83 负责档位备选境界切换（`work_session` 子任务开任务冻结）；ADR 99 仅对主 Bot 生效会话模型重基 |
| [`85`](./85-project-agent-hosts-inputs-and-surfaces.md) / [`87`](./87-user-turn-live-process-presentation.md) | 2026-11-15 | [ADR 85](./85-project-agent-hosts-inputs-and-surfaces.md) 对应展示交接条款由 [ADR 87](./87-user-turn-live-process-presentation.md) D1–D11 2026-11-09 修订替代（仅新契约范围） |
| [`86`](./86-batched-persisted-conversation-reads.md) / [`88`](./88-project-agent-execution-continuity.md) / [`96`](./96-task-execution-responsiveness.md) | 2026-11-15 | ADR 86 热会话与 ADR 96 §3.1/§3.3 已向 [ADR 104-progressive](./104-progressive-interaction-and-coordination-storage.md) 与 [ADR 121](./121-desktop-session-windowing-contract.md) 演进；ADR 88 §7.2/§11.2/§21.2 与 §8（被 [ADR 95](./95-progress-driven-execution-policy.md) 取代）保留部分取代指针 |
| [`92-scoped-permission-inheritance.md`](./92-scoped-permission-inheritance.md) | 2026-10-21 | §9.3 全局 `settings.localAccessLevel` 真源决定被 [ADR 101](./101-bot-owned-access-policy.md) 局部取代 |
| [`104-progressive-interaction-and-coordination-storage.md`](./104-progressive-interaction-and-coordination-storage.md) | 2026-11-15 | §5.1 早期路径描述统一至 §9 `read-models` 存储路径口径 |
| [`108-bot-reply-document-preview.md`](./108-bot-reply-document-preview.md) | 2026-11-15 | 回复预览卡片与文档查看展示容器部分由 [ADR 109](./109-resource-reference-preview-and-artifact-collaboration.md) / [ADR 114](./114-reply-citation-resolution-and-open.md) 取代 |
| [`109-resource-reference-preview-and-artifact-collaboration.md`](./109-resource-reference-preview-and-artifact-collaboration.md) | 2026-11-15 | 目录标签与 launcher 头部快捷入口受 [ADR 125](./125-resource-window-directory-tabs.md) 部分取代；§23 裸文件名定位由 [ADR 114](./114-reply-citation-resolution-and-open.md) §2 取代 |
| [`112-runtime-module-and-loading-boundaries.md`](./112-runtime-module-and-loading-boundaries.md) | 2026-11-01 | 早期 manifest 3 草案被替代；实际沿用 schema 2，最小 reader/writer 为 5（主线后随 ADR 124 推进至 `11`，未来特性门槛迁 `> 11`） |
| [`115-input-prediction-and-draft-boundary.md`](./115-input-prediction-and-draft-boundary.md) | 2026-11-15 | `input_prediction` 用量从 [ADR 25](./25-runtime-usage-ledger.md) `requests.jsonl` 隔离至独立 `usage/input-prediction.jsonl` |
| [`116-session-control-and-resource-settlement.md`](./116-session-control-and-resource-settlement.md) | 2026-11-15 | §6.1–§6.3 / §12 的目录粒度永久 hold 与唯一释放条件被 [ADR 126](./126-execution-resource-claim-closure-and-unknown-retention.md) / [ADR 127](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) 部分取代 |
| [`119-user-stop-cognition-admission-and-settlement.md`](./119-user-stop-cognition-admission-and-settlement.md) | 2026-11-15 | 仍为 Proposed；§6.3 `FollowUp.handling` 已被 [ADR 120](./120-runtime-facts-disposition-and-resource-wait.md) 事实取代，§12 门禁 `10` 已作废，遗留三件义务工具已由 [ADR 124](./124-legacy-stop-obligation-controlled-resolution.md)（门禁 `11`）独立处置 |
| [`124-legacy-stop-obligation-controlled-resolution.md`](./124-legacy-stop-obligation-controlled-resolution.md) | 2026-11-15 | §1.5 / §4.1 / §6.2 / §8.3 / §13 的永久占用、逐条仅 `user_panel` 确认与禁止设置入口被 [ADR 126](./126-execution-resource-claim-closure-and-unknown-retention.md) / [ADR 127](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) 部分取代（`indexed` 列表依然不对普通日常界面展示「待核实」，可通过设置/诊断与受阻提示查看） |

## 不能整篇当作现行契约

下面这些文件按其页头处于**草案 / Proposed**、**整体作废**或**部分被取代**状态；草案和未接受的整篇都不是生效契约，部分被替代的仅失效被点名条款：

| 类别 | 文件 | 当前页头 / 适用说明 |
|---|---|---|
| **Proposed（未接受，5 篇）** | [`77-image-generation-capability.md`](./77-image-generation-capability.md) | `Proposed`（待架构评审；补齐工作区外 `imageReadGrant` 对齐 ADR 90/92） |
| **Proposed（未接受，5 篇）** | [`104-bot-capability-visibility.md`](./104-bot-capability-visibility.md) | `Proposed`（待逐项评审；已清理 `ADR 107` 引用，Bot 自定义指令另延 `132+`） |
| **Proposed（未接受，5 篇）** | [`113-checkpoint-content-addressed-storage-and-retention.md`](./113-checkpoint-content-addressed-storage-and-retention.md) | `Proposed`（仅 §4.6 提前落地；兼容门槛拟迁 `> 11` 未占用代次） |
| **Proposed（未接受，5 篇）** | [`119-user-stop-cognition-admission-and-settlement.md`](./119-user-stop-cognition-admission-and-settlement.md) | `Proposed`（未批准实施；§6.3 `handling` 与门禁 `10` 已被 ADR 120 / 124 取代） |
| **Proposed（未接受，5 篇）** | [`123-main-bot-unnoticed-memory.md`](./123-main-bot-unnoticed-memory.md) | `Proposed`（已更名「无感上下文整理（情节压缩）」，增补 `L7_CONTINUITY` 仲裁与 SQLite/FTS 复用约束，未授权实现） |
| **早期草案（3 篇）** | [`15`](./15-plugin-skill-mcp-system.md)、[`17`](./17-local-context-compaction.md)、[`18`](./18-claude-code-style-file-edit-plan.md) | 早期设计/历史计划草案，核心思路已被后续 Accepted ADR 吸收或局部作废 |
| **分阶段状态（1 篇）** | [`38-web-search-fetch-provider.md`](./38-web-search-fetch-provider.md) | Phase 1 `web_fetch` 已 `Accepted / Shipped`（跨宿主无 `BrowserWindow`）；Phase 2 `web_search` 仍为 `Proposed` |
| **整体 / 默认壳被取代（2 篇）** | [`42-context-display-vs-trigger-accounting.md`](./42-context-display-vs-trigger-accounting.md)、[`67-task-shell-workbench-radar.md`](./67-task-shell-workbench-radar.md) | 42 `Superseded`（由 ADR 52 / 56 取代）；67 `Superseded in default 0.1 shell`（默认 0.1 壳切至 ADR 80 / 84） |
| **部分作废或部分被取代（Accepted）** | [`16`](./16-skill-call-lifecycle.md)、[`21`](./21-pending-task-resume.md)、[`22`](./22-stream-reattach-on-reload.md)、[`27`](./27-workspace-switch-and-cross-workspace-running.md)、[`31`](./31-mcp-connection-management.md)、[`32`](./32-mcp-authentication.md)、[`33`](./33-per-message-turn-duration.md)、[`34`](./34-conversation-delete-goal-plan-cascade.md)、[`40`](./40-embedded-browser-and-agent-control.md)、[`41`](./41-rename-goal-mode-to-plan-mode.md)、[`46`](./46-conversation-bound-browser-tabs.md)、[`47`](./47-workbench-multi-resource-tabs.md)、[`48-cli`](./48-cli-first-class-release.md)、[`49`](./49-cancel-path-hard-sandbox.md)、[`52`](./52-unified-next-request-context-accounting.md)、[`59-browser`](./59-browser-panel-reveal-capability.md)、[`60`](./60-quick-chat-independent-popover-window.md)、[`64`](./64-workbench-source-highlight-without-monaco.md)、[`66`](./66-browser-headless-fallback-execution.md)、[`68`](./68-goal-delivery-mode-contract.md)、[`69`](./69-handoff-triage-classifier.md)、[`72`](./72-l1-default-web-entry.md)、[`85`](./85-project-agent-hosts-inputs-and-surfaces.md)、[`86`](./86-batched-persisted-conversation-reads.md)、[`88`](./88-project-agent-execution-continuity.md)、[`92`](./92-scoped-permission-inheritance.md)、[`96`](./96-task-execution-responsiveness.md)、[`104-progressive`](./104-progressive-interaction-and-coordination-storage.md)、[`108-bot`](./108-bot-reply-document-preview.md)、[`109`](./109-resource-reference-preview-and-artifact-collaboration.md)、[`112`](./112-runtime-module-and-loading-boundaries.md)、[`116`](./116-session-control-and-resource-settlement.md)、[`124`](./124-legacy-stop-obligation-controlled-resolution.md) | 各文件页头 / blockquote / `## 被替代条款` 已写明具体被替代条款，未点名部分继续生效 |

> 注：此前本表曾将 `74`、`76`、`105`、`126`、`127` 列为未接受或无状态；2026-11-15 已在对应原文规范标注为 `Accepted`（仍不等于实现完成或发布验收通过）。

## 修订记录

列出页头「最后更新」晚于创建日、带有修订注明、或于 2026-11-15 本轮对齐修订的文件（共 100 条）。括号摘要对照各文件页头原文，完整细节以文件为准。

| 文件 | 创建 | 最后更新 | 页头注明 |
|---|---|---|---|
| [`15-plugin-skill-mcp-system.md`](./15-plugin-skill-mcp-system.md) | 2026-05-20 | 2026-11-15 | 标注早期设计草案中已作废的云端 Skill / wildcard 放行 / 单一 `<userData>` 路径条款 |
| [`16-skill-call-lifecycle.md`](./16-skill-call-lifecycle.md) | — | 2026-11-15 | 跨 ADR 对齐：Clarify `scope.cwd` 与 ADR 49 / 90 / 92 / 101 规则衔接 |
| [`17-local-context-compaction.md`](./17-local-context-compaction.md) | 2026-06-08 | 2026-11-15 | 标注早期 `0.75/0.95` 与 `user` 消息交接块条款已被 [System Context 架构](../architecture/19-system-prompt-context-architecture.md) 及 [ADR 55](55-shared-system-context-assembler.md) / [ADR 56](56-provider-observed-context-accounting.md) / [ADR 57](57-canonical-conversation-history-projector.md) 取代 |
| [`18-claude-code-style-file-edit-plan.md`](./18-claude-code-style-file-edit-plan.md) | 2026-06-09 | 2026-11-15 | 标明本文统一文件工具设计已被 ADR 51 吸收、§13 工具参数流式进度已独立为 ADR 29 |
| [`21-pending-task-resume.md`](./21-pending-task-resume.md) | — | 2026-11-15 | 明确与 Project Agent 持久化连续性契约的适用边界 |
| [`22-stream-reattach-on-reload.md`](./22-stream-reattach-on-reload.md) | — | 2026-11-15 | 补注隐藏思考不回传渲染层与单活跃流前提被后续 ADR 部分取代，澄清 HMR 重连定位 |
| [`24-provider-cache-and-empty-response-guard.md`](./24-provider-cache-and-empty-response-guard.md) | 2026-06-11 | 2026-11-15 | 修正治理基线相对路径链接 |
| [`25-runtime-usage-ledger.md`](./25-runtime-usage-ledger.md) | 2026-06-25 | 2026-11-15 | 跨 ADR 对齐：明确 `requests.jsonl` 与 [ADR 115](115-input-prediction-and-draft-boundary.md) `input_prediction` 账本物理隔离 |
| [`26-agent-loop-termination.md`](./26-agent-loop-termination.md) | 2026-06-12 | 2026-11-15 | 明确单回合无限循环与 Project Agent 自主协调循环（ADR 88/95/96/103/117）的适用边界 |
| [`27-workspace-switch-and-cross-workspace-running.md`](./27-workspace-switch-and-cross-workspace-running.md) | — | 2026-11-15 | 明确跨工作区可见性在 0.1 默认 Bot 列表工作台与项目代理宿主下的衔接 |
| [`28-openai-subscription-oauth.md`](./28-openai-subscription-oauth.md) | — | 2026-11-15 | 修正悬空 `ADR 23` 引用至 `ADR 37`；对齐 `effort` 词表与渠道独占边界 |
| [`30-provider-recovery-broker.md`](./30-provider-recovery-broker.md) | 2026-06-15 | 2026-11-15 | 明确三层模型切换边界：ADR 30 同模型重试 vs ADR 83 档位备选故障切换 vs ADR 99 主 Bot 重基；标注 KXT ADR-0005 为外部仓引用 |
| [`31-mcp-connection-management.md`](./31-mcp-connection-management.md) | 2026-06-15 | 2026-11-15 | 跨 ADR 对齐：更新架构文档相对路径，明确 Local-First Desktop + CLI/TUI 共用本地 `mcp-registry` 与 ADR 0001 fail-closed `peer-credential-helper` |
| [`32-mcp-authentication.md`](./32-mcp-authentication.md) | 2026-06-16 | 2026-11-15 | 跨 ADR 对齐：合入 `oauth2`、废止 `file-fallback` 明文降级、强制迁入跨宿主 `peer-credential-helper` |
| [`33-per-message-turn-duration.md`](./33-per-message-turn-duration.md) | 2026-06-17 | 2026-11-15 | 对齐主进程 `append` 持久化边界，标注 `conversations:replace-messages` 在活跃聊天与 Project Bot 主链路已被取代 |
| [`34-conversation-delete-goal-plan-cascade.md`](./34-conversation-delete-goal-plan-cascade.md) | 2026-06-18 | 2026-11-15 | 收窄硬删除适用范围至经典空闲对话，补充 0.1.0 资源锁/未知义务边界 |
| [`35-mode-scoped-tool-projection.md`](./35-mode-scoped-tool-projection.md) | — | 2026-11-15 | 跨 ADR 对齐：演进为 `(mode × role × host × botAdmission)` 四维投影矩阵，补全 `project_agent` / `explorer` 6 工具 / `verifier` 白名单与 [System Context 架构](../architecture/19-system-prompt-context-architecture.md) 链接 |
| [`37-provider-channel-and-wire-protocol-separation.md`](./37-provider-channel-and-wire-protocol-separation.md) | 2026-06-18 | 2026-11-15 | 更新实施状态，对齐 `effort` 全词表与 [ADR 48-provider](48-provider-model-options.md) / ADR 83 模型选项及档位校验 |
| [`38-web-search-fetch-provider.md`](./38-web-search-fetch-provider.md) | 2026-06-20 | 2026-11-15 | 标明 Phase 1 `web_fetch` 已跨宿主无 Electron `BrowserWindow` 落地、记录 manifest `riskLevel` 现状差异，Phase 2 `web_search` 维持 Proposed |
| [`39-updater-download-ux.md`](./39-updater-download-ux.md) | 2026-06-25 | 2026-11-15 | 规范标注 Accepted 并对齐发布渠道与签名公证约束 |
| [`40-embedded-browser-and-agent-control.md`](./40-embedded-browser-and-agent-control.md) | 2026-06-25 | 2026-11-15 | 规范标注 Accepted 并标明 L1 在经典会话／独立浏览窗口与后台 `work_session` 间的适用边界 |
| [`41-rename-goal-mode-to-plan-mode.md`](./41-rename-goal-mode-to-plan-mode.md) | 2026-06-30 | 2026-11-15 | 明确 §5 方案选型表已由下方「六之补二：B2-b 修订」与统一执行契约最终定案，历史记录保留 |
| [`42-context-display-vs-trigger-accounting.md`](./42-context-display-vs-trigger-accounting.md) | 2026-06-30 | 2026-11-15 | 标明整体契约已被 [ADR 52](52-unified-next-request-context-accounting.md) 与 [ADR 56](56-provider-observed-context-accounting.md) 取代 |
| [`43-conversation-runtime-state-bucketing.md`](./43-conversation-runtime-state-bucketing.md) | 2026-07-01 | 2026-11-15 | 规范标注 Accepted，并标明后续向 [ADR 87](87-user-turn-live-process-presentation.md) 与 [ADR 121](121-desktop-session-windowing-contract.md) 的演进 |
| [`45-mcp-oauth-config-ux-simplification.md`](./45-mcp-oauth-config-ux-simplification.md) | 2026-07-01 | 2026-11-15 | 对齐跨宿主 OAuth 安全边界与 ADR 0001 / ADR 32 |
| [`46-conversation-bound-browser-tabs.md`](./46-conversation-bound-browser-tabs.md) | 2026-07-15 | 2026-11-15 | 对齐 L1 `BrowserSession` 在经典会话／资源窗口与 `work_session` L2 Playwright 间的边界 |
| [`47-workbench-multi-resource-tabs.md`](./47-workbench-multi-resource-tabs.md) | 2026-07-15 | 2026-11-15 | 对齐 [ADR 118](118-openui-interactive-results-and-runtime-boundaries.md) `interactive` 标签兼容、[ADR 125](125-resource-window-directory-tabs.md) 资源窗口与 [ADR 109](109-resource-reference-preview-and-artifact-collaboration.md) 第一阶段已接受 / 后续包待实施边界；2026-11-09 补充 ADR 125 替代范围 |
| [`48-cli-first-class-release.md`](./48-cli-first-class-release.md) | 2026-07-20 | 2026-11-15 | 补充重号消歧说明及 macOS 发布签名/公证对齐；2026-11-06 [ADR 108-cli](108-cli-basic-shell-commands.md) 收窄「CLI 自动更新可缓做」 |
| [`48-provider-model-options.md`](./48-provider-model-options.md) | 2026-07-17 | 2026-11-15 | 补充重号消歧说明，并与 ADR 28 / 37 / 83 对齐选项边界 |
| [`49-cancel-path-hard-sandbox.md`](./49-cancel-path-hard-sandbox.md) | 2026-07-21 | 2026-11-15 | 跨 ADR 对齐：明确被 ADR 90 / 92 / 101 / 106 部分取代的范围 |
| [`50-cli-system-proxy-fallback.md`](./50-cli-system-proxy-fallback.md) | 2026-07-22 | 2026-07-22 | 代码已落地：`apps/tui` 新增 macOS 系统代理读取 + env 回退，bun test 17 pass / tsc EXIT=0 |
| [`51-unified-desktop-cli-file-tools.md`](./51-unified-desktop-cli-file-tools.md) | 2026-07-22 | 2026-07-23 | 日期有更新，括号未写原因 |
| [`52-unified-next-request-context-accounting.md`](./52-unified-next-request-context-accounting.md) | 2026-07-23 | 2026-07-25 | 日期有更新（标明部分被 ADR 56 取代） |
| [`56-provider-observed-context-accounting.md`](./56-provider-observed-context-accounting.md) | 2026-07-25 | 2026-11-15 | 跨 ADR 对齐：明确 `input_prediction` 预约与 UTF-8 估算迁出 `requests.jsonl`，守护不变式 1 / 7 |
| [`57-canonical-conversation-history-projector.md`](./57-canonical-conversation-history-projector.md) | 2026-07-25 | 2026-11-15 | 跨 ADR 对齐：登记 [ADR 97](97-reasoning-replay-and-continuation-custody.md) / [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 两条窄例外与 mid-turn `_compaction` 冷重载不变量 |
| [`59-appshots-capability-boundary.md`](./59-appshots-capability-boundary.md) | 2026-07-30 | 2026-11-15 | 补充重号消歧说明；P0a 边界保留 |
| [`59-browser-panel-reveal-capability.md`](./59-browser-panel-reveal-capability.md) | 2026-08-03 | 2026-11-15 | 补充重号消歧说明，并标注受 ADR 66 / 72 / 85 / 109 收窄的适用范围 |
| [`60-quick-chat-independent-popover-window.md`](./60-quick-chat-independent-popover-window.md) | 2026-07-30 | 2026-11-15 | 规范标注 Accepted 并对齐 `effort` 全词表与渠道分组口径 |
| [`61-beta-to-stable-channel-graduation.md`](./61-beta-to-stable-channel-graduation.md) | 2026-08-03 | 2026-11-15 | 跨 ADR 对齐：将 `auto` 自动毕业规则由仅 `-beta` 扩展至 `-alpha` / `-beta` / `-rc` 全预发布通道，对齐 [ADR 54](54-open-runtime-public-packages-and-release-policy.md) 与 [ADR 108-cli](108-cli-basic-shell-commands.md) |
| [`62-automation-runtime-boundary.md`](./62-automation-runtime-boundary.md) | 2026-08-04 | 2026-11-15 | 补充 Automation worktree 与共享 Git 写入的资源 claim 准入约束 |
| [`63-user-artifact-evidence-boundary.md`](./63-user-artifact-evidence-boundary.md) | 2026-08-16 | 2026-11-15 | 补充 ADR 90 对部分 GIF/WebP 预览须走 Chromium bitmap 解码器的边界约束 |
| [`64-workbench-source-highlight-without-monaco.md`](./64-workbench-source-highlight-without-monaco.md) | 2026-08-17 | 2026-11-15 | 跨 ADR 对齐：标注聊天开块延迟高亮与 ADR 109 R9/R10 用户显式编辑对部分前提的演进 |
| [`65-cli-headless-exec.md`](./65-cli-headless-exec.md) | 2026-08-18 | 2026-11-15 | 跨 ADR 对齐：同步裸 `peer` 默认进入 Bot 壳 / `--classic`、权限遵循 ADR 101、基础壳命令 `doctor` / `sessions resume` 等归入 ADR 108-cli |
| [`66-browser-headless-fallback-execution.md`](./66-browser-headless-fallback-execution.md) | 2026-08-21 | 2026-11-15 | 明确 L1 headless 降级适用于经典对话内嵌 `<webview>`；0.1.0 Project Bot 后台任务走 ADR 71 L2 + ADR 38 `web_fetch`；2026-11-14 曾修正架构文档引用 |
| [`67-task-shell-workbench-radar.md`](./67-task-shell-workbench-radar.md) | 2026-08-22 | 2026-11-15 | 明确原型 A 默认 0.1 壳层已被 ADR 80 / ADR 84 取代 |
| [`68-goal-delivery-mode-contract.md`](./68-goal-delivery-mode-contract.md) | 2026-08-26 | 2026-11-15 | 标明 Project Bot 模式下默认直写与无确认合回已由 ADR 80 决策 7–8 取代，并受 ADR 116 / 127 资源占用锁约束 |
| [`69-handoff-triage-classifier.md`](./69-handoff-triage-classifier.md) | 2026-08-26 | 2026-11-15 | 标明 Project Bot 模式下静默 `AUTO_MERGE` 由 ADR 80 决策 7–8 取代，且合回写入受 ADR 116 / 127 资源锁约束 |
| [`70-l1-browser-action-surface.md`](./70-l1-browser-action-surface.md) | 2026-09-01 | 2026-11-15 | 明确引用消歧为 [ADR 59-browser](59-browser-panel-reveal-capability.md) |
| [`71-l2-playwright-external-browser.md`](./71-l2-playwright-external-browser.md) | 2026-09-01 | 2026-11-15 | 消解§决策一内部工具面矛盾，并明确 0.1.0 Project Bot `work_session` 使用 L2 + `web_fetch` 的隔离地位 |
| [`72-l1-default-web-entry.md`](./72-l1-default-web-entry.md) | 2026-09-02 | 2026-11-15 | 收窄适用范围：L1 默认网页入口仅限经典前台会话；0.1.0 Project Bot 模式遵循 ADR 85 决策 5 |
| [`73-goal-interruption-suspension-vs-failure.md`](./73-goal-interruption-suspension-vs-failure.md) | 2026-09-03 | 2026-11-15 | 澄清 Project Bot 模式下受委派 WorkSession 技术中断由主 Bot 接管续接；保留 `interrupted` 持久化规则与取消终态优先权 |
| [`74-deployment-surfaces-and-local-storage.md`](./74-deployment-surfaces-and-local-storage.md) | 2026-09-06 | 2026-11-15 | 状态规范为 Accepted，与 [ADR 48-cli](48-cli-first-class-release.md)、[ADR 81](81-project-agent-memory-system.md)、[ADR 85](85-project-agent-hosts-inputs-and-surfaces.md)、[ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md)、[ADR 121](121-desktop-session-windowing-contract.md) 对齐 |
| [`75-remote-read-preflight.md`](./75-remote-read-preflight.md) | 2026-09-26 | 2026-11-15 | 跨 ADR 对齐：补注 [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 决策 8 的 4 个 opt-in project 操作与远程无授权底线 |
| [`76-peer-acp-agent.md`](./76-peer-acp-agent.md) | 2026-09-08 | 2026-11-15 | 状态规范标注为 `Accepted`，与 [ADR 48-provider](48-provider-model-options.md) / [ADR 83](83-model-routing-by-role.md) 选项契约保持一致 |
| [`77-image-generation-capability.md`](./77-image-generation-capability.md) | 2026-09-15 | 2026-11-15 | 明确工作区外生成图片的会话 `imageReadGrant` 边界对齐 [ADR 90](90-local-image-capability-and-product-review.md) / [ADR 92](92-scoped-permission-inheritance.md)；状态仍为 Proposed |
| [`78-intake-ui-delivery-arm.md`](./78-intake-ui-delivery-arm.md) | 2026-09-23 | 2026-11-15 | 标明与 Project Agent 连续核验及意图闭环的衔接 |
| [`80-project-agent-delegation-model.md`](./80-project-agent-delegation-model.md) | 2026-09-24 | 2026-10-10 | ADR 91 补充自主协调、目标修订与取消重派 |
| [`81-project-agent-memory-system.md`](./81-project-agent-memory-system.md) | 2026-09-24 | 2026-11-15 | 对齐 ADR 85 存储根 `<dataRoot>/projects/<workspaceId>/memory/` 与 `<dataRoot>/memory/`；2026-09-26 P0-2 评审结论不变 |
| [`82-project-objectives-and-watches.md`](./82-project-objectives-and-watches.md) | 2026-09-24 | 2026-11-15 | 对齐 `watches` 仅限本机执行、`act` 写盘走资源 claim 锁，以及用户目标作为持续委派锚点的地位 |
| [`83-model-routing-by-role.md`](./83-model-routing-by-role.md) | 2026-09-24 | 2026-11-15 | 明确三层模型切换边界：同模型单次重试 / 档位边界切换 / 主 Bot 重基 vs 子任务冻结；对齐 effort 全词表、渠道能力裁剪及专用通道归属 |
| [`84-bot-list-shell.md`](./84-bot-list-shell.md) | 2026-09-26 | 2026-11-15 | 补充 [ADR 109](109-resource-reference-preview-and-artifact-collaboration.md) 与 [ADR 125](125-resource-window-directory-tabs.md) 新增第 4 栏可展开资源工作区与独立资源窗口 `NativeResourceWindow`；原 2026-09-30 角色更新保留 |
| [`85-project-agent-hosts-inputs-and-surfaces.md`](./85-project-agent-hosts-inputs-and-surfaces.md) | 2026-09-26 | 2026-11-15 | 明确后台 `work_session` 的 L2 Playwright + `web_fetch` 网页隔离与 L1 用户资源标签归属，以及 ADR 87 展示交接契约 |
| [`86-batched-persisted-conversation-reads.md`](./86-batched-persisted-conversation-reads.md) | 2026-10-02 | 2026-11-15 | 补充与 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 及 [ADR 121](121-desktop-session-windowing-contract.md) 的演进边界 |
| [`87-user-turn-live-process-presentation.md`](./87-user-turn-live-process-presentation.md) | 2026-10-05 | 2026-11-15 | 修复 D1 对 ADR 111 的错误编号引用，原 `2026-11-09` 追加过程叙述与正式交付分离修订；同日经用户（负责人）接受，D1 表"接受本草案后修订的范围"列所列条款替代生效；实施未完成，V01–V17 待验证 |
| [`88-project-agent-execution-continuity.md`](./88-project-agent-execution-continuity.md) | 2026-10-07 | 2026-11-15 | 补充 §7.2 / §11.2 / §21.2 跨 ADR 部分取代与演进指针；2026-11-01 关联 ADR 117 实施边界；§22 中断核验契约保留 |
| [`89-independent-agent-delegation-and-communication.md`](./89-independent-agent-delegation-and-communication.md) | 2026-10-10 | 2026-10-10 | 补充 ADR 91 自主协调设计引用 |
| [`91-project-bot-autonomous-coordination.md`](./91-project-bot-autonomous-coordination.md) | 2026-10-10 | 2026-11-15 | 明确 ADR 82 用户确认的持久 `ProjectObjective(act)` 为合法持续委派来源之一，且受资源 claim 锁约束；2026-11-05 第 15 节身份解析、派发责任与独立 PR 候选 |
| [`92-scoped-permission-inheritance.md`](./92-scoped-permission-inheritance.md) | 2026-10-11 | 2026-10-21 | 日期有更新（ADR 101 局部取代 §9.3） |
| [`93-verification-continuity-and-repair-ownership.md`](./93-verification-continuity-and-repair-ownership.md) | 2026-10-18 | 2026-11-01 | 关联 ADR 117 实施边界 |
| [`94-reply-attempts-silent-wait-and-recovery.md`](./94-reply-attempts-silent-wait-and-recovery.md) | 2026-10-18 | 2026-11-01 | 关联 ADR 117 实施边界 |
| [`95-progress-driven-execution-policy.md`](./95-progress-driven-execution-policy.md) | 2026-10-18 | 2026-11-06 | 消息终态、稳定输入排序与恢复事实补充 |
| [`96-task-execution-responsiveness.md`](./96-task-execution-responsiveness.md) | 2026-10-18 | 2026-11-15 | 补充 §3.1 与 ADR 104-progressive、§3.3 与 ADR 121 的演进衔接说明；2026-11-06 消息终态、稳定输入排序与恢复事实补充 |
| [`97-reasoning-replay-and-continuation-custody.md`](./97-reasoning-replay-and-continuation-custody.md) | 2026-10-18 | 2026-11-15 | 跨 ADR 对齐：补全 ADR 19 相对链接，并作为窄例外登记入 ADR 57 |
| [`98-large-history-execution-responsiveness.md`](./98-large-history-execution-responsiveness.md) | 2026-10-18 | 2026-10-20 | 日期有更新，括号未写原因 |
| [`99-authoritative-reply-receipts-and-model-recovery.md`](./99-authoritative-reply-receipts-and-model-recovery.md) | 2026-10-19 | 2026-11-15 | 修正 Architecture 文档引用；明确主 Bot 模型重基与 `work_session` 冻结分工的边界 |
| [`102-unified-task-lifecycle-projection.md`](./102-unified-task-lifecycle-projection.md) | 2026-10-21 | 2026-11-15 | 明确关联引用为 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) |
| [`104-bot-capability-visibility.md`](./104-bot-capability-visibility.md) | 2026-10-22 | 2026-11-15 | 补充重号消歧说明，清理外部未合入的自定义指令草案引用并标明对 ADR 58 的拟取代范围 |
| [`104-progressive-interaction-and-coordination-storage.md`](./104-progressive-interaction-and-coordination-storage.md) | 2026-10-22 | 2026-11-15 | 补充重号消歧说明，并与 §9 统一 read-models 存储路径表述；2026-10-28 历史分叉、安全恢复与旧 writer 屏障补充 |
| [`105-portable-coordination-baseline-integrity.md`](./105-portable-coordination-baseline-integrity.md) | 2026-10-22 | 2026-11-15 | 规范标注 `状态：Accepted` 并消歧 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) |
| [`106-readonly-git-and-delegation-capability-admission.md`](./106-readonly-git-and-delegation-capability-admission.md) | 2026-10-23 | 2026-11-15 | 明确依赖指向 ADR 104-progressive，与重号 Proposed 草案 ADR 104-visibility 消歧 |
| [`108-bot-reply-document-preview.md`](./108-bot-reply-document-preview.md) | 2026-10-24 | 2026-11-15 | 补充重号消歧说明，并标注展示容器部分由 ADR 109 / 114 取代 |
| [`108-cli-basic-shell-commands.md`](./108-cli-basic-shell-commands.md) | 2026-11-06 | 2026-11-15 | 补充重号消歧说明，并对齐 `peer update` 跨频道毕业语义 |
| [`109-resource-reference-preview-and-artifact-collaboration.md`](./109-resource-reference-preview-and-artifact-collaboration.md) | 2026-10-25 | 2026-11-15 | 跨 ADR 对齐：更新 §§1–39 全节覆盖说明，标注目录标签/头部快捷入口被 [ADR 125](125-resource-window-directory-tabs.md) 部分取代，§23 裸文件名规则被 [ADR 114](114-reply-citation-resolution-and-open.md) 取代；原 2026-10-27 补充 §35 记录保留 |
| [`110-follow-up-responsibility-and-current-list.md`](./110-follow-up-responsibility-and-current-list.md) | 2026-10-28 | 2026-11-15 | 补充 ADR 126 / 127 对 `indexed` / 未知 claim 闭包与 `plan.status` 边界的衔接说明；2026-11-08 同步 ADR 124 可见性修订 |
| [`111-project-agent-duplex-supervision-and-continuity.md`](./111-project-agent-duplex-supervision-and-continuity.md) | 2026-10-28 | 2026-11-15 | 明确 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 引用消歧 |
| [`112-runtime-module-and-loading-boundaries.md`](./112-runtime-module-and-loading-boundaries.md) | 2026-10-28 | 2026-11-01 | 关联 ADR 117 实施边界 |
| [`113-checkpoint-content-addressed-storage-and-retention.md`](./113-checkpoint-content-addressed-storage-and-retention.md) | 2026-10-29 | 2026-11-15 | 跨 ADR 对齐：将拟议特性门槛从 `6` 迁至 `> 11` 未占用代次，并明确引用 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md)；全文仍为 Proposed |
| [`114-reply-citation-resolution-and-open.md`](./114-reply-citation-resolution-and-open.md) | 2026-10-30 | 2026-11-15 | 消歧 [ADR 108-bot](108-bot-reply-document-preview.md) 引用 |
| [`115-input-prediction-and-draft-boundary.md`](./115-input-prediction-and-draft-boundary.md) | 2026-10-31 | 2026-11-15 | 跨 ADR 对齐：`input_prediction` 账本分拆为 `usage/input-prediction.jsonl` 并收口单开关契约 |
| [`116-session-control-and-resource-settlement.md`](./116-session-control-and-resource-settlement.md) | 2026-11-01 | 2026-11-15 | 标注 ADR 126 / 127 已接受，对 §6.1–§6.3 / §12 的部分取代；2026-11-08 曾确认 ADR 124 可见性修订不改释放条件 |
| [`117-intent-driven-coordination-and-goal-closure.md`](./117-intent-driven-coordination-and-goal-closure.md) | 2026-11-01 | 2026-11-15 | 补充 ADR 82 持久目标作为合法委派来源，以及与 ADR 120 / 126 / 127 对 §14–§15 资源等待契约的对齐 |
| [`118-openui-interactive-results-and-runtime-boundaries.md`](./118-openui-interactive-results-and-runtime-boundaries.md) | 2026-11-02 | 2026-11-05 | 2026-11-05 用户接受 IUI-00—04 首期范围并纳入 RC36 集成与发布验证 |
| [`119-user-stop-cognition-admission-and-settlement.md`](./119-user-stop-cognition-admission-and-settlement.md) | 2026-11-03 | 2026-11-15 | 跨 ADR 对齐：标明 §6.3 `FollowUp.handling` 与 §12 门禁 `10` 已被 [ADR 120](120-runtime-facts-disposition-and-resource-wait.md) / [ADR 124](124-legacy-stop-obligation-controlled-resolution.md) 事实取代；本文仍为 Proposed |
| [`120-runtime-facts-disposition-and-resource-wait.md`](./120-runtime-facts-disposition-and-resource-wait.md) | 2026-11-03 | 2026-11-08 | 文末确认 ADR 124 的退役索引不对用户开放，且不改变本文的停止确认归属 |
| [`121-desktop-session-windowing-contract.md`](./121-desktop-session-windowing-contract.md) | 2026-11-05 | 2026-11-15 | 跨 ADR 对齐：准确区分 `BotSqliteAdapter` 消费 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 交互 SQLite 读模型与 `store.appendMessage` JSONL 持久真源 |
| [`123-main-bot-unnoticed-memory.md`](./123-main-bot-unnoticed-memory.md) | 2026-11-06 | 2026-11-15 | 跨 ADR 对齐：更名为「无感上下文整理（情节压缩）」，增补 `L7_CONTINUITY` 与 [ADR 81](81-project-agent-memory-system.md) 预算仲裁、复用 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) SQLite/FTS 及非阻塞回读约束；本文仍为 Proposed |
| [`124-legacy-stop-obligation-controlled-resolution.md`](./124-legacy-stop-obligation-controlled-resolution.md) | 2026-11-07 | 2026-11-15 | 同步 ADR 126 / 127 对 §1.5 / §4.1 / §6.2 / §8.3 / §13 的部分取代，并澄清旧暂停 `paused` 与新撤回 `cancelled` 的 `plan.status` 边界；2026-11-08 修订待核实不对用户开放 |
| [`125-resource-window-directory-tabs.md`](./125-resource-window-directory-tabs.md) | 2026-11-09 | 2026-11-15 | 跨 ADR 对齐：在被替代条款补入 [ADR 109](109-resource-reference-preview-and-artifact-collaboration.md)，并显式保留 [ADR 118](118-openui-interactive-results-and-runtime-boundaries.md) `interactive` 标签与 §17.4 布局兼容 |
| [`126-execution-resource-claim-closure-and-unknown-retention.md`](./126-execution-resource-claim-closure-and-unknown-retention.md) | 2026-11-09 | 2026-11-15 | 正式转为 Accepted，与 ADR 127 配套生效；对齐克隆交回边界与格式门槛说明；2026-11-09 曾由 ADR 125 改号为 ADR 126 |
| [`127-unknown-outcome-reconciliation-and-delegated-resolution.md`](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) | 2026-11-09 | 2026-11-15 | 同步 ADR 126 为 Accepted，明确列出对 ADR 116 / 124 的部分取代条款及已退役条目的设置/诊断入口边界 |

## 过时引用

| 位置 | 仍写着 | 被指文件现在的页头 |
|---|---|---|
| [`knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`](../architecture/22-tui-desktop-shared-runtime-and-host-governance.md#L27) | ADR 65（`peer exec`）是 `Proposed` | [`65-cli-headless-exec.md`](./65-cli-headless-exec.md) 页头为 `Accepted`（P0 已落地，2026-11-15 对齐基础壳命令至 ADR 108-cli） |

## 目录

「读取」一列压缩页头核心状态与跨 ADR 边界提示，细节以各文件正文与「后续」为准。

### 0001 凭据

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 0001 | [ADR 0001：跨平台凭证 Vault 与统一 Helper](./0001-cross-platform-credential-vault.md) | 2026-07-15 | 2026-07-15 | 页头已接受（跨宿主 fail-closed 凭据基线） |

### 15–18 早期能力草案

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 15 | [Plugin / Skill / MCP 能力体系设计](./15-plugin-skill-mcp-system.md) | 2026-05-20 | 2026-11-15 | 设计草案（局部作废：云端 Skill / wildcard `allow` / `<userData>` 路径已被 16/49/58/74/85/92/101 取代） |
| 16 | [Peer Agent Runtime 调用生命周期](./16-skill-call-lifecycle.md) | — | 2026-11-15 | 部分作废（本地能力链与 `scope.cwd` 有效；「宙斯 / Cloud CEO Gateway」已作废） |
| 17 | [Local Context Compaction 机制设计](./17-local-context-compaction.md) | 2026-06-08 | 2026-11-15 | 设计草案（`0.75/0.95` 与 `user` 交接块已被 ADR 55 / 56 / 57 与 Architecture 19 取代） |
| 18 | [Claude Code 风格文件编辑机制计划](./18-claude-code-style-file-edit-plan.md) | 2026-06-09 | 2026-11-15 | 历史计划草案（§1–§12 已并入 ADR 51；§13 已独立为 ADR 29） |

### 21–79 宿主、工具、浏览器与发布

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 21 | [ADR 21 — 跨重启的任务续传（Pending Task Resume，会话锚定版）](./21-pending-task-resume.md) | — | 2026-11-15 | Accepted（适用经典单会话 `/restart`；Project Agent 由 ADR 88 / 104-progressive / 111 承接） |
| 22 | [ADR 22 — HMR/重载后的流式重连(Stream Reattach on Reload)](./22-stream-reattach-on-reload.md) | — | 2026-11-15 | Accepted（隐藏思考回传渲染层与单活跃流前提已被 ADR 85 / 87 / 121 部分取代） |
| 24 | [Provider Cache And Empty Response Guard](./24-provider-cache-and-empty-response-guard.md) | 2026-06-11 | 2026-11-15 | Accepted（修正治理基线路径） |
| 25 | [Runtime Usage Ledger](./25-runtime-usage-ledger.md) | 2026-06-25 | 2026-11-15 | Accepted（`requests.jsonl` 与 ADR 115 `input_prediction` 账本物理隔离） |
| 26 | [ADR 26 — Agent Loop Termination Semantics](./26-agent-loop-termination.md) | 2026-06-12 | 2026-11-15 | Accepted（单回合模型循环无上限；Project Agent 自主协调另受 ADR 88/95/96/103/117 约束） |
| 27 | [ADR 27 — 工作区切换与跨工作区运行可见性(Workspace Switch & Cross-Workspace Running)](./27-workspace-switch-and-cross-workspace-running.md) | — | 2026-11-15 | Accepted（跨项目并发投影与侧栏可见性已由 ADR 80 / 84 / 85 扩展承接） |
| 28 | [28. OpenAI Subscription OAuth (ChatGPT Login)](./28-openai-subscription-oauth.md) | — | 2026-11-15 | Accepted（`oauth_chatgpt` 为 OpenAI 官方专属通道；修正旧 `ADR 23` 至 ADR 37；对齐 `effort`） |
| 29 | [29. 工具调用参数流式进度（Tool Arg Progress Streaming）](./29-tool-arg-progress-streaming.md) | — | — | 页头已接受 |
| 30 | [30. Provider Recovery Broker](./30-provider-recovery-broker.md) | 2026-06-15 | 2026-11-15 | Accepted（第一层同模型退避重试；区分 ADR 83 档位切换与 ADR 99 主 Bot 重基；标注外部 KXT 引用） |
| 31 | [31. MCP 连接管理与设置入口](./31-mcp-connection-management.md) | 2026-06-15 | 2026-11-15 | Accepted（Desktop + CLI/TUI 共用 `<dataRoot>` `mcp-registry`，凭据强制走 ADR 0001 Vault） |
| 32 | [ADR 32: MCP Authentication and Credential Injection](./32-mcp-authentication.md) | 2026-06-16 | 2026-11-15 | Accepted（合入 `oauth2`，废止 `file-fallback`，强制迁入 ADR 0001 `peer-credential-helper`） |
| 33 | [Per-Message Turn Duration Persistence](./33-per-message-turn-duration.md) | 2026-06-17 | 2026-11-15 | Accepted（活跃对话与 Project Bot 主链路中 `replace-messages` 已被增量 `append` 取代） |
| 34 | [Conversation Delete Cascades to Goal Plans](./34-conversation-delete-goal-plan-cascade.md) | 2026-06-18 | 2026-11-15 | Accepted（硬删除收窄至经典空闲对话；0.1.0 须遵守资源锁与 unknown 义务约束） |
| 35 | [Mode-Scoped Tool Projection](./35-mode-scoped-tool-projection.md) | — | 2026-11-15 | Accepted（演进为 `mode × role × host × botAdmission` 四维矩阵，对齐 `project_agent`/`explorer`/`verifier`） |
| 36 | [36. MCP 工具卡标题透传（MCP Tool Card Title Passthrough）](./36-mcp-tool-card-title-passthrough.md) | — | — | 页头已接受 |
| 37 | [37. Provider Channel 与 Wire 协议分离](./37-provider-channel-and-wire-protocol-separation.md) | 2026-06-18 | 2026-11-15 | Accepted（`effort` 统一为 `off \| low \| medium \| high \| xhigh \| max`，与 ADR 48-provider / 83 联动裁剪） |
| 38 | [38. Web Search / Fetch Provider（联网搜索与读链接能力）](./38-web-search-fetch-provider.md) | 2026-06-20 | 2026-11-15 | 分阶段：Phase 1 `web_fetch` Accepted（跨宿主无 `BrowserWindow` 落地）；Phase 2 `web_search` Proposed |
| 39 | [39. 应用更新下载交互改造（非模态后台下载）](./39-updater-download-ux.md) | 2026-06-25 | 2026-11-15 | Accepted（macOS 签名公证前提见 ADR 0001 §5 / ADR 48-cli；渠道升级见 ADR 61） |
| 40 | [40. 内嵌浏览器 + Agent 操控（webview 载体 + webContents 直控桥）](./40-embedded-browser-and-agent-control.md) | 2026-06-25 | 2026-11-15 | Accepted（经典/独立窗保留 L1；0.1.0 `work_session` 已按 ADR 71 / 85 剥离 L1） |
| 41 | [ADR 41：将现有「Goal 模式」正名为「Plan 模式」](./41-rename-goal-mode-to-plan-mode.md) | 2026-06-30 | 2026-11-15 | 部分被替代（`plan` wire 迁移有效；「Runner 独占」与 §5 选型表已被 B2-b 推翻） |
| 42 | [ADR 42：上下文计数口径分离（显示口径 vs 压缩触发口径）](./42-context-display-vs-trigger-accounting.md) | 2026-06-30 | 2026-11-15 | Superseded（整体契约已被 ADR 52 与现行 ADR 56 取代） |
| 43 | [会话运行时状态按 conversationId 分桶（消灭跨会话串内容）](./43-conversation-runtime-state-bucketing.md) | 2026-07-01 | 2026-11-15 | Accepted（分桶与跨流路由原则已向 ADR 87 与 ADR 121 演进） |
| 44 | [44. 全局动效体系：自建语义基元 + 激进收敛（不引第三方库）](./44-motion-system-consolidation.md) | 2026-07-01 | 2026-07-01 | 页头已接受 |
| 45 | [45. MCP OAuth 配置交互简化：探测即自动配置 + 回调地址只读 + 授权端点自动发现](./45-mcp-oauth-config-ux-simplification.md) | 2026-07-01 | 2026-11-15 | Accepted（对齐跨宿主 OAuth 安全边界与 ADR 0001 / ADR 32） |
| 46 | [46. 会话绑定的 Workbench 与多标签浏览器](./46-conversation-bound-browser-tabs.md) | 2026-07-15 | 2026-11-15 | Accepted（`work_session` 改走 L2；用户资源窗口/独立窗与 ADR 109 / 125 对齐） |
| 47 | [47. Workbench 多资源标签模型](./47-workbench-multi-resource-tabs.md) | 2026-07-15 | 2026-11-15 | Accepted（决策一第 4 条在资源窗口范围被 ADR 125 取代；兼容 ADR 118 `interactive` 与 ADR 109） |
| 48 | [CLI First-Class Release（CLI 与 Desktop 同仓一等发布）](./48-cli-first-class-release.md) | 2026-07-20 | 2026-11-15 | Accepted（CLI + npm 安装面；macOS 签名公证；ADR 108-cli 收窄自动更新条款） |
| 48 | [48. 渠道无关的模型选项与渠道投影](./48-provider-model-options.md) | 2026-07-17 | 2026-11-15 | Accepted（渠道选项投影；`effort` 与上下文裁剪对齐 ADR 28 / 37 / 83） |
| 49 | [49. 取消路径硬沙箱（允许跨工作区读写）](./49-cancel-path-hard-sandbox.md) | 2026-07-21 | 2026-11-15 | Accepted（跨工作区边界已被 ADR 90 / 92 / 101 / 106 部分取代） |
| 50 | [50. CLI 系统代理回退（macOS）](./50-cli-system-proxy-fallback.md) | 2026-07-22 | 2026-07-22 | 页头已接受（代码已落地） |
| 51 | [Unified Desktop and CLI File Tools（桌面端与 CLI 文件工具统一）](./51-unified-desktop-cli-file-tools.md) | 2026-07-22 | 2026-07-23 | 页头已接受（吸收 ADR 18 §1–§12） |
| 52 | [ADR 52：统一下一次请求上下文统计](./52-unified-next-request-context-accounting.md) | 2026-07-23 | 2026-07-25 | 部分被替代（估算权威已被 ADR 56 取代；最终投影等边界保留） |
| 53 | [Tool Call Duration Accounting](./53-tool-call-duration-accounting.md) | 2026-07-23 | 2026-07-23 | 页头已接受 |
| 54 | [ADR 54：开放 Runtime 公开包与发布策略](./54-open-runtime-public-packages-and-release-policy.md) | 2026-07-24 | 2026-07-24 | 页头已接受 |
| 55 | [ADR 55：Desktop 与 TUI 统一 System Context Assembler](./55-shared-system-context-assembler.md) | 2026-07-25 | 2026-07-25 | 页头已接受 |
| 56 | [ADR 56：Provider 实测优先的精确上下文记账](./56-provider-observed-context-accounting.md) | 2026-07-25 | 2026-11-15 | Accepted（实测优先上下文权威；明确 ADR 115 `input_prediction` 估算迁出 `requests.jsonl`） |
| 57 | [ADR 57：Desktop 与 TUI 统一 Canonical Conversation History Projector](./57-canonical-conversation-history-projector.md) | 2026-07-25 | 2026-11-15 | Accepted（登记 ADR 97 / 104-progressive 两条窄例外及 `_compaction` 冷重载不变量） |
| 58 | [本地 Skill 范围与工作空间挂载](./58-local-skill-scope-and-workspace-mounting.md) | 2026-07-27 | 2026-07-27 | 页头已接受（取代 ADR 15 云端 `SkillDefinition`；ADR 104-visibility 为拟议后续） |
| 59 | [Appshots 能力边界与 Evidence 链](./59-appshots-capability-boundary.md) | 2026-07-30 | 2026-11-15 | Accepted（P0a 边界保留） |
| 59 | [59. Browser 面板主动打开与可见工作现场闭环](./59-browser-panel-reveal-capability.md) | 2026-08-03 | 2026-11-15 | Accepted（`work_session` reveal 边界受 ADR 66 / 72 / 85 / 109 收窄） |
| 60 | [Quick Chat 独立 Popover 窗](./60-quick-chat-independent-popover-window.md) | 2026-07-30 | 2026-11-15 | Accepted（`effort` 由 ADR 37 / 48-provider 统一；`model` 分组与 ADR 76 共享） |
| 61 | [61. beta→stable 通道自动毕业决策](./61-beta-to-stable-channel-graduation.md) | 2026-08-03 | 2026-11-15 | Accepted（`auto` 毕业扩展至 `-alpha` / `-beta` / `-rc` 全预发布通道，对齐 ADR 54 / 108-cli） |
| 62 | [62. Automation Runtime 与持久化边界](./62-automation-runtime-boundary.md) | 2026-08-04 | 2026-11-15 | Accepted（补充 Automation worktree 与共享 Git 写入的资源 claim 准入约束） |
| 63 | [63. 用户产物与 Evidence 边界](./63-user-artifact-evidence-boundary.md) | 2026-08-16 | 2026-11-15 | Accepted（补充 ADR 90 对部分 GIF/WebP 预览须走 Chromium bitmap 解码器约束） |
| 64 | [64. Workbench 源码预览先复用 highlight.js，不上 Monaco](./64-workbench-source-highlight-without-monaco.md) | 2026-08-17 | 2026-11-15 | Accepted（按帧全树高亮由 ADR 121 延迟高亮取代；只读前提对 ADR 109 R9/R10 放宽） |
| 65 | [65. CLI 无头发起（`peer exec`）](./65-cli-headless-exec.md) | 2026-08-18 | 2026-11-15 | Accepted（P0 已落地；无回合上限；裸 `peer` 与基础壳命令对齐 ADR 84 / 108-cli） |
| 66 | [66. 浏览器工具的后台降级执行（Headless Fallback）](./66-browser-headless-fallback-execution.md) | 2026-08-21 | 2026-11-15 | Accepted（适用于经典内嵌 `<webview>`；Project Bot 后台走 L2 + `web_fetch`） |
| 67 | [67. 任务壳 + 工作台雷达（原型 A）](./67-task-shell-workbench-radar.md) | 2026-08-22 | 2026-11-15 | Superseded in default 0.1 shell（默认 0.1 壳层已切至 ADR 80 / ADR 84；仅作历史对照） |
| 68 | [68. 交付模式契约：direct 与隔离合回统一语义](./68-goal-delivery-mode-contract.md) | 2026-08-26 | 2026-11-15 | Accepted（经典 Goal 基线；Project Bot 下默认直写与无确认合回已由 ADR 80 取代） |
| 69 | [69. 合回分流（Triage）分类器：结构化 verdict 替代布尔判定](./69-handoff-triage-classifier.md) | 2026-08-26 | 2026-11-15 | Accepted（分类诊断保留；Project Bot 下静默 `AUTO_MERGE` 已由 ADR 80 取代） |
| 70 | [70. L1 内嵌浏览器动作面扩展（hover / scroll / key / drag）](./70-l1-browser-action-surface.md) | 2026-09-01 | 2026-11-15 | Accepted（引用消歧至 ADR 59-browser） |
| 71 | [71. L2 受控外部浏览器（Playwright / CDP）安全模型](./71-l2-playwright-external-browser.md) | 2026-09-01 | 2026-11-15 | Accepted（L2 第一刀已落地；为 0.1.0 `work_session` 唯一受委派浏览器执行层） |
| 72 | [72. 网页任务默认入口：L1 内置浏览器（`browser_*`）](./72-l1-default-web-entry.md) | 2026-09-02 | 2026-11-15 | Accepted（仅限经典前台会话；0.1.0 Project Bot 遵循 ADR 85 决策 5） |
| 73 | [73. Goal 中断挂起与失败解耦的状态契约](./73-goal-interruption-suspension-vs-failure.md) | 2026-09-03 | 2026-11-15 | Accepted（受委派 WorkSession 技术中断由主 Bot 接管续接；保留 `interrupted` 与取消终态） |
| 74 | [74. 部署面与本机存储策略](./74-deployment-surfaces-and-local-storage.md) | 2026-09-06 | 2026-11-15 | Accepted（本机 `<dataRoot>` 分层基线已在 ADR 81/85/104-progressive/121 落地；远端拓扑渐进演进） |
| 75 | [75. 远程读取预检：通过不等于获得执行权](./75-remote-read-preflight.md) | 2026-09-26 | 2026-11-15 | Accepted（补注 ADR 85 决策 8 四项 opt-in 操作与远程无授权底线） |
| 76 | [ADR 76：Peer 作为 ACP Agent](./76-peer-acp-agent.md) | 2026-09-08 | 2026-11-15 | Accepted（实施边界已定；与 ADR 48-provider / 83 选项契约一致，打包验收另记） |
| 77 | [77. 多服务图片生成能力与凭证、产物边界](./77-image-generation-capability.md) | 2026-09-15 | 2026-11-15 | Proposed（未接受；工作区外 `imageReadGrant` 对齐 ADR 90 / 92） |
| 78 | [78. Intake 期武装 UI 交付视觉验证门](./78-intake-ui-delivery-arm.md) | 2026-09-23 | 2026-11-15 | Accepted（与 ADR 80 / 88 / 117 连续核验及意图闭环协同生效） |
| 79 | [79. 移除预配置基准分支：交付绑定跟随工作区实时 HEAD](./79-remove-preconfigured-base-branch.md) | 2026-09-23 | — | 页头已接受 |

### 80–99 0.1.0 项目代理与执行链

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 80 | [80. 项目代理委托模型：一个项目一个代理，任务由代理开出](./80-project-agent-delegation-model.md) | 2026-09-24 | 2026-10-10 | 页头已接受（2026-10-10 补充 ADR 91；阶段 F 已按 2026-10-23 核对进入 0.1.0 RC 收敛） |
| 81 | [81. 项目代理记忆体系：带来源的事实记录，只进事实层，自动但可撤](./81-project-agent-memory-system.md) | 2026-09-24 | 2026-11-15 | Accepted（对齐 ADR 85 `<dataRoot>/projects/<workspaceId>/memory/` 与 `<dataRoot>/memory/` 存储根） |
| 82 | [82. 项目目标与定时 / 事件驱动推进](./82-project-objectives-and-watches.md) | 2026-09-24 | 2026-11-15 | Accepted（`watches` 仅限本机；`act` 写盘受资源 claim 锁约束；为用户目标持续委派锚点） |
| 83 | [83. 模型分工：档位 + 角色，用户说了算，开任务时冻结](./83-model-routing-by-role.md) | 2026-09-24 | 2026-11-15 | Accepted（三层切换：30 重试 / 83 边界切换 / 99 主 Bot 重基；`work_session` 冻结；`effort` 对齐） |
| 84 | [84. 机器人列表壳：工作台不再是页面，应用本身就是机器人列表](./84-bot-list-shell.md) | 2026-09-26 | 2026-11-15 | Accepted（Bot 列表壳；补充 ADR 109 / 125 资源工作区与 `NativeResourceWindow`） |
| 85 | [85. 项目代理的宿主、输入与多入口（0.1.0 落地边界）](./85-project-agent-hosts-inputs-and-surfaces.md) | 2026-09-26 | 2026-11-15 | Accepted（后台网页走 L2 + `web_fetch`；展示交接部分被 ADR 87 2026-11-09 修订取代） |
| 86 | [ADR 86：已持久化对话的批量读取](./86-batched-persisted-conversation-reads.md) | 2026-10-02 | 2026-11-15 | Accepted（热会话读写优先走 ADR 104-progressive / 121；批量/目录读取继续复用） |
| 87 | [87. 用户回合可展开的实时过程](./87-user-turn-live-process-presentation.md) | 2026-10-05 | 2026-11-15 | Accepted（D1–D11 已接受并部分取代 ADR 85；修正 D1 对 ADR 111 引用；V01–V17 待验证） |
| 88 | [88 项目代理连续执行与结果交付方案](./88-project-agent-execution-continuity.md) | 2026-10-07 | 2026-11-15 | Accepted（§7.2 / §11.2 / §21.2 保留向后续 ADR 的部分取代与演进指针；§22 保留） |
| 89 | [ADR 89：独立 Agent 接手、双向通信与真实工作动态](./89-independent-agent-delegation-and-communication.md) | 2026-10-10 | 2026-10-10 | 页头已接受（补充 ADR 91 引用） |
| 90 | [ADR 90：本地图片能力与安装版产品截图审查](./90-local-image-capability-and-product-review.md) | 2026-10-10 | 2026-10-10 | 页头已接受 |
| 91 | [ADR 91：主 Bot 自主协调、并行调度与取消重派](./91-project-bot-autonomous-coordination.md) | 2026-10-10 | 2026-11-15 | Accepted（§§1–14 RC12 已实现；§15 为独立 PR 候选；纳入 ADR 82 `act` 持久委派来源） |
| 92 | [ADR 92：具体资源授权与执行链继承](./92-scoped-permission-inheritance.md) | 2026-10-11 | 2026-10-21 | 页头已接受（§9.3 全局真源被 ADR 101 局部取代） |
| 93 | [ADR 93：复核续跑与未完成工作的处理责任](./93-verification-continuity-and-repair-ownership.md) | 2026-10-18 | 2026-11-01 | 页头已接受（关联 ADR 117 实施边界） |
| 94 | [ADR 94：主 Bot 回复、静默等待与历史错误](./94-reply-attempts-silent-wait-and-recovery.md) | 2026-10-18 | 2026-11-01 | 页头已接受（关联 ADR 117 实施边界） |
| 95 | [ADR 95：以实际进展驱动持续执行](./95-progress-driven-execution-policy.md) | 2026-10-18 | 2026-11-06 | 页头已接受（取代 ADR 88 §8 默认工作总额与 ADR 93 硬上限） |
| 96 | [ADR 96：任务执行期间的响应性与有序持久化](./96-task-execution-responsiveness.md) | 2026-10-18 | 2026-11-15 | Accepted（§3.1 历史写读与 §3.3 窗口投影已演进对齐 ADR 104-progressive / 121） |
| 97 | [ADR 97：推理回传、续接归属与已汇报等待](./97-reasoning-replay-and-continuation-custody.md) | 2026-10-18 | 2026-11-15 | Accepted（补全 Architecture 19 相对链接，并作为窄例外登记入 ADR 57） |
| 98 | [ADR 98：大历史规模下的任务执行响应性](./98-large-history-execution-responsiveness.md) | 2026-10-18 | 2026-10-20 | 页头已接受 |
| 99 | [ADR 99：权威回复回执、模型切换恢复与历史详情](./99-authoritative-reply-receipts-and-model-recovery.md) | 2026-10-19 | 2026-11-15 | Accepted（`continuity_model_changed` 重基仅适用主 Bot；`work_session` 维持 ADR 83 冻结） |

### 100–127 近期契约

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 100 | [ADR 100：待处理事项与对话提问生命周期](./100-actionable-attention-and-question-lifecycle.md) | 2026-10-20 | 2026-10-20 | 页头已接受 |
| 101 | [ADR 101：主 Bot 授权主体与子 Agent 动态继承](./101-bot-owned-access-policy.md) | 2026-10-21 | 2026-10-21 | 页头已接受（局部取代 ADR 92 §9.3） |
| 102 | [ADR 102：任务生命周期单一投影](./102-unified-task-lifecycle-projection.md) | 2026-10-21 | 2026-11-15 | Accepted（关联引用消歧至 ADR 104-progressive） |
| 103 | [ADR 103：核验收口、进度与停滞治理](./103-verification-settlement-and-progress.md) | 2026-10-21 | — | 页头已接受 |
| 104 | [ADR 104：Bot 能力绑定与专属上下文：全局共享、独立配置及动态继承](./104-bot-capability-visibility.md) | 2026-10-22 | 2026-11-15 | Proposed（未接受；已清理 `ADR 107` 引用，Bot 自定义指令另延 `132+`） |
| 104 | [ADR 104：交互优先读取与协调日志增量存储](./104-progressive-interaction-and-coordination-storage.md) | 2026-10-22 | 2026-11-15 | Accepted（统一 §9 read-models 存储路径口径；交互优先 SQLite 与协调真源） |
| 105 | [ADR 105：协调基线的可迁移内容证明](./105-portable-coordination-baseline-integrity.md) | 2026-10-22 | 2026-11-15 | Accepted（协调基线可迁移内容证明契约；引用消歧至 ADR 104-progressive；发布验收另记） |
| 106 | [ADR 106：结构化只读 Git 与委派能力准入](./106-readonly-git-and-delegation-capability-admission.md) | 2026-10-23 | 2026-11-15 | Accepted（明确依赖指向 ADR 104-progressive，与重号 Proposed 草案 ADR 104-visibility 消歧） |
| 108 | [108. Bot 回复文件引用的有界只读预览](./108-bot-reply-document-preview.md) | 2026-10-24 | 2026-11-15 | Accepted（展示容器部分已由 ADR 109 / ADR 114 取代） |
| 108 | [ADR 108：CLI 基础壳命令](./108-cli-basic-shell-commands.md) | 2026-11-06 | 2026-11-15 | Accepted（实现未发布验收；收窄 ADR 48-cli 自动更新与 ADR 61 预发布毕业语义） |
| 109 | [ADR 109：内容引用、资源预览与产物协作契约](./109-resource-reference-preview-and-artifact-collaboration.md) | 2026-10-25 | 2026-11-15 | Accepted（第一阶段 R1–R4d/R5/R5a/R6；独立窗口与 R7–R10 待后续包；部分被 ADR 114 / 125 取代） |
| 110 | [ADR 110：跟进责任收口与当前待办列表判定](./110-follow-up-responsibility-and-current-list.md) | 2026-10-28 | 2026-11-15 | Accepted（衔接 ADR 124 `indexed` 退役及 ADR 126 / 127 unknown claim 闭包边界） |
| 111 | [ADR 111：主 Bot 双向监督、可靠续接与上下文连续性](./111-project-agent-duplex-supervision-and-continuity.md) | 2026-10-28 | 2026-11-15 | Accepted（明确 ADR 104-progressive 引用消歧；未发布验收） |
| 112 | [ADR 112：运行时模块与功能加载边界](./112-runtime-module-and-loading-boundaries.md) | 2026-10-28 | 2026-11-01 | Accepted（实际沿用 schema 2，最小 reader/writer 为 5；关联 ADR 117 深模块边界） |
| 113 | [ADR 113：检查点内容寻址存储与本机数据保留](./113-checkpoint-content-addressed-storage-and-retention.md) | 2026-10-29 | 2026-11-15 | Proposed（未接受；兼容门槛迁至 `> 11`，仅 §4.6 提前落地） |
| 114 | [114. 回复引用的定位与打开](./114-reply-citation-resolution-and-open.md) | 2026-10-30 | 2026-11-15 | Accepted（消歧 ADR 108-bot 引用；取代 ADR 109 §23 裸文件名定位规则） |
| 115 | [ADR 115：智能输入建议与用户草稿边界](./115-input-prediction-and-draft-boundary.md) | 2026-10-31 | 2026-11-15 | Accepted（`input_prediction` 账本独立写入 `usage/input-prediction.jsonl` 并收口单开关契约） |
| 116 | [ADR 116：任务控制、执行停稳与资源交接](./116-session-control-and-resource-settlement.md) | 2026-11-01 | 2026-11-15 | Accepted（§6.1–§6.3 / §12 部分被 ADR 126 / 127 取代；2026-11-08 确认可见性不改释放） |
| 117 | [ADR 117：意图驱动的协调判断、持续责任与目标闭环](./117-intent-driven-coordination-and-goal-closure.md) | 2026-11-01 | 2026-11-15 | Accepted（补充 ADR 82 持久目标委派来源；§14–§15 对齐 ADR 120 / 126 / 127；未合入未发布） |
| 118 | [ADR 118：OpenUI 可交互结果复用与运行时边界](./118-openui-interactive-results-and-runtime-boundaries.md) | 2026-11-02 | 2026-11-05 | Accepted（IUI-00—04 首期范围；尚未发布验收） |
| 119 | [ADR 119：用户停止、认知续跑准入与宿主收尾](./119-user-stop-cognition-admission-and-settlement.md) | 2026-11-03 | 2026-11-15 | Proposed（未接受；§6.3 `FollowUp.handling` 与 §12 门禁 `10` 已被 ADR 120 / 124 取代） |
| 120 | [ADR 120：运行事实、统一处置与资源等待闭环](./120-runtime-facts-disposition-and-resource-wait.md) | 2026-11-03 | 2026-11-08 | Accepted（统一运行事实处置；退役索引不对用户开放，不改停止确认） |
| 121 | [ADR 121：Desktop 会话窗口契约](./121-desktop-session-windowing-contract.md) | 2026-11-05 | 2026-11-15 | Accepted（`BotSqliteAdapter` 消费 ADR 104-progressive 读模型，`store.appendMessage` 为 JSONL 真源） |
| 122 | [ADR 122：TUI 机器人列表与输入条呈现](./122-tui-bot-list-and-composer-chrome.md) | 2026-11-06 | 2026-11-06 | Accepted（实现未发布验收） |
| 123 | [ADR 123：主 Bot 会话的无感上下文整理（情节压缩）](./123-main-bot-unnoticed-memory.md) | 2026-11-06 | 2026-11-15 | Proposed（未接受；已更名「无感上下文整理（情节压缩）」，复用 ADR 104-progressive SQLite/FTS） |
| 124 | [ADR 124：遗留停止义务的受控核实与跟进退役](./124-legacy-stop-obligation-controlled-resolution.md) | 2026-11-07 | 2026-11-15 | Accepted（2026-11-08 索引不对用户开放；PR 297 未合；部分被 ADR 126 / 127 取代） |
| 125 | [125. 资源窗口目录标签](./125-resource-window-directory-tabs.md) | 2026-11-09 | 2026-11-15 | Accepted（目录为一等资源标签；含决策五；补全对 ADR 109 部分取代与 ADR 118 兼容） |
| 126 | [ADR 126：执行资源 claim 的受控闭包、unknown 保留与隔离逃生](./126-execution-resource-claim-closure-and-unknown-retention.md) | 2026-11-09 | 2026-11-15 | Accepted（2026-11-15 与 ADR 127 一并转正，部分取代 ADR 116 / 124；尚未实现与发布验收） |
| 127 | [ADR 127：未知执行结果的对账协议、策略化自主收口与资源范围收敛](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) | 2026-11-09 | 2026-11-15 | Accepted（仅保留 `ask` / `bot_verified` 两档，`auto` 取消；部分取代 ADR 116 / 124；未实现） |

## 维护

2026-11-06 起，修改和新增功能先过本页，再写代码。细则见 [change-intake.md](../../playbook/change-intake.md)。

新增一篇 ADR 时，使用还没有被占用的编号（当前主线从 `132+` 顺延，兼顾在途远端分支 `128–131`），并在同一天给本页目录加一行。修订一篇 ADR 时，改那篇的「最后更新」，写明新增、删减、修复或优化了什么，以及哪一条款被替代，同时改本页对应行。禁止复用已有编号或回填历史缺号。不要因为本页写了「页头已接受 / Accepted」，就把它说成发布验收已经通过。

2026-11-06 本轮落实既有 ADR 95 / 96 / 120 的输入排序、有序持久化及统一恢复事实；各原文新增日期补充，未新增编号，既有权限、Evidence、存储所有权边界保持。实施与逐项验收见 [persisted-turn-recovery.md](../../playbook/v0.1.0/persisted-turn-recovery.md)。

2026-11-06 实施前收紧：ADR110/120 以 A 级明确既有 blockedReason 的本地存储机器故障投影与安全失败叶子准备，不新增存储格式；ADR95 限定查询工件完整/截断材料的进度认定。

2026-11-07 新增 ADR 124。同日 20:03（Asia/Shanghai）用户明确「那就落实124」，状态改为已接受并授权实施。它只在有效 indexed 处置下收窄 ADR 110 的当前列表规则，不改变 ADR 116 的释放条件，不接受 ADR 119 的其余条款，也不把核实写成 ADR 120 的停止确认。

2026-11-08 修订 ADR 124 的用户可见性。用户在 Peer-Agent PR 297 手测通过后确认「要」：待核实不对用户开放。确认后仍写 `disposition=indexed` / `obligation_indexed`，索引留给诊断、支持和以后核对。Desktop、TUI 和工作面板不展示「待核实」分区、列表、徽章或注意提示。证据、停稳回执、占用、`user_panel` 授权和主 Bot 工具边界不变。

2026-11-09 新增 ADR 125（资源窗口目录标签），并修订 ADR 47 决策一第 4 条在资源窗口标签条范围内的适用；经典 Workbench 一级能力栏语义不变。新增 ADR 126 与 ADR 127 提案，解决长时阻塞的 unknown 永久锁问题。

2026-11-15 执行全量跨 ADR 一致性对齐（合入 `origin/main` `7600b00` 后基于 `923fb71` 推进，共修订 87 篇 ADR 并全量重建本图谱）：
1. **A2 正式接受 ADR 126 + ADR 127**：双篇一并转为 `Accepted` 并显式标出对 ADR 116 / 124 的部分取代范围；ADR 127 仅保留 `ask` / `bot_verified` 两档（`auto` 取消），退役后 `indexed` 的过期 `ask` 声明经 Settings / 诊断与受阻提示出口而不重开「待核实」主列表。
2. **A3 模型切换与选项收敛**：明确 ADR 30（同模型重试）→ ADR 83（档位边界切换、`work_session` 冻结）→ ADR 99（仅主 Bot 会话重基）三层边界；统一 `effort` 全词表与渠道裁剪（37 / 48-provider）、`oauth_chatgpt` 独占（28）及 Architecture 19 Phase 4.5 推理回放降级。
3. **A4 网页工具双层隔离与资源窗口收敛**：明确 0.1.0 `work_session` 剥离 L1 `browser_*` 并专走 L2 Playwright（ADR 71）+ `web_fetch`（ADR 38），L1 保留于经典会话 / 独立浏览窗 / 用户资源窗口标签；确认 ADR 109 第一阶段（R1–R4d/R5/R5a/R6）Accepted 与 R7–R10 / R5w1-w2 待后续包，ADR 125 补全对 ADR 109 部分取代与 ADR 118 兼容。
4. **A5 凭据与账本边界**：严格坚持 ADR 0001 fail-closed Vault，废止 ADR 32 `file-fallback`；将 ADR 115 `input_prediction` 隔离到独立 `usage/input-prediction.jsonl` 账本。
5. **A6 Proposed 严控与重号 / 门禁清理**：维持 `77 / 104-visibility / 113 / 119 / 123` 五篇 `Proposed` 不转正；清理 `ADR 107` 无效引用，将 `113 / 123 / 126` 特性门槛重编至 `> 11`；重号 `48 / 59 / 104 / 108` 全文消歧并登记在途远端分支 `128–131` 及待重编至 `132+` 规则。
