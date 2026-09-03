# 73. Goal 中断挂起与失败解耦的状态契约

创建时间：2026-09-03

状态：Accepted

级别：A 级（改状态机契约：`GoalPlanStatus` 新增 `interrupted` 挂起态、persist 派生规则、re-arm 触发条件、通知策略语义）

关联：

- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/decisions/68-goal-delivery-mode-contract.md`
- peer_agent `packages/protocol/src/goal.ts`（GoalPlanStatus）
- peer_agent `packages/runtime-node/src/goal-plan-store.mjs`（persist 派生）
- peer_agent `packages/runtime-node/src/goal-intake-convergence.mjs`（re-arm 判定）
- peer_agent `packages/runtime-node/src/goal-runner.mjs`（中断事实与 resume 消费）
- peer_agent `apps/desktop/electron/main/task-notification-policy.mjs`（通知语义）

## 背景

「未消费执行中断」（stream 被打断、budget/超时等宿主因素导致执行中断，但叶子任务没有真实失败）目前被 `persist` 的 `hasUnconsumedInterruption` 分支**压成 `failed` 终态**：

```js
// goal-plan-store.mjs
const hasUnconsumedInterruption = Boolean(
  normalized.runner?.interruption &&
    !(recoverable === true && status === 'running'),
);
const nextStatus = hasUnconsumedInterruption ? 'failed' : derivePlanStatus(...);
```

这造成同一字符串 `failed` 承载两种语义：

1. **真实失败**：叶子任务硬失败，终态。弹「任务失败」正确。
2. **未消费中断**：执行被挂起，可恢复。`failed` 是错误表达——用户看到「任务失败」误导，实际只是被打断；re-arm 恢复后立刻弹「任务已完成」，形成「失败→完成」的误导通知链。

通知层 `isAttentionTransition` 只认「进入 failed」就弹「任务失败」，无法区分两种来源；re-arm（`shouldRearmFailedGoalPlanFromChange`）又绑死 `status==='failed'`，把恢复机制耦合在 collapsed 的失败态上。

## 决策

### 1. 新增独立挂起态 `interrupted`

`GoalPlanStatus` 增加 `interrupted`：表示「执行被外部因素挂起、可恢复、非终态」。它与用户主动 `paused` 区分（`paused` 是用户意图，`interrupted` 是宿主/环境事实），与 `failed` 区分（叶子任务无真实失败）。

### 2. persist 派生规则

`persist` 中未消费中断改为派生为 `interrupted` 而非 `failed`：

```js
const nextStatus = hasUnconsumedInterruption
  ? 'interrupted'
  : derivePlanStatus(...);
```

- 真实叶子失败仍派生 `failed`（`derivePlanStatus` 叶子失败分支不变）。
- `derivePlanStatus` 对 `interrupted` 计划的派生规则：
  - 叶子全 completed → `completed`（中断不改变叶子事实，恢复后自然归位）;
  - 叶子有真实失败 → `failed`;
  - 否则保持 `interrupted`。

### 3. re-arm 触发条件

`shouldRearmFailedGoalPlanForChange` 改名/扩展为「中断挂起或失败终态的 accepted_goal 计划收到 goal-accepted 变更即可 re-arm」：

- 触发条件从 `status === 'failed'` 扩展为 `status === 'failed' || status === 'interrupted'`
  （或更精确：`status === 'interrupted'` 或「`failed` 且叶子失败为真」）。
- re-arm 路径 `resume()` 消费中断标记并恢复执行，消费时把 `interrupted` 形态的计划拉回 executing。
- 通知层对 `failed → executing`（re-arm 成功）不再弹「已完成」——完成通知只在真实进入 `completed` 时弹。

### 4. 通知语义

- `interrupted` 挂起**不弹**「任务失败」；弹「已暂停，待恢复」。
- 只有真实叶子失败（derivePlanStatus 派生 failed 时叶子确有失败）弹「任务失败」。
- 恢复完成 → `completed` 弹「任务已完成」。
- 因此图中「失败→完成」误导链消除：interrupted 弹「已暂停，待恢复」，恢复后弹「任务已完成」。

### 5. 消费中断 = 恢复执行

`resumeRunner` 是中断事实的唯一消费者（与现状一致）：resume 原子消费 interruption 证据，计划从 `interrupted` → `executing`，runner.interruption 清空。普通 persist 不得把 `interrupted` 重新派生为 completed/failed（除非叶子事实变化）。

## 非目标

- 不改 `derivePlanStatus` 的叶子失败派生规则（真实失败仍终态 failed）。
- 不给 `interrupted` 加自动重试/自动恢复——恢复仍由 goal-accepted re-arm 或显式 resume 驱动。
- 不迁移存量数据：老计划里 collapsed `failed` 不回填为 `interrupted`（通知层已不再误弹）。
- 不改 runner 的中断捕获/重试预算语义（stream_interrupted_retrying 等不变）。

## 验证明细

（收尾时补充实际运行结果）

## 验收

- `packages/protocol`：`GoalPlanStatus` 路合类型含 `interrupted`，类型检查通过。
- `packages/runtime-node`：persist 派生单测——未消费中断→`interrupted`（不是 failed）；叶子真实失败→`failed`；interrupted 计划叶子全 completed→`completed`。`goal-runner-rearm.test.mjs`：goal-accepted 变更对 `interrupted` 计划触发 resume。
- `apps/desktop`：通知策略单测——interrupted 挂起弹「已暂停，待恢复」不弹「任务失败」；真实失败弹「任务失败」；re-arm 后完成弹「任务已完成」。
- 存量 3129 份计划数据无破坏（旧 failed 不回填，无迁移脚本）。
