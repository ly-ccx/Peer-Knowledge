# 项目代理能力分层与模块化建设

创建时间：2026-09-24
最后更新：2026-09-24

> 状态：Draft（随 ADR 80 评审）  
> 级别：A 级（执行宿主、调度、通讯、异常、结果追踪的模块边界）  
> 关联决策：`knowledge/decisions/80-project-agent-delegation-model.md`  
> 关联运行时契约：`knowledge/architecture/project-agent-delegation-runtime.md`（对象、工具、白名单；本文管模块怎么拆、怎么建）  
> 关联产品稿：`design/product/project-agent-workbench.md`  
> 关联决策：ADR 21（续传）、22（流重连）、25（用量账本）、26（循环终止）、30（Provider 恢复）、35（模式投影）、43（运行态分桶）、63（产物与证据）、73（中断 ≠ 失败）

---

## 0. 一句话

交互模式是锚定回复：每条用户消息被代理接住，要干活的就锚定这条消息开任务，任务交回的关键信息由代理整理后回复原消息，插话由代理自主决定并入、取代或另开（产品稿 §2.3、§3.5）。支撑它的模块，把「一个项目代理带多条任务、任务里再带临时子 agent」拆成七层：下层只提供能力，上层只做决策；命令向下走，事件向上走，查询只读投影；每一份状态只有一个真源。

```text
L7  表达层        Desktop 代理对话 / 右栏 / 卡片 · TUI · 远程 / 手机
                  ─────────────── 只读投影 + 已有 IPC 动作 ───────────────
L6  代理编排层    ProjectAgentRunner（单线程 actor）· LocalDelegationProvider · 代理上下文来源
L5  异常与恢复层  FailurePolicy · Watchdog · CircuitBreaker · 取消级联 · 重启恢复
L4  结果与签收层  SessionReportBuilder · VerificationVerdict · AcceptancePolicy · 签收提交 · WorkSession 投影 · DeliveryTimeline · 依赖闸门
L3  通讯层        DelegationEventMapper · ProjectInbox · SessionMessenger
L2  派发与调度层  SessionSupervisor · ExecutionScheduler · IsolationPlanner
L1  执行宿主层    AgentProfileRegistry · AgentTurnExecutor · TurnSink
L0  基座（已有）  能力链 · agent loop · Provider 协调与恢复 · conversation / goal-plan store · Evidence · 权限审查 · 压缩 · Goal Runner
```

---

## 1. 分层原则

1. **依赖只向下。** 上层通过下层的 Interface 调用，下层不知道上层存在。L3 不认识项目代理，L2 不认识卡片。
2. **命令向下，事件向上，查询旁路。**
   - 命令（开任务、发消息、取消）：带幂等键，最多生效一次。
   - 事件（任务状态变化、需要你、完成）：至少投递一次，接收方按事件 id 去重。
   - 查询（任务列表、报告）：只读 store 投影，不改状态。
3. **一份状态一个真源。**

| 状态 | 真源 | 其他地方只能 |
|---|---|---|
| 任务执行状态、成功标准、验收 | GoalPlan store | 投影 |
| 权限待处理请求 | permission-review（main） | 引用 `pendingRequestId` |
| 会话消息、父子关系、消息来源 | conversation-store | 投影 |
| 事件投递进度 | ProjectInbox 游标 | — |
| 调度队列、并发槽位 | ExecutionScheduler 内存态，可从 store 重建 | — |
| 证据 | EvidenceIndex | 引用 |

4. **包的落点。**

| 包 | 放什么 | 原因 |
|---|---|---|
| `packages/protocol` | 对象、事件、失败码、纯投影函数 | Desktop / TUI / 远程共用契约 |
| `packages/runtime-node` | L2–L6 的可移植实现 | TUI 共用同一套调度与编排，避免两套真相 |
| `apps/desktop/electron/main` | L1 的 Desktop 适配器、Provider 注册、IPC、application service | 宿主相关 |
| `apps/desktop/renderer` | L7 | 只做投影与交互 |

5. **`main.mjs` 不再长胖。** 组合逻辑进 `project-agent-application-service.mjs`，`main.mjs` 只装配。

---

## 2. 模块总览

