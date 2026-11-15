# ADR 41：将现有「Goal 模式」正名为「Plan 模式」

> 创建时间：2026-06-30
> 最后更新：2026-11-15（明确 §5 方案选型表已由下方「六之补二：B2-b 修订」与统一执行契约最终定案，历史记录保留）
> 状态：**部分修订（Superseded in part）** — 方案 A（wire 值 `'goal'`→`'plan'`）与 wire 值迁移三步已落地；但本 ADR 核心结论之一「Runner 归 goal 模式独占、plan 回归纯审批门(A1)」及下文 §5 早期选型对比已于 2026-07-03 被 **B2-b 修订推翻**（另见 [ADR 35](35-mode-scoped-tool-projection.md) 当前模式投影矩阵）：plan 与 goal「批准后」执行段合一，共用同一自驱 Runner。详见文末「§六之补二：B2-b 修订——plan/goal 执行段合一」
> 关联代码：`peer_agent`
> 关联文档：本仓 `design/product/goal-mode-ultrathink-workflow.md`（真正的 Goal 模式设计）、`knowledge/specifications/15-goal-plan-lifecycle-governance.md`

---

## 一、背景与决策

当前产品里有一个名为 **Goal 模式** 的对话模式。经代码实证复核，它的全部行为约束都是「**先规划、经用户批准、再执行**」（plan-before-execute），即：

- 必须先调 `goal_create_plan` 产出结构化计划；
- 计划未获批准前，运行时闸门会阻断一切副作用工具（连只读联网 `web_fetch` 都被 `goal_plan_required` 拦截，本对话开头已实测）；
- 交付重心是「一份计划 + 审批门」。

**这本质上是 Plan 模式，不是 Goal 模式。** 真正的 Goal 模式应当是「给定目标与可验证的成功标准，Agent 自主跑 explore→plan→act→verify 闭环、自我纠错、跑到验证通过再回来」，而不是停在「写完计划等批准」。

**决策**：把现有「Goal 模式」正名为「**Plan 模式**」（plan-before-execute）；释放出 "Goal" 这个名字，留给后续真正的目标自驱模式（设计见配套文档）。本 ADR 只界定**正名 + 改造范围**，不在本知识库仓改任何代码。

---

## 二、为什么是 Plan 不是 Goal（代码实证）

| 证据点 | 位置 | 事实 |
| --- | --- | --- |
| 模式枚举 | `apps/desktop/renderer/src/chat/state/preferences.ts` | `export type ChatMode = 'chat' \| 'goal'`，注释自述「`'goal'` 为先规划后执行模式」 |
| 文案唯一源 | `apps/desktop/electron/main/prompt/sources/mode-copy.mjs` | `MODE_COPY.goal` 共 11 条，全部围绕 "Plan-before-execute / You MUST first produce a structured plan / blocked until approved" |
| 生效注入路径 | `apps/desktop/electron/main/prompt/sources/runtime-reminder-source.mjs` | `fromRuntimeMode()` 读取 `MODE_COPY[mode]`，注入 `L6_MODE_REMINDER` 层，进入生效 System Context |
| 「假」注入路径 | `apps/desktop/electron/main/prompt/sources/mode-source.mjs` | 文件头注释明确：`createModePromptSource` **未被 prompt-assembler 注册**，渲染结果**不进入生效 System Context**（改文案时不要被它误导） |
| 运行时闸门 | `apps/desktop/electron/main/goal-plan-store.mjs` + gate 逻辑 | 计划未批准前阻断副作用工具；这是 plan 门禁，不是目标自驱 |

**结论**：名为 `goal`，实现处处是 `plan`。命名与语义已经漂移，正名是「让名字回归事实」。

---

## 三、正名后的命名建议

> 以下为建议口径，最终落地以 `peer_agent` 仓改动为准。

| 维度 | 现状 | 正名后 |
| --- | --- | --- |
| 模式 key（枚举值） | `'goal'` | `'plan'`（推荐）。如担心存量会话 meta 迁移成本，可保留 `'goal'` 作为 wire 值、仅改 UI/文案显示为 "Plan"，二选一见 §5 |
| UI 显示名 | Goal / 目标 | Plan / 计划 |
| 文案常量 | `MODE_COPY.goal` | `MODE_COPY.plan` |
| 工具名 | `goal_create_plan` / `goal_update_task` / `goal_get_plan` | **保持不变**（这些工具名本就含 "plan"，语义正确；改名牵动协议与历史记录，成本高收益低） |
| 数据存储 | `goal-plan-store.mjs` | **保持不变**（文件名已含 "plan"，语义正确） |
| 面板组件 | `GoalPlanPanel.tsx` | **保持不变**（已含 "Plan"，语义正确） |

**命名原则**：只改「对外语义会让人误解为目标自驱」的地方（模式 key/显示名/模式文案），**不动**那些名字里已经含 "plan"、语义本就正确的工具与存储——避免无收益的大面积重命名。

