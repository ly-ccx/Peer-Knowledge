# Peer Agent 三栏毛玻璃表面架构优化

> 创建时间：2026-07-31
> 最后更新：2026-07-31
> 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`
> 分析基线：`33403c483a3a1d2b2fefa006fe00c9fbbfcfa078`
> 文档性质：现状代码地图、问题诊断与可实施迁移方案；本文不直接修改产品代码。

## 摘要

Peer Agent 的桌面主界面由 Sidebar、主会话和 Workbench 三列组成。macOS 窗口已经启用 Electron 原生透明与 vibrancy，渲染层也具备首帧实色兜底、成功启动后放开文档透明、非 macOS 与“降低透明度”回退等基础能力。

当前主要问题不在于“有没有毛玻璃”，而在于**同一层基础 Chrome 材质由三个直接子列重复生产**：`.app-sidebar`、`.main-panel` 和 `.workbench-panel` 分别设置 `--glass-chrome`、`backdrop-filter` 与降级逻辑，而 `.app-layout` 只负责 Grid。结果是材质来源不唯一，边界、阴影、圆角和拖拽反馈不断以局部补丁拼接，容易出现色差、重复模糊、合成开销和响应式回归。

建议把 `.app-layout` 定义为桌面三栏模式下唯一的基础 Chrome 材质所有者：

- `.app-layout`：统一提供 `--glass-chrome`、blur、饱和度和降低透明度回退；
- `.app-sidebar`、`.main-panel`、`.workbench-panel`：默认透明，不再各自生产玻璃，只负责布局、宽度、overflow 和交互；
- `.thread` 与 Workbench 内部 ViewSlot/卡片：负责实色内容纸面、圆角和可读性；
- `.main-panel`：统一表达主会话左右镜像阴影；
- Sidebar/Workbench resizer：用独立反馈层表达 hover、active、damping，不再借列边框承担视觉反馈；
- 窄屏 overlay：作为独立模式显式恢复面板自身玻璃材质，不能照搬桌面三栏的透明子列规则。

核心原则是：**统一的是同层基础材质，不是把所有组件样式都塞进 `.app-layout`。**

---

## 一、范围与非目标

### 1.1 本文覆盖

1. Electron `BrowserWindow` 的透明、vibrancy、主题和首帧显示链路；
2. `index.html`、`main.tsx`、`base.css` 的文档透明与实色回退；
3. `.app-layout` 三栏 DOM、CSS Grid、开合状态和响应式模式；
4. Sidebar、Main、Thread、Workbench 的背景、blur、圆角、边界和阴影职责；
5. 左右拖拽宽度、自动收起、DOM 快路径和交互反馈；
6. 目标职责模型、迁移步骤、风险和验收清单。

### 1.2 非目标

- 不统一所有内容卡片的颜色和圆角；
- 不改变 Electron 主窗口的产品尺寸、最小尺寸或原生交通灯行为；
- 不改动聊天消息、Markdown、附件等业务组件；
- 不取消非 macOS 与“降低透明度”的实色可用性；
- 不以增加更多边框、遮罩或局部色块来掩盖材质链问题；
- 本文不包含产品代码改动。

---

## 二、源文件地图

| 层级 | 文件 | 关键符号/选择器 | 当前职责 |
|---|---|---|---|
| Electron 窗口 | `apps/desktop/electron/main/main.mjs` | `createWindow()` | 创建透明窗口；macOS 设置 vibrancy；同步原生主题；首帧延迟显示 |
| HTML 首帧 | `apps/desktop/index.html` | 内联 `<style>`、`data-boot-shell` | CSS bundle 前提供浅/深实色底；按 `data-vibrancy` 放开透明 |
| Renderer 入口 | `apps/desktop/renderer/src/main.tsx` | `document.documentElement.dataset.vibrancy` | macOS bootstrap 成功后打开透明链路 |
| 文档基础层 | `apps/desktop/renderer/src/styles/base.css` | `html`、`body`、`#root`、`[data-vibrancy]` | 默认实色；macOS 成功启动后透明；降低透明度回退 |
| 主题 Token | `apps/desktop/renderer/src/styles/tokens.css` | `--glass-chrome`、`--blur-chrome`、`--chrome-canvas` | 材质色、模糊、边缘高光与内容画布 Token |
| React 根结构 | `apps/desktop/renderer/src/App.tsx` | `.app-shell`、`.app-page-layer`、`.app-layout` | 页面层、三栏结构、开合状态投影 |
| Shell/主区 | `apps/desktop/renderer/src/styles/shell.css` | `.app-shell`、`.main-panel`、`.thread` | 页面层、主列、内容纸面与全屏规则 |
| Sidebar | `apps/desktop/renderer/src/styles/sidebar.css` | `.app-layout`、`.app-sidebar`、`.sidebar-resizer` | Grid、左栏玻璃、宽度、阴影和拖拽反馈 |
| Workbench | `apps/desktop/renderer/src/styles/workbench.css` | `.workbench-panel`、`.workbench-resizer` | 右栏玻璃、阴影、开合、拖拽反馈和响应式覆盖 |
| 左栏拖拽 | `apps/desktop/renderer/src/workbench/SidebarResizer.tsx` | `onPointerDown`、`data-active`、`data-damping` | 左栏拖拽 DOM 快路径、阻尼和松手提交 |
| 右栏拖拽 | `apps/desktop/renderer/src/workbench/WorkbenchPanel.tsx` | `onPointerDown`、`onMove`、`onUp` | 右栏宽度快路径、自动收左栏、活动反馈 |
| 状态源 | `apps/desktop/renderer/src/workbench/WorkbenchContext.tsx` | `width`、`sidebarWidth`、`sidebarOpen`、持久化 | 宽度与开合的 React 权威状态、CSS 变量同步和设置持久化 |