| 层 | 模块 | 包 | 现状 |
|---|---|---|---|
| L1 | AgentProfileRegistry | runtime-node | 新建 |
| L1 | AgentTurnExecutor + TurnSink | runtime-node 接口 / desktop 适配器 | **改造**：收拢 `runGoalTurn`、`runExplorer`、`runVerifier` 的手工拼装 |
| L2 | SessionSupervisor | runtime-node | 新建 |
| L2 | ExecutionScheduler | runtime-node | 新建；接 Goal Runner 已预留但未接线的 `canRunPlan` |
| L2 | IsolationPlanner | runtime-node | 改造：包装已有 `prepareIsolation` / worktree adapter |
| L3 | DelegationEventMapper | runtime-node（纯函数） | 新建 |
| L3 | ProjectInbox | runtime-node | 新建 |
| L3 | SessionMessenger | runtime-node | 新建 |
| L3 | AnchorScopeResolver | runtime-node（纯函数） | 新建：引用插话 → 可作用的任务范围 |
| L2 | 带快照的子会话原语 | conversation-store | **改造**：从划词子会话（`SelectionOrigin` + `buildInheritedBackground`）抽出，任务与划词共用 |
| L4 | WorkSession 投影 | protocol（纯函数） | 新建 |
| L4 | 消息处置投影 `projectMessageDispositions` | protocol（纯函数） | 新建 |
| L6 | ReplyComposer（回复挂靠 + 卡片生成） | runtime-node | 新建 |
| 横向 | 记忆模块组：MemoryStore · MemoryAdmissionPolicy · MemoryCurator · EpisodeBuilder · MemoryRetriever · `project-memory-source` · MemoryMaintenance · LocalMemoryProvider | protocol / runtime-node / system-context / desktop | 新建，见 ADR 81 与 `project-agent-memory-system.md` §11 |
| L4 | SessionReportBuilder | runtime-node | 新建 |
| L4 | DeliveryTimeline | runtime-node（投影） | 新建 |
| L4 | VerificationVerdictBuilder | protocol / runtime-node（纯函数） | 新建：汇总已有验证事实，不做新验证 |
| L4 | AcceptancePolicy `decideAcceptance` | protocol（纯函数） | 新建 |
| L4 | 签收提交 | 已有 `goalPlansRevise` + `evaluateAcceptanceCloseGate` | 改造：`acceptedBy` 增加 `'policy'` |
| L5 | FailurePolicy / Watchdog / CircuitBreaker | runtime-node | 新建；复用 `blockerAudit`、ADR 30、ADR 73 |
| L6 | ProjectAgentRunner | runtime-node | 新建 |
| L6 | LocalDelegationProvider | desktop runtime-gateway | 新建 |
| L6 | `project-agent-source` / `project-roster-source` | system-context | 新建 |
| L7 | 代理对话、右栏、卡片、`delegation:*` IPC | renderer / main ipc | 新建 |

---

## 3. L1 执行宿主层

回答：**怎么跑一轮 agent**，不管这轮是谁的。

### 3.1 现状问题

- `runGoalTurn` 必须拿到渲染窗口的 `webContents`，否则直接返回 `blocked: 'No renderer window is available for Goal Runner'`。窗口关掉，后台任务就停。
- Explorer / Verifier 各自用 `createCollectingWebContents()` 伪造一个 `webContents`，再各自拼 `sendMessage` 参数。
- 项目代理、任务、调研子 agent 再各拼一遍，就是第四、五、六套。

### 3.2 AgentProfileRegistry

每种角色一份静态画像，调用方只说角色，不再手拼参数。

```ts
interface AgentProfile {
  role: 'project_agent' | 'session_worker' | 'explorer' | 'verifier' | 'visual_verifier' | 'research_subagent';
  mode: 'project_agent' | 'goal' | 'explorer' | 'verifier';   // 决定工具投影（ADR 35）
  persistTranscript: boolean;       // false = ephemeral，不写会话正文
  defaultModelBinding: 'conversation' | 'role_default';
  budget: { maxToolCallsPerTurn?: number; maxDurationMs?: number };
  canSpawn: 'sessions_and_subagents' | 'subagents' | 'none';     // 深度限制的静态来源
}
```

### 3.3 AgentTurnExecutor

```ts
interface AgentTurnExecutor {
  runTurn(input: {
    profile: AgentProfile['role'];
    conversationId: string | null;  // ephemeral 时为 null
    messages: ProviderMessage[];
    contextInputs: SystemContextInputs; // explorerContext / roster / reminders…
    sink: TurnSink;
    signal: AbortSignal;
    priority: TurnPriority;         // 交给 L2 调度器取槽位
  }): Promise<TurnOutcome>;
}

type TurnOutcome =
  | { kind: 'done'; toolCallCount: number; text: string }
  | { kind: 'waiting_user'; reason: string }
  | { kind: 'aborted'; by: 'user' | 'preempted' | 'cascade' }
  | { kind: 'failed'; failure: DelegationFailure }; // 已分类，见 L5
```

`TurnSink` 两个适配器：

- `BroadcastSink`：可见会话的流事件按 `streamId` 广播给所有窗口，由 renderer 的流路由器落桶（ADR 43）。没有窗口也照跑；窗口打开时按 ADR 22 重连认领。
- `CollectingSink`：ephemeral 子 agent 收集文本与事件，结束后交给报告解析。

不变量：

1. 执行宿主不决定任务状态，只返回已分类的 `TurnOutcome`。
2. 后台回合不依赖任何渲染窗口。
3. 每一轮先向 L2 取槽位再调用 Provider，结束（含异常）必须归还。

---

## 4. L2 派发与调度层

回答：**开什么、什么时候跑、在哪跑**。

### 4.1 SessionSupervisor（派发）

```ts
interface SessionSupervisor {
  spawn(req: SpawnSessionRequest, caller: { conversationId: string; toolCallId: string }):
    Result<WorkSession, 'depth_limit' | 'quota_exceeded' | 'isolation_conflict' | 'invalid_request' | 'breaker_open'>;
  message(sessionId: string, msg: { text: string; origin: MessageOrigin; idempotencyKey: string }): Result<void, …>;
  cancel(sessionId: string, reason: CancelReason): Result<void, …>;
  get(sessionId: string): WorkSession | null;
  list(projectAgentConversationId: string): WorkSession[];
  lineage(conversationId: string): { role: ConversationRole | null; parentId: string | null; depth: number };
}
```

`spawn` 的实现步骤：

