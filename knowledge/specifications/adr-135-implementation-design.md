# ADR 135 工程实施文档：自然绘本猫形象、直观 Bot ↔ Worker 流转与可插拔 CLI 执行器

> 创建时间：2026-11-25  
> 最后更新：2026-11-25  
> 状态：可执行实施规范（供 Codex 直接按模块落地与验收）  
> 对应决策：[ADR 135：自然绘本猫形象体系、主对话内联任务流与可插拔 CLI 执行器](../decisions/135-editorial-cat-avatars-inline-worker-stream-and-pluggable-cli-executors.md)  
> 关联代码仓：`/Users/yinliang/.codex/worktrees/native-rust-cli/Peer-Agent`（本地分支 `codex/native-rust-cli`）  
> 视觉参考与交互基线：
> - 路线 A 绘本猫实景对比页（已视觉验收）：`scratch/build-avatar-compare-html.mjs` 中的 8 只自然毛色绘本猫（本文 §2 给出完整可直接复制的精确 SVG 源码）
> - 交互流转目标：侧栏树直出活跃任务（红框 1）+ 主对话流无边框单行任务动态与输入框上方汇总条（红框 2）

---

## 0. 执行前必读：代码仓当前工作树基线（CRITICAL）

在开始改代码前，请先核对 `/Users/yinliang/.codex/worktrees/native-rust-cli/Peer-Agent` 当前工作树（基于本地 `codex/native-rust-cli` HEAD `e4e6e85b`）的 6 个未提交修改文件，**切勿误回滚已完成且验收通过的抽屉修复**：

| 文件路径 | 当前状态 | Codex 处理指令 |
|---|---|---|
| `apps/desktop/renderer/src/project-agent/styles/bot-drawer.css` | **已完成并视觉验收**：移除 `.bot-overview-details` 内部多余竖线与嵌套边框按钮；`.bot-model-settings-head` 右对齐「跟随全局」 | **保留，不要回滚** |
| `apps/desktop/renderer/src/project-agent/drawer/BotPolicyFields.tsx` | **已完成并视觉验收**：渲染 `.bot-model-settings-head`（左侧角色名、右侧「跟随全局」）并传 `hideSource` | **保留，不要回滚** |
| `apps/desktop/renderer/src/project-agent/BotModelControls.tsx` | **已完成并视觉验收**：新增 `hideSource?: boolean`，避免 `tier` 模式重复文案 | **保留，不要回滚** |
| `apps/desktop/renderer/src/project-agent/styles/bot-model-controls.css` | **已完成并视觉验收**：单列 `.bot-model-settings-row` 与 `.bot-model-settings-head` 样式 | **保留，不要回滚** |
| `apps/desktop/renderer/src/project-agent/BotAvatar.tsx` | 旧草稿（被用户否决的高饱和糖果色几何猫） | **按本文 §2 完整替换为路线 A 自然绘本猫** |
| `apps/desktop/renderer/src/project-agent/styles/bot-list.css` | 包含旧糖果猫样式草稿 | **按本文 §2 + §4 完整更新** |

> **Git / PR 纪律**：
> - 所有改动在本地 `codex/native-rust-cli` 提交并验证后，**切勿直接 `git push origin codex/native-rust-cli`**；请单独切功能分支（如 `feat/editorial-cat-avatars-and-worker-stream`）推送并提 PR 指向 `codex/native-rust-cli`。
> - 全程严禁修改用户真实的 `~/.peer-agent/` 目录，所有 E2E / 截图验证必须使用隔离临时 `PEER_AGENT_HOME`。
> - Rust 代码严格遵守 **零 `unsafe`** 铁律。

---

## 1. Phase 1（当前交付）文件变更总览

Phase 1 聚焦桌面端渲染层体验收口与 `ExecutorIcon` 执行器微标抽象，**不改动 Rust 运行时与协议持久化格式**，所有现有单测与协议契约 100% 保持兼容。

| 模块 | 文件路径（相对 `Peer-Agent/`） | 动作 | 核心职责 |
|---|---|---|---|
| **M1 头像** | `apps/desktop/renderer/src/project-agent/BotAvatar.tsx` | 重写生成态渲染 | 8 只自然毛色绘本猫（`viewBox="0 0 64 64"`）、3/4 豆豆眼与视线微跟随、柔圆领口、睡眠/思考/报错态、预留 `executorKind` / `showExecutorBadge` |
| **M1 头像样式** | `apps/desktop/renderer/src/project-agent/styles/bot-list.css` | 修改 `.bot-avatar*` | 绘本猫无硬描边/无廉价渐变样式、深色对比度适配、视线与呼吸微动效 |
| **M1 外观设置** | `apps/desktop/renderer/src/project-agent/drawer/BotSettingsTab.tsx` | 小幅优化 | 更新色板说明/无障碍文案（明确色板用于主题点缀而非染猫毛），保持 56px 绘本猫预览与「重新生成」一键切换不同猫造型 |
| **M2 执行器微标** | `apps/desktop/renderer/src/project-agent/ExecutorIcon.tsx` | **新建** | `ExecutorKind` 类型与 `ExecutorIcon` 组件；默认 `'peer'` 渲染自家 14px 极简小猫 CLI 微标，预留 `claude-code`/`codex`/`opencode`/`gemini-cli` |
| **M3 侧栏红框1** | `apps/desktop/renderer/src/project-agent/BotRow.tsx` | 修改 | 工作态副标题展示 `{running} 个工作中` / `{running} working`；去冗余噪音标签；保持安静时间/状态节奏 |
| **M3 侧栏红框1** | `apps/desktop/renderer/src/project-agent/BotSidebarTasks.tsx` | 修改 | 极细竖向引导线 + `[状态微标] + [ExecutorIcon] + [完整任务标题]`；移除行内「重验」按钮；默认 4 条 + `再显示 N 个任务` |
| **M3 侧栏红框1** | `apps/desktop/renderer/src/project-agent/BotListShell.tsx` | 修改 | 默认隐藏常驻大灰 `.bot-search-frame`，点击顶栏搜索图标或按 `⌘F`/`⌘K` 展开轻量内联过滤条（query 非空时自动保持可见） |
| **M3 侧栏样式** | `apps/desktop/renderer/src/project-agent/styles/bot-list.css` | 修改 `.bot-sidebar-task*` / `.bot-search*` | 废止纯黑 keycap 选中块，改用柔和霜纸选中态；增加竖向引导线与状态弧/点样式 |
| **M4 对话流红框2** | `apps/desktop/renderer/src/project-agent/conversation/ReplyTaskReferences.tsx` | 重构 | 无边框单行内联任务动态行：`[ExecutorIcon] 任务标题   [实时状态/短结论] ›`；保留 `data-session-id` 契约 |
| **M4 对话流样式** | `apps/desktop/renderer/src/project-agent/styles/bot-conversation.css` | 修改 `.bot-reply-task-references*` | 无边框无底色静息态、负水平出血左对齐正文、柔和 hover 态、语义状态文字色 |
| **M4 汇总条红框2** | `apps/desktop/renderer/src/project-agent/conversation/ComposerTouchBar.tsx` + `styles/bot-touchbar.css` | 微调 | 左侧融入轻量 `ExecutorIcon` / 状态微标与简洁 `{total} 个任务 · {running} 个运行中` 文案，视觉更轻盈 |
| **M5 抽屉修复** | `bot-drawer.css`, `BotPolicyFields.tsx`, `BotModelControls.tsx`, `bot-model-controls.css` | **保留现状** | 概况卡去多余线条 + `任务执行 · 跟随全局` 右对齐 |
| **单测与验收** | `apps/desktop/renderer/src/project-agent/**/*.test.ts` + E2E 脚本 | 补充与运行 | 补齐 `ExecutorIcon`、侧栏任务投影与内联任务流单测 + 亮/暗双主题实机截图验收 |

