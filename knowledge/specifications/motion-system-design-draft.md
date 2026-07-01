# 全局动效体系设计草案（激进成体系）

- 创建时间：2026-07-01
- 最后更新：2026-07-01
- 状态：**已被取代**（设计阶段产物；已落地并升级为正式规范 `motion-system.md`，本文仅留作设计溯源）
- 关联代码仓：`peer_agent`（`apps/desktop/renderer`）
- 关联计划：全局动效体系治理（planId e8a770f3）

---

## 0. 现状事实（基于代码实测，非估算）

| 文件 | keyframes 数 |
| --- | --- |
| `styles/tokens.css` | 18 |
| `chat/styles/chat-surface.css` | 16 |
| `styles/llm-settings.css` | 5 |
| `styles/sidebar.css` | 5 |
| `chat/styles/goal-panel.css` | 4 |
| `styles/workbench.css` | 1 |
| **合计** | **49** |

- `prefers-reduced-motion` 兜底散写在 **8 个文件、共 11 处**（tokens 2、updater 2、sidebar 2、workbench 2、overlay 1、chat-surface 1、goal-panel 1、llm-settings 1）。
- Token 层已完备：时长 `--za-motion-fast 120 / medium 200 / slow 320`；缓动 `--za-ease-out / -standard / -spring / -decelerate / -accelerate`。
- `Overlay.tsx` 已统一封装模态入场/退场编排；治理脚本 `check-architecture-governance.mjs` 已有 `assertOverlayMotionAdmission()`。

**结论**：不是缺动画，而是同一语义有十余种写法、各处散写。治理核心＝收敛为一组语义基元 + 统一准入纪律（可被治理脚本强制）。

---

## 1. 语义基元清单（待确认 · 决策点 A）

把 49 个 keyframes 按语义归为 5 组，收敛到约 13 个命名基元。所有基元统一 `motion-` 前缀（新命名空间，与旧 `za-` 别名解耦，便于治理脚本识别）。

### 入场 enter（收敛自 ~15 个）
- `motion-enter-fade`：纯淡入
- `motion-enter-rise`：淡入 + 上移（默认，覆盖 panel/message/toast/dropdown/tool-card 等）
- `motion-enter-pop`：淡入 + 缩放回弹（spring，覆盖 thinking-pop 等强调入场）

### 退场 exit（收敛自 6 个）
- `motion-exit-fade`：纯淡出
- `motion-exit-sink`：淡出 + 下移
- `motion-exit-collapse`：淡出 + 缩小，**支持方向变量**（`--motion-collapse-x/y`），升级弹窗"飞向左上角"即此基元定向实例

### 脉冲/呼吸 pulse（收敛自 ~11 个）
- `motion-pulse-soft`：循环呼吸（thinking/running/active 状态）
- `motion-pulse-attention`：一次性注意力脉冲（徽标出现、消息闪现）

### 流光/微光 sheen（收敛自 ~12 个）
- `motion-sheen`：斜向扫光（进行态、进度条光泽，统一 `za-text-sweep` / `*-sheen` / `*-flow`）
- `motion-halo`：外扩柔光环（徽标 halo、executing-glow）

### 进度/加载 progress（收敛自 ~6 个）
- `motion-spin`：旋转
- `motion-dots`：加载点波动
- `motion-progress-slide`：不定长进度条滑动（browser-progress、skeleton）

> 每个基元同时提供：`@keyframes motion-*` + 一个 utility class `.motion-*`（封装 duration/easing/fill-mode），组件只需加 class 或 `animation-name`，不再自定义时长曲线。

---

## 2. 是否引入 JS 编排 helper（待确认 · 决策点 B）

**推荐：引入极轻量 helper（约 1 文件、无第三方依赖），落在 `apps/desktop/renderer` 公共层。**