---

## 三、窗口与文档透明链路

### 3.1 Electron 窗口层

`apps/desktop/electron/main/main.mjs` 的 `createWindow()` 在 macOS 上建立原生材质能力：

- `backgroundColor: '#00000000'`；
- `transparent: true`；
- `vibrancy: 'sidebar'`；
- `visualEffectState: 'active'`；
- `titleBarStyle: 'hiddenInset'`；
- `show: false`，等待 `ready-to-show` 再显示，降低冷启动露黑概率。

非 macOS 使用实色窗口背景，避免 Windows/Linux 透明窗体的闪黑或合成异常。`nativeTheme.themeSource` 与应用 appearance mode 同步，保证原生 vibrancy 与 Renderer 主题方向一致。

这层是**系统材质能力来源**，但不是组件表面的最终视觉定义。Electron 只提供“可透出的原生背景”，Renderer 仍需决定哪些区域允许透出、叠加多少 tint、哪些内容保持实色。

### 3.2 HTML 首帧兜底

`apps/desktop/index.html` 在 CSS bundle 注入前用未分层内联样式给 `html/body/#root` 提供浅色 `#F4F6F9` 或深色 `#16191D`。这是必要的时序兜底：

- React 或 CSS bootstrap 尚未完成时不能暴露透明黑底；
- bootstrap 失败时仍有可读的启动壳；
- `data-vibrancy='true'` 出现后，同一未分层样式再把文档层放开为透明。

内联规则不能只依赖 `base.css` 替代，因为未分层样式在 cascade layer 中优先于 `@layer base`，而且它必须在 bundle 到达前工作。

### 3.3 Renderer 启动标记

`apps/desktop/renderer/src/main.tsx` 在 macOS User-Agent 且模块正常执行到 React 挂载前设置：

```ts
document.documentElement.dataset.vibrancy = 'true';
```

它的语义不是“用户偏好”，而是**当前 Renderer 已具备放开透明底的启动条件**。标记不存在时，文档层维持实色兜底。

后续可以考虑把平台事实通过 preload 明确暴露，避免 User-Agent 判断；但迁移时不应先删除现有标记，否则会破坏已验证的启动链路。

### 3.4 CSS 文档层

