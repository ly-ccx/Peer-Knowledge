# Goal 模式多 Agent 编排体系计划

> 创建时间：2026-07-04
> 最后更新：2026-07-04
> 状态：方案沉淀（Draft）
> 关联代码：`peer_agent`（本知识库只存知识，代码改动一律在该代码仓落地）
> 关联文档：
> - `design/product/goal-mode-ultrathink-workflow.md`
> - `design/product/goal-runner-explorer-task-list.md`
> - `knowledge/decisions/35-mode-scoped-tool-projection.md`
> - `knowledge/decisions/41-rename-goal-mode-to-plan-mode.md`
> - `knowledge/specifications/15-goal-plan-lifecycle-governance.md`

---

## 一、目标

把当前 Goal Runner + 动态 readonly Explorer 的机制，升级为更完整的多 Agent 编排体系：

```text
Goal Orchestrator
  -> Main Agent
  -> Readonly Explorers
  -> Verifier
  -> Evidence-backed completion
```

目标不是堆固定角色，而是把目标推进、只读探查、完成复核和状态治理拆清楚。

核心原则：

```text
主 Agent 负责目标推进。
Explorer 只负责只读探查。
Verifier 只负责复核。
Runner 只负责编排状态。
工具执行仍走 Runtime Projection / PermissionGrant / Evidence。
```

适用范围：

- Goal 原生自驱：用户在 Goal 模式给出目标后，形成 `goal_self_driven` / `accepted_goal` 契约并进入 Runner。
- Plan 批准后执行段：按照 ADR 41 的 B2-b 修订，Plan 与 Goal 在“批准/接受后的托管执行段”共用同一个自驱 Runner；差异收敛在执行前授权方式，Plan 仍保留批准门，Goal 以目标契约接受为准。

## 二、现状判断

当前多 Agent 编排已经有基础，但还不是完整体系。

已具备：

- `GoalRunner` 是主进程托管编排器，负责 plan/runner 状态、tick、阻塞和 Explorer 派发。
- 协议和 store 已具备 `workflowKind`、`accepted`、`accepted_goal`、`GoalRunnerPhase`、`blockerAudit` 等字段；后续重点不是再补字段，而是让 Runner 真正按这些事实推进。
- 主 Agent 可以在 Runner turn 中调用 `request_explorer`。
- `request_explorer` 本身只登记请求，不直接探查。
- Runner 在回合结束后批量派发 Explorer，并把报告回填到 `GoalPlan.runner.explorers`。
- Explorer 模式只投影只读工具：`read_file`、`search_files`。
- Explorer 不允许 `bash`、`edit_file`、`write_file`、`goal_update_task`、MCP/Web/Browser 副作用能力。
- Explorer 报告不会直接改任务状态；任务完成仍必须由主 Agent 调 `goal_update_task` 并带 Evidence。

主要不足：

- 普通 Goal/Plan 用户回合中的 `request_explorer` 可能只是 ack，真正派发主要发生在 Runner 托管回合。
- `explorer-source` 已存在并已注册，但 `runExplorer` 尚未把 `explorerContext` 透传给 `sendMessage` / `buildSystemContext`；当前 Explorer 任务信息仍主要通过 user message + runtime reminder 传入。
- Explorer evidence 仍偏弱；缺失时会补 `goal-explorer://.../stream/...`，还不是严格 Evidence Registry 校验。
- 缺少 deterministic `inspect` / `plan_scaffold` 编排门；主 Agent 可能在信息不足时直接 act。
- 缺少只读 Verifier 子 Agent 独立复核完成声明。

## 三、目标架构

多 Agent 体系分四类运行主体：

| 主体 | 职责 | 可用能力 | 禁止事项 |
| --- | --- | --- | --- |
| Goal Runner | 状态机、phase、tick、并发、阻塞/恢复 | 读写 GoalPlan runner 状态 | 不直接执行本地能力 |
| Main Agent | 目标理解、行动、修复、写任务 Evidence | Goal 模式完整工具集，受 PermissionGrant 约束 | 不伪造 Tool Result / Evidence |
| Readonly Explorer | 并行只读探查，返回事实和证据 | `read_file`、`search_files` | 不写文件、不跑 shell、不改 plan |
| Verifier | 只读复核完成声明和 DoD | 只读工具 + Evidence 读取 | 不改文件、不改任务状态 |

主 Agent 是唯一行动者和唯一任务状态写入者。Explorer / Verifier 只能提供证据和建议。

