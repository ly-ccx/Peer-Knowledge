# 任务信息卡

创建时间：2026-09-14
最后更新：2026-09-22（任务信息卡实施及自动/Electron验收记录回写）

## 当前有效方案

本节是当前实现依据。参考用户提供的 Codex「输出内容 / 来源」截图的信息层级和轻量卡片表达，不推断其未展示的点击行为。以下历史章节只用于解释演进，不再作为冲突规则的实现依据。

### 目标与边界

回答「产出了什么、参考了什么、还有什么在运行、工作发生在哪里」。优先级为产出与来源、活动运行、环境详情。卡片属于当前会话，开关独立于 App 级 Workbench；Workbench 负责打开具体文件、网页和计划，不成为无目标的“更多”落点。

展示层复用现有事实：messages、taskOverview、BackgroundRunsProvider、会话 browserSession、现有 Git/工作区状态。不新增执行通道、授权路径、Evidence 存储或摘要生成。保留两段式停止确认、运行历史、会话隔离与 TS/TSX 长源码高亮。若实现需要跨越上述边界，先升级设计评审。

### 分区与显示条件

固定顺序：**产出 → 来源与工具 → 正在运行（有活动才出现）→ 环境（折叠）**。

| 分区 | 事实与显示条件 | 默认显示 | 点击去向 |
| --- | --- | --- | --- |
| 产出 | 当前会话 taskOverview 中有明确 openPath 的用户可消费产物；复用治理 ref 过滤和去重，不把工具结果 ref 当文件 | 每类最多 2 项；无产出显示一句「暂无产出」 | 打开该文件/图片/代码对应的 Document target；文件缺失明确报错，不改开空 Workbench |
| 来源与工具 | 当前会话真实附件、明确网页资料和非 synthetic 的结构化 Skill/MCP 调用；安装清单、助手正文中的工具名不算使用 | 总计最多 4 项；无资料和调用时显示「暂无来源或工具记录」 | 本地资料打开具体文件；网页激活对应会话 tab，未打开则导航该 URL；工具定位对应调用详情，不导航到无关文档页 |
| 正在运行 | 当前会话 running/stopping 后台任务，使用同一运行快照 | 最多 2 项；没有活动时整个分区消失 | 本卡片内展开该运行的真实命令、目录、状态、日志和原有停止确认 |
| 环境 | 现有工作区、Git HEAD、起始分支及隔离状态；不是模型生成摘要 | 默认一行简要状态，可展开详情 | 展开只展示事实；独立「环境设置」入口展开设置区，复用现有 handler 和禁用条件 |

来源事实必须可追溯到当前会话，不扫描用户日常浏览器，不将浏览器全局历史当资料。不能可靠提供打开目标的对象不伪造可点击行为；缺失目标明确说明原因。显示名称允许缩短，完整路径/URL通过 tooltip 或详情可查。

所有查看更多均在所属分区内展开为完整列表，显示真实隐藏数，并可收起。无隐藏项不显示按钮；切换会话清除展开、选中运行与停止确认。产物的过滤规则在展开前后相同。运行终态从实时列表退出，但不删除运行记录、日志或 Evidence。计划进度不抢占卡片主体，需要时通过明确的「查看计划」入口打开当前会话计划。

### 环境信息与设置

明确区分「当前分支」「起始分支」「工作目录」「运行位置」「隔离方式」。不再把分支名标为“当前工作区”，不把起始分支选择误导成 checkout。非 Git 目录不显示无效 Git 操作；detached HEAD 如实表达，不伪装为分支名。

环境设置默认关闭，只在用户主动打开时展示；分支选择、创建分支、Worktree 隔离及提交/推送的现有可用入口不得悄悄删除。沿用 ChatSurface 已有操作及 streaming/可用性限制，不在卡片重建 Git 执行。控件各占清楚的一行，标签和值分开，触发器、箭头、菜单均不得被滚动容器裁掉。当前轮不改变输入框既有状态胶囊的事实语义。

### 视觉和布局

一张随内容收拢的浅底卡片，细边框、适度圆角、轻阴影；分区标题弱化，行采用小图标和对象名称，少量分隔线。取消大号“实时”装饰和表单优先结构。不为模仿截图而放没有真实功能的加号。