`apps/desktop/renderer/src/styles/base.css` 默认让 `body`、`html`、`#root` 使用 `--za-app-bg` / `--chrome-canvas` 实色；仅当 `html[data-vibrancy='true']` 时改为透明。`prefers-reduced-transparency: reduce` 下恢复实色。

因此完整链路是：

```text
BrowserWindow 原生透明与 vibrancy
  → index.html 首帧实色兜底
  → main.tsx 成功启动后写 data-vibrancy
  → index.html 未分层规则放开透明
  → base.css 正常运行态放开透明
  → app-layout / 组件表面叠加材质 tint 与 blur
```

### 3.5 哪些重复必须保留

`index.html` 与 `base.css` 都存在实色/透明规则，看似重复，但职责不同：

- `index.html`：bundle 前、bootstrap 失败路径；
- `base.css`：应用运行态、主题 Token 与可访问性回退。

这属于**必要的防故障重复**，不能与三列组件重复生产玻璃混为一谈。

---

## 四、三栏 DOM 与布局状态

### 4.1 DOM 主干

`apps/desktop/renderer/src/App.tsx` 的聊天页面主干可概括为：

```text
main.app-shell
└── div.app-page-layer.app-chat-page
    └── WorkbenchProvider
        └── div.app-layout
            ├── Sidebar
            │   └── .app-sidebar
            ├── main.main-panel
            │   └── section.thread.thread-has-header
            │       └── ChatSurface
            └── WorkbenchPanel
                └── aside.workbench-panel
```

设置页与聊天页使用 `.app-page-layer` 叠放。聊天工作区保持挂载，非活动页只切换 `visibility` 和 `pointer-events`，避免返回聊天时重建长会话 DOM、Markdown 和测量缓存。

### 4.2 Grid

`.app-layout` 当前定义在 `styles/sidebar.css`：

```css
grid-template-columns:
  var(--za-sidebar-current-width)
  minmax(0, 1fr)
  var(--za-workbench-width);
```

根节点状态控制列宽：

- `data-sidebar-collapsed='true'`：左列变为 `0px`；
- `data-workbench-open='true'`：右列使用 `--za-workbench-width`；
- Workbench 关闭时右列为 `0px`。

### 4.3 响应式模式

窄屏媒体查询会把 Sidebar 和 Workbench 改成绝对定位 overlay，主列保持全宽。这意味着桌面三栏与窄屏 overlay 不是同一种表面关系：

- 桌面三栏：三个直接子列共享同一个基础 Chrome 平面；
- 窄屏 overlay：侧栏/工作台脱离 Grid，浮在主内容上，必须拥有独立可读的材质和阴影。

因此“直接子列透明”只能作为桌面默认规则；overlay modifier 必须显式恢复独立背景、blur 和投影，不能简单全局删除 Sidebar/Workbench 的所有材质声明。

---

## 五、当前表面职责与问题

### 5.1 Token

`styles/tokens.css` 当前关键 Token：

| Token | 浅色示例 | 深色示例 | 语义 |
|---|---:|---:|---|
| `--glass-chrome` | `hsla(215,16%,98%,0.52)` | `hsla(220,22%,12%,0.48)` | Chrome 半透明 tint |
| `--blur-chrome` | `24px` | `24px` | Chrome 模糊半径 |
| `--glass-edge-highlight` | 顶部 inset 高光 | 较弱顶部 inset 高光 | 玻璃边缘高光 |
| `--chrome-canvas` | `#FAFBFC` | `#11141A` | 可读内容纸面 |
| `--za-sidebar-bg` | `#F3F5F8` | `#181C24` | 降低透明度下的 Sidebar 实色 |

Token 本身已能表达“玻璃 Chrome”和“实色内容纸面”的区分，问题主要出在所有权。

### 5.2 当前所有权