运行时归属：

- Runner 的执行 turn 以 `mode: 'goal'` 驱动，从而复用 Goal 的自驱上下文、pre-act 写盘范围守卫、不可逆动作确认和 Verification Gate。
- Plan approval gate 只保护“批准前”的副作用；一旦 Plan 被批准进入托管执行段，就进入同一套 Runner / Explorer / Verifier 编排。
- Renderer 只能展示 phase、batch、verifier、blocker 和 evidence 计数，不拥有权限真相。

## 四、编排流程

完整 Goal 流程应收敛为：

```text
accept goal / approve plan execution
  -> orient
  -> inspect
  -> plan_scaffold
  -> act
  -> verify
  -> repair
  -> synthesize
```

注：协议字段使用 `plan_scaffold`，UI 可以展示为 “scaffold”，但持久化和测试必须使用协议字面量。

### 4.1 orient

读取并确认：

- 用户原始目标。
- 当前 active GoalContract / GoalPlan。
- boundaries / successCriteria。
- conversation workspace。
- 项目指令与已知上下文。

产出：

```ts
{
  phase: 'orient',
  goalUnderstanding: string,
  knownFacts: string[],
  missingFacts: string[],
  initialRisks: string[]
}
```

### 4.2 inspect

收集足够事实，不允许副作用。

允许：

- `read_file`
- `search_files`
- `goal_get_plan`
- `request_explorer`

不允许：

- `edit_file`
- `write_file`
- `bash`
- MCP/Web/Browser mutation

inspect 阶段退出条件：

- 已识别目标涉及的主要模块/文件。
- 已识别成功标准是否可自动验证。
- 已识别是否需要并行 Explorer。
- 已列出仍然未知但可接受的假设。

### 4.3 plan_scaffold

把探查结果整理成可追踪任务：

- tasks
- dependencies
- successCriteria
- boundaries
- involvedFiles
- verification plan

Goal 模式下 `plan_scaffold` 是内部导航脚手架，不是 Plan approval gate。Plan 模式的批准前计划仍然是用户审批对象；批准后执行段的 `plan_scaffold` 则用于 Runner 在执行中重整任务、证据和验证路径。

### 4.4 act

主 Agent 执行改动。

规则：

- 修改文件前必须已有足够读取上下文。
- 写入仍受 workspace / outOfScope / PermissionGrant 约束。
- 不可逆动作逐动作确认。
- 完成、失败、阻塞都要及时回写 `goal_update_task`。

### 4.5 verify

验证顺序：

1. 运行自动 DoD。
2. 检查每个 completed leaf task 是否有 Evidence。
3. 启动 Verifier 只读复核。
4. 若 Verifier 失败，进入 repair。

### 4.6 repair

修复验证失败项。

进入条件：

- 自动 DoD 失败。
- Verifier 指出证据不足。
- Verifier 指出目标未满足。
- 运行结果与 successCriteria 冲突。

### 4.7 synthesize

收口输出：

- 做了什么。
- 证据在哪里。
- 哪些检查通过。
- 哪些风险或后续项仍存在。

不能只凭 assistant 文本声明完成。

## 五、Explorer 设计

### 5.1 Explorer 请求

主 Agent 不直接创建固定角色，而是创建任务实例：

```ts
interface ExplorerRequest {
  explorerId: string;
  planId: string;
  question: string;
  reason: string;
  scope?: {
    include?: string[];
    exclude?: string[];
  };
  profile: 'readonly_explorer';
  budget: {
    maxToolCalls: number;
    maxDurationMs: number;
  };
  exitCriteria: string[];
}
```

### 5.2 Explorer 权限

Explorer 模式只允许：

```text
read_file
search_files
```

禁止：

```text
bash
edit_file
write_file
goal_update_task
goal_create_plan
request_explorer
MCP mutations
Web/Browser side effects
```

### 5.3 Explorer 输出

Explorer 必须返回结构化报告：

```ts
interface ExplorerReport {
  explorerId: string;
  planId: string;
  question: string;
  findings: Array<{
    claim: string;
    evidenceRefs: string[];
  }>;
  evidenceRefs: string[];
  confidence: 'low' | 'medium' | 'high';
  recommendedNextAction?: string;
  blockedReason?: string;
}
```

### 5.4 Explorer 证据要求

后续应从“弱引用”升级为“真实 Evidence Registry 校验”：