---

## 四、改造范围界定（核心）

> 本 ADR 的最重要产出。落地在 `peer_agent` 仓，本知识库仓不改代码。

### 4.1 In-scope（应改 — 仅「正名」必需的最小集）

| # | 文件 | 改动性质 |
| --- | --- | --- |
| 1 | `apps/desktop/electron/main/prompt/sources/mode-copy.mjs` | 把 `MODE_COPY.goal` 键名/文案口径从 "goal" 调整为 "plan"（**唯一文案源，改这一处即可同时影响 mode-source 与 runtime-reminder**） |
| 2 | `apps/desktop/renderer/src/chat/state/preferences.ts` | `ChatMode` 枚举值与注释、`CHAT_MODES`、`isChatMode` 守卫（若采用「改 wire 值」方案） |
| 3 | `apps/desktop/renderer/src/chat/hooks/useConversationMode.ts` | 注释/类型引用随枚举更新（逻辑不变） |
| 4 | UI 显示层 | 模式切换控件的展示文案 Goal/目标 → Plan/计划（具体组件以 `peer_agent` 仓为准，如 `ChatSurface.tsx` 等） |
| 5 | i18n 文案 | 模式名相关的中英文文案键值 |

### 4.2 Out-of-scope（明确不动）

- ❌ **不重写运行时闸门算法**：`goal-plan-store.mjs` 的 `supersedeAwaitingDrafts / derivePlanStatus / aggregateProgress / persist` 状态机逻辑保持原样（正名不改行为）。
- ❌ **不改工具协议**：`goal_create_plan / goal_update_task / goal_get_plan` 工具名与签名不变（含 "plan" 语义已正确，改名牵动协议与历史，成本高）。
- ❌ **不改存储文件名/面板组件名**：`goal-plan-store.mjs`、`GoalPlanPanel.tsx` 已含 "plan"，保持。
- ❌ **不动 `mode-source.mjs` 的注册状态**：它本就是未注册的「死路径」，正名不需要激活它（仅在改 `MODE_COPY` 时同步键名即可）。
- ❌ **不在本次引入任何「目标自驱」新行为**：那是配套文档 B 的事，与正名解耦，分开落地。

### 4.3 边界原则

> **正名 = 只改名字与语义口径，零行为变化。** 改完后 Plan 模式的运行时行为应与今天的 Goal 模式**逐字等价**（同样的审批门、同样的闸门、同样的状态机）。任何「顺便优化行为」的冲动都属于越界，应留到文档 B 的真正 Goal 模式里做。

---

## 五、两种落地方案（迁移成本权衡）

> **[历史对比保留，已定案（2026-07-03 / 2026-11-15 对齐）]**：下表为迁移前的 A/B 权衡记录。实际已采用方案 A 完成 wire 值清理，并经下文「六之补二：B2-b 修订」推翻了早先“Runner 归 goal 独占、plan 仅纯审批”的前提（plan 批准后与 goal 共用自驱 Runner 执行段）。

| 方案 | 做法 | 优点 | 代价 |
| --- | --- | --- | --- |
| **A. 彻底改 wire 值** | 枚举值 `'goal'` → `'plan'`，存量会话 meta 做一次性迁移 | 命名彻底干净 | 需迁移历史会话 `mode` 字段 + 测试 |
| **B. 只改显示层** | wire 值仍是 `'goal'`，仅 UI/文案显示 "Plan"，`MODE_COPY` 内部口径改为 plan 语义 | 零数据迁移、零兼容风险 | 代码里仍残留 `'goal'` 字面量，需注释说明「wire=goal、语义=plan」 |

**推荐**：若后续真要做「真正的 Goal 模式」，则采用方案 A——因为新 Goal 模式会引入新的 wire 值（如 `'goal'` 重新被赋予自驱语义），现在就把旧值腾成 `'plan'` 最干净，避免两个语义抢同一个字面量。

---

## 六、影响

- **正向**：命名与事实一致，降低团队/用户认知负担；为「真正的 Goal 模式」腾出名字与概念空间。
- **风险**：方案 A 涉及存量会话 meta 迁移，需回归测试模式恢复逻辑（`useConversationMode` 的 `setMode(convMode)` 路径）。
- **回滚**：纯命名改动，可直接 revert。

---

## 六之补、落地状态（2026-07-01 更新）

方案 A 已在 `peer_agent` 仓实现并提交，代码实证：

- `apps/desktop/renderer/src/chat/state/preferences.ts`：`export type ChatMode = 'chat' | 'plan'`（wire 值已由 `'goal'` 改为 `'plan'`）。
- `normalizeChatMode` 提供向后兼容：历史 `'goal'` 归一化为 `'plan'`，旧会话 `mode` 不降级为 `chat`。
- 提示词侧（`prompt/sources/mode-source.mjs`、`runtime-reminder-source.mjs`）保留注释：历史 `'goal'` 别名按当前 `'plan'` 处理，确保 `MODE_COPY` 命中。
- Workbench Tab 亦已同步改名（`'goal'`→`'plan'`，旧持久化状态归一化）。
- 工具投影：相关 plan 工具 `availableInModes` 由 `['goal']` 改为 `['plan']`，避免归一化后被过滤。