| 选择器 | 背景/模糊 | 圆角/边界 | 当前问题 |
|---|---|---|---|
| `.app-layout` | 无材质，只做 Grid | 无 | 未承担同层共享材质 |
| `.app-sidebar` | `--glass-chrome` + 24px blur | 透明右边框、顶部高光 | 与 Main/Workbench 重复生产玻璃 |
| `.main-panel` | `--glass-chrome` + 24px blur | 直角 | 与两栏重复；降级逻辑重复 |
| `.thread` | `--chrome-canvas` | `--radius-lg` | 职责方向正确：内容纸面 |
| `.workbench-panel` | `--glass-chrome` + 24px blur | 透明左边框、顶部高光 | 与另两列重复；关闭/overlay 规则复杂 |
| Sidebar `::after` | 8px 轻阴影 | 右缘 | 主会话边界效果写在左栏 |
| Workbench `::before` | 8px 镜像轻阴影 | 左缘 | 主会话边界效果写在右栏 |

### 5.3 根因

真实问题可以重写为：

> 基础 Chrome 材质没有唯一所有者，导致相邻列分别执行相同 tint 和 backdrop-filter；内容层级、边界表达和交互反馈被迫分散到多个组件补丁中。

### 5.4 具体风险

#### 风险 A：重复 blur 与色差

三个相邻元素都设置 `backdrop-filter`。即使视觉近似，相邻合成层仍可能因底层内容、GPU tile、透明度和层级不同出现边界色差。

#### 风险 B：修改需要多点同步

调整 `--glass-chrome` 使用方式、saturate、降低透明度回退时，需同时核对 `sidebar.css`、`shell.css`、`workbench.css`。

#### 风险 C：边界效果职责倒置

主会话“浮在左右 Chrome 上方”的阴影，应由主会话边界统一表达；当前却由 Sidebar 和 Workbench 各画一半。Workbench 关闭、响应式 overlay 或组件重构时容易漏掉一侧。

#### 风险 D：视觉与拖拽交互耦合

透明 `border-left/right` 被用作 resizer hover/active 的颜色载体。它虽避免布局抖动，但把列边界和交互反馈绑在一起，导致“去掉常态边框”容易误伤拖拽反馈。

#### 风险 E：响应式规则被误删

如果直接把 Sidebar/Workbench 背景全部设为透明，窄屏绝对定位 overlay 会失去独立承载面，内容透到主区，出现对比度和层级问题。

#### 风险 F：合成与性能

多个全高 `backdrop-filter` 合成层会增加 GPU 合成面积。拖拽期间 CSS Grid 宽度持续变化，重复的全高模糊层也会提高重绘/合成风险。

---

## 六、拖拽与状态链路

### 6.1 权威状态源

`WorkbenchContext.tsx` 持有：

- Workbench `width`、当前会话开合状态、活动 Tab；
- `sidebarWidth`、`sidebarOpen`、`sidebarAutoCollapsed`；
- 设置持久化和 CSS 变量同步。

主要尺寸约束：

| 项目 | 数值/约束 |
|---|---|
| Workbench 默认宽度 | `600px` |
| Workbench 范围 | `320px`–`900px`，且不超过约 `55vw` |
| 主区拖拽最低宽度 | `480px` |
| 左栏恢复滞回阈值 | 主区达到 `520px` |
| Sidebar 默认宽度 | `264px` |
| Sidebar 范围 | `220px`–`400px` |
| Sidebar 收起阻尼阈值 | 约 `180px` |
| 设置持久化 | 约 `250ms` 防抖 |

### 6.2 性能快路径

左右 resizer 都采用相同的性能策略：

1. `pointerdown` 记录起点和起始宽度；
2. `pointermove` 直接写根元素 CSS 变量；
3. 不在每一帧调用 React `setState`；
4. `pointerup` 才把最终宽度提交到 Context；
5. Context 再负责持久化和稳定态同步。

这一策略应保留。材质迁移不应把宽度变更改成每帧 React render。

### 6.3 自动收起

Workbench 向左扩张时，会计算当前主区剩余宽度；空间不足会自动收起 Sidebar。缩回 Workbench 后，只有主区恢复到更高阈值才恢复 Sidebar，形成滞回区，避免阈值附近横跳。

### 6.4 交互反馈

