# 项目代理委托运行时

创建时间：2026-09-24
最后更新：2026-11-25

## 2026-11-01：意图驱动协调与目标闭环（交付分支源码已实施）

[ADR 117](../decisions/117-intent-driven-coordination-and-goal-closure.md) 提议在既有 coordination work 中记录输入解释、原目标覆盖与下一步处置，修正阶段签收过早结束根责任、交付失败影响范围过大等边界。四包按意图契约 → 统一判断/收尾 → 交付/失败隔离 → 事实/进展治理顺序，见[实施卡](../../playbook/v0.1.0/intent-driven-coordination.md)。当前四包已获准实施并在交付分支完成源码自测；实际接口、证据边界和与 ADR116 的 RC32 组合契约见 ADR117 §14–§15。下述 GoalPlan/Evidence 真值和验收政策保留；源码自测不等于组合候选或安装版验收。

## 2026-10-23：只读 Git 与委派能力预检

[ADR106](../decisions/106-readonly-git-and-delegation-capability-admission.md) 增加 `local.git.query`：主 Bot 与只读工作者可以取得带时间、完整性和 Evidence 的仓库事实，通用 shell 限制继续保留。新委派声明 requiredCapabilities，宿主按目标工作者实际投影，在新建会话/计划及协调替换的执行版本变更前检查成功标准所需能力。缺项属于技术受阻，返回分层诊断，不要求用户降低验收范围。成功准入仅保存需求和工具清单指纹；不改写历史任务、会话与 Evidence，也不批量恢复或关闭既有任务。

## 2026-10-06：受阻循环修复契约

`SessionReport.summary` 来自工作会话最后一段持久化的可见 assistant 正文，`keyFindings` 来自已完成叶任务的 result；没有结果时返回空值。不得把 goal 或成功标准当成调查结论。`taskBrief` 单独保存原任务说明，界面说明区域只使用该字段，不把报告换个标题当说明。报告附 `contentSource` 标记正文来源；工作者正文是未验证的结果陈述，不能代替 Evidence 或独立核验，不改变签收状态。主机器人据此读取实际报告并继续核对，避免因为目标投影为空而反复另开任务。

UI 完成门针对界面交付。提交记录的“hash、主题”属于 Git 元数据，不能因词语“主题”自动武装视觉门；实际界面主题、颜色、组件修改仍须通过原有视觉门。本修复不撤销已存在的视觉要求，不自动签收 manual 成功标准。旧任务的错误验收事实保留可查，新任务使用修复后的分类。

### 完成前核对与结果签收（2026-10-06）

两者是不同事实。Runner 因 `manual_dod_confirmation_required` 停在 executing 时，主 Bot 对话投影“核对报告”卡，展示具体待人工核对标准，并提供右侧完整报告。不能生成完成后的 `confirm_result` 动作。人工核对通过后才继续原 Runner 的 verify；不写 `resultAcceptance`，不豁免自动检查、Verifier、权限或 Evidence。

既有 `project-agent:confirm-result` IPC 的请求由协议声明为两种明确 stage：兼容旧请求的 `result_acceptance`，以及带 `reviewToken` 的 `manual_completion`。应用服务回读 workspace/session 归属，监督者串行回读当前报告、成功标准与核验结果；核对 token 绑定这些事实，过期或任务状态变化则拒绝。仅本地用户点击记录既有 GoalManualConfirmation（decidedBy=local_ui），模型普通回答或自述不构成确认。重复点击同一 token 幂等；持久化失败不恢复 Runner，恢复失败保留确认供重试。完整报告只投影可见输出，不包含私有思考。

已完成的任务只有在 Runner 不再执行/复核时才公开结果签收。临时 completed 状态随后回到 executing 时，最新主对话刷新必须撤销已消失的宿主卡片，不保留旧的可操作缓存。服务端点击失败同样触发事实刷新，界面把状态变化解释为自然语言；原始错误码只作诊断数据。

### 主对话执行预算与复核收尾（2026-10-06）

ProjectAgentRunner 的既有用户/唤醒预算必须传入每次 AgentTurnExecutor 请求，成为 request-scoped executionBudget；不能只在整次 Provider Agent Loop 返回后计数。共享 Runtime Pipeline 在开始工具批次之前检查剩余工具调用额度，批次超额时不派发该批次；每个模型请求同时消耗模型轮次额度。耗尽属于未完成的结构化 exhausted 终态，保留已有工具结果、Evidence、公开进展及 usage，经宿主错误收尾停止当前回复；不能自动重试耗尽回合、伪造完成或继续循环。没有显式预算的普通聊天保持既有配置。Capability Provider → Runtime Projection → PermissionGrant → Evidence 链路不变。

