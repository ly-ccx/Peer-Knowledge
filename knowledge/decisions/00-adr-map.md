# ADR 文档图谱

2026-11-16：ADR0001/131同日A补强：模型OAuth须前置CAS加密刷新意图，唯一刷新者才发远端请求；未知结果保全并阻止旧refresh自动重放。完成仅提交自己的意图代；旧预读token宿主仍须迁移并通过drain/升级兼容闸，不宣称新增字段解决全版本并发。

2026-11-16：ADR28/`48-provider-model-options.md`原生移植前A校正：订阅采用当前生产内置权威模型目录（替代旧gpt-5前缀/远程fallback文字），选择值沿当前Protocol标量类型，有限select投影预算；订阅Responses不发送max_output_tokens，off/default采用原有CLI语义。普通API-key与权限边界不变，实现/真实模型验收另记。

2026-11-16：ADR0001/131实施前A修订：原生模型OAuth可协商Helper v1快照/条件写入，原Vault nonce作为opaque记录revision，迟到刷新不能覆盖轮换或复活删除。旧四action/密文格式/权限不变，缺feature在远端刷新前拒绝；模型配置写入与提示投影仍须单独验收，不冒充P4完成。

2026-11-16：新增 [ADR132 MCP Vault 与原生 OAuth](132-mcp-vault-and-native-oauth.md)，先登记 MCP Helper 命名空间、v2 元数据与不可变 slot 提交；取代 ADR32 的新写入 safeStorage / plaintext fallback。实现及验收另记。

2026-11-16：ADR131补记MCP Streamable HTTP的有界控制回复和双向请求id区分；属ADR31已有双向协议的B级补齐，不新增能力或授权路径。

2026-11-15：ADR131 增补 NR-04 原生 MCP dispatch 与停稳观测，实施前登记可选 nativeMcp handle 身份、初始化后实时复核和 unfenced external 对账。授权、可见性、Evidence 与既有人工收口政策不变；实现/验收另记。

创建时间：2026-11-06
最后更新：2026-11-09（登记 ADR87 D1–D11 修订经用户接受：过程叙述与正式交付分离，A 级；实施未完成，V01–V17 待验证，结果回填 ADR87 D10。85 对应展示交接条款同日被替代。同日新增 ADR 126 提案：执行资源 claim 的受控闭包、unknown 保留与隔离逃生；ADR 124 仍为已接受，ADR 126 只修订其永久占用边界，状态为未接受、未实现。同日新增 ADR 127 提案：unknown 对账、策略化自主收口与资源范围收敛；ADR 126 的闭包机制不变）

2026-11-09（晚）新增 ADR 125：资源窗口目录标签（方向经用户确认）；ADR 47 决策一第 4 条在资源窗口标签条范围内被替代。

> 这是 `knowledge/decisions/` 的索引，不是一条新的架构决定。
> 基线是知识库 `origin/main` 的 `ec96b057`（2026-11-06 核对，已包含 #122）。
> 编号 108 有两篇：`108-bot-reply-document-preview.md` 与 `108-cli-basic-shell-commands.md`（Accepted 2026-11-06，实现未发布验收）。引用必须带文件名。

本页只记录文件里写明的状态、日期和替代关系。页头写了接受，只说明这篇决定曾被接受，不说明对应实现已经发布验收。

## 知识库分层

ADR 是知识库五层中的决策层。产品方向和架构治理各自保留权威；2026-10-23 起，体验冲突以规范层为准。同一篇 ADR 里，后写的「后续」只改它点名的条款。

| 层 | 位置 | 回答的问题 |
|---|---|---|
| 架构 | `knowledge/architecture/` | 系统怎么分，哪条链不能旁路。治理基线是 `20-architecture-governance.md` |
| 决策 | `knowledge/decisions/` | 某一次边界怎么定。A 级改动先改这里，再改代码 |
| 规范 | `knowledge/specifications/` | 体验、动效和交互怎么做 |
| 产品 | `design/product/`、`design/visual/` | 路线和版本计划。方向以 `design/product/peer-product-alignment.md` 为准 |
| 执行与现场 | `playbook/`、`knowledge/experience/` | 怎么落地、怎么回归、出过什么问题 |

决策目录内部不再按主题分文件夹。编号大致按写入时间排列。读某一条时，先看文件名，再看页头状态，再看文末「后续」。

## 编号

2026-11-07 按 `origin/main` `3402e83` 重数：本图谱之外有 **110** 个决策文件、**105** 个编号。此前本段写的 109 个文件少计 1，编号数仍是 105。缺的编号是 `2`–`14`、`19`、`20`、`23`、`107`。`0001` 不占 `1`。`108-cli-basic-shell-commands.md` 复用编号 108，文件数比合并前多 1，编号数不变。ADR 122 用 121 之后的下一个空号，不回填 107，也不复用 108。ADR 124 用 123 之后的下一个空号，同样不回填、不复用。收入 ADR 124 之后，决策文件为 **111**，编号为 **106**。

2026-11-09 按 `origin/main` 重数：图谱之外为 **114** 个决策文件、**110** 个编号（含 48/59/104/108 四组同号双篇），已计入 ADR 126 / 127 提案。

同一个编号有两篇时，引用必须带文件名：

| 编号 | 文件 | 读取 |
|---|---|---|
| 48 | `48-cli-first-class-release.md` | 页头已接受 |
| 48 | `48-provider-model-options.md` | 页头已接受 |
| 59 | `59-appshots-capability-boundary.md` | 页头已接受 |
| 59 | `59-browser-panel-reveal-capability.md` | 页头已接受 |
| 104 | `104-bot-capability-visibility.md` | 未接受 |
| 104 | `104-progressive-interaction-and-coordination-storage.md` | 页头已接受 |
| 108 | `108-bot-reply-document-preview.md` | 页头已接受 |
| 108 | `108-cli-basic-shell-commands.md` | 已接受，实现未发布验收 |