1. **校验调用方**：`lineage(caller).role === 'project_agent'`，否则 `depth_limit`。校验 `anchorMessageId` 是代理会话里的用户消息；引用插话时校验范围（§5.4）。
2. **幂等**：键为 `(caller.conversationId, toolCallId, hash(req))`，复用 `runtime-core` 的 `goal-idempotency` 账本。压缩续跑后模型重发同一个 `spawn_session`，返回已存在的任务，不开第二条。
3. **建会话**：用「带快照的子会话」原语：`role: 'work_session'`，`parentConversationId = caller`，main 捕获截至锚点的上下文快照；首条消息 = 锚点原话（逐字）+ 代理写的任务说明，`origin: project_agent`。有 `supersedes` 时附上旧任务报告，按 `inherit.branch` 决定分支来源。
4. **结构化建 GoalPlan**：用 `title / goal / successCriteria / boundaries` 直接创建计划；`requiresApproval` 决定 `workflowKind` 为 `plan_approval` 还是 `goal_self_driven`。不在任务里再跑一轮 intake，任务第一轮直接进入 Goal Runner 已有的 `orient → inspect → plan_scaffold`。
5. **隔离决策**：交给 IsolationPlanner。
6. **入队**：交给 ExecutionScheduler；有 `dependsOn` 时状态为 `queued`。
7. **取代收尾**：有 `supersedes` 时，新任务建成后才把旧任务 GoalPlan 置 `paused` + `supersededBy`（先建后停，保证原子）；旧任务是 `result_ready` / `accepted` 时第 1 步就拒绝。
8. **记证据**：调度 Tool Result（含 `anchorMessageId`）进 EvidenceIndex，它同时是消息处置投影的输入。

### 4.2 ExecutionScheduler（调度）

调度的粒度是**回合**，不是任务。长任务每一轮结束都归还槽位，下一轮重新排队，这样多条任务之间天然公平，用户的回合也不会被后台任务堵住。

槽位：

| 槽位 | 默认 | 说明 |
|---|---|---|
| 全局模型回合 | 4 | 同时在跑的 Provider 回合总数 |
| 每项目运行中任务 | 3（硬上限 6） | 超出的 spawn 进 `queued` |
| 每 Provider 并发 | 按 Provider 配置 | 429 由 ADR 30 恢复层退避，调度器同步降并发 |
| 子 agent 池 | 沿用 Explorer 5 / 8 | Explorer、Verifier、调研子 agent 共用 |

优先级：

| 级 | 回合 | 规则 |
|---|---|---|
| P0 | 用户直接触发的回合：代理的用户回合、用户介入后的任务回合 | 不排在任何后台回合后面；槽位满时可以借一个 |
| P1 | 代理的唤醒回合 | |
| P2 | 任务的 Runner 回合 | 同级按上次运行时间轮转 |
| P3 | 子 agent | |

依赖闸门：`spawn_session({ dependsOn: [sessionId], dependsOnPolicy: 'accepted' | 'result_ready' })`。依赖满足前任务保持 `queued`，不启动 Runner。依赖任务失败或被取消时，下游任务转 `blocked`，产生事件交给代理决定。

接线：Goal Runner 的 `canRunPlan(plan)` 钩子由调度器实现（依赖与每项目上限）；每一轮的槽位由 AgentTurnExecutor 获取和归还。

### 4.3 IsolationPlanner（在哪跑）

- `isolation: 'auto'`：本项目已有写仓库任务在跑，或依赖链上有未交回的分支，就用 worktree；否则共享主工作区。
- 主工作区脏且需要切分支：拒绝开出，返回 `isolation_conflict` 和原因，不自动 stash（沿用阶段 D 规则）。
- 包装已有的 `prepareIsolation` / `goalWorktreeAdapter`，不另写 git 逻辑。

---

## 5. L3 通讯层

回答：**消息和事件怎么在代理、任务、用户之间流动**。三条通道，方向固定：

```text
向下（命令）  代理 ──message_session──▶ 任务         SessionMessenger
向下（介入）  用户 ──直接发消息─────────▶ 任务         同一条会话、同一个 Runner
向上（事件）  任务 ──DelegationEvent───▶ 代理收件箱   EventMapper → ProjectInbox
```

任务永远不直接往代理的会话里写字；代理只通过自己的回合读取收件箱快照。

### 5.1 DelegationEventMapper

纯函数：`(previousFacts, currentFacts) → DelegationEvent[]`。输入是 GoalPlan 变更、权限待处理队列变化、Runner 终态。输出事件带确定性 id：`hash(sessionId, transition, factVersion)`，同一次状态跃迁重复映射也得到同一个 id。

### 5.2 ProjectInbox

- 每个项目一个只追加日志：`~/.peer-agent/delegation/<projectAgentConversationId>.jsonl`，每条带单调递增的 `seq`。
- **投递语义：至少一次 + 去重。** 写入前按事件 id 去重。
- **消费游标 `consumedSeq`**：代理回合开始时记录快照上界；回合成功结束才推进游标。回合失败或被抢占，事件下次还会出现。
- **已汇报标记**：代理对某事件递过卡片或写过汇报后，事件标记 `reported`，roster 快照里不再作为「新事件」出现，避免代理重复汇报。
- 只存事件与引用，不复制报告正文。

### 5.3 SessionMessenger

- `message_session` 在任务会话里写一条消息，来源 `origin: { kind: 'project_agent', conversationId, toolCallId }`。
- 用户介入写 `origin: { kind: 'user' }`，并产生 `user_intervened` 事件。
- 投递时机：任务 Runner 空闲或 `waiting_user` 时立即唤醒；正在跑时进入该任务的待消费队列，在下一轮开始时注入。
- 冲突规则：同一轮内用户消息与代理消息都待消费时，用户消息排在后面（离模型最近），并在 runtime reminder 里标明「用户指令优先于项目代理指令」。

消息来源字段：在会话消息元数据上新增 `origin`，不复用旧协议里给「硅基员工」用的 `sender` 字段。

### 5.4 AnchorScopeResolver（引用插话的路由）

纯函数：`resolveScope(quotedMessageId, facts) → sessionId[] | null`。

