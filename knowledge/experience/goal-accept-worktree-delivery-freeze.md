# 验收后 Worktree 交回卡顿：完整诊断与修复方案

创建时间：2026-08-17  
最后更新：2026-08-17  
状态：方案已按当前代码校正，代码尚未落地  
代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`  
知识仓：`/Users/liangyin/Documents/MiaoYan/peer-knowledge`

关联代码：

- `apps/desktop/electron/main/goal-delivery-handoff.mjs`
- `apps/desktop/electron/main/goal-worktree-adapter.mjs`
- `apps/desktop/electron/main/main.mjs`（`goalPlanStore.onChange`）
- `packages/runtime-node/src/goal-plan-store.mjs`（`persist` / `recordDeliveryHandoff`）
- `packages/protocol/src/goal.ts`（`formatGoalDeliveryHandoff`）
- `apps/desktop/renderer/src/App.tsx`（`acceptResultFromWorkbench`）

---

## 1. 诊断

### 1.1 problem_rewrite

用户点「验收」后，若该 Goal 绑定了独立 Worktree，主进程会在计划写盘的 `onChange` 里异步启动交回（`handoffPlan` → worktree commit → `git update-ref` 挪目标分支指针）。

可观察症状不是渲染进程同步跑 `git merge`，而是：

- 整窗短暂无响应，或按钮/抽屉像死锁；
- 卡片停在「正在交回目标分支」；
- 偶发 30 秒后才变成「交回已停止」；
- 若用户正好 checkout 在目标分支上，工作区 `git status` 会突然变得很脏，文件树刷新像卡死。

系统语言：`Goal 验收写盘` 与 `Worktree 交回` 仍走同一条 `persist → onChange` 边沿；交回虽已推迟到 `queueMicrotask`，但 `delivering` 写盘会再发一次 `onChange`，锁不能防同计划重入；交回用裸 `update-ref`，不是安全快进。

### 1.2 constraints

- 验收必须立刻落 `resultAcceptance`，不能等 git。
- 交回不得污染用户当前工作区的未提交改动。
- 不得在用户正 checkout 的分支上裸挪 ref（工作区与 HEAD 会脱节）。
- 主进程可让出事件循环；`onChange` 里的交回已用 `queueMicrotask` 推迟，但 `handoffPlan` 自己写 `delivering` 仍会再发一次 `onChange`。
- 交回状态只在「已验收 + `executionIsolation === 'worktree'`」时展示。
- 本知识仓只写方案；代码改动一律在 `peer_agent`。

### 1.3 root_cause_hypotheses

**主因（已由当前代码证实，不是猜测）：同计划重入交回。调度已推迟，但边沿过滤和同计划锁都还没做。**

当前 `main.mjs` 已是：

```js
if (planId && typeof goalDeliveryHandoff?.handoffPlan === 'function') {
  queueMicrotask(() => {
    const plan = goalPlanStore.getPlan(planId);
    if (!plan) return;
    void goalDeliveryHandoff.handoffPlan(plan)...
  });
}
```

所以验收 IPC **不再同步等待** `handoffPlan`。但仍会这样重入：

1. 验收 `goalPlans:revise` → `persist`（同步写盘）→ 同步 `onChange` → 排入 microtask A。
2. 当前栈返回后，A 跑 `handoffPlan`。
3. `handoffPlan` 在第一个 `await` **之前**就 `recordDeliveryHandoff({ status: 'delivering' })`，再次同步 `persist` + `onChange`，排入 microtask B。
4. 仓库锁的判定是「同一 `repo + targetBranch` 上，**别的** planId 才拦截」。本计划再次进入时直接放行。
5. 于是同一次点击会并行跑两套 `commitWorktreeIfNeeded` + `mergeIntoTarget`，抢同一个 worktree 的 `index.lock`。git 子进程最多等 30s，主进程被二次写盘、二次广播、二次概览刷新占用，体感就是整页卡住。

`queueMicrotask` 只把卡顿从「点验收当下冻死」挪到「验收刚返回后的下一拍」。它没有消掉双飞 git。

**次因：交回改的是分支指针，不是工作区合并。**

`mergeIntoTarget` 实际是：

```text
git merge-base target task
git rev-parse target
git update-ref refs/heads/<target> <task>
```

没有 `git merge`，也没有 `checkout`。测试只断言「当前分支名不变、用户脏文件还在」。若用户正好在目标分支上，`update-ref` 会让 HEAD 跳走、工作区文件不动，`git status` 瞬间变成大面积变更；Files 视图的 `fs.watch` 会刷一整棵树。

**已排除：**

- 渲染进程同步执行 `git merge`（不存在这条路径）。
- 验收 IPC 等待 merge 完成（`handoffPlan` 是 `void` + `queueMicrotask`，不 await）。
- 整页被 Electron 渲染线程死循环冻住（卡点在主进程同步写盘 + 重入 git）。

**证伪方式：** 在 `handoffPlan` 入口打计数。若一次验收出现两次进入，且第二次发生在第一次仍在跑 git 时，主因成立。

### 1.4 source_of_truth

修完之后：

- **验收事实**只由 `resultAcceptance` 表示，`goalPlans:revise` 只写这一笔。
- **交回事实**只由 `deliveryHandoff` 表示，由独立交回调度器推进；`onChange` 只负责边沿调度，禁止 `delivering` 写盘再触发一轮交回。
- **目标分支**只允许快进；用户正占用该分支时，只能在工作区干净时做 `merge --ff-only`，禁止 `update-ref`。

### 1.5 causal_chain

将改这些节点：

| 节点 | 现状 | 目标 |
|---|---|---|
| `persist` → `onChange` | 已 `queueMicrotask`，但每次 persist 都会再排一轮 | 只在「已验收且尚未交回」边沿调度一次；`delivering` 写盘不再二次触发 |
| `locks` | 只挡不同 plan | 同 plan 重入直接返回 in-flight |
| `mergeIntoTarget` | 无条件 `update-ref` | 按「是否正占用目标分支 / 工作区是否干净」分支处理 |
| 交回文案 | `stopped` 默认「交回已停止」 | 超时、脏工作区、锁冲突都有明确原因，可重试 |
| 验收 UI | 只等 revise，交回无进度 | 验收瞬间完成；卡片立刻进入「正在交回」，失败可点开原因并重试 |

### 1.6 success_checks

- 一次验收，`handoffPlan` 只真正执行一轮 git。
- 验收 IPC 在交回 git 开始前返回（或最多只同步写完 `resultAcceptance`）。
- 用户不在目标分支：目标分支快进，当前 checkout 的分支名、工作区脏文件都不动。
- 用户在目标分支且工作区干净：快进后工作区文件与 HEAD 一致，没有「HEAD 跳了、文件没动」。
- 用户在目标分支且工作区脏：交回停止，原因是「当前工作区有未提交改动」，不挪 ref。
- 目标分支已前进：仍停止为 `target_branch_moved`，不三方合并。
- 交回中/失败时，窗口可滚动、可打字、可关抽屉；不会整页假死超过 200ms。
- 现有测试 `goal-delivery-handoff.test.mjs` 全过，并补上重入与「占用目标分支」用例。

### 1.7 non_goals

- 不把验收改成同步等待 merge。
- 不做三方 `git merge` 自动解决冲突。
- 不在这次改 Files 视图虚拟化、聊天滚动、search_files。
- 不顺手改 Goal 隔离分支命名（`PeerAgent/automation-*`）——可另开小修。
- 不把 worktree 历史残骸一次性清掉当作修复。

---

## 2. 现状链路（点验收时）

```text
Renderer  点验收
  → await goalPlansRevise({ resultAcceptance })
