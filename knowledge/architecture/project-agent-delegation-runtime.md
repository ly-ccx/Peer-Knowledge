# 项目代理委托运行时

创建时间：2026-09-24
最后更新：2026-10-01

> 状态：随 ADR 80 Accepted（2026-09-26）。§13 已关闭。落点目录以 `playbook/v0.1.0/` 为准。  
> 级别：A 级运行时契约  
> 关联决策：`knowledge/decisions/80-project-agent-delegation-model.md`  
> 关联产品稿：`design/product/project-agent-workbench.md`  
> 模块分层与建设顺序：`knowledge/architecture/project-agent-capability-layers.md`（本文管对象、工具、白名单；分层文档管模块怎么拆，§5 的调度、异常细节以分层文档为准）  
> 关联文档：
> - `knowledge/architecture/20-architecture-governance.md`
> - `knowledge/architecture/19-system-prompt-context-architecture.md`
> - `knowledge/decisions/35-mode-scoped-tool-projection.md`
> - `design/product/goal-mode-multi-agent-orchestration-plan.md`
> - `knowledge/architecture/task-lifecycle-and-acceptance-flow.md`

---

## 0. 一句话

项目代理是一条常驻 Conversation，以 `project_agent` 模式运行，只拿到只读工具和调度工具；它开出的任务锚定在触发它的用户消息上，是子 Conversation + GoalPlan，由现有 Goal Runner 推进；任务的状态变化以结构化事件回到项目代理的收件箱，由 `ProjectAgentRunner` 唤醒代理跑一轮，代理把任务交回的关键信息整理成一条回复挂回原消息。每条用户消息都有可投影的处置。

---

## 1. 运行主体与深度

| 主体 | 载体 | 生命周期 | 能力 | 能开什么 |
|---|---|---|---|---|
| 项目代理 | Conversation，`role: 'project_agent'`，每个 Workspace 一条 | 常驻，随项目存在 | 只读 + 调度（§4） | 任务；只读临时子 agent |
| 任务 | Conversation，`role: 'work_session'`，`parentConversationId` 指向项目代理 | 从开出到验收 / 取消；验收后仍可追问 | 现有 Goal 模式工具集，受 PermissionGrant 约束 | 任务内临时子 agent（Explorer / Verifier） |
| 临时子 agent | 无持久 Conversation（`ephemeral: true`，与现有 Explorer 一致） | 一次运行 | 按 profile，默认只读 | 不能开任何东西 |

深度限制由调度 Provider 在执行层校验：调用方 Conversation 的 `role` 不是 `project_agent` 时，`spawn_session` 返回结构化 `depth_limit` 失败。模式投影层也不会把调度工具投影给 `work_session` 与临时子 agent。两层都拦，不依赖 prompt。

---

## 2. 协议对象

落点：`packages/protocol/src/delegation.ts`。以下是形状草案，字段名以实现评审为准。

```ts
type WorkSessionStatus =
  | 'queued'          // 已开出，等待依赖或并发槽位，Runner 未启动
  | 'starting'        // Conversation 已建，GoalPlan 尚未持久化
  | 'awaiting_approval' // 计划待用户批准
  | 'running'
  | 'needs_user'      // 权限 / 决策 / 补充信息
  | 'verifying'       // 机器完成，正在算结论 / 代理追加核验中
  | 'result_ready'    // 签收策略 = confirm，等用户确认
  | 'accepted'        // 已签收：策略代签（acceptedBy: 'policy'）或用户确认
  | 'cancelled'
  | 'failed';

interface WorkSession {
  sessionId: string;            // = 子 conversationId
  projectAgentConversationId: string;
  workspacePath: string;
  title: string;                // = 当前 GoalPlan.title
  planId: string | null;
  status: WorkSessionStatus;    // 投影值，真源是 GoalPlan + 权限队列
  spawnedAt: string;
  spawnedByToolCallId: string;  // 项目代理那次 spawn_session 的 Tool Call
  isolation: 'none' | 'worktree';
  origin: DelegationOrigin;     // 锚定到哪条用户消息，见 §2.4
  supersededBy?: string;        // 被哪条新任务取代
}

interface SessionReport {
  sessionId: string;
  planId: string | null;
  status: WorkSessionStatus;
  summary: string;              // 任务侧生成的摘要，只是说明，不是证据
  keyFindings: {                // 任务 synthesize 阶段的结构化交回，供代理重新整理回复
    conclusions: string[];
    changes: { path: string; summary: string }[];
    openQuestions: string[];
    risks: string[];
  };                            // 同样是叙述，不是证据
  evidenceRefs: string[];       // 必须能在 EvidenceIndex / 计划持有引用里解析
  criteriaProgress: { passed: number; total: number };
  needsUser?: {
    kind: 'permission' | 'decision' | 'plan_approval' | 'input';
    pendingRequestId: string;   // 指向 main 里已有的待处理请求，不复制一份
    prompt: string;
  };
  failureReason?: string;
}

type DelegationEvent =
  | { type: 'session_spawned'; session: WorkSession }
  | { type: 'session_progress'; sessionId: string; report: SessionReport }
  | { type: 'session_needs_user'; sessionId: string; report: SessionReport }
  | { type: 'session_verified'; sessionId: string; report: SessionReport; verdict: VerificationVerdict; decision: AcceptanceDecision }
  | { type: 'session_ended'; sessionId: string; report: SessionReport }
  | { type: 'user_intervened'; sessionId: string; messageId: string }
  | { type: 'objective_signal'; objectiveId: string; observation: WatchObservation }   // ADR 82
  | { type: 'digest_due'; scheduledAt: string };
```