---

## 2. M1 详细规格：路线 A · 8 只自然毛色绘本猫（`BotAvatar.tsx`）

### 2.1 协议映射与向后兼容契约
- `packages/protocol/src/project.ts` 中的 `BOT_AVATAR_SHAPES` 与 `BOT_AVATAR_COLORS` **严禁改动**。
- `BotAvatar` 接收 props 扩展（全部新增项可选，零破坏调用方）：
  ```ts
  export interface BotAvatarProps {
    readonly avatar: BotAvatarModel;
    readonly label: string;
    readonly workspaceId: string;
    readonly mood?: BotAvatarMood;
    readonly animate?: boolean;
    /** 当前 Bot 绑定的执行器（Phase 1 默认 'peer'） */
    readonly executorKind?: ExecutorKind;
    /** 仅在多 CLI 模式或非默认执行器时置 true；默认 false（避免猫套猫） */
    readonly showExecutorBadge?: boolean;
  }
  ```
- **角色确定性映射**：
  ```ts
  const SHAPE_TO_CAT_ID: Readonly<Record<string, CatBreedId>> = {
    circle: 'midnight',      // 望月黑猫
    square: 'calico',        // 三花小猫
    pill: 'ginger-beret',    // 橘猫画师
    arch: 'siamese',         // 拿铁暹罗
    hex: 'blue-glasses',     // 蓝猫学者
    diamond: 'tuxedo',       // 奶牛绅士
    triangle: 'pearl-cat',   // 珍珠白猫
    star: 'tabby-scarf',     // 暖棕狸花
  };
  ```
  > 注意：如果 `avatar.kind === 'generated'` 且 `avatar.variant === undefined`（老档案），仍可沿用 `legacyVariant(workspaceId)` 做确定性映射，避免老用户全部撞成同一只猫。

### 2.2 精确几何与配色规范（`viewBox="0 0 64 64"`，已视觉验证）

所有 8 只绘本猫共享同一套温润几何骨架，确保成组排列（侧栏、首页欢迎卡、设置页）高度和谐统一：

1. **共用丰润猫头路径 (`CAT_HEAD`)**（更宽脸颊 + 偏低宽底圆润猫耳，绝无尖刺与兔耳感）：
   ```text
   M15.4 30.2 C14.6 24.4 16.0 17.6 18.8 17.2 C21.8 16.8 25.0 20.6 26.8 22.6 C29.8 22.0 34.4 22.0 37.4 22.6 C39.4 20.6 42.4 16.8 45.4 17.2 C48.2 17.6 49.4 24.4 48.6 30.2 C49.8 32.8 50.2 35.4 49.8 38.2 C48.8 45.2 41.8 49.6 32.0 49.6 C22.2 49.6 15.2 45.2 14.2 38.2 C13.8 35.4 14.2 32.8 15.4 30.2 Z
   ```
2. **共用柔圆悬空领口底座 (`SOFT_COLLAR`)**（绝无平切硬底边）：
   ```text
   M21.0 46.8 C23.0 52.8 27.2 55.2 32.0 55.2 C36.8 55.2 41.0 52.8 43.0 46.8 C39.5 48.8 35.8 49.6 32.0 49.6 C28.2 49.6 24.5 48.8 21.0 46.8 Z
   ```
3. **3/4 微侧脸五官层（`.bot-avatar-face` — 承接指针视线跟随 `--bot-gaze-x / --bot-gaze-y`）**：
   - **清醒态**：两颗极简竖直圆角豆豆眼（宽度 `3.0`、高度 `5.2`、`rx="1.5"`，默认位置 `x="23.2"` 与 `x="32.1"`，`y="33.2"`；望月黑猫眼色 `#FAF2E1`，其余 7 只猫眼色 `#28201B` 或 `#23272B`）。
   - **微柔鼻点**（仅非黑猫 7 款可选微弱点缀，绝不画三角鼻/`w` 嘴/胡须）：`<ellipse cx="29.4" cy="39.8" rx="1.3" ry="0.85" opacity="0.85" />`。
   - **睡眠态**（`animate && mood === 'idle'`）：两道柔和下弯闭眼短弧（`d="M22.4 35.6 Q24.6 37.6 26.8 35.6 M31.3 35.6 Q33.5 37.6 35.7 35.6"`，`stroke-width="1.8"`，`stroke-linecap="round"`，颜色随眼色），同样极度克制，不出现重线条。
   - **报错态**（`mood === 'error'`）：保持绘本温柔感，豆豆眼改为柔和砖红 `#A83B32`（黑猫为 `#F4A69E`），不画狰狞叉叉。
   - **思考/工作态**（`mood === 'working' || mood === 'thinking'`）：维持清醒豆豆眼 + 极其克制的微幅呼吸动效（复用 `useAvatarMotion`，尊重 `prefers-reduced-motion`）。
