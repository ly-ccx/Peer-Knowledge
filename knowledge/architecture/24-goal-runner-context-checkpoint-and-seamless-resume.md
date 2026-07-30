# Goal Runner 上下文检查点与无限续航技术实现

创建时间：2026-07-28
最后更新：2026-07-28
状态：完整技术实现方案 / 待分期落地
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

关联文档：

- `knowledge/decisions/17-local-context-compaction.md` — 本地证据材料化、分层压缩和按需回捞原则
- `knowledge/architecture/21-auto-context-compaction-run-resume.md` — 自动压缩与同一 Agent Run 续接基础协议
- `knowledge/architecture/23-compaction-path-root-governance.md` — 单一 Compaction Pipeline、双宿主一致性与容量口径
- `design/product/goal-mode-ultrathink-workflow.md` — Goal 自驱工作流和完成门槛

## 一、结论与架构决策

本文决定把 Goal 模式的长时间执行改造成一个可以反复执行以下循环的持久化工作流：

```text
run → checkpoint → compact → rehydrate → resume same run
    → checkpoint → compact → rehydrate → resume same run
    → ... → success criteria passed → completed
```

上下文到达阈值不是 Goal 终态，也不是一次新的用户会话，而是同一 `planId`、同一逻辑 `runId` 内的一次维护事务。压缩次数不得成为 Goal 能否完成的限制条件。

核心架构不是“写一份更长的摘要”，而是四层连续性模型：

```text
GoalPlan                  权威任务事实：做什么、做到哪、如何验收
GoalExecutionCheckpoint   权威执行游标：刚做了什么、现在卡在哪、第一步做什么
Continuity Summary        历史语义：为什么这么做、有哪些决策和失败经验
Bounded Recent Tail       最近协议现场：必要原文、未闭合工具结构、短期局部状态
```

Evidence / artifact 不塞入上述任意一层的正文；它们保存在本地证据存储中，只以 `evidenceRef`、`artifactRef` 和重新读取提示进入模型上下文。

必须遵守以下优先级：

```text
用户最新明确要求
  > GoalPlan 的目标、边界、任务状态和 successCriteria
  > 已提交 GoalExecutionCheckpoint
  > 可验证 Evidence / artifact
  > 最近保留消息
  > Continuity Summary
  > 模型基于摘要的推断
```

冲突时，低优先级内容不得覆盖高优先级事实。摘要不是任务状态真源，最近消息也不能把已由 Evidence 证明完成的任务重新改回未完成。

## 二、问题诊断

### 2.1 problem_rewrite

问题位于 Goal Runner、上下文压缩、持久化计划和 provider 请求预检之间的状态衔接层。可观察症状是：Goal 自驱过程中上下文触顶后，压缩可能因为 `keep + tools` 过大而失败；即使压缩成功，下一轮也主要依赖自由文本 handoff 猜测执行游标，无法机器保证不丢进度、不重做、不跳过验证。

### 2.2 constraints

1. Goal 必须在用户没有追加消息时继续自驱，直到完成、需要用户决策、不可恢复失败或被取消。
2. 同一 Goal 可经历任意多次压缩；每次压缩都必须可重入、可恢复、可观测。
3. 子任务完成必须继续遵守 Evidence gate，不能因为摘要写了“已完成”就完成任务。
4. 未闭合工具调用必须保持 provider 协议合法，但大工具结果不得以全文锁死 keep 预算。
5. Desktop 与 TUI 必须复用同一协议、store 和编排语义；宿主只负责 UI 和传输接线。
6. 不能依赖模型记忆、聊天窗口是否还显示旧消息，或用户手动输入“继续”。
7. 持久化必须原子化；应用崩溃、窗口刷新和进程重启后都能判断事务停在哪一步。
8. 不得把 secrets、大日志、完整 shell 输出复制进 checkpoint。
9. tools schema 属于 provider 请求预算的一部分，但不应和消息历史混成一个不可解释的失败数字。
10. 旧版本 GoalPlan 必须惰性迁移，不能要求一次性重写所有持久化文件。

### 2.3 root_cause_hypotheses

主因有两层：

1. 自动压缩使用 `preserveLatestUserTurn=true`，把最近真人 user 后的未闭合工具尾整体放入 keep；Goal 长流程的一轮可能包含大量工具结果，导致 keep 没有稳定上限。
2. 当前 handoff 虽然要求记录目标、文件、错误、下一步和 Evidence，但它仍是自由文本；代码中没有独立 `goalCheckpoint`，`GoalRunnerStatus` 也没有 `compacting_context` / `resuming_after_compaction`。因此压缩是会话事件，不是 Goal 状态机中的事务。

反证条件：如果在 keep 严格有界、tools 单独核算后仍频繁无法达到目标预算，则主因转为 system prompt / tools schema 固定底座过大；如果 checkpoint 完整注入后仍重做任务，则需要检查恢复首步守卫和 Evidence 去重，而不是继续加长摘要。

### 2.4 source_of_truth

压缩后唯一可靠的 Goal 真源是磁盘上的 `GoalPlan`。新增的 `GoalExecutionCheckpoint` 作为 `GoalPlan.runner.contextCheckpoint` 的结构化子记录原子写回同一计划文件；历史 checkpoint 只以精简 run trace 事件归档，不维护第二份可竞争的计划文件。

### 2.5 causal_chain

本文修改的因果链节点：

```text
tool result materialization
→ bounded keep selection
→ Goal checkpoint prepare/commit
→ compaction pipeline
→ conversation continuity persistence
→ system context rehydration
→ same-run resume guard
→ task/evidence update
→ repeated compaction
→ success criteria completion gate
```

### 2.6 success_checks

1. 单次 Goal 在测试中连续触发至少 10 次 compaction，`planId` 和逻辑 `runId` 不变，最终完成。
2. 每次压缩后的第一个 provider request 都含已提交 checkpoint，且执行 `firstAction` 或先报告不可执行原因。
3. 压缩前已完成任务不重复执行，除非 checkpoint 明确要求复验且产生新的 verifier run。
4. 压缩发生在工具调用边界、应用崩溃前后和窗口重载期间时，均不产生 orphan `tool_result`。
5. 压缩失败不会直接把 Goal 标记为 `failed`；只有所有降级层失败且证明固定底座无法装入窗口才进入不可恢复状态。
6. Desktop 与 TUI 使用同一协议类型和 checkpoint renderer，行为测试一致。

### 2.7 non_goals

- 不保证压缩摘要逐字保留全部聊天历史。
- 不把“从 Goal 发起到结束的全部原文”长期放在模型 prompt。
- 不用提高上下文阈值掩盖 keep 无界问题。
- 不让 checkpoint 替代 GoalPlan、Evidence 或 successCriteria。
- 不把 compaction done 伪装成 `chat:stream:done`。
- 不在本方案中改变模型提供商的 token 计费规则。

## 三、现状基线与缺口

### 3.1 已有能力

当前代码已经具备以下基础：

- `goal-plan-store.mjs` 使用 `index.jsonl + ${planId}.json` 持久化计划，写入采用 `.tmp` 后 `rename` 的原子替换。
- `GoalPlan.runner` 已保存 `status`、`intent`、`phase`、`currentTaskId`、预算、Explorer、Verifier、run trace 等状态。
- `goal-runner-source.mjs` 每轮从 GoalPlan 重建 `Active goal runner context`，不会只依赖聊天历史。
- `provider-request-coordinator.mjs` 是 Desktop provider 请求前的统一入口。
- `compaction-coordinator.mjs` 统一执行自动、紧急和手动压缩，先持久化再发 `chat:compaction done`，之后重建 system prompt。
- `context-compactor.mjs` 支持 continuity carry-forward、最近用户决策锚点、结构化 fallback 和 keep 二次 microcompact。
- `tool-artifact-store.ts` 可将大型工具结果材料化为 `local_tool_result_ref`，保留预览、Evidence 和回捞路径。
- Goal Runner 已按 compaction boundary 构造运行时历史；Desktop/TUI 共享 Goal store 和 Runner 编排。

### 3.2 明确缺口

1. `GoalRunnerStatus` 当前只有 `idle/running/paused/exploring/blocked/budget_exhausted/completed/failed`，没有压缩事务状态。
2. 协议中没有 `GoalExecutionCheckpoint`；仓库搜索不到 `goalCheckpoint`。
3. handoff 是自由文本，无法验证 `currentTaskId`、`firstAction`、`doNotRepeat` 和 `pendingVerification` 是否存在。
4. compaction coordinator 不知道当前请求是否属于 Goal，也无法在压缩前提交 Goal checkpoint。
5. Goal Store 与 conversation compaction 分别持久化，没有共同的事务 id 和恢复判定。
6. keep 以最近真人 user / 工具闭合关系切分为主，缺少 Goal 专用 token + 条数双上限。
7. 当前压缩失败在 coordinator 中继续抛出，由上游终态处理；没有 Goal 专用的分层降级与继续策略。
8. 恢复后没有强制的“第一动作协议”，模型可能先重新探索、重复写文件或直接跳到下一任务。

## 四、术语与标识

