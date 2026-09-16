# 任务监控栏（Task Monitor Rail）产品与信息架构设计

创建时间：2026-09-14
最后更新：2026-09-16（按用户截图纠偏：监控栏归当前会话面板，不是独立 Workbench 视图）

## 1. 文档定位

本文回答一个问题：**参照 Qoder 的任务信息区，Peer Agent 如何把任务监控能力嵌入当前会话面板，并让它与独立 Workbench 保持清晰边界。**

三份文档的分工（本文不重复它们的内容）：

| 文档 | 负责 |
| --- | --- |
| [`right-workbench-panel.md`](./right-workbench-panel.md) | Workbench 窗口级容器：开合、宽度、Tab 切换、快捷键 |
| [`goal-right-status-panel.md`](./goal-right-status-panel.md) | Goal（计划）专题：目标、进度、阻塞、验收的层级与状态反馈 |
| **本文** | **会话内任务监控栏：宿主边界、环境 / 进度 / 后台任务 / 产出分区，以及与独立 Workbench 的共存** |

核心结论：Qoder 右侧面板的价值不在视觉，而在于**把一个长任务运行期间"散落在各处的运行事实"收敛到同一处**——用户不用翻聊天记录、不用切 Tab，就能回答"后台还有没有在跑的进程""这次动了哪些文件"。

**信息归属的边界（2026-09-15 用户修正，本设计的定位性结论）**：

- **环境信息（分支/本地/提交推送）归中间的对话面板**——它是"当前会话在哪个环境里工作"的常驻语境，贴着输入框（Qoder 底部状态条：`cbu-xiaoer-node-nexus · 本地 · PeerAgent/nexus-upload-media-…`）。Peer Agent 对应物是 composer 的环境胶囊（`ChatSurface.tsx` 的 `envCapsule` / `formatComposerEnvCapsule` + 下拉），**不进右栏、不重复展示**。
- **右栏是任务监控栏**——只回答"这个任务正在/已经产生了什么"：后台任务（含内联详情）+ 产出。Qoder 右栏顶部按钮就叫"隐藏任务监控"。

Peer Agent 已经有这些事实，但它们**分散在不同 surface**：后台进程在 ChatHeader 弹层、产出在任务总览页。本设计的目标是新增一个**会话作用域的监控栏**，把这些事实按同一套分区模型投影出来，而不是再造数据源。

### 1.1 变更分级（按仓库 AGENTS.md）

B 级：新增 renderer 侧的分区 surface，复用既有 protocol 类型与 IPC，不改变 capability 暴露、权限模型、Evidence 语义、System Context 顺序或存储边界。

硬约束（不可违反）：

- 分区栏是**只读投影**。它展示事实，不产生新的事实来源；任何一项的可信来源仍是 Tool Result / Evidence / capability manifest。
- 不使用 renderer 直连 `fs` / `child_process`；所有本地事实经既有 IPC 通道取得。
- 不把 Evidence ref（`tool-result://`、`local-shell-artifact://`、`goal-plan://`）当作可点击的产出展示——这类 ref 是治理标识，不是用户产物（该规则在 `taskOverviewArtifacts.ts` 已有实现，见 §3.4）。
- 权限真值仍只来自主进程 PermissionGate；本栏最多**显示**当前访问级别，不参与判定。

## 2. Qoder 右侧面板原始拆解

来源：用户提供的 Qoder 截图（会话「图片上传功能迁移」，右侧一列）。自上而下 7 个分区。

### 2.1 分区清单与字段

| # | 分区 | 截图中的实际内容 | 字段 |
| --- | --- | --- | --- |
| 1 | 进展摘要卡 | 绿色标识 + `更新于 16:13` + 一段自然语言进展（"图片上传迁移推进中：upload() 已改走图片空间 HSF（bizcode cbuaigcpromotionpublic），multipart 入口补完，插件显式启用后请求通了…"） | `updatedAt`、`summaryText` |
| 2 | 环境信息 | `无变更` / `本地` / `PeerAgent/nexus-upload-media-pre` / `提交或推送` | `gitDirtyState`、`runLocation`（本地/远端）、`branchName`、`commitOrPushAction` |
| 3 | 后台进程 | `cd /Users/liangyin/Do… ⤵ 运行中` | `command`、`cwd`、`status` |
| 4 | 技能与 MCP | `a1` | `enabledCapabilityNames[]` |
| 5 | 产出 | （截图中为空，仅有标题） | `artifacts[]`（文件/变更/截图） |
| 6 | 网页查阅 | `cd.aone.alibaba-inc.com/unite/micro…` ×2、`pre-cbu-xiaoer-node-nexus.alibaba…` | `visitedPages[]`（favicon、域名+路径、可点击回到页面） |
| 7 | 来源 | （截图中仅标题 + `+`） | `sources[]`、`addSourceAction` |