- 引用的是用户消息：范围 = 锚定在这条消息上的任务（含被取代链上的后继任务）。
- 引用的是代理回复：范围 = 这条回复的 `sourceSessionIds`。
- 没有引用：`null`，代理自行判断，不限范围。

范围在两处生效：写进本轮 roster 快照告诉代理「这条消息只关于这些任务」；调度 Provider 在执行层校验，越界的 `message_session` / `cancel_session` / `supersedes` 返回 `out_of_scope`。引用是用户给出的硬约束，不靠代理自觉。

### 5.5 卡片的存储

卡片是代理回复的一部分：`AgentReplyMeta.cards` 只存 `{ type, sessionId }`，渲染时读实时投影，所以卡片状态永远和真源一致（在任务里批准后，代理对话里的卡片同步收起）。卡片由 L6 的 ReplyComposer 按任务投影生成，代理不能自己指定卡片类型。

---

## 6. L4 结果与签收层

回答：**做到哪了、验证得怎么样、算不算完**。验证由代理负责（决定验证到什么程度、要不要追加核验），结论由运行时计算，签收由策略决定：低风险且验证通过时策略代签，其余请用户确认。

### 6.1 WorkSession 投影

protocol 里的纯函数 `projectWorkSession(plan, pendingRequests, lineage) → WorkSession`。状态枚举在运行时契约的基础上补一个 `queued`：

```text
queued → starting → awaiting_approval → running ⇄ needs_user → verifying ─┬─ auto ────→ accepted（策略代签）
                                            │                             └─ confirm → result_ready → accepted（用户确认）
                                            └──────────────→ failed / cancelled
```

与 `projectGoalPlan`（行动权投影）同层，两者对同一个 GoalPlan 给出一致结论，测试里互相校验。

### 6.2 SessionReportBuilder

`build(sessionId) → SessionReport`，数据来源：

| 字段 | 来源 |
|---|---|
| 状态、标准进度 | GoalPlan + 关闭闸门判定（`evaluateAcceptanceCloseGate` 的只读调用） |
| `evidenceRefs` | 计划持有引用，经 EvidenceIndex 解析；解析不到的标 `unresolved` |
| 产物 | UserArtifact（ADR 63），不从文本猜 |
| 分支与改动 | `deliveryBinding` + range diff 统计 |
| `summary` | Runner `synthesize` 阶段的输出，明确标注为叙述，不是证据 |
| `needsUser` | 权限待处理队列 / 计划批准状态 |

### 6.3 消息处置投影（按消息的结果跟踪）

`projectMessageDispositions(agentConversation, delegationEvidence, sessions) → Map<messageId, MessageDisposition[]>`，纯函数，放 protocol。

- 输入：带 `anchorMessageId` 的调度 Tool Call 证据、回复的 `replyTo`、任务当前状态。
- 输出驱动用户消息上的状态标记：处理中（锚定任务在跑）、需要你（锚定任务有待处理请求）、已回复、已并入「…」、已停掉「…」改开「…」。
- 取代链：旧任务 → 新任务 → 更新的任务，标记显示链尾的状态，点开可以看整条链。
- 不单独存储；想知道「这条消息后来怎么样了」永远现算。

### 6.4 DeliveryTimeline（按项目的结果跟踪）

按项目投影出每条任务的时间线：开出、首次运行、需要你（次数与等待时长）、机器完成、验收、交回、失败 / 取消。

- 数据来自 GoalPlan run events 与收件箱，不新建真源。
- 用途：右栏的已结束分组、代理回答「这周做了什么」、以后的项目记忆，以及诊断面板的吞吐与等待统计。

### 6.5 验证结论：VerificationVerdictBuilder

`computeVerificationVerdict(plan, evidenceIndex, hostAuthority) → VerificationVerdict`，纯函数，放 protocol / runtime-node。它不做新的验证，只把已有的验证事实汇成一个结论：

| 输入 | 已有来源 |
|---|---|
| 叶子任务证据、成功标准、UI 交付 | `evaluateVerificationGate`（只认宿主状态） |
| 独立复核 | `runner.verifierRuns` |
| 视觉验证 | UI 交付闸门 / visual verifier |
| 质量自检 | `plan.qualityReview` |
| 验证报告 | 计划完成时已自动生成的 `goal-reports/<planId>.md` |

输出 `passed / partial / failed`、覆盖统计和 `unverified` 清单（没有被自动验证覆盖、必须告诉用户的点）。

### 6.6 签收策略：AcceptancePolicy

`decideAcceptance(verdict, sideEffectProfile, projectPrefs, userSignals) → AcceptanceDecision`，纯函数，放 protocol。

- `sideEffectProfile` 由任务 Evidence 汇总：写入路径是否都在工作区 / 任务分支 / worktree 内，有没有外部网络变更、MCP 变更、浏览器提交、删除、越界写。
- `userSignals`：用户对这件事说过「给我看看再说」，或项目设置「每次都要我确认」。
- `auto` 需要全部满足：结论 `passed`、无待确认人工标准、副作用只在工作区内、无外部 / 破坏性副作用、无用户过目要求、验证不低于下限。其余为 `confirm` 并列出原因。
- 策略表是一个 Seam：以后按项目或按任务类型替换，不改调用方。

### 6.7 签收提交