不变量：

1. `WorkSession.status` 是投影，不单独持久化；由 GoalPlan 状态、`resultAcceptance`、权限待处理队列计算。计算函数放在 protocol，与 `projectGoalPlan` 同层，便于 Desktop / TUI 共用。
2. `SessionReport.summary` 只能以 Tool Result 或事件事实进入项目代理上下文，不能进入 `L0`–`L6`。
3. `needsUser.pendingRequestId` 引用的是同一个待处理请求。无论用户在代理对话还是任务里批准，解决的都是同一条请求。

### 2.4 锚定：任务从哪条消息来

```ts
interface DelegationOrigin {
  parentConversationId: string;   // 项目代理会话
  anchorMessageId: string;        // 触发这条任务的用户消息
  anchorText: string;             // 用户原话，逐字写入任务首条消息，不只给代理转述
  contextSnapshotId: string;      // 截至锚点的代理对话上下文快照
  supersedes?: string;            // 取代的旧任务 sessionId
  inherited?: { reportOf?: string; branchOf?: string }; // 从旧任务继承了什么
  memorySnapshotId?: string;      // 开任务时冻结的相关记忆（ADR 81）
  objectiveId?: string;           // 由项目目标推进开出时所属的目标（ADR 82）
  modelSelection: ModelSelectionSnapshot; // 各角色模型，开任务时解析并冻结（ADR 83）
}
```

- 上下文快照复用划词子会话的机制：`buildInheritedBackground` + `background-snapshot-store`。快照由 main 按运行时事实捕获（不接受 renderer 传入的历史），有字数上限，覆盖范围和截断显式标注。
- 任务首条消息 = 用户原话 + 代理写的任务说明（目标、成功标准、边界）。快照作为事实类上下文进入任务，不作为系统指令。
- 划词子会话的 `SelectionOrigin { parentConversationId, reference, snapshotId }` 与 `DelegationOrigin` 同构；实现时抽出公共的「带快照的子会话」原语，两者共用，不复制。

### 2.5 回复：代理的话挂在哪条消息上

代理会话里的助手消息增加回复元数据：

```ts
interface AgentReplyMeta {
  replyTo: string[];              // 被回复的用户消息 id，界面显示引用条
  sourceSessionIds: string[];     // 这条回复依据的任务，界面显示来源芯片
  verdictChips: { sessionId: string }[]; // 验证结论标记，渲染时读 VerificationVerdict 投影（§2.7）
  evidenceRefs: string[];         // 追问时展开的证据；只保留能解析的引用
  cards: { type: 'needs_user' | 'plan_approval' | 'confirm_result' | 'session_failed'; sessionId: string }[];
}
```

- **用户回合**：代理的最终文本自动 `replyTo` 本轮的用户消息。本轮有多条用户消息（插话排队合并）时，自动回复最后一条，前面的消息须由调度工具或 `post_reply` 给出处置。
- **唤醒回合**：代理必须用 `post_reply` 显式指定回复哪条消息。唤醒回合里没有经过 `post_reply` 的文本，若本轮只由一个锚点的事件触发，就挂到该锚点；否则作为不挂靠的备注显示。
- **卡片与结论标记由 Runner 生成，代理不能伪造。** 代理只给 `sourceSessionIds`，Runner 按这些任务的当前投影自动附上：每条已结束的任务附验证结论标记（如「已验证 3/3」「部分验证 2/3」）；签收策略判定需要确认的附「需要你确认」卡；有待处理请求的附需要你卡。代理无法给一条没过线的任务贴「已验证」。
- **证据引用按需展开。** `evidenceRefs` 只在用户追问细节时由代理附上，ReplyComposer 逐条经 EvidenceIndex 解析，解析不到的丢弃并记告警，渲染为可打开的证据芯片（测试输出、截图、diff、验证报告）。

### 2.6 处置：每条用户消息的下文

```ts
type MessageDisposition =
  | { kind: 'answered'; replyMessageIds: string[] }
  | { kind: 'spawned'; sessionIds: string[] }                  // 开任务（含并行）
  | { kind: 'queued'; sessionId: string; dependsOn: string[] } // 开任务但挂依赖
  | { kind: 'amended'; sessionId: string }                     // 并入在跑的任务
  | { kind: 'superseded'; oldSessionId: string; newSessionId: string; reason: string }
  | { kind: 'stopped'; sessionIds: string[]; reason: string };
```

- 处置是**投影**，不单独存：由带 `anchorMessageId` 的调度 Tool Call 证据 + 回复的 `replyTo` + 任务状态计算，函数放在 protocol（`projectMessageDispositions`）。一条消息可以有多个处置（同时并入一条、并行开一条）。
- 不变量：用户回合结束后，本轮每条用户消息至少有一个处置。用户回合的最终文本自动构成 `answered`，所以结构上总能满足；测试要覆盖多条消息合并的回合。
- **引用插话限定范围**：用户消息带引用（引用某条用户消息或某条代理回复）时，引用解析出一组相关任务（锚定在被引用消息上的任务，或被引用回复的 `sourceSessionIds`）。这条消息上的 `message_session` / `cancel_session` / `supersedes` 只能作用于这组任务，调度 Provider 在执行层校验，越界返回 `out_of_scope`。

### 2.7 验证结论与签收策略

用户不再逐条验收。验证由代理负责，结论由运行时计算，签收由策略决定，细节按需披露。