### 2.2 交互与视觉规律（可提炼的规则）

1. **每项都是「图标 + 值」的单行结构**，左侧图标承担类型识别，右侧是值本身；不写字段名。
2. **分区之间用细分隔线分节**，分区标题是弱化的小字号文本。
3. **值本身可点击即跳转**：分支名 → 分支详情；产出 → 打开该文件/变更；网页 → 回到该页面。
4. **摘要卡固定在顶部且最先出现**，是"我现在该知道什么"的一句话答案，其余分区是它的证据明细。
5. **空分区保留标题、不渲染占位文案**（产出、来源在截图中都是空标题）。
6. **进展摘要卡有时间戳**（`更新于 16:13`），其余分区不显示时间，避免每行都带噪音。

## 3. 字段 → 数据源映射（逐项对照 Peer Agent 现状）

状态列定义：

- **已具备（位置错）**：数据源与渲染都已存在，只是在别的 surface，本设计只做迁移/复用。
- **需聚合**：数据在本地已存在，但还没有面向"会话上下文"的投影，需要新增聚合层。
- **缺失**：目前没有权威数据源，需要先补数据链路（不在 P0/P1 范围）。

### 3.1 环境信息

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 当前分支名 | `apps/desktop/renderer/src/chat/hooks/useWorkspaceGit.ts` → `WorkspaceGitState.current`；底层 IPC `git:list-branches` | 需聚合（hook 已有，未投影到栏） |
| 分支列表 / 本地与远端区分 | 同上 → `branches` / `localBranches` / `remoteBranches` | 需聚合 |
| `无变更` / 有变更 | 现有 IPC 只有 `git:diff`、`git:diff-range`，**无 git status** | 需聚合（依赖新增 status 通道） |
| `本地` / 远端 运行位置 | 会话工作区概念已存在（`goal-worktree-adapter.mjs` 的 `currentBranch(root)`、worktree 隔离） | 需聚合 |
| `提交或推送` 动作 | `file-access-application-service.mjs` → `createGitBranch` / `pushGitBranch`；IPC `git:create-branch` | 已具备（动作通道在，未在此栏暴露） |

结论：环境信息**不进任务监控栏**（2026-09-15 用户修正：它是中间对话面板的语境，贴着输入框）。上表数据源全部已有归宿——composer 环境胶囊（`ChatSurface.tsx` 的 `envCapsule`，含分支/隔离分支切换）已消费 `useWorkspaceGit`；剩余缺口（git status 的 dirty 态）留待补 `git:status` IPC 后接入胶囊，与本栏无关。历史版本曾把「分支名 + 运行位置」放进右栏 P0，已随重构移除。

### 3.2 后台进程

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 命令行 | `packages/protocol/src/index.ts:934` `ManagedShellTask.command` | 已具备（位置错） |
| 工作目录 | 同上 `ManagedShellTask.cwd` | 已具备（位置错） |
| 运行状态（运行中/已完成/失败…） | 同上 `ManagedShellTask.status`、`exitCode`、`startedAt`、`completedAt` | 已具备（位置错） |
| 状态文案映射 | `apps/desktop/renderer/src/workbench/backgroundTaskPresentation.ts`（`运行中`/`停止中`/`已完成`/`失败`/`已停止`/`超时`，含测试 `backgroundTaskPresentation.test.ts`） | 已具备（复用即可） |

现状：`BackgroundRuntimePanel.tsx` 已经是完整的运行列表（含 `background-run-row`、点击进入 `BackgroundRunDetails`），入口是 `GlobalBackgroundTasksButton.tsx` 的 **ChatHeader 弹层**。结论：**零新增数据工作**，本设计把它**合并**为监控栏的常驻分区：栏内点击任务行直接内联展开 `BackgroundRunDetails`（含两段式停止确认：本地 confirm 态 → `reconcileStopRequest` 调停 → `stops.stop`），不再跳去弹层；ChatHeader 全局入口保留（跨会话视角与监控栏的会话作用域视角并存）。