预算耗尽是本次尝试结束，不计为提供方不可用，也不进入提供方自动退避/熔断重试。失败卡和回合先落盘，再提交本次收件箱游标及输入执行确认；提交只确认这些事件已尝试处理，不写任务完成、结果签收或验证通过。手动重试沿既有路径重新执行，新用户消息可开启新回合。重启不得因未提交同批收件箱而重新消费已持久化的耗尽回合。界面使用共享错误分类，明确提示检查达到上限、回复尚未完成；完整诊断仍在右侧详情。

手动重试属于用户正在等待的交互：即使原回合是 wake，也必须经既有 ProjectAgentActivity 立即显示等待、公开进展及工具过程，并支持既有停止回复动作。原 kind、事件、预算与授权边界保持；不能把重试点击伪装为新的用户任务授权。自动 wake 仍不披露中间正文。手动重试的公开段落随 agent_turn.publicUpdates 持久化，私有思考不进入该投影；停止后重试携带原事件批继续，不能丢弃空 userInputs 的 wake。重试 IPC 仍等待本次执行收尾，不以按钮变灰代表任务完成。

项目代理固定 restricted_local：文件 Provider 对已准入目录以外的只读搜索/列举请求，应经原 PermissionGrant 与 Evidence 路径及时拒绝，不进入普通聊天的人工授权等待。它不继承全局 full/session 授权，也不因手动重试扩大目录范围。普通聊天仍按原授权策略处理越界请求，但权限调用必须保留 Manifest 对应的 read/list/search capability 与 L1_local_read 类型，不能伪装为文件写入。停止回合也保存原事件批到既有 meta.recovery，重启后只允许显式重试，不自动重放。

失败卡的 retried 解决记录必须由新的 canonical 回合成功收尾支持。关闭窗口、宿主退出、租约丢失或停止回复不能单凭等待结束就写成重试成功。旧版已写入 retried、但没有后续宿主回合的卡片继续保留重试动作；追加记录仍保留，不改历史事实。

耗尽 agent_turn.meta.recovery 采用 ProjectAgentTurnRecovery 契约保存宿主 events 与 throughSeq，供明确的手动重试及写入后、游标提交前的崩溃恢复。恢复只认最新宿主回合对应的预算错误卡，历史恢复资料不进入新授权。旧耗尽记录缺少批次事实时只停住自动推进，不能盲目提交当前收件箱；手动重试或新用户输入可携带当前真实事件重新处理。

post_reply 锚点失败通过现有 Tool Result 返回被拒绝的 messageIds，以及当前对话最近最多 5 条真实用户消息的 id/短摘要（每条最多 120 字）。这些是事实恢复材料，不是新用户指令、授权或 System Context。端口不能丢弃这些字段；模型须重新选择并提交经过原校验的锚点。不得自动替换未知 id、公开被拒绝的回复正文，或把历史锚点当作唤醒回合开新任务的授权。权限、来源状态、Evidence 与独立核验校验保持有效。

显式重试通过既有 project-roster L7 Source 准入原 canonical 回合的工具执行摘录（最多 16 项、总 12000 字符），包含 turnId、工具名、参数/结果的限长预览、原 Evidence refs 与截断事实。只读原记录，不重新执行旧工具；不准入 private thinking 或 round.text。摘录是未验证的历史事实，不成为系统指令、当前任务状态或新的 Tool Result/Evidence；来源截断、事实变化仍须经原工具回查。只绑定当前被重试回合，普通新输入及自动 wake 不继承这些摘录。重试仍使用原预算与授权，但模型应接续已经取得的结果，不反复从头调查。

独立复核的 verifying 标记只表示复核仍在进行。通过、未通过、异常、取消和不可用都必须收尾；未产生有效结论时清除标记并保留此前验证事实，不写虚假的 passed/failed verdict。成功完成调用返回本次实际结论，不再返回 verifying。记录结论失败同样结束暂态，并保留可诊断错误。

核验输入同时准入 buildSessionReport 读取的实际工作者可见报告及 contentSource，作为用户消息中的未验证事实材料。报告缺失/截断必须明示，不能拿 goal 填充。核验器对报告断言与执行快照进行比较，报告本身不是执行 Evidence；除成功标准明确要求文件交付外，对话中的报告不得被误判为“必须写入报告文件”。已有 readonly、引用准入及输出 JSON 校验不变。

工具过程计时使用 Tool Call/Result 事件的宿主 startedAtMs/endedAtMs。Activity 接收事件时钟仅作旧事件兼容兜底；agent_turn.rounds[].toolCalls 可持久化同一时间，经过 Runner、历史读取与 renderer 投影仍保留。缺失计时不制造 0 秒；已知小于一秒显示“少于 1 秒”。计时是展示元数据，不改变 Evidence 或完成事实。

