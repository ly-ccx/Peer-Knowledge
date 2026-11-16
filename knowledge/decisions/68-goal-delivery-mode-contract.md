# 68. 交付模式契约：direct 与隔离合回统一语义

创建时间：2026-08-26
最后更新：2026-11-15（标明 Project Bot 模式下默认直写与无确认合回已由 ADR 80 决策 7–8 取代，并受 ADR 116 / 127 资源占用锁约束）

状态：Accepted（经典单对话 Goal 模式基线；在 0.1.0 Project Bot 模式下，默认 `direct` 写回与无确认直落已部分取代）

级别：A 级（改合回契约：GoalDeliveryHandoff 增字段、交付事实写入点、UI 渲染语义、脏检查策略）

关联：

- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/decisions/16-skill-call-lifecycle.md`
- peer_agent `packages/protocol/src/goal.ts`（GoalDeliveryHandoff / GoalDeliveryBinding）
- peer_agent `apps/desktop/electron/main/goal-delivery-handoff.mjs`
- peer_agent `apps/desktop/renderer/src/chat/components/GoalPlanPanel.tsx`

## 背景

同一产品里存在两种合法交付路径，但只有一种被记录：

1. **隔离合回**：计划在独立 Worktree 的任务线上执行，完成后 rebase/merge 进目标分支。整条链路有状态机（idle → delivering → delivered / stopped），UI 有合回路线图、重试按钮、三态灯（还没进 / 已进 / 合不进）。
2. **直接交付（direct）**：计划在当前工作区执行，改动直接提交到目标分支（通常随执行一并 push）。**完成时没有任何代码写交付事实**——`recordDeliveryHandoff` 只在合回链路被调用，`canHandoff` 明确排除非隔离计划（注释：「完成即结束：没开隔离的改动留在当前工作区，不合回」）。

由此产生三层断裂（均有实测证据）：

- **事实层**：非隔离计划完成后 `deliveryHandoff` 为空，交付事实只散落在验收检查里，永远不进状态机。
- **表达层**：UI 从「无记录」反推出「还没进 ${目标分支}」——对已直接交付完成的计划是**反事实**；同时 `showMergeRoute = hasTaskLine(plan) || isolated` 因空壳 taskBranch 给非隔离计划也画合回路线图，暗示一个不存在的合回动作。
- **执行层**：真需要合回的隔离计划被 `git status --porcelain` 非空即挡（`target_checkout_dirty`），untracked 噪音也算脏——实测工作区里与任务线版本**逐字节一致**的 untracked 文件（demo/version-map.html, 23901B）把合回挡死，「再试一次」点多少次都是死局。

## 决策

### 1. deliveryMode 契约字段

`GoalDeliveryHandoff` 增加只读字段：

```ts
export type GoalDeliveryMode = 'merge' | 'direct';

export interface GoalDeliveryHandoff {
  readonly status: GoalDeliveryHandoffStatus;
  /** 交付模式：merge=隔离任务线合回；direct=当前工作区直接提交。缺省视为 'merge'（向后兼容）。 */
  readonly deliveryMode?: GoalDeliveryMode;
  // …existing fields…
}
```

缺省值语义为 `'merge'`：存量数据不迁移，老记录自然兼容。

### 2. direct 交付事实的写入点

主进程在计划状态流转为 `completed` 时判定并写入：

- 判定条件（全部满足）：
  - `deliveryBinding.executionIsolation !== 'worktree'`（非隔离）；
  - 绑定的交付仓库 HEAD 已包含计划工作（实测可用的判据：验收检查通过 且 `HEAD != baseCommit`；工程上取 `HEAD` 领先 `baseCommit` 或 HEAD == baseCommit 但质量检查全过两种情形，以 store 判定为准）；
  - 计划此前无 `deliveryHandoff` 记录（幂等，不覆盖已存在状态）。
- 写入内容：`{ status: 'delivered', deliveryMode: 'direct', repoId, targetBranch, commitSha: HEAD, updatedAt }`。
- 写入位置：主进程计划完成路径（`main.mjs` 完成门之后，与 `scheduleGoalDeliveryHandoff` 同一挂接层），调用 `goalPlanStore.recordDeliveryHandoff`，不新增 IPC、不新增执行路径。
- 失败处理：写入失败不阻断完成流，记 log，下次完成门重试幂等。

### 3. UI 按交付语义渲染

- **灯条**：`deliveryMode === 'direct' && status === 'delivered'` → 「已随 ${dest} 交付」/ `delivered with ${dest}`；不再显示「还没进」。
- **合回路线图（任务线 → 发版线）**：只对 `executionIsolation === 'worktree'` 的隔离计划渲染。direct 计划不画路线图。
- **重试按钮**：维持只有隔离计划显示（现有 `canMergeIntoSource` 不变）。
- **任务总览（TaskOverview）**：同语义的 lamp 标签。

### 4. 合回脏检查分级

`target_checkout_dirty` 从「porcelain 非空即挡」改为三级：

1. **modified / staged（含 deleted/renamed）**：一律挡——真有未提交工作。
2. **untracked 且与任务线变更集无路径碰撞**：放行。
3. **untracked 且路径碰撞**：比较内容；与任务线将写入的版本逐字节一致 → 放行（merge 会把它变成 tracked）；不一致 → 挡（`target_checkout_dirty`，提示先处理碰撞文件）。

任务线变更集 = `git diff --name-only baseCommit..taskBranch`（worktree 内执行）。

### 5. 空壳任务线治理（源头）

- 新计划：`planNeedsTaskBranch` 增加 `executionIsolation` 判定——非隔离计划不再创建 taskBranch 引用（空壳从源头消失）。
- 存量：一次性归一脚本/逻辑——已 `completed` 且无 handoff 记录且 taskBranch 停在 baseCommit 的计划，补写 direct delivered 事实（同 §2 判定）并清掉空壳 taskBranch 字段。运行时判定同 §2（完成时幂等补写）。

## 非目标

- 不改隔离合回的状态机与重试语义（stopped → 重试仍走原链路）。
- 不给 direct 交付加「合回」动作——没有东西可合。
- 不迁移存量 stopped 记录的 stoppedReason。

## 模式适用边界（2026-11-15 对齐）

- **0.1.0 Project Bot 模式（[ADR 80](80-project-agent-delegation-model.md) 决策 7–8）**：委托执行默认走隔离工作树/分支；不再采用默认直接提交到主工作区（无隔离 `direct`）或绕过用户确认的静默写入。`direct` 交付事实仅用于保留经典单对话兼容基线，且不作为主线新增能力的默认模式。
- **资源锁接入（[ADR 116](116-session-control-and-resource-settlement.md) / [ADR 127](127-unknown-outcome-reconciliation-and-delegated-resolution.md)）**：任何合回写盘与分支清理动作，在执行前仍须按声明范围取得并结清设备级 `execution-resources` claim，不得在目录尚持未知占用时直接合入。

## 验收

- Protocol 类型检查通过；`packages/protocol` goal 测试含 direct 灯条/标签用例。
- 主进程完成路径对非隔离 completed 计划写入 direct delivered 事实（幂等）。
- `GoalPlanPanel.evidence` 测试断言：合回路线图只对隔离计划渲染；direct 灯条不再出现「还没进」。
- `goal-delivery-handoff` 测试含分级脏检查用例：untracked 无碰撞放行、同内容碰撞放行、异内容碰撞挡。
- 存量 3129 份计划数据无破坏（字段缺省兼容，无迁移脚本）。