## 已写明的替代和作废

只有正文自己写了替代或作废，才记在这里。没有出现的文件，不因为日期早就被当成过时。

| 文件 | 日期 | 写明的变化 |
|---|---|---|
| `52-unified-next-request-context-accounting.md` | 2026-07-25 | 页头标明部分被 ADR 56 取代。观察用量以 `56-provider-observed-context-accounting.md` 为准 |
| `41-rename-goal-mode-to-plan-mode.md` | 2026-07-03 | wire 值从 `goal` 迁到 `plan` 仍然有效。原结论「Runner 只属于 goal、plan 只是审批门」被 B2-b 推翻：批准后两边共用同一个 Runner |
| `16-skill-call-lifecycle.md` | 页头未标日期 | 本地能力链仍有效。原文中的「宙斯客户端 / Cloud CEO Gateway」已作废，不再是产品主语 |
| `112-runtime-module-and-loading-boundaries.md` | 2026-11-01 | 早期 manifest 3 草案已被替代。文中写明实际沿用 schema 2，新记录的最小 reader/writer 是 5 |

## 不能整篇当作现行契约

下面这些文件还在目录里。草案和未接受的，整篇都还不是生效契约。写了「部分被替代」或「部分作废」的，只有被点名的条款失效，其余句子仍然有效。

`105-portable-coordination-baseline-integrity.md` 没有「状态」行。它的第二行写的是「实施前决策，发布验收另记」，并写明用户已授权修复日志恢复。

| 文件 | 页头 |
|---|---|
| `15-plugin-skill-mcp-system.md` | 设计草案 |
| `16-skill-call-lifecycle.md` | 本地能力链仍有效。原文写的「宙斯客户端 / Cloud CEO Gateway」已作废，不再是产品主语 |
| `17-local-context-compaction.md` | 设计草案 |
| `18-claude-code-style-file-edit-plan.md` | 计划草案 |
| `38-web-search-fetch-provider.md` | Proposed on 2026-06-20（设计草案，尚未动代码） |
| `41-rename-goal-mode-to-plan-mode.md` | 部分修订（Superseded in part） — 方案 A（wire 值 `'goal'`→`'plan'`）与 wire 值迁移三步已落地；但本 ADR 核心结论之一「Runner 归… |
| `52-unified-next-request-context-accounting.md` | Superseded in part by ADR 56 |
| `74-deployment-surfaces-and-local-storage.md` | Proposed（产品方向已与用户对齐；实现未开工。本文不是已落地 Accepted 实现。） |
| `76-peer-acp-agent.md` | 实施边界已确定，尚未完成实现或验收 |
| `77-image-generation-capability.md` | Proposed（待架构评审；不是已接受或已实现能力） |
| `104-bot-capability-visibility.md` | Proposed（用户已确认扩展设计方向及默认全开的兼容规则，并要求完整重写；本文待逐项评审，实现与验收另记） |
| `113-checkpoint-content-addressed-storage-and-retention.md` | Proposed（用户要求先写决策、审阅后再实现；2026-10-29 用户已对 §6 的四个问题作出决定，全文待用户审阅后转为 Accepted 再实施）。§4.6 恢复入口由用户 202… |
| `119-user-stop-cognition-admission-and-settlement.md` | Proposed（用户要求先写完整 ADR；尚未批准实施，未改变运行行为）。ADR 124 已接受，只收窄其中「不增加工具通道」一句，不接受本篇 |

## 修订记录

只列出页头「最后更新」晚于创建日，或括号里写了修订说明的文件。没有统一的增删改 changelog。括号里的话是原文摘要；没写原因的，只记日期变过。

