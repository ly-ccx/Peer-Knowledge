# 全局动效体系规范（Motion System）

- 创建时间：2026-07-01
- 最后更新：2026-07-01
- 状态：**已落地**（typecheck + architecture:check + build 全绿）
- 关联代码仓：`peer_agent`（`apps/desktop/renderer`）
- 关联决策：`knowledge/decisions/44-motion-system-consolidation.md`
- 设计溯源：本文由 `motion-system-design-draft.md` 定稿升级而来

---

## 0. 为什么要有这套体系

治理前的事实（基于代码实测）：同一语义的动画有十余种写法，**49 个 `@keyframes` 散落在 6 个文件**，`prefers-reduced-motion` 兜底重复散写在 8 个文件 11 处。典型症状：

- 升级弹窗点「更新」后直接消失，用户不知道进度已挪到左上角徽标（跨组件视觉断裂）。
- 有的面板有入场动画、有的没有；同样是「淡入上移」有 5 种时长/位移写法。

**核心结论**：问题不是缺动画，而是缺**单一真相**与**准入纪律**。本规范把动画收敛为一组语义基元，并用治理脚本强制准入。

---

## 1. 四层结构（单一真相）

```
Token 层     tokens.css      时长 / 缓动 / 位移变量（唯一数值来源）
   ↓
语义基元层   motion.css      @keyframes motion-* + utility class .motion-*（唯一动画定义源）
   ↓
编排层       useMotionPresence.ts   卸载时序 + reduced-motion 探测（JS，无第三方依赖）
   ↓
组件层       各组件 CSS/TSX   只引用基元，禁止散写 @keyframes
```

### Token 层（`styles/tokens.css`）
- 时长：`--za-motion-fast 120ms` / `--za-motion-medium 200ms` / `--za-motion-slow 320ms`
- 缓动：`--za-ease-out` / `-standard` / `-spring` / `-decelerate` / `-accelerate`
- 位移：`--za-motion-shift-sm 6px` / `--za-motion-shift 12px` / `--za-motion-shift-lg 24px`
- 全局 `prefers-reduced-motion` 兜底**仅此一处**（`animation-duration:1ms` 通配）。

### 语义基元层（`styles/motion.css`）
18 个 `@keyframes motion-*` + 14 个 utility class，按 5 组语义组织：

| 组 | 基元 | 用途 |
| --- | --- | --- |
| 入场 enter | `motion-enter-fade` / `motion-enter-rise` / `motion-enter-pop` | 纯淡入 / 淡入+位移（默认）/ 淡入+缩放回弹 |
| 退场 exit | `motion-exit-fade` / `motion-exit-sink` / `motion-exit-collapse` | 纯淡出 / 淡出+下移 / 淡出+定向缩小 |
| 脉冲 pulse | `motion-pulse-soft` / `motion-pulse-attention` | 循环呼吸 / 一次性注意力脉冲 |
| 流光 sheen | `motion-sheen` / `motion-halo` / `motion-ripple` / `motion-glow` | 斜向扫光 / 外扩柔光环 / 涟漪 / 辉光 |
| 进度 progress | `motion-spin` / `motion-dots` / `motion-progress-slide` / `motion-flash` / `motion-shimmer` | 旋转 / 加载点 / 进度滑动 / 一次性高亮 / 骨架微光 |

> 注：实际落地为 18 个基元（草案计划 13 个）。迁移中发现 `ripple/glow/flash` 表达的机制与 sheen/pulse 不同，独立成基元更清晰——规范以落地事实为准。

**方向/参数通过 CSS 变量定制，不新增 keyframe**：
- `motion-enter-rise` 位移由 `--motion-enter-from` 定制（正值从下方升入、负值从上方落下）。
- `motion-exit-collapse` 方向由 `--motion-collapse-x/y` 定制（升级弹窗「飞向左上角」即此基元定向实例）。
- `motion-flash` 颜色由 `--motion-flash-from/to/glow` 定制。