```ts
interface VerificationVerdict {
  sessionId: string;
  planId: string;
  outcome: 'passed' | 'partial' | 'failed';
  gate: { passed: boolean; unmet: { kind: string; reason: string; criterionId?: string }[] }; // evaluateVerificationGate
  criteria: { total: number; passed: number; manualPending: number };
  independentVerifier: 'passed' | 'failed' | 'not_required' | 'missing';  // runner.verifierRuns
  visual: 'passed' | 'failed' | 'not_required' | 'missing';               // UI 交付闸门
  qualityReview: 'passed' | 'failed' | 'not_required' | 'missing';
  unverified: string[];        // 没有被自动验证覆盖的点，必须告诉用户
  reportRef?: string;          // 已有的自动验收报告（goal-reports/<planId>.md）
  computedAt: string;
}

interface AcceptanceDecision {
  mode: 'auto' | 'confirm';
  reasons: AcceptanceReason[];  // confirm 时列出原因，auto 时为空
}

type AcceptanceReason =
  | 'verdict_not_passed' | 'manual_criteria_pending' | 'external_side_effects'
  | 'destructive_operation' | 'out_of_scope_write' | 'project_requires_confirm'
  | 'user_requested_review' | 'verification_below_floor';
```

- `VerificationVerdict` 由纯函数 `computeVerificationVerdict(plan, evidenceIndex, hostAuthority)` 计算，输入全部是宿主解析的事实（沿用 `evaluateVerificationGate` 只认宿主状态的约束），不接受模型参数。
- `AcceptanceDecision` 由纯函数 `decideAcceptance(verdict, sideEffectProfile, projectPrefs, userSignals)` 计算。`sideEffectProfile` 来自任务的 Evidence（写了哪些路径、跑了什么命令、有没有外部网络变更、MCP 变更、浏览器提交、删除），不来自代理的描述。
- `auto` 的条件（全部满足）：结论 `passed`；没有待确认的人工标准；副作用只在工作区 / 任务分支 / worktree 内；没有外部副作用和破坏性操作；项目没有设置「每次都要我确认」；用户没有对这件事说过「给我看看再说」。其余一律 `confirm`。

**验证下限**（代理只能上调，不能下调）：

| 改动类型 | 下限 |
|---|---|
| 改了代码 | 至少一条可执行成功标准（test / command）+ 验证闸门 + 质量自检 |
| 改了界面 | 上一行 + 视觉验证（intake 时已按 UI 交付臂自动启用） |
| 多文件或跨模块改动 | 上一行 + 独立 Verifier |
| 只读调研 / 文档 | 验证闸门（叶子证据） |

**签收的提交时机**：

```text
任务 completed → 运行时算 VerificationVerdict + AcceptanceDecision
  → 事件 session_verified（带结论与决策）→ 唤醒代理
  → 代理本轮可以 verify_session 追加核验（签收暂缓，核验结束后重算）
  → 代理 post_reply 汇报这条任务：
       auto    → 运行时写 resultAcceptance { acceptedBy: 'policy', verdictRef }，任务结束
       confirm → 回复附「需要你确认」卡，任务停在 result_ready
```

代签与汇报绑定：代理没有向用户说明情况，就不会代签。代理不能在 `confirm` 时代签，也不能在 `auto` 时阻止代签以外的任何事（它可以追加核验推迟代签，但不能无限推迟：追加核验有次数上限）。

**合入与推送**：合入源头分支默认 `confirm`（回复里附「合入 develop」一键动作），项目设置 `autoHandoffOnPolicyAccept` 打开后随代签自动合入；推送远端永远走权限审查，不自动。

**重新打开**：用户说「不对」「这个有问题」时，代理开一条派生任务（Goal Thread，`parentPlanId` 指向原计划）修正；策略代签的记录保留并标注 `reopenedBy`，不改写历史。

**分层披露**：

| 层 | 什么时候 | 内容 | 数据 |
|---|---|---|---|
| 0 结论 | 默认 | 一两句：做成了什么、验证了什么、还有什么没验证 + 结论标记 | `keyFindings`、`VerificationVerdict` |
| 1 细节 | 用户问「怎么验证的」「改了哪些」 | 成功标准逐条及验证方式、改动文件、测试结果摘要 | `get_session_report`、`get_verification_detail` |
| 2 证据 | 用户要看证据 | 证据芯片：测试输出、截图、diff、验证报告 | `evidenceRefs` 经 EvidenceIndex 解析 |

结论为 `partial` / `failed` 时，第 0 层必须说出没验证或没通过的点；结论标记由运行时渲染，代理的文字与标记冲突时以标记为准。

---

## 3. 调度能力

新增 `LocalDelegationProvider`，放在 `apps/desktop/electron/main/runtime-gateway/local-delegation-provider.mjs`，参照 `local-goal-provider.mjs`。纯逻辑（校验、事件映射、深度限制）下沉到 `packages/runtime-node`，TUI 共用。