- 唯一写入口仍是 `goalPlansRevise` 写 `resultAcceptance`，经过关闭闸门，不接受 `userOverride`。
- **策略代签**：`auto` 时由运行时在代理为这条任务 `post_reply` 之后写入 `{ acceptedBy: 'policy', verdictRef }`。代签与汇报绑定：代理没说明情况就不会代签；代理追加核验（`verify_session`）期间暂缓，结束后重算。
- **用户确认**：`confirm` 时代理回复附「需要你确认」卡，用户点确认走已有 IPC 写 `{ acceptedBy: 'user' }`。
- **合入源头分支**：默认随回复附一键「合入」动作；项目设置 `autoHandoffOnPolicyAccept` 打开后随代签自动合入。推送远端永远走权限审查。
- **重新打开**：用户说「不对」时代理开派生任务（`parentPlanId`），原签收记录保留并标 `reopenedBy`。
- 代理没有任何直接签收工具：白名单里没有，Provider 里也没有这个方法。代理能做的只是追加核验和汇报。

### 6.8 按需披露的数据面

| 层 | 数据来源 | 代理怎么取 |
|---|---|---|
| 0 结论 | `keyFindings` + `VerificationVerdict` | 唤醒时 roster 快照里已有 |
| 1 细节 | 标准逐条及验证方式、改动文件、测试摘要 | `get_session_report`、`get_verification_detail` |
| 2 证据 | 测试输出、截图、diff、验证报告 | `evidenceRefs` 经 EvidenceIndex 解析后由 ReplyComposer 渲染为证据芯片 |

---

## 7. L5 异常与恢复层

回答：**出错了谁发现、谁处理、谁拍板**。分工是：确定性策略先处理，处理不了交给代理判断，涉及权限、范围、预算时交给用户。

### 7.1 失败分类

| 类 | 例子 | 检测 | 默认处理 | 升级到 |
|---|---|---|---|---|
| `provider_transient` | 网络、5xx、429 | ADR 30 恢复层 | 同 Provider 重试 → 备用 Provider | 用尽后任务进 `interrupted`（ADR 73），事件给代理 |
| `tool_failure` | 命令失败、文件不存在 | Tool Result | 任务内模型自行处理 | 同一指纹重复 → `blockerAudit` → blocked → 代理 |
| `permission_denied` | 用户拒绝授权 | 权限审查 | 任务收到结构化拒绝 | 代理知情；代理不能替用户重新申请同一权限 |
| `verification_failed` | 标准不过、Verifier 打回 | Goal 验证闸门 | 任务内 repair 循环 | 超过修复上限 → blocked → 代理 |
| `budget_exhausted` | 回合数、token、时长用尽 | Runner 预算 | 任务停住 | 代理向用户递「追加预算」卡；代理不能自己加 |
| `stalled` | 长时间无新证据或状态变化 | Watchdog | 合成停滞事件 | 代理 `message_session` 纠偏或取消 |
| `host_interruption` | 退出、崩溃、重启 | 进程生命周期 | `interrupted`，启动后按已有上限自动续跑 | 超过续跑上限 → 代理 |
| `isolation_conflict` | 主工作区脏、worktree 创建失败 | IsolationPlanner | spawn 同步返回失败 | 代理告诉用户 |
| `dependency_failed` | 上游任务失败 / 取消 | 调度器 | 下游 `blocked` | 代理 |
| `agent_misuse` | 参数非法、越深度、超配额 | Supervisor | 同步 Tool Error 给代理 | — |
| `agent_turn_failure` | 代理自己的回合失败 | 执行宿主 | 游标不推进，退避重试；界面提示 | 连续失败 → 用户 |
| `systemic` | 窗口期内多条任务同一指纹失败 | CircuitBreaker | 熔断：本项目停止新开任务和自动重试 | 用户 |

失败码进 protocol（`DelegationFailure { code, fingerprint, retryable, detail }`），执行宿主返回的 `TurnOutcome.failed` 已经带分类，上层不再解析错误字符串。

### 7.2 FailurePolicy

纯函数：`(failure, history) → 'retry' | 'escalate_agent' | 'escalate_user' | 'terminal'`，重试带上限与退避。策略表可测试、可替换，是一个 Seam。

### 7.3 Watchdog

- 停滞：任务 `running` 超过阈值没有新的叶子证据或状态变化（复用 `blockerAudit` 指纹）。
- 心跳：在跑的回合超过 `maxDurationMs` 没有任何流事件，按超时中止，归还槽位。
- 孤儿：`work_session` 的父会话不存在，归到项目的历史任务并告警，不自动取消。

### 7.4 CircuitBreaker

按项目计数：窗口期内同一指纹失败 ≥ 3 条任务就熔断。熔断期间 `spawn` 返回 `breaker_open`，自动重试暂停，代理会话里出现一张卡片说明原因。用户确认后半开：先放行一条任务，成功再闭合。

### 7.5 取消级联

| 动作 | 影响 | 不影响 |
|---|---|---|
| 取消代理的当前回合 | 这一轮 | 所有任务 |
| `cancel_session` | 任务 Runner、任务内子 agent（AbortSignal）、GoalPlan → `cancelled`；下游依赖 → `blocked` | 分支与 worktree（删除仍要二次确认） |
| 取代（`supersedes`） | 新任务建成后，旧任务 Runner 停止、任务内子 agent 中止、GoalPlan → `paused` + `supersededBy`；新任务签收或用户放弃旧任务时才 → `cancelled` | 旧任务分支与 worktree；旧任务的下游依赖改挂到新任务前先转 `blocked` 交代理决定 |
| 用户暂停任务 | 该任务 → `paused` | 其他任务 |
| 关闭项目 / 切走工作区 | 无（ADR 27：切换不中断运行） | — |
| 退出应用 | 所有任务 → `interrupted` | 数据 |

### 7.6 重启恢复顺序

