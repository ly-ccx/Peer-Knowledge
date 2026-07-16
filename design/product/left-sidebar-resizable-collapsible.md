# 左侧栏可拖拽 / 可收起设计规范

创建时间：2026-06-26
最后更新：2026-06-26

## 背景

Peer Agent 的右侧工作台（Workbench Panel）已经具备「可拖拽改宽 + 临界自动收起 + 顶栏 toggle 常驻入口」一整套交互（见 `right-workbench-panel.md`）。但**左侧栏**还是一块固定资产：

- 宽度由 `--za-sidebar-width: 264px`（`tokens.css`）写死，用户**不能拖**。
- 收起态 `data-sidebar-collapsed='true'` 已经存在，但目前**只被右侧拖拽逻辑被动触发**（主区被挤太窄时自动收左栏），用户自己**既不能主动收起、也没有展开入口**。

本期把右侧那套成熟模式**镜像到左侧**：左栏可拖拽改宽、拖到阈值以下松手自动收起、主区顶栏左侧常驻一个与右侧对称的 toggle 按钮可展开/收起。难点不在交互本身，而在于**与右侧已有的「挤压自动收左栏」逻辑共用同一个 collapsed 状态且不互相打架**。

本文档约定交互、尺寸、状态与持久化规则，交由代码仓 `peer_agent` 的 `apps/desktop/renderer` 落地。

## 现状速览

- 主布局：`apps/desktop/renderer/src/App.tsx` → `.app-shell` → `.app-layout`（CSS grid，左栏 / 主区 `1fr` / 右栏 workbench）。
- 左栏宽度由 `--za-sidebar-width: 264px`（`tokens.css`）控制——是 CSS 变量，但全局固定值，无拖拽、无覆盖。
- 收起态：`.app-layout[data-sidebar-collapsed='true']` 会把左栏那一列压成 `0`、隐藏 `.app-sidebar`；非全屏时主区顶栏自动 `padding-left: 78px` 给 macOS 交通灯让位（见 `chat.css` 中 `.chat-header` 收起态规则）。
- 该 collapsed 状态目前由 `WorkbenchContext` 持有，配套一个 `sidebarAutoCollapsed` 标记，用来区分「右侧挤压自动收的」与「用户主动收的」，从而决定主区变宽后是否自动恢复左栏。
- 右侧 toggle（`WorkbenchToggle`）是 28×28 图标按钮，挂在 `ChatHeader` 的 `.chat-header-right`；右栏 `WorkbenchPanel` 的 Resizer 走 pointer events 直接改 CSS 变量、松手才落 state、宽度持久化到 settings 文件、支持双击重置与键盘箭头微调。**左栏整套对齐这个范式即可。**

## 命名

- 左栏拖拽分隔条叫 **Sidebar Resizer**（`.sidebar-resizer`）。
- 主区顶栏左侧的展开/收起按钮叫 **SidebarToggle**（镜像 `WorkbenchToggle`）。
- 拖拽可被覆盖的动态宽度变量叫 **`--za-sidebar-current-width`**（与写死的基准 token `--za-sidebar-width` 区分）。

## 尺寸与阈值（已确认）

| 项 | 值 | 说明 |
| --- | --- | --- |
| 默认宽度 | **264px** | 保持现状 token 值，双击 Resizer 重置回这里 |
| 可拖最小（展开态） | **220px** | 再窄会话标题会挤 |
| 可拖最大 | **400px** | 左栏只是索引区，不宜过宽 |
| 自动收起阈值 | **拖到 < 180px 松手即收起** | 跨过 220 后进入「阻尼区」，继续拖过约 40px 触发收起 |

阻尼区行为：用户把宽度拖到 220px 以下时，不立即收起，而是进入带阻力的「预收起」区间（视觉上可给轻微阴影/降透明提示）。松手时判定：落点 ≥ 180px → 吸附回 220px（最小展开宽度）；落点 < 180px → 收起。这与右侧 workbench 的阻尼吸附是同一思路，方向相反。

## 入口与触发

### SidebarToggle 按钮

- 位置：主区顶栏 `ChatHeader` 的 `.chat-header-left` **最左侧**，与右侧 `.chat-header-right` 里的 WorkbenchToggle 视觉对称。
- 视觉：与 WorkbenchToggle 同规格的 28×28 图标按钮，用「左侧面板」线性图标（两栏面板缩略 + 左栏高亮），方向与右侧镜像。
- **显示策略：常驻对称**（已确认）。展开态、收起态都显示，图标随状态变：
  - 展开态：图标表示「收起左栏」，`aria-pressed="true"`。
  - 收起态：图标表示「展开左栏」，`aria-pressed="false"`。