| 工具 | capabilityId（草案） | 作用 | 副作用与授权 |
|---|---|---|---|
| `spawn_session` | `local.delegation.spawn_session` | 开任务：锚定一条用户消息，建子 Conversation（首条 = 用户原话 + 任务说明 + 上下文快照），按参数结构化创建 GoalPlan；带 `supersedes` 时原子地取代旧任务 | 只创建会话与计划，不执行本地能力；按 `goal-create` 同类处理，self-grant，记 Evidence |
| `message_session` | `local.delegation.message_session` | 并入：给任务追加指令或纠偏，作为该任务里的一条用户侧消息，来源标为项目代理，带 `anchorMessageId` | 同上 |
| `cancel_session` | `local.delegation.cancel_session` | 停止：停 Runner，GoalPlan 进 `cancelled`，带 `anchorMessageId` 与原因 | 不删分支 / worktree；`result_ready` / `accepted` 的任务返回 `not_cancellable` |
| `post_reply` | `local.delegation.post_reply` | 在代理会话里发一条回复，指定 `replyTo`、`sourceSessionIds`、可选 `evidenceRefs`；结论标记与卡片由 Runner 按投影附上；汇报已验证任务时触发签收提交（§2.7） | 只写代理自己的会话；self-grant，记 Evidence |
| `verify_session` | `local.delegation.verify_session` | 追加核验：派独立 Verifier（只读）、要求任务补跑检查（经 `message_session`）、或要求视觉复核；核验期间暂缓签收 | 不直接执行能力；次数有上限 |
| `get_verification_detail` | `local.delegation.get_verification_detail` | 取一条任务的验证细节：标准逐条、验证方式、证据引用摘要、未验证项 | 只读 |
| `create_objective` / `update_objective` / `pause_objective` / `close_objective` / `list_objectives` / `get_objective` | `local.delegation.objective.*` | 项目目标与 watches（ADR 82） | 必须锚定用户消息；代理提议的目标走确认卡；`autonomy` 只能由用户消息上调 |
| `set_proactivity` | `local.delegation.set_proactivity` | 改主动性档位与免打扰时段（ADR 80 决策 9） | 必须锚定用户消息；不影响必达项 |
| `set_model_policy` | `local.delegation.set_model_policy` | 改档位映射、角色设置、项目模型范围（ADR 83） | 必须锚定用户消息；设置页可见可撤；范围只能在项目层收紧 |
| `list_sessions` | `local.delegation.list_sessions` | 列出本项目任务与投影状态 | 只读 |
| `get_session_report` | `local.delegation.get_session_report` | 取一条任务的 `SessionReport` | 只读 |
| `spawn_subagent` | `local.delegation.spawn_subagent` | 开只读临时调研子 agent，复用 Explorer 执行路径，结果作为 Tool Result 返回 | 只读 profile；预算受 §5 约束 |

`spawn_session` 输入：

```ts
{
  anchorMessageId: string;       // 必填：这条任务回应哪条用户消息
  title: string;
  goal: string;                  // 代理写的任务说明；用户原话由 Supervisor 从锚点逐字带上
  successCriteria: string[];     // 可为空，但产品上要求代理尽量给出
  boundaries?: string[];
  requiresApproval: boolean;     // true → 计划先进用户批准卡
  isolation?: 'auto' | 'none' | 'worktree'; // auto：已有其他写仓库任务在跑时用 worktree
  contextRefs?: string[];        // 代理已读过的文件 / 调研报告引用，交给任务作为事实上下文
  dependsOn?: string[];          // 上游任务 sessionId；满足前保持 queued
  dependsOnPolicy?: 'accepted' | 'result_ready'; // 默认 accepted
  supersedes?: string;           // 取代的旧任务
  inherit?: { report: boolean; branch: 'auto' | 'yes' | 'no' }; // 取代时继承什么；branch auto = 旧任务改动与新目标仍相关时继承
  modelPreference?: { role: 'worker' | 'verifier' | 'explorer'; model: string }[]; // 用户本次指定（ADR 83），须过能力与范围过滤
  modelChoiceReason?: string;    // 角色为「自动」时代理的选择理由
  verification?: {               // 代理声明的验证要求；低于下限时按下限执行（§2.7）
    independentVerifier?: boolean;
    visual?: boolean;
    extraChecks?: string[];      // 额外的可执行检查，会并入成功标准
    requireUserConfirm?: boolean; // 代理判断这件事应当让用户过目
  };
}
```

取代语义（`supersedes`）：

1. **原子**：先建新任务，成功后再停旧任务；新任务建失败，旧任务不受影响。
2. **旧任务可恢复**：旧任务的 GoalPlan 进 `paused`，记 `supersededBy`，分支与 worktree 保留。用户点「恢复原任务」即恢复这份计划，新任务不受影响（要不要停新任务由用户或代理另行决定）。新任务被验收、或用户在旧任务上点「不要了」时，旧任务才转 `cancelled`。
3. **继承**：`inherit.report` 把旧任务的 `SessionReport`（含 `keyFindings`）作为新任务的事实上下文；`inherit.branch` 为 `yes` 时新任务从旧任务分支继续，`no` 时从源头重新拉。
4. **不能取代等确认或已签收的任务**：返回 `not_cancellable`。结果已经出来的东西由用户确认或说「不对」，代理只能另开。

`message_session` 输入：`{ sessionId, anchorMessageId, text }`。`cancel_session` 输入：`{ sessionId, anchorMessageId, reason }`。`post_reply` 输入：`{ replyTo: string[], body: string, sourceSessionIds: string[] }`。

用户提问复用现有 `request_user_input`（`local.interaction.request_user_input`），不新增 `ask_user`。

---

## 4. `project_agent` 模式投影

按 ADR 35 的机制新增 `project_agent` 模式，与 `explorer` 一样是**严格白名单**：只有显式声明 `availableInModes` 含 `project_agent` 的工具才会投影。

白名单：

