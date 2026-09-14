# 任务上下文栏（Task Context Rail）产品与信息架构设计

创建时间：2026-09-14
最后更新：2026-09-14

## 1. 文档定位

本文回答一个问题：**参照 Qoder 的任务右侧面板，Peer Agent 需要在主交互区右侧常驻哪些任务上下文信息，这些信息各自来自哪里。**

三份文档的分工（本文不重复它们的内容）：

| 文档 | 负责 |
| --- | --- |
| [`right-workbench-panel.md`](./right-workbench-panel.md) | Workbench 窗口级容器：开合、宽度、Tab 切换、快捷键 |
| [`goal-right-status-panel.md`](./goal-right-status-panel.md) | Goal（计划）专题：目标、进度、阻塞、验收的层级与状态反馈 |
| **本文** | **任务上下文分区：环境信息 / 后台进程 / 技能与 MCP / 产出 / 网页查阅 / 来源 / 进展摘要** |

核心结论：Qoder 右侧面板的价值不在视觉，而在于**把一个长任务运行期间"散落在各处的运行事实"收敛到同一处**——用户不用翻聊天记录、不用切 Tab，就能回答"我现在在哪个分支""后台还有没有在跑的进程""这次动了哪些文件""agent 查过哪些网页"。

Peer Agent 已经有这些事实，但它们**分散在不同 surface**：后台进程在 ChatHeader 弹层、产出在任务总览页、技能与 MCP 在 ChatHeader 弹层、分支只在会话初始化时读一次。本设计的目标是新增一个**会话作用域的分区栏**，把这些事实按同一套分区模型投影出来，而不是再造数据源。

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

结论：环境信息是**唯一一项数据链路需要小补的分区**——git status（dirty 状态）目前没有 IPC。P0 先落地「分支名 + 运行位置」，dirty 状态在补 `git:status` 通道后再接。

### 3.2 后台进程

| 字段 | Peer Agent 数据源 | 状态 |
| --- | --- | --- |
| 命令行 | `packages/protocol/src/index.ts:934` `ManagedShellTask.command` | 已具备（位置错） |
| 工作目录 | 同上 `ManagedShellTask.cwd` | 已具备（位置错） |
| 运行状态（运行中/已完成/失败…） | 同上 `ManagedShellTask.status`、`exitCode`、`startedAt`、`completedAt` | 已具备（位置错） |
| 状态文案映射 | `apps/desktop/renderer/src/workbench/backgroundTaskPresentation.ts`（`运行中`/`停止中`/`已完成`/`失败`/`已停止`/`超时`，含测试 `backgroundTaskPresentation.test.ts`） | 已具备（复用即可） |

现状：`BackgroundRuntimePanel.tsx` 已经是完整的运行列表（含 `background-run-row`、点击进入 `BackgroundRunDetails`），入口是 `GlobalBackgroundTasksButton.tsx` 的 **ChatHeader 弹层**。结论：**零新增数据工作**，本设计只把它从"弹层"提升为"常驻分区"。

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

**实施陷阱（必须知道）**：不能用 `item.taskId === conversationId` 去挑"本会话那一条"。`TaskOverviewItem.taskId` 是**稳定投影身份**，取值可能是 conversationId、planId 或 automationId+runId；而聚合器对「有活跃计划的会话」只推 goal_plan 投影，并用 `projectedPlanConversationIds` 跳过同会话的 conversation 投影——**恰恰在长任务会话里 `taskId` 就是 planId**。正确做法是取并集：`taskId === conversationId` 或 `item.conversationId === conversationId`（后者是 goal_plan / automation 投影的深链字段）。另有两点：产物挂在 `planSteps[].artifacts` 而非 item 上；多条命中时应优先有产物的一条。实现见 `taskContextRail.ts` 的 `selectConversationTaskOverviewItem()`。

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

### P0（本次实施）：数据已具备的三区

实施记录（2026-09-14）：三区已落地为 **Workbench 新增一级视图「上下文」**（`WorkbenchTabId` 增加 `'context'`）。

| 分区 | 为什么是 P0 | 复用点 |
| --- | --- | --- |
| 环境信息 | 会话一开始就能确定，零异步风险 | `useWorkspaceGit` |
| 后台进程 | 数据链路完整且有测试 | `ManagedShellTask` + `backgroundTaskPresentation` + `BackgroundRuntimePanel` |
| 产出 | 全部投影逻辑已存在 | `deriveTaskArtifacts` + `taskOverviewArtifacts.ts` |