- 区域属性：`-webkit-app-region: no-drag`（ChatHeader 整体是 drag 区，按钮必须排除）。
- 快捷键：**`⌘B`**（与 VS Code 侧边栏一致；右侧用的是 `⌘\`，两者不冲突）。若落地时发现 `⌘B` 已被占用，停下来与需求方确认换键。
- Tooltip：「显示/隐藏侧边栏 (⌘B)」。

### 交通灯让位带来的位置位移（已知约束）

收起后主区顶到窗口最左，**非全屏时** `ChatHeader` 会自动 `padding-left: 78px` 给 macOS 红绿灯让位。因此收起态下 SidebarToggle 会落在红绿灯右侧（约 78px 处），比展开态往右挪一截——这是系统交通灯决定的，不可避免，属预期行为。全屏时无让位、按钮回到最左。

## 状态与持久化

新增两个字段，复用现有 settings IPC 通道（与 workbench 同一套 `get/set`）：

| 字段 | 作用域 | 默认 | 说明 |
| --- | --- | --- | --- |
| `sidebarWidth` | 全局 | 264 | 展开态宽度，拖拽松手时写入；收起不改它（用于展开时恢复） |
| `sidebarOpen` | 全局 | true | 用户主动开合意图 |

实现上**复用 / 收敛进现有 `WorkbenchContext`**（它已持有 sidebar collapsed 与 `sidebarAutoCollapsed`），不另起一套 store，避免两个 source of truth。`--za-sidebar-current-width` 在展开态绑定 `sidebarWidth`，拖拽中直接改 CSS 变量、不走 React state，松手才落 state 并持久化。

## 三种收起来源的协调（核心难点）

加了拖拽 + toggle 后，「收起」有三个触发来源，必须共用同一个 `collapsed` 状态，但要能区分**主动**与**自动**：

| 来源 | 性质 | 是否可被自动恢复 |
| --- | --- | --- |
| 用户点 SidebarToggle | 主动 | 否——用户明示意图，主区变宽也不自动展开 |
| 用户把左栏拖到 < 180px 松手 | 主动 | 否——同上，视为用户明示收起 |
| 右侧拖拽把主区挤到临界宽度以下 | 自动 | 是——主区恢复够宽时自动把左栏展开回去 |

协调规则：

1. 沿用现有 `sidebarAutoCollapsed` 标记。**自动收起**时置 `true`；**主动收起**（toggle 或拖窄）时置 `false`。
2. 右侧挤压逻辑只在 `sidebarAutoCollapsed === true` 时才有权自动恢复左栏；用户一旦主动收起（标记为 `false`），右侧不得擅自展开。
3. 用户主动展开（点 toggle）时清掉 `sidebarAutoCollapsed`，回到正常受控状态。
4. 避免回弹冲突：自动恢复用「滞回（hysteresis）」——收起阈值与恢复阈值留出间隔（如主区 < 480 收、> 520 才恢复），防止在临界点反复横跳。

## 视觉与过渡

- `.sidebar-resizer`：贴在左栏右缘的细拖拽带（命中区 ~6–8px，视觉 1px 分隔线），hover/active 时主色高亮，`cursor: col-resize`。
- 收起/展开过渡：grid 列宽 `width` 走 `transition`（约 160–200ms ease），与右侧 workbench 收展节奏一致；拖拽进行中关闭 transition 防止跟手延迟。
- 颜色一律走 token，不写死色值。

## 无障碍 / 国际化

- SidebarToggle、Sidebar Resizer 都需要 `aria-label`，文案走 `@peer/i18n`：
  - `sidebar.toggle.open` / `sidebar.toggle.close`
  - `sidebar.resizer`
- Resizer 作为分隔器应有 `role="separator"` + `aria-orientation="vertical"`，并支持键盘箭头微调宽度（与右侧 workbench Resizer 一致）。

## 落地拆解（交给 peer_agent 实现）

1. **状态与持久化**：在 `WorkbenchContext` 收敛 `sidebarWidth` / `sidebarOpen`，复用现有 settings `get/set` IPC，理清与 `sidebarAutoCollapsed` 的关系。
2. **CSS 布局改造**：`sidebar.css` 把第 1 列宽度从写死 token 改为可被覆盖的 `--za-sidebar-current-width`，新增 `.sidebar-resizer` 样式与收起态过渡。
3. **Sidebar Resizer**：pointer events 直接改 CSS 变量、松手落 state、双击重置 264、键盘箭头微调、拖到 < 180 阻尼区自动收起。
4. **SidebarToggle**：镜像 WorkbenchToggle，挂到 `ChatHeader` 的 `.chat-header-left` 最左，常驻对称、图标随状态变，注册 `⌘B`。
5. **三来源协调**：统一 `data-sidebar-collapsed` 状态，区分主动 / 自动，加滞回防回弹，确保不破坏右侧现有挤压逻辑。
6. **回归**：typecheck + 构建；自查收起态交通灯让位正常、右侧挤压逻辑未被破坏、宽度/开合持久化生效。

## 已确认决策清单

| 编号 | 决策 |
| --- | --- |
| L1 | 默认 264 / 最小 220 / 最大 400 / 收起阈值 180 |
| L2 | SidebarToggle 嵌入主区顶栏，与右侧 toggle 对称（方案 B） |
| L3 | SidebarToggle 常驻对称，图标随状态变（方案 ①） |
| L4 | 快捷键 `⌘B`（右侧为 `⌘\`，互不冲突） |
| L5 | 三种收起来源共用 collapsed 状态，区分主动 / 自动，自动恢复仅作用于自动收起 |
| L6 | `sidebarWidth` / `sidebarOpen` 全局持久化，复用现有 settings IPC，收敛进 WorkbenchContext |