- 只读：`list_files`、`read_file`、`search_files`、`goal_get_plan`
- 调度：§3 全部
- 交互：`request_user_input`
- 记忆（ADR 81）：`memory_search`、`memory_remember`、`memory_forget`、`memory_explain`（任务侧只投影 `memory_search`）
- 不投影 `web_fetch` 与外网搜索（P0-2 关闭）。`batch_search` 是本机文件检索，在白名单内。需要上网的事开任务。

明确不投影：`edit_file`、`write_file`、`bash`、`goal_create_plan`、`goal_update_task`、`request_explorer`、有副作用的 MCP / 浏览器 / 桌面控制 / Automation 提案。

执行层兜底：`permission-gate` 对 `project_agent` 模式下的任何写类 `permissionPolicy.kind` 直接拒绝并记 Evidence，防止投影配置漂移。

---

## 5. `ProjectAgentRunner`

落点：`packages/runtime-node/src/project-agent-runner.mjs`，Desktop 与 TUI 共用。它对项目代理的作用，相当于 Goal Runner 对单个 GoalPlan 的作用。

### 5.1 收件箱与唤醒

```text
任务侧事实变化（GoalPlan store 变更 / 权限队列变化 / Runner 终态）
  → DelegationEventMapper 映射成 DelegationEvent
  → 写入该项目代理的收件箱（持久化，重启可恢复）
  → ProjectAgentRunner 判断是否唤醒
      · 用户正在和代理对话、代理回合进行中 → 只入箱，本轮结束后再处理
      · 空闲 → 合并去抖窗口内的事件，唤醒代理跑一轮
  → 代理本轮看到收件箱快照（§7 roster source），决定：
      汇报用户 / 继续调度 / 向用户提问 / 什么都不说
```

唤醒规则：

| 事件 | 是否唤醒 | 说明 |
|---|---|---|
| `session_needs_user` | 立即 | 代理把卡片递给用户，可附带自己的判断 |
| `session_verified` | 立即 | 代理决定是否追加核验，然后汇报结论；`auto` 时汇报即代签，`confirm` 时附「需要你确认」卡 |
| `session_ended`（failed / cancelled） | 立即 | 代理决定重试、换方案或告诉用户 |
| `session_progress` | 不单独唤醒 | 只更新 roster 快照；长时间无进展由 §5.3 处理 |
| `user_intervened` | 不唤醒 | 下次代理回合时作为事实可见 |
| `objective_signal`（ADR 82，`changed = true`） | 按 severity：`urgent` 立即；`notable` 合并去抖；`info` 不单独唤醒，攒到下一次唤醒或每日小结 | 代理按目标的 `autonomy` 决定汇报、提议或开任务 |
| `digest_due`（每日小结时间到） | 立即 | 代理把 `digest` 项整理成一条「今日小结」 |

代理被唤醒的回合不伪造用户消息：触发内容作为 runtime reminder + roster 快照注入，写入代理对话的是代理自己的助手消息与卡片。

### 5.1.1 送达：SurfacingPolicy（ADR 80 决策 9）

唤醒代理和打扰用户是两件事：代理可以醒来处理事件、更新目标与记忆，却不一定要告诉用户。代理每次 `post_reply` 前，ReplyComposer 调纯函数：

```ts
type Surfacing = 'interrupt' | 'message' | 'digest' | 'silent';

function decideSurfacing(input: {
  origin: 'user_request' | 'objective_signal' | 'agent_idea';
  kind: 'needs_user' | 'confirm' | 'failure_needs_decision' | 'result' | 'observation' | 'idea' | 'objective_risk';
  novelty: boolean;                 // 与上次送达给用户的同类内容摘要比较
  severity: 'info' | 'notable' | 'urgent';
  proactivity: 'off' | 'low' | 'normal' | 'high';
  quietHours: boolean;              // 当前是否在免打扰时段
}): Surfacing;
```

规则（自上而下）：

| 条件 | 送达 |
|---|---|
| `needs_user` / `confirm` / `failure_needs_decision` / `objective_risk` | `interrupt`；免打扰时段内降为 `message`，但 `objective_risk` 且临近截止仍 `interrupt` |
| 用户发起的任务结果（`origin = user_request`） | 至少 `message`；档位 `normal` / `high` 时 `interrupt` |
| 代理发起的内容且 `novelty = false` | `silent` |
| 代理发起的 `urgent` | `interrupt` |
| 代理发起的 `notable` | `off` → `digest`；`low` → `digest`；`normal` → `message`；`high` → `interrupt` |
| 代理发起的 `info` / `idea` | `off` → `silent`；`low` → `digest`；`normal` → `digest`；`high` → `message` |

- 代理可以在 `post_reply` 里给出自己判断的 `severity`，但只能在确定性规则给出的下限之上上调，不能下调。
- `digest` 项不写进对话，存入收件箱的小结队列，`digest_due` 时由代理合并成一条消息；`silent` 项只更新右栏与记忆。
- 档位与免打扰时段是用户设置（项目级，可继承用户级默认），代理只能通过锚定用户消息的 `set_proactivity` 修改。

### 5.2 并发与预算

- 每个项目并发运行的任务上限默认 3，可配置，硬上限 6。
- 两条以上会写仓库的任务同时运行时，后开的任务强制 `isolation: 'worktree'`（复用改造阶段 D 的隔离路径）；主工作区脏时拒绝开出并返回结构化原因。
- 代理自发唤醒（非用户触发）有频率上限，防止事件风暴烧 token。
- 项目代理的 `spawn_subagent` 共享 Explorer 的并发配额与预算。

### 5.3 停滞检测