三区共同点：**不新增数据通道、不新增协议类型、不改权限与 Evidence 语义**。纯投影迁移。

已成文的实现位置：

- 投影（纯函数，可测）：`apps/desktop/renderer/src/workbench/taskContextRail.ts`
- UI：`apps/desktop/renderer/src/workbench/views/TaskContextRailView.tsx`
- 测试：`apps/desktop/renderer/src/workbench/taskContextRail.test.ts`（9 项）

实施期发现的两条硬约束（与 §5 的初版设想不同，以此处为准）：

1. **不复活已退役的后台管理面。** 提交 `bd9fd0b4` 已把后台运行**管理**收敛到 ChatHeader，并让 `normalizeWorkbenchTab` 把 `background`/`shell`/`threads` 一律归一到 `plan`，测试也断言退役 tab 不得恢复成"空白重复的管理面"。因此本栏的后台进程区是**会话作用域的只读投影**，删除/停止等写操作仍只在 ChatHeader 面板内。
2. **必须复用同一个轮询 reader。** `BackgroundRunsProvider` 持有唯一的 Runtime 轮询；上下文栏通过新增的 `useBackgroundRunsContext()` 消费同一份快照，并用 `requestRunDetails(taskId)` + `BackgroundRuntimePanel` 的 `initialTaskId` 深链到既有详情视图 —— 不新建第二个 poller，也不新建第二套详情。

### P1：网页查阅

需要从会话内的 browser 工具调用聚合已访问页面，并避免与用户 tab 隐私混淆。依赖聚合层设计。

### P2：技能与 MCP、来源、进展摘要卡

- 技能与 MCP：数据完备，但需要先定"会话作用域能力过滤"的口径。
- 来源：需要先定义产品语义。
- 进展摘要卡：A 级，需要摘要生成链路 + Context Source 准入。

## 5. 栏位与容器约束

- **宿主（已实施）**：作为 **Workbench 的一级视图**接入，与 计划 / 浏览器 / 文件 / 文档 并列（`WorkbenchPanel.tsx` 的 `TABS` 中新增 `context`，视图槽 `workbench-view--context`），复用 Workbench 既有的开合、宽度、最大化与持久化能力。
- **与计划面板的关系**：计划（Goal）仍是独立的一级视图，两者由 Workbench tab 切换，同屏只显示一个 —— 比"在同一个右栏里抢位置"更简单，也不需要新增显示优先级规则。
- **只读约束**：本栏所有项均为只读展示 + 跳转动作；不在此栏内提供写操作（如切分支、杀进程）。写操作留在各自既有的、受权限闸门约束的入口。
- **空态**：分区为空时整段不渲染（对齐 Qoder 空分区行为，不写占位文案）。
- **样式**：分区样式追加在 `apps/desktop/renderer/src/styles/workbench.css` 末尾的 `@layer components` 内，复用 `--za-*` / `--ui-*` token；不新增本地 `@keyframes`（架构治理脚本禁止）。

### 5.1 曾经的候选方案（已否决，留档）

初版设想是复用 `WorkbenchContext` 的 `goalSlot`（`ChatSurface.tsx` L1724-1727 的右栏 portal 宿主，`GoalPlanPanel` 通过 `sidePanelContainer` 挂载）。否决原因：`goalSlot` 是**单节点** portal 宿主且已被计划面板占用，两者共存需要引入"同一时刻显示哪一个"的抢占规则；而 Workbench tab 体系本来就提供并行的多视图切换，成本更低且不动计划面板的既有行为。

## 6. 验收标准

1. 环境信息、后台进程、产出三区在桌面端会话右侧实际可见。
2. 每区每一项都可点击打开对应详情：分支 → 分支信息；后台进程 → `BackgroundRunDetails`；产出 → 文件/变更/截图。
3. 产出区遵守既有过滤规则：不展示 `tool-result://`、`local-shell-artifact://`、`goal-plan://` 等治理 ref。
4. 后台进程区的状态文案与 `backgroundTaskPresentation` 一致（含"运行中/已完成/失败/超时"）。
5. `cd apps/desktop && pnpm typecheck` 与 `pnpm test` 通过。
6. 分区为空时不出现占位文案，标题保留。
