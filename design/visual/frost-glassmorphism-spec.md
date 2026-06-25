# Peer Frost 毛玻璃规范（Glassmorphism Spec）

> 创建时间：2026-06-23
> 最后更新：2026-06-23
> 状态：v1.0 初稿
> 适用范围：`apps/desktop/` 全部 Chrome 层（侧栏 / Workbench / Composer / 浮层 / 红绿灯安全区）
> 关系定位：
> - 上承 `frost-implementation-guide.md` 第四节"浮层 / 弹窗范式"，将毛玻璃从"仅浮层"扩展到 Chrome 层
> - Token 真源仍为 `apps/desktop/renderer/src/styles/tokens.css`，本文新增的 `--glass-*` token 必须在 tokens.css 落地
> - 红线沿用 Frost 8 条，本文不松绑

---

## 一、设计意图

Peer Frost 的核心意象是"清晨冰面上的工具集"，毛玻璃不是装饰，是设计语言的本体表达。本规范定义"全 Chrome 毛玻璃 + 内容实色"的分层策略：

- **Chrome 层（外壳）** 用毛玻璃，强化空间纵深与冷感氛围
- **Content 层（内容）** 保持实色，保护长时间阅读的可读性与性能

> 反例：全屏毛玻璃。Task Thread 主区是用户日均停留最久的阅读区域，毛玻璃会持续消耗注意力，且 `backdrop-filter` 在长滚动列表上性能代价极大。

---

## 二、分层策略（必须遵守）

```
┌─────────────────────────────────────────────────────────┐
│ Sidebar          │  Main Task Surface  │  Workbench    │
│ 毛玻璃 (Chrome)   │  实色 (Content)      │  毛玻璃 (Chrome)│
│                 │                     │                │
│  Channel/会话    │  Thread events      │  Goal/Term/   │
│  半透明 + blur   │  --paper-sheet 实色 │  Browser/File │
│                 │  ↓                  │  半透明 + blur │
│                 │  Composer (浮起毛玻璃)│                │
└─────────────────────────────────────────────────────────┘
```

### 2.1 该用毛玻璃（Chrome 层）

| 区域 | blur 半径 | 透明度档位 | 平台优选 |
|---|---|---|---|
| Sidebar（含红绿灯安全区） | 24px | `--glass-chrome` | macOS vibrancy `sidebar` / Win11 acrylic |
| Workbench Panel | 24px | `--glass-chrome` | macOS vibrancy `under-window` / Win11 acrylic |
| Composer（底部浮起） | 16px | `--glass-control` | CSS `backdrop-filter`（区域小，性能可控） |
| Popover / Modal / Review card | 20px | `--glass-popover` | CSS `backdrop-filter`（沿用既有范式） |
| TabRail（Workbench 左 56px） | 24px | `--glass-chrome` | 跟随 Workbench |

### 2.2 绝不用毛玻璃（Content 层）

| 区域 | 原因 |
|---|---|
| Task Thread 消息流主区 | 阅读宽度 840-1040px，长时间停留，毛玻璃伤眼且性能炸 |
| Artifact / Evidence 详情卡 | 信息密度高，需要稳定底色 |
| Goal Runner Plan 主区 | 任务态需要视觉锚点 |
| 设置页整屏 detail route | 与主任务流分离，毛玻璃反而割裂感 |
| 终端 / 浏览器 / 文件视图的内容区 | 工具内容区，但其外壳容器（Workbench Panel）是毛玻璃 |

> 区分原则：**容器是否为"临时性 / 导航性"** —— 是则毛玻璃，承载主要消费内容则实色。

---

## 三、Token 增量（落地到 tokens.css）

新增 `--glass-*` token 系列，与现有 `--chrome-*` / `--paper-*` 体系平行，但仅用于声明半透明背景值：