| 文件 | 创建 | 最后更新 | 页头注明 |
|---|---|---|---|
| `17-local-context-compaction.md` | 2026-06-08 | 2026-07-24 | 日期有更新，括号未写原因 |
| `25-runtime-usage-ledger.md` | 2026-06-25 | 2026-07-26 | 日期有更新，括号未写原因 |
| `30-provider-recovery-broker.md` | 2026-06-15 | 2026-07-30 | 日期有更新，括号未写原因 |
| `41-rename-goal-mode-to-plan-mode.md` | 2026-06-30 | 2026-07-03 | 日期有更新，括号未写原因 |
| `42-context-display-vs-trigger-accounting.md` | 2026-06-30 | 2026-07-01 | 日期有更新，括号未写原因 |
| `46-conversation-bound-browser-tabs.md` | 2026-07-15 | 2026-09-02 | 日期有更新，括号未写原因 |
| `48-cli-first-class-release.md` | 2026-07-20 | 2026-11-06 | ADR 108 收窄「CLI 自动更新可缓做」，只保留无人值守安装 |
| `50-cli-system-proxy-fallback.md` | 2026-07-22 | 2026-07-22 | 代码已落地：`apps/tui` 新增 macOS 系统代理读取 + env 回退，bun test … |
| `51-unified-desktop-cli-file-tools.md` | 2026-07-22 | 2026-07-23 | 日期有更新，括号未写原因 |
| `52-unified-next-request-context-accounting.md` | 2026-07-23 | 2026-07-25 | 日期有更新，括号未写原因 |
| `56-provider-observed-context-accounting.md` | 2026-07-25 | 2026-07-26 | 日期有更新，括号未写原因 |
| `59-browser-panel-reveal-capability.md` | 2026-08-03 | 2026-08-15 | 日期有更新，括号未写原因 |
| `65-cli-headless-exec.md` | 2026-08-18 | 2026-08-18 | `exec` 默认不再设 `--max-turns` 上限 |
| `67-task-shell-workbench-radar.md` | 2026-08-22 | 2026-09-24 | 日期有更新，括号未写原因 |
| `72-l1-default-web-entry.md` | 2026-09-02 | 2026-09-02 | 第一刀系统提示落地 |
| `80-project-agent-delegation-model.md` | 2026-09-24 | 2026-10-10 | ADR 91 补充自主协调、目标修订与取消重派 |
| `81-project-agent-memory-system.md` | 2026-09-24 | 2026-09-26 | P0-2 评审通过 |
| `82-project-objectives-and-watches.md` | 2026-09-24 | 2026-10-01 | 日期有更新，括号未写原因 |
| `83-model-routing-by-role.md` | 2026-09-24 | 2026-10-24 | 补齐档位参数、角色继承覆盖与请求通道 |
| `84-bot-list-shell.md` | 2026-09-26 | 2026-09-30 | 状态驱动的机器人角色 |
| `85-project-agent-hosts-inputs-and-surfaces.md` | 2026-09-26 | 2026-11-09 | ADR87 修订接受：公开 delta 归过程、正文由 canonical 回复承接、新契约禁纯文本 fallback（仅新契约范围；旧记录与既有 fallback 语义只读保留） |
| `87-user-turn-live-process-presentation.md` | 2026-10-05 | 2026-11-09 | D1–D11 过程叙述与正式交付分离修订经用户接受，A 级；实施未完成，V01–V17 待验证 |
| `88-project-agent-execution-continuity.md` | 2026-10-07 | 2026-11-01 | 关联 ADR 117 实施边界；§22 中断核验契约保留 |
| `89-independent-agent-delegation-and-communication.md` | 2026-10-10 | 2026-10-10 | 补充 ADR 91 自主协调设计引用 |
| `91-project-bot-autonomous-coordination.md` | 2026-10-10 | 2026-11-05 | 第 15 节身份解析、派发责任与独立 PR 候选 |
| `92-scoped-permission-inheritance.md` | 2026-10-11 | 2026-10-21 | 日期有更新，括号未写原因 |
| `93-verification-continuity-and-repair-ownership.md` | 2026-10-18 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `94-reply-attempts-silent-wait-and-recovery.md` | 2026-10-18 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `95-progress-driven-execution-policy.md` | 2026-10-18 | 2026-11-06 | 稳定输入排序与查询工件进度 |
| `98-large-history-execution-responsiveness.md` | 2026-10-18 | 2026-10-20 | 日期有更新，括号未写原因 |
| `102-unified-task-lifecycle-projection.md` | 2026-10-21 | 2026-10-22 | 日期有更新，括号未写原因 |
| `104-bot-capability-visibility.md` | 2026-10-22 | 2026-10-25 | 日期有更新，括号未写原因 |
| `104-progressive-interaction-and-coordination-storage.md` | 2026-10-22 | 2026-10-28 | 历史分叉、安全恢复与旧 writer 屏障补充 |
| `106-readonly-git-and-delegation-capability-admission.md` | 2026-10-23 | 2026-10-24 | 日期有更新，括号未写原因 |
| `108-bot-reply-document-preview.md` | 2026-10-24 | 2026-10-25 | 日期有更新，括号未写原因 |
| `109-resource-reference-preview-and-artifact-collaboration.md` | 2026-10-25 | 2026-10-27 | 补充 §35：独立只读窗口的阅读连续性 |
| `110-follow-up-responsibility-and-current-list.md` | 2026-10-28 | 2026-11-08 | ADR 124 的 indexed 处置离开当前列表，且不进入用户可见的「待核实」 |
| `111-project-agent-duplex-supervision-and-continuity.md` | 2026-10-28 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `112-runtime-module-and-loading-boundaries.md` | 2026-10-28 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `115-input-prediction-and-draft-boundary.md` | 2026-10-31 | 2026-11-01 | 日期有更新，括号未写原因 |
| `116-session-control-and-resource-settlement.md` | 2026-11-01 | 2026-11-08 | ADR 124 已接受，释放仍只认停稳回执；可见性修订不改变释放条件 |
| `117-intent-driven-coordination-and-goal-closure.md` | 2026-11-01 | 2026-11-03 | 日期有更新，括号未写原因 |
| `118-openui-interactive-results-and-runtime-boundaries.md` | 2026-11-02 | 2026-11-05 | 日期有更新，括号未写原因 |
| `119-user-stop-cognition-admission-and-settlement.md` | 2026-11-03 | 2026-11-07 | 本篇仍未接受。ADR 124 已接受，只收窄三件义务工具，不接受本篇其余条款 |
| `120-runtime-facts-disposition-and-resource-wait.md` | 2026-11-03 | 2026-11-08 | ADR 124 已接受；核实不是停止确认。2026-11-08 起退役索引不对用户开放 |
| `123-main-bot-unnoticed-memory.md` | 2026-11-06 | 2026-11-06 | 替代草案估算触发、全文回流及裁尾回退；补齐有限准入、保真、回读、撤销、并发与恢复 |
| `124-legacy-stop-obligation-controlled-resolution.md` | 2026-11-07 | 2026-11-08 | 2026-11-07 20:03 Asia/Shanghai 已接受并授权实施。2026-11-08 修订用户可见性：索引只留内部审计，日常界面不展示「待核实」 |
| `125-resource-window-directory-tabs.md` | 2026-11-09 | 2026-11-09 | 新增：资源窗口目录为一等资源标签；47 的被替代条款同日登记 |