4. **8 只猫完整分层色值与装饰定义**：
   - **`midnight`（望月黑猫 · `circle`）**：
     - 领口：`SOFT_COLLAR('#C4553F')` + 奶白胸三角 `M27.2 48.5 C28.8 52.8 30.8 54.6 32.0 54.6 C33.2 54.6 35.2 52.8 36.8 48.5 Z` (`#F5EDE0`)
     - 猫头底色：`#353640`（炭靛黑，深色主题下仍与 `#1c1c1b` 侧栏清晰分离）
     - 裁剪内层：柔和耳蜗 `#505261`（左 `M18.8 20.2 C18.0 22.5 18.4 24.8 20.2 25.6 C21.8 24.8 22.4 22.6 21.0 20.4 Z`，右镜像）+ 下巴奶白 `<ellipse cx="30.2" cy="46.4" rx="9.2" ry="5.0" fill="#F4ECE0" />`
     - 项圈与新月：弧线 `M23.5 47.6 Q32.0 51.4 40.5 47.6` (`stroke="#E5AA3B"`, `stroke-width="2.2"`) + 新月 `M31.0 50.8 A2.2 2.2 0 1 1 29.4 54.3 A1.75 1.75 0 1 0 31.0 50.8 Z` (`#F3C85F`)
     - 眼色：`#FAF2E1`（无鼻点）
   - **`calico`（三花小猫 · `square`）**：
     - 领口：`SOFT_COLLAR('#C45A43')` + 领心 `#F7EFE2`
     - 猫头底色：`#FBF4E7`
     - 裁剪内层：左上暖橘斑 `M10 14 L30.8 14 C32.0 22.0 28.6 29.8 21.4 31.8 C16.8 33.0 13.0 31.2 10 28 Z` (`#DF8947`)；右上炭黑斑 `M36.5 14 L54 14 L53 34.5 C47.5 34.0 42.0 31.2 39.2 26.2 C37.2 22.5 36.6 18.2 36.5 14 Z` (`#3B3633`)；右颊微橘斑 `<ellipse cx="45.2" cy="41.2" rx="6.0" ry="4.6" fill="#E39759" opacity="0.88" />`
     - 鼻点：`#CE9482`
   - **`ginger-beret`（橘猫画师 · `pill`）**：
     - 领口：`SOFT_COLLAR('#475B6C')` + 奶白小领 `#FBF3E4`
     - 猫头底色：`#E6A15A`；裁剪内耳蜗 `#F5CA98` + 奶油腮颊 `<ellipse cx="30.5" cy="44.2" rx="13.8" ry="7.4" fill="#FBF2E3" />`
     - 倾斜鼠尾草绿贝雷帽：`M21.0 23.6 C22.2 15.2 34.8 13.0 42.8 18.4 C44.8 19.8 44.2 23.0 40.8 23.8 C35.2 25.0 26.5 25.0 21.0 23.6 Z` (`#5D7D67`) + 帽蒂 `M33.2 15.5 C33.5 13.4 35.0 12.6 36.2 13.2` (`stroke="#486351"`, `stroke-width="1.7"`)
     - 鼻点：`#C9826C`
   - **`siamese`（拿铁暹罗 · `arch`）**：
     - 领口：`SOFT_COLLAR('#4D6C8E')` + 浅牛仔蓝围巾叠层 `#6285A8`
     - 猫头底色：`#F2E6D5`；裁剪内左右焦糖耳 `#6F5344` + 柔雾咖啡面罩 `<ellipse cx="29.4" cy="36.8" rx="10.0" ry="7.0" fill="#B5927B" opacity="0.48" />`
     - 鼻点：`#5D4437`
   - **`blue-glasses`（蓝猫学者 · `hex`）**：
     - 领口：`SOFT_COLLAR('#D5C4AD')` + 奶白内搭三角 `#F6F0E6`
     - 猫头底色：`#8F9EAB`；裁剪内浅雾耳蜗 `#B5C1CB` + 银白下巴 `<ellipse cx="30.5" cy="46.2" rx="10.2" ry="4.8" fill="#E7ECF1" />`
     - 轻盈暖黄铜细框椭圆眼镜（注意 `stroke-width="1.2"`、`rx="5.1" ry="4.2"`，严禁粗圆框变大眼青蛙）：左 `(24.7, 35.8)`、右 `(34.0, 35.8)`、鼻梁 `M29.8 35.6 H28.9`，`stroke="#C59C54"` `stroke-opacity="0.85"`
     - 眼色：`#23272B`，鼻点：`#6E7B87`
   - **`tuxedo`（奶牛绅士 · `diamond`）**：
     - 领口：`SOFT_COLLAR('#343235')` + 象牙白领口三角 `#FAF6EE` + 酒红小领结 (`#BA4839` / 中心结 `#9E392C`)
     - 猫头底色：`#FAF6EE`；裁剪内不对称炭黑斜刘海 `M12 14 L52 14 L52 31 C44.5 30.0 38.0 26.8 31.8 27.8 C25.5 28.8 20.5 26.2 13 25.5 Z` + 右鬓角 `M34.5 24 C38.0 28.5 43.2 32.8 49.5 33.8 L52 20 Z` (`#343235`)
     - 鼻点：`#C69083`
   - **`pearl-cat`（珍珠白猫 · `triangle`）**：
     - 后层垂坠金黄头巾尾：`M40.5 24.5 C49.5 27.5 53.2 37.5 49.8 48.8 C46.2 49.8 42.5 47.6 41.2 43.5 Z` (`#E5A52E`)
     - 领口：`SOFT_COLLAR('#62798F')`
     - 猫头底色：`#FAF4E8`；裁剪内柔粉耳蜗 `#F0D3CA` + 非对称斜裹钴蓝头巾 `M13 28.5 C20.5 20.5 34.5 19.5 47.5 27.5 C49.5 29.0 50.5 33.0 49.5 36.5 C43.0 28.0 28.5 24.8 13.5 31.8 Z` (`#2A62B2`)
     - 单颗纯白珍珠：`<circle cx="43.0" cy="42.8" r="2.1" fill="#FFFFFF" />`
     - 鼻点：`#D6A297`
   - **`tabby-scarf`（暖棕狸花 · `star`）**：
     - 领口：`SOFT_COLLAR('#5A4D45')`
     - 猫头底色：`#CEBCA3`；裁剪内柔棕额帽 `M13 14 L51 14 L51 27.5 C43 26.0 37.0 24.0 32.0 25.8 C27.0 24.0 21.0 26.0 13 27.5 Z` (`#8E745E`) + 暖白嘴腮 `<ellipse cx="30.2" cy="44.6" rx="12.0" ry="6.4" fill="#F4ECDF" />`
     - 暖赤陶围巾：`M21.8 46.8 C26.2 49.8 37.8 49.8 42.2 46.8 C43.0 50.0 40.8 53.0 38.0 53.4 C33.5 54.0 28.8 54.0 24.8 53.2 C22.2 52.6 21.0 49.6 21.8 46.8 Z` (`#C4563F`) + 围巾尾 (`#AD4631`)
     - 鼻点：`#8D6957`

#### 2.2.1 全部 8 只绘本猫精确 SVG 路径源码表（已实景验收 v2，可直接复制进 `BotAvatar.tsx`）

以下路径全部基于 `viewBox="0 0 64 64"`，经浅/深双主题 `56px` 与 `36px` 实景视觉验收；实施时请直接使用以下精确坐标（切勿自由改写成尖角几何猫）：

