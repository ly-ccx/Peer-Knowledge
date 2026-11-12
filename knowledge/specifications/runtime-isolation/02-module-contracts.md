# 02 逐模块 Interface 与所有权

创建时间：2026-11-11
最后更新：2026-11-12
状态：详细设计候选。所有 `Context` 为 Host 构造的 `{VerifiedCaller,HostRef,remainingBudget,AbortSignal}`；业务写入另外要求 operation key 和当前 authority，不能从 UI 拼装。`Ref` 均能由其 owner 在数据根内验证，不能转成任意路径。

## M00 Presentation / Client State

Interface：`sendInput(ProjectInput):CommandReceipt`、`requestControl(ControlTarget):CommandReceipt`、`openView(ViewQuery):ViewPage`、`subscribe(SubscriptionRequest):SubscriptionReceipt`；组件只使用客户端接口，不持有 Runtime/Store。`saveClientState({key,expectedRevision,draft|readingAnchor|layout}):StateWriteReceipt`、`readClientState(key):ClientState` 只允许当前客户端拥有的设备内表达状态；保存draft不把它变成正式输入或Agent上下文。ADR115已显式启用/选模型的continuation仍可通过原预测profile准入当前draft，不扩大范围。

拥有草稿、组合输入、焦点与阅读意图；持久端口由 Gateway 的 ClientState Adapter 提供，按原 input-drafts/布局存储，不写 task/approval。依赖 Protocol、chat-kernel/task-thread 和受限 Client API，不依赖领域实现。QU 保存失败保留内存草稿并给可恢复反馈；晚返回只在同 key/expectedRevision 时采纳，不抢焦点或恢复自动贴底。卸载取消查询与表达订阅，不取消工作。重新连接用同operationId查提交结果，不能因按钮恢复可点而重复发送。

## M01 Client Gateway / Command Delivery

```ts
openConnection(bootstrap: BootstrapProof): Promise<ConnectionReceipt>
execute(meta: CallMeta, command: CommandRequest): Promise<CommandReceipt>
lookup(meta: CallMeta, key: CommandKey): Promise<CommandReceipt|NotFound>
query(meta: CallMeta, request: ViewQuery): Promise<ViewPage>
subscribe(meta: CallMeta, request: SubscriptionRequest): Promise<SubscriptionReceipt>
saveClientState(meta: CallMeta, input: ClientStateWrite): Promise<StateWriteReceipt>
close(connectionId: Id): Promise<void>
```

Gateway 拥有连接/方法准入、运输预算及 command journal 的接收/路由，不拥有任务/权限结论。只依赖 Protocol/schema、CallerResolver、CommandJournalPort、OwnerCommandPorts、QueryPort、ClientStatePort 和 Transport。QG/QA/QC/QU/QE 按04；execute的 accepted 只在 journal 提交后返回，lookup不调模型。断线销毁订阅与纯读，保留已接受命令。远程批准/管理仍按现行 catalog 限制；搬迁不扩大角色。

## M02 Input / Work Coordination

```ts
acceptInput(key: CommandKey, input: ProjectInput, context: Context): Promise<InputReceipt>
handleBatch(workspaceId: Id, cursor: EventCursor, refs: readonly EventRef[]): Promise<BatchReceipt>
controlWork(key: CommandKey, workId: Id, kind: 'pause'|'cancel'|'resume',
  expectedSource: SourceVector, authorityRef: Id): Promise<WorkControlReceipt>
readWorkHead(workId: Id): Promise<WorkHead>
recoverWork(workId: Id, expectedSource: SourceVector): Promise<RecoveryReceipt>
stagePendingInput(key: CommandKey, inputRef: Id, expectedRevision: Revision): Promise<PendingInputHandoff>
claimPendingInput(key: CommandKey, expectedRevision: Revision): Promise<PendingInputHandoff>
finishPendingInput(key: CommandKey, revision: Revision, inputReceiptRef: Id): Promise<HandoffReceipt>
discardPendingInput(key: CommandKey, revision: Revision, caller: VerifiedCaller): Promise<HandoffReceipt>
```