同一天被 ADR 117 的实施边界带过一笔的有：`88`、`93`、`94`、`95`、`110`、`111`、`112`，当时的最后更新都是 2026-11-01。ADR 110 在 2026-11-07 追加了 ADR 124 的关系说明；同日 20:03 起该说明改为已接受的 indexed 展示修订，117 那一笔仍在正文里。2026-11-08 再写明这条 indexed 处置不进入用户可见的「待核实」。ADR 117 自己的最后更新是 2026-11-03，记的是四包源码自测完成。ADR 118 在 2026-11-05 把交互结果纳入 RC36。ADR 91 在 2026-11-05 增加第 15 节身份解析。`48-cli-first-class-release.md` 在 2026-11-06 把 CLI 自动更新收窄为只保留无人值守安装，显式 `peer update` 改由 `108-cli-basic-shell-commands.md` 规定。

## 过时引用

| 位置 | 仍写着 | 被指文件现在的页头 |
|---|---|---|
| `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` | ADR 65 是 Proposed | `65-cli-headless-exec.md` 于 2026-08-18 写明 Accepted，且 P0 已落地 |
| `AGENTS.md` 对阶段 F 的一句话 | 项目代理壳 Proposed，见 ADR 80 | `design/product/peer-transformation-charter.md` 在 2026-10-23 已把阶段 F 核对为已落地、进入 RC 收敛。ADR 80 页头仍留着「实现未开工」，要连文末后续一起读 |

## 目录

「读取」一列只压缩页头，方便扫。细节以文件为准。

### 0001 凭据

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 0001 | [ADR 0001：跨平台凭证 Vault 与统一 Helper](./0001-cross-platform-credential-vault.md) | 2026-07-15 | 2026-07-15 | 页头已接受 |

### 15–18 早期能力草案

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 15 | [Plugin / Skill / MCP 能力体系设计](./15-plugin-skill-mcp-system.md) | 2026-05-20 | — | 草案 |
| 16 | [Peer Agent Runtime 调用生命周期](./16-skill-call-lifecycle.md) | — | — | 部分作废 |
| 17 | [Local Context Compaction 机制设计](./17-local-context-compaction.md) | 2026-06-08 | 2026-07-24 | 草案 |
| 18 | [Claude Code 风格文件编辑机制计划](./18-claude-code-style-file-edit-plan.md) | 2026-06-09 | — | 草案 |