| 名称 | 含义 | 生命周期 |
|---|---|---|
| `planId` | GoalPlan 主键 | Goal 全生命周期不变 |
| `runId` | 一次逻辑自驱执行的主键 | 跨多次压缩、provider retry、stream reattach 保持不变 |
| `turnId` | 一次模型 turn | 每次 provider 交互变化 |
| `streamId` | 一次宿主流连接 | 重连或恢复时可变化 |
| `checkpointId` | 一次执行检查点主键 | 每次 checkpoint 变化 |
| `compactionId` | 一次压缩事务主键 | 每次压缩变化 |
| `sequence` | 同一 run 的 checkpoint 单调序号 | 只能递增 |
| `planVersion` | GoalPlan 结构修订版本 | 计划修订时递增 |
| `contextEpochId` | system prompt / 上下文配置代际 | 配置变化时变化 |
| `conversationRevision` | 会话持久化修订 | 每次会话写入递增或生成新 revision |

`runId` 是“同一个 Goal 仍在继续”的判定依据；`streamId` 只用于事件路由，不能作为任务身份。压缩不得生成新 `runId`。

> 现状校准：当前 `GoalRunnerState` 尚未定义 `runId`。本文要求在协议和 Goal Store 中新增持久化 `runId`；首次启动/恢复旧计划时生成，只有用户显式重新运行一个终态 Goal 或创建新 Goal 时才生成新值。不能直接复用当前短生命周期 `streamId`。

### 4.1 必须始终成立的不变量

1. **身份不变**：一次逻辑 Goal 执行中，`planId/runId` 跨所有 compaction 不变。
2. **序号单调**：同一 run 的 checkpoint `sequence` 严格递增，不允许回退或并列提交。
3. **先存后删**：没有 committed checkpoint，不能删除/替换 active history。
4. **只存一个当前检查点**：模型 prompt 中只注入最新 committed 且未 consumed 的 checkpoint。
5. **证据不由摘要创造**：summary/checkpoint 文本都不能注册或伪造 Evidence。
6. **协议合法**：任何压缩候选都不产生 orphan tool call/result。
7. **恢复优先**：存在 committed checkpoint 时，普通 Goal 调度不得抢跑。
8. **首步可验证**：`firstAction` 必须有可观察成功条件。
9. **副作用不盲重放**：未知状态副作用工具默认不重跑。
10. **压缩非终态**：compaction 事件不能直接关闭 Goal 或同一 run。
11. **大小有界**：checkpoint、continuity、recent tail、tools projection 分别有预算；任何一项都不能无限增长。
12. **崩溃可判定**：持久化状态足以判断下一步是重压、rehydrate、resume、consume 还是 blocked。

## 五、状态真源与读取顺序

### 5.1 GoalPlan：长期真源

GoalPlan 必须持续保存：

- 原始目标、范围和非目标。
- 任务树、依赖和每个叶子任务状态。
- successCriteria 与机器验证结果。
- Evidence 索引和任务 Evidence refs。
- 当前 Runner 意图、阶段、任务游标、预算和 blocker。
- 当前已提交 checkpoint 的引用和正文。

聊天摘要不得直接修改上述事实。所有状态变化继续通过 Goal Store API，并经过现有 Evidence gate。

### 5.2 GoalExecutionCheckpoint：短期执行真源

Checkpoint 回答“现在如何无缝接着做”，但不重新定义目标。它是计划真源中的可替换最新记录：同一时刻只有一个 `committed` checkpoint；旧记录进入 run trace 后不再参与 prompt。

### 5.3 Continuity Summary：历史语义

Continuity Summary 回答：

- 为什么走到这里。
- 用户有哪些长期偏好和决策。
- 哪些方案已否决及原因。
- 哪些失败经验不能忘。
- 哪些文件、命令和技术事实影响后续。

它可以由 LLM 生成，但不能声称没有 Evidence 的工作已完成，也不能覆盖 GoalPlan / checkpoint。

### 5.4 Bounded Recent Tail：协议现场

Recent Tail 只保留 checkpoint 无法取代的协议级信息：最近用户原话、最近少量 assistant/tool 结构、未闭合工具调用 id，以及短小工具结果。它必须受 token 和消息条数双预算约束。

## 六、协议数据模型

新增协议放在 `packages/protocol/src/goal.ts`，并从 protocol package 公共入口导出。

```ts
export type GoalCheckpointStatus =
  | 'preparing'
  | 'committed'
  | 'consumed'
  | 'superseded'
  | 'invalid';

export type GoalCheckpointReason =
  | 'soft_threshold'
  | 'hard_threshold'
  | 'provider_overflow'
  | 'task_boundary'
  | 'manual_compact'
  | 'process_recovery';

export type GoalResumePolicy =
  | 'continue_same_turn'
  | 'start_recovery_turn'
  | 'verify_then_continue'
  | 'wait_for_user';

export interface GoalCheckpointProgress {
  readonly total: number;
  readonly completed: number;
  readonly failed: number;
  readonly blocked: number;
  readonly percent: number;
  readonly nextRunnableTaskIds: readonly string[];
}

export interface GoalCheckpointAction {
  readonly actionId: string;
  readonly kind: 'inspect' | 'edit' | 'write' | 'tool' | 'test' | 'verify' | 'decision';
  readonly summary: string;
  readonly status: 'completed' | 'failed' | 'running' | 'unknown';
  readonly target?: string;
  readonly evidenceRefs: readonly string[];
  readonly result?: string;
  readonly occurredAt?: string;
}

export interface GoalCheckpointToolCall {
  readonly toolCallId: string;
  readonly toolName?: string;
  readonly status: 'requested' | 'running' | 'completed' | 'failed' | 'unknown';
  readonly resultEvidenceRefs: readonly string[];
  readonly replayPolicy: 'never' | 'query_status' | 'safe_retry' | 'ask_user';
  readonly idempotencyKey?: string;
}

export interface GoalCheckpointFirstAction {
  readonly kind: 'tool' | 'inspect' | 'edit' | 'verify' | 'synthesize' | 'wait_user';
  readonly instruction: string;
  readonly target?: string;
  readonly successCheck: string;
  readonly requiredEvidenceRefs: readonly string[];
  readonly forbiddenUntilComplete?: readonly string[];
}

export interface GoalCheckpointBudgetSnapshot {
  readonly contextWindow: number | null;
  readonly beforeTokens: number;
  readonly targetTokens: number;
  readonly systemTokens: number;
  readonly toolsTokens: number;
  readonly checkpointTokens: number;
  readonly continuityTokens: number;
  readonly recentTailTokens: number;
  readonly keepBudgetTokens: number;
  readonly compactionCount: number;
}

export interface GoalExecutionCheckpoint {
  readonly schemaVersion: 1;
  readonly checkpointId: string;
  readonly compactionId: string;
  readonly sequence: number;
  readonly status: GoalCheckpointStatus;
  readonly reason: GoalCheckpointReason;

  readonly planId: string;
  readonly planVersion: number;
  readonly runId: string;
  readonly conversationId?: string;
  readonly streamId?: string;
  readonly contextEpochId?: string;
  readonly conversationRevision?: string;

  readonly currentTaskId?: string;
  readonly runnerPhase?: GoalRunnerPhase;
  readonly runnerIntent?: GoalRunnerIntent;
  readonly progress: GoalCheckpointProgress;

  readonly objectiveNow: string;
  readonly currentWork: string;
  readonly recentActions: readonly GoalCheckpointAction[];
  readonly completedSincePrevious: readonly string[];
  readonly mostImportantFact: string;
  readonly decisions: readonly string[];
  readonly blockers: readonly string[];
  readonly risks: readonly string[];
  readonly openQuestions: readonly string[];
  readonly pendingVerifications: readonly string[];
  readonly doNotRepeat: readonly string[];
  readonly handoffNote: string;
  readonly firstAction: GoalCheckpointFirstAction;

  readonly evidenceRefs: readonly string[];
  readonly mustReadEvidenceRefs: readonly string[];
  readonly openToolCalls: readonly GoalCheckpointToolCall[];
  readonly budget: GoalCheckpointBudgetSnapshot;
  readonly resumePolicy: GoalResumePolicy;

  readonly createdAt: string;
  readonly committedAt?: string;
  readonly consumedAt?: string;
  readonly digest: string;
}
```

`GoalRunnerState` 增加：

```ts
export type GoalRunnerStatus =
  | 'idle'
  | 'running'
  | 'compacting_context'
  | 'resuming_after_compaction'
  | 'paused'
  | 'exploring'
  | 'blocked'
  | 'budget_exhausted'
  | 'completed'
  | 'failed';

export interface GoalRunnerState {
  // existing fields...
  /** 一次逻辑自驱执行的持久化身份；跨 compaction/stream retry 不变。 */
  readonly runId?: string;
  readonly contextCheckpoint?: GoalExecutionCheckpoint;
  readonly lastConsumedCheckpointId?: string;
  readonly lastConsumedCheckpointSequence?: number;
  readonly compactionCount?: number;
  readonly lastCompactionAt?: string;
}
```

### 6.1 必填字段语义

用户强调的交接信息逐一映射如下：

| 需要保留的信息 | 字段 |
|---|---|
| 最近做了哪些事 | `recentActions` |
| 到了什么进度 | `progress`、`currentTaskId`、`runnerPhase` |
| 当前最重要的事实 | `mostImportantFact` |
| 需要交接什么 | `handoffNote` |
| 后续模型第一件事 | `firstAction` |
| 当前具体在做什么 | `objectiveNow`、`currentWork` |
| 不能重复做什么 | `doNotRepeat` |
| 还要验证什么 | `pendingVerifications` |
| 证据在哪里 | `evidenceRefs`、`mustReadEvidenceRefs` |
| 未闭合工具怎么办 | `openToolCalls[].replayPolicy` |

### 6.2 大小与内容限制

Checkpoint 不能变成第二份无限增长摘要。规范化时执行：