```css
/* 浅色模式 :root */
:root {
  /* Chrome 层毛玻璃底色（侧栏 / Workbench） */
  --glass-chrome:        hsla(215, 16%, 98%, 0.72);
  --glass-chrome-hover:  hsla(215, 16%, 96%, 0.78);

  /* 控件层毛玻璃底色（Composer） */
  --glass-control:       hsla(218, 18%, 96%, 0.78);

  /* 浮层毛玻璃底色（Popover / Modal） */
  --glass-popover:       hsla(212, 12%, 99%, 0.82);

  /* 边缘高光（模拟玻璃边缘 1px） */
  --glass-edge-highlight: inset 0 1px 0 hsla(210, 30%, 100%, 0.45);

  /* blur 半径分档 */
  --blur-chrome:    24px;
  --blur-control:   16px;
  --blur-popover:   20px;
  --blur-saturate:  saturate(180%);
}

/* 暗色模式 [data-theme="dark"] */
[data-theme="dark"] {
  --glass-chrome:        hsla(215, 14%, 14%, 0.62);
  --glass-chrome-hover:  hsla(215, 14%, 18%, 0.68);
  --glass-control:       hsla(218, 16%, 16%, 0.68);
  --glass-popover:       hsla(212, 12%, 12%, 0.74);
  --glass-edge-highlight: inset 0 1px 0 hsla(210, 20%, 100%, 0.08);
  /* blur 与 saturate 同浅色 */
}
```

### 3.1 与红线的兼容性自检

| 红线 | 毛玻璃如何遵守 |
|---|---|
| 5（纯黑禁 / 纯白仅环境层） | `--glass-*` 一律用 `hsla()` + 冷色 hue（210-218），禁止 `rgba(0,0,0,...)` 与 `rgba(255,255,255,...)`；浅色透明度上限 0.82，深色上限 0.74 |
| 7（阴影限定 2 场景） | 玻璃边缘高光用 `--glass-edge-highlight`（`inset` 模拟），不新增 box-shadow token；外阴影沿用 `--shadow-popover` |
| 8（圆角 ≤ 16px） | 毛玻璃容器圆角沿用 `--radius-xl` (16px) 或更小；窗口外缘圆角由 Electron 窗口配置控制，不在本规范内 |
| 6（状态不只靠颜色） | Sidebar 选中态在毛玻璃底色上叠加 `--azure-trace` 左侧 2px 印记 + 文字加粗，不只靠透明度变化 |

---

## 四、平台分轨实现

### 4.1 macOS：原生 vibrancy（首选）

```ts
new BrowserWindow({
  vibrancy: 'sidebar',           // 侧栏主窗口
  visualEffectState: 'active',   // 失焦保持
  transparent: true,
  backgroundColor: '#00000000',
  titleBarStyle: 'hiddenInset',  // 红绿灯安全区
})
```

- Sidebar 区域：`vibrancy: 'sidebar'`
- Workbench Panel：单独 BrowserView 不可行（会断层），用同窗口内 CSS `backdrop-filter` 兜底
- 红绿灯安全区（52px）：天然透出 vibrancy，无需 CSS

> 性能优势：vibrancy 走 NSVisualEffectView，性能比 CSS `backdrop-filter` 高一个数量级，且能透出真实桌面壁纸。

### 4.2 Windows 11：acrylic / mica

```ts
new BrowserWindow({
  backgroundMaterial: 'acrylic',  // Win11 22H2+
  // 或 'mica'（更克制，主窗口推荐）
})
```

- 主窗口推荐 `mica`（仅在窗口边缘渲染，性能好）
- Sidebar / Workbench 内部用 CSS `backdrop-filter` 叠加 `--glass-chrome`

### 4.3 Windows 10：CSS 兜底

`acrylic` 在 Win10 下有窗口拖动卡顿的系统级 bug，**直接用 CSS `backdrop-filter`**，不调用原生 API。

### 4.4 降级矩阵