输入服务拥有原 inputId 的耐久接收与消费cursor，Work Coordination拥有既有work/intent/mandate/disposition/责任和交付关系。依赖输入/inbox/coordination Repository、现有纯Intent/Disposition kernel、SchedulerPort、SessionControlPort、VerificationPort、角色化TurnDispatchPort；不持有Supervisor或UI Query。模型语义由主Bot attempt产生，kernel只检查来源/版本/准入，不硬编码规划。

QW 每workspace一个判定；先校验lease与输入身份，提交原输入/关联，再在当前source上处置；写入前后跨await重检control。handleBatch仅在其产生的必要原提交成功后推进原cursor；中断批次下次从已提交cursor继续。同work pause/resume按接收序，不因后来消息撤销先前stop。重复inputId返回原message/work refs；事实不足/持久化错保留pending并返回原具体blocker。recoverWork只恢复该候选，不扫描无关正文或重发未知派发。

原重启pendingTask归输入交接，不归UI草稿。peek只读；原consume迁为claimPendingInput，不提前删除正文。以原文件版本/digest及稳定operation记录step，使用同inputId提交；finish仅在原InputReceipt身份/目标匹配后CAS清除原pending文件。显式用户丢弃另记discard回执，不能抹已派发unknown；不同workspace/坏文件保留具体blocker，不自动丢弃。claim与receipt关联保存在command journal steps，输入事实仍在原Input/Inbox，不新增第二输入真源。新旧重启helper不能混跑。

## M03 Session Scheduler

```ts
enqueue(key: CommandKey, ref: {sessionId: Id; planId: Id; expectedExecution: SessionExecutionIdentity},
  priority: ExistingPriority): Promise<QueueReceipt>
selectReady(workspaceId: Id, limit: number): Promise<readonly AdmittedAttemptRef[]>
onSettlement(receiptRef: Id): Promise<ScheduleReceipt>
readQueue(workspaceId: Id, cursor?: Cursor): Promise<QueuePage>
recoverQueue(workspaceId: Id): Promise<RecoveryReceipt>
```

拥有原排队顺序与公平调度，不建立新任务真源。依赖原Plan/QueueRepository、ControlFactsPort、ResourceAdmissionPort、TurnDispatchPort、现有依赖/priority kernel；不依赖Query/ModelEncoder/Grant UI。QT的每Runtime16槽只约束在途，原任务/模型预算不变。select先按轻索引过滤候选，再逐个校验当前execution、control、依赖和原reserve/activate；只有真实准入才写phase并派发。失败释放本次未激活预留，已派发按receipt结算；不能把资源等待写成failed。队列可由当前Plan重建，只有owner持lease可重写顺序镜像；保留已有enqueue序与aging，不用时间猜执行结束。

## M04 Session Control

```ts
request(key: CommandKey, input: ExistingSessionControlRequest, context: Context): Promise<ControlOperationRef>
readFacts(sessionId: Id): Promise<ControlFacts>
reconcile(operationId: Id): Promise<ControlProgressReceipt>
awaitSettlement(operationId: Id, readBudgetMs: number): Promise<ControlProgressReceipt>
```

拥有原SessionControlOperation/StopBarrierReceipt，镜像不是第二owner。依赖Coordination/PlanRepository、ExecutionHandlePort、ResourceAdmissionPort、现行Control kernel与lease；不依赖Query、模型或Project UI。QC一session只有当前操作；request先耐久recorded并关闭新准入，再排空/中断；原30s窗口到期进入reconciling，不能自动settled。取消覆盖接管依现行superseded/操作链保留回执；resume须当前source/原authority重检，不从旧消息sources恢复。

awaitSettlement只是有界读取，不占住control线程等停稳；响应可为draining/reconciling。句柄结果未知按原unknown/claim保护，不因进程连接断开判ended。冷恢复用operation/execution/recorder身份继续同一操作，不生成新的取消副作用。磁盘失败按04关闭内存新准入、保留未知和本地故障，绝不回stopped。