- `recentActions` 最多 12 条；优先保留当前任务、失败和未验证动作。
- `decisions` 最多 12 条；更早决策进入 continuity summary。
- `blockers/risks/openQuestions/pendingVerifications/doNotRepeat` 各最多 10 条。
- 所有自由文本单项默认上限 2,000 字符，`handoffNote` 上限 4,000 字符。
- `evidenceRefs` 去重后最多 100 条；超过时优先保留当前任务和 must-read，其余由计划 Evidence 索引回查。
- 禁止内联完整工具输出、文件全文、图片 base64、tools schema、完整 diff 和 secrets。
- `digest` 对规范化后的稳定 JSON 计算 SHA-256；不含 `status/committedAt/consumedAt` 等生命周期字段，便于校验内容是否被改写。

### 6.3 Checkpoint 生成来源

结构化字段不允许全部交给 LLM自由生成：

- `planId/planVersion/runId/currentTaskId/phase/intent/progress/evidenceRefs` 从 GoalPlan 和 Runner 读取。
- `recentActions` 从 run trace、任务更新、工具调用 ledger 和 Evidence index 投影。
- `openToolCalls` 从 agent loop / tool orchestrator 的权威调用状态投影。
- `budget` 从统一 Context Accounting Pipeline 读取。
- `mostImportantFact/handoffNote/firstAction/doNotRepeat` 可由模型提出，但必须经过确定性规范化和 Runner 校验；`firstAction` 必须指向当前任务或验证门槛。
- 如果模型未提供可接受内容，Runner 使用确定性 fallback：当前 task 标题 + 最近未完成动作 + 下一个机器可验证步骤。

## 七、Goal 压缩事务

### 7.1 事务状态机

每次 Goal 压缩采用显式状态机：

```text
running
  → compacting_context(preparing)
  → compacting_context(checkpoint_committed)
  → compacting_context(conversation_compacted)
  → resuming_after_compaction(system_rehydrated)
  → running(checkpoint_consumed)
```

失败分支：

```text
checkpoint prepare 失败       → 保持 running，不执行 destructive compaction
checkpoint commit 失败        → 保持/恢复 running，不执行 compaction
summary / keep 预算失败       → 进入分层降级，不立即 Goal failed
conversation persist 失败     → checkpoint 保持 committed，启动恢复流程
system rehydrate 失败         → 不发送 provider 请求，重试 rehydrate
resume 首步无法执行           → blocked 或 repair，不静默跳过
固定底座无法容纳              → context_unrecoverable，才允许 Goal failed
```

### 7.2 prepare 阶段

触发 soft threshold、hard threshold、provider overflow、task boundary 或手动 compact 时，coordinator 首先调用：

```ts
prepareGoalCheckpoint({
  planId,
  runId,
  conversationId,
  streamId,
  compactionId,
  reason,
  runtimeMessages,
  openToolCalls,
  budgetSnapshot,
})
```

prepare 必须：

1. 读取最新 GoalPlan，不使用调用者缓存。
2. 校验计划状态仍是 `executing`，Runner 未取消/暂停。
3. 计算 `sequence = previous.sequence + 1`。
4. 从计划、run trace、Evidence 和工具 ledger 构建 checkpoint。
5. 校验 `currentTaskId` 存在、未完成且依赖满足；否则选择权威的 next runnable task。
6. 校验 `firstAction` 与当前任务一致。
7. 写入 `status='preparing'`，Runner 改为 `compacting_context`。
8. 追加 `goal_checkpoint_prepared` run trace 事件，只保存摘要、id、digest 和关键 refs，不复制全文。

prepare 本身不能删除会话消息。

### 7.3 commit 阶段

Checkpoint 规范化和校验完成后，通过 Goal Store 的专用 API 原子提交：

```ts
commitGoalCheckpoint(planId, {
  expectedPlanVersion,
  expectedRunId,
  expectedPreviousCheckpointId,
  checkpoint,
})
```

采用 compare-and-swap：

- 当前 `plan.version` 必须等于 `expectedPlanVersion`，否则重新 prepare。
- 当前 `runner.runId` 必须一致，防止旧 run 覆盖新 run。
- 当前 checkpoint id 必须等于期望前驱，防止并发压缩乱序提交。
- 提交后 checkpoint 状态为 `committed`，`committedAt` 写入。
- `compactionCount += 1` 只在 conversation compact 成功后增加，不能在 prepare 阶段提前计数。

Commit 是 compaction 删除 old 消息前的写前日志（write-ahead record）。没有 committed checkpoint，不允许对 Goal 会话做 destructive compaction。

### 7.4 compact 阶段

Coordinator 传入 Goal 上下文：

```ts
runCompactionCheck({
  ...existing,
  goalContext: {
    planId,
    runId,
    checkpointId,
    compactionId,
    mode: 'goal',
  },
  keepPolicy: goalKeepPolicy,
})
```

压缩产物必须同时包含：

- cumulative continuity summary。
- bounded recent tail。
- `_compaction` metadata：`compactionId/checkpointId/planId/runId/sequence`。
- budget breakdown 和所用降级层。

`persistCompactionToConversation()` 持久化后，conversation continuity item 增加 checkpoint 引用：

```ts
interface ContinuityContextItem {
  // existing fields...
  readonly compactionId?: string;
  readonly checkpointId?: string;
  readonly planId?: string;
  readonly runId?: string;
  readonly checkpointSequence?: number;
}
```

会话中不重复保存 checkpoint 全文，只存引用。权威正文始终从 GoalPlan 读取。

### 7.5 rehydrate 阶段

`persistAndNotifyCompaction()` 完成后，现有 coordinator 已调用 `rehydrateSystemPromptAfterCompaction()`。Goal 扩展要求重建顺序固定为：

```text
1. provider/system 基础指令
2. workspace / AGENTS / policy sources
3. Active Goal Plan facts
4. Active Goal Execution Checkpoint
5. Continuity Summary
6. bounded recent messages
7. projected tools schema
```

系统上下文新增 `goal-checkpoint-source.mjs`，只接受 store 投影结果，不直接信任 conversation message 中的 checkpoint 文本。该 source 的 trust 为 `runtime`，scope 为 `run`，并输出 `checkpointId/digest/sequence` 元数据供调试。

### 7.6 resume 与 consume 阶段

重建 system prompt 后，Runner 切到 `resuming_after_compaction`，同一 `runId` 继续。恢复 turn 的系统指令必须明确：

```text
你正在从 Goal checkpoint 恢复，不是开始新任务。
先核对 planId/runId/checkpointId/currentTaskId。
第一动作优先执行 checkpoint.firstAction。
不得重复 doNotRepeat 中的动作。
不得把摘要中的“计划”写成“已完成”。
若第一动作前置证据不足，先读取 mustReadEvidenceRefs。
完成第一动作后，把新 Evidence 写回 Goal Store，再继续正常 Runner 循环。
```

Checkpoint 不是在 prompt 注入时立即消费，而是在以下条件满足后标记 `consumed`：

1. 恢复 turn 已成功开始并确认 checkpoint id。
2. `firstAction` 已完成、失败或被明确阻塞。
3. 结果已通过 Goal Store / Evidence 写回。
4. `lastConsumedCheckpointId` 更新为当前 id。

如果模型返回普通文本却没有执行或解释 `firstAction`，Runner 不得消费 checkpoint；下一 tick 仍按恢复协议继续。

### 7.7 安全压缩点

正常 soft-threshold compaction 只在安全点进入 destructive 阶段：

- 没有本地工具正在修改状态，或工具已返回且结果已进入 ledger/Evidence。
- provider stream 已到可切分边界，不能截断半个 tool-call JSON / content block。
- Goal Store 没有并发 task update 正在提交。
- conversation revision 已固定并可 CAS。

如果 provider 在一次长生成/工具链中直接 overflow，走 emergency：先取消/冻结 provider request，收集已完成的协议块，把半成品标记为 incomplete，不把它当普通 assistant 完成消息；然后 checkpoint + compact + recovery turn。不得为了立刻压缩而伪造 tool_result 或截断协议对象。

Checkpoint 生成本身必须始终有确定性路径，不依赖额外 LLM 请求成功。LLM 只可优化 `handoffNote/mostImportantFact/firstAction` 可读性；如果它超时、overflow 或返回非法结构，立即使用 Plan + run trace + Evidence 构建 fallback checkpoint，避免出现“为了压缩先调用摘要模型，而摘要模型也超窗”的死锁。

### 7.8 端到端时序与职责边界

```text
GoalRunner      ProviderCoordinator  GoalStore   CompactionCoordinator  ConversationStore  SystemContext  Provider
   |                    |                |                |                    |               |          |
   | run normal tick    |                |                |                    |               |          |
   |------------------->| preflight      |                |                    |               |          |
   |                    | threshold hit  |                |                    |               |          |
   |<-- request CP data-|                |                |                    |               |          |
   | build deterministic checkpoint     |                |                    |               |          |
   |----------------------------- prepare/commit -------->|                    |               |          |
   |                    |                | committed Cn    |                    |               |          |
   |                    |-------------------------- compact(goalContext) ----->|               |          |
   |                    |                |                | materialize/select keep             |          |
   |                    |                |                | summarize/degrade    |               |          |
   |                    |                |                |-- persist messages ->|               |          |
   |                    |                |<-- mark compaction persisted --------|               |          |
   |                    |                |                |---------------- rehydrate --------->|          |
   |                    |<--------------- compacted messages + prompt ---------|               |          |
   |<-- status resuming |                |                |                    |               |          |
   |-------------------- provider request (same runId, checkpoint Cn) --------------------------------->|
   |<-------------------------------- tool/action/result ------------------------------------------------|
   |----------------------------- evidence/task update ------->|                    |               |     |
   |----------------------------- consume Cn ----------------->|                    |               |     |
   | normal tick resumes |                |                |                    |               |          |
```