外层 rail 负责定位和让位，内层 card 承担背景、边框与滚动上限。空态不撑满整列，长列表达到可用高度才滚动。使用项目既有 token；局部 dropdown 样式必须实际覆盖通用最小宽度，不靠 overflow:hidden 掩盖截断。

消息导航属于正文列，其定位必须扣除卡片占位，不允许刻线覆盖卡片。Workbench 与卡片开关互不控制；双开时保证正文、卡片和 Workbench 有可用空间，窄布局需要自适应排布，不依靠相互覆盖。关闭卡片后释放占位。测量实际子控件边界，不能只比较被裁切容器的 scrollWidth。

### 被替换的旧规则

- 废止下方历史章节的「无背景裸内容」规则；改为用户确认的轻量卡片。
- 废止环境控制常驻并优先集中右栏的规定；状态与设置分开，设置按需展开。
- 废止安装技能/MCP清单充当会话使用事实的规定；保留前轮已落地的结构化调用筛选。
- 废止全局 hiddenTotal 和跳转 Workbench documents 的查看更多规则；每区独立展开。
- 废止后台任务终态常驻实时列表的历史行为；保留活动过滤及历史日志。
- 历史测试与尺寸记录不算本轮验收证据，特别是英文非 Git 测试不能证明中文 Git/Worktree 控件正确。

### 测试矩阵与实施顺序

1. 先更新本文，再实现会话事实投影和明确打开目标。
2. 实现分区与环境设置拆分，再处理卡片收拢和消息导航/Workbench让位。
3. 自动回归：当前/其他会话 × 有/无真实资料或调用；运行活动/终态；每区有/无隐藏项 × 展开/收起；每种对象的准确打开目标；超限产物过滤不变；TS/TSX 高亮不退化。
4. Electron：中/英文 × 普通 Git/Worktree/非 Git × 宽/窄窗口 × 信息卡开关/Workbench开关四组合，共48格。输出逐格结果、截图和正文/卡片/控件/消息导航边界。没有隐藏项时展开交互不适用，但要证明按钮不存在。
5. 交互场景验证真实命令自然结束后退出、历史日志仍可取；文件/网页/调用准确打开；环境详情与设置可展开且操作入口保留。夹具资料与真实执行分开标注。
6. 完成后回写实际范围、可复跑命令、证据和未覆盖项，未运行检查不得记录为通过。

## 本轮实施状态

2026-09-22：实现及下述自动、隔离 Electron 检查已完成；尚未提交代码或知识库变更。

## 实施与验收记录

### 实际实施

产出优先，来源与工具合并，活动后台运行按会话过滤；环境置于末尾，事实与下次任务设置分别展开。文件打开具体路径，网页切换具体 tab，工具参数/结果在卡内展开。附件使用已有文本/图片内容，缺失时提示不可直接预览。当前任务隔离读取 deliveryLine，不冒用下次任务偏好。计划保留轻量入口；未添加无功能的加号。

卡片改为随内容收拢、有限高度滚动；修正 Dropdown 层级覆盖。按会话容器宽度自适应：不足640px时信息卡置于正文上方；1000px窗口限制Workbench显示宽度，不更改用户保存偏好。消息导航不覆盖卡片。验收发现原双开正文仅112px，新增至少300px断言后修复并重跑。

### 可复跑命令（在代码仓根目录运行）

```sh
node --experimental-strip-types --test apps/desktop/renderer/src/workbench/taskMonitor*.test.ts apps/desktop/renderer/src/app/pages/taskOverviewArtifacts.test.ts
node --experimental-strip-types --test apps/desktop/renderer/src/workbench/file-preview/fileTypes.test.ts apps/desktop/renderer/src/workbench/file-preview/sourceHighlight.test.ts apps/desktop/renderer/src/chat/components/markdown/codeHighlighter.test.ts
pnpm --filter @peer-agent/desktop typecheck
node apps/desktop/scripts/task-monitor-electron-smoke.mjs
```

以上命令本轮实际执行通过。长Electron命令需允许超过普通前台调用时限；脚本创建独立临时目录，打印SMOKE_ROOT，并输出report.json、matrix.json、48格截图、layout.json、tool-results.json及history-after-completion.json。不要把启动接受状态当运行成功，应检查最终report.status及matrix格数。

### 矩阵及证据