> 遗留衔接（2026-07-02 更新命名决策）：命名决策已拍板——**真正的 Goal 模式继续叫 "Goal" 并复用 `'goal'` wire 值**（不再另起 `'goal-run'` 之类独立新值）。详见 `design/product/goal-mode-ultrathink-workflow.md` 第十六章开放问题 5。

> **wire 值迁移已落地（2026-07-03 更新）**：上述「先迁数据 → 再撤映射 → 重新赋自驱语义」三步已在 `peer_agent` 仓完成并验证。迁移后基线：`ChatMode = 'chat' | 'plan' | 'goal'`（`'goal'` 已重新承载自驱语义）；`conversation-store.mjs` 新增 `migrateLegacyGoalMode` 对存量 index 一次性 `goal→plan`（marker 防重复）；全链路 `normalizeChatMode`/`normalizeMode`/tool 投影/闸门/prompt 各 source 的 `goal→plan` 兼容映射均已撤销；新增 `MODE_COPY.goal` 与三态 UI；防偏航 re-anchor/drift/verification gate 落地。注意：当时的「Runner 归 goal 独占、plan 回归纯审批门」随后已被下方 B2-b 修订为 plan/goal 批准后执行段合一。落地追踪见 `design/product/goal-runner-explorer-task-list.md`「Goal 模式落地前置动作」（三步已勾销）。

---

## 六之补二：B2-b 修订——plan/goal 执行段合一（2026-07-03）

**触发**：用户反馈 plan 计划卡片点「批准并执行」后只显示「已批准」、不自动推进，与按钮字面语义（「执行」）不符。经确认，用户真实诉求是「批准即无人值守自动跑到完成」。

**决策**：修订本 ADR 原结论「Runner 归 goal 模式独占(A1)、plan 回归纯审批门」。改为 **plan 与 goal 批准后执行段合一（代号 B2-b）**：

- plan 批准后与 goal 一样启动同一个自驱 Runner 托管推进，直至命中验证闸门或完成。
- 复用现有全套护栏——续推上下文注入、防偏航 re-anchor、Verification Gate——而非新写一套无护栏的裸自驱（否决 B2-a）。护栏天然生效的原因：Runner 驱动的 turn 一律以 `mode:'goal'` 执行（`runGoalTurn` 写死），故三大护栏对 plan 批准后启动的 Runner 同样命中。

**修订后 plan 与 goal 的边界**：差异收敛到「**批准前的规划把关粒度**」——plan 仍是 plan-before-execute 的审批门（用户对计划本身逐条把关）；goal 面向可验证目标自驱。**批准后二者行为一致**。此前「批准后是否自驱」这一区分点作废。

**已知代价（知情接受）**：

- 本 ADR 原「A1 独占」结论作废，plan/goal 在执行段不再有行为差异，理论上削弱了「plan = 纯审批、不托管」的定位。
- 无人值守自驱的固有风险（长任务偏航、自称完成、不可逆操作）由复用的 goal 护栏兜底，不额外裸奔。

**落地实证（`peer_agent` 仓，2026-07-03）**：

| 改动点 | 位置 | 内容 |
| --- | --- | --- |
| 核心闸门 | `apps/desktop/electron/main/main.mjs` `goalPlans:approve` handler | 移除 `conv?.mode === 'goal'` 判断，改为批准即 `void goalRunner?.start(planId)`（plan/goal 均启动） |
| 注释同步 | `apps/desktop/electron/main/prompt/sources/goal-runner-source.mjs` | 头部与 `observe()` 内联注释由「Runner 归 goal 独占」改为「执行段合一，按 turn 的 `mode:'goal'` 注入护栏」 |

**验证**：`pnpm --filter desktop typecheck` 通过；`goal-runner` / `goal-runner-source` / `goal-mode-gate` 三套单测共 34 项全部通过（0 失败）。既有测试不经过 IPC handler（直接调 `store.recordApproval` + `runner.start`），Runner 自身审批门未动，故无需改测试。

---

## 七、参考

- 配套设计：本仓 `design/product/goal-mode-ultrathink-workflow.md`（真正的 Goal 模式 = ultrathink + workflow）。
- 生命周期治理：本仓 `knowledge/specifications/15-goal-plan-lifecycle-governance.md`。
- CC 机制出处（Anthropic 官方）：`code.claude.com/docs` 的 best-practices / common-workflows / sub-agents / hooks-guide / slash-commands；ultrathink 思考预算阶梯另见 Simon Willison 对 `cli.js` 的反编译（`ultrathink ≈ 31999 tokens`）。