```tsx
// 共用头部轮廓与柔圆领口
export const CAT_HEAD_PATH =
  'M15.4 30.2 C14.6 24.4 16.0 17.6 18.8 17.2 C21.8 16.8 25.0 20.6 26.8 22.6 C29.8 22.0 34.4 22.0 37.4 22.6 C39.4 20.6 42.4 16.8 45.4 17.2 C48.2 17.6 49.4 24.4 48.6 30.2 C49.8 32.8 50.2 35.4 49.8 38.2 C48.8 45.2 41.8 49.6 32.0 49.6 C22.2 49.6 15.2 45.2 14.2 38.2 C13.8 35.4 14.2 32.8 15.4 30.2 Z';

export const SOFT_COLLAR_PATH =
  'M21.0 46.8 C23.0 52.8 27.2 55.2 32.0 55.2 C36.8 55.2 41.0 52.8 43.0 46.8 C39.5 48.8 35.8 49.6 32.0 49.6 C28.2 49.6 24.5 48.8 21.0 46.8 Z';

// 共用左右柔和耳蜗（置于 clipPath 内）
const LEFT_INNER_EAR = 'M18.8 20.2 C18.0 22.4 18.5 24.6 20.2 25.4 C21.8 24.6 22.4 22.5 21.0 20.4 Z';
const RIGHT_INNER_EAR = 'M45.2 20.2 C46.0 22.4 45.5 24.6 43.8 25.4 C42.2 24.6 41.6 22.5 43.0 20.4 Z';

// 各角色精确补充图层（按渲染前后顺序）：
// 1) midnight (circle):
//    collarFill='#C4553F'
//    collarInner='M27.2 48.5 C28.8 52.8 30.8 54.6 32.0 54.6 C33.2 54.6 35.2 52.8 36.8 48.5 Z' (#F5EDE0)
//    headFill='#353640', innerEarFill='#505261', chin=<ellipse cx="30.2" cy="46.4" rx="9.2" ry="5.0" fill="#F4ECE0"/>
//    collarArc='M23.5 47.6 Q32.0 51.4 40.5 47.6' (stroke='#E5AA3B' strokeWidth=2.2 strokeLinecap='round')
//    crescent='M31.0 50.8 A2.2 2.2 0 1 1 29.4 54.3 A1.75 1.75 0 1 0 31.0 50.8 Z' (#F3C85F)
//    eyeFill='#FAF2E1', eyeOffset=(-0.5, 0.2), noseFill=null
//
// 2) calico (square):
//    collarFill='#C45A43'
//    collarInner='M27.4 48.8 C29.0 52.8 30.8 54.4 32.0 54.4 C33.2 54.4 35.0 52.8 36.6 48.8 Z' (#F7EFE2)
//    headFill='#FBF4E7'
//    clipPatches:
//      'M10 14 L30.8 14 C32.0 22.0 28.6 29.8 21.4 31.8 C16.8 33.0 13.0 31.2 10 28 Z' (#DF8947)
//      'M36.5 14 L54 14 L53 34.5 C47.5 34.0 42.0 31.2 39.2 26.2 C37.2 22.5 36.6 18.2 36.5 14 Z' (#3B3633)
//      <ellipse cx="45.2" cy="41.2" rx="6.0" ry="4.6" fill="#E39759" opacity="0.88"/>
//    eyeFill='#28201B', eyeOffset=(-0.4, 0.4), noseFill='#CE9482'
//
// 3) ginger-beret (pill):
//    collarFill='#475B6C'
//    collarInner='M26 48.6 Q32 52.4 38 48.6 L36.4 53.0 Q32 54.8 27.6 53.0 Z' (#FBF3E4)
//    headFill='#E6A15A', innerEarFill='#F5CA98'
//    muzzle=<ellipse cx="30.5" cy="44.2" rx="13.8" ry="7.4" fill="#FBF2E3"/>
//    beret='M21.0 23.6 C22.2 15.2 34.8 13.0 42.8 18.4 C44.8 19.8 44.2 23.0 40.8 23.8 C35.2 25.0 26.5 25.0 21.0 23.6 Z' (#5D7D67)
//    beretStem='M33.2 15.5 C33.5 13.4 35.0 12.6 36.2 13.2' (stroke='#486351' strokeWidth=1.7 strokeLinecap='round')
//    eyeFill='#28201B', eyeOffset=(-0.4, 0.7), noseFill='#C9826C'
//
// 4) siamese (arch):
//    collarFill='#4D6C8E'
//    collarScarf='M23.5 47.6 Q32 52.0 40.5 47.6 L39.2 52.4 Q32 55.2 24.8 52.4 Z' (#6285A8)
//    headFill='#F2E6D5'
//    clipPatches:
//      'M12 14 L27 14 L25 27.5 C20.5 28.0 16.0 26.8 12 24 Z' (#6F5344)
//      'M37 14 L52 14 L52 24.5 C48.0 27.0 43.5 28.0 39 27.5 Z' (#6F5344)
//      <ellipse cx="29.4" cy="36.8" rx="10.0" ry="7.0" fill="#B5927B" opacity="0.48"/>
//    eyeFill='#28201B', eyeOffset=(-0.4, 0.4), noseFill='#5D4437'
//
// 5) blue-glasses (hex):
//    collarFill='#D5C4AD'
//    collarInner='M27.6 48.5 L32 53.5 L36.4 48.5 Z' (#F6F0E6)
//    headFill='#8F9EAB', innerEarFill='#B5C1CB'
//    chin=<ellipse cx="30.5" cy="46.2" rx="10.2" ry="4.8" fill="#E7ECF1"/>
//    glasses:
//      <ellipse cx="24.7" cy="35.8" rx="5.1" ry="4.2" stroke="#C59C54" strokeWidth="1.2" strokeOpacity="0.85" fill="#FFFFFF" fillOpacity="0.1"/>
//      <ellipse cx="34.0" cy="35.8" rx="5.1" ry="4.2" stroke="#C59C54" strokeWidth="1.2" strokeOpacity="0.85" fill="#FFFFFF" fillOpacity="0.1"/>
//      <path d="M29.8 35.6 H28.9" stroke="#C59C54" strokeWidth="1.2" strokeOpacity="0.85"/>
//    eyeFill='#23272B', eyeOffset=(-0.4, 0.4), noseFill='#6E7B87'
//
// 6) tuxedo (diamond):
//    collarFill='#343235'
//    collarInner='M27.4 48.4 L31.5 54.0 L35.6 48.4 Z' (#FAF6EE)
//    headFill='#FAF6EE'
//    clipPatches:
//      'M12 14 L52 14 L52 31 C44.5 30.0 38.0 26.8 31.8 27.8 C25.5 28.8 20.5 26.2 13 25.5 Z' (#343235)
//      'M34.5 24 C38.0 28.5 43.2 32.8 49.5 33.8 L52 20 Z' (#343235)
//    bowTie='M27.8 49.0 L31.5 50.8 L27.8 52.6 Z M35.2 49.0 L31.5 50.8 L35.2 52.6 Z' (#BA4839)
//    bowKnot=<circle cx="31.5" cy="50.8" r="1.25" fill="#9E392C"/>
//    eyeFill='#261F1B', eyeOffset=(-0.4, 0.5), noseFill='#C69083'
//
// 7) pearl-cat (triangle):
//    backDrape='M40.5 24.5 C49.5 27.5 53.2 37.5 49.8 48.8 C46.2 49.8 42.5 47.6 41.2 43.5 Z' (#E5A52E)
//    collarFill='#62798F', headFill='#FAF4E8', innerEarFill='#F0D3CA'
//    clipBand='M13 28.5 C20.5 20.5 34.5 19.5 47.5 27.5 C49.5 29.0 50.5 33.0 49.5 36.5 C43.0 28.0 28.5 24.8 13.5 31.8 Z' (#2A62B2)
//    pearl=<circle cx="43.0" cy="42.8" r="2.1" fill="#FFFFFF"/>
//    eyeFill='#28201B', eyeOffset=(-0.6, 0.7), noseFill='#D6A297'
//
// 8) tabby-scarf (star):
//    collarFill='#5A4D45', headFill='#CEBCA3'
//    clipCap='M13 14 L51 14 L51 27.5 C43 26.0 37.0 24.0 32.0 25.8 C27.0 24.0 21.0 26.0 13 27.5 Z' (#8E745E)
//    clipMuzzle=<ellipse cx="30.2" cy="44.6" rx="12.0" ry="6.4" fill="#F4ECDF"/>
//    scarfMain='M21.8 46.8 C26.2 49.8 37.8 49.8 42.2 46.8 C43.0 50.0 40.8 53.0 38.0 53.4 C33.5 54.0 28.8 54.0 24.8 53.2 C22.2 52.6 21.0 49.6 21.8 46.8 Z' (#C4563F)
//    scarfTail='M34.8 50.8 L38.4 50.2 L39.2 55.6 C37.4 56.2 35.8 56.0 34.8 55.2 Z' (#AD4631)
//    eyeFill='#28201B', eyeOffset=(-0.4, 0.4), noseFill='#8D6957'
//
// 共用清醒眼坐标（基准 x1=23.6, x2=32.5, y=32.8，叠加各角色 eyeOffset(dx, dy)）：
//   <rect x={23.6 + dx} y={32.8 + dy} width="3.0" height="5.2" rx="1.5" fill={eyeFill} />
//   <rect x={32.5 + dx} y={32.8 + dy} width="3.0" height="5.2" rx="1.5" fill={eyeFill} />
```