职责必须唯一：

- **GoalRunner**：解释计划、构建 checkpoint 内容、校验 firstAction、恢复守卫、consume。
- **ProviderRequestCoordinator**：判断 provider 请求是否需要 preflight，协调 GoalRunner 与 compaction；不生成任务事实。
- **GoalStore**：CAS、原子持久化、状态机和 run trace。
- **CompactionCoordinator**：消息/预算压缩事务、conversation 持久化顺序、事件、rehydrate；不修改任务完成状态。
- **SystemContext**：只读注入 GoalPlan/checkpoint/continuity；不写回。
- **ToolOrchestrator**：工具状态、Evidence、idempotency ledger；不决定 Goal 下一任务。

### 7.9 真实持久化示例

下面展示 `<planId>.json` 的相关片段；省略任务树和无关 Runner 字段：

```json
{
  "planId": "plan-123",
  "version": 17,
  "status": "executing",
  "runner": {
    "enabled": true,
    "runId": "run-abc",
    "status": "resuming_after_compaction",
    "intent": "execute",
    "phase": "act",
    "currentTaskId": "implement-strategy",
    "compactionCount": 3,
    "lastConsumedCheckpointSequence": 2,
    "contextCheckpoint": {
      "schemaVersion": 1,
      "checkpointId": "cp-003",
      "compactionId": "compact-003",
      "sequence": 3,
      "status": "committed",
      "reason": "soft_threshold",
      "planId": "plan-123",
      "planVersion": 16,
      "runId": "run-abc",
      "conversationId": "conv-9",
      "currentTaskId": "implement-strategy",
      "runnerPhase": "act",
      "runnerIntent": "execute",
      "progress": {
        "total": 5,
        "completed": 2,
        "failed": 0,
        "blocked": 0,
        "percent": 40,
        "nextRunnableTaskIds": ["implement-strategy"]
      },
      "objectiveNow": "实现有界 keep 和自动降级",
      "currentWork": "已完成切分算法，尚未接入 coordinator",
      "recentActions": [
        {
          "actionId": "a-22",
          "kind": "edit",
          "summary": "新增 goal keep policy 纯函数",
          "status": "completed",
          "target": "packages/runtime-core/src/goal-keep-policy.ts",
          "evidenceRefs": ["tool-result://write-22"]
        }
      ],
      "completedSincePrevious": ["root-cause-fix"],
      "mostImportantFact": "恢复后的第一步必须接 coordinator，不能重新设计 keep 算法",
      "decisions": ["keepBudget 使用 token + turn + message 三重上限"],
      "blockers": [],
      "risks": ["tools schema 仍可能构成固定底座"],
      "openQuestions": [],
      "pendingVerifications": ["runtime-core unit tests"],
      "doNotRepeat": ["不要重新编辑已通过测试的 splitMessagesForCompaction"],
      "handoffNote": "接入 provider preflight，再补多次 compaction 测试。",
      "firstAction": {
        "kind": "edit",
        "instruction": "将 goalKeepPolicy 传入 provider-request-coordinator",
        "target": "apps/desktop/electron/main/chat-runtime/provider-request-coordinator.mjs",
        "successCheck": "provider request coordinator 单测覆盖 Goal policy 传递",
        "requiredEvidenceRefs": ["tool-result://write-22"]
      },
      "evidenceRefs": ["tool-result://write-22"],
      "mustReadEvidenceRefs": ["tool-result://write-22"],
      "openToolCalls": [],
      "budget": {
        "contextWindow": 258000,
        "beforeTokens": 205000,
        "targetTokens": 141900,
        "systemTokens": 18000,
        "toolsTokens": 27000,
        "checkpointTokens": 1800,
        "continuityTokens": 9000,
        "recentTailTokens": 12000,
        "keepBudgetTokens": 16384,
        "compactionCount": 3
      },
      "resumePolicy": "continue_same_turn",
      "createdAt": "2026-07-28T12:00:00.000Z",
      "committedAt": "2026-07-28T12:00:01.000Z",
      "digest": "sha256:..."
    }
  }
}
```

`planVersion` 记录 prepare 时读取的版本；commit 后 GoalPlan 顶层 `version` 会递增，因此两者不要求相等。CAS 比较的是提交请求携带的 `expectedPlanVersion` 与写入前的当前版本。

## 八、T2：Goal 专用 keep 策略

### 8.1 原则

Goal 自动压缩不再使用“最近真人 user 之后全部原文均必须保留”的无界语义。应保留的是**有界的可执行现场**：

```text
keep = latest human anchor
     + protocol-safe open tool skeleton
     + bounded recent completed tail
```

GoalPlan 和 checkpoint 已经保存目标与进度，因此 keep 不负责长期记忆。

### 8.2 默认预算

默认配置建议进入 runtime-core：

```ts
export const GOAL_KEEP_POLICY = {
  maxRecentUserTurns: 2,
  maxRecentMessages: 20,
  maxCompletedToolResults: 4,
  minKeepTokens: 4_096,
  maxKeepTokens: 16_384,
  keepContextRatio: 0.10,
  checkpointMaxTokens: 4_096,
  continuityMaxTokens: 12_000,
  targetRequestRatio: 0.55,
  softTriggerRatio: 0.72,
  hardTriggerRatio: 0.88,
};
```

实际 keep budget：

```text
keepBudget = clamp(
  floor(contextWindow × keepContextRatio),
  minKeepTokens,
  maxKeepTokens
)
```

若 contextWindow 很小，预算优先级为：协议合法性 > checkpoint > system/tools > continuity > recent tail。不能为了满足 `minKeepTokens` 把请求推过窗口。

### 8.3 切分算法

1. 先 materialize 所有超阈值 tool results。
2. 找到所有未闭合工具调用，保留 call id、tool name、arguments 摘要、status、result refs；不保留巨型 stdout。
3. 从尾部按 user turn 选择最多 2 个 turn。
4. 同时按消息数和 token 预算裁剪；任一上限先到即停。
5. 当前 turn 超预算时，按结构拆分：
   - user 原文若超大，保留首尾、附件 refs 和内容摘要。
   - assistant reasoning 不作为必保正文。
   - tool result 只留 ref、关键 findings 和短预览。
   - tool call/result 对不得拆成协议孤儿；无法合法保留时，把整对移出 request 并在 checkpoint 记录。
6. keep 完成后再次执行 provider-wire validation。

### 8.4 多层降级

当候选仍超过目标预算时，按固定顺序降级：

```text
D0 normal summary + normal bounded keep
D1 structural summary
D2 fallback_drop summary（仍保 checkpoint）
D3 aggressive keep microcompact
D4 closed tool results → refs only
D5 recent tail 收缩到最新 user anchor + open tool skeleton
D6 continuity 收缩为 checkpoint-required decisions/evidence index
D7 tools schema projection
D8 recovery request：checkpoint + 最小 system + 必需 tools
```

只有 D8 仍超过 provider hard limit 时，才抛 `GOAL_CONTEXT_UNRECOVERABLE`。`CONTEXT_COMPACTION_INSUFFICIENT_REDUCTION` 对 Goal 模式应是可降级信号，不是直接终态。

### 8.5 tools schema 投影

Tools 固定底座可能独自超过阈值。Goal 模式需要 `ToolProjectionPolicy`：

- 恢复第一步需要的工具必须保留。
- 当前 phase 需要的基础工具保留，如 read/search/edit/test/goal_update_task。
- 高体积、当前无关 MCP tools 可暂时隐藏；并在 system context 中说明可按需重新启用。
- projection 结果必须稳定、可审计，记录 `includedToolNames/excludedToolNames/toolsTokensBefore/toolsTokensAfter`。
- 模型不得调用未注入的工具；需要时下一 tick 重建工具集。
- 手动普通 chat 默认不启用 Goal 投影，避免改变产品语义。

目标请求预算不再只报告一个总数，必须分项：

```text
system + tools + checkpoint + continuity + recentTail + providerOverhead
```

### 8.6 真实失败样例的预算演算

原失败日志：

```text
before = 379622
minimal candidate = 374937
triggerLimit = 206400
```

旧算法的问题是 `minimal candidate` 仍包含近乎无界的 current-turn keep 和全部 tools，因此只比 before 少 4,685 tokens。新算法不承诺以下数字是该会话的实测分项（旧日志没有分项），但要求按同一窗口把预算压成类似的有界结构：

```text
provider contextWindow（由 triggerLimit/旧比例反推，仅用于示意） ≈ 258000
目标 targetAfter = 55%                                      ≈ 141900

最小 system / policy                                        18000
投影后的 tools                                               30000
Goal checkpoint                                               4000
continuity summary                                           12000
bounded recent tail                                          16000
provider overhead / output reservation                       20000
---------------------------------------------------------------
候选总量                                                     100000
runway                                                        41900+
```

关键不是某个固定数字，而是每一项都有独立上限和降级责任。即便 tools 实际为 60k，系统仍能明确知道应该投影 tools，而不是继续尝试把摘要从 5k 压到 2k。

### 8.7 多次压缩为何不会线性膨胀

第 N 次压缩的活跃 prompt 不是：

```text
summary1 + checkpoint1 + summary2 + checkpoint2 + ... + recent
```

而是：

