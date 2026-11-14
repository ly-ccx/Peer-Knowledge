# Peer Frost 2.0：全端视觉设计与底层因子规范

创建时间：2026-11-14
最后更新：2026-11-14
状态：已定稿实施规范（C 级界面表达基线）
适用范围：Peer Desktop（`apps/desktop/renderer/`）、Peer CLI/TUI（`apps/tui/src/`）、Peer 官网文档（`docs/`）
权威关联：
- 产品北极星：[peer-product-alignment.md](../product/peer-product-alignment.md)
- 体验基线：[peer-product-experience-standard.md](../../knowledge/specifications/peer-product-experience-standard.md)
- 壳层与交互：[14-product-design-language.md](../../knowledge/specifications/14-product-design-language.md)、[peer-frost-unified-design.md](../product/peer-frost-unified-design.md)
- 动效体系：[motion-system.md](../../knowledge/specifications/motion-system.md)
- CLI/TUI 主题治理：[cli-theme-governance.md](../../knowledge/specifications/cli-theme-governance.md)
- 代码 Token 真源：`apps/desktop/renderer/src/styles/tokens.css`、`apps/tui/src/tui-theme.ts`

> 本规范沉淀自桌面端现状审计与官网改版验证，在 [peer-product-experience-standard.md](../../knowledge/specifications/peer-product-experience-standard.md) 的基础上，将光学色阶、排版字阶、几何曲率、纵深阶梯、空间栅格与跨端 Token 收敛为可执行的原子级参数基线；并明确全站统一 `--font-sans` + `--font-mono`、全面启用 L0–L4 冷石板阶梯（淘汰旧纯中性灰桌面色值）。本规范不改变任何运行时契约、能力链、权限或 Evidence 边界。

---

## 一、设计气质与三大铁律

核心意象：**清晨冰面上的精密工程仪器（Cold Glass + Cold Slate Paper + Graphite + Glacial Azure）**。

1. **阅读面与结构卡严格二分**：Bot 的自然语言简报直接落在安静的阅读纸面上，不套全幅彩色气泡；只有结构化动作（权限审批、计划批准、结果确认、失败阻断、原消息引用、展开的过程时间线）才拥有容器边界与凹槽。
2. **五级表面明度阶梯**：禁止把所有区域刷成同一块灰或同一块黑。从下沉代码槽（L0）→ 环境壳（L1）→ 主阅读纸面（L2）→ 抬升卡片/指令台（L3）→ 控件交互面（L4），每一级必须具备可分辨的冷石板明度差。
3. **跨端同源表达**：Desktop、TUI 与官网共享同一冷石板底面、同一石墨字阶与冰湖青决策印记，不再各画一套割裂调色板。

---

## 二、九大底层视觉因子规范

### 因子 1：光学色相与五级表面阶梯（Surface & Color Physics）

- **色相物理约束**：所有中性背景、表面、描边与文字统一锁定在冷石板色区 **`H = 214°–220°`**，低饱和 **`S = 8%–22%`**。
- **零纯黑纯白铁律**：禁止在界面表面或文字中使用 `#000000`、`#FFFFFF`、`rgba(0,0,0,*)`、`rgba(255,255,255,*)` 或零饱和死灰（如 `#141414` / `#383838`）。

| 阶梯 | 语义 Token | 适用对象 | Light（HSL ≈ 216°） | Dark（HSL ≈ 218°） |
|---|---|---|---|---|
| **L0 凹槽层** | `--paper-sunken` / `--chrome-sunken` | 代码块、命令行槽、搜索框底、Switch 关闭轨、工具输出槽 | `#EAEFF5` | `#0D1016` |
| **L1 环境壳层** | `--chrome-canvas` / `--chrome-raised` | 非玻璃侧栏、宽屏内联工作现场底、SettingsGroup 表头带 | `#EFF3F8` | `#13171F` |
| **L2 主阅读纸面** | `--paper-base` | 对话主区阅读流、文档流、页面阅读底 | `#F7F9FC` | `#171C25` |
| **L3 抬升卡片面** | `--paper-sheet` / `--control-composer` | 选中 Bot 行、结构化动作卡、设置组内容区、Composer 指令台 | `#FCFDFF` | `#1E2430` |
| **L4 控件交互阶** | `--control-fill` / `-hover` / `-active` | 下拉按钮、次操作按钮、分段条底槽、悬停高亮 | `#E6ECF3` → `#DCE4EE` → `#D2DCE8` | `#252C3A` → `#2D3647` → `#364054` |

### 因子 2：毛玻璃与受光边缘物理公式（Frost Material）