委托背景按任务锚点准入的 A 级变更见 `project-agent-input-attachments.md`。指定历史快照继续保留完整性确认，普通模型提问不充当历史遗漏授权。

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

**2026-11-25 补充（[ADR 137](../decisions/137-web-research-verifier-floor-and-preparation-recovery.md)）**：请求 `local.web.search` / `local.web.fetch` 且未请求交互结果发布的只读会话，独立核验为 `not_required`，按本行交付，不因 `model_review` 标准或核验模型配置自动上调。其 `model_review` 标准不被标记通过，列为未经独立核验，不阻断关闭闸门。显式复核仍走既有 `reverify_session`。其余会话的验证下限与 `model_review` 验证不变；ADR 131 NR-04 的「必须等待独立核验」限于普通 headless Goal Runner。

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

**失败后复核的完成衔接（2026-10-07，B 级修复）**：主 Bot 的 `verify_session` 使用现有本机 Verifier、Evidence 索引和完成闸门。只读任务若仅停在旧的 `verifier_failed`，复核通过且核验对象未改变，Runner 应重新检查叶子证据、成功标准、人工确认及 UI 门；全部通过后清除旧阻塞并发布原有 completed 事件，再由原签收策略判定。核验记录在现有 `hostVerification` 内绑定任务/标准/报告的内容指纹；对象变化、运行中、暂停、取消、缺证据或其他阻塞均不能被旧核验放行。旧记录缺指纹时需再复核，不能补造通过事实。此衔接不授予模型签收能力，不写记忆，不代替人工 DoD 或项目 confirm 策略。真实确认动作仍在主对话的宿主卡片里呈现；模型不得自行编造「去卡片亲手验收」选项或把自然语言回复称作宿主签收。

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
  dependsOnPolicy?: 'accepted'; // 唯一策略：全部 completed 且 resultAcceptance.acceptedAt 已持久化；result_ready 不放行
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
- 落地范围与验收见 `playbook/v0.1.0/beta3-verification-consistency.md`。这是已发布 Beta3 审查后的补修，交付 Beta4；不扩展 Beta4 的并行、隔离与项目目标能力。
- 档案增加可持久化的 `acceptancePolicy`（auto / confirm）、`planApproval`（never / writes / always）和既有 `modelPolicy`。更新经 `update-profile` 校验并保存；既有档案缺字段时读取默认值，不批量重写旧数据。模型覆盖只接受当前已配置的模型与允许角色。
- 验证必须覆盖正式注册入口到模型调用、Provider 到监督者、完成事件到 L7、回复拒绝、错误终态、重启 id 与三种卡片动作。模块单测通过不能替代真实项目、安装迁移与连续日用验收。

### 14.2 Beta4 发布前的真实交付缺口补修（2026-10-01）

- 结构化自动验收的同一用户委托按宿主执行身份幂等：项目/父对话、用户锚点集合、kind/readOnly、验收操作参数、dependsOn/supersedes；标题/brief/criterion 描述与 id 不改变身份。没有自动标准时保持严格请求身份。不同目标参数、新用户锚点、显式替代保持不同；不通过模糊文本相似度合并。持久化旧计划可重建身份匹配，保留原记录不批改。
- read_file/list_files/search_files 执行成功后，既有 EvidenceIndex 可追加 `bodyPreview: { kind: 'file', text: string, truncated: boolean }`，正文最多 4000 字符、复用既有秘密脱敏；披露最多 2000 字符并保留截断事实。来源是 Provider Tool Result，不是助手正文或 goal wrapper；读取展示执行时快照，不复读当前文件。旧无快照记录不得编造历史证据。
- completed 无独立 verdict 时也产生 result_ready 唤醒事实，完成事件以稳定 completedAt 标识幂等，不把完成事实当核验/签收事实。项目代理仍按现有工具核验并关联回复，宿主再过关闭闸门。
- 针对已完成但未交付任务的用户锚点，回复必须带对应 sources 与当前 statusClaims；漏来源拒绝并返回待引用 session 和宿主状态。正常纯问答与尚未完成任务的普通交流不受此规则影响。
- memory Provider 从已有主机 toolContext 读取 mode/turnRole/workspace/messages，和 flat context 保持相同身份准入。模型工具参数不决定角色；worker 仍不可写记忆。熟悉项目沉淀沿用关联回复、宿主核验与 Evidence 准入，不以 stated 或源外回复绕过。
- 范围及回归见 `playbook/v0.1.0/beta3-real-gaps.md`；沿用 ADR 80/81/85，无新的执行通道或存储目录，交付 Beta4，仅本补修范围，不开放并行/隔离/项目目标等其他功能。