### 2.3 `BotAvatar.tsx` 细节注意事项
- 每个 `<clipPath id={...}>` 必须使用 `useId()` 派生的唯一 ID，防止侧栏 + 顶栏 + 抽屉同时渲染同一只猫时 SVG `clipPath` ID 冲突导致裁切失效！
- **禁止**在 `.bot-avatar-generated svg` 上添加厚重 `drop-shadow` 或塑料光泽渐变；仅保留极轻自然贴合纸面的呈现（浅色主题下对纯白/奶白猫可加极轻 `filter: drop-shadow(0 1px 1.5px rgba(28, 25, 22, 0.08))` 保证浅色纸面边缘柔润清晰）。
- 保留 `data-avatar-kind="generated"`、`data-avatar-shape={visualShape}`、`data-avatar-breed={catId}`、`data-avatar-mood={mood}`、`data-avatar-sleeping={sleeping}` 以便自动化测试断言。
- 保留 `botAvatarDisplayColor(color)` 导出函数（`BotConversation.tsx` 与 `BotSettingsTab.tsx` 均有引用）。
- 在 `BotSettingsTab.tsx` 外观设置区域：
  - 将颜色色板标签从易产生误解的「颜色」微调或补充提示为「对话点缀色」（或保留既有 i18n 键不破译文、加一行简短辅助说明），明确点选色板更新的是对话主题色而非把猫染成绿/紫色；
  - 「重新生成」按钮继续调用 `regenerateAvatar: true`，让用户一键轮换不同绘本猫造型。

---

## 3. M2 详细规格：`ExecutorIcon.tsx`（自家小猫 CLI 执行器微标）

新建文件：`apps/desktop/renderer/src/project-agent/ExecutorIcon.tsx`

### 3.1 接口与默认语义
```ts
export type ExecutorKind = 'peer' | 'claude-code' | 'codex' | 'opencode' | 'gemini-cli';

export interface ExecutorIconProps {
  readonly kind?: ExecutorKind;
  readonly size?: number;
  readonly className?: string;
  readonly title?: string;
}
```
- `kind` 缺省时恒为 `'peer'`。
- 导出辅助函数 `executorDisplayName(kind: ExecutorKind, isZh: boolean): string`：
  - `'peer'` → `isZh ? 'Peer 小猫 CLI' : 'Peer Native CLI'`
  - `'claude-code'` → `'Claude Code'`
  - `'codex'` → `'Codex CLI'`
  - `'opencode'` → `'OpenCode'`
  - `'gemini-cli'` → `'Gemini CLI'`

### 3.2 自家「Peer 小猫 CLI」16×16 单色剪影微标规范
设计原则：**极简、高辨识、14px 下不糊成一团、与 Peer 黑猫望月 Logo 同源、自适应浅/深主题（使用 `currentColor`）**：
```tsx
// viewBox="0 0 16 16" — 简洁圆润猫耳 + 侧坐/头像剪影 + 两点镂空微眼
<svg viewBox="0 0 16 16" width={size} height={size} fill="none" aria-hidden="true" className={cls}>
  <path
    d="M3.2 6.8 C2.9 4.7 3.5 2.5 4.6 2.4 C5.6 2.3 6.5 3.6 7.0 4.3 C7.6 4.1 8.4 4.1 9.0 4.3 C9.5 3.6 10.4 2.3 11.4 2.4 C12.5 2.5 13.1 4.7 12.8 6.8 C13.3 7.7 13.5 8.7 13.3 9.7 C12.9 12.1 10.9 13.6 8.0 13.6 C5.1 13.6 3.1 12.1 2.7 9.7 C2.5 8.7 2.7 7.7 3.2 6.8 Z"
    fill="currentColor"
  />
  {/* 两颗极简镂空微眼（用 paper/surface 背景色或 mask 切出，14px 依然清晰灵动） */}
  <rect x="5.4" y="7.5" width="1.15" height="2.0" rx="0.58" fill="var(--executor-icon-cutout, var(--paper-sheet, #ffffff))" />
  <rect x="8.8" y="7.5" width="1.15" height="2.0" rx="0.58" fill="var(--executor-icon-cutout, var(--paper-sheet, #ffffff))" />
</svg>
```
> 建议优先用 SVG `<mask>`（带 `useId()` 唯一 mask ID）镂空两颗微眼，这样无论底色是白色、浅灰 hover、深色侧栏还是毛玻璃背景，眼睛都真正透明透底，完全不依赖 `--paper-sheet` 猜测背景色！

### 3.3 后续外部 CLI 图标占位
- 在同一文件内预先定义 `'claude-code'`（暖珊瑚 8 向星芒 `#D97757`）、`'codex'`（简洁双环结 `currentColor`）、`'opencode'` / `'gemini-cli'`（简洁菱星/终端符号），便于 Phase 3 直接复用而无需改任何前端组件签名。

---

## 4. M3 详细规格：红框 1 · 侧栏「Bot → 活跃子任务树」升级

### 4.1 `BotRow.tsx` 改造细节
1. **工作态副标题优先**：
   - 计算 `const activeCount = item.state.running;`
   - 当 `activeCount > 0` 时，副标题位显示简洁的 **`{activeCount} 个工作中`**（英文 `{activeCount} working`），视觉使用轻柔 `--graphite-soft`（不叠加噪杂动画点或鲜艳文字）；
   - 当 `activeCount === 0` 时，保持现有最近回复 `preview` 与右侧时间 `timeLabel`。
2. **头像与状态点**：
   - `BotAvatar` 保持 `34px`–`36px` 尺寸；
   - 移除此前贴在头像角落多余的 `.bot-avatar-pip`（当子任务已直接展示在 Bot 下方或 Bot 副标题已显示 `N 个工作中` 时，角落圆点显得重复；保留右侧安静的 `needsYou` 小徽章或 `bot-unread` 6px 实心圆点）。