```text
mergedContinuity(N) + latestCheckpoint(N) + boundedRecent(N)
```

规则：

- 旧 checkpoint 在 consume/supersede 后只留下精简 run trace，不再进 prompt。
- continuity merge 的输出受 `continuityMaxTokens` 上限控制，并覆盖旧 summary，而不是 append。
- 已完成任务的详细过程退出 active tail，只保 GoalPlan 状态、必要决策和 Evidence refs。
- 最近窗口每次重新按固定预算从 active history 选择。
- compaction 后目标 55% 留出 runway，避免立即重复触发。

因此 prompt 大小对 compaction 次数应近似 O(1)，持久化 run trace 可增长但有独立 retention/归档策略，不进入活跃上下文。

## 九、工具调用、Evidence 与幂等

### 9.1 tool_result 材料化

所有宿主在工具执行完成后、写入 provider history 前统一调用 `materializeToolResultContent()`：

- 小输出原样内联。
- 大输出写 artifact，provider history 只放 `local_tool_result_ref`。
- 已经是 `local_*_ref` 的结果不二次材料化。
- 写盘失败时可短暂内联，但必须在下一次 preflight 优先重试材料化。

### 9.2 未闭合工具调用

压缩可能发生在：工具已请求、正在执行、结果已产生但尚未写回、结果已写回但任务状态未更新。Checkpoint 必须记录每个调用状态和 `replayPolicy`。

恢复规则：

| 状态 | 恢复行为 |
|---|---|
| `requested`，未开始 | 若工具幂等且有 key，可 safe retry；否则查询状态/阻塞 |
| `running` | 查询工具 registry，不直接重跑 |
| `completed`，有 Evidence | 不重跑；按 ref 读取结果并补任务写回 |
| `failed` | 保留失败证据，根据 firstAction 决定修复或换方案 |
| `unknown` | 默认 `query_status`；高风险工具必须等待用户或人工确认 |

### 9.3 幂等键

副作用工具调用必须使用：

```text
idempotencyKey = sha256(planId + runId + taskId + actionId + normalizedArgs)
```

工具 orchestrator 和 checkpoint 同时保存该 key。恢复时先查 ledger；存在 completed 记录则返回原 Evidence，不再次执行。读操作可以 safe retry，但仍应优先使用已有 artifact，避免成本和结果漂移。

### 9.4 doNotRepeat

`doNotRepeat` 不只是自然语言提醒。Runner 在恢复第一 turn 前构建集合：

- 已完成 task ids。
- completed tool idempotency keys。
- 已应用 edit 的 patch/digest。
- 已完成 verifier targets。
- 用户明确否决的方案 fingerprints。

工具执行前守卫检查该集合；命中时要求模型提供“为什么需要重做”的新证据或条件变化，否则拒绝执行。

## 十、Checkpoint 内容构建算法

```ts
async function buildGoalCheckpoint(input): Promise<GoalExecutionCheckpoint> {
  const plan = goalPlanStore.getPlan(input.planId);
  const runner = normalizeRunnerState(plan.runner);
  const currentTask = resolveAuthoritativeCurrentTask(plan, runner);
  const progress = aggregateProgress(plan.tasks);
  const recentEvents = selectRecentRunTrace(plan.runTrace, currentTask.taskId);
  const evidence = projectEvidenceIndex(plan, currentTask.taskId, recentEvents);
  const tools = projectOpenToolCalls(input.openToolCalls, evidence);
  const proposedHandoff = await maybeSynthesizeHandoff({
    plan,
    currentTask,
    recentEvents,
    evidence,
  });

  return normalizeAndValidateCheckpoint({
    ...deterministicFields(plan, runner, currentTask, progress),
    ...boundedNarrativeFields(proposedHandoff),
    recentActions: deriveRecentActions(recentEvents, evidence),
    openToolCalls: tools,
    firstAction: validateOrFallbackFirstAction(proposedHandoff, plan, currentTask),
    doNotRepeat: deriveDoNotRepeat(plan, recentEvents, evidence),
  });
}
```

### 10.1 mostImportantFact 选择

优先级：

1. 用户最近改变目标/边界的明确要求。
2. 当前 task 的 blocker 或导致策略改变的失败证据。
3. 当前 task 的不可逆状态。
4. 下一个动作成立所依赖的关键事实。
5. 如果都没有，使用当前 task 和成功标准的最短陈述。

不得用泛化句子，例如“继续完成任务”“注意上下文”。

### 10.2 firstAction 选择

按以下决策树：

```text
有 mustReadEvidenceRefs 未读取？ → inspect evidence
有 running/unknown tool call？    → query status
有 pending verification？        → verify
当前 task 尚无实现证据？          → 执行该 task 的最小下一步
当前 task 已完成但未写回？         → goal_update_task
所有 task 完成但 DoD 未过？        → run success criterion
全部通过？                         → synthesize completion
```

`firstAction.successCheck` 必须具体，例如测试命令 exit 0、文件含字段、工具状态 completed；禁止只写“确认没问题”。

### 10.3 handoffNote 模板

```text
当前目标：...
当前任务：taskId / title
最近完成：...（附 Evidence refs）
当前工作：...
关键事实：...
已确认决策：...
失败/否决方案：...
未闭合事项：...
风险/阻塞：...
后续第一步：...
第一步成功标准：...
不要重复：...
```

模板用于可读性；结构化字段才用于机器恢复。

## 十一、System Context 注入与恢复提示

### 11.1 新增 Prompt Source

在 `packages/system-context/src/sources/goal-checkpoint-source.mjs` 新增独立 source，并由 `prompt-assembler.mjs` 在 `goal-runner-source` 之后、`continuity-source` 之前注册。

输入仅接受宿主从 Goal Store 读取并规范化的：

```ts
interface GoalCheckpointPromptInput {
  readonly checkpoint: GoalExecutionCheckpoint | null;
  readonly expectedPlanId?: string;
  readonly expectedRunId?: string;
}
```

source 必须拒绝：

- `status !== 'committed'` 的 checkpoint。
- `planId/runId` 与当前 Runner 不一致。
- digest 校验失败。
- sequence 小于等于 `lastConsumedCheckpoint.sequence` 的过期记录。
- schemaVersion 不支持且无法迁移的记录。

### 11.2 注入格式

模型看到的 checkpoint 分为机器头和人类可读正文：

```text
Active Goal execution checkpoint (authoritative runtime state, scope=run).
checkpointId=...
sequence=...
planId=...
runId=...
currentTaskId=...
digest=...
resumePolicy=...

Current objective: ...
Current work: ...
Most important fact: ...
Progress: ...
Recent actions:
- ... [evidenceRefs=...]
Pending verification:
- ...
Do not repeat:
- ...
Open tool calls:
- ... replayPolicy=...
Must read evidence:
- ...
First action: ...
First action success check: ...
Handoff: ...
```

这段提示必须声明：它是 factual runtime state，不是用户消息，不得被低优先级摘要改写。

### 11.3 注入预算

Checkpoint source 必须在组装前测 token：

- 正常上限 `4,096` tokens。
- 达到上限时先删除较旧 `recentActions`，再压短 `handoffNote`，绝不删除 `firstAction/currentTaskId/mostImportantFact/pendingVerifications/doNotRepeat/openToolCalls`。
- 如果最小 checkpoint 仍超上限，写 artifact 并注入结构化核心 + artifact ref；不得静默截断 JSON 造成字段不完整。

### 11.4 首轮恢复确认

恢复 turn 的 provider 响应不要求输出冗长“我已理解”，但运行时必须观察到以下任一事件：

- 发起与 `firstAction` 匹配的工具调用。
- 使用 Goal Store 更新对应任务/验证结果。
- 明确返回 `checkpoint_resume_blocked`，说明具体阻塞与需要的输入。

普通闲聊文本不算恢复成功。

## 十二、持久化与崩溃恢复

### 12.1 持久化布局

沿用现有 Goal Store 的逻辑布局；实际根目录由 `createGoalPlanStore({ storeDir })` 注入，默认来自宿主 `pathOf('goalPlans')`，不能在协议中硬编码成某个 home 目录：

```text
<goal-store-dir>/
├── index.jsonl
├── evidence-index.jsonl
├── .changes.jsonl
└── <planId>.json
```

`contextCheckpoint` 嵌入 `<planId>.json` 的 `runner`。不新增独立可编辑 markdown 作为状态真源；否则计划文件与交接文件会发生双写竞争。

可选诊断 artifact 路径同样由宿主配置，例如：

```text
<goal-checkpoint-artifact-dir>/<planId>/<sequence>-<checkpointId>.json
```

它仅用于审计/排错，写入失败不得阻断主事务，且恢复时仍以 GoalPlan 内最新 committed checkpoint 为准。

### 12.2 原子写入

复用 Goal Store 的：

```text
serialize → write <planId>.json.tmp → rename <planId>.json
```

必须新增 CAS 校验和单进程锁：`planId` 粒度只能同时有一个 checkpoint/compaction 事务。跨进程并发由持久化 revision 和 expected version 检测，冲突方重新读取后决定退出或重试。

### 12.3 Conversation 与 Goal 的跨存储一致性

GoalPlan 和 conversation 当前不在同一数据库，不能做真正 ACID 事务。采用 saga + write-ahead checkpoint：

```text
A. commit checkpoint to GoalPlan
B. compact and persist conversation (includes checkpointId)
C. mark checkpoint conversationRevision / compaction committed
D. rehydrate and resume
E. consume checkpoint
```

每一步幂等。崩溃恢复根据以下矩阵：