- 来源4类×当前/其他会话×有/无事实，另测去重与synthetic排除；各可展开分区有/无隐藏项，隐藏时展开/收起；精确文件路径、网页tab与工具详情目标。
- 中英文×Git/非Git×空闲/执行中8格环境组件检查；另测未知/当前目录/Worktree隔离状态与偏好分离。
- Electron中英文×真实临时Git/Worktree/非Git×1440/1000窗口×卡片及Workbench四开关组合48格全部通过，测量子控件实际边界、正文至少300px及导航/面板不重叠。
- Electron精确来源文件正文、调用结果、网页目标URL而非原活动标签验证通过；真实后台Shell状态和详情、自然结束退出、历史快照与磁盘stdout保留验证通过。
- 回归与类型检查证据：local-shell-artifact://shell_edfa6557-8faf-4169-aa5d-2cf039b6aec1。
- 最后一轮Electron报告核验：local-shell-artifact://shell_3e270b45-aa92-4576-bf85-6ad86dc5a240（report passed、errors为空、matrix 48）。

### 已知边界与未覆盖项

Skill/MCP调用历史、资料和会话消息是夹具，不代表线上MCP或模型执行；网页是本地HTTP测试服务。Shell经过真实执行链路，授权为测试专用批准。Git/Worktree为隔离临时仓库，未在用户仓库执行切换、提交或推送。环境操作handler和禁用状态有组件测试，未逐个执行真实Git变更。产物过滤和展开由自动组件/投影测试覆盖，Electron的精确文件打开使用来源附件。超过500000字符源码仍保持既有纯文本回退。截图已生成并保存，但不声称做了独立人工逐像素审查。提交/推送入口仍由既有Git操作界面承担，不在信息卡伪造操作。上述边界不等于未通过检查，不将其冒充已覆盖。

---

## 历史设计（已被上述当前有效方案替代）

原题：任务监控栏（Task Monitor Rail）产品与信息架构设计。原最后更新：2026-09-21。以下保留历史上下文，冲突时以当前有效方案为准。

## 1. 文档定位

本文回答一个问题：**参照 Qoder 的任务信息区，Peer Agent 如何把任务监控能力嵌入当前会话面板，并让它与独立 Workbench 保持清晰边界。**

三份文档的分工（本文不重复它们的内容）：

| 文档 | 负责 |
| --- | --- |
| [`right-workbench-panel.md`](./right-workbench-panel.md) | Workbench 窗口级容器：开合、宽度、Tab 切换、快捷键 |
| [`goal-right-status-panel.md`](./goal-right-status-panel.md) | Goal（计划）专题：目标、进度、阻塞、验收的层级与状态反馈 |
| **本文** | **会话内任务监控栏：宿主边界、环境 / 进度 / 后台任务 / 产出分区，以及与独立 Workbench 的共存** |

核心结论：Qoder 右侧面板的价值不在视觉，而在于**把一个长任务运行期间"散落在各处的运行事实"收敛到同一处**——用户不用翻聊天记录、不用切 Tab，就能回答"后台还有没有在跑的进程""这次动了哪些文件"。

**信息归属的边界（2026-09-21 用户修正：环境控制集中到任务监控栏）**：

- **输入框只显示执行状态**——`formatComposerEnvCapsule` 说明「这次写在哪」，不再用下拉把「人在哪」和「下次从哪分叉」混成同一个「在 xxx」。
- **右栏是任务监控栏**——同时回答「这个任务正在/已经产生了什么」和「当前环境」。环境区拆成当前工作区 HEAD 与任务源头两行；源头选择和 Worktree 开关只出现在这里。选源头不会 `checkout`。Qoder 右栏顶部按钮就叫"隐藏任务监控"。

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

结论：环境信息**进任务监控栏，并且当前工作区与任务源头必须拆开**（2026-09-21 用户修正：输入框胶囊把「人在哪」和「下次从哪分叉」混成同一个「在 xxx」，选了源头会话里仍显示 HEAD）。

- **当前工作区**：只读投影 `WorkspaceGitState.current`（真实 HEAD）。选源头**不会** `checkout`。
- **任务源头**：草稿可选的 `workspace.baseBranch`；会话绑定后改为只读任务线。下拉与 Worktree 开关放在本栏，复用 `ChatSurface` 已有 `workspaceUpdate` / `preferredWorktree`，不新增写通道。
- **输入框**：只留 `formatComposerEnvCapsule` 状态，不再提供源头下拉。

