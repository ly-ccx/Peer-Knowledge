# 01 协议与命令交付

创建时间：2026-11-11
最后更新：2026-11-11
状态：详细设计候选；引用 [ADR128](../../decisions/128-local-runtime-isolation-and-bounded-query-contract.md)。

## 1. 通用类型与验证

`Id` 为 1–128 字节 ASCII opaque token，字符 `[A-Za-z0-9_.:-]`，拒绝 `..`；现有允许更长的 executionEpoch/外部引用保持原 Protocol 上限，不强行改写。`Digest` 为 64 位小写 SHA256。`Revision` 为原 Store 的 opaque version；不可转成时间排序。跨源版本按 `{kind,id,version}` 升序排列、无重复，最多 32 项，超过时使用宿主签发的 `snapshotRef`，不截断。

```ts
type HostRef = { hostId: Id; generation: Id; dataRootId: Digest };
type CallMeta = {
  protocol: 1; connectionId: Id; requestId: Id;
  target: HostRef; budgetMs: number;
};
type VerifiedCaller = {
  connectionId: Id; source: 'desktop'|'quick_chat'|'tui'|'cli'|'remote'|'runtime';
  actorRef: Id; scopeRefs: readonly Id[];
}; // server-created, never copied from client payload
type CommandKey = { method: CommandMethod; scopeRef: Id; operationId: Id; digest: Digest };
type QueryScope =
  | {kind:'application'; section: ExistingApplicationSection}
  | {kind:'workspace'; workspaceId: Id; parentConversationId?: Id; entityId?: Id};
type Fault = { code: FaultCode; phase: string; operationRef?: CommandKey;
  retry: 'never'|'read_again'|'lookup_receipt'|'after_refresh'|'after_recovery';
  source?: SourceVector; retryAfterMs?: number; detailsRef?: Id };
```

Payload 的 workspace/parent/entity 只是目标选择；Gateway 按注册连接、原 registry/profile/父子关系解析 scope，不因 caller 自报角色、路径、hostId 或 commandId 放行。Electron Main/Query/IPC 与原生 Rust Core 共用 schema（`packages/protocol` 单一真源），验证字符串字节数、数组长度、深度（最多 16）、整数溢出、枚举和未知字段。受保护对象引用沿原 schema，不能用用户路径替代 objectRef。

actorRef是Gateway解析的稳定授权主体，不是connectionId/window generation；本地用户在同一Bot主体下Desktop/TUI重连取得同actor，来源窗口/角色另作审计并逐次校验。remote使用原认证主体，不因相同operationId接管本地主体。客户端在原device ClientState保存未获最终回执的CommandKey；新连接先重新认证同scope后lookup，旧request响应丢弃不妨碍查已接受命令。UUID相撞且digest不同仍拒绝，不按窗口重新生成operation绕过幂等。

Transport schema 1 与 canonical schema 分开。握手必须精确支持 protocol 1、方法目录 revision 1 和当前 writer/reader 能力集合；不支持返回 `PROTOCOL_UNSUPPORTED`，不做 permissive JSON 或旧同步回退。握手只暴露数据根摘要、版本和公开方法能力，不发送凭据、真实根路径或任意 service 名。

Wire 分四种 envelope：`request/response`、`commandReceipt`、`factInvalidation`、`activityFrame`，分别解码；没有 `emit(name, any)`。factInvalidation区分canonical source与presentation source；原窗口外观/尺寸事件绑定已注册window generation/revision，不伪装canonical commit。最大控制帧 64 KiB、普通命令参数 64 KiB、查询响应 256 KiB、activity 帧 32 KiB；大输入/附件沿已有受限 upload/resource staging 得到 immutable ref，再在命令中引用。正文总量不因信封上限被裁断。

## 2. 公开方法目录

方法只能进入命名 handler。以下 `Payload` 复用同名现行 Protocol 对象，新增字段仅为 `operationId/expectedSource`，UI 无法传 execution authorization。每个已迁移写入方法都经统一 command journal；表中不允许任意 method 字符串继续下派。