- Sidebar resizer：`data-active`、`data-damping`，常态透明右边框，hover/active 使用 accent，阻尼使用警告色；
- Workbench resizer：`data-active`，常态透明左边框，hover/focus/active 使用 accent；
- resizer 命中区约 6px，位于列内侧。

目标架构应保留状态语义，但把可见线画在 resizer 自己的伪元素上，而不是改变列容器 border color。

---

## 七、目标架构

### 7.1 单一材质来源

桌面三栏模式下：

```text
BrowserWindow vibrancy
└── document transparent
    └── .app-layout                  ← 唯一基础 glass-chrome + blur
        ├── .app-sidebar             ← transparent，布局/交互
        ├── .main-panel              ← transparent，布局/阴影
        │   └── .thread              ← chrome-canvas + radius
        └── .workbench-panel         ← transparent，布局/交互
            └── ViewSlot / cards     ← 各自内容表面
```

### 7.2 职责矩阵

| 层 | 应负责 | 不应负责 |
|---|---|---|
| BrowserWindow | 原生 vibrancy、透明窗口、平台背景、首帧显示 | 组件圆角、栏间边界 |
| 文档层 | 启动兜底、运行态透明、可访问性回退 | 三栏局部材质 |
| `.app-layout` | 基础 Chrome tint、blur、saturate、桌面模式统一降级 | 内容纸面圆角、拖拽状态 |
| 直接子列 | Grid item、宽度、overflow、层级、拖拽命中 | 重复 backdrop-filter |
| `.main-panel` | 主列布局、左右镜像阴影 | 内容实色纸面、外层圆角 |
| `.thread` | 可读实色背景、圆角、内部裁切 | 系统 vibrancy |
| Workbench ViewSlot/卡片 | 具体内容背景、圆角、边框 | 整列基础玻璃 |
| resizer | hover/active/damping 反馈和命中区 | 常态列分隔线 |

### 7.3 建议 CSS 形态

示意而非最终补丁：

```css
.app-layout {
  background: var(--glass-chrome, var(--za-app-bg));
  -webkit-backdrop-filter: blur(var(--blur-chrome, 24px)) saturate(1.2);
  backdrop-filter: blur(var(--blur-chrome, 24px)) saturate(1.2);
}

.app-sidebar,
.main-panel,
.workbench-panel {
  background: transparent;
  -webkit-backdrop-filter: none;
  backdrop-filter: none;
}

.thread {
  background: var(--chrome-canvas, var(--za-app-bg));
  border-radius: var(--radius-lg);
}

@media (prefers-reduced-transparency: reduce) {
  .app-layout {
    background: var(--za-app-bg);
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }
}
```

### 7.4 阴影所有权

Sidebar 右缘和 Workbench 左缘的镜像阴影，本质上描述的是主会话与两侧 Chrome 的层级。建议由 `.main-panel` 统一表达：

- 方案 A：一个 `box-shadow` 同时包含左右两组阴影；
- 方案 B：`.main-panel::before` / `::after` 分别绘制左右阴影。

选择标准：

- 阴影不应占用布局宽度；
- 不应遮挡左右 resizer；
- Workbench 关闭时右阴影应随边界自然消失或被状态规则禁用；
- 窄屏 overlay 下改由 overlay 自己投影，不沿用桌面主列阴影。

推荐优先使用主列伪元素，因为方向、范围和状态更容易独立控制。

### 7.5 Resizer 反馈层

建议常态列容器不再保留透明边框。把反馈移到命中区伪元素：

```css
.sidebar-resizer::after,
.workbench-resizer::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  opacity: 0;
  background: var(--za-accent);
}

/* hover / focus / data-active 时 opacity: 1；damping 时切警告色。 */
```

这样列容器材质连续，交互反馈仍明确，且不会因 border 开关导致盒模型变化。

### 7.6 Overlay 模式

窄屏模式应明确建立 modifier，例如媒体查询下：

```css
@media (max-width: ...) {
  .app-sidebar,
  .workbench-panel--open {
    background: var(--glass-chrome);
    backdrop-filter: blur(var(--blur-chrome)) saturate(1.2);
    box-shadow: var(--overlay-shadow);
  }
}
```