剩余缺口（git status 的 dirty 态）仍待补 `git:status` IPC；补上后接入本栏当前工作区行，不回到输入框。

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

### P0（已实施）：无背景裸内容

实施记录（2026-09-16 终版·裸内容）：监控区**没有卡片面板**——无背景色、无边框、无圆角、无阴影；右侧就是分区标签 + 图标行直接浮在会话区域上。分区（环境信息 / 技能与 MCP / 任务进度 / 后台任务 / 产出 / 网页查阅）之间只用留白和 28% 透明度的极细分隔线；行静止时完全无背景，hover 才出现 32% 透明度的极轻底色；唯一保留底色的是展开的后台任务日志块（55% 透明度，文本可读性需要）。底部「查看更多 (N)」仍居中弱化。打开时 `.chat-surface--with-monitor` 给正文列加 `padding-right` 让位；`.chat-header` 是 absolute 整行定位不受影响。关闭时不占任何布局。

| 契约 | 实现 |
| --- | --- |
| 单卡片面 | `.task-monitor-card` 唯一承担底色/圆角/阴影；外层 rail 只定位 |
| 分区数据源 | 环境=当前工作区 HEAD（`workspaceGit.current`）+ 任务源头（`gitChrome.taskLine` / `baseBranch`）+ workspacePath；技能与 MCP=listSkills+listCapabilities+mcpListCapabilities（与 ChatHeaderCapabilities 同链路）；进度/产出=taskOverview 会话投影；后台任务=BackgroundRunsContext 会话过滤；网页查阅=browserSession.tabs（host+首段路径短标签） |
| 查看更多 | hiddenTotal = 产出隐藏项 + 后台超限 + 网页超限；点击跳 Workbench documents |
| 与独立 Workbench 并存 | `:has(.chat-surface > .task-monitor-rail)` 钳制 Workbench 实际显示宽度（卡片 372px + 正文 360px），不改持久化宽度 |

| 分区 | 复用点 |
| --- | --- |
| 环境信息 | 当前工作区 HEAD 与任务源头分行；源头/Worktree 控制复用 `ChatSurface` 已有 handler。输入框只留状态胶囊 |
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
- **写操作边界**：后台任务停止继续走 `useBackgroundRunsContext` 的同一条 `stops.stop` 链路（含两段式确认）；源头选择与 Worktree 开关复用 `ChatSurface` 已有 `workspaceUpdate` / `preferredWorktree`。本栏不新增写通道，也不 `git checkout`。
- **空态**：分区为空时整段不渲染（对齐 Qoder 空分区行为，不写占位文案）。
- **样式**：分区样式在 `apps/desktop/renderer/src/styles/workbench.css` 末尾的 `@layer components` 内（`task-monitor-*`），复用 `--za-*` / `--ui-*` token；不新增本地 `@keyframes`（架构治理脚本禁止）。

### 5.1 已否决方案（留档）

- **Workbench 一级「监控」Tab**：物理归属错误。它会把当前会话事实误建模为窗口级工作区内容，并与截图中的两个独立开关冲突。
- **`goalSlot` / portal 抢占**：计划面板与任务监控栏争用单节点宿主，无法表达两者同屏并存。
- **只保留 composer 胶囊**：胶囊适合输入区紧凑入口，但不能替代栏内完整环境详情。正确做法是两处共享 `workspaceGit` / `workspacePath` 事实。

## 6. 验收标准

1. 任务监控栏 DOM 直接属于当前 `.chat-workspace`，不属于 `.workbench-panel`，Workbench 中也不存在 `monitor` Tab。
2. 会话监控开关与独立 Workbench 开关覆盖四格组合；两者同时打开时聊天正文、监控栏和 Workbench 均保持可用且不重叠。
3. 环境信息在栏内拆成当前工作区 HEAD 与任务源头两行；源头选择和 Worktree 开关只出现在监控栏。输入框只留环境状态，不再用下拉选源头。
4. 后台任务只显示本会话运行；点击行在栏内展开 `BackgroundRunDetails`，并复用同一停止确认链路。
5. 任务进度来自当前会话 `TaskOverviewItem.planProgress`；产出遵守既有治理 ref 过滤与打开详情规则。
6. `taskMonitorOwnership.test.ts` 四格全部通过，desktop typecheck / build 与相关 Workbench 布局测试通过。
7. 真机截图覆盖四格，且同时打开时正文宽度不归零。