### 3.3 技能与 MCP

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 本次会话可用的能力名列表 | `apps/desktop/renderer/src/chat/components/thread/ChatHeaderCapabilities.tsx`，消费 protocol 的 `CapabilityManifest` / `SkillSummary` / `CapabilityHealth` | 已具备（位置错） |
| 分组（skill / mcp / plugin / builtin） | 同上，已按类型分组渲染 | 已具备（位置错） |
| 状态色（可用/需认证/不可用） | 同上，`StatusTone` = `available` / `needsAuth` / `disabled` / `unavailable` | 已具备（位置错） |
| 单项详情 | `capabilities/components/SkillDetailDialog.tsx`、`CapabilityDetailPanel.tsx` | 已具备（复用即可） |

结论：**零新增数据工作**，复用 `ChatHeaderCapabilities` 的数据装配与详情弹窗，只换宿主。注意：栏内只显示"本会话实际可用/已启用"的能力，与 header 的完整能力列表语义不同，需要按会话过滤。

### 3.4 产出

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 产物列表（代码变更/文件/截图） | `apps/desktop/electron/main/task-overview-aggregator.mjs` → `deriveTaskArtifacts(evidenceRefs, evidenceIndex, artifactRoots)`，自 L409 起 | 已具备（位置错） |
| 产物 kind 映射 | 同文件 `USER_ARTIFACT_PRESENTATION`(L353)：`code-change`→`code`、`file`→`file`、`image`→`image` | 已具备（复用即可） |
| 动作文案 | 同上：`code`→`查看变更`、`file`→`打开文件`、`image`→`预览截图` | 已具备（复用即可） |
| 展示上限与分组 | `apps/desktop/renderer/src/app/pages/taskOverviewArtifacts.ts`：`MAX_VISIBLE_ARTIFACTS_PER_KIND = 2`，按 kind 分组 + `summary`/`total`/`hiddenTotal` | 已具备（复用即可） |
| 过滤规则 | 同上：`BLOCKED_REF_PREFIXES` 屏蔽 `local-shell-artifact://`、`tool-result://`、`goal-plan://`；`ALLOWED_KINDS` 仅 `code/file/image` | 已具备（必须复用，不得放宽） |

结论：产出分区的**全部逻辑已存在**，P0 只需把 `taskOverviewArtifacts.ts` 的投影接到会话作用域（当前它挂在任务总览页的 step 上）。

**实施陷阱（必须知道）**：不能用 `item.taskId === conversationId` 去挑"本会话那一条"。`TaskOverviewItem.taskId` 是**稳定投影身份**，取值可能是 conversationId、planId 或 automationId+runId；而聚合器对「有活跃计划的会话」只推 goal_plan 投影，并用 `projectedPlanConversationIds` 跳过同会话的 conversation 投影——**恰恰在长任务会话里 `taskId` 就是 planId**。正确做法是取并集：`taskId === conversationId` 或 `item.conversationId === conversationId`（后者是 goal_plan / automation 投影的深链字段）。另有两点：产物挂在 `planSteps[].artifacts` 而非 item 上；多条命中时应优先有产物的一条。实现见 `taskMonitorRail.ts` 的 `selectConversationTaskOverviewItem()`。

### 3.5 网页查阅

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 页面 URL | `apps/desktop/renderer/src/workbench/browserSessionState.ts`（`BrowserTabSession` 含 url/title，按 `workbenchSessionKey(conversationId)` 分会话）+ `BrowserView.tsx` 的 `onRuntimeChange` → `currentUrl` | 需聚合 |
| 页面标题 | `browserSessionState.ts` 的 tab `title`；运行时来自 `webview.getTitle()`（`BrowserView.tsx` 内） | 需聚合 |
| favicon | 未见现成来源 | 缺失（P2，可先用域名首字母占位） |
| 点击回到该页面 | Workbench 已有 `browser` tab 与激活 tab 的能力（`activateBrowserTab`） | 需聚合 |