- Explorer 的 `read_file` / `search_files` 结果注册为 evidence refs。
- `reportExplorer` 校验 evidenceRefs 属于本次 Explorer 运行。
- 无真实 evidenceRefs 的报告不能进入 `completed`。
- Explorer 失败不阻断整批，但会进入当前 batch 的失败统计。

## 六、Verifier 设计

Verifier 是只读复核者，不是第二个行动 Agent。

输入：

```text
goal
successCriteria
changed files
task evidenceRefs
criterionResults
recent tool results
Explorer reports
```

输出：

```ts
interface VerificationReport {
  passed: boolean;
  failedCriteria: Array<{
    criterionId?: string;
    reason: string;
    evidenceRefs: string[];
  }>;
  missingEvidence: Array<{
    taskId?: string;
    reason: string;
  }>;
  risks: string[];
  recommendedNextAction?: string;
}
```

运行记录：

```ts
interface GoalVerifierRun {
  verifierId: string;
  planId: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  report?: VerificationReport;
  failureReason?: string;
}
```

落点建议：

- 持久化在 `GoalPlan.runner.verifierRuns[]`，同时可派生 latest verifier status 给 UI。
- `VerificationReport` 中的 evidenceRefs 必须引用已存在的 Tool Result / Evidence；Verifier 不产生“完成证据”，只复核已有证据是否足以支撑完成声明。
- Verifier 报告不能绕过 `criterionResults`。最终 completed 仍必须同时满足：自动 DoD passed、completed leaf task evidence 完整、Verifier passed。

规则：

- Verifier 只读。
- Verifier 不调用 `goal_update_task`。
- Verifier 不修改文件。
- Verifier 不决定最终状态，只给 Runner 和 Main Agent 提供复核事实。
- Runner 根据 Verifier 报告进入 `synthesize` 或 `repair`。
- Verifier failed / missingEvidence / failedCriteria 均进入 `repair`，由 Main Agent 修复并重新写入任务 Evidence 或 criterionResults。

## 七、Runner 调度策略

### 7.1 Phase 状态

在 `GoalRunnerState` 中明确 `phase`：

```ts
type GoalRunnerPhase =
  | 'orient'
  | 'inspect'
  | 'plan_scaffold'
  | 'act'
  | 'verify'
  | 'repair'
  | 'synthesize'
  | 'blocked';
```

phase 是编排事实，不替代工具执行 Evidence。

### 7.2 Explorer 并发

保留当前模型：

- 默认并发：5。
- 硬上限：8。
- 同一轮 Explorer 共享 `batchId`。
- 单个 Explorer fail-soft。

增强：

- 按 priority 排序。
- 对相同 `question + scope` 做 fingerprint 去重。
- 整批失败率过高则 Runner blocked。
- Explorer batch 完成后强制 re-anchor。

### 7.3 no-progress 与 blocker audit

当前 no-progress 以“完成数 + 叶子 Evidence 数”作为双信号。后续增强为 blocker audit：

```ts
interface BlockerAudit {
  fingerprint: string;
  occurrences: number;
  firstSeenAt: string;
  lastSeenAt: string;
  reason: string;
}
```

同一 blocker 连续出现达到阈值后进入 `blocked`，避免盲目烧轮次。

## 八、System Context 接入

### 8.1 Explorer Context Source

`explorer-source` 已经存在并能渲染 `runtime.explorer.brief` 和 `runtime.explorer.contract`。待补的是调用链接线：Runner 派发 Explorer 时，把 Explorer brief 作为 `explorerContext` 传入 `sendMessage`，再由 `buildSystemContext` 输入给 source。

```ts
explorerContext: {
  explorerId,
  planId,
  question,
  reason,
  scope,
  budget,
  exitCriteria
}
```

不要把核心任务信息长期塞进伪造 user message。允许保留最小 user trigger，但权威 brief 和 readonly contract 必须来自 System Context。

### 8.2 Goal Runner Context Source

Goal Runner 每轮注入：

- active goal。
- current task。
- boundaries。
- success criteria。
- runner phase。
- evidence count。
- explorer batch status。
- verification status。

事实上下文和执行契约分层：

```text
L7_CONTINUITY: factual runtime snapshot
L6_MODE_REMINDER: execution contract
```

## 九、UI 展示

Goal 面板应展示：

```text
Phase: inspect / plan_scaffold / act / verify / repair
Main Agent status
Explorer batch: 3/5 completed
Verifier status
Current blocker
Evidence count
Verification result
```

Goal 模式不显示 Plan approval card。

Goal 用户确认卡只用于：