### 编排层（`app/hooks/useMotionPresence.ts`）
纯 CSS 无法优雅处理两件事，故抽出极轻量 JS helper（无第三方依赖）：
1. **退场卸载时序**：React 卸载组件时元素直接消失、退场动画播不完；helper 用 `onAnimationEnd` 后再卸载。
2. **reduced-motion 探测**：统一读取偏好，避免各组件重复判断。

---

## 2. 准入纪律（治理脚本强制）

由 `scripts/check-architecture-governance.mjs` 的 `assertMotionPrimitivesAreCentralized()` 自动校验：

1. 组件 CSS **禁止新增 `@keyframes`**，必须引用语义基元。
2. 时长/缓动只能用 `--za-motion-*` / `--za-ease-*` token，禁止 magic number。
3. 位移类基元位移上限 **≤ 24px**（克制原则）。
4. 循环动画只动合成层属性（`transform` / `opacity`），禁止触发 layout/paint。
5. `prefers-reduced-motion` **只在 tokens.css 全局兜底一处**；组件级 media query 仅允许做「基元无法表达的终态修正」（如 shimmer 文字透明恢复），不得重复「关闭动画」的基础逻辑。

### 受控例外白名单
仅 3 个文件可定义 `@keyframes`（治理脚本 `keyframeAllowlist` 登记）：

| 文件 | 例外 keyframe | 为何不能通用化 |
| --- | --- | --- |
| `styles/motion.css` | 全部 `motion-*` | 语义基元层本身 |
| `styles/tokens.css` | `za-loading-skeleton` / `za-message-shimmer` / `za-content-shimmer` | 双背景层扫过 / 一次性 opacity 淡出，基元不表达 |
| `styles/llm-settings.css` | `card-sheen` / `badge-sheen` | 品牌默认卡/徽章艺术高光，机制不可通用化 |

**新增例外必须同时更新白名单**，确保「例外」是被治理登记的，而非随手散写。

---

## 3. 跨组件连续性样板：升级流程

「点更新 → 左上角进度 → 完成卡片」是跨组件连续性的**参考样板**。

### CSS 层（方向一致 + 时序衔接，方案 C1）
- 弹窗退场：`motion-exit-collapse` + `transform-origin:top left` + `--motion-collapse-x/y` → 朝左上角版本徽标定向收缩淡出。
- 徽标承接：进度环 `motion-pulse-attention` 脉冲 + `::before` `motion-halo` 外扩光环。
- 完成卡片：右下角 `UpdateToast` 用 `motion-enter-rise` 入场 / `motion-exit-sink` 退场。

### 状态层（真正的断裂点在这里）
CSS 样板到位后，真正的断裂是 **React 状态时序空窗**：点「更新」后 `download()` 异步转调主进程，`phase` 要等首个 `download-progress` 事件才变 `downloading`，弹窗已飞走而进度环尚未挂载。

**解法**：`VersionBadge` 加 `pendingDownload` 过渡态——点击瞬间即以 0% 点亮进度环（脉冲+光环就绪）接住飞来的弹窗，真实 downloading/终态到来后清除。

> **样板启示**：跨组件连续性 = CSS 方向/时序衔接 **＋** 状态就绪时序对齐。只做 CSS 不够，必须消除状态空窗。

---

## 4. 范围边界

- **In**：Token 校准、语义基元层（CSS + JS helper）、6 文件 keyframes 迁移收敛、升级流程连续性样板、治理脚本断言。
- **Out**：不引第三方动画库（见 ADR 44）；不改动画的业务触发逻辑（只换实现）；不做全新动效创意（只收敛+补齐）；FLIP 共享布局动画（方案 C2）后置。

---

## 5. 新增/修改动画时怎么做

1. 能用现有基元 → 加 utility class 或 `animation: motion-* ...`，用 `--motion-*` 变量定制方向/参数。
2. 现有基元差一点 → 优先给基元加 CSS 变量参数，而非新建 keyframe。
3. 确属全新机制 → 加到 `motion.css` 成为新基元；若是不可通用化的品牌特例 → 加到白名单文件并更新治理脚本 `keyframeAllowlist`。
4. 涉及卸载退场 → 用 `useMotionPresence`，不要手写 `onAnimationEnd`。
5. 提交前跑 `pnpm architecture:check` 确认未违反准入。