| method | 接收者 / 权限来源 | Payload → Result（不含 envelope） |
|---|---|---|
| `input.submit` | Input/Work；已注册本地用户或原受限 remote scope | `ProjectInput`（附件 refs）→ `InputReceipt{inputId,messageRef}` |
| `pendingInput.stage/claim/clear` | 原本地重启输入owner/M02 | `stage={PendingTaskRef,expectedRevision}`；`claim={expectedRevision}`；`clear={expectedRevision,reason:input_committed/user_discard,inputReceiptRef?}` → `PendingInputHandoff/HandoffReceipt`；committed必须附匹配回执 |
| `work.control` | Work Coordination；现行 work 控制权限 | `{workId,kind:pause/cancel/resume,expectedSource,authorityRef}` → `WorkControlReceiptRef` |
| `session.control` | Session Control；原 `SessionControlOperation` 准入 | `{sessionId,kind:pause/cancel/takeover/resume,expectedExecution,authorityRef}` → `ControlOperationRef` |
| `approval.decide` | Authorization；合法批准界面/现行 TUI，remote 仍受原限制 | `{approvalId,decision,expectedRevision}` → `ApprovalDecisionReceipt` |
| `policy.update` | Authorization；当前 Bot 本地用户主体 | `BotAccessPolicyUpdateRequest` → `BotAccessPolicySnapshot` |
| `obligation.decide` | 原义务/claim owner；原人工或 bot_verified 政策 | 原 grant/decision/expected claim identity → 原义务/闭包回执 |
| `verification.request` | Verification；原用户/受准入运行时 | `{sessionId,sourceRevision,criteriaRef,authorityRef}` → `VerificationRequestRef` |
| `result.accept` | Acceptance；原人工/政策签收权限 | `{sessionId,sourceRevision,verdictRef,expectedSource,authorityRef}` → 原 acceptance receipt |
| `project.change` | 原 Project/Bot Lifecycle；本地管理权限 | discriminator 为 create/update/archive/delete + 原 payload → 原管理回执 |
| `settings.change` | 原配置 owner；原设置/模型路由/目标/记忆修改权限 | 固定 submethod + 原 typed patch/CAS → 原配置/记忆/目标回执 |
| `resource.change` | 原资源编辑 owner；具体对象与版本权限 | 原 ResourceEdit/interactive publication command → 原修改/发布回执 |
| `resource.inspect` | 原受限用户资源/能力Provider | 原resourceRef/范围/预期版本 → 已物化ResourceSnapshotRef；仍经能力链 |
| `integration.perform` | 原MCP/Skill/Plugin/安装管理Provider及角色准入 | 现行catalog中固定操作 + 原typed参数 → 原操作回执/refs |
| `clientState.read/save` | Gateway ClientState Adapter | 固定kind=`draft/readingAnchor/layout`、自身key与CAS → 表达状态/保存回执；不进command journal |
| `client.bootstrap/presentation.perform:<exact-channel>` | 原本地窗口owner/Gateway | 冻结清单的原窗口/连接typed参数 → 原表达回执；绑定window generation，无业务接收日志 |
| `command.lookup` | Command Journal；原调用方或同 scope 的受准入诊断 | `CommandKey` → `CommandReceipt` |
| `query.run` | Query Service；已验证 scope | `ViewQuery` → `ViewPage`，见 03 |
| `query.cancel` | 连接自己的在途读取 | `{requestId,generation}` → `{cancelled:boolean}` |
| `view.subscribe/ack/unsubscribe` | 连接自己的 scope | `SubscriptionRequest/ackCursor/id` → `SubscriptionReceipt` |
| `activity.attach/detach` | 已授权 attempt/conversation | `{attemptRef,afterFrame?}` → 流式帧/重连结果 |