- **`--glass-chrome`**（窗口原生 Vibrancy 玻璃层）：Light `hsla(215, 22%, 96%, 0.78)`（hover `0.86`）；Dark `hsla(218, 22%, 11%, 0.72)`（hover `0.80`）。
- **`--glass-popover`**（临时浮层 / Tooltip / 下拉菜单 / 轻浮层）：Light `hsla(214, 24%, 99%, 0.88)`；Dark `hsla(218, 20%, 13%, 0.88)`（窄窗浮起的 `bot-work-panel` 为防正文透字，提升至 `color-mix(in srgb, var(--paper-sheet) 94%, transparent)`）。
- **模糊与饱和度**：`--blur-chrome: 24px`、`--blur-popover: 24px`、`--blur-saturate: 1.6`（防止背景字穿透干扰）。
- **1px 受光内高光（`--glass-edge-highlight`）**：Light `inset 0 1px 0 hsla(210, 45%, 100%, 0.78)`；Dark `inset 0 1px 0 hsla(214, 40%, 100%, 0.08)`。
- **降级铁律**：`@media (prefers-reduced-transparency: reduce)` 或 `data-window-material="solid"` 一律退回 `--chrome-raised` 实色底并清除 `backdrop-filter`。

### 因子 3：石墨字阶与 WCAG 对比度基线

所有可读/可交互文本与所在底面对比度 **必须 ≥ 4.5:1**（大字标题 ≥ 3:1）：

| 字阶 Token | 用途 | Light 值 | Dark 值 |
|---|---|---|---|
| `--graphite-base` | 页面标题、正文、主操作标签、选中行名称 | `#181C22` | `#EEF2F7` |
| `--graphite-base-hover` | 主操作按钮悬停态底色 | `#262C35` | `#D7DFEA` |
| `--graphite-soft` | 副标题、设置说明、列表预览、次级图标 | `#4E5664` | `#B2BCCB` |
| `--graphite-fade` | 时间戳、计数字、占位符、元信息标签 | `#616A79` | `#8C98A9` |
| `--graphite-mute` | 仅限 `disabled` 态与非信息装饰线 | `#A4AEBC` | `#4A5362` |
| `--chrome-hairline` | 环境壳层 1px 发丝边与分割线 | `#DDE4EE` | `#27303E` |
| `--graphite-hairline` | 内容层 1px 细分割线 | `#D4DCE8` | `#2A3343` |

### 因子 4：冰湖青印记与四态冷调语义

- **冰湖青 `--azure-*`**：Light `--azure-seal: #286891`、`--azure-soft: #7FB0CF`、`--azure-trace: #E1ECF4`；Dark `--azure-seal: #76B0D4`、`--azure-soft: #3B6A8B`、`--azure-trace: #1D2E3F`。
  - **白名单用途（单屏显著印记 ≤ 3 处）**：① 键盘 `focus-visible` `2px` 外环；② **需要你处理**的决策角标与注意力卡；③ 滑块激活段与分隔条 hover 指示；④ 可点击文件路径 / 引用定位；⑤ Checkbox 选中态。
  - **CTA 禁令**：主操作按钮永远使用 `--graphite-base` 底 + `--paper-sheet` 字，绝不用 `--azure-*` 填充主按钮。
- **四态冷调语义（颜色 + `PeerIcon` + 文案三元并存）**：
  - `--state-success`：Light `#296E5D` / Dark `#63B39D`
  - `--state-confirm` / `--state-info`：Light `#286891` / Dark `#76B0D4`
  - `--state-warn`：Light `#32639B` / Dark `#76A5D6`
  - `--state-danger`：Light `#963850` / Dark `#D97C92`
  - `--state-thinking`：Light `#5B7296` / Dark `#92A7C9`

### 因子 5：三语境排版系统与字号阶梯

- **双字体栈**：
  - `--font-sans`: `"Inter", -apple-system, "PingFang SC", "Noto Sans SC", "Hiragino Sans GB", system-ui, sans-serif`（全站统一 Sans，废除过时 Serif 要求；`--font-serif-zh` 仅保留为指向 `--font-sans` 的兼容别名）。
  - `--font-mono`: `"IBM Plex Mono", "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace`（强制用于文件路径、分支/worktree 名、Shell 命令、能力 ID、核验计数、时间戳、版本号、键帽）。
- **字重与数字纪律**：只使用 `400` / `500` / `600`，**新增组件禁止写 `700 / bold`**；数字计数字段统一启用 `font-variant-numeric: tabular-nums`。
- **8 档标准化字阶**（`100%` 根字号 `16px`，随 `data-font-scale` 等比缩放）：
  - `heading-lg`：`1.625rem`（26px）/ 600 / `-0.03em`（页内二级大标题；页面级主 H1 仍维持 ≥ 30px）
  - `heading-md`：`1.25rem`（20px）/ 600 / `-0.025em`（模态与任务详情标题）
  - `heading-sm`：`1rem`（16px）/ 500–600 / `-0.015em`（分组标题、抽屉标题）
  - `body-lg`：`0.9375rem`（15px）/ `1.68` 行高 / 500（主会话阅读正文与用户指令正文）
  - `body`：`0.875rem`（14px）/ `1.5` 行高 / 500–600（列表项主名、设置行名、卡片标题）
  - `control`：`0.8125rem`（13px）/ `1.35` 行高 / 400–500（按钮、下拉、抽屉明细）
  - `meta`：`0.75rem`（12px）/ `1.5` 行高 / 400（说明文字、副路径、引用来源标签、行内 `code`）
  - `caption`：`0.6875rem`（11px）/ `1.35` 行高 / 400–500（状态胶囊、时间戳、角标、微标签）