```ts
type GlassStrategy = 'native-vibrancy' | 'native-acrylic' | 'css-backdrop' | 'solid-fallback'

function pickStrategy(): GlassStrategy {
  if (process.platform === 'darwin') return 'native-vibrancy'
  if (process.platform === 'win32') {
    const build = parseInt(os.release().split('.')[2] ?? '0', 10)
    if (build >= 22000) return 'native-acrylic'  // Win11
    if (build >= 19041) return 'css-backdrop'    // Win10 20H1+
    return 'solid-fallback'
  }
  return 'css-backdrop'  // Linux 走 CSS
}
```

### 4.5 用户偏好兜底

```css
@media (prefers-reduced-transparency) {
  :root {
    --glass-chrome:   var(--chrome-raised);
    --glass-control:  var(--control-fill);
    --glass-popover:  var(--chrome-raised);
    --blur-chrome:    0px;
    --blur-control:   0px;
    --blur-popover:   0px;
  }
}
```

主题面板新增开关：`Translucent chrome`（默认开启，与既有 `Translucent sidebar` 合并）。

---

## 五、性能预算（硬指标）

### 5.1 红线阈值

| 指标 | 阈值 | 检测方式 |
|---|---|---|
| 同屏 `backdrop-filter` 元素数 | ≤ 5 | DevTools Layers 面板 |
| 单个 blur 半径 | ≤ 24px | code review + grep |
| 嵌套 blur 容器 | 0（绝对禁止） | 父子任意一层有 blur，另一层禁止 |
| 滚动列表内 blur 元素 | 0 | 列表项实色，仅容器 blur |
| 拖动窗口时帧率 | ≥ 50 fps | Electron Performance API |

### 5.2 优化技巧（必须实施）

```css
/* 1. 限制重绘范围 */
.glass-chrome {
  background: var(--glass-chrome);
  backdrop-filter: blur(var(--blur-chrome)) var(--blur-saturate);
  -webkit-backdrop-filter: blur(var(--blur-chrome)) var(--blur-saturate);
  contain: layout style paint;     /* 关键 */
  will-change: backdrop-filter;    /* 隔离合成层 */
  box-shadow: var(--glass-edge-highlight);
}

/* 2. 滚动期间降级 */
[data-scrolling="true"] .glass-chrome {
  backdrop-filter: none;
  background: var(--chrome-raised);
}
```

```ts
// 滚动监听：滚动中临时关闭 blur，停止 150ms 后恢复
let scrollTimer: number | null = null
container.addEventListener('scroll', () => {
  document.documentElement.dataset.scrolling = 'true'
  if (scrollTimer) clearTimeout(scrollTimer)
  scrollTimer = window.setTimeout(() => {
    delete document.documentElement.dataset.scrolling
  }, 150)
}, { passive: true })
```

### 5.3 低端设备探测

```ts
const isLowEnd =
  navigator.hardwareConcurrency < 4 ||
  /* Electron 检测集显 */
  (await app.getGPUInfo('basic')).gpuDevice?.[0]?.vendorId === INTEL_INTEGRATED

if (isLowEnd) document.documentElement.dataset.glass = 'off'
```

```css
[data-glass="off"] {
  --glass-chrome: var(--chrome-raised);
  --blur-chrome: 0px;
}
```

---

## 六、组件接入清单

### 6.1 Sidebar（`apps/desktop/renderer/src/components/Sidebar/`）

```css
.sidebar {
  background: var(--glass-chrome);
  backdrop-filter: blur(var(--blur-chrome)) var(--blur-saturate);
  -webkit-backdrop-filter: blur(var(--blur-chrome)) var(--blur-saturate);
  border-right: 1px solid var(--chrome-hairline);
  box-shadow: var(--glass-edge-highlight);
  contain: layout style paint;
}

/* macOS 下让 vibrancy 透出，CSS 不再叠半透明背景 */
[data-platform="darwin"] .sidebar {
  background: transparent;
  backdrop-filter: none;
}
```