任务在 `running` 下超过阈值没有新的叶子 Evidence 或状态变化，Runner 产生一条合成的停滞事件唤醒代理。代理可以 `message_session` 纠偏或告诉用户。复用现有 `blockerAudit` 指纹，不另起一套。

### 5.4 取消与恢复

- 用户取消项目代理的当前回合，不影响任务继续运行。
- 应用重启：收件箱持久化；任务由现有 Goal Runner 恢复逻辑（ADR 73 中断 ≠ 失败）接管；项目代理在下次空闲时处理积压事件。

---

## 6. 权限冒泡

```text
任务内 Tool Call 需要授权
  → 现有 permission-review 产生待处理请求（真源在 main）
  → 任务对话照常出现权限卡
  → DelegationEventMapper 产生 session_needs_user（pendingRequestId 指向同一请求）
  → 项目代理对话渲染同一请求的卡片
  → 用户在任一处批准 / 拒绝 → 同一请求被解决 → 两处卡片同步收起
```

规则：

1. 项目代理不能批准、拒绝或改写任何权限请求。调度工具没有这类参数。
2. 任务的授权上限不超过用户对该项目已授予的范围；`spawn_session` 不接受任何扩大权限的参数。
3. 计划批准（`requiresApproval: true`）走同一路径，`kind: 'plan_approval'`，批准对象是任务的 GoalPlan。
4. 远程 / 手机入口批准时同样解决同一请求，不另开通道。

---

## 7. Evidence

- 每次调度 Tool Call 产出 Evidence：谁（项目代理对话）、何时、开了 / 改了 / 取消了哪条任务、带了什么意图。
- `SessionReport.evidenceRefs` 必须可解析；不可解析的引用在报告里标 `unresolved`，代理与界面都不能把它当证据。
- 项目代理的助手消息不是证据。结论标记只读 `VerificationVerdict`，签收只看关闭闸门 + 结论 + 签收策略。
- 临时子 agent 的报告沿用 Explorer 的 `allowedEvidenceRefs` 校验。

---

## 8. System Context

| 来源 | 层 | 内容 | 注入条件 |
|---|---|---|---|
| `project-agent-source` | `L1_AGENT` | 角色契约：只读 + 调度；什么时候直接回答、什么时候开任务；不替用户做判断；汇报必须引用任务报告 | `mode === 'project_agent'` |
| `project-roster-source` | `L7_CONTINUITY` | 本项目任务快照：标题、投影状态、需要你项、最近报告摘要、收件箱积压 | 同上；只注入快照，不注入任务全文 |
| `project-memory-source` | `L7_CONTINUITY` | 项目简报 + 用户偏好 + 按本轮检索到的记忆与事件卡，每条带来源标签（ADR 81） | 项目代理每轮；任务按冻结的 `memorySnapshotId`；只在事实层，不升为指令 |
| 现有 `project-instructions-source` | `L3_INSTRUCTIONS` | 项目 AGENTS.md 等 | 不变 |

任务侧：`spawn_session` 的 `goal` / `boundaries` 作为该任务首条用户意图与 GoalPlan 字段进入，不作为系统指令；`contextRefs` 作为附件类事实上下文。

项目代理对话常驻，压缩必须可用：复用现有 compaction 管线，roster 快照每轮重新生成，不进压缩摘要。

---

## 9. 存储

| 数据 | 落点 | 说明 |
|---|---|---|
| 项目代理 Conversation | conversation-store，`role: 'project_agent'` | 每个 Workspace 最多一条；懒创建 |
| 项目代理 id | Workspace 设置 `projectAgentConversationId` | 找不到时重建，不猜 |
| 任务 Conversation | conversation-store，`role: 'work_session'` + `parentConversationId` | 复用划词子会话已有的父子字段形态 |
| 收件箱 | `~/.peer-agent` 下按项目的 JSONL | 只存事件引用，不复制报告正文 |
| GoalPlan / Evidence | 不变 | |

`role` 缺省视为历史会话：迁移时不改写，界面归为该项目的「历史任务」。

---

## 10. IPC 与 Renderer 投影

- 新增 `delegation:list` / `delegation:changed`，payload 是 `WorkSession[]`，由 main 聚合；renderer 不自行扫描 GoalPlan 判断状态。
- `taskOverview` 聚合增加按项目分组与 `projectAgentConversationId`，用于侧栏角标。
- 卡片（需要你 / 需要你确认）与结论标记绑定 `sessionId` 与 `pendingRequestId`，交互调用已有的批准 / 验收 IPC，不新增绕过 main 的动作。

---

## 11. 与现有模块的关系

| 现有模块 | 用法 |
|---|---|
| `runtime-node` `createGoalRunner` | 原样作为任务的执行引擎 |
| Explorer / Verifier（`main.mjs` `explorerRunner` / `verifierRunner`） | 原样留在任务内；`spawn_subagent` 复用 Explorer 执行路径 |
| `local-goal-provider` | 任务内不变；`spawn_session` 通过 intake 路径创建 GoalPlan，不在调度 Provider 里复制计划逻辑 |
| `permission-review` | 真源不变，只新增事件映射 |
| conversation-store 划词子会话 | 父子字段形态复用 |
| 阶段 D worktree 隔离 | 并行写仓库任务复用 |
| `task-overview-aggregator` | 增加项目维度 |
| `remote-access` | 远程入口对接项目代理对话 |

`main.mjs` 已超过四千行，项目代理的组合逻辑放在独立的 `project-agent-application-service.mjs`，`main.mjs` 只做装配。

---

## 12. 测试清单