`project/settings/resource.change/integration.perform` 与 `existingCatalog:<exact-channel>` 是[现行411项catalog冻结映射](ipc-route-inventory.json)中的精确方法枚举；后者每项都是独立schema-bound方法，不是接受任意method/payload的fallback。参数/结果使用清单绑定的现行Protocol/preload合同，另加expectedSource；有原显式用户修改的保留原语义，没有向Renderer开放任意patch。该清单固定各项目标Module/contract与角色策略；源catalog增加操作必须先更新规格。业务入口由原Feature owner处理，不让客户端直接调用M13 Repository。

Application scope的section闭集为原settings/providerCatalog/registry/usage/diagnostics/clientState/activeHost/automation/pendingInput/tasks，需原本地角色；remote只看原允许workspace交集。section只选择原服务的读取范围，不新增方法权限。工作区scope与application scope不能互换。`conversations:add-usage`收紧为受信Runtime的原Provider usage producer；`client-tool:execute`的原已认证Gateway投递迁入本地Host，Renderer不再作为执行投递者。原角色快照和两项新targetRolePolicy在清单分列，模型能力/Grant政策不扩大。消息替换仅原显式用户编辑/重发/删除入口，必须CAS且不能把UI流式列表回写成ToolResult/Evidence/新执行占位。

旧产品响应存在完整Plan/History数组的，前端消费者必须迁到03的有界View/refs；不能因兼容旧响应而在新服务背后重新全量hydrate。`settings:get-sync`仅允许main已保存的≤64KiB locale/theme/窗口bootstrap镜像，附source/asOf，缺失返回unavailable并异步补读；不读Store或Provider。其它sync项只操作已注册窗口/拖动状态，不做业务I/O。

Secret输入走Broker私有staging：返回一次性opaque secretIntentRef，命令日志只存该ref和非秘密元数据，明文及可离线猜测的secret digest不进日志。重启丢失staging时返回NEEDS_SECRET_INPUT并查原Vault/Provider回执；不能用空secret执行或普通payload持久化。用户密码库的显式reveal/fill沿06的独立window-scoped通道，不能进入普通Query/Activity。

敏感配置的wire变换固定为：`llm:add/update/models:fetch`的整个原配置对象（含apiKey/customHeaders），`mcp:put-credential`的整个原secret/oauth对象，`mcp:upsert-server`的整个原env/headers对象，`password-vault:upsert`的整个原password对象，先在原允许window的Broker入口验证并staging；公开command仅携带opaque ref、id/非秘密选择项和expectedSource，不把这些对象先交Gateway算digest。`settings:import/export`仍原生文件选择/原导入器，journal只存操作与导入/导出回执ref；解析正文不进入普通command/Query。OAuth code/token、站点导入cookies等原平台内部材料也仅在原私有Adapter流转，原公开命令只能选择已登记source/site refs。此处是对旧preload中宽Record/secret字段的明确wire覆盖，不声称原参数原样持久化。

宽`Record<string,unknown>`的配置入口不作为新协议的任意字段许可：Provider私有表单字段集合固定为当前Protocol `LlmProviderConfig`去除`id/groupId/createdAt/resolvedWire/customHeadersInvalid/connectionState/connectionStateReason/configVersion/lastCheckedAt/lastSuccessAt/lastErrorCategory`，另允许原apiKey和`clearSecretParts`；已有id/groupId仅在原update/add-model目标位置保留。secretIntentRef只在staging后的公开command。clearSecretParts是无重复、最多6项的枚举数组，闭集`providerCredential/providerHeaders/mcpCredential/mcpEnv/mcpHeaders/vaultPassword`，每个方法只能使用自己对应项；缺省保留、显式列项清除、有新值替换，同一项clear与新值同时出现拒绝。modelOptionValues/customHeaders/env的字典仅按原声明schema及本协议总字节/深度限制处理，不成为任意RPC。公开View的secret、OAuth token、env/header值只给configured/key元数据；省略旧secret值表示保留，明确clear才清除，不能用masked占位覆写。所有原有秘密解析仍在原credential/config owner，不增加新的导出接口。