```text
1. 加载 store（conversation / goal-plan / inbox）
2. Goal Runner recoverContextCheckpoints + interrupted 续跑（已有）
3. ExecutionScheduler 从 store 重建队列：queued、依赖、每项目计数
4. ProjectInbox 从游标重放未消费事件
5. 有未汇报的唤醒类事件的项目代理排一次唤醒回合
6. 窗口打开后按 ADR 22 重连在跑的流
```

顺序本身要有集成测试：调度器必须在收件箱重放之前重建，否则代理会基于不完整的任务清单做决策。

---

## 8. L6 代理编排层

回答：**项目代理什么时候思考、看到什么、能做什么**。

### 8.1 并发模型：代理单线程，并发都在任务侧

「多线程异步处理」的具体含义：

| 并发单元 | 并发方式 | 为什么 |
|---|---|---|
| 项目代理 | **单线程 actor**：同一时刻最多一轮 | 两轮并行会在同一段对话上抢写、重复开任务 |
| 任务 | 多条并行，每条由 Goal Runner 的 pump 独立推进，受 L2 槽位约束 | 并行干活在这里 |
| 子 agent | 任务内并发池 | 沿用 Explorer |

这是 Node 单进程事件循环上的异步并发，不是操作系统线程。真正耗时的是 Provider 流与子进程，它们本来就是异步 IO。

### 8.2 ProjectAgentRunner 状态机

```text
            用户消息                      回合结束
  idle ─────────────────▶ user_turn ──────────────────▶ idle
   │                        ▲    │                       │
   │ 唤醒条件满足            │    │ 用户又发消息           │ 游标之后还有未汇报的唤醒类事件
   ▼                        │    └─▶ 进入消息队列          ▼
  wake_turn ──用户消息──────┘（抢占：安全点中止）      wake_turn
```

规则：

1. **用户消息抢占唤醒回合。** 代理没有副作用，已经提交的调度命令有幂等保护，所以唤醒回合可以在安全点（两次工具调用之间）中止，随即开始用户回合。已开出的任务会出现在新回合的 roster 快照里。
2. **用户回合不被抢占。** 用户回合中来的新消息进入已有的消息队列；新事件只入箱。
3. **回合后补处理。** 回合结束时，如果游标之后还有未汇报的唤醒类事件，立即排一次唤醒回合。
4. **合并与限频。** `needs_user` 立即唤醒；其余唤醒类事件合并去抖（默认 3 秒）；两次自发唤醒最短间隔默认 30 秒；每小时自发唤醒次数有上限，超过后只更新角标，不再唤醒。
5. **唤醒回合不伪造用户消息。** 触发内容作为 runtime reminder 和 roster 快照注入。
6. **排队的插话合并成一个用户回合。** 用户回合进行中又来了几条消息，下一个用户回合一次性看到它们，并且要给每一条都做处置（§8.3）。

### 8.3 插话处置（代理自主决定停、并、开）

用户回合里，代理对本轮每条用户消息做一次处置判断。输入是这条消息、它的引用范围（§5.4）、roster 快照里在跑的任务（每条带锚点原话摘要、状态、最近的 `keyFindings`）。

| 处置 | 调用 | 约束 |
|---|---|---|
| 回答 | 无调度调用，最终文本自动回复 | — |
| 开任务 / 并行 | `spawn_session({ anchorMessageId })` | 受并发上限 |
| 排队 | `spawn_session({ anchorMessageId, dependsOn })` | 依赖必须是本项目任务 |
| 并入 | `message_session({ sessionId, anchorMessageId })` | 在引用范围内；任务未终态 |
| 取代 | `spawn_session({ anchorMessageId, supersedes, inherit })` | 在引用范围内；旧任务不是 `result_ready` / `accepted`；原子 |
| 停止 | `cancel_session({ sessionId, anchorMessageId, reason })` | 同上 |

判断由代理（模型）做，这是用户要的自主性；约束由 Provider 在执行层强制，这是治理。判断倾向写进 `project-agent-source`：

- 目标没变、只是补充或纠偏 → 并入，不要为了干净重开。
- 目标变了且旧任务的继续执行会白费 → 取代，并在回复里说一句为什么。
- 拿不准是并入还是取代 → 并入，并在回复里说明「如果你是想换方向，告诉我我就重开」。
- 用户说停 → 停止，不追问。

每个处置都投影到用户消息的状态标记上（§6.3），取代附「恢复原任务」入口，所以误判的代价是一次点击。

### 8.4 ReplyComposer（整理回复）

- **挂靠**：用户回合的最终文本自动 `replyTo` 本轮用户消息；唤醒回合必须用 `post_reply` 指定回复对象，否则按「单一锚点触发就挂该锚点，否则作不挂靠备注」处理。
- **整理**：唤醒回合的 roster 快照给出触发任务的 `SessionReport.keyFindings`；角色契约要求先结论、再必要细节，不照抄任务日志，未解决的问题和风险要说出来。
- **来源、结论标记与卡片**：回复带 `sourceSessionIds`；ReplyComposer 按这些任务的当前投影附结论标记（已验证 / 部分验证 / 未通过）和卡片（需要你、需要你确认、失败），代理不能指定。代理文字与结论标记冲突时，以标记为准。
- **分层披露**：默认只给第 0 层（一两句结论 + 验证了什么 + 没验证什么）；用户追问才用 `get_session_report` / `get_verification_detail` 给第 1 层细节；用户要证据才附 `evidenceRefs` 给第 2 层证据芯片（§6.8）。结论为 `partial` / `failed` 时，第 0 层必须点出缺口。
- **汇报即签收提交点**：对 `auto` 任务的 `post_reply` 触发策略代签（§6.7）。
- **合并回复**：同一锚点下多条任务先后完成时，代理可以逐条回复，也可以等齐了回一次总的；ReplyComposer 不强制，但去重规则保证同一事件不会被回复两次（收件箱的 `reported` 标记）。