Main      revisePlan
  → persist(resultAcceptance)          // writeFileSync + 同步 onChange
    → broadcast goalPlans:changed
    → taskOverviewBroadcast.request
    → queueMicrotask(handoffPlan A)    // 当前栈已推迟，但还会再排
         → persist(delivering)         // 再次 onChange
           → queueMicrotask(handoffPlan B)
         → await git commit / update-ref   // A/B 并行，抢 index.lock
```

关键代码：

- 验收只写验收：`App.tsx` `acceptResultFromWorkbench`
- 交回挂在写盘回调：`main.mjs` `onChange` 里 `queueMicrotask(() => handoffPlan(...))`
- 交回锁不管同计划：`goal-delivery-handoff.mjs` `locks.has(key) && locks.get(key) !== plan.planId`
- 所谓 merge：`git update-ref refs/heads/${targetBranch} ${taskBranch}`
- 用户可见态：`formatGoalDeliveryHandoff`（`delivering` / `delivered` / `stopped`）

git 调用有 30s timeout，但超时文案会掉进默认「交回已停止」。

---

## 3. 目标行为

把一次点击拆成两段互不重入的事实：

```text
验收（同步、短、可 IPC 等待）
  只写 resultAcceptance
  立刻关抽屉 / 播庆祝动画
  卡片出现「正在交回 …」

交回（异步、单飞、可失败可重试）
  当前 persist 栈清空后再启动
  同一 repo+targetBranch 同时只跑一个
  同一 plan 重入直接复用进行中的 Promise
  成功：目标分支快进，handoff=delivered
  失败：handoff=stopped + 可读原因 + 保留 worktree