### 21–79 宿主、工具、浏览器与发布

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 21 | [ADR 21 — 跨重启的任务续传（Pending Task Resume，会话锚…](./21-pending-task-resume.md) | — | — | 页头已接受 |
| 22 | [ADR 22 — HMR/重载后的流式重连(Stream Reattach on …](./22-stream-reattach-on-reload.md) | — | — | 页头已接受 |
| 24 | [Provider Cache And Empty Response Guard](./24-provider-cache-and-empty-response-guard.md) | — | — | 页头已接受 |
| 25 | [Runtime Usage Ledger](./25-runtime-usage-ledger.md) | 2026-06-25 | 2026-07-26 | 页头已接受 |
| 26 | [ADR 26 — Agent Loop Termination Semantics](./26-agent-loop-termination.md) | — | — | 页头已接受 |
| 27 | [ADR 27 — 工作区切换与跨工作区运行可见性(Workspace Switch…](./27-workspace-switch-and-cross-workspace-running.md) | — | — | 页头已接受 |
| 28 | [28. OpenAI Subscription OAuth (ChatGPT Lo…](./28-openai-subscription-oauth.md) | — | — | 页头已接受 |
| 29 | [29. 工具调用参数流式进度（Tool Arg Progress Streamin…](./29-tool-arg-progress-streaming.md) | — | — | 页头已接受 |
| 30 | [30. Provider Recovery Broker](./30-provider-recovery-broker.md) | 2026-06-15 | 2026-07-30 | 页头已接受 |
| 31 | [31. MCP 连接管理与设置入口](./31-mcp-connection-management.md) | — | — | 页头已接受 |
| 32 | [ADR 32: MCP Authentication and Credential…](./32-mcp-authentication.md) | — | — | 页头已接受 |
| 33 | [Per-Message Turn Duration Persistence](./33-per-message-turn-duration.md) | — | — | 页头已接受 |
| 34 | [Conversation Delete Cascades to Goal Plans](./34-conversation-delete-goal-plan-cascade.md) | — | — | 页头已接受 |
| 35 | [Mode-Scoped Tool Projection](./35-mode-scoped-tool-projection.md) | — | — | 页头已接受 |
| 36 | [36. MCP 工具卡标题透传（MCP Tool Card Title Passt…](./36-mcp-tool-card-title-passthrough.md) | — | — | 页头已接受 |
| 37 | [37. Provider Channel 与 Wire 协议分离](./37-provider-channel-and-wire-protocol-separation.md) | — | — | 页头已接受 |
| 38 | [38. Web Search / Fetch Provider（联网搜索与读链接能…](./38-web-search-fetch-provider.md) | — | — | 草案 |
| 39 | [39. 应用更新下载交互改造（非模态后台下载）](./39-updater-download-ux.md) | 2026-06-25 | 2026-06-25 | 页头已接受 |
| 40 | [40. 内嵌浏览器 + Agent 操控（webview 载体 + webCont…](./40-embedded-browser-and-agent-control.md) | 2026-06-25 | 2026-06-25 | 页头已接受 |
| 41 | [ADR 41：将现有「Goal 模式」正名为「Plan 模式」](./41-rename-goal-mode-to-plan-mode.md) | 2026-06-30 | 2026-07-03 | 部分被替代 |
| 42 | [ADR 42：上下文计数口径分离（显示口径 vs 压缩触发口径）](./42-context-display-vs-trigger-accounting.md) | 2026-06-30 | 2026-07-01 | 页头已接受 |
| 43 | [会话运行时状态按 conversationId 分桶（消灭跨会话串内容）](./43-conversation-runtime-state-bucketing.md) | 2026-07-01 | — | 页头已接受 |
| 44 | [44. 全局动效体系：自建语义基元 + 激进收敛（不引第三方库）](./44-motion-system-consolidation.md) | 2026-07-01 | 2026-07-01 | 页头已接受 |
| 45 | [45. MCP OAuth 配置交互简化：探测即自动配置 + 回调地址只读 + 授…](./45-mcp-oauth-config-ux-simplification.md) | 2026-07-01 | 2026-07-01 | 页头已接受 |
| 46 | [46. 会话绑定的 Workbench 与多标签浏览器](./46-conversation-bound-browser-tabs.md) | 2026-07-15 | 2026-09-02 | 页头已接受 |
| 47 | [47. Workbench 多资源标签模型](./47-workbench-multi-resource-tabs.md) | 2026-07-15 | 2026-11-09 | 页头已接受；决策一第 4 条在资源窗口范围内被 ADR 125 替代 |
| 48 | [CLI First-Class Release（CLI 与 Desktop 同仓一…](./48-cli-first-class-release.md) | 2026-07-20 | 2026-11-06 | 页头已接受 |
| 48 | [48. 渠道无关的模型选项与渠道投影](./48-provider-model-options.md) | 2026-07-17 | 2026-07-17 | 页头已接受 |
| 49 | [49. 取消路径硬沙箱（允许跨工作区读写）](./49-cancel-path-hard-sandbox.md) | 2026-07-21 | 2026-07-21 | 页头已接受 |
| 50 | [50. CLI 系统代理回退（macOS）](./50-cli-system-proxy-fallback.md) | 2026-07-22 | 2026-07-22 | 页头已接受 |
| 51 | [Unified Desktop and CLI File Tools（桌面端与 C…](./51-unified-desktop-cli-file-tools.md) | 2026-07-22 | 2026-07-23 | 页头已接受 |
| 52 | [ADR 52：统一下一次请求上下文统计](./52-unified-next-request-context-accounting.md) | 2026-07-23 | 2026-07-25 | 部分被替代 |
| 53 | [Tool Call Duration Accounting](./53-tool-call-duration-accounting.md) | 2026-07-23 | 2026-07-23 | 页头已接受 |
| 54 | [ADR 54：开放 Runtime 公开包与发布策略](./54-open-runtime-public-packages-and-release-policy.md) | 2026-07-24 | 2026-07-24 | 页头已接受 |
| 55 | [ADR 55：Desktop 与 TUI 统一 System Context As…](./55-shared-system-context-assembler.md) | 2026-07-25 | 2026-07-25 | 页头已接受 |
| 56 | [ADR 56：Provider 实测优先的精确上下文记账](./56-provider-observed-context-accounting.md) | 2026-07-25 | 2026-07-26 | 页头已接受 |
| 57 | [ADR 57：Desktop 与 TUI 统一 Canonical Convers…](./57-canonical-conversation-history-projector.md) | 2026-07-25 | 2026-07-25 | 页头已接受 |
| 58 | [本地 Skill 范围与工作空间挂载](./58-local-skill-scope-and-workspace-mounting.md) | 2026-07-27 | 2026-07-27 | 页头已接受 |
| 59 | [Appshots 能力边界与 Evidence 链](./59-appshots-capability-boundary.md) | 2026-07-30 | — | 页头已接受 |
| 59 | [59. Browser 面板主动打开与可见工作现场闭环](./59-browser-panel-reveal-capability.md) | 2026-08-03 | 2026-08-15 | 页头已接受 |
| 60 | [Quick Chat 独立 Popover 窗](./60-quick-chat-independent-popover-window.md) | 2026-07-30 | — | 页头已接受 |
| 61 | [61. beta→stable 通道自动毕业决策](./61-beta-to-stable-channel-graduation.md) | 2026-08-03 | 2026-08-03 | 页头已接受 |
| 62 | [62. Automation Runtime 与持久化边界](./62-automation-runtime-boundary.md) | 2026-08-04 | — | 页头已接受 |
| 63 | [63. 用户产物与 Evidence 边界](./63-user-artifact-evidence-boundary.md) | 2026-08-16 | — | 页头已接受 |
| 64 | [64. Workbench 源码预览先复用 highlight.js，不上 Mon…](./64-workbench-source-highlight-without-monaco.md) | 2026-08-17 | 2026-08-17 | 页头已接受 |
| 65 | [65. CLI 无头发起（`peer exec`）](./65-cli-headless-exec.md) | 2026-08-18 | 2026-08-18 | 页头已接受 |
| 66 | [66. 浏览器工具的后台降级执行（Headless Fallback）](./66-browser-headless-fallback-execution.md) | 2026-08-21 | 2026-08-21 | 页头已接受 |
| 67 | [67. 任务壳 + 工作台雷达（原型 A）](./67-task-shell-workbench-radar.md) | 2026-08-22 | 2026-09-24 | 页头已接受 |
| 68 | [68. 交付模式契约：direct 与隔离合回统一语义](./68-goal-delivery-mode-contract.md) | 2026-08-26 | — | 页头已接受 |
| 69 | [69. 合回分流（Triage）分类器：结构化 verdict 替代布尔判定](./69-handoff-triage-classifier.md) | 2026-08-26 | — | 页头已接受 |
| 70 | [70. L1 内嵌浏览器动作面扩展（hover / scroll / key / …](./70-l1-browser-action-surface.md) | 2026-09-01 | 2026-09-01 | 页头已接受 |
| 71 | [71. L2 受控外部浏览器（Playwright / CDP）安全模型](./71-l2-playwright-external-browser.md) | 2026-09-01 | 2026-09-01 | 页头已接受 |
| 72 | [72. 网页任务默认入口：L1 内置浏览器（`browser_*`）](./72-l1-default-web-entry.md) | 2026-09-02 | 2026-09-02 | 页头已接受 |
| 73 | [73. Goal 中断挂起与失败解耦的状态契约](./73-goal-interruption-suspension-vs-failure.md) | 2026-09-03 | — | 页头已接受 |
| 74 | [74. 部署面与本机存储策略](./74-deployment-surfaces-and-local-storage.md) | 2026-09-06 | 2026-09-06 | 未接受 |
| 75 | [75. 远程读取预检：通过不等于获得执行权](./75-remote-read-preflight.md) | 2026-09-26 | 2026-09-26 | 页头已接受 |
| 76 | [ADR 76：Peer 作为 ACP Agent](./76-peer-acp-agent.md) | 2026-09-08 | — | 未完成 |
| 77 | [77. 多服务图片生成能力与凭证、产物边界](./77-image-generation-capability.md) | 2026-09-15 | 2026-09-15 | 未接受 |
| 78 | [78. Intake 期武装 UI 交付视觉验证门](./78-intake-ui-delivery-arm.md) | 2026-09-23 | — | 页头已接受 |
| 79 | [79. 移除预配置基准分支：交付绑定跟随工作区实时 HEAD](./79-remove-preconfigured-base-branch.md) | 2026-09-23 | — | 页头已接受 |

### 80–99 0.1.0 项目代理与执行链

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 80 | [80. 项目代理委托模型：一个项目一个代理，任务由代理开出](./80-project-agent-delegation-model.md) | 2026-09-24 | 2026-10-10 | 页头已接受 |
| 81 | [81. 项目代理记忆体系：带来源的事实记录，只进事实层，自动但可撤](./81-project-agent-memory-system.md) | 2026-09-24 | 2026-09-26 | 页头已接受 |
| 82 | [82. 项目目标与定时 / 事件驱动推进](./82-project-objectives-and-watches.md) | 2026-09-24 | 2026-10-01 | 页头已接受 |
| 83 | [83. 模型分工：档位 + 角色，用户说了算，开任务时冻结](./83-model-routing-by-role.md) | 2026-09-24 | 2026-10-24 | 页头已接受 |
| 84 | [84. 机器人列表壳：工作台不再是页面，应用本身就是机器人列表](./84-bot-list-shell.md) | 2026-09-26 | 2026-09-30 | 页头已接受 |
| 85 | [85. 项目代理的宿主、输入与多入口（0.1.0 落地边界）](./85-project-agent-hosts-inputs-and-surfaces.md) | 2026-09-26 | 2026-11-09 | 页头已接受；展示交接条款被 ADR87 2026-11-09 修订替代（仅新契约范围） |
| 86 | [ADR 86：已持久化对话的批量读取](./86-batched-persisted-conversation-reads.md) | 2026-10-02 | 2026-10-02 | 页头已接受 |
| 87 | [87. 用户回合可展开的实时过程](./87-user-turn-live-process-presentation.md) | 2026-10-05 | 2026-11-09 | 页头已接受；D1–D11 修订（过程叙述与正式交付分离）2026-11-09 经用户接受，实施未完成 |
| 88 | [88 项目代理连续执行与结果交付方案](./88-project-agent-execution-continuity.md) | 2026-10-07 | 2026-11-01 | 页头已接受 |
| 89 | [ADR 89：独立 Agent 接手、双向通信与真实工作动态](./89-independent-agent-delegation-and-communication.md) | 2026-10-10 | 2026-10-10 | 页头已接受 |
| 90 | [ADR 90：本地图片能力与安装版产品截图审查](./90-local-image-capability-and-product-review.md) | 2026-10-10 | 2026-10-10 | 页头已接受 |
| 91 | [ADR 91：主 Bot 自主协调、并行调度与取消重派](./91-project-bot-autonomous-coordination.md) | 2026-10-10 | 2026-11-05 | 页头已接受 |
| 92 | [ADR 92：具体资源授权与执行链继承](./92-scoped-permission-inheritance.md) | 2026-10-11 | 2026-10-21 | 页头已接受 |
| 93 | [ADR 93：复核续跑与未完成工作的处理责任](./93-verification-continuity-and-repair-ownership.md) | 2026-10-18 | 2026-11-01 | 页头已接受 |
| 94 | [ADR 94：主 Bot 回复、静默等待与历史错误](./94-reply-attempts-silent-wait-and-recovery.md) | 2026-10-18 | 2026-11-01 | 页头已接受 |
| 95 | [ADR 95：以实际进展驱动持续执行](./95-progress-driven-execution-policy.md) | 2026-10-18 | 2026-11-06 | 页头已接受 |
| 96 | [ADR 96：任务执行期间的响应性与有序持久化](./96-task-execution-responsiveness.md) | 2026-10-18 | 2026-11-06 | 页头已接受 |
| 97 | [ADR 97：推理回传、续接归属与已汇报等待](./97-reasoning-replay-and-continuation-custody.md) | 2026-10-18 | 2026-10-18 | 页头已接受 |
| 98 | [ADR 98：大历史规模下的任务执行响应性](./98-large-history-execution-responsiveness.md) | 2026-10-18 | 2026-10-20 | 页头已接受 |
| 99 | [ADR 99：权威回复回执、模型切换恢复与历史详情](./99-authoritative-reply-receipts-and-model-recovery.md) | 2026-10-19 | — | 页头已接受 |

### 100–125 近期契约

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 100 | [ADR 100：待处理事项与对话提问生命周期](./100-actionable-attention-and-question-lifecycle.md) | 2026-10-20 | 2026-10-20 | 页头已接受 |
| 101 | [ADR 101：主 Bot 授权主体与子 Agent 动态继承](./101-bot-owned-access-policy.md) | 2026-10-21 | 2026-10-21 | 页头已接受 |
| 102 | [ADR 102：任务生命周期单一投影](./102-unified-task-lifecycle-projection.md) | 2026-10-21 | 2026-10-22 | 页头已接受 |
| 103 | [ADR 103：核验收口、进度与停滞治理](./103-verification-settlement-and-progress.md) | 2026-10-21 | — | 页头已接受 |
| 104 | [ADR 104：Bot 能力绑定与专属上下文：全局共享、独立配置及动态继承](./104-bot-capability-visibility.md) | 2026-10-22 | 2026-10-25 | 未接受 |
| 104 | [ADR 104：交互优先读取与协调日志增量存储](./104-progressive-interaction-and-coordination-storage.md) | 2026-10-22 | 2026-10-28 | 页头已接受 |
| 105 | [ADR 105：协调基线的可迁移内容证明](./105-portable-coordination-baseline-integrity.md) | 2026-10-22 | — | 页头未写状态 |
| 106 | [ADR 106：结构化只读 Git 与委派能力准入](./106-readonly-git-and-delegation-capability-admission.md) | 2026-10-23 | 2026-10-24 | 页头已接受 |
| 108 | [108. Bot 回复文件引用的有界只读预览](./108-bot-reply-document-preview.md) | 2026-10-24 | 2026-10-25 | 页头已接受 |
| 108 | [ADR 108：CLI 基础壳命令](./108-cli-basic-shell-commands.md) | 2026-11-06 | 2026-11-06 | 已接受，实现未发布验收 |
| 109 | [ADR 109：内容引用、资源预览与产物协作契约](./109-resource-reference-preview-and-artifact-collaboration.md) | 2026-10-25 | 2026-10-27 | 页头已接受 |
| 110 | [ADR 110：跟进责任收口与当前待办列表判定](./110-follow-up-responsibility-and-current-list.md) | 2026-10-28 | 2026-11-08 | 页头已接受；ADR 124 的 indexed 处置离开当前列表，且不进入用户可见的「待核实」 |
| 111 | [ADR 111：主 Bot 双向监督、可靠续接与上下文连续性](./111-project-agent-duplex-supervision-and-continuity.md) | 2026-10-28 | 2026-11-01 | 页头已接受 |
| 112 | [ADR 112：运行时模块与功能加载边界](./112-runtime-module-and-loading-boundaries.md) | 2026-10-28 | 2026-11-01 | 页头已接受 |
| 113 | [ADR 113：检查点内容寻址存储与本机数据保留](./113-checkpoint-content-addressed-storage-and-retention.md) | 2026-10-29 | 2026-10-29 | 未接受 |
| 114 | [114. 回复引用的定位与打开](./114-reply-citation-resolution-and-open.md) | 2026-10-30 | 2026-10-30 | 页头已接受 |
| 115 | [ADR 115：智能输入建议与用户草稿边界](./115-input-prediction-and-draft-boundary.md) | 2026-10-31 | 2026-11-01 | 页头已接受 |
| 116 | [ADR 116：任务控制、执行停稳与资源交接](./116-session-control-and-resource-settlement.md) | 2026-11-01 | 2026-11-08 | 页头已接受；ADR 124 不改变释放条件；ADR 126 提案修订 unknown 的永久 hold（未接受） |
| 117 | [ADR 117：意图驱动的协调判断、持续责任与目标闭环](./117-intent-driven-coordination-and-goal-closure.md) | 2026-11-01 | 2026-11-03 | 页头已接受 |
| 118 | [ADR 118：OpenUI 可交互结果复用与运行时边界](./118-openui-interactive-results-and-runtime-boundaries.md) | 2026-11-02 | 2026-11-05 | 页头已接受 |
| 119 | [ADR 119：用户停止、认知续跑准入与宿主收尾](./119-user-stop-cognition-admission-and-settlement.md) | 2026-11-03 | 2026-11-07 | 未接受。ADR 124 已接受，只收窄三件义务工具 |
| 120 | [ADR 120：运行事实、统一处置与资源等待闭环](./120-runtime-facts-disposition-and-resource-wait.md) | 2026-11-03 | 2026-11-08 | 页头已接受；ADR 124 不把核实当成停止确认。退役索引不对用户开放 |
| 121 | [ADR 121：Desktop 会话窗口契约](./121-desktop-session-windowing-contract.md) | 2026-11-05 | 2026-11-05 | 页头已接受 |
| 122 | [ADR 122：TUI 机器人列表与输入条呈现](./122-tui-bot-list-and-composer-chrome.md) | 2026-11-06 | 2026-11-06 | 已接受，实现未发布验收 |
| 123 | [ADR 123：主 Bot 会话的无感记忆](./123-main-bot-unnoticed-memory.md) | 2026-11-06 | 2026-11-06 | 未接受；本轮收紧容量、准入与恢复，未授权实现 |
| 124 | [ADR 124：遗留停止义务的受控核实与跟进退役](./124-legacy-stop-obligation-controlled-resolution.md) | 2026-11-07 | 2026-11-08 | 已接受并授权实施。2026-11-08 修订：索引只留内部审计，日常界面不展示「待核实」。Peer-Agent PR 297 未合并、未发版；ADR 126 提案修订 §1.5/§6.2 的绝对不释放边界（未接受） |
| 125 | [125. 资源窗口目录标签](./125-resource-window-directory-tabs.md) | 2026-11-09 | 2026-11-09 | 已接受（方向经用户确认）；同日追加决策五：launcher 且无辅助面板时隐藏头部网页/目录/变更三入口（辅助面板一开即恢复，按下态与焦点回退契约不变）；实施回执按验证要求第 5 条 |
| 126 | [ADR 126：执行资源 claim 的受控闭包、unknown 保留与隔离逃生](./126-execution-resource-claim-closure-and-unknown-retention.md) | 2026-11-09 | 2026-11-09 | 未接受提案。逐 claim 闭包修订 ADR 116/124 的永久占用边界；前提是死亡证明或用户确认、无 live、无未结束句柄；unknown 保留且不重放。ADR 127 提案扩展其授权模型（未接受） |
| 127 | [ADR 127：未知执行结果的对账协议、策略化自主收口与资源范围收敛](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) | 2026-11-09 | 2026-11-09 | 未接受提案。把 unknown 从“人工逐次确认”扩展为源头回执、宿主对账与 `ask / bot_verified / auto` 策略；不改变证据边界，不引入 force |

## 维护

2026-11-06 起，修改和新增功能先过本页，再写代码。细则见 `playbook/change-intake.md`。

新增一篇 ADR 时，使用还没有被占用的编号，并在同一天给本页目录加一行。修订一篇 ADR 时，改那篇的「最后更新」，写明新增、删减、修复或优化了什么，以及哪一条款被替代，同时改本页对应行。不要复用已有编号。不要因为本页写了「页头已接受」，就把它说成发布验收已经通过。


2026-11-06 本轮落实既有 ADR 95 / 96 / 120 的输入排序、有序持久化及统一恢复事实；各原文新增日期补充，未新增编号，既有权限、Evidence、存储所有权边界保持。实施与逐项验收见 `playbook/v0.1.0/persisted-turn-recovery.md`。

2026-11-06 实施前收紧：ADR110/120 以 A 级明确既有 blockedReason 的本地存储机器故障投影与安全失败叶子准备，不新增存储格式；ADR95 限定查询工件完整/截断材料的进度认定。

2026-11-07 新增 ADR 124。同日 20:03（Asia/Shanghai）用户明确「那就落实124」，状态改为已接受并授权实施。它只在有效 indexed 处置下收窄 ADR 110 的当前列表规则，不改变 ADR 116 的释放条件，不接受 ADR 119 的其余条款，也不把核实写成 ADR 120 的停止确认。

2026-11-08 修订 ADR 124 的用户可见性。用户在 Peer-Agent PR 297 手测通过后确认「要」：待核实不对用户开放。确认后仍写 `disposition=indexed` / `obligation_indexed`，索引留给诊断、支持和以后核对。Desktop、TUI 和工作面板不展示「待核实」分区、列表、徽章或注意提示。证据、停稳回执、占用、`user_panel` 授权和主 Bot 工具边界不变。该代码 PR 仍未合并，这次修订尚未写入代码。

2026-11-09 新增 ADR 127 提案。它回应“unknown 永久锁 + 主 Bot 无自主收口权”的批评：源头先登记结果、宿主执行对账协议、用户按项目/Bot 委托 `ask / bot_verified / auto` 收口权，claim 按声明范围保护；模型不能伪造执行结果或证据，外部未围栏效果仍保留人工门。

2026-11-09 新增 ADR 126 提案。它来自一次真实长时间阻塞：已取消会话留下的 unknown 调用把项目目录永久锁死，两条空 unknown 的旧取消也被巡检永久跳过。提案把“登记进程已死、无活体/句柄”的历史 unknown 从目录 hold 降为 `RetainedUnknown`，并提供逐 claim、用户在宿主卡片确认的闭包，以及不释放原锁的独立 clone 逃生。它只修订 ADR 116 §6.2/§6.3 与 ADR 124 §1.5/§6.2 的永久占用边界；ADR 124 的知悉、退役、界面可见性和 `release_resource` 拒绝规则不变。状态为未接受、未实现，待用户评审后再开代码实施。

2026-11-09 新增 ADR 125（资源窗口目录标签），并修订 ADR 47 决策一第 4 条在资源窗口标签条范围内的适用；经典 Workbench 一级能力栏语义不变。实施在 Peer-Agent 代码仓进行，本页不维护执行状态。

## 原生 CLI 迁移（2026-11-14）

用户已接受原生 Rust / Ratatui 三份迁移决策并授权按 P0→P1 自测后持续实施，最终无 Bun/Node sidecar。评审稿原编号 116–118 与本页既有 ADR 冲突，改登记为 129–131；既有 116–118 不变，128 仍为另一在途设计，不在本次接受范围。

| 编号 | 文件 | 状态 |
|---|---|---|
| 129 | [原生 Rust CLI 与 Ratatui](129-native-rust-cli-and-ratatui.md) | Accepted，2026-11-14；实现 / 验收另记 |
| 130 | [有界内存与历史](130-bounded-cli-memory-and-transcript.md) | Accepted，2026-11-14；预算待实测 |
| 131 | [跨语言契约、数据与恢复](131-native-cli-contract-storage-and-recovery.md) | Accepted，2026-11-14；2026-11-15 A级补充 NR-04 用量双文件提交恢复及canonical预算观察快照，收紧ADR25恢复保证；实现 / 恢复另记 |
| 132 | [MCP Vault 与原生 OAuth](132-mcp-vault-and-native-oauth.md) | Accepted，2026-11-16；MCP Helper 命名空间、旧凭据迁移与不可变 slot 提交。实现 / 验收另记 |

2026-11-14 同日澄清 ADR 131 §1 的同号引用：`104-bot-capability-visibility.md` 仍未接受；`104-progressive-interaction-and-coordination-storage.md` 已接受的 writer fence / 恢复契约保留。未移动既有边界。

2026-11-14 NR-03：ADR 131 增补 canonical budget nativeRecorder v1 可选合同与原生停稳观测 Adapter；只证明 runner 死亡且无开放句柄，unknown/权限/Evidence/claim 收口要求不变，实施及验收另记。

2026-11-14 NR-03 复核：ADR 131 补充真实 Provider 创建结果/Evidence/dispatch 已确认后，同 owner 的 missing file claim 身份确认；保留 unknown/closure/外来身份阻断，schema 不变。

2026-11-15 ADR131/57: A-level historySelection v1, projector3 and capacity boundary binding supplement precedes implementation. Legacy markers retain suffix semantics; compatibility/recovery acceptance is tracked separately.