## M05 Resource Admission

```ts
inspect(execution: SessionExecutionIdentity, scopes: readonly ExecutionResourceScope[]): Promise<AdmissionFact>
reserve(input: ExistingReserveRequest): Promise<ClaimReceipt>
activate(claimId: Id, expectedRevision: Revision, execution: SessionExecutionIdentity): Promise<ClaimReceipt>
recordHandle(claimId: Id, handle: ManagedHandleObservation): Promise<ClaimReceipt>
settle(input: ExistingSettleRequest): Promise<ResourceSettlementReceipt>
reconcile(input: ExistingReconciliationRequest): Promise<ReconciliationReceipt>
```

拥有原设备资源账本claim/hold/retainedUnknown/闭包与对账回执。依赖ExecutionResourceRepository、当前Lease/ControlFacts、受管句柄/recorder proof和原127政策；不依赖Scheduler排序、UI或模型文字。QS资源事务串行同resourceRef，跨项目仍原子；inspect没有预留效力。reserve/activate在同事务验证execution/policyRef/claim revision，不能先快照后无检查写。父进程死不证明工具死；`ask/bot_verified`和scope沿原126/127；失败返回具体protection，不自动清理账本。计算许可与业务claim分表，计算worker退出不释放工具资源。

## M06 Agent Turn / Execution

```ts
run(ref: AdmittedAttemptRef, inputRefs: readonly InputRef[], context: Context): Promise<TurnReceipt>
interrupt(attempt: AttemptRef, controlOperationRef: Id): Promise<InterruptObservation>
reattach(attempt: AttemptRef, afterFrame?: number): Promise<AttemptSnapshot>
recoverAttempt(attempt: AttemptRef): Promise<AttemptRecoveryReceipt>
```

AdmittedAttemptRef固定work/session/plan（适用时）、role、executionEpoch、goalRevision、modelSelectionRef、leaseRef、turn/messageId与原dispatchRef；不传整个Settings/Supervisor。Agent Turn拥有本attempt流式和终态消息，不写Work accepted或Grant。依赖ContextAdmission、ModelAdapter、CapabilityRuntime、TurnRepository/TerminalCommitter、既有response/continuation guards；无Verification/Query反向依赖。

QT/QX，工具序与角色限制保留。先确保原messageId占位耐久，再启动模型；ToolCall经唯一能力链；结果按原toolCallId配对。所有done/error/aborted/finally共享同一terminal barrier：封闭迟到分片 → await准确消息提交 → 发布真实终态/释放槽。缺消息不upsert/不取最后assistant回退。模型/工具未知派发不能自动重跑；recoverAttempt按原native checkpoint/receipt恢复，Context超预算返回具体恢复阻塞，不裁掉约束。等待子任务按原silentWait/continuation协议让出槽和锁。

## M07 Context Admission

```ts
prepare(input: {attempt: AttemptRef; inputRefs: readonly InputRef[];
  modelSelectionRef: Id; contextEpoch?: Id}): Promise<AdmittedContextRef>
preparePrediction(input: ExistingPredictionContextRequest): Promise<AdmittedPredictionContextRef>
open(ref: AdmittedContextRef): Promise<EncodedContextInput>
assertCurrent(ref: AdmittedContextRef, attempt: AttemptRef): Promise<ContextValidity>
dispose(ref: AdmittedContextRef): Promise<void>
```

拥有原Context epoch/snapshot/source admission，不拥有PermissionGrant或能力执行。依赖已登记Source registry/assembler、CanonicalInteraction/Memory/Instruction只读Ports、当前model能力与原权威计量、附件既有准入、版本Store；不依赖Provider-specific消息形状/Renderer。依QX/QR的纯prepare子任务和04的8请求/32MiB上限。层序、trust/checksum、L7 continuity和原成对ToolResult不变，Source内容不提升为system指令。