- `project_agent` 模式只投影白名单工具；写类工具不可见；执行层兜底拒绝写类调用。
- `work_session` 调 `spawn_session` 返回 `depth_limit`；临时子 agent 看不到调度工具。
- `spawn_session` 创建子 Conversation、父子关系、GoalPlan；`requiresApproval` 时进入 `awaiting_approval`。
- 并行写仓库任务第二条起强制 worktree；主工作区脏时拒绝。
- 任务权限请求产生 `session_needs_user`，两处批准解决同一请求。
- 代理没有任何批准权限的入口。
- `session_verified` 唤醒代理；代理文本不影响结论与 `resultAcceptance`。
- 收件箱持久化，重启后积压事件被处理且不重复汇报。
- 停滞检测产生唤醒；唤醒频率上限生效。
- 用户直接在任务里发消息产生 `user_intervened`，任务 Goal 生命周期不受代理干扰。
- 历史会话（无 `role`）迁移后可见且不被改写。
- `spawn_session` 缺 `anchorMessageId` 被拒；任务首条消息逐字包含锚点原话；上下文快照由 main 捕获，覆盖到锚点为止。
- 用户回合结束后每条用户消息至少一个处置；多条消息合并的回合同样成立。
- 引用插话时对范围外任务的 `message_session` / `cancel_session` / `supersedes` 返回 `out_of_scope`。
- 取代是原子的：新任务建失败时旧任务不变；旧任务进 `paused` 可恢复；`result_ready` / `accepted` 不可取代、不可停止。
- 代理无法给没过线的任务贴「已验证」：结论标记与卡片只由 Runner 按投影生成。
- 唤醒回合中没有 `post_reply` 的文本按规则挂靠或作为备注，不会误挂到无关消息。
- `VerificationVerdict` 只由宿主事实计算；模型参数无法影响结论。
- `decideAcceptance`：逐条覆盖 confirm 原因；副作用画像来自 Evidence 而不是代理描述。
- 代签只在 `auto` 且代理已 `post_reply` 汇报后发生；写入 `acceptedBy: 'policy'` 前必过关闭闸门，且不接受 `userOverride`。
- `verify_session` 暂缓签收，核验结束后重算结论与决策；超过次数上限返回错误。
- 代理无法下调验证下限：`spawn_session` 的验证声明低于下限时按下限执行。
- 结论为 `partial` / `failed` 时，回复的结论标记如实显示；`evidenceRefs` 中解析不到的引用被丢弃。
- 用户「不对」后派生任务挂 `parentPlanId`，原代签记录保留并标 `reopenedBy`。

---

## 13. 未决问题

已于 2026-09-26（P0-2）关闭，结论写在 ADR 80 的评审结论里：

1. 不投影外网读取。
2. 模型按 ADR 83：代理默认快档，任务默认强档。
3. 只读工具不够时直接开任务，不先请示。
4. 已绑定机器人的目录里，TUI 默认打开该机器人；`peer --classic` 保留直接任务。

## 14. Beta 1–3 桌面集成修复契约（2026-09-30）

范围是补齐 ADR 80、81、83、84、85 已接受的装配与交互。对应代码修复分支 `PeerAgent/pa/beta123-integration-repair`；不扩展 Beta4 的并行、隔离与目标能力。

- 桌面装配提供一个可重装、调用时读取的调度端口给统一 Local Tool Host，包含 SessionSupervisor 和已登记的幂等账本目录。宿主退出时释放端口和定时器。Provider 仍通过 Manifest、Projection、PermissionGrant 和 Evidence 执行；Renderer 不调用监督者。
- 项目代理及任务角色模型均通过现有聊天服务的 ModelRouter 解析，读取实时模型配置与机器人 `modelPolicy`。开任务时冻结任务角色选择；非 UI 任务在视觉模型不可用时可不设可选的 visualVerifier，UI 任务仍必须通过视觉能力筛选，不用空 catalog，也不在主进程复制路由逻辑。
- 回合上下文袋包含任务名册和唤醒事件，注册的 `project-roster` Source 把它们放入 L7。历史对话使用会话事实投影，内部 agent 过程不作为可见回复或系统指令。每次回合有跨重启唯一 id。
- 本次用户输入的稳定消息 id 与限长原文摘要作为 `inputAnchors` 事实进入同一个 L7 Source；任务名册保留其 `origin.anchorMessageId`。id 由宿主从已入队的 inputId 派生，模型不能生成或覆盖。摘要中和伪工具语法，不成为行为指令；调度执行仍对持久化父对话校验归属和用户消息类型。没有这些索引时不得通过猜测 id 绕过锚点校验。
- 后台巡检在持有租约时消费持久输入队列，包括启动租约取得前与离线期间提交的输入；写入对话后推进游标，再入代理回合。同一巡检还恢复持久收件箱中未确认的旧事件，即使本轮没有新事件也尝试既有 Runner 的 kick；空收件箱不产生模型回合，成功回合后才推进收件箱游标。复用同一队列、去重与单线程 Runner，不新增执行入口。
- `spawn_session.successCriteria` 接受既有 GoalSuccessCriterion 的结构化形态（command / test / file-contains / file-exists / manual）和旧字符串。字符串仍归一为 manual，仍要求用户确认；不因为项目策略 auto 而绕过 DoD 闸门。结构化标准由既有 Goal 工具、权限和 Evidence 路径核验，非法或不完整字段在调度前拒绝。任务结果的独立复核和签收闸门保持原约束。
- Goal Runner 的 L7 事实保留成功标准的稳定 id 和检查参数（command / path / expect）；过长参数省略并提示经既有 `goal_get_plan` 回查，不用截断后的值代替完整标准。`goal_get_plan` 的只读 Tool Result 保留白名单标准字段与既有 CriterionResult，供压缩后恢复；不回写计划，不替模型执行检查，也不扩大权限或替代证据闸门。
- 只有成功的 `post_reply` Tool Result 可以生成回复。正式 ReplyComposer 返回已校验的结构化消息，收尾使用该消息，不重新采信模型参数；失败、拒绝与取消不得伪装成成功空回复。取消复用聊天服务已有的 stream abort 入口，不增加 `sendMessage` 的参数。
- 熟悉项目通过监督者创建只读 research 任务；空项目回答写为固定 stated 职责记忆，README 同意才开文档任务。系统生命周期触发先保存可回查的锚定消息，任务能力沿用统一权限链，确认过的事实只能带来源写入 verified 记忆。
- 可见回复持久化后才按策略签收被引用的已完成任务。确认卡、重试卡、README 卡分别经 `project-agent:confirm-result`、`project-agent:retry`、`project-agent:accept-readme` IPC；宿主校验 workspace 归属、当前状态和重复点击。失效卡不能重新执行已完成操作。
- `accepted` 投影以持久化的 `resultAcceptance` 为准；核验结束解除 `verifying`。小结保留已校验的来源、结论与 Evidence 引用，实际送达后才触发签收。模型的任务列表仍限 50 条，宿主的项目事实集合不得沿用分页上限做来源归属判断。

