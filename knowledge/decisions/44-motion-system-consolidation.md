# 44. 全局动效体系：自建语义基元 + 激进收敛（不引第三方库）

## Status

Implementation done locally on 2026-07-01（Token 层 + 语义基元层 CSS + JS 编排
helper + 6 文件 keyframes 收敛 + 治理脚本断言 + 升级流程连续性修复已落地于
`peer_agent` 仓，本机 typecheck / architecture:check / build 全绿）。

落地范围属渲染层动效基础设施，**未触及** runtime 契约与主进程链路，非
`AGENTS.md` 定义的 A 级变更。代码改动一律在 `peer_agent` 仓，本知识库仅作可追溯记录。

- 创建时间：2026-07-01
- 最后更新：2026-07-01
- 关联规范：`knowledge/specifications/motion-system.md`
- 关联计划：全局动效体系治理（planId e8a770f3）

## Context

### 现状（改造前，基于代码证据）

- **49 个 `@keyframes` 散落 6 个文件**（tokens 18 / chat-surface 16 / llm-settings 5 /
  sidebar 5 / goal-panel 4 / workbench 1）。同一语义（如「淡入上移」）有十余种时长/位移写法。
- `prefers-reduced-motion` 兜底重复散写在 **8 个文件 11 处**。
- Token 层已完备（时长三档、5 条缓动），`Overlay.tsx` 已封装模态入场/退场编排，
  治理脚本已有 `assertOverlayMotionAdmission()`——**基座具备，缺的是收敛与纪律**。

### 用户痛点（触发本次治理）

> 「整个 app 动画参差不齐，有些有有些没有，尤其升级弹窗点击后直接消失，用户
> 都不知道回到左上角有个进度条。」

### 力度选择

在「保守（只补基元不动旧代码）/ 彻底（收敛去重）/ 激进（成体系+JS 编排+治理）」
三档中，用户明确选择**激进成体系**。

## Decision

### D1：自建语义基元层，**不引第三方动画库**

放弃 framer-motion / motion / react-spring 等，改为自建：
- CSS：18 个 `motion-*` 语义基元（`@keyframes` + utility class），收敛 5 组语义。
- JS：极轻量 `useMotionPresence`（无第三方依赖），只管卸载时序 + reduced-motion 探测。

### D2：激进收敛 + 受控例外白名单

把 6 文件 49 keyframes 收敛到 motion.css 一组基元，逐处替换调用点并删除冗余。
无法通用化的机制保留为**受控例外**，登记在治理脚本白名单（3 文件 5 例外）。

### D3：治理脚本强制准入

新增 `assertMotionPrimitivesAreCentralized()`：禁止组件散写 `@keyframes`、强制
motion.css 为单一真相、`prefers-reduced-motion` 收敛到全局兜底。

### D4：升级流程作为跨组件连续性样板（方案 C1）

弹窗朝左上角定向收缩（`motion-exit-collapse`）+ 徽标脉冲/光环时序衔接；并修复
真正的状态时序空窗（`pendingDownload` 过渡态）。FLIP 共享布局动画（C2）后置。

## Rationale / 权衡

### 为什么不引第三方库（D1 核心权衡）

| 维度 | 引 framer-motion 等 | 自建语义基元（选择） |
| --- | --- | --- |
| 与现有基座 | 与已完备的 token + 治理脚本**双轨化**，两套动画心智 | 复用既有 token/Overlay/治理，单轨 |
| 包体积 | framer-motion gzip ~50KB+ | JS helper 约 1 文件、~0 依赖 |
| 治理可控性 | 库内动画绕过 `architecture:check` | 基元即 CSS，治理脚本可静态断言 |
| reduced-motion | 需适配库 API | tokens.css 全局兜底一处通吃 |
| 设计语言一致性 | 库默认曲线/时长偏离 Peer Frost | 强制走 `--za-motion-*` token |

结论：项目已有完整 token 体系 + 治理脚本在管动效准入，引库是**净负债**——
增重、双轨、稀释纪律。自建成本主要是一次性收敛，长期由治理脚本守住。

### 为什么激进而非保守（D2 权衡）

保守方案（只加基元不动旧代码）会让新旧命名空间**永久混用**，治理脚本只能降级为
「只禁新增」，无法根治「同一语义多种写法」。激进方案代价是回归面大（数十处替换），
但用户已明确选激进，且每处替换都做了 keyframe body 逐一比对（无损映射），风险可控。

### 落地与计划的偏差（诚实记录）

- 基元数 **13 → 18**：迁移中发现 `ripple/glow/flash` 机制独立，拆分更清晰。
- 发现并修复计划外的**既有治理隐患**：`assertOverlayMotionAdmission` 锚点
  `za-panel-in` 早已失效（靠注释残留蒙混通过），一并改为真实基元 `motion-enter-rise`。
- 升级流程连续性的真正断裂点是 **React 状态时序空窗**（非 CSS），CSS 样板此前已就位。

## Consequences

### 正面
- 动画有单一真相，新增/修改动画有明确路径（见规范 §5）。
- 治理脚本静态拦截散写 keyframes（负向测试验证生效）。
- 升级流程视线不再断裂；该样板可复用于其他跨组件过渡。
- 无第三方动画依赖，包体积与心智负担不增。

### 负面 / 待跟进
- 受控例外白名单需人工维护，新增例外要同步治理脚本。
- 部分动画有可感知范围外的细微视觉变化（如 settings 整页入场放弃 0.995→1 微缩放、
  加载点波动峰值 -2px→-6px 归一化），已在迁移中逐处确认并接受。
- FLIP 共享布局动画（C2）未做，升级弹窗「飞向左上角」是定向收缩而非真实位移动画。

## 关联

- 规范：`knowledge/specifications/motion-system.md`
- 设计溯源：`knowledge/specifications/motion-system-design-draft.md`
- 前序更新交互决策：`knowledge/decisions/39-updater-download-ux.md`
- 代码落点：`apps/desktop/renderer/src/styles/motion.css`、
  `app/hooks/useMotionPresence.ts`、`app/components/VersionBadge.tsx`、
  `scripts/check-architecture-governance.mjs`