### 8.5 LocalDelegationProvider

L6 与 L2–L4 之间唯一的模型侧接口。每个工具方法只做参数校验和转发：

| 工具 | 转发到 |
|---|---|
| `spawn_session` | `SessionSupervisor.spawn` |
| `message_session` | `SessionSupervisor.message` → SessionMessenger |
| `cancel_session` | `SessionSupervisor.cancel` |
| `list_sessions` | `SessionSupervisor.list` |
| `get_session_report` | `SessionReportBuilder.build` |
| `spawn_subagent` | AgentTurnExecutor（`research_subagent` 画像，P3 优先级） |
| `post_reply` | ReplyComposer（`auto` 任务汇报后触发签收提交） |
| `verify_session` | 独立 Verifier（只读）/ SessionMessenger 要求补跑检查 / 视觉复核；暂缓签收 |
| `get_verification_detail` | VerificationVerdictBuilder + EvidenceIndex（只读） |

所有带 `anchorMessageId` 的调用先过 AnchorScopeResolver 的范围校验。Provider 里没有批准、直接签收、改结论、下调验证下限、改预算、指定卡片的方法，这是结构性约束，不靠 prompt。

### 8.6 代理看到什么

每一轮的上下文 = 代理会话历史（经压缩）+ `project-agent-source`（`L1_AGENT` 角色契约，含 §8.3 的处置倾向与 §8.4 的回复规矩）+ `project-roster-source`（`L7_CONTINUITY`：在跑任务及其锚点摘要、引用范围、游标之后的新事件与 `keyFindings`、熔断状态）+ `project-memory-source`（`L7_CONTINUITY`：项目简报、用户偏好、按本轮检索到的记忆与事件卡，带来源标签，ADR 81）+ 项目指令（`L3_INSTRUCTIONS`）。roster 与记忆每一轮重新生成，不进压缩摘要。

---

## 9. L7 表达层

- IPC：`delegation:list` / `delegation:changed`（`WorkSession[]`）、`delegation:timeline`（DeliveryTimeline）。批准、验收、取消、介入发消息都复用已有 IPC 或经 main 的 application service，renderer 不直接改任何状态。
- Renderer：代理对话按 ADR 43 按 `conversationId` 分桶；右栏订阅 `delegation:changed`；卡片按引用读投影。
- TUI 与远程入口消费同一批投影与命令，不另开通道。

---

## 10. 横切：预算、观测、证据

- **预算**：任务级（回合数、token、时长）由 Runner 执行；项目级日 token 预算由调度器在取槽位时检查，按父子关系汇总 ADR 25 的用量账本。超预算产生 `budget_exhausted`，由用户决定是否追加。
- **观测**：诊断面板展示调度队列、槽位占用、熔断状态、收件箱积压、唤醒频率。审计 = 收件箱 + 调度 Tool Result 的证据 + 任务 run events。
- **证据**：调度命令、任务报告引用、子 agent 报告引用都走 EvidenceIndex；叙述性摘要一律不算证据。

---

## 11. 端到端时序

### 11.1 正常路径

```text
用户发消息 M：「把用量面板改成按天分组」
  ProjectAgentRunner idle → user_turn
  代理处置 M = 开任务：spawn_session({ anchorMessageId: M })
    Supervisor：校验深度与锚点 → 幂等 → 带快照建子会话（首条 = M 原话 + 任务说明）
               → 建 GoalPlan → IsolationPlanner → 入队 → 证据
  M 的状态标记：处理中 · 用量面板按天分组；user_turn 结束（代理可以只说一句「在做了」，也可以不说）
Scheduler 放行 → Goal Runner pump → AgentTurnExecutor(session_worker, P2)
  任务要跑 pnpm test → 权限审查产生待处理请求
  EventMapper → session_needs_user → Inbox
  Runner：needs_user 立即唤醒 → wake_turn → post_reply({ replyTo: [M] }) + Runner 附「需要你」卡
用户在代理会话里点允许 → 同一请求被解决 → 任务继续
任务完成 → keyFindings 交回 → 运行时算 VerificationVerdict（passed 3/3）+ AcceptanceDecision（auto）
  → session_verified → 唤醒
  → 代理判断验证够了（不够就 verify_session 追加核验，签收暂缓）
  → post_reply({ replyTo: [M], sourceSessionIds })：「改好了，测试和截图都核对过。」+ Runner 附「已验证 3/3」
  → 运行时代签：goalPlansRevise 写 resultAcceptance { acceptedBy: 'policy' } → 关闭闸门 → accepted
  M 的状态标记：已完成 · 已验证
用户追问「怎么验证的？」→ 代理 get_verification_detail → 回复第 1 层细节
用户要看证据 → 代理附 evidenceRefs → 回复里出现测试输出 / 截图 / diff / 验证报告芯片
（若 decision = confirm：回复附「需要你确认」卡，列出原因；用户确认才写 acceptedBy: 'user'）
```

### 11.2 插话取代

