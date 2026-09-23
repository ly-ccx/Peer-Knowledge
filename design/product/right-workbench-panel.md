# 右侧工作面板（Workbench）设计规范

创建时间：2026-06-23
最后更新：2026-09-21（文件区合并为 master-detail；文档区重定位为会话产物聚合）

## 背景

Peer Agent 当前的右侧空间只在 Goal 流程激活时被 `GoalPlanPanel` 通过 portal 占用，宽度 380px 写死、用户不可控、没有"打开/收起"入口。对照 Codex 的工作台体验，缺三件事：

1. **常驻入口**：标题栏右上角一个能展开/收起右侧栏的按钮。
2. **多目标内容**：右侧栏内承载 *Goal / 终端 / 浏览器 / 文件* 四种目标视图，按需切换。
3. **可拖拽宽度**：左右栏之间的分隔线可拖动，宽度持久化。

本文档约定交互、视觉、状态与持久化规则，交由代码仓 `peer_agent` 的 `apps/desktop/renderer` 落地。

## 现状速览

- 主布局：`apps/desktop/renderer/src/App.tsx` → `.app-shell` → `.app-layout`（CSS grid）→ `.app-sidebar`（左）+ `.main-panel`（右）。
- 左侧栏宽度由 `--za-sidebar-width: 264px`（`tokens.css`）控制，CSS 变量但无拖拽。
- 顶部右上角槽位：`app/components/AppHeader.tsx` 是空 stub，`shell.css` 已经把它定位在 `top:0; right:0; left: var(--za-sidebar-width)`，是天然的按钮承载区。
- 会话内顶栏：`chat/components/thread/ChatHeader.tsx`（高 52px，`-webkit-app-region: drag`），右侧 `.chat-header-right` 目前只有 Find 按钮。
- 现有 GoalPlanPanel：`ChatSurface.tsx` 内的 `<aside className="chat-side-panel" />` 作为 portal 槽位，`GoalPlanPanel.tsx` 通过 `sidePanelContainer` 注入。**本期需要全量迁出**到 Workbench。
- 没有任何 resize handle、panelWidth 状态、持久化字段。

## 命名

- 整体特性叫 **Workbench**（工作台），右侧那条可展开的栏叫 **Workbench Panel**。
- 四个子视图叫 **GoalView / TerminalView / BrowserView / FilesPane**。
  - **FilesPane** 是 master-detail 容器：左侧文件树（原 FilesView）+ 右侧文件预览（原 DocumentView 的 detail 部分，含 Preview/Source/Diff）。两者同屏常驻，不再互斥切换。
- 第五个 tab「产物」（原「文档」tab 的重定位）承载 **SessionArtifactsView**：本会话产物的聚合列表，点击条目进入文件区的 detail 预览。
- 顶部触发按钮叫 **WorkbenchToggle**。

## 入口与触发

### WorkbenchToggle 按钮

- 位置：窗口右上角，挂在 `AppHeader` 上（不挂 ChatHeader，因为 Workbench 是窗口级的，不属于单条会话）。
- 视觉：与 ChatHeader 内 Find 按钮同一规格的图标按钮（28×28），图标使用「右侧面板」线性图标（参考截图右上角红框，两栏面板缩略 + 右栏高亮）。
- 状态：
  - 收起态：图标线性、`opacity: 0.7`，`aria-pressed="false"`。
  - 展开态：图标实心、主色描边，`aria-pressed="true"`。
- 快捷键：`⌘\`（与 Codex/VS Code 一致）。
- 区域属性：`-webkit-app-region: no-drag`，避免落在拖动区里失效。
- 提示：Tooltip 文案「显示/隐藏工作台 (⌘\\)」。

### 子视图切换

WorkbenchToggle 只控制"开/关"，不切视图。视图切换由 Panel 内部的 **Tab Rail**（左侧细条 tab 列表）负责：

- Tab 顺序固定：**Goal / 终端 / 浏览器 / 文件 / 产物**。
- 默认选中：当前会话上次保留的 tab；首次打开默认为「终端」（Goal tab 仅在有活跃 GoalPlan 时才会作为新会话的默认）。
- 不提供独立 tab 快捷键；唯一快捷键是 `⌘\` 控制 Panel 开合，tab 切换全部靠点击。

#### Goal tab 的特殊行为

- **常驻可见**，无活跃 GoalPlan 时该 tab 置灰、`aria-disabled="true"`、tooltip「暂无 Goal」。
- 置灰态**纯装饰**——点击不做任何事、不跳转、不展开说明。这是为了避免和"从 chat 输入框发起 Goal"的主路径分裂。
- 当 conversation 中产生新 GoalPlan 时：
  - 若 Workbench 当前关闭，**自动展开**。
  - 自动把当前会话的 activeTab 切到 `goal`。
  - 该自动行为只在「GoalPlan 从无到有」那一瞬间触发；用户随后手动切走/关掉 Panel 不会再被打断。

## 布局与尺寸

主布局从两列改成三列 grid：

```
[ app-sidebar ][ main-panel ][ workbench-panel? ]
   左 264 (tok)   弹性 1fr      右 0 / collapsedHidden / W