| Goal checkpoint | Conversation compaction | 恢复动作 |
|---|---|---|
| 无 / preparing | 无 | 丢弃 preparing，正常继续或重新触发 |
| committed | 无 | 使用原始 conversation 重新执行 compaction |
| committed | 有同 checkpointId | 跳过再次压缩，直接 rehydrate |
| committed | 有不同更新 checkpoint | 按 sequence/revision 选择最新合法组合，旧记录 supersede |
| consumed | 有 | 正常 running |
| consumed | 无 | 数据损坏；从 artifact / continuity 重建并进入 repair |

### 12.4 应用启动恢复扫描

Goal Runner 启动时扫描：

```ts
for (const plan of goalStore.listExecutingPlans()) {
  const cp = plan.runner.contextCheckpoint;
  if (!cp) continue;
  if (cp.status === 'preparing' && isStale(cp)) rollbackPreparing();
  if (cp.status === 'committed') enqueueCheckpointRecovery(plan.planId);
  if (plan.runner.status === 'compacting_context') enqueueCompactionRecovery(plan.planId);
  if (plan.runner.status === 'resuming_after_compaction') enqueueResumeRecovery(plan.planId);
}
```

`isStale` 只决定是否重建 preparing 记录，不得把 Goal 标记失败。恢复队列遵守现有 Runner 并发限制。

### 12.5 取消与用户新消息竞态

- 用户取消 Goal：中止当前 compaction signal，checkpoint 标为 `superseded`，Runner 进入取消终态；不得自动 resume。
- 用户暂停：允许已经开始的原子持久化完成，但不发新 provider request；状态转 `paused`。
- 用户在 compact 中追加消息：消息先持久化，当前 checkpoint 记录的 `conversationRevision` 失效；compact commit 前检测 revision，重新 prepare，把新用户要求提升为最高优先级。
- 用户修改 plan：`planVersion` 变化使 CAS 失败；重新生成 checkpoint。
- 同时发生 provider overflow 和 soft preflight：按 `conversationId + runId` single-flight 合并为一个 compactionId。

### 12.6 Checkpoint、run trace 与 artifact 回收

无限续航不能让磁盘状态无界增长：

- `runner.contextCheckpoint` 永远只保存当前记录；新 checkpoint commit 时，旧 consumed/superseded 记录退出 Runner。
- run trace 当前实现会 append；新增归档策略：活动计划内保留最近 500 个轻量事件或最近 30 天事件（二者取更小集合），更早事件聚合成 task/checkpoint 统计后写审计 artifact。
- `goal_checkpoint_*` 事件不保存 handoff 正文、原始 args 或完整 Evidence 内容。
- checkpoint 诊断 artifact 默认保留：执行中 Goal 全部；Goal 终态后最近 20 个或 30 天；用户删除 Goal 时清理。
- Evidence/artifact 有独立保留策略，run trace 归档不得删除仍被 GoalTask / criterion 引用的 Evidence。
- continuity 只保 active merged summary；旧版本随 conversation revision 管理，不进入 prompt。
- 回收任务必须可中断、可重试，失败只报警，不阻断 Goal 执行。

## 十三、Goal Runner 集成

### 13.1 Runner 状态转换 API

`goal-plan-store.mjs` 增加：

```ts
prepareContextCheckpoint(planId, input)
commitContextCheckpoint(planId, input)
markContextCompactionPersisted(planId, input)
markContextCheckpointConsumed(planId, input)
supersedeContextCheckpoint(planId, input)
recoverContextCheckpoint(planId)
```

这些 API 内部统一调用现有 `persist()` 和 `appendRunTraceEvent()`，调用者不得用通用 `setRunnerState()` 拼装半个 checkpoint。

Run trace 新事件：

```text
goal_checkpoint_prepared
goal_checkpoint_committed
goal_compaction_started
goal_compaction_degraded
goal_compaction_persisted
goal_resume_started
goal_checkpoint_consumed
goal_checkpoint_superseded
goal_compaction_unrecoverable
```

事件仅保存：ids、sequence、taskId、budget、降级层、duration、error code、Evidence refs；不存完整 handoff。

### 13.2 Goal Runner tick

现有 Runner tick 入口增加最前置恢复分支：

```ts
if (runner.contextCheckpoint?.status === 'committed') {
  return resumeFromCheckpoint(plan);
}
if (runner.status === 'compacting_context') {
  return recoverCompaction(plan);
}
if (runner.status === 'resuming_after_compaction') {
  return continueResumeGuard(plan);
}
return runNormalGoalTick(plan);
```

普通任务调度不得越过未消费 checkpoint。

### 13.3 无限续航与 Runner 预算

“上下文可无限续航”不等于取消成本、回合、工具和无进展预算。需要把预算拆成两类：

```text
segment budget：一次 compaction 之间的 provider turns / tool calls / token runway
run safety budget：整个 Goal 的成本、时间、连续无进展次数和高风险操作上限
```

规则：

- 成功 consume checkpoint 后，`segmentRoundCount/segmentToolCallCount` 清零；现有累计 `roundCount/toolCallCount` 保留作遥测，不直接因为压缩次数增加而失败。
- `maxTurns/maxToolCalls` 若继续作为全 run 硬上限，会与“直到 Goal 完成”冲突；应迁移为 segment 上限或由用户/策略配置的安全预算。
- `budget_exhausted` 只由真实成本/时间/风险预算触发，不能由 `compactionCount` 触发。
- 增加 no-progress 熔断：连续 3 个 segment 的 task/evidence/progress/digest 均无变化时，进入 re-diagnose；再次无进展才 blocked。
- 每个 segment 必须至少产生以下之一，否则不算有进展：task 状态变化、新 Evidence、成功验证、blocker 明确化、用户决策请求。
- 用户可设置总成本/时长上限；达到后应 `waiting_user/budget_exhausted`，不是伪装成 Goal completed。
- compaction/resume 内部请求计入成本遥测，但不占任务业务回合预算。

因此，系统允许无限次**有进展的** compaction/resume；不允许无限空转。

### 13.4 任务边界主动 checkpoint

为了避免单轮无限膨胀，在以下稳定边界主动 checkpoint，即使尚未到 soft threshold：

- 叶子任务从 `running` 变为 `completed/failed/waiting_user`。
- 大型实现阶段结束，下一步切到验证。
- Explorer 聚合完成，主 Runner 将开始 act。
- Verifier 完成，Runner 将调整计划。
- 当前工具累计结果超过 keepBudget 的 75%。

任务边界 checkpoint 可只写结构状态，不一定立即压缩；下一次 preflight 复用它，减少触顶时的紧急工作。

### 13.5 完成门槛

Goal 不因 compaction/resume 自动完成。完成仍要求：

1. 所有必需叶子任务有合法终态。
2. completed 任务有 Evidence refs。
3. 自动 successCriteria 都有 passed result 和 evidenceRef。
4. 无未决 blocker / open tool call。
5. checkpoint 的 pendingVerifications 为空。
6. 最终完成消息持久化成功。

最后一个 checkpoint 可标 `consumed` 后再将 Runner/Plan completed；不能直接从 `compacting_context` 跳 completed。

## 十四、Compaction Pipeline 集成

### 14.1 Coordinator 入参

`runCompactionCheck()` 增加可选：

```ts
interface GoalCompactionContext {
  planId: string;
  runId: string;
  checkpointId: string;
  compactionId: string;
  sequence: number;
  keepPolicy: GoalKeepPolicy;
  recoveryLevel: number;
}
```

普通 chat 为 `undefined`，保持原语义。Goal 与普通 chat 的差异通过显式策略对象表达，不再散落 `if (goal)`。

### 14.2 返回值

```ts
interface CompactionResult {
  // existing fields...
  goal?: {
    checkpointId: string;
    compactionId: string;
    sequence: number;
    recoveryLevel: number;
    projectedTools: string[];
    excludedTools: string[];
  };
  budgetBreakdown: {
    before: number;
    system: number;
    tools: number;
    checkpoint: number;
    continuity: number;
    recentTail: number;
    after: number;
    target: number;
  };
}
```

错误对象增加结构化字段，而不是只解析 message：

```ts
error.code = 'GOAL_CONTEXT_UNRECOVERABLE';
error.budgetBreakdown = ...;
error.minimumRecoveryLevelTried = 8;
error.fixedFloorTokens = system + minimumTools + minimumCheckpoint;
```

### 14.3 触发阈值与目标值分离

触发阈值不是压缩后目标：

```text
softTrigger  ≈ 72%
hardTrigger  ≈ 88%
targetAfter  ≈ 55%
```

这样每次压缩留出足够 runway，避免一两轮后再次触顶。大窗口模型可按 provider 输出 token reservation 动态调整；所有比例以统一 Context Accounting Pipeline 为准。

### 14.4 累积摘要

第二次及后续压缩不得把上次 checkpoint 当普通历史摘要反复膨胀：

- continuity summary 采用 replace/merge，不是无界 append。
- 旧 checkpoint 不进入 summary 正文；只保留影响后续的长期决策、失败经验和 Evidence refs。
- 当前 checkpoint 始终由 Goal Store重新注入。
- summary metadata 记录 `coveredCheckpointSequence`，用于判断历史覆盖范围。

## 十五、Desktop 与 TUI 接入

### 15.1 共享层

必须下沉共享：