### 4.2 `BotSidebarTasks.tsx` 重构细节
1. **默认展示条数**：`const DEFAULT_VISIBLE = 4;`（兼顾 3–5 个并行 worker 一屏可见又不拉爆侧栏）。
2. **单行 DOM 结构（彻底移除 `.bot-sidebar-task-tag` 胶囊！）**：
   ```tsx
   <button
     key={task.sessionId}
     type="button"
     className={`bot-sidebar-task${selected ? ' is-selected' : ''}`}
     data-session-id={task.sessionId}
     data-task-tone={visual.tone}
     aria-current={selected ? 'page' : undefined}
     title={`${task.title} · ${visual.label}`}
     onClick={(event) => {
       event.stopPropagation();
       onOpenTask(workspaceId, task.sessionId);
     }}
   >
     <span className={`bot-sidebar-task-state${visual.spin ? ' is-spinning' : ''}`} data-tone={visual.tone} aria-hidden="true" />
     <ExecutorIcon kind={task.executorKind ?? 'peer'} size={14} className="bot-sidebar-task-cli" />
     <span className="bot-sidebar-task-title">{task.title}</span>
   </button>
   ```
   - **状态微标视觉映射（`.bot-sidebar-task-state`）**：
     - `running / starting / verifying / result_ready(owner=bot)`：10px 轻柔半弧旋转环（`border: 1.5px solid transparent; border-top-color: #d9822b; border-right-color: #d9822b;` 暖琥珀色，对齐参考图里的橙黄小旋转弧，柔和耐看）。
     - `waiting_user / followUp.owner === 'user' / verification_failed / failed`：6px 实心点（待用户确认用暖琥珀 `#d96b27`，核验失败/执行失败用克制砖红 `var(--state-danger)`）。
     - `result_ready`（已完成待交接 / 正常就绪）：6px 柔和翡翠绿点 `var(--state-success)`。
     - `queued`：6px 浅灰空心环 `border: 1.4px solid var(--graphite-fade)`。
   - **彻底移除**：
     - 移除右侧的 `.bot-sidebar-task-tag`（不再在侧栏塞「待批」「重验」「失败」「核验」文字块；完整状态通过 `title` tooltip、状态点语义和右侧主舞台呈现）；
     - 绝对不加项目文件夹 `📁 xxx` 胶囊，把所有水平宽度留给 `.bot-sidebar-task-title`！
3. **溢出折叠行**：
   - 文案统一为轻盈风格：`isZh ? \`再显示 ${hiddenCount} 个任务\` : \`Show ${hiddenCount} more\``；展开后提供 `isZh ? '收起部分任务' : 'Show fewer'`。

### 4.3 `bot-list.css` 侧栏任务与选中态精确样式
- **极细竖向引导线**：
  ```css
  .bot-sidebar-tasks {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 1px;
    padding: 2px 4px 6px 32px;
  }
  .bot-sidebar-tasks::before {
    content: '';
    position: absolute;
    left: 24px;
    top: 2px;
    bottom: 10px;
    width: 1px;
    background: color-mix(in srgb, var(--graphite-base) 8%, transparent);
    pointer-events: none;
  }
  ```
- **三列紧凑网格 + 柔和霜纸选中态（彻底废止 `--chrome-keycap-bg` 黑块！）**：
  ```css
  .bot-sidebar-task {
    display: grid;
    grid-template-columns: 12px 15px minmax(0, 1fr);
    align-items: center;
    gap: 6px;
    width: 100%;
    min-height: 28px;
    padding: 4px 8px;
    border: 0;
    border-radius: var(--ui-radius-row, 8px);
    background: transparent;
    color: var(--graphite-soft);
    font: inherit;
    font-size: 12.2px;
    text-align: left;
    cursor: pointer;
    transition: background var(--za-motion-fast) ease, color var(--za-motion-fast) ease;
  }
  .bot-sidebar-task:hover:not(.is-selected) {
    background: var(--chrome-glass-hover, var(--chrome-hover));
    color: var(--graphite-base);
  }
  .bot-sidebar-task.is-selected {
    background: color-mix(in srgb, var(--graphite-base) 8%, transparent);
    color: var(--graphite-base);
    font-weight: 560;
  }
  [data-theme="dark"] .bot-sidebar-task.is-selected {
    background: color-mix(in srgb, #ffffff 11%, transparent);
    color: var(--graphite-base);
  }
  .bot-sidebar-task-cli {
    color: var(--graphite-soft);
    opacity: 0.85;
  }
  .bot-sidebar-task.is-selected .bot-sidebar-task-cli,
  .bot-sidebar-task:hover .bot-sidebar-task-cli {
    color: var(--graphite-base);
    opacity: 1;
  }
  ```

### 4.4 `BotListShell.tsx` 侧栏搜索框降噪（兼容全部快捷键与测试）
- 新增本地状态 `const [searchOpen, setSearchOpen] = useState(false);`，`const showSearchInput = searchOpen || list.query.length > 0;`。
- 静息态（`!showSearchInput`）不渲染占空间的 `.bot-search-frame` 大灰框，仅由 `.bot-sidebar-utilbar` 中的搜索按钮触发（点击展开并 `focus()`；若外部传了 `onOpenSearch` 则走全局搜索面板，否则展开侧栏内联过滤框）；快捷键 `list-search` 触发时同样先 `setSearchOpen(true)` 再聚焦 `searchRef`；按 `Escape` 且输入为空时自动收起。
- 核对已有前端测试（`botVersionPlacement.test.ts` 等），确保顶栏 `Peer` + 版本号与右侧 `+` 新建按钮 DOM 位置契约保持 100% 通过。

---

## 5. M4 详细规格：红框 2 · 主对话流内联无边框任务动态 & Touch Bar 打磨

### 5.1 `ReplyTaskReferences.tsx` 重构（主对话流内联单行动态）
在 `ContinuousReply.tsx` 中紧跟回复正文（与 `InlineInteractiveReplies` 之后、`ReplyPresence` 之前/附近）渲染，彻底告别重底色块：

```tsx
export function ReplyTaskReferences({ messages, workIndex, i18n, onOpen }: {
  readonly messages: readonly BotChatMessage[];
  readonly workIndex: BotWorkIndex;
  readonly i18n: I18nRuntime;
  readonly onOpen: (sessionId: string) => void;
}) {
  const references = replyTaskReferences(messages, workIndex);
  if (!references.length) return null;
  const isZh = Boolean(i18n.locale?.startsWith('zh'));

  return (
    <div
      className="bot-reply-task-references bot-inline-worker-feed"
      role="group"
      aria-label={i18n.t('projectAgent.chat.work.heading')}
    >
      {references.map((row) => {
        const title = row.session?.title && row.session.title !== row.id
          ? row.session.title
          : i18n.t('projectAgent.chat.work.related');
        const statusInfo = inlineWorkerStatus(row, i18n, isZh);
        return (
          <button
            type="button"
            className="bot-inline-worker-row"
            key={row.id}
            data-session-id={row.id}
            data-tone={statusInfo.tone}
            title={`${title} · ${statusInfo.text}`}
            onClick={() => onOpen(row.id)}
          >
            <ExecutorIcon kind="peer" size={14} className="bot-inline-worker-cli" />
            <span className="bot-inline-worker-title">{title}</span>
            <span className="bot-inline-worker-status">{statusInfo.text}</span>
            <PeerIcon name="chevronRight" size={13} className="bot-inline-worker-arrow" />
          </button>
        );
      })}
    </div>
  );
}
```