```

- Workbench Panel 收起时：grid 列宽 0，组件 `display: none`，不参与排版。
- Workbench Panel 展开时：grid 列宽 = `--za-workbench-width`（CSS 变量，初始 `420px`）。
- 最小宽度 `320px`，最大宽度 `min(900px, 55vw)`，越界时夹紧到边界并轻微弹回（120ms）。
- 主区（main-panel）目标可见宽度 `≥ 480px`，但**不硬性禁止**继续拖窄（见下"拖拽与挤压"）。

### Panel 内部

```
┌─ Workbench Panel ─────────────────────┐
│ ┌── TabRail ──┐ ┌── ViewSlot ───────┐ │
│ │ Goal        │ │                   │ │
│ │ 终端  ●     │ │  active view      │ │
│ │ 浏览器       │ │                   │ │
│ │ 文件         │ │                   │ │
│ └─────────────┘ └───────────────────┘ │
└───────────────────────────────────────┘
```

- TabRail：宽 56px，纵向排列；每个 tab 是 32×32 图标 + 8px label（label 跟随当前语言）。
- ViewSlot：剩余空间，承载具体子视图。子视图自己处理顶部工具条。
- Panel 顶部留 52px padding-top 与 ChatHeader 对齐（macOS hiddenInset 不需要再为红绿灯让位，AppHeader 已经在那里）。

## 文件区（FilesPane，master-detail）

2026-09-21 合并：原「文件」与「文档」两个互斥一级 tab 合并为一个「文件」区。动机：旧交互里点树中文件会强制把 activeTab 从 `files` 切到 `documents`，返回再手动切回，导航上下文（树）与内容（预览）被建模成两个平级世界，造成乒乓跳转。

### 结构

```
┌─ FilesPane（「文件」tab 的 ViewSlot 内容）──────┐
│ ┌─ master：文件树 ──┐ ┌─ detail：文件预览 ────┐ │
│ │ FilesView（常驻） │ │ DocumentView detail    │ │
│ │ 展开态/滚动/选中  │ │ Preview/Source/Diff    │ │
│ └──────────────────┘ └───────────────────────┘ │
└──────────────────────────────────────────────────┘
```

- **点文件不切 tab**：树点击走 `openFileInPlace`（只更新 detail 的文档会话），`activeTab` 保持 `files`，Workbench 只在关闭态被强制打开。
- 树与预览**双向同步**：树选中项跟随 detail 当前文件；`revealInFiles` 从「跳转到 files tab」改为「在常驻树中定位并展开」。
- 宽度自适应：容器 ≥ ~560px 时左右分栏（树约 40%）；更窄时 detail 覆盖树，detail 头部显示面包屑 + 返回按钮（Esc 同效）回到纯树。返回只隐藏 overlay，不改文档会话状态。
- 窄覆盖态下再点树中其他文件 → 立即重新显示 detail（覆盖态解除）。

### 「产物」tab（SessionArtifactsView）

- 原「文档」tab 重定位为**会话产物聚合**：按任务分组列出本会话产物（复用 `taskOverviewArtifacts` 投影与治理过滤，不新增数据通道），轮询仅在 tab 激活时启用。
- 点击产物条目 → `openFile`（落点改为 `files` tab 的 detail 预览），不在产物 tab 内嵌预览。
- detail 组件（DocumentView）只此一份，宿主从 documents ViewSlot 迁至 FilesPane 右栏；「浏览文件」回跳按钮随宿主迁移消失，被窄覆盖态的返回按钮取代。

## 拖拽分隔线（Resizer）与挤压策略

### Resizer 基础

- 一个 6px 宽的不可见 hit-area，位于 main-panel 与 workbench-panel 的交界。
- Hover：中间出现 2px 主色细条，`cursor: col-resize`。
- 拖拽时：
  - 全屏 overlay 接管 pointer，避免触发下层 hover。
  - body 加 `user-select: none`，关闭文本选择。
  - 实时更新 `--za-workbench-width` CSS 变量（不走 React state，避免每帧 rerender）。
  - 松手时把最终宽度写入持久化（见下）。
- 双击分隔线：宽度回到默认 `420px`。
- 键盘可达性：分隔线 `role="separator"` `tabindex="0"`，左/右方向键步进 16px，`Home/End` 跳到边界。

### 主区被挤的"临界吸附"逻辑

- 临界点：`window.innerWidth - sidebar(264) - workbench(W) < 480`。
- 用户拖拽 Workbench 增大、即将越过临界时：
  - 先在主区低于 480px 的位置出现一个 8px 的"软阻尼"（动一点但跟手感变沉）。
  - 用户继续拖过阻尼区 ≥ 24px，**自动收起 sidebar**（动画 180ms），主区获得 264px 让步空间，Workbench 继续跟手。
  - 收起时记录 `sidebarAutoCollapsed = true` 标记，区分用户主动收起和自动收起。
- 反向（拖小 Workbench 让出空间）：
  - 当 `window.innerWidth - workbench(W) ≥ 264 + 480` 重新成立、且 `sidebarAutoCollapsed === true`，**自动展开 sidebar**（动画 180ms）。
  - 用户在自动收起期间手动点 sidebar 切换按钮，则清除 `sidebarAutoCollapsed`，后续不再自动展开（尊重用户最近一次明示）。
- sidebar 自身的可拖拽本期不做。

## 状态机

```
closed ──toggle──▶ opening ──(transitionend)──▶ open
  ▲                                              │
  └──────────── closing ◀──toggle────────────────┘