- 真实复跑补充：`independentVerifier=missing` 必须进入既有 `verificationBelowFloor` 签收闸门；`result_ready` 来源的 `post_reply` 若未补独立核验，返回 `verification_required`，由模型走既有 verify_session/Provider 链重试，不由生命周期直接运行核验。宿主保留的 `lifecycle-research-*` 锚点不能作为 memory_remember 的 stated 来源（它是文件熟悉请求，不是用户陈述文件事实）。

- 核验器事实输入补充：既有 verifier user 请求可携带本计划叶子/标准引用对应的 EvidenceIndex 文件快照，总正文限 12000 字符。执行正文是 factual/untrusted context，不能成为系统指令。passed 报告的 evidenceRefs 必须非空且归属于这些已索引快照或本轮真实 Tool Result；缺失/伪造报告仅走现有一次格式修复，随后失败，不制造引用或弱化验收。

- 完成唤醒竞态补充：既有 runner.verifierRuns 的最新终态记录（runId/status/completedAt）作为结果事实修订标识。completed 状态先于核验落盘时，核验终态修订仍须产生一次 result_ready 事件；它只要求代理重读宿主事实，不宣称核验通过。普通 acceptance/updatedAt 更新不重复唤醒。

### 14.3 RC命令证据核验补修（2026-10-02）

- EvidenceIndex既有bodyPreview扩展command种类，内容是实际local.shell.exec的成功终态、exitCode0且PermissionGrant已allow的Tool Result结构化stdout/stderr/退出码快照。两宿主使用共享准入Module；执行call/result/Evidence身份匹配。拒绝、失败、运行中、超时、中断及wrapper/模型声明不准入成功快照。秘密脱敏与单条4000字符上限保持；首个Provider快照不可被wrapper覆盖，旧记录无快照不得补造历史内容。
- Verifier准入本计划标准/叶子引用的file或command快照，标准引用优先，总预算12000字符，并保留createdAt与truncated事实。记录有显式planId时必须匹配；仅无planId旧记录可按相同conversation归属。快照进入已有Verifier用户事实请求，绝不成为系统指令。截断/矛盾/缺少最新证据必须继续使用既有只读工具取证或报告失败。
- 既有Evidence展示command种类直接呈现执行快照，不以读取当前文件覆盖历史事实。权限、核验、签收及独立交付授权的闸门保留。实施范围、原失败与验收见 `playbook/v0.1.0/rc-command-evidence.md`；依ADR80，不开放额外能力或存储。


### RC 本地计划批准历史（2026-10-02，Accepted）

ApprovalStore压缩保留approved的plan_approval折叠历史，避免新决定在监督者回读前即被丢弃，并支持崩溃后重放；普通已终结工具批准压缩规则不变。旧版本已经删除的历史仍unknown。

本地计划批准先落盘ApprovalStore，然后监督者回读真实approved/local_ui且workspace/session/plan/conversation、capability/kind/approvalId绑定一致的记录，将既有GoalApproval闭合字段decision=approve、confirmationId、decidedBy、decidedAt冻结进计划，再排队或启动。非人工、未批准或错绑定不能生成该事实；写失败不执行。批准已落盘但未启动时可重放完成准入。重启和ApprovalStore压缩不会删除已冻结的计划历史；旧计划没有历史保持unknown。Verifier Source把该有限历史加入现有L7事实brief，不能作为PermissionGrant、工具Evidence引用或结果签收。任务通过既有goal_get_plan读取。见rc-local-plan-approval-facts实施卡。

### RC 用户回答恢复补正（2026-10-02，Accepted）

message_session(intent:answer)的原文是用户侧事实。当任务已准入且确实能消费等待用户输入时，运行时消费该回答并沿既有GoalRunner恢复；不能只落盘而让任务继续waiting_user。answer在非等待会话保持追加语义，amend在运行中仍作为下一回合纠正；等待中的两种intent都沿同一回答消费接口。暂停/取代/前置失败排队以及未批准计划的门不因文字声明批准而打开。证据由实际message_session Tool Result与原GoalPlan事件/Runner产生，不从代理文字推断恢复成功。见rc-session-answer-resume实施卡。

### 2026-10-02 成功回复的内层循环收尾

成功 post_reply 的回合终结必须覆盖 Provider 内层循环。Delegation Provider 在已有 ToolResult.outputPreview.control 返回 terminal；控制属于本地结构化结果，失败/拒绝/取消不得携带此成功控制。成功 suppressed 或幂等重放仍结束本轮。现有 terminal tool pipeline 先应用 Tool Result/计费与 Context accounting，再统一 done，由外层 Runner 落 canonical 回复或安静抑制；不要求模型再生成文字，不放宽空响应错误护栏。权限/Projection/Evidence 与持久化边界保持。见 playbook/v0.1.0/rc-post-reply-terminal.md。