open仅向合法ModelAdapter提供本attempt内存/stream refs，不向Renderer返回全部历史。跨await降权、换父、control、source变更使ref失效；有界重prepare最多2次，继续变化返回CONTEXT_VERSION_CHANGED。保真预算不足返回CONTEXT_BUDGET_EXCEEDED，不静默裁尾/删除未知工具；恢复用原受支持的压缩/模型切换/明确重试入口，未接受ADR123的情节记忆不顺带启用。

## M08 Model Provider / Encoder

```ts
resolve(selectionRef: Id, role: ExistingRole): Promise<ResolvedModel>
stream(input: {attempt: AttemptRef; contextRef: AdmittedContextRef;
  projectionRef: Id; dispatchRef: Id}, sink: ModelFrameSink): Promise<ModelOutcome>
completeCognition(input: ExistingPredictionOrCompletionRequest,
  contextRef: AdmittedPredictionOrCompletionContextRef, sink: ModelFrameSink): Promise<ModelOutcome>
cancel(dispatchRef: Id): Promise<ModelCancellationObservation>
lookup(dispatchRef: Id): Promise<ExistingDispatchOutcome>
```

只负责现有渠道/角色/强度解析、credential seam、Provider lowering/网络或本地推理、结构化流；原冻结选择和83政策不变。依赖Context reader、Projection schema、CredentialPort、现有transport/recovery/encoder；不依赖Goal验收、UI或全局Permission单例。网络等待不占控制线程，deadline沿原配置。SDK按需加载，重试按原Provider分类；未知已经发送的派发必须lookup/原continuation政策，不能换模型重放未知工具。失败保留安全traceRef与原cause，不将认证失败改成空成功；凭据不进message/log/Query。

## M09 Capability Runtime

```ts
project(input: ExistingProjectionRequest): Promise<RuntimeProjectionRef>
invoke(input: {attempt: AttemptRef; projectionRef: Id; call: ExistingToolCall;
  dispatchRef: Id}): Promise<ExistingClientToolResult>
settle(dispatchRef: Id): Promise<DispatchSettlementReceipt>
stop(handleRef: Id, controlOperationRef: Id): Promise<ManagedHandleObservation>
```

拥有调用生命周期与原结果/Evidence提交；Evidence本体由实际Provider产生，执行器不从文本合成。依赖Registry/Manifest/Projection、Authorization、ResourceAdmission、currentControl/Lease、Provider Ports、ToolResult/EvidenceRepository；不importWorkCoordinator实现。QX；角色/Mode/Projection/lease/control/resource/Grant全部当前匹配才派发。先耐久登记原dispatch/声明scope，再调用Provider；正常/拒绝/取消/超时都生成原结构化结果；未知副作用保留原unknown。Platform Adapter只是Provider的实现，不另走一条执行链。

委派/等待/Agent通信Provider使用受准入的DelegationCommandPort，内部同样operation/execution identity；不抓父Supervisor可变对象。平台/Provider回调后先保存其原result，再按当前epoch决定是否公开给当前attempt；旧结果保留原历史，不推进新epoch。队列/连接超时不伪造工具失败或成功。

## M10 Authorization

```ts
resolve(input: ExistingBotPrincipalRequest): Promise<PrincipalPolicySnapshot>
review(call: ExistingPermissionRequest, execution: AttemptRef): Promise<GrantOrPendingOrDenied>
decide(key: CommandKey, input: ExistingApprovalDecision, caller: VerifiedCaller): Promise<ApprovalReceipt>
validate(grantRef: Id, call: ExistingToolCall, execution: AttemptRef): Promise<GrantValidity>
updatePolicy(key: CommandKey, input: ExistingPolicyCASRequest): Promise<PolicyReceipt>
```

拥有原主体(policy binds workspace/current agentConversationId)、revision、待批准与逐操作Grant；依赖原BotAccessPolicy/Approval/GrantRepository、父子身份解析、Role/Mode/explicit-deny kernel、OS权限事实。没有工具或调度依赖。QC处理用户决定，QS处理policy事务，批准等待不占调用队列/写锁；已登记pending成为原awaitingApproval挂起点，决定后只唤醒原call/attempt重新准入。