```text
任务 S1（锚定 M）在跑，用户发 N：「算了，不按天，改成按模型分组」（未引用）
  唤醒回合被抢占（若有）→ user_turn
  代理对照 roster：N 与 S1 相关，目标变了 → 取代
  spawn_session({ anchorMessageId: N, supersedes: S1, inherit: { report: true, branch: 'auto' } })
    Supervisor：校验 S1 可取代 → 带快照建 S2（首条 = N 原话 + 说明 + S1 报告）→ S2 建成后 S1 → paused + supersededBy
  代理回复 N：「原来按天分组的任务已停，改成按模型分组重新做；已有的面板结构沿用。」
  N 的状态标记：已停掉「按天分组」，改开「按模型分组」· 恢复原任务
  M 的状态标记：已被新消息取代
```

### 11.3 失败路径

```text
任务 A 连续三次同一测试失败 → blockerAudit → blocked
  → session_needs_user（kind: decision）→ 唤醒 → 代理判断：
     - 能换思路：message_session 给出新方向，任务继续
     - 需要取舍：递卡片给用户
同一窗口内任务 B、C 也同指纹失败 → CircuitBreaker 熔断
  → spawn 返回 breaker_open，自动重试暂停，代理会话出现熔断卡
```

---

## 12. 建设顺序

每一步都能单独合入、单独验证。M2 本身就有独立价值（后台任务不再依赖窗口），建议最先做。

| 步 | 模块 | 退出条件 | 对应分期 |
|---|---|---|---|
| M1 | 契约：`protocol/delegation.ts`（对象、事件、失败码、`DelegationOrigin`、`AgentReplyMeta`、`VerificationVerdict`、`AcceptanceDecision`、`projectWorkSession`、`projectMessageDispositions`、`computeVerificationVerdict`、`decideAcceptance`）；会话元数据 `role` / `parentConversationId` / `origin`；`acceptedBy` 增加 `'policy'` | 纯函数单测；与 `projectGoalPlan` 一致性测试；处置投影覆盖七种处置；签收策略逐条覆盖 confirm 原因 | P1 |
| M2 | 执行宿主：AgentProfileRegistry + AgentTurnExecutor + TurnSink；把 `runGoalTurn` / `runExplorer` / `runVerifier` 迁过去 | 关掉所有窗口 Goal Runner 仍能推进；已有 Goal / Explorer / Verifier 测试全绿 | P1 前置 |
| M3 | 派发：从划词子会话抽出「带快照的子会话」原语；SessionSupervisor（锚点、快照、原话带入）+ `project_agent` 模式白名单 + LocalDelegationProvider（spawn / list / report / post_reply） | 深度、幂等、白名单、锚点必填测试；划词子会话回归全绿；代理无法调用写类工具 | P1 |
| M4 | 通讯：EventMapper + ProjectInbox + SessionMessenger | 事件去重、游标推进、重放测试 | P1 |
| M5 | 编排：ProjectAgentRunner + ReplyComposer + 两个上下文来源；结论标记与策略代签提交；renderer 的回复引用条、来源芯片、结论标记、消息状态标记 | P1 场景跑通：低风险任务汇报即代签；需确认任务出现确认卡（调度器先用每项目上限 1 的简化版） | P1 |
| M6 | 需要你冒泡 + 插话（回答 / 并入 / 停止）+ AnchorScopeResolver；按需披露（`get_verification_detail`、证据芯片）与 `verify_session` | 两处批准同一请求；代理无批准入口；引用插话越界返回 `out_of_scope`；多消息合并回合每条都有处置；追问能逐层展开到证据；追加核验暂缓签收 | P2 |
| M7 | 调度：ExecutionScheduler（槽位、优先级、依赖）+ IsolationPlanner；接 `canRunPlan`；插话补齐并行、排队、取代（原子 + 继承 + 恢复原任务） | 三任务并行互不污染；P0 回合不被后台堵住；依赖闸门测试；取代原子性与恢复测试 | P3 |
| M8 | 异常：FailurePolicy + Watchdog + CircuitBreaker + 取消级联 + 重启恢复顺序 | 失败分类表逐行有测试；重启恢复集成测试 | P1 做基础（失败事件唤醒代理），P3 做全 |
| M9 | 结果跟踪：DeliveryTimeline + 汇报去重 + 项目记忆挂点 | 代理能基于时间线回答「这周做了什么」 | P4 |
| MM1–MM5 | 记忆体系（稳定 workspaceId → 存储与工具 → 事件卡与简报 → Curator 与准入 → 过期与冲突 → Skill Patch 候选） | 见 `project-agent-memory-system.md` §14；MM1 可在 M5 之后并行开工 | P2–P5 |

---

## 13. 待评审点

1. 项目代理单线程 actor，用户消息抢占唤醒回合（§8.2）。
2. `spawn_session` 结构化建 GoalPlan，不在任务里再跑一轮 intake（§4.1）。
3. 调度粒度是回合而不是任务（§4.2）。
4. 事件至少投递一次 + 去重，游标在代理回合成功后才推进（§5.2）。
5. 默认数值：全局 4 个回合槽位、每项目 3 条运行中任务、熔断阈值 3、去抖 3 秒、自发唤醒最短间隔 30 秒。
6. M2（执行宿主去窗口依赖）属于 chat runtime 的 B 级改动，是否先于 ADR 80 转 Accepted 单独做。
7. 被取代的旧任务进 `paused` 而不是直接 `cancelled`，直到新任务被验收或用户放弃（§8.3，运行时契约 §3）。
8. 拿不准并入还是取代时默认并入（§8.3）。
9. 引用插话在执行层强制限定范围（§5.4）。
10. 签收策略 `auto` 的条件与验证下限表（§6.6，运行时契约 §2.7）。
11. 合入源头分支默认仍需一键确认，`autoHandoffOnPolicyAccept` 默认关闭（§6.7）。
12. 代签在代理汇报之后才提交，追加核验次数有上限（§6.7）。