理由：纯 CSS 无法优雅处理两件事——
1. **退场卸载时序**：React 卸载组件时元素直接消失，退场动画播不完。需要 `onAnimationEnd` 后再卸载（`Overlay.tsx` 已有此逻辑，抽出复用）。
2. **reduced-motion 探测**：JS 侧读取 `matchMedia('(prefers-reduced-motion)')`，供组件跳过编排。

helper 只做编排（何时挂 class、何时卸载），**不做动画本身**（动画仍在 CSS）。API 设想：`useMotionPresence(open) → { mounted, status }`（enter/exit/idle）。

**明确不引第三方库**（framer-motion / motion 等）：已有完整 token + 治理脚本基座，引库会双轨化、增重、稀释既有纪律。此取舍将写入 ADR。

---

## 3. 升级流程连续性方案（待确认 · 决策点 C）

**断裂现象**：点"更新"→ 弹窗在屏幕中央消失 → 进度出现在左上角徽标，中间无视觉牵引，用户不知去看左上角。

现有代码已有意图基元：`za-collapse-to-corner`（弹窗向左上收缩）+ `za-badge-attention`（徽标脉冲）+ `za-badge-halo`（外扩光环）。问题是三者**未被编排串联**。

两个方案：
- **方案 C1（推荐，稳）**：用 `motion-exit-collapse` 定向版让弹窗朝左上角收缩淡出，**紧接着**徽标播 `motion-pulse-attention` + `motion-halo`。靠"方向一致 + 时序衔接"制造连续感。改动小、无布局耦合、可 reduced-motion 降级。
- **方案 C2（炫，重）**：真正的 FLIP 共享布局动画——元素从弹窗位置连续"飞"到徽标位置。视觉最顺滑，但需测量两点坐标、处理布局耦合，手写成本高、回归面大。

推荐 C1 起步，把它做成"跨组件连续性"的复用样板；C2 作为后续可选增强。

---

## 4. 准入纪律（待确认，随 A/B/C 定）

1. 组件 CSS **禁止新增 `@keyframes`**，必须引用语义基元（治理脚本断言）。
2. 时长/缓动只能用 `--za-motion-*` / `--za-ease-*` token，禁止 magic number。
3. 位移类基元位移上限 ≤ 24px（克制原则）。
4. 只动合成层属性（transform/opacity），禁止触发 layout/paint 的属性做循环动画。
5. `prefers-reduced-motion` **只在 tokens.css 全局兜底一处**，删除其余 10 处重复。

---

## 5. 范围边界

- **In**：Token 校准、语义基元层（CSS + JS helper）、6 文件 49 keyframes 迁移收敛、升级流程连续性样板、治理脚本断言、规范文档 + ADR。
- **Out**：不引第三方动画库；不改动画的业务触发逻辑（只换实现）；不做全新动效创意（只收敛+补齐缺失）；FLIP（C2）默认后置。

---

## 待确认决策汇总

- **决策点 A**：语义基元清单与命名（§1）——是否采纳这 13 个 `motion-*` 基元与分组？
- **决策点 B**：是否引入轻量 JS 编排 helper（§2）？
- **决策点 C**：升级流程用 C1（定向收缩+时序衔接）还是 C2（FLIP）？

---

## 6. 决策定稿（2026-07-01 用户确认）

| 决策点 | 结论 | 落地影响 |
| --- | --- | --- |
| A · 语义基元清单 | **采纳**：13 个 `motion-*` 基元 / 5 组 | `primitives-css` 按 §1 建基元分片 |
| B · JS 编排 helper | **引入**：`useMotionPresence`（无第三方依赖，只管卸载时序 + reduced-motion 探测） | `orchestrator` 抽出复用 `Overlay.tsx` 逻辑 |
| C · 升级流程连续性 | **C1**：定向收缩淡出 + 徽标脉冲/光环时序衔接 | `updater-continuity` 按 C1 实现，FLIP(C2) 后置 |

准入纪律（§4）随之定稿，作为 `governance` 治理脚本断言的规格来源；ADR 将在 `knowledge` 阶段记录「不引第三方库 + 激进收敛」的决策与备选权衡。
