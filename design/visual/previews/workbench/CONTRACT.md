# 高保真原型实现契约

> 唯一真相：`peer_agent/apps/desktop/renderer/src/styles/tokens.css`
> 目的：原型迁移到 peer_agent 时**只替换变量来源，不改一行数值**。

创建时间：2026-07-31
最后更新：2026-07-31

---

## 一、八条红线（tokens.css 头部原文）

| # | 红线 | 本稿如何满足 |
|---|---|---|
| 1 | Azure 不上 CTA | CTA 用 `--graphite-base` 实色 |
| 2 | H1 字号 ≥ 30px | H1 = 30px |
| 3 | 标题与正文统一 sans | 全站 `--font-sans`，**禁止 serif/宋体** |
| 4 | 单屏 azure ≤ 3 | 仅：运行中状态点、问候区强调、背景微光 |
| 5 | 纯黑禁 / 纯白仅环境层 | 阴影用石墨 `rgba(26,29,33,…)`；纯白只在 `--chrome-*` |
| 6 | 状态不只靠颜色 | 每个状态都有 icon 或形状差异（spinner/方章/空心点） |
| 7 | 阴影限定 2 场景 | 仅「卡片抬升」与「浮层」两类 |
| 8 | 圆角 ≤ 16px | 最大 `--radius-xl: 16px` |

## 二、字体栈（tokens.css:35-39）

```css
--font-sans: "Inter", -apple-system, "PingFang SC", "Noto Sans SC", "Hiragino Sans GB", system-ui, sans-serif;
--font-serif-zh: var(--font-sans);   /* 已被显式关掉，等同 sans */
--font-mono: "IBM Plex Mono", "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
```

**关键**：`--font-serif-zh` 在 tokens.css 里被别名回 sans。之前稿子用
`"Songti SC", "Noto Serif SC"` 是直接违反红线 3，本次全部移除。

## 三、字阶 × 字距表（对齐 landing 的分档手法）

大字号收紧、小字号放开，这是保真度的主要来源。

| 用途 | font-size | letter-spacing | weight | color |
|---|---|---|---|---|
| H1 问候 | 30px | -0.035em | 600 | `--graphite-base` |
| 数字指标 | 26px | -0.03em | 600 | `--graphite-base` |
| 区块 H2 | 17px | -0.025em | 600 | `--graphite-base` |
| 卡片标题 | 15px | -0.02em | 600 | `--graphite-base` |
| 正文强调 | 14px | -0.015em | 500 | `--graphite-base` |
| 正文 | 13.5px | -0.01em | 400 | `--graphite-soft` |
| 列表项 | 13px | -0.01em | 400/500 | `--graphite-base` |
| 次要说明 | 12.5px | 0 | 400 | `--graphite-soft` |
| 元信息 | 12px | 0 | 400 | `--graphite-fade` |
| 标签 | 11.5px | 0.01em | 500 | `--graphite-soft` |
| 徽标/mono | 11px | 0.02em | 500 | `--graphite-fade` |
| 分组标题 | 10.5px | 0.08em | 600 | `--graphite-mute` |
| 极小 mono | 9.5px | 0.03em | 500 | `--graphite-mute` |

至少 13 档字号、5 档以上字距。

## 四、阴影六档（tokens.css:142-149，双层石墨）

```css
--shadow-card:        0 1px 2px rgba(26,29,33,.08), 0 10px 28px rgba(26,29,33,.10);
--shadow-card-hover:  0 2px 4px rgba(26,29,33,.10), 0 16px 36px rgba(26,29,33,.14);
--shadow-card-active: 0 1px 3px rgba(26,29,33,.10), 0 8px 22px rgba(26,29,33,.12);
--shadow-popover:     0 2px 12px rgba(26,29,33,.06);
--shadow-drag:        0 4px 16px rgba(26,29,33,.10);
--shadow-soft:        0 1px 2px rgba(26,29,33,.06), 0 6px 18px rgba(26,29,33,.08);
```

用法：静态卡片 `--shadow-soft`；可交互卡片 `--shadow-card` + hover 升到
`--shadow-card-hover`；弹层 `--shadow-popover`；输入区 `--shadow-composer`。

## 五、分层（Chrome 毛玻璃 / Content 实色）

| 层 | 用途 | 背景 | 模糊 |
|---|---|---|---|
| Chrome | 侧栏、顶栏、右栏 | `--glass-chrome` + `--glass-edge-highlight` | `--blur-chrome: 24px` `saturate(1.6)` |
| Control | 输入框、切换器 | `--glass-control` | `--blur-control: 16px` |
| Popover | 弹层、命令面板 | `--glass-popover` | `--blur-popover: 24px` |
| Content | 卡片、列表 | `--paper-sheet` / `--paper-base` **实色** | 无 |

## 六、色板（light，tokens.css:74-115）

```
chrome:    canvas #FAFBFC  raised #F3F5F8  sunken #EBEEF3  hover #F0F2F6  active #E5E8EE  hairline #DCE0E8
paper:     base #EDF1F6    sheet #F7F9FC   sunken #DDE3EB  hover #EAEEF4  active #D5DCE6
control:   composer #EFF2F6  fill #EAEDF2  fill-hover #DFE3EA
graphite:  base #1A1D21  hover #2A2D33  soft #525660  fade #878B95  mute #B0B4BC  hairline #DCE0E8
azure:     seal #3B7FAB  soft #7BA8C8  trace #D8E4EE
state:     thinking #6B7FA0  confirm #1F6B9B  success #3E7A6B  warn #3B6FAB  danger #7A3E50  denied #5C5A70
radius:    xs 2  sm 6  md 8  lg 12  xl 16
```

## 七、迁移方式

原型 `:root{}` 里的变量名与 tokens.css **完全同名**。迁进 peer_agent 时：

1. 删掉原型的 `:root{...}` 变量块
2. 改为引入 `styles/tokens.css`
3. 其余 CSS 一行不动（因为引用的都是 `var(--graphite-base)` 这类正名 token）

深色模式同理：tokens.css 已有 `.theme-dark` 覆盖（:353-395），原型无需另写。

## 八、密度基准

对齐 `design/visual/previews/github-landing-preview.html`（1393 行）：
本页目标 ≥ 1000 行，字号 ≥ 10 档，字距 ≥ 4 档。