once不跨调用继承，Full不覆盖deny/Role/OS/计划门；撤回后所有新执行validate当前版本。恢复pending按原stale政策，不自动续旧Grant。损坏/未知schema拒绝，不重建成宽权限。View里看得到批准记录不代表能决定它。

## M11 Verification / Acceptance

```ts
requestReview(key: CommandKey, input: ExistingVerificationRequest): Promise<ReviewRequestRef>
readReportSource(target: {kind:'session'|'plan'; id:Id}, sourceRevision: Revision): Promise<ReportSourceRef>
applyVerdict(key: CommandKey, requestRef: Id, verdictRef: Id): Promise<VerificationReceipt>
accept(key: CommandKey, input: ExistingAcceptanceRequest, caller: VerifiedCaller): Promise<AcceptanceReceipt>
recoverReview(requestRef: Id): Promise<ReviewRecoveryReceipt>
```

拥有原review request/verdict refs/resultAcceptance/交付事实；依赖独立ReportSource/EvidenceReader、现有纯criteria/acceptance gate、RoleTurnDispatch、GoalPlan/coordination Repo、当前policy/control。Agent Turn不反向调用本模块；readReportSource不进入完整session/acceptance投影。QT核验保留槽；真实Verifier也走原模型/工具/权限/Evidence链。apply必须匹配被核验的source/criteria/attempt，结果变更返回VERSION_CONFLICT，不能把旧passed套到新结果。等待人工/外部核验不持锁。中断核验记录interrupted，既有已完成工具结果保留，恢复原request/续接政策；无证据历史保持未验证，不由读取补passed。

## M12 Projection Query

```ts
query(query: ViewQuery, caller: VerifiedCaller, budget: ReadBudget): Promise<ViewPage>
subscribe(input: SubscriptionRequest, caller: VerifiedCaller): Promise<SubscriptionReceipt>
cancelRead(connectionId: Id, requestId: Id): Promise<boolean>
invalidate(event: CanonicalRevisionHint): Promise<void>
catchUp(sourceRef: Id, targetVersion: Revision): Promise<ProjectionReceipt>
```

只拥有可丢弃读模型，依赖命名ReadRepository、原纯生命周期projector、LiveObservation只读Port、projection worker；不依赖Supervisor/GoalRunner/PermissionGate的业务实现。QQ/QP/QR/QE按04；View算法、字段和source边界见03。冷/变更后的重建都是worker，返回rebuilding而不是同步main全文回退。损坏隔离该source，其他项目继续。live缺失是unknown，不按timer变ended；重启新cursor generation，旧响应不能污染新View。

## M13 Canonical Repositories / Commit Service

Interface是05的按聚合方法目录，不暴露generic `replaceState(any)`。共同协议为`prepare(typedOperation,expectedSource,owner):PreparedRef`、`commit(PreparedRef,currentOwner):CommitReceipt`、`lookup(operationRef):CommitFact`，其中typedOperation由聚合owner私有构造，客户端不可调用。拥有耐久与物理格式/锁/CAS，业务结论只由原domain owner产生。

依赖文件/SQLite/blob Adapter、原schema/reducer/版本/锁/lease/fence；不依赖UI/Query或Model。QS/QR；prepare不持写锁，commit在原锁序内重检版本/owner/fence，保证原sidecar/精确messageId和terminal barrier。成功后才发revision hint，丢通知可由canonical version补读。失败不删原数据或恢复sidecar，不将未知commit当作可自动重做。大记录按05流式/worker，不把整个Store状态传回control。

## M14 Host Lifecycle / Platform Broker

Interface与具体方法见06：`start/handshake/registerBroker/drain/stop/recoverCandidates`、`platform.invoke/lookup`。Host只装配Adapter、持有资源和恢复依赖，不写协调/验收算法。Broker只实现受限平台操作，验证原execution context。依赖Protocol、Process/Transport/Caller/Repository adapters、各Module的recover Ports；没有UI Query/全Store扫描依赖。