- Protocol types：`packages/protocol/src/goal.ts`。
- Keep selection、budget calculation、checkpoint validation/digest：`packages/runtime-core/src/`。
- Tool materialization：`packages/runtime-node/src/tool-artifact-store.ts`。
- Prompt source：`packages/system-context/src/sources/goal-checkpoint-source.mjs`。
- Goal store / Runner 暂时继续复用 Desktop main 实现，后续按 22/23 号架构文档逐步下沉 runtime-node。

### 15.2 Desktop

改造点：

- `provider-request-coordinator.mjs`：识别 Goal request，压缩前 prepare/commit checkpoint。
- `compaction-coordinator.mjs`：接收 Goal context，发送阶段事件，持久化后更新 checkpoint。
- `main.mjs persistCompactionToConversation`：写 checkpoint refs / revision。
- `goal-runner.mjs`：增加恢复优先分支和 consume guard。
- `ChatSurface.tsx`：显示“正在整理上下文并继续”，不得把 compaction 当终态；完成后保持贴底。

### 15.3 TUI

TUI 已复用 Goal store/Runner，但 provider controller 仍有宿主接线：

- `chat-controller.ts/provider-chat-model.ts` 使用同一 checkpoint prepare/commit API。
- `context-compact.ts` 复用 runtime-core 的 Goal keep/预算算法，不再维护分叉模板。
- 状态栏显示 `Compacting context (checkpoint N)…` 和 `Resuming goal…`。
- 进程退出后重新启动，TUI 也执行 committed checkpoint 恢复扫描。

### 15.4 跨端一致性

同一 plan 可在 Desktop/TUI 间继续时：

- 新宿主读取同一 GoalPlan/checkpoint。
- 宿主生成新 `streamId`，但保留 `runId`。
- `contextEpochId` 如变化则重建 system prompt。
- open tool call 若属于旧宿主且无法查询，按 replayPolicy 进入 blocked/safe retry，不伪造 completed。

## 十六、事件与 UI 协议

### 16.1 Compaction 事件

扩展 `chat:compaction`：

```ts
interface GoalCompactionEvent {
  conversationId: string;
  streamId?: string;
  stage:
    | 'checkpointing'
    | 'start'
    | 'degrading'
    | 'persisting'
    | 'rehydrating'
    | 'resuming'
    | 'done'
    | 'error';
  planId?: string;
  runId?: string;
  checkpointId?: string;
  compactionId?: string;
  sequence?: number;
  recoveryLevel?: number;
  retryable?: boolean;
  fatal?: boolean;
  message?: string;
  budgetBreakdown?: CompactionBudgetBreakdown;
}
```

`done` 仅表示压缩事务完成，不表示 Goal 完成。Goal Runner 随后继续发正常 stream 事件。

### 16.2 用户体验

默认横幅文案：

```text
正在整理上下文，目标会自动继续…
已保存进度，正在恢复当前任务…
```

只在以下情况打断用户：

- 高风险未闭合工具状态无法确认。
- 凭据/权限缺失。
- GoalPlan 与用户新要求冲突，需要产品决策。
- D8 固定底座仍超 provider 窗口。

不要展示内部摘要全文；调试面板可展示 checkpoint id、sequence、预算分项、降级层和第一动作。

### 16.3 滚动与消息列表

压缩后 conversation messages 会整表重写。Desktop 必须：

1. 在 compaction start 捕获 stick-to-bottom 状态和可见 anchor。
2. 更新 messages 后 reset virtual measurements。
3. 如果之前贴底，多帧重试贴底；如果用户在看历史，恢复 anchor 而非强制跳底。
4. checkpoint/handoff 系统消息不作为普通聊天气泡显示。

## 十七、错误分类与恢复策略

| 错误码 | 含义 | Goal 行为 |
|---|---|---|
| `GOAL_CHECKPOINT_CONFLICT` | planVersion/runId/CAS 冲突 | 重读并重新 prepare |
| `GOAL_CHECKPOINT_INVALID` | 必填字段或 digest 错 | 确定性重建；不压缩 |
| `GOAL_CHECKPOINT_PERSIST_FAILED` | Goal Store 写失败 | 重试/阻塞；不删历史 |
| `CONTEXT_COMPACTION_INSUFFICIENT_REDUCTION` | 当前层降幅不足 | 进入下一降级层 |
| `GOAL_CONTEXT_UNRECOVERABLE` | D8 固定底座仍超窗 | 非自动重试，blocked/failed |
| `GOAL_CONVERSATION_PERSIST_FAILED` | conversation 写失败 | 保留 committed checkpoint，saga 恢复 |
| `GOAL_REHYDRATE_FAILED` | system prompt 重建失败 | 不发 provider；重试 |
| `GOAL_RESUME_GUARD_FAILED` | 第一动作未被遵守 | 重试 recovery turn，达到上限后 blocked |
| `GOAL_OPEN_TOOL_UNKNOWN` | 副作用工具状态未知 | 查询/等待用户，不盲重跑 |
| `GOAL_CHECKPOINT_STALE` | sequence/revision 已落后 | supersede，不执行 |

重试使用指数退避但有上限；“无限续航”指压缩次数不设业务上限，不表示对同一个确定性错误无限空转。相同错误签名连续出现 3 次且无 token/状态改善时，进入 repair 或 blocked，避免 runaway。

## 十八、安全与隐私

1. Checkpoint 经过与 system context 相同的 secret redaction。
2. 工具输出只记录 ref 和关键 findings，不复制原始凭据。
3. 用户提供的 prompt injection 文本即使出现在 tool_result/summary 中，也标为 untrusted evidence，不可覆盖 checkpoint 协议。
4. `firstAction` 若来自模型，必须经权限和风险分类；高风险不可因恢复自动绕过确认。
5. checkpoint artifact 权限与 Goal Store 相同，仅本地用户可读。
6. 遥测禁止上传 handoff 正文、用户原文、文件路径全文和 Evidence 内容；只上报计数、耗时、错误码、hash 和 token 分项。
7. 删除 Goal 时同步删除 checkpoint 诊断 artifact；Evidence 依既有保留策略处理。

## 十九、可观测性

### 19.1 结构化日志

每次事务记录：

```text
planIdHash, runIdHash, checkpointSequence, compactionId,
triggerReason, recoveryLevel,
beforeTokens, afterTokens, targetTokens,
systemTokens, toolsTokens, checkpointTokens, continuityTokens, tailTokens,
oldMessageCount, keptMessageCount, materializedToolResultCount,
checkpointPrepareMs, summaryMs, persistMs, rehydrateMs, resumeMs,
outcome, errorCode
```

### 19.2 指标

- `goal_compaction_total{reason,outcome,level}`
- `goal_compaction_duration_ms`
- `goal_compaction_reduction_ratio`
- `goal_checkpoint_size_tokens`
- `goal_resume_latency_ms`
- `goal_resume_guard_failure_total`
- `goal_duplicate_action_prevented_total`
- `goal_open_tool_recovery_total{policy,outcome}`
- `goal_compactions_per_completed_goal`
- `goal_unrecoverable_context_total{provider,model}`

### 19.3 SLO

- 99% Goal compaction 成功进入 resume，不需要用户输入。
- 99% resume 在压缩持久化后 10 秒内开始（不含 provider 排队）。
- 0 个因 compaction done 被误标 completed 的 Goal。
- 0 个已知副作用工具因恢复而无 idempotency guard 重复执行。
- 对支持的最小 contextWindow，D8 请求必须可装入；否则模型配置在启动时标记不支持 Goal 无限续航。

## 二十、迁移与兼容

### 20.1 schemaVersion

- `GoalExecutionCheckpoint.schemaVersion = 1`。
- GoalPlan 顶层 schema 版本递增，读取旧 plan 时 `contextCheckpoint=undefined`。
- 只有首次 checkpoint 时才写新字段，采用惰性迁移。
- 未识别字段保留，保证向前兼容。

### 20.2 旧 continuity

没有 checkpoint refs 的旧 compaction 继续可读；下一次 Goal 压缩生成 sequence 1，并把现有 continuity 当历史语义输入，不尝试从旧摘要伪造已完成 Evidence。

### 20.3 feature flags

```text
goalContextCheckpoint.enabled
goalContextCheckpoint.boundedKeepEnabled
goalContextCheckpoint.toolProjectionEnabled
goalContextCheckpoint.crashRecoveryEnabled
```

先内部 dogfood，再 beta；每个 flag 必须有 kill switch。禁用 checkpoint 时回到现有链路，但 bounded keep 可独立开启。

## 二十一、文件级施工清单

### Phase 1：协议与纯函数

1. `packages/protocol/src/goal.ts`
   - 增加 checkpoint types、Runner status 和 state 字段。
2. `packages/runtime-core/src/goal-checkpoint.ts`（新）
   - normalize、validate、digest、size limits、firstAction fallback。
3. `packages/runtime-core/src/goal-keep-policy.ts`（新）
   - bounded tail、tool pair safety、budget/degrade ladder。
4. `packages/runtime-core/src/context-compaction.ts`
   - 接入显式 keep policy 和 Goal metadata。
5. package export / d.ts
   - 暴露上述协议与纯函数。

### Phase 2：Goal Store 与 Runner

1. `apps/desktop/electron/main/goal-plan-store.mjs`
   - checkpoint CAS API、状态转换、run trace 事件、惰性迁移。
2. `apps/desktop/electron/main/goal-runner.mjs`
   - prepare/build/recover/consume；tick 恢复优先分支。
3. `apps/desktop/electron/main/goal-runner-message-persistence.mjs`
   - 不把 checkpoint 当普通 assistant 消息。
4. `apps/tui/src/goal-runner-adapter.ts`
   - 暴露同一恢复入口。