### 6.2 Workbench Panel（`apps/desktop/renderer/src/components/Workbench/`）

同 Sidebar 处理，但 `vibrancy: 'under-window'`。注意：Workbench 内部的 ViewSlot（终端 / 浏览器 / 文件）必须用实色 `--paper-sheet`，**不能透下去**。

### 6.3 Composer（`apps/desktop/renderer/src/components/Composer/`）

```css
.composer {
  background: var(--glass-control);
  backdrop-filter: blur(var(--blur-control)) var(--blur-saturate);
  border: 1px solid var(--chrome-hairline);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-popover), var(--glass-edge-highlight);
}
```

### 6.4 Popover / Modal（沿用 `image-preview-overlay` 范式）

无需改动，已合规。本规范上线后将既有遮罩 `--chrome-raised` 透明值统一替换为 `--glass-popover`，blur 半径调到 `--blur-popover`。

---

## 七、改动前后纪律（每次必过）

改 UI 之前：
1. 这个区域属于 Chrome 还是 Content？Content 一律实色，不要试探
2. 是否会出现嵌套 blur？父容器有 blur，子组件禁用
3. 是否在长滚动列表里？列表项一律实色

改 UI 之后：
4. grep 残留：`backdrop-filter` 是否使用了 `--blur-*` token，未硬编码 `blur(20px)`
5. grep 残留：`background: rgba(0,0,0` / `rgba(255,255,255` 在 glass 区域
6. DevTools Layers 面板：同屏 blur 元素数 ≤ 5
7. 性能自测：拖动窗口、长列表滚动帧率 ≥ 50fps
8. 暗色 + 浅色 + Catppuccin 三主题截图自检
9. macOS / Win11 / Win10 三平台截图自检（至少 macOS + 一台 Windows）
10. 系统设置 "减少透明度" 开启后退化为实色

---

## 八、回归对照表

| 症状 | 错误写法 | 正确写法 |
|---|---|---|
| 主区毛玻璃 | Thread 主区加 `backdrop-filter` | 主区一律 `var(--paper-sheet)` 实色 |
| 硬编码 blur | `backdrop-filter: blur(20px)` | `blur(var(--blur-chrome))` |
| 黑色遮罩 | `background: rgba(0,0,0,0.4)` | `background: var(--glass-popover)`（红线 5） |
| 嵌套 blur | 卡片在毛玻璃容器内再加 blur | 卡片用半透明实色 + `--glass-edge-highlight` |
| macOS 双层 | vibrancy 之上又加 CSS 背景 | macOS 下 `.sidebar` 设 `background: transparent` |
| 滚动卡顿 | 列表项每个 blur | 容器单层 blur，列表项实色 |
| 暗色发灰 | 浅色 token 直接套用 | 暗色重定义 `--glass-*`（hue 不变，alpha 降到 0.62-0.74） |

---

## 九、实施路径建议

1. **Phase 1（Token 落地）**：在 `tokens.css` 新增 `--glass-*` 与 `--blur-*`，浅/暗双模式 + Catppuccin 全覆盖
2. **Phase 2（macOS 原生）**：BrowserWindow 配置 vibrancy，Sidebar / Workbench 在 darwin 下走 transparent
3. **Phase 3（Win11 acrylic）**：`backgroundMaterial` 配置，CSS 作为兜底层
4. **Phase 4（CSS 全平台兜底）**：Composer / Popover 走 CSS `backdrop-filter`
5. **Phase 5（性能闭环）**：滚动降级 + 低端设备探测 + `prefers-reduced-transparency`
6. **Phase 6（主题面板）**：合并 `Translucent sidebar` 为 `Translucent chrome` 全局开关

---

> 维护：当 `tokens.css` 新增 `--glass-*` 或调整 blur 档位时，同步更新本文第三节。本文与 `frost-implementation-guide.md` 第四节互为引用，浮层范式仍以第四节为锚。