- **`inlineWorkerStatus(row, i18n, isZh)` 精确状态文案与语义色**：
  - `row.session?.followUp?.owner === 'user' || row.status === 'waiting_user'` → `{ text: isZh ? '待你确认' : 'Needs decision', tone: 'warn' }`
  - `row.status === 'result_ready' && row.session?.followUp?.reason === 'verification_failed'` → `{ text: isZh ? '核验未通过' : 'Verification failed', tone: 'danger' }`
  - `row.status === 'failed'` → `{ text: isZh ? '执行失败' : 'Execution failed', tone: 'danger' }`
  - `row.status === 'verifying'` → `{ text: isZh ? '核验中' : 'Verifying', tone: 'active' }`
  - `row.status === 'running' || row.status === 'starting'` → `{ text: isZh ? '执行中' : 'Running', tone: 'active' }`
  - `row.status === 'accepted'` → `{ text: isZh ? '已完成' : 'Completed', tone: 'good' }`
  - `row.status === 'cancelled' || row.status === 'superseded'` → `{ text: isZh ? '已停止' : 'Stopped', tone: 'muted' }`
  - 兜底：复用 `i18n.t('projectAgent.chat.sessionState.' + row.status)`，`tone: 'muted'`。

### 5.2 `bot-conversation.css` 内联单行任务动态样式
```css
.bot-reply-task-references.bot-inline-worker-feed {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 8px;
  min-width: 0;
  max-width: min(680px, 100%);
}

.bot-inline-worker-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: calc(100% + 12px);
  margin-inline: -6px;
  min-height: 30px;
  padding: 4px 6px;
  border: 0;
  border-radius: var(--ui-radius-control-compact, 7px);
  background: transparent;
  color: var(--graphite-base);
  font: inherit;
  font-size: 13px;
  line-height: 1.45;
  text-align: left;
  cursor: pointer;
  transition: background var(--za-motion-fast) var(--za-ease-standard);
}

.bot-inline-worker-row:is(:hover, :focus-visible) {
  background: var(--chrome-hover);
}

.bot-inline-worker-row:focus-visible {
  outline: 1.5px solid var(--azure-seal);
  outline-offset: -1px;
}

.bot-inline-worker-cli {
  flex: none;
  color: var(--graphite-soft);
}

.bot-inline-worker-title {
  flex: 0 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--graphite-base);
  font-weight: 520;
}

.bot-inline-worker-status {
  flex: none;
  font-size: 12px;
  font-weight: 450;
  color: var(--graphite-fade);
  white-space: nowrap;
}

.bot-inline-worker-row[data-tone="warn"] .bot-inline-worker-status { color: var(--state-confirm); }
.bot-inline-worker-row[data-tone="danger"] .bot-inline-worker-status { color: var(--state-danger); }
.bot-inline-worker-row[data-tone="active"] .bot-inline-worker-status { color: var(--graphite-soft); }
.bot-inline-worker-row[data-tone="good"] .bot-inline-worker-status { color: var(--state-success); }

.bot-inline-worker-arrow {
  flex: none;
  color: var(--graphite-fade);
  transition: transform var(--za-motion-fast) ease, color var(--za-motion-fast) ease;
}

.bot-inline-worker-row:hover .bot-inline-worker-arrow {
  color: var(--graphite-base);
  transform: translateX(2px);
}
```
> **注意**：不要删除 `.bot-reply-bar` 通用样式，因为引用气泡（`ReplyAnchors` / `.bot-reply-source` / `.bot-user-quote`）仍在复用 `.bot-reply-bar`！只针对 `.bot-reply-task-references` 切换到 `.bot-inline-worker-feed` + `.bot-inline-worker-row`。

### 5.3 `ComposerTouchBar.tsx` + `bot-touchbar.css` 轻量化打磨
- 在 `props.kind === 'bot'` 分支中：
  - 当 `summary.total > 0` 时，左侧按钮采用轻盈的 **`[ExecutorIcon (13px) 或状态微标] {summary.total} 个任务 · {summaryText} ⌄`**（英文 `{summary.total} workers · {summaryText}`），去掉多余冗余括号与生硬分割，贴合参考图里 `3 workers · 3 running ⌄` 的直观节奏；
  - 当 `isIdle` 且 `props.historyTotal === 0` 时，维持安静低存在感浅色文案（`--graphite-fade`），不抢输入区焦点。

---

## 6. M5：已验收抽屉修复清单（保持完整，勿回滚）

1. `bot-drawer.css`：
   - `.bot-overview-tab .bot-overview-details`：无内部竖线、`gap: 14px 20px; padding: 15px 16px;`；
   - `.bot-overview-tab .bot-overview-details .bot-overview-cap-link`：无边框、全宽 hover 悬停行、右侧 `chevronRight`；
   - `.bot-drawer-body .bot-model-settings-head`：`display: flex; justify-content: space-between; align-items: baseline;`。
2. `BotPolicyFields.tsx` + `BotModelControls.tsx` + `bot-model-controls.css`：
   - 全部 7 个模型角色行（对话模型、任务执行、复核及折叠的高级角色）均将「跟随全局 / 自动选择」移至角色标题行右侧，下拉框下方零悬空文案。

---

## 7. Phase 2–4 完整技术蓝图：可插拔多 CLI 执行器架构

本节供 Phase 2 及后续迭代直接按契约实施（Phase 1 不需修改 Rust crate）。

### 7.1 Protocol 层扩展（`packages/protocol/src/executor.ts`）
```ts
export type WorkerExecutorKind = 'peer' | 'claude-code' | 'codex' | 'opencode' | 'gemini-cli';

export interface WorkerExecutorRef {
  readonly kind: WorkerExecutorKind;
  /** 可选：该 CLI 下的预设档案或模型覆盖（仅透传给对应适配器） */
  readonly profile?: string;
}

export interface BotExecutorPolicy {
  /** Bot 委派子任务时的默认执行器，缺省等同于 'peer' */
  readonly defaultWorkerExecutor?: WorkerExecutorRef;
  /** 明确禁止该 Bot 使用的外部 CLI（安全策略收窄） */
  readonly deniedExecutorKinds?: readonly WorkerExecutorKind[];
}

export interface DetectedCliExecutor {
  readonly kind: WorkerExecutorKind;
  readonly available: boolean;
  readonly binaryPath?: string;
  readonly version?: string;
  readonly authState: 'ready' | 'unauthenticated' | 'unknown' | 'unavailable';
  readonly reason?: string;
}
```
- `BotProfile` 新增可选字段 `readonly executorPolicy?: BotExecutorPolicy | null;`
- `BotListSession` / `WorkSession` 新增可选字段 `readonly executor?: WorkerExecutorRef;`（未显式记录的历史会话在投影层统一归为 `{ kind: 'peer' }`）。

### 7.2 Rust `WorkerExecutor` Trait 定义（`crates/peer-project-agent/src/executors/mod.rs`，零 `unsafe`）