原因是 overlay 已脱离 `.app-layout` 的平面关系，需要独立承载。它不是桌面规则的例外补丁，而是另一种明确布局模式。

---

## 八、分阶段迁移方案

### 阶段 0：建立视觉与性能基线

在改代码前保存：

1. macOS 浅色/深色三栏截图；
2. Sidebar 收起、Workbench 关闭、二者同时打开截图；
3. 窄屏 overlay 截图；
4. “降低透明度”截图；
5. 左右拖拽录屏和边界反馈；
6. DevTools Layers/Performance 中全高 backdrop-filter 层数量与拖拽帧表现。

回滚点：无代码改动。

### 阶段 1：把桌面基础材质上移到 `.app-layout`

1. 在 `.app-layout` 添加 `--glass-chrome`、blur、saturate；
2. 在桌面模式下将三个直接子列改为透明并取消自身 blur；
3. 将降低透明度的基础 Chrome 回退收敛到 `.app-layout`；
4. 保留 `.thread` 的 `--chrome-canvas` 和圆角；
5. 暂时保留现有阴影和 resizer border，降低一次迁移的变量数量。

验收：三列色调一致；内容纸面可读；全高 blur 层由三份降为一份。

回滚点：恢复三个子列原背景/blur，移除 `.app-layout` 材质。

### 阶段 2：统一主会话边界阴影

1. 把 Sidebar `::after` 和 Workbench `::before` 的镜像阴影迁移到 `.main-panel`；
2. 确保 Workbench 关闭、Sidebar 收起时边界正确；
3. 删除两栏中的旧阴影伪元素；
4. 不改 resizer 命中区。

验收：左右阴影强度、范围一致；关闭任一栏无残影；拖拽不被遮挡。

回滚点：恢复两栏伪元素，删除主列阴影。

### 阶段 3：解耦拖拽反馈与列边框

1. 给两个 resizer 增加独立 `::after` 反馈线；
2. 复用现有 `data-active`、`data-damping` 和 focus 状态；
3. 删除列容器透明 border 和 `border-color` transition；
4. 验证 pointer 拖出 6px 命中区后 active 反馈持续；
5. 保持 pointermove 直接写 CSS 变量的性能快路径。

验收：常态无硬分隔线；交互态反馈完整；布局不跳动；宽度算法不变。

回滚点：恢复透明 border 与 `:has()` 变色规则。

### 阶段 4：显式治理 overlay 与降级

1. 为窄屏 Sidebar/Workbench overlay 恢复独立玻璃材质和投影；
2. 确认 `prefers-reduced-transparency` 下 overlay 使用实色；
3. 检查设置页、全屏、窗口恢复和主题切换；
4. 删除已无用途的重复注释与旧回退规则；
5. 增加结构/样式回归测试或截图测试。

验收：桌面共享材质与窄屏独立 overlay 均成立，没有透明 overlay 或双 blur。

回滚点：保留阶段 1–3，只恢复旧响应式面板材质规则。

---

## 九、验收清单

### 9.1 结构

- [ ] `.app-layout` 是桌面三栏唯一的基础 `--glass-chrome` / `backdrop-filter` 所有者；
- [ ] `.app-sidebar`、`.main-panel`、`.workbench-panel` 在桌面模式不再重复 blur；
- [ ] `.thread` 保留 `--chrome-canvas` 实色背景与 `--radius-lg` 圆角；
- [ ] Workbench 内部内容视图自行承担内容表面，不依赖整列实色；
- [ ] 主会话左右阴影由 `.main-panel` 单一来源表达；
- [ ] resizer 反馈不再依赖列容器 border。

### 9.2 视觉

- [ ] 浅色/深色三列基础材质连续，无接缝色差；
- [ ] Thread 圆角清晰，四角露出的是统一玻璃底；
- [ ] 左右阴影方向、范围和强度镜像一致；
- [ ] Sidebar/Workbench 常态无硬分隔线；
- [ ] hover、focus、active、damping 反馈仍清楚；
- [ ] Sidebar 收起或 Workbench 关闭后无残影；
- [ ] 窄屏 overlay 有独立承载和阴影，不透明穿透主内容。