### Phase 3：Compaction 与 provider 链路

1. `apps/desktop/electron/main/chat-runtime/provider-request-coordinator.mjs`
   - preflight 前 checkpoint transaction。
2. `apps/desktop/electron/main/chat-runtime/compaction-coordinator.mjs`
   - Goal context、阶段事件、分层降级、saga 状态。
3. `apps/desktop/electron/main/context-compactor.mjs`
   - bounded Goal keep、budget breakdown、Goal metadata。
4. `apps/desktop/electron/main/main.mjs`
   - conversation checkpoint refs/revision。
5. OpenAI / Anthropic / Gemini loops
   - 统一传 run/goal/tool ledger，不在各 loop 复制策略。

### Phase 4：System Context 与跨端 UI

1. `packages/system-context/src/sources/goal-checkpoint-source.mjs`（新）。
2. `packages/system-context/src/prompt-assembler.mjs`。
3. Desktop preload/protocol types/`ChatSurface.tsx`。
4. TUI `chat-controller.ts`、`provider-chat-model.ts`、状态栏组件。
5. 调试面板显示 checkpoint/budget/recovery level。

### Phase 5：崩溃恢复、工具 ledger 与 rollout

1. 启动扫描和 saga repair。
2. Tool idempotency ledger / open call query。
3. Metrics、feature flags 和 kill switches。
4. 多次 compaction soak test。
5. beta 迁移和线上告警。

## 二十二、测试矩阵

### 22.1 纯函数测试

- checkpoint normalize：字段裁剪、去重、优先级、digest 稳定。
- invalid currentTaskId 自动回落到 next runnable。
- firstAction fallback 决策树每个分支。
- keep 按 user turn / message / token 三重限制。
- tool call/result 不产生 orphan。
- user 超长、tool_result 超长、Anthropic block、OpenAI tool role、Gemini 变体。
- D0→D8 每层预算单调不增。
- tools projection 保留 firstAction 必需工具。

### 22.2 Goal Store 测试

- prepare → commit → persisted → consumed 正常路径。
- CAS planVersion/runId/checkpoint predecessor 冲突。
- 原子 rename 失败不破坏旧 plan。
- 旧 schema 惰性迁移。
- run trace 不复制正文。
- Evidence gate 仍然生效。
- cancel/pause/new user message 竞态。

### 22.3 Compaction 测试

- 最近 current turn 超大时 bounded keep 过线。
- tools 固定底座过大时投影后过线。
- D8 仍超限抛结构化 unrecoverable。
- continuity 多轮 merge 不线性膨胀。
- checkpointId 写入 conversation metadata。
- persist 失败不发 done，保留 committed checkpoint。
- rehydrate 失败不发 provider request。

### 22.4 Resume 测试

- checkpoint 后第一个动作严格匹配 firstAction。
- must-read Evidence 未读取时禁止 edit。
- completed tool idempotency key 不重跑。
- running tool query status。
- unknown side-effect tool 转 blocked。
- 模型闲聊不 consume checkpoint。
- firstAction 写回 Evidence 后 consume。
- plan 在压缩中修改后旧 checkpoint stale。

### 22.5 崩溃注入测试

分别在以下点 `process.exit` / 注入异常并重启：

1. preparing 写入前后。
2. committed 写入后、conversation compact 前。
3. conversation `.tmp` 写入后、rename 前。
4. conversation compact 后、checkpoint persisted 前。
5. rehydrate 前后。
6. provider request 发出前后。
7. tool result 产生后、Evidence 写回前。
8. checkpoint consume 前后。

每个点验证：不丢 Goal、不重复副作用、不产生孤儿 tool_result、可明确恢复或阻塞。

### 22.6 无限续航 soak test

构造 Goal：

- 30 个有依赖叶子任务。
- 每任务产生大 tool artifact。
- contextWindow 人工缩到 16k/32k。
- 每 1–2 个 task 强制触发 compaction。
- 至少 10 次 checkpoint/compact/resume。

断言：

```text
same planId
same logical runId
strictly increasing checkpoint sequence
all required task evidence preserved
no duplicate idempotency keys executed
all success criteria passed
plan completed
```

同时在 OpenAI/Anthropic/Gemini adapter 和 Desktop/TUI 两宿主运行合同测试。

### 22.7 UI 测试

- 横幅阶段顺序正确。
- compaction done 不结束 Goal stream。
- 切会话回来能恢复当前阶段。
- 压缩后贴底/anchor 不跳顶部。
- 用户取消可停止 resume。
- 调试面板不泄露正文/secrets。

## 二十三、验收命令建议

落地后至少运行：

以下命令已按当前 `package.json` script 和现有测试文件名校准；新增文件落地后再把它们加入对应 package test glob：

```bash
# Protocol 当前没有 test script：用 typecheck + build 验证协议
pnpm --filter @peer-agent/protocol typecheck
pnpm --filter @peer-agent/protocol build

# Runtime core / System Context
pnpm --filter @peer-agent/runtime-core test
pnpm --filter @peer-agent/runtime-core typecheck
pnpm --filter @peer-agent/system-context test
pnpm --filter @peer-agent/system-context typecheck

# Desktop main 定向测试
node --test apps/desktop/electron/main/context-compactor.test.mjs
node --test apps/desktop/electron/main/chat-runtime/compaction-coordinator.test.mjs
node --test apps/desktop/electron/main/chat-runtime/provider-request-coordinator.test.mjs
node --test apps/desktop/electron/main/goal-plan-store.test.mjs
node --test apps/desktop/electron/main/goal-runner.test.mjs

# Desktop/TUI package tests
pnpm --filter @peer-agent/desktop test
pnpm --filter @peer-agent/tui test

# 全仓类型与构建
pnpm typecheck
pnpm build
```

这些是实施后的验收命令，不代表本文编写时已经运行过未来新增的测试。

## 二十四、发布门槛

### Definition of Done

- [ ] Protocol、Store、Runner、Compactor、System Context、Desktop/TUI 均使用同一 checkpoint schema。
- [ ] Goal compaction 有 committed checkpoint 写前日志。
- [ ] keep 有 token + turn + message 硬预算。
- [ ] 大 tool_result 在进入 keep 前材料化。
- [ ] checkpoint 后第一动作有运行时守卫。
- [ ] compaction 可重复至少 10 次并最终完成 Goal。
- [ ] 崩溃恢复矩阵全部通过。
- [ ] 副作用工具有 idempotency guard。
- [ ] 自动 successCriteria 仍由 Evidence gate 控制。
- [ ] Desktop/TUI 合同测试通过。
- [ ] 遥测和 UI 不泄露 checkpoint 正文。
- [ ] feature flag/kill switch 可用。

### 不允许上线的情况

- 仍有任何路径把 `chat:compaction done` 当 Goal terminal。
- checkpoint 可以由模型直接改写 task status。
- conversation 已删除 old，而 checkpoint 尚未 committed。
- 恢复时默认重跑未知状态的副作用工具。
- D0 失败后直接 Goal failed，没有降级梯子。
- 多轮 summary/checkpoint 随 compaction 次数线性膨胀。

## 二十五、实施顺序与每阶段退出条件

### Milestone A：有界上下文

交付：Goal keep budget、tool materialization、预算分项、D0–D6。

退出条件：当前失败样例不再因 current turn tool 尾导致 `minimal candidate≈before`；现有普通 chat/manual compact 测试不回归。

### Milestone B：可恢复检查点

交付：协议、Goal Store CAS、prompt source、resume first-action guard。

退出条件：一次 compaction 前后同 run 连续完成当前 task；已完成动作不重复。

### Milestone C：事务与崩溃恢复

交付：saga、启动扫描、open tool ledger、idempotency。

退出条件：崩溃注入矩阵通过，无重复副作用。

### Milestone D：无限续航与双宿主

交付：10+ 次 soak、Desktop/TUI 一致性、指标/UI/flags。

退出条件：人工小窗口下 Goal 经多次 compact/resume 后全部 successCriteria 通过并 completed。

## 二十六、最终行为示例

```text
T0 用户创建 Goal
T1 Runner 创建计划，runId=R1，执行 task A
T2 tool results 材料化；A 完成并写 Evidence
T3 达 soft threshold
T4 prepare checkpoint C1(sequence=1)
   - currentTask=B
   - recentActions=[A completed]
   - mostImportantFact=...
   - firstAction=读取 B 所需 evidence X
   - doNotRepeat=[A 的 edit/test]
T5 commit C1
T6 compact old → summary；recent tail 限定 16k
T7 conversation 持久化引用 C1；system rehydrate
T8 同 run R1 恢复，先读取 evidence X
T9 firstAction 写回后 consume C1，继续 B
...
T20 第十次压缩 C10，runId 仍为 R1
...
T30 所有任务和 successCriteria 有 Evidence
T31 Goal completed
```

从用户视角，整个过程只是一条持续运行的 Goal；压缩是内部维护步骤。模型不需要记住从 T0 起的全部原文，因为目标和进度来自 GoalPlan，执行游标来自 Checkpoint，历史原因来自 Summary，局部协议来自有界 Recent Tail。

## 二十七、最终原则

```text
Plan owns what is true.
Checkpoint owns what happens next.
Evidence proves what already happened.
Summary carries why.
Recent tail carries protocol locality.
Compaction never ends the Goal.
```

中文表述：

> 计划保存事实，检查点保存接力棒，证据证明已完成，摘要保存缘由，最近窗口保存协议现场；上下文压缩永远不是 Goal 的终点。