所有worker/SDK/订阅/平台回调都有唯一owner和generation；启动失败回收本generation已创建资源。重启限额用06的固定退避；不会因Query失败重启Runtime。退出不推定外部工具已死，先关闭新准入、按现行stop/receipt处理；未结事实保留。OS/凭据不适用的宿主返回明确capability unavailable，而不是调用另一条本机能力旁路。

## 依赖闭合规则

M02→M03/M04/M11；M03→M05/M06；M06→M07/M08/M09；M09→M10/M05/Provider；M11→M06/ReportSource；上述均→其必要M13 Ports。M12只→ReadRepository/pure projector/受限LiveObservation，不反向供命令授权。M14装配这些公开Ports；任何“当前状态”回读必须命名且有界，不能注入完整Module作为捷径。

M09的委派Provider是外层Adapter，向M02/M03提交已准入命令；反馈走原持久事件和当前kernel，不持锁递归等待。报告来源读取不能回M11。本轮明确这两个合法反馈与非法读取递归的区别，导入规则和真实调用trace都必须验收。

## 既有 Feature Modules：分别拥有事实，不建立总 FeatureService

以下F编号只是审查/路由身份，对应已有独立服务；不新增一个switch分发全部功能的大Module。现行411项方法的参数与返回逐项绑定原Protocol/preload合同，写方法统一附CommandKey/expectedSource并遵守01。引用共享M13持久化不意味着M13拥有业务政策。

| ID / 现有责任 | 公开Interface（现行typed request/result） | 数据归属 / 依赖 | 队列与异常恢复 |
|---|---|---|---|
| F01 Project/Bot/Workspace Lifecycle | `applyProjectChange(key,request)`、`readProjectSource(ids)` | registry/profile/workspaces/linkedFolder；原Lifecycle kernel、M10主体、M13，不含执行进展 | QA/QS；CAS，创建半应用按原创建回执恢复，删除保留原任务/引用级联规则 |
| F02 Conversation/Selection | `applyConversationChange(key,request)`、`applySelectionChange(key,request)` | 原会话meta、显式编辑、引用子会话、selection draft；M13/M10/原user command policy | QA/QU/QS；禁止流式回写全历史；精确目标/版本冲突返回，不复活已删除占位 |
| F03 Resource Workspace/Interactive Results | `applyResourceChange(key,request)`、`inspectResource(key,ref)`、`readSnapshot(ref,revision)` | 原resource draft/version/修改/发布与交互回执；M09受限能力/M10/M13/M14 | QA/QX/QS/QB；按原writer/CAS/发布原子性，失败原draft/版本可读，未知写入先对账 |
| F04 Configuration/Model Catalog | `applyConfigurationChange(key,request)`、`fetchProviderCatalog(key,request)`、`resolveRole(request)` | settings/developer/provider/model/locale/shortcut配置；原83解析、M08 network/credential Ports、M13/M14 | QA/QS/QB；保存成功后发revision，读不提交默认值；secret只经staging，失效配置可独立编辑 |
| F05 Memory | `applyMemoryChange(key,request)`、`curate(approvedWorkRef)`、`readSource(refs)` | 原MemoryItem/episode/provenance/switch；原81准入、M06 curator/M07 Source/M13 | QA/QT/QS；冲突/撤销/关闭当前gate重检，失败不把候选记忆写入system；不启用Proposed123 |
| F06 Objectives/Watch | `applyObjectiveChange(key,request)`、`handleWatchSignal(ref)` | 原Objective/watch/probe回执；原82自主档位、M02受准入输入/M06 probe/M13 | QA/QW/QT/QS；丢通知从原watch cursor补，观测不等于新授权，取消/重启不重复探测副作用 |
| F07 Automation | `applyAutomationChange(key,request)`、`trigger(key,request)`、`readRunSource(ref)` | 原device定义/run/overlap/missed与Grant；原Automation kernel、M02/M06/M10/M13 | QA/QW/QT/QS；原run identity幂等，超时/关窗不重启已未知执行，按原回执恢复 |
| F08 Integration Catalog/Lifecycle | `applyIntegrationChange(key,request)`、`performCatalogRequest(key,request)` | 原MCP/Skill/Plugin配置、manifest与安装/凭据引用；M09受限管理Provider、M07 Source注册、M13/M14 | QA/QX/QB；安装前后完整性/失败回执保留，Manifest刷新不绕Projection，不把外来内容变system指令 |
| F09 Attention/Read Cursor/Delivery | `markRead(key,request)`、`surfaceCommittedEvent(ref)` | 原readCursor/通知去重/交付事实；原surfacing policy、M13/M14、纯attention projector | QA/QS/QE；只读游标不签收任务；通知丢失不重放模型，恢复保留草稿/注意力 |
| F10 Usage | `recordProviderUsage(producer,record)`、`readUsageSource(query)` | 原权威usage request/未知计量；受信M08/原计量、M13，不信Renderer造usage | QS/QP；按原requestId去重，校正可重投影，未知保持unknown，不生成账单结论 |
| F11 Input Prediction | `predict(request)`、`validate(request)`、`cancel(requestId)`、`status()` | 原短期内存候选/请求代次，不拥有用户draft/正式输入；原115/预测kernel、M07预测profile/M08空工具认知Port，M13仅原有界来源读 | QG请求容量/QT背景认知许可，每宿主最多1个预测、无过期等待队列；不启动AgentTurn/Task；关闭/换draft立即失效，validate不调模型，不自动发送 |