InputPrediction的predict/validate/cancel是原ADR115可取消的建议request，不是耐久业务command，不把每次草稿网络请求写进command journal；使用requestId/源draft revision判定重复与过时，Provider usage仍由F10记录。它没有工具或自动发送权限。ClientState与该类派生request不拥有任务、Grant或验收事实，不因省略journal产生执行旁路。

窗口尺寸/ready/返回ack/WebContents注册等只改变表达/连接状态的精确清单项为presentation-request，使用QG/QB/QE和原窗口身份/代次，重复请求按该窗口revision处理，不以command journal持久化每帧布局。关闭连接可结束这些请求，不取消业务。`chat:stream:reattach`只进入activity.attach；`quick-chat:submit`进入input.submit。真实OS效果、配置、输入、任务、授权、发布仍是受准入command，不能借presentation分类绕开执行链。bootstrap只返回当前已认证连接与有界镜像/refs，补读由Query异步完成，不在main构建完整配置/历史。

内部wire方法闭集为 `runtime.dispatchTurn/invokeCapability/reconcile/readLiveFacts/assertInvocationCurrent/assertCredentialRequestCurrent`、`platform.register/invoke/lookup/nonce`、`store.prepare/commit/lookup/appendHistoricalObservation/readSource`、`projection.catchUp`、`host.progress/cancelComputeJob`；各Module的其它同进程Ports不自动成为wire方法。Runtime只可调用其必要platform/store；Query仅readSource/catchUp；Platform仅必要assert与原调用historical append；Storage不能调用模型。它们不进入renderer preload、remote methods或模型工具目录。模型仍经Manifest/Projection见到原工具。

## 3. 命令的耐久交付与幂等

接收有四个不同事实：`received`（只到内存）、`accepted`（journal 已提交）、领域操作已提交、实际执行/验证/签收结果。Transport 只报告前两项与领域回执引用，不把一个 command 的 applied 解释为任务完成。

```ts
type CommandReceipt = {
  key: CommandKey; receivedAt: string; acceptedAt?: string;
  delivery: 'accepted'|'dispatching'|'settled'|'needs_reconciliation';
  owner?: HostRef; domainReceiptRefs: readonly Id[];
  outcome?: 'applied'|'rejected'|'superseded'|'cancelled_before_dispatch';
  fault?: Fault;
};
```

1. Gateway 验证 caller/scope/schema/容量，计算规范参数 digest。digest 包含 method、principal、scope、expectedSource 和完整参数；规范 JSON 按 key 排序，禁止 NaN/undefined/重复 key。requestId、重试时间不在 digest 中。
2. journal 唯一键为 `(actorRef,scopeRef,operationId)`。同键同 digest 返回原 receipt；不同 digest 返回 `IDEMPOTENCY_CONFLICT`。跨连接重试必须复用 key，不能重新生成 operationId。
3. journal 事务写入参数/immutable refs、来源身份、接收序号、`accepted`，fsync 后才回 accepted。容量满/磁盘故障不伪造 accepted。接受前丢连接的结果是客户端未知，必须 lookup；“未收到 ack”不等于未接收。
4. 当前项目 lease owner 以 CAS 认领 `dispatching`；每个聚合只允许一个正在提交的 command step。领域入口在首次副作用前使用原 operation/dispatch 身份。工具和模型派发仍走现行 durable dispatch receipt，不能靠 command journal 自行重放。
5. 领域提交成功后，journal 保存原 receipt ref/版本并 settled。多步操作保存 step receipts；不是跨 Store 原子事务。某步结束不使其余步骤被推定完成。
6. 崩溃处于 dispatching 时，恢复先查领域 receipt/目标身份/原 dispatch；有确证则补 settled，无派发确证且领域入口有原幂等保证则续原 operation。效果不明则 `needs_reconciliation`，交给原 owner 的对账接口；不自动再发模型/工具。
7. 设置类旧入口缺 operation receipt 时，当前值恰好等于期望值只能返回 `desired_state_present_attribution_unproven`，保留操作历史；重新操作必须用新 observed revision，不能把相等值当成原操作成功证明。该不确定性只约束该修改，不冻结无关任务。