```

- `opening` / `closing` 走 180ms `cubic-bezier(0.2, 0.8, 0.2, 1)` 宽度过渡。
- `open` 时拖拽不会触发状态变化，只更新宽度。
- 子视图的内部状态（如终端 buffer、浏览器 URL）必须在 `closed` 期间保持挂载（`visibility: hidden + width: 0`），不能 unmount——否则切回来要重连/重载，体验崩。
  - 例外：`FilesView` 可在收起 5 分钟后释放文件树缓存（按需重建成本低）。

## 持久化

写入 electron app userData 下的现有 settings store（与 sidebar workspace 同一个文件）：

| 字段 | 作用域 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- | --- |
| `workbench.open` | 全局 | boolean | `false` | 上次关闭窗口时面板是否展开 |
| `workbench.width` | 全局 | number | `420` | 展开宽度，单位 px，落库前夹到 [320, 900] |
| `workbench.activeTab[conversationId]` | 会话级 | `'goal' \| 'terminal' \| 'browser' \| 'files'` | `'terminal'` | 每个 conversation 独立记忆，缺省回落到 `'terminal'` |
| `workbench.sidebarAutoCollapsed` | 运行时 | boolean | `false` | 仅内存态，不持久化；窗口关闭即丢 |

- `open` 与 `width` 全局持久化：开多个会话时打开/关闭/宽度行为一致，符合"工具栏"心智。
- `activeTab` 会话级：每个会话上次看的是哪个 tab，跳回去能续上。schema 用 map 而不是给 conversation 表加列，迁移成本低。
- 读取时机：renderer 启动后从 main 拉一次，写入一个 Zustand/Context store；后续变更走防抖 250ms 的 IPC 写回。

## 子视图职责（仅约束接口，实现细节见各自专题文档）

### GoalView（迁移自 GoalPlanPanel）

GoalView 的产品定位、信息架构、状态交互与聊天流降噪规则，统一见 [`goal-right-status-panel.md`](./goal-right-status-panel.md)。本文只约束其 Workbench 容器行为。

- **全量迁移**：`GoalPlanPanel.tsx` 不再通过 `chat-side-panel` portal 注入，改成 Workbench 的 GoalView 内部组件。
- 删除 `ChatSurface.tsx` 里的 `<aside className="chat-side-panel" />` 槽位与 `setGoalSideEl` 相关逻辑；GoalPlanPanel 的 props 改成直接订阅同一个 store。
- 视觉上对齐 420px 默认宽度，并按 Goal 右侧状态区专题规范重新组织内部信息；不得继续把旧聊天卡片原样搬入右栏。
- 触发：当 conversation 出现 GoalPlan 时按上文"自动展开 + 自动选中 Goal tab"的规则进入。

### TerminalView

- **只读输出类**：复用现有 Bash 工具调用流，把每条 Bash tool result 的 stdout/stderr 串成可滚动的 buffer。
- 上方工具条：当前会话 cwd、清屏、复制全部。
- 不接受键盘输入；执行入口仍是 chat 输入框里的工具调用。
- 不引入独立 pty，不需要重新设计权限——完全沿用 PermissionGateStrip 的现有审查链路。

### BrowserView

- 内嵌 `webview`（Electron 标签）或 `iframe`，地址栏 + 前进/后退 + 刷新。
- **默认空白页**，不自动探测 dev server，不记忆上次 URL。用户每次手动输入或粘贴。
- 严格沙箱：不开启 `nodeIntegration`，外链在系统浏览器打开。

### FilesView

- 树状视图，**根目录跟随当前会话的 cwd**；切换 conversation 时刷新根。
- 仅展示，不在此处编辑；点击文件打开系统默认 app（或在主区 chat 中粘贴路径，二期决定）。
- 隐藏 `.git`、`node_modules`、`.DS_Store` 默认折叠。
- 收起 5 分钟后释放缓存（见状态机例外）。

## 视觉规范

沿用 Frost 设计语言（`design/visual/frost-implementation-guide.md`）：

- Panel 背景：`--surface-overlay`，与 main-panel 之间 1px `--border-subtle` 分隔。
- TabRail 背景：`--surface-base`；选中态用 `--accent-soft` 圆角胶囊；置灰 tab `opacity: 0.4` 且无 hover 反馈。
- 阴影：Panel 不投影，靠分隔线区分层次（避免与左侧 sidebar 视觉权重冲突）。
- 暗色/亮色主题各自走 token，不写死色值。

## 无障碍 / 国际化

- WorkbenchToggle、TabRail item、Resizer 都需要 `aria-label`，文案走 `@peer/i18n`：
  - `workbench.toggle.open` / `workbench.toggle.close`
  - `workbench.tab.goal` / `.terminal` / `.browser` / `.files`
  - `workbench.tab.goal.disabled`（tooltip）
  - `workbench.resizer`
- 屏幕阅读器顺序：sidebar → main-panel → workbench-panel（按 DOM 顺序自然读出，不需要 `aria-flowto`）。

## 落地拆解（交给 peer_agent 实现）

1. **Shell 改造**：`App.tsx` 的 `.app-layout` 改成三列 grid，引入 `useWorkbenchStore`（open/width/activeTab map/sidebarAutoCollapsed）。
2. **AppHeader 实装**：把 stub 改成真实 header，放 WorkbenchToggle，注册 `⌘\` 全局快捷键。
3. **WorkbenchPanel 组件**：TabRail + ViewSlot + Resizer 三件套，Resizer 走 pointer events 直接改 CSS 变量。
4. **GoalPlanPanel 全量迁移**：从 `ChatSurface.tsx` 的 `chat-side-panel` portal 注入改为 Workbench 的 GoalView；删除旧 `chat-side-panel` aside、`setGoalSideEl`、`sidePanelContainer` 相关代码。
5. **持久化通道**：main 进程加 `workbench:get` / `workbench:set` IPC，复用现有 settings 文件；activeTab 使用 map 存储。
6. **挤压策略**：实现 sidebar 自动收起/恢复的临界吸附逻辑，注意区分用户主动操作与自动操作。
7. **子视图占位**：TerminalView / BrowserView / FilesView 先各自给一个空骨架（带 loading 提示），后续单独排期填充。
8. **回归**：确认旧的 `chat-side-panel` 移除后没有残留样式/选择器；Goal 自动展开只在"无→有"瞬间触发一次。

## 已确认决策清单

| 编号 | 决策 |
| --- | --- |
| Q1 | GoalPlan 全量迁移到 Workbench，作为第一个 tab |
| Q1.1 | Goal tab 总是显示，无 Goal 时置灰 |
| Q1.2 | 新生成 GoalPlan 时自动展开 Workbench 并选中 Goal tab |
| Q1.3 | 置灰的 Goal tab 纯装饰，点击无反应 |
| Q1.4 | GoalPlanPanel 全量迁移，删除旧 chat-side-panel portal |
| Q2 | 不做"全屏 Workbench" |
| Q3 | FilesView 根目录跟随会话 cwd |
| Q4 | open / width 全局，activeTab 会话级 |
| Q4.1 | 同 Q4 |
| Q5 | TerminalView 只读，不开 pty |
| Q6 | Tab 顺序：Goal / 终端 / 浏览器 / 文件 / 产物 |
| Q7 | 不为 tab 切换加快捷键，仅保留 `⌘\` |
| Q8 | BrowserView 默认空白页 |
| Q9 / Q9.1 | 主区被挤超过临界时自动收 sidebar，反向自动恢复，可被用户明示覆盖 |
| Q10 | 文件区 master-detail：点文件走 `openFileInPlace`，不切一级 tab（2026-09-21） |
| Q11 | `documents` tab 重定位为「会话产物」聚合；detail 组件唯一宿主是 FilesPane（2026-09-21） |