读接口直接进入03相应有界View；仅feature source读取Port供M07/M12使用，不能回调其完整写服务形成递归。每个F模块只依赖自身原领域kernel、必要M Ports及Repository；F之间不互持对象。F01删除等跨领域用例由原编排以step receipts调用各owner，不在Repository里隐含业务级联。

M08.completeCognition保留原completion/ADR115空工具面与角色/项目/隐私预算；使用原cognition request/dispatch身份，不伪造Agent attempt或messageId。M07预测profile只按ADR115准入已允许来源/continuation草稿，不持久化草稿/候选快照；M08的通用Provider trace对此请求仅metadata。QT共享在途预算只计资源许可，不把预测变成领域任务。

## RI-00续证后的入口审查要求（2026-11-12）

自然profile补到`runner.pump → runner-coordination.selectNext → pending/recoverySelection → resolveRoster → Supervisor.list`，以及`F11.readSnapshot → BotDirectory.get → projectRow → Supervisor`。两者是当前实际依赖，不能因不属于UI查询而漏迁。此处登记证据与复审门，不宣称新Interface已经完成实现或验收。

重开后的源栈进一步确认`runRounds → turnFacts/rows`及`runRounds → readSlot`也进入roster；不要只收窄repair入口。GoalPlanStore与Desktop host facts的UI-delivery端口分别审查，不能由一个缺失推断另一个缺失；本次打包现场实际provider为null，dev/preview的活动authority仍按其原UI/Evidence owner保留。

- M02/M03所需roster是原kernel的执行/托管/控制事实，归原事实owner及M13读Port，不能改成依赖M12的UI派生页；不得以缓存needsYou或旧列表批准调度。进入实现前列出所有roster消费者的实际字段闭集、当前source/ownership/unknown与版本失效行为，保留修复custody、等待子任务、暂停结算、缺失session及重启后的语义；不注入完整Supervisor。
- F11在模型准入前的snapshot也必须计入QG/QT/M07/M13预算，不能同步调用完整Bot呈现列表。沿ADR115已允许的主体/profile、结构化未决门、当前runner活动和公开历史Source取得版本绑定事实；缺失/旧代次/版本变化返回none或原unavailable，validate不调模型。草稿/权限/ToolResult/Evidence边界不变。
- 两条链须在RI-01前自上而下复审完成，给出明确端口/字段/批次、容量/取消与故障恢复；本次仍在RI-00取证，不能将这份复审要求误记为已完成详细设计或直接开始代码重构。