```rust
use peer_protocol::LocalAccessLevel;
use peer_runtime::CancellationToken;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tokio::sync::mpsc;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum WorkerExecutorKind {
    Peer,
    ClaudeCode,
    Codex,
    Opencode,
    GeminiCli,
}

#[derive(Debug, Clone)]
pub struct ExecutorSpawnContext {
    pub workspace_id: String,
    pub session_id: String,
    pub plan_id: String,
    /// 始终由 GoalWorktreeAdapter 分配的隔离工作目录，外部 CLI 不可越界
    pub working_dir: PathBuf,
    pub prompt: String,
    pub access_level: LocalAccessLevel,
    /// 若支持续跑，传入上轮外部 CLI 会话句柄
    pub resume_handle: Option<String>,
    /// 仅包含该执行器白名单允许的环境变量，禁止透传无关 Vault 密钥
    pub env_overrides: Vec<(String, String)>,
    pub cancel: CancellationToken,
}

#[derive(Debug, Clone)]
pub enum ExecutorEvent {
    PhaseChanged { phase: String, summary: Option<String> },
    ToolActivity { name: String, summary: String, status: String },
    OutputDelta { text: String },
    /// 桥接回 Peer ApprovalStore 审批卡
    PermissionRequested { request_id: String, capability: String, summary: String },
    SessionHandle { external_session_id: String },
    Completed { final_report: String, exit_code: i32 },
    Failed { code: String, message: String, retryable: bool },
}

pub trait WorkerExecutor: Send + Sync {
    fn kind(&self) -> WorkerExecutorKind;
    fn run_episode(
        &self,
        ctx: ExecutorSpawnContext,
        events: mpsc::Sender<ExecutorEvent>,
    ) -> Result<(), String>;
}
```

### 7.3 `SessionSupervisor` 替换点与统一核验闭环
1. **抽出 `PeerNativeExecutor`**：将当前 `crates/peer-project-agent/src/supervisor.rs` 中直接调用 `peer_runtime::native_exec::execute_plan` / `recover_plan` 的逻辑封装为 `PeerNativeExecutor`，零行为变更通过全部既有 Rust 100+ 单测与 `ts_rust_parity` 测试。
2. **注册表分发**：`SessionSupervisor` 持有 `Arc<ExecutorRegistry>`，依据 `session.executor.kind` 路由至对应 `WorkerExecutor`。
3. **统一核验与收口（不信任外部 CLI 自报成功）**：
   - `ExecutorEvent::Completed { final_report, .. }` 返回后，写入规范 `workerOutput` 与会话状态 `result_ready`，**强制触发同一条 `finish_verifier_run` + `EvidenceIndexStore` 核验链**；
   - 核验器读取 `GoalWorktreeAdapter` 内的真实 `git diff`、文件变更清单与校验命令结果，决定自动签收（`accepted`）、人工确认（`waiting_user`）还是核验未通过（`verification_failed` + 支持 1/3..3/3 重验）。

### 7.4 外部 CLI 适配协议矩阵（Phase 3–4 参考）

| 执行器 | 启动与流式协议 | 续跑句柄 | 权限 / 沙箱映射 | 进程清理与取消 |
|---|---|---|---|---|
| **Peer Native (`peer`)** | 进程内 `peer_runtime::native_exec` | `GoalPlan` + `ConversationStore` | 原生 `PermissionGrant` + `ApprovalStore` | 原生 `CancellationToken` |
| **Claude Code (`claude-code`)** | `claude -p --output-format stream-json --verbose` | `--resume <session_id>` | PreToolUse hook 桥接 `ApprovalStore`；按 `LocalAccessLevel` 设 `--allowedTools` / `--permission-mode` | `kill_on_drop(true)` + 独立进程组终止 |
| **Codex CLI (`codex`)** | `codex exec --json --cd <worktree>` | `codex exec resume <id>` | 严格按 `LocalAccessLevel` 映射 `--sandbox read-only \| workspace-write` | `kill_on_drop(true)` + 独立进程组终止 |
| **OpenCode / Gemini CLI (ACP)** | 标准 `ACP`（JSON-RPC over stdio，复用 ADR 76 协议经验） | ACP `session/load` | 原生 ACP `session/request_permission` 桥接 `ApprovalStore` | ACP `session/cancel` + 超时强杀 |

---

## 8. Phase 1 交付验收清单（Codex 必须逐项跑通）

### 8.1 自动化测试与构建门禁
在 `/Users/yinliang/.codex/worktrees/native-rust-cli/Peer-Agent` 执行（确保 Node `v25.9.0` 与 Cargo 在 `PATH` 中）：

```bash
export PATH="$HOME/.nvm/versions/node/v25.9.0/bin:$HOME/.cargo/bin:$PATH"
node --test "packages/protocol/src/project.test.ts"
node --test "apps/desktop/renderer/src/project-agent/**/*.test.ts"
pnpm --filter @peer-agent/desktop typecheck
pnpm --filter @peer-agent/desktop exec vite build
node apps/desktop/scripts/verify-overlay-backdrop-filter.mjs
```

全部命令必须退出码 `0`、零新增告警。

### 8.2 实机 Electron 视觉截图验收矩阵（Light + Dark 必须逐图肉眼审查）
使用隔离临时 `PEER_AGENT_HOME` 启动真实 Electron 窗口（`1280×860`），构造 8 个 Bot（覆盖全部 8 个 `BOT_AVATAR_SHAPES`），为第 1 个 Bot 构造 4 个活跃子任务（覆盖：运行中、待你确认、核验未通过、排队中）及 1 条含 3 个 `ReplyTaskReferences` 的 Bot 回复，**必须截取并实际查看以下 8 张图**：

| 截图 | 验证核心要点 |
|---|---|
| `verify-home-light.png` / `verify-home-dark.png` | 8 只路线 A 自然绘本猫毛色温润自然（无荧光绿/紫/粉）、3/4 豆豆眼清晰、柔圆领口无平切底边、浅深双主题轮廓通透、首页欢迎卡协调；静息侧栏无厚灰大搜索框 |
| `verify-sidebar-tasks-light.png` / `verify-sidebar-tasks-dark.png` | 工作中 Bot 副标题显示 `N 个工作中`；下挂任务带极细竖向引导线 + 状态弧/点 + 自家小猫 CLI 微标 + 完整可读任务标题（无 `📁` 胶囊挤标题）；选中某子任务为柔和霜纸底（**绝非纯黑块**），无行内「重验」按钮；超过 4 条显示 `再显示 N 个任务` |
| `verify-inline-stream-light.png` / `verify-inline-stream-dark.png` | Bot 主对话回复下方渲染无边框单行任务动态流（`[小猫 CLI 微标] 任务标题 + 语义状态 ›`），与正文严格左对齐、hover 柔和；输入框上方 Touch Bar 简洁呈现活跃任务与历史任务入口 |
| `verify-drawer-light.png` / `verify-drawer-dark.png` | 概况页 2×2 卡片零多余竖线、「挂载能力」无嵌套边框；设置页 `对话模型 / 任务执行 / 复核` 右侧行内对齐「跟随全局」且下拉框下零悬空文案；外观区 56px 绘本猫预览清晰 |

### 8.3 本地打包与 PR 收口
1. 打包并校验本地 macOS 安装包（供用户实机试测）：
   ```bash
   CSC_IDENTITY_AUTO_DISCOVERY=false pnpm --filter @peer-agent/desktop dist:mac
   pnpm --filter @peer-agent/desktop verify:packaged
   ```
2. 本地 `codex/native-rust-cli` 提交后，另建功能分支推送并开启指向 `codex/native-rust-cli` 的独立 PR（**不得直接 push `codex/native-rust-cli`**）。