```

用户工作区规则：

| 用户当前状态 | 交回动作 |
|---|---|
| 不在目标分支 | 在 worktree 里快进目标分支指针（可用 `update-ref` 或 `merge --ff-only` 到该 ref）。不碰用户 checkout。 |
| 正在目标分支，工作区干净 | 在**用户仓库根**执行 `git merge --ff-only <taskBranch>`，让文件和 HEAD 一起快进。 |
| 正在目标分支，工作区脏 | 停止，原因 `target_checkout_dirty`。不挪 ref。 |
| 目标分支已不在 task 的祖先上 | 停止，原因 `target_branch_moved`。不三方合并。 |
| 同目标已有别的计划在交回 | 停止，原因 `same_target_busy`。 |

「干净」定义为：`git status --porcelain` 在用户仓库根为空。用户自己的未提交改动永远优先。

---

## 4. 分层改动

### 4.0 交回调度从 `onChange` 里拆出去（P0，先做）

`main.mjs` 已经用 `queueMicrotask` 把交回挪出验收 IPC 调用栈，但「广播 / 概览刷新 / 自动开跑 / 交回 / worktree 清理」仍全挂在每一次 `persist` 的 `onChange` 上。缺的是边沿过滤：`delivering` 写盘会再排一轮。

建议抽 `scheduleGoalDeliveryHandoff(planId)`：

1. 读最新 plan；不满足 `canHandoff` 则返回。
2. 同一 `planId` 已有 in-flight Promise：直接复用。
3. 继续用 `queueMicrotask` / `setImmediate` 启动，确保验收 IPC 先返回。
4. `recordDeliveryHandoff` 继续走 `persist` 广播 UI，但 **`onChange` 不再因为 `deliveryHandoff` 变化而二次 `schedule`**。

判定可用：`payload` 带上变更字段，或 `onChange` 里若 `deliveryHandoff.status` 已是 `delivering|delivered|stopped` 则跳过调度。最稳的是「只在 `resultAcceptance.acceptedAt` 从空到有」时调度一次。

`handoffPlan` 自己的锁改成：

```text
if (locks.has(key)) {
  if (locks.get(key) === plan.planId) return currentPromise; // 同计划重入
  return stop('same_target_busy');                           // 不同计划
}
```

并让锁持有的是 Promise，而不是只记 planId。

### 4.1 安全快进替换裸 `update-ref`（P0）

重写 `mergeIntoTarget`：

1. `rev-parse --abbrev-ref HEAD`（用户仓库根）
2. `merge-base` + `rev-parse target`：目标已前进则 `target_branch_moved`
3. 若 HEAD == targetBranch：
   - `status --porcelain` 非空 → `target_checkout_dirty`
   - 否则在用户仓库根 `git merge --ff-only <taskBranch>`
4. 若 HEAD != targetBranch：
   - `git update-ref --stdin` 或 `merge-base` 确认可快进后再 `update-ref`
   - 不要 `checkout` 用户工作区

`merge_conflict` 只留给真正的 merge 失败；`update-ref` 失败不要再误标成冲突。超时单独记 `git_timeout`。

### 4.2 验收 UI 与交回进度解耦（P1）

保持「验收不等 git」：

- `acceptResultFromWorkbench` 仍只 `await goalPlansRevise`。
- `resultAcceptancePending` 只覆盖这一次 revise，返回就清。
- 交回中的禁用范围不要扩到整页，只禁用「再点一次验收」。

展示：

- `delivering`：卡片/计划面板显示「正在交回 `<repo> / <branch>`」，可滚动、可关。
- `stopped`：显示具体原因，提供「重试交回」（只重跑 `scheduleGoalDeliveryHandoff`，不改 `resultAcceptance`）。
- `delivered`：现有「已交回 …」，可附短 SHA。

`formatGoalDeliveryHandoff` 补原因：

| `stoppedReason` | 中文 |
|---|---|
| `target_branch_moved` | 目标分支已更新（已有） |
| `same_target_busy` | 同一目标正在交回（已有） |
| `merge_conflict` | 交回时发生冲突（已有） |
| `target_checkout_dirty` | 当前工作区有未提交改动，未写入目标分支 |
| `git_timeout` | 交回超时，可重试 |
| `git_lock` | 仓库正被占用，可重试 |
| 其他 | 交回已停止（兜底） |

### 4.3 写盘与广播不要堵验收（P1）

不必把整个 `persist` 改成 async。最小改动：

- `recordDeliveryHandoff` 允许 `notifyLocal: false` 再由调度器自己广播一次；或
- `publishPersistedChange` 对交回状态变更改成 `setImmediate` 广播。

目的：验收 IPC 的调用栈上最多一次 `writeFileSync`，不要叠「验收写盘 + delivering 写盘 + 两次概览刷新」。

`taskOverviewBroadcast` 已有调度器，保持 debounce，不要在交回过程中改成同步重算整表。

### 4.4 交回成功后再收 worktree（P2）

`retainOrCleanupPlan` 已存在，但计划中断会留残骸。交回成功（`delivered`）后应：

1. `collect()` 证据已在执行期落过的，不必再 collect。
2. `git worktree remove` 该 plan 的目录。
3. 分支若已并入目标分支，删除 `PeerAgent/automation-<id>/run-<id>`（或未来的 `PeerAgent/goal-<id>`）。
4. `deliveryBinding.worktreePath` 清空，但保留 `taskBranch` / `commitSha` 在 `deliveryHandoff` 里追溯。

失败则保留 worktree，方便重试。

### 4.5 测试（与 P0/P1 同批）

扩 `goal-delivery-handoff.test.mjs`：

1. **重入**：`persist/onChange` 模拟两次 `queueMicrotask` 调度。断言只有一次 `update-ref` / `merge`，最终 `delivered`。
2. **占用目标分支 + 干净**：用户 HEAD 就是 target，工作区干净。断言文件内容变成 task 分支的版本，`status` 干净。
3. **占用目标分支 + 脏**：用户有 `user-dirty.txt`。断言 target ref 不变，`stoppedReason === 'target_checkout_dirty'`。
4. **不在目标分支**：保持现有用例（分支名不变、脏文件还在、目标分支已含隔离改动）。
5. **目标已前进**：保持 / 补强 `target_branch_moved`。
6. **IPC 不泄漏等待**：`revise` 的假时钟下，验收返回时 git 尚未完成。

渲染侧只加轻量契约测试：验收按钮在 `delivering` 时不再全页 `disabled`；`stopped` 露出原因文案。

---

## 5. 建议落地顺序

不要先改文案。先修管道，再修 git 契约，最后补 UI。

1. **P0 重入**：同计划锁 + 推迟调度 + `onChange` 不再因 delivering 二次启动。  
   验证：新重入测试；手动点验收，日志里 `handoffPlan` 只进入一次。
2. **P0 快进契约**：禁止对当前 checkout 分支 `update-ref`。  
   验证：干净/脏两条新测试。
3. **P1 原因与重试**：新 `stoppedReason` + 重试 IPC/按钮。  
   验证：脏工作区文案可读；修干净后重试能交回。
4. **P1 验收栈减负**：delivering 写盘不挡 `revise` 返回。  
   验证：验收抽屉立刻关闭，卡片随后变成「正在交回」。
5. **P2 清理 worktree**：成功后删除隔离目录。  
   验证：`git worktree list` 不再累加该 plan。

预估：P0 约 1 个工作单元（`goal-delivery-handoff.mjs` + `main.mjs` + 测试）；P1 再加 protocol 文案和一处按钮；P2 独立收尾。

---

## 6. 明确不做什么

- 不把「验收」改成「验收并等待合入」。
- 不自动 `stash` 用户脏文件再合入。
- 不在用户工作区做非快进合并。
- 不把卡顿归咎于渲染层再去做骨架屏/禁用整窗。
- 不在本方案里清理历史遗留的 4 个 goal worktree（那是运维动作，不是根因）。

---

## 7. 落地时的代码锚点

| 改动 | 文件 |
|---|---|
| 推迟调度、只在验收边沿启动 | `apps/desktop/electron/main/main.mjs` |
| 同计划单飞锁、安全快进、原因码 | `apps/desktop/electron/main/goal-delivery-handoff.mjs` |
| 重入 / 脏工作区 / 占用目标分支测试 | `apps/desktop/electron/main/goal-delivery-handoff.test.mjs` |
| 新 stoppedReason 文案 | `packages/protocol/src/goal.ts` |
| 可选：handoff 变更不二次调度 | `packages/runtime-node/src/goal-plan-store.mjs`（`publishPersistedChange` 或 payload） |
| 重试入口 | `App.tsx` / `GoalPlanPanel.tsx` + 一条 IPC（复用现有 revise 或新 `goalPlans:retryHandoff`） |
| 成功后收 worktree | `goal-worktree-adapter.mjs` 的 `retainOrCleanupPlan` |

---

## 8. 验收清单（给人点的）

1. 知识库会话里验收一个带独立执行环境的 Goal：抽屉马上关上，界面可继续操作。
2. 卡片先「正在交回」，再「已交回 peer_agent / `<branch>`」。
3. 打开目标仓：目标分支包含隔离提交；若当时不在该分支，当前工作区未提交改动仍在。
4. 再测一遍「就停在目标分支上、故意留一个未提交文件」：交回停止并说明原因，分支指针不变；清掉脏文件后点重试，交回成功且工作区与 HEAD 一致。
5. 主进程日志 / 测试：一次验收只有一轮 git。