关键差异：Qoder 展示的是"**agent 访问过的页面**"（agent 行为的产物），而我们现有的是"**用户打开的浏览器 tab**"（用户态）。两者语义不同。P1 的可行做法是从会话内的 browser 工具调用记录（Tool Result）聚合出已访问 URL 列表，而不是直接暴露用户 tab 列表——否则会把用户隐私态混进任务事实。

结论：**P1，且需要聚合层**，不能直接复用 tab 列表。

### 3.6 来源

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 任务来源条目 | 任务卡有"来源/交付"元信息字段（`TaskOverviewPage.tsx` L128、L162 的注释与分组），但会话内无来源列表 | 缺失 |
| 新增来源入口 | 无 | 缺失 |

结论：**缺失**。这一区在 Qoder 里对应的是它自己的任务来源体系（工作项/需求），Peer Agent 没有对等的上游对象。P2 处理，且需要先明确定义"来源"在本产品里指什么（会话来源渠道？关联工作项？），否则会造出无权威来源的展示。

### 3.7 进展摘要卡

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 摘要文本 | 目前只有聊天流的自然语言叙述，无结构化摘要 | 缺失 |
| 更新时间戳 | 无 | 缺失 |

结论：**缺失，且是最需要谨慎的一项**。它看起来只是"把最后一段话搬上去"，但实质上要求一个**摘要生成与准入**链路，属于 A 级变更（影响 System Context 与模型调用）。P2 处理，且必须走既有 Context Source 机制，不得在 renderer 里就地拼一句话塞进来。

## 4. 落地顺序

### P0（已实施）：会话内任务监控卡片堆叠

实施记录（2026-09-16 三次迭代定稿）：监控区是 **Apple 控制中心式多卡片堆叠**。外层 `.task-monitor-rail` 是无底色的堆叠容器（absolute 于 `.chat-surface`，头部之下，透明、无边框、无阴影）；每个分区是一张独立毛玻璃小卡（`.task-monitor-section`：14px 圆角、`blur(18px) saturate(1.15)`、自身阴影）。环境信息为 tile 半宽小卡矩阵（两两并排，对齐控制中心 Wi-Fi/蓝牙形态），进度/后台任务/产出为全宽卡。打开时 `.chat-surface--with-monitor` 给正文列（thread+composer，均为 in-flow）加 `padding-right` 让位，会话内容向左收窄；`.chat-header` 是 absolute 整行定位，不受 padding 影响，**头部永远不被挤压**。关闭时不占任何布局。清单按钮独占控制本区；`WorkbenchToggle` 独立控制 Workbench。旧 `'context'` / `'monitor'` 持久化值回退 `plan`。

| 布局契约 | 实现 |
| --- | --- |
| 堆叠容器 | `.task-monitor-rail`：absolute、transparent、无阴影；`--task-monitor-card: clamp(280px, 24%, 340px)` 与正文 `padding-right`（卡片+双侧 space-3 边距）同源，正文右缘恒等于卡片左缘减边距，绝不重叠 |
| 独立小卡 | `.task-monitor-section`：14px 圆角、`color-mix` 半透明底 + `backdrop-filter: blur(18px) saturate(1.15)`、`0 6px 20px` 阴影、10px 间距堆叠；`--tile` 变体用于半宽小卡 |
| tile 矩阵 | `.task-monitor-tiles`：`grid-template-columns: repeat(2, minmax(0,1fr))`，分支/工作区/运行位置各自成卡两两并排 |
| 与独立 Workbench 并存 | `:has(.chat-surface > .task-monitor-rail)` 钳制 Workbench 实际显示宽度（卡片 372px + 正文 360px 预留），不改持久化宽度，任一侧关闭自动恢复 |

| 分区 | 复用点 |
| --- | --- |
| 环境信息 | `ChatSurface` 已有 `workspaceGit` / `workspaceIsGit` / `workspacePath`，与 composer 环境胶囊共享事实 |
| 任务进度 | 当前会话唯一 `TaskOverviewItem.planProgress` / `statusLabel` |
| 后台任务（内联详情） | `ManagedShellTask` + `backgroundTaskPresentation` + `BackgroundRunDetails`（含两段式停止确认） |
| 产出 | `deriveTaskArtifacts` + `taskOverviewArtifacts.ts` |

四区共同点：**不新增数据通道、不新增协议类型、不改权限与 Evidence 语义**。这是既有事实的会话作用域投影与宿主迁移。

实现位置：

