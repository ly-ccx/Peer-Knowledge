# 39. 应用更新下载交互改造（非模态后台下载）

## Status

Implementation done locally on 2026-06-25（渲染层 + i18n + CSS 已落地于
`peer_agent` 仓，本机 typecheck / lint 通过）。设计决策见 §Decision。

落地范围属于渲染层交互改造，**未触及** runtime 契约与主进程更新链路，
故不属于 `AGENTS.md` 定义的 A 级变更。代码改动一律在 `peer_agent` 仓，本
知识库仅作可追溯记录。

- 创建时间：2026-06-25
- 最后更新：2026-06-25

## Context

### 现状（改造前，基于代码证据）

更新能力是「主进程能力 + 渲染层表达」两段：

- 主进程 `apps/desktop/electron/main/auto-updater.mjs`：`autoDownload=false`，
  检查到新版本只广播事件；用户点「更新」才 `downloadUpdate()`，进度经
  `download-progress` 事件回传；`UpdaterStatus` 已暴露
  `phase / percent / install / openInstaller`。
- 渲染层 `useUpdater.ts` 订阅状态，`VersionBadge.tsx` 点徽标打开
  `UpdateModal.tsx`。
- `UpdateModal.tsx` 用**全屏遮罩模态** `Overlay` 承载所有阶段
  （available / downloading / downloaded / error）。

### 问题

1. **下载阶段霸屏且点不掉**：下载阶段
   `isBusy = downloading || downloaded` → `closeOnBackdrop={!isBusy}`，
   点遮罩不关闭；且该阶段弹窗内**只渲染吉祥物 + 进度条 + 文案，没有任何
   关闭/收起入口**。用户被一个全屏暗化大弹窗困住，只剩 ESC 能逃。

2. **关闭没有动画**：`Overlay` 基座本身**有**退场编排
   （`requestClose()` → `closing` 态播 `za-fade-out` / `za-slide-down-out`
   → 动画结束才 `onClose` 卸载）；但 `VersionBadge.tsx` 的关闭是
   `onClose={() => setModalOpen(false)}` **直接卸载组件**，绕过了退场动画，
   体感就是「咔一下没了」。

3. **阶段切换生硬**：available → downloading → downloaded 在同一挂载的弹窗
   里直接换内容，阶段之间无过渡。

根因：把「需要用户决策的提示」（available/error）和「不需要用户盯着的过程」
（downloading）以及「完成后的轻量召唤」（downloaded）全塞进了同一个**模态**
容器里，违背了「过程不该霸屏」的交互直觉。

## Decision

把更新表达按「是否需要用户当下决策」拆成三种载体，下载过程从模态降级为
非模态后台任务：

### 决策一：弹窗动画退场 + 后台静默下载

- 用户点「更新」后，弹窗走 `Overlay` 已有的 `requestClose` 退场编排**动画
  收起**（修掉原先直接卸载、绕过动画的写法），下载转入后台。
- 主进程链路（`autoDownload=false` → `downloadUpdate()` → 事件回传）本就能在
  弹窗关闭后继续工作，无需改动。
- `UpdateModal` 职责收敛为只承载需要用户决策/感知的阶段：
  available / checking / not-available / error；不再渲染 downloading /
  downloaded / ready-to-open 的霸屏分支。

### 决策二：徽标 mini 环形进度

- 后台下载期间，版本徽标原先的红点 `.sidebar-version-dot` **原地升级为 mini
  环形进度**，按 `percent` 填充，作为「正在后台下载」的唯一轻量反馈。
- 复用红点的位置与体量，不包裹整个文字徽标，改动可控且与既有视觉一脉相承。

### 决策三：右下角完成卡片

- 下载完成（downloaded / ready-to-open）后，右下角滑入一张**非模态卡片**：
  「新版本已就绪」+ 主按钮「立即安装」+ ✕ 收起。
- 「立即安装」走**原有安装流程**（Windows 重启安装 / macOS 打开 dmg），即调用
  既有的 `install` / `openInstaller`，安装语义零改动。
- ✕ 收起后卡片消失，**徽标保留红点兜底**，点徽标可重新唤出完成卡片，与现有
  「点徽标进入更新」的逻辑天然衔接。

## 契约边界（明确不动什么）

- **不动主进程** `apps/desktop/electron/main/auto-updater.mjs`：后台下载、通道
  选择、事件回传链路保持原样。
- **不动 protocol**：`UpdaterStatus` 既有字段（`phase / percent / install /
  openInstaller`）已满足全部新交互，无需新增协议字段。
- **不动安装语义**：完成卡片的「立即安装」复用既有安装入口，平台分支行为不变。
- 改动只落在 **渲染层 + i18n + CSS** 三处。

## 涉及文件（均在 `peer_agent` 仓）

- `apps/desktop/renderer/src/.../UpdateModal.tsx`：收敛职责，移除霸屏的
  downloading / downloaded / ready-to-open 分支，关闭走 Overlay 退场动画。
- `apps/desktop/renderer/src/.../UpdateToast.tsx`（新建）：右下角完成卡片，
  含进/退场动画。
- `apps/desktop/renderer/src/.../VersionBadge.tsx`：点「更新」= 下载 + 动画关
  弹窗；下载中红点变 mini 环形进度；完成挂载 toast；维护 ✕ 收起后徽标兜底。
- 更新相关 CSS（`updater.css` 等）：卡片滑入/滑出、徽标环形进度、reduced-motion
  降级。
- `packages/i18n/src/index.ts`：中英文案补充（已就绪 / 立即安装 / 收起等）。

## 动画与降级（prefers-reduced-motion）

- 三处动画：① 弹窗退场（复用 Overlay `za-fade-out` / `za-slide-down-out`）；
  ② 徽标环形进度填充；③ 右下角卡片滑入/滑出。
- `tokens.css` 已有全局 `@media (prefers-reduced-motion: reduce)` 兜底（动画时长
  压到 ~1ms），系统开启「减少动态效果」时新增动画自动降级为近瞬时，不依赖各
  组件单独处理。

## 验证方式

本机静态验证（已通过）：

- `pnpm --filter @peer-agent/desktop typecheck`
- lint

人工自测三条路径：

1. **主路径**：点徽标 → 弹窗 →「更新」→ 弹窗动画收起、后台下载 → 徽标环形
   进度 → 右下角完成卡片 →「立即安装」（Windows 重启 / macOS 打开 dmg）。
2. **收起再唤出**：完成卡片点 ✕ → 滑出、红点保留 → 点徽标重新唤出卡片。
3. **失败兜底**：下载中断网 → 点徽标进入 error 分支（错误信息 +「打开 Release
   页面」+「重新检查」），不新造失败 UI。

另建议开系统「减少动态效果」复核动画降级。

## 关联

- 产品设计：`design/product/release-auto-update.md` 第 7 节「渲染层更新 UI」
  即本次落地内容。