- scope expansion confirmation
- irreversible action confirmation
- product/business decision
- manual DoD confirmation

## 十、分阶段落地计划

### Slice 1：Runner Phase

- 基线：协议和 store 已有 `GoalRunnerPhase` / `runner.phase` / `blockerAudit` 字段。
- Runner 在 `orient` / `inspect` / `plan_scaffold` / `act` / `verify` / `repair` / `synthesize` 间确定性推进。
- 每次 phase 变化写入 `runner.phase`，并在 context source 中作为事实注入。
- UI 展示 phase。

验收：

- Goal 启动后先进入 `orient/inspect`。
- phase 写入 runner state。
- 旧计划兼容。
- Plan 批准后的执行段也能展示同一套 phase。

### Slice 2：Explorer Context Source 接线

- 基线：`explorer-source` 已注册；尚未由 `runExplorer` 正式传入 `explorerContext`。
- `runExplorer` 传入 `explorerContext`。
- `sendMessage` / `buildSystemContext` 接收并注入 `explorerContext`。
- 移除对伪造 user message 的依赖，只保留最小任务触发消息。

验收：

- Explorer prompt 中出现 `runtime.explorer.brief`。
- Explorer contract 来源为 System Context。
- 非 explorer 模式不注入 explorer context。

### Slice 3：Explorer Evidence Registry

- 为 Explorer 读取/搜索结果注册 Evidence。
- `reportExplorer` 校验 evidenceRefs。
- 禁止无 Evidence 的 completed Explorer report。

验收：

- 无 evidenceRefs 的 Explorer report 不能 completed。
- 伪造 refs 被拒绝或 warning。
- Explorer 报告 evidence 能追溯到工具结果。

### Slice 4：Deterministic Inspect Planner

- Runner 在 `inspect` 阶段生成 `ExplorePlan`。
- ExplorePlan 产出 questions / requiredBeforeAct。
- requiredBeforeAct 为 true 时必须先派 Explorer。

验收：

- 复杂目标不会直接进入 act。
- Explorer question 可追踪。
- inspect 结束条件可测试。

### Slice 5：Verifier 子 Agent

- 新增 `mode: 'verifier'` 或复用只读 profile。
- Verifier 只投影只读工具。
- Runner 在主 Agent 声明完成后启动 Verifier。
- Verifier run 写入 `GoalPlan.runner.verifierRuns[]`，供 UI 和 repair loop 追踪。
- Runner 完成门聚合 `criterionResults`、leaf task evidence 和 latest verifier report。

验收：

- Verifier failed 时进入 repair。
- Verifier passed + DoD passed + task Evidence 完整时才能 completed。
- Verifier 无法写文件或更新 plan。
- Verifier passed 但 DoD 或 task Evidence 不完整时仍不能 completed。

### Slice 6：UI 完整呈现

- Goal 面板展示 phase。
- 展示 Explorer batch 进度。
- 展示 Verifier 状态。
- 展示 blocker audit。

验收：

- Goal UI 不混用 Plan approval。
- 用户能看清当前卡在哪个 phase。
- Explorer / Verifier 状态可追踪。

## 十一、测试清单

必须覆盖：

- Goal 启动后进入 `orient/inspect`。
- Explorer mode 只投影 `read_file/search_files`。
- Explorer report 无真实 Evidence 时不能 completed。
- Explorer 并发 fail-soft。
- Explorer batch 去重和 priority。
- 主 Agent 利用 Explorer 报告进入 act。
- Verifier failed 时 Runner 进入 repair。
- Verifier passed + DoD passed + task Evidence 完整时 Runner completed。
- Plan mode 不受影响，仍然审批后才能副作用执行；批准后的执行段进入同一套 Runner phase。
- Goal mode 不需要 plan approval，但仍受 workspace / outOfScope / irreversible confirmation / PermissionGrant 约束。

## 十二、最终验收标准

多 Agent 编排体系成型时，应满足：

1. 主 Agent 不再只靠 prompt 自觉判断是否充分了解上下文。
2. Runner 能确定性进入 inspect，并按需要派发 Explorer。
3. Explorer 只能只读，不碰状态、不执行副作用。
4. Explorer 报告必须有 Evidence。
5. Verifier 独立复核完成声明。
6. 主 Agent 是唯一行动者和状态写入者。
7. Renderer 只展示，不拥有权限真相。
8. 所有本地能力仍走 Runtime Projection / PermissionGrant / Evidence。