### 9.3 平台与故障路径

- [ ] macOS 正常启动后桌面背景可透入；
- [ ] CSS/React bootstrap 失败时仍显示实色启动壳；
- [ ] 非 macOS 保持实色，不出现透明黑屏；
- [ ] “降低透明度”开启后基础 Chrome 和 overlay 均回退实色；
- [ ] 浅色/深色切换时 Electron `nativeTheme` 与 Renderer 一致；
- [ ] 全屏时交通灯留白和页面尺寸不回归。

### 9.4 交互与性能

- [ ] Sidebar 宽度范围、阻尼收起阈值和双击/键盘行为不变；
- [ ] Workbench 宽度范围、55vw 限制和主区 480px 下限不变；
- [ ] Workbench 扩张自动收 Sidebar、缩回后 520px 滞回恢复行为不变；
- [ ] pointermove 仍直接写 CSS 变量，不改为每帧 React setState；
- [ ] pointerup 后 Context 权威状态和持久化值一致；
- [ ] DevTools 中全高 blur 合成层数量减少；
- [ ] 连续拖拽无明显掉帧、闪烁或材质跳变。

### 9.5 自动检查

建议至少运行：

```bash
cd /Users/liangyin/Documents/DEV/github/peer_agent
pnpm --filter @peer-agent/desktop typecheck
git diff --check

cd apps/desktop
node --test \
  renderer/src/workbench/workbenchOpenState.test.ts \
  renderer/src/workbench/workbenchTabState.test.ts \
  renderer/src/workbench/workbenchBrowserVisibility.test.ts
```

如果项目建立视觉回归能力，应补充浅/深色、三栏开合、overlay 和降低透明度的截图基线。

---

## 十、实施约束与代码审查规则

### 10.1 必须遵守

1. 先迁移材质所有权，再删除旧组件规则；
2. 每一阶段独立截图和拖拽验收，不把材质、阴影、resizer、响应式一次改完；
3. 不删除 `index.html` 首帧兜底；
4. 不删除 `data-vibrancy` 链路，除非 preload 平台契约已完成替代并覆盖失败路径；
5. 不改变拖拽 DOM 快路径和阈值算法；
6. Overlay 模式必须单独检查，不能只验收宽屏三栏。

### 10.2 Code Review 检查问题

- 这条 `backdrop-filter` 是基础材质还是独立浮层？
- 如果是基础材质，为什么不在 `.app-layout`？
- 这个圆角属于列容器还是内容纸面？
- 这个阴影描述的是哪个层压在哪个层上？所有权是否写在正确一侧？
- 这条 border 是常态视觉边界还是交互反馈？能否由 resizer 自身表达？
- 桌面共享材质规则在 overlay 模式下是否仍成立？
- 降低透明度、非 macOS 和启动失败路径是否有明确回退？

---

## 十一、决策结论

1. **同意**把 `.app-layout` 设为桌面三栏基础毛玻璃的单一来源；
2. **同意**直接子列默认透明，只保留布局和交互职责；
3. **同意**把实色、圆角和内部裁切下沉到 `.thread` 与 Workbench 内容表面；
4. **同意**主会话左右阴影由 `.main-panel` 统一表达；
5. **同意**resizer 反馈与列边框解耦；
6. **保留**`index.html` 与 `base.css` 的双重启动/运行态兜底；
7. **保留**非 macOS 和降低透明度的实色回退；
8. **要求**窄屏 overlay 作为独立表面模式治理，不能机械继承桌面透明子列规则。

目标不是减少 CSS 行数，而是让每一层只有一个明确的视觉事实来源：

```text
系统材质归 BrowserWindow
启动安全归 index/base
三栏基础玻璃归 app-layout
列布局与交互归直接子列
主会话层级归 main-panel
内容纸面归 thread / ViewSlot
拖拽反馈归 resizer
```

达到这一结构后，调整磨砂强度、主题、边界和响应式行为时，才不需要在三个组件之间反复补缝。