### 14.1 核验格式与汇报状态一致性（2026-10-01）

- 报告只准入最终助手段中的一个完整结构化报告。格式错误最多重跑一次既有只读 Verifier；合法核验失败、权限拒绝、取消和提供方失败不属于格式恢复。恢复失败仍保持关闭闸门失败，不补造验证或签收事实。
- Explorer、文字 Verifier 及格式重试必须使用宿主持久化计划绑定的执行目录：有效 worktree delivery binding > targetWorkspacePath > 原任务会话 workspacePath > 既有宿主 workspaceRoot。沿用已存在的 sendMessage.workspacePath 参数传递，只读能力与授权不变；无会话核验不能因 conversationId 为 null 而继承另一个全局活跃项目。视觉复核沿用同一目录解析。
- `post_reply.sources` 非空时，`statusClaims` 必须逐项声明对应任务当前投影状态。宿主不一致时拒绝该回复，并返回实际状态供模型重新组织解释。`accepted` 声明必须已存在持久化签收，不能根据通过的 verifier 或 auto 策略预测。
- 宿主生成 `sessionStates` 快照，回复落盘后的策略签收完成或失败后再更新。Renderer 只表达事实；模型正文承载发现与解释，不承载签收真值。拒绝的 post_reply 不允许经 fallback 重新变成可见回复。
- 对话读取把状态投影刷新为本项目任务的当前状态，用户后续确认后不继续显示旧的待确认快照；读取不重写历史正文与持久化快照。
- 落地范围与验收见 `playbook/v0.1.0/beta3-verification-consistency.md`。这不是 Beta3 发布认证，也不开放 Beta4 能力。
- 档案增加可持久化的 `acceptancePolicy`（auto / confirm）、`planApproval`（never / writes / always）和既有 `modelPolicy`。更新经 `update-profile` 校验并保存；既有档案缺字段时读取默认值，不批量重写旧数据。模型覆盖只接受当前已配置的模型与允许角色。
- 验证必须覆盖正式注册入口到模型调用、Provider 到监督者、完成事件到 L7、回复拒绝、错误终态、重启 id 与三种卡片动作。模块单测通过不能替代真实项目、安装迁移与连续日用验收。

### 14.2 真实交付缺口补修（2026-10-01）

- 结构化自动验收的同一用户委托按宿主执行身份幂等：项目/父对话、用户锚点集合、kind/readOnly、验收操作参数、dependsOn/supersedes；标题/brief/criterion 描述与 id 不改变身份。没有自动标准时保持严格请求身份。不同目标参数、新用户锚点、显式替代保持不同；不通过模糊文本相似度合并。持久化旧计划可重建身份匹配，保留原记录不批改。
- 文件能力执行成功后，既有 EvidenceIndex 可追加 `bodyPreview: { kind: 'file', text: string, truncated: boolean }`，正文最多 4000 字符、复用既有秘密脱敏；披露最多 2000 字符并保留截断事实。来源是 Provider Tool Result，不是助手正文或 goal wrapper；读取展示执行时快照，不复读当前文件。旧无快照记录不得编造历史证据。
- completed 无独立 verdict 时也产生 result_ready 唤醒事实，完成事件以稳定 completedAt 标识幂等，不把完成事实当核验/签收事实。项目代理仍按现有工具核验并关联回复，宿主再过关闭闸门。
- 针对已完成但未交付任务的用户锚点，回复必须带对应 sources 与当前 statusClaims；漏来源拒绝并返回待引用 session 和宿主状态。正常纯问答与尚未完成任务的普通交流不受此规则影响。
- memory Provider 从已有主机 toolContext 读取 mode/turnRole/workspace/messages，和 flat context 保持相同身份准入。模型工具参数不决定角色；worker 仍不可写记忆。熟悉项目沉淀沿用关联回复、宿主核验与 Evidence 准入，不以 stated 或源外回复绕过。
- 范围及回归见 `playbook/v0.1.0/beta3-real-gaps.md`；沿用 ADR 80/81/85，无新的执行通道或存储目录，不开放 Beta4。