### 因子 6：几何曲率与同心圆角定律

全系统一启用 `corner-shape: superellipse(1.4)`（开关正圆 `--peer-corner: round` 例外），圆角必须消费 `--ui-radius-*` 白名单：
- **微印记**：`--ui-radius-detail: 2px`、`--ui-radius-chip: 8px`、`--ui-radius-control-compact: 8px`
- **控件行**：`--ui-radius-control: 12px`、`--ui-radius-row: 12px`、`--ui-radius-inset: 12px`
- **一级面板**：`--ui-radius-panel: 16px`、`--ui-radius-modal: 16px`、`--ui-radius-message: 16px`、`--ui-radius-composer: 16px`
- **同心减法**：面板内全宽头带采用 `calc(var(--ui-radius-panel) - 1px)` 贴合外框；内嵌组件圆角必须严格小于外层圆角，禁止 16px 套 16px 留窄缝。

### 因子 7：五级纵深阶梯（Z-Elevation）

| 级 | 名称 | 边框 / 投影 / 材质 | 典型对象 |
|---|---|---|---|
| **E0** | 凹槽层 | 0 投影，`1px solid var(--chrome-hairline)`（或无描边），L0 底 | 搜索槽、代码块、命令行预览槽、Switch 轨道 |
| **E1** | 结构平铺层 | 0 投影，`1px solid var(--chrome-hairline)`，L3 底 | SettingsGroup、审批/确认卡、抽屉任务列表、选中 Bot 行 |
| **E2** | 主壳牌 / 指令台 | `1px hairline` + `--glass-edge-highlight` + `--shadow-card` / `--shadow-composer` | Vibrancy 下的主工作区、第四栏纸面、Composer 指令台 |
| **E3** | 锚定浮层 | `1px hairline` + `--shadow-popover` + `--glass-popover` | Dropdown、ModelPicker、OverflowMenu、窄窗 WorkPanel |
| **E4** | 模态遮罩层 | `--glass-modal-scrim` + `--glass-modal-background` + `--glass-modal-shadow` | Overlay 统一承接的全部模态对话框 |

### 因子 8：空间栅格与紧凑密度因子

- **基础栅格**：`4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 64px`（`--space-*`）。
- **主壳三栏尺寸**：
  - 左栏 Bot List：默认 `292px`（范围 `240–360px`），darwin 顶部安全距 `40px`（非 darwin `12px`）。
  - 中栏主线程：顶栏锁定 **`52px`**（含项目名 + 单行 mono 绑定路径提示 + 右侧图标按钮）；可读列宽上限 `800px`（`--bot-column-gutter: 28px`）。
  - 宽屏 Work Panel（`wide="true"`）：作为 `.bot-main` 右侧 **内联分栏**（`326px` 宽，L1 `--chrome-canvas` 底 + 左侧 `1px hairline`，零外投影与嵌套圆角）；窄屏（`wide="false"`）转为 E3 浮起抽屉。
- **`[data-density="compact"]` 生效尺度**：覆盖 `--ui-control-height: 2rem`、`--ui-control-height-compact: 1.75rem`、`--space-3: 10px`、`--space-4: 12px`、`--space-5: 16px`、`--space-6: 20px`。

### 因子 9：跨端映射与组件语法

1. **TUI 对齐**：`apps/tui/src/tui-theme.ts` 采用同一冷黑曜石/冷雪纸明度阶梯与冰湖青焦点色（淘汰刺眼荧光青柠 `#b8f35b`），并维持 ≥4.5:1 文本及选区对比度。
2. **禁止未定义变量与硬编码**：Renderer 业务 CSS 禁止引用未在 `tokens.css` 注册的变量（历史上大量出现的 `--graphite-secondary`、`--border-color`、`--text-secondary` 等统一收敛到正名 Token）。
3. **动作卡与引用条语法**：
   - 引用条（`ReplyAnchors` / `QuoteChip`）保持在 `.bot-reply-body` 上方内部对齐，L0 柔底 + 无边框 + **禁止左侧装饰竖线**。
   - 动作卡（`CardView`：审批/计划/确认/阻断）采用 E1 容器 + 4 段式结构；停止与未完成反馈（`agent_stopped` / `agent_unavailable`）保留紧贴文本流的 8px 节奏。