普通 command 的 budget 仅限定“接收/入队/响应”，不限制工作总轮数。超过响应 deadline 后服务继续持有已接受的 operation，客户端查 receipt。撤销接收需要显式 control command；断开连接不是取消。

## 4. 查询、订阅与 Activity

`ViewQuery={view,scope,filter,cursor?,limit,byteBudget,afterSource?}`；`ViewPage={availability,source,items,nextCursor?,hasMore,asOf,liveObservation?}`。view 与 filter 是 03 中的 discriminated union。cursor 编码 view/scope/filter digest、snapshot generation、稳定排序位置与 schema，≤2 KiB；签名由设备 Query 进程的短期 key 生成，服务重启失效时返回 `CURSOR_EXPIRED`。重新取页保持用户锚点，不能自动跳底。

每条 subscription 固定 scope 与 view kinds；一次快照后返回 cursor。失效帧只含实体 IDs/范围和 canonical revisions，≤32 KiB。相同实体的失效可合并，不能合并/丢掉 command、approval、ToolResult/Evidence 或 canonical 事件。超过窗口先发 `gap`，客户端补读当前页后 ack；断线重连从原 canonical cursor 补读，不依赖内存通知必达。Query 本地事件序号不是 canonical commit 序号。

Activity 按 `(attemptId,executionEpoch,frameSequence)` 排序，保持旧重连缓冲与 sidecar 语义；同一帧不重复添加。订阅缓冲溢出发 `resync_required`，从受限 attempt 状态/已提交窗口重建。最终 done/error/aborted 只在原 terminal barrier 成功后发布；提交失败保留 sidecar 并返回本地持久化故障。

## 5. 错误和重试表

| code | 固定含义 / retry |
|---|---|
| `INVALID_REQUEST/FRAME_TOO_LARGE/SCOPE_DENIED` | 无业务接收，never；限制细节不泄露外项目身份 |
| `PROTOCOL_UNSUPPORTED/HOST_GENERATION_CHANGED/ROOT_MISMATCH` | 不继续旧连接；重新握手/明确升级，不同步回退 |
| `QUEUE_FULL/BUDGET_EXPIRED_BEFORE_ACCEPT` | 若 journal 确认无记录才算未接收；lookup_receipt，再按原 key 重试 |
| `DEADLINE_EXCEEDED/CONNECTION_LOST` | 查询 read_again；command lookup_receipt；工具效果不推定 |
| `VERSION_CONFLICT/POLICY_CHANGED/EXECUTION_STALE` | after_refresh，命令不自动改参数重发 |
| `INDEX_REBUILDING/INDEX_DAMAGED/CURSOR_EXPIRED` | read_again 或 after_recovery；绝不全量 main 回退 |
| `LOCAL_PERSISTENCE_FAILED/COMMAND_JOURNAL_UNAVAILABLE` | 未知提交点先 lookup/恢复；保留原结果和输入 |
| `NOT_PROJECT_OWNER/LEASE_LOST` | 按原项目宿主路由/交接；不抢占 active writer |
| `OUTCOME_UNKNOWN/RECOVERY_REQUIRED` | 原对账/控制政策；never 自动重放 |
| `HOST_START_FAILED/CREDENTIAL_UNAVAILABLE/NEEDS_SECRET_INPUT` | 保留原操作；按06先lookup，确证未派发才新操作补secret/配置，不弱存储/换宿主重放 |
| `CONTEXT_VERSION_CHANGED/CONTEXT_BUDGET_EXCEEDED/CONTEXT_CONTENT_TOO_LARGE` | 原source/attempt阻塞与受支持恢复，不静默裁约束或重发未知调用 |
| `COMPUTE_WORKER_STOP_UNCONFIRMED` | 只保留该计算许可，按实际worker身份恢复；不释放业务资源 |

Fault 诊断使用有界 detailsRef，不带原始堆栈、secret、绝对路径或用户正文。保留原 Store/Provider 错误 cause 的本地关联，不把磁盘失败改称模型失败。