- 投影：`apps/desktop/renderer/src/workbench/taskMonitorRail.ts`
- UI：`apps/desktop/renderer/src/workbench/views/TaskMonitorRailView.tsx`
- 会话宿主：`apps/desktop/renderer/src/chat/components/ChatSurface.tsx`
- 所有权与四格测试：`taskMonitorOwnership.test.ts`、`taskMonitorRail.test.ts`、`useTaskOverview.performance.test.ts`

实施硬约束：

1. **不复活全局后台管理面。** 后台任务只作为当前会话监控栏的会话作用域视图；旧 ChatHeader 全局弹层入口已删除。
2. **必须复用同一个 Runtime reader 与 stops 链路。** `BackgroundRunsProvider` 持有唯一轮询；监控栏通过 `useBackgroundRunsContext()` 消费同一快照并复用两段式停止确认。
3. **只在监控栏打开且会话可见时轮询 TaskOverview。** `ChatSurface` 只在 `taskMonitorOpen` 时挂载监控栏；栏内继续使用 `enabled: active && !!conversationId` 门控隐藏会话。
4. **会话监控栏与独立 Workbench 可以同时打开。** 外层网格只钳制 Workbench 的实际显示宽度，不改用户持久化宽度；在 1280px 真机验证中分别保留聊天正文 360px、会话监控栏 248px、Workbench 408px。

### P1：网页查阅

需要从会话内的 browser 工具调用聚合已访问页面，并避免与用户 tab 隐私混淆。依赖聚合层设计。

### P2：技能与 MCP、来源、进展摘要卡

- 技能与 MCP：数据完备，但需要先定"会话作用域能力过滤"的口径。
- 来源：需要先定义产品语义。
- 进展摘要卡：A 级，需要摘要生成链路 + Context Source 准入。

## 5. 栏位与容器约束

- **宿主（已实施）**：悬浮卡片挂在 `.chat-surface` 内部（absolute）；打开时正文列 `padding-right` 让位、头部（absolute 整行）不被挤压，关闭时不占布局。清单按钮独占控制，独立 `WorkbenchToggle` 不参与该状态。
- **与计划面板的关系**：计划（Goal）仍属于独立 Workbench；两者可同屏并存，DOM 和状态互不嵌套，宽度调停保证聊天正文不归零。
- **写操作边界**：后台任务停止继续走 `useBackgroundRunsContext` 的同一条 `stops.stop` 链路（含两段式确认）；本栏不新增写通道。
- **空态**：分区为空时整段不渲染（对齐 Qoder 空分区行为，不写占位文案）。
- **样式**：分区样式在 `apps/desktop/renderer/src/styles/workbench.css` 末尾的 `@layer components` 内（`task-monitor-*`），复用 `--za-*` / `--ui-*` token；不新增本地 `@keyframes`（架构治理脚本禁止）。

### 5.1 已否决方案（留档）

- **Workbench 一级「监控」Tab**：物理归属错误。它会把当前会话事实误建模为窗口级工作区内容，并与截图中的两个独立开关冲突。
- **`goalSlot` / portal 抢占**：计划面板与任务监控栏争用单节点宿主，无法表达两者同屏并存。
- **只保留 composer 胶囊**：胶囊适合输入区紧凑入口，但不能替代栏内完整环境详情。正确做法是两处共享 `workspaceGit` / `workspacePath` 事实。

## 6. 验收标准

1. 任务监控栏 DOM 直接属于当前 `.chat-workspace`，不属于 `.workbench-panel`，Workbench 中也不存在 `monitor` Tab。
2. 会话监控开关与独立 Workbench 开关覆盖四格组合；两者同时打开时聊天正文、监控栏和 Workbench 均保持可用且不重叠。
3. 环境信息在栏内显示分支 / 工作区 / 本地运行位置，composer 环境胶囊仍保留；两处共享同一事实源。
4. 后台任务只显示本会话运行；点击行在栏内展开 `BackgroundRunDetails`，并复用同一停止确认链路。
5. 任务进度来自当前会话 `TaskOverviewItem.planProgress`；产出遵守既有治理 ref 过滤与打开详情规则。
6. `taskMonitorOwnership.test.ts` 四格全部通过，desktop typecheck / build 与相关 Workbench 布局测试通过。
7. 真机截图覆盖四格，且同时打开时正文宽度不归零。
