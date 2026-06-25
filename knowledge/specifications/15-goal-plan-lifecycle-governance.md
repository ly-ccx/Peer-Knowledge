# Goal 计划生命周期治理

> 创建时间：2026-06-25
> 最后更新：2026-06-25
> 状态：Goal 模式缺陷复盘 + 治理规范
> 关联代码：`peer_agent` `apps/desktop/electron/main/goal-plan-store.mjs`、`prompt/sources/mode-copy.mjs`

---

## 一、背景：一次「僵尸 executing 计划」事故

在一次连续交互中（先调 Diff 标题栏样式、再把顶部留白 52px→24px、再把 TabRail 留白 60px→6px），Agent 每次方案微调都新建了一个 Goal 计划，旧计划没有收尾。最终右侧目标面板里堆了多个"执行中（4/5、2/4）"的计划，但它们的代码改动其实早已完成并提交。

用户的直觉判断是对的：**这是个 bug**。但排查后发现根因和最初设想不同，需要分两层定性。

---

## 二、根因分析（两层）

### 第一层：代码缺陷（L2'）

`goal-plan-store.mjs` 本就有两套自动收尾机制，且都正确：

- `derivePlanStatus()`：当计划处于 `executing` 且**所有叶子任务**都是终态（completed/failed）时，自动把顶层推进为 completed/failed。
- `aggregateProgress()`：按叶子聚合 progress。
- `persist()`：每次写盘都重算上述两者。

但 `supersedeAwaitingDrafts()` 存在明确缺口：它在 `createPlan` 时被调用，**只作废同会话里 `awaiting_approval` 状态的旧草稿**，对已经 `executing`（已批准、执行中）的旧计划直接跳过。

因此：当用户中途改方案、Agent 另起新计划时，旧的 `executing` 计划既不会被自动收尾（因为它的叶子没全部终态），也不会被作废 —— 于是变成"僵尸 executing 计划"。

### 第二层：Agent 行为缺陷（L3）

- **滥建计划**：同一个目标（"收紧工作台顶部留白"）本应用一个计划随需求细化（revise），Agent 却新建了多个计划。
- **漏回写**：完成的子任务没有边做边用 `goal_update_task` 回写 evidence，而是拖到最后才补。叶子长期停在非终态，即使有自动收尾逻辑也不会触发。

---

## 三、修复方案

### L2'：扩展 supersede 覆盖活跃态旧计划

把 `supersedeAwaitingDrafts` 从"只作废 awaiting_approval 草稿"扩展为"收尾/作废同会话所有活跃态旧计划"。活跃态 = `drafting / awaiting_approval / approved / executing / paused`（即 `ACTIVE_PLAN_STATUSES`）。

收尾策略按旧计划状态分流：

| 旧计划状态 | 处理 |
| --- | --- |
| `awaiting_approval` | 直接作废为 `cancelled`（既有行为不变） |
| 其它活跃态，且**全叶子终态** | 按 `derivePlanStatus('executing', tasks)` 如实收尾为 `completed`/`failed` |
| 其它活跃态，**仍有未完成叶子** | 作废为 `cancelled`，原因标注 superseded |
| 已是 completed/failed/cancelled 等终态 | 不触碰 |

关键原则：

- **不谎报完成度**。有未完成叶子的旧计划只作废，绝不伪造成 completed。
- 全部走 `persist()` 正规写盘 + onChange 广播，并向 `revisionHistory` 追加 `changedBy: 'system:supersede'` 审计条目，保留可追溯事实。
- 仅在 `conversationId` 非空时生效，跨会话不互相误伤。

单测覆盖（`goal-plan-store.test.mjs`）：executing 含未完成叶子→cancelled、executing 全叶子终态→completed、drafting→cancelled，并保留原 awaiting_approval 作废与跨会话隔离用例。

### L3：固化 Agent 行为约束

在 `prompt/sources/mode-copy.mjs` 的 goal 文案（单一文案源）追加两条：

1. **边执行边回写**：每完成/失败/阻塞一个子任务，立即用 `goal_update_task` 回写 result + evidenceRefs，不得拖到最后批量回写，否则计划会残留"执行中"的陈旧子任务。
2. **同会话单活跃计划**：新建计划前，先收尾或作废仍在执行的旧计划——能如实判定完成的收尾为 completed/failed，否则作废；同一目标优先 revise 现有计划，而非另起新计划。

---

## 四、沉淀的纪律（适用于所有 Goal 模式执行）

- **一个目标，一个计划**：需求在执行中细化，用修订（revise）而非新建。只有当目标本质改变时才另起计划，且必须先收尾旧计划。
- **回写即时性**：子任务状态变化与 `goal_update_task` 调用同步发生，让面板进度始终反映真实状态。
- **完成必有证据**：子任务标 completed 必须带来自真实工具结果的 evidenceRefs，不允许仅凭断言。
- **收尾不谎报**：被取代的计划如实反映完成度——真完成才 completed，没完成就 cancelled。

---

## 五、参考

- 缺陷修复提交见 `peer_agent` 仓 `dev/0.0.1` 分支。
- 相关实现：`goal-plan-store.mjs`（`supersedeAwaitingDrafts` / `derivePlanStatus` / `aggregateProgress` / `persist`）。
- 行为约束源：`prompt/sources/mode-copy.mjs`（`MODE_COPY.goal`，被 mode-source 与 runtime-reminder 复用）。
