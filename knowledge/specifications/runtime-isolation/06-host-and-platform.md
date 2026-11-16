# 06 宿主、Platform Broker 与打包

创建时间：2026-11-11
最后更新：2026-11-16（与 ADR 129 / ADR 133 对齐：删除 TUI/Bun `--internal-*-host-v1` 与 Bun storage-worker 条款，收窄为 Desktop-only 过渡隔离及 Electron Shell ↔ 独立 Rust Core 进程接入约束）
状态：详细设计候选；本轮不启动、关闭、安装或重启用户应用。

## 1. 部署选择与启动入口

固定为每个 Desktop 宿主实例一组受管运行/查询边界，不能每 Bot 创建进程（TUI/CLI 已按 `ADR 129` 迁至原生 Rust，**禁止**以 Bun 启动 `--internal-runtime-host-v1` / `--internal-query-host-v1` 私有 JS sidecar）。过渡期 Desktop main 仅在有界查询/响应止损范围内使用受管 `utilityProcess`；按 `ADR 133` 终局时，Desktop main 直接启动并连接同一独立原生 **Rust Core** 进程及配套有界投影读取，不再建设另一套永久 TS Runtime 进程。

Desktop 与原生 Rust CLI 继续沿现有 `<dataRoot>`、`host.lease`、writer fence 与交接回执决定同一项目唯一执行者。存在现行可连接宿主或合法交接时按协议连接；不能连接或版本不兼容时由各自允许的模式拒绝冲突写入，竞争同项目仍由原 lease/fence 拒绝，不能降协议/强抢。同一数据根内跨进程仍遵守原有物理锁与配额约定；不同数据根不建立机器全局 daemon/锁，本版不声称能跨独立根限制整机总 CPU。业务 writer 仍每项目/聚合唯一。

这避免了把新的全局daemon选主/常驻安装混入本次重构。独立系统服务不是实现时任选项，本版明确不安装；退出/后台存活继续遵守原宿主产品策略。

## 2. Bootstrap 与 CallerResolver

```ts
startHost({kind:'runtime'|'query', dataRootHandle, requiredFeatures}): Promise<HostConnection>
handshake({protocol:1, methodsRevision:1, rootId, hostId, generation,
  bootstrapNonce, supportedCanonicalFeatures}): Promise<HandshakeReceipt>
registerBroker({brokerId,generation,capabilitySet}, privatePort): Promise<BrokerReceipt>
drain({scope,reason,deadlineMs}): Promise<DrainReceipt>
stop({generation,drainReceiptRef}): Promise<HostExitObservation>
recoverCandidates({workspaceId,cursor,limit}): Promise<RecoveryPage>
cancelComputeJob({jobId,generation,reason}): Promise<WorkerExitObservation>
```

dataRootHandle由既有DataStore resolver解析并realpath，rootId为canonical根身份摘要；Query不能创建/切换数据根。bootstrapNonce为256-bit一次性随机量，通过继承pipe/MessagePort发送，不放argv、环境变量、URL、renderer或日志。main注册实际spawn返回PID/启动身份；子进程回显nonce+协议/rootId/generation，5秒内完成，否则清本generation并返回HOST_START_FAILED。

Desktop renderer只接现行preload/IPC owner；Gateway验证注册window、顶层frame和精确本地origin，再创建VerifiedCaller。remote或受管桌面桥接只经现行网关认证、继承pipe/MessagePort与方法scope。没有未认证的localhost HTTP/WebSocket端点或新任意socket方法。外来数据里的UID/role/hostId从不构成身份。

runtime/query/store/platform各自有能力更小的连接角色，握手方法白名单不同：Query不能store.commit，renderer不能platform.invoke，Storage不能调用模型。协议/方法revision不匹配拒绝连接，不回到未校验旧payload。跨宿主交接通过原lease/control receipts，本连接generation只过滤迟到通信，不能替代lease或证明工具死亡。

## 3. 平台方法白名单

所有调用都属于已登记Capability Provider或原受限用户资源操作；Broker不接受通用`exec/eval/readFile(path)/getSecret`。Browser参数必须是当前已登记browser action union，不允许任意JS作为新增兜底。

| method | 允许输入 → 输出 | 执行/取消归属 |
|---|---|---|
| `dialog.chooseFile/chooseDirectory` | 原选择器过滤/多选配置、调用scope → opaque resource refs/取消 | 本地用户显式操作；modal不持锁，关闭窗口返回cancelled/unavailable |
| `clipboard.readSelection/write` | 已注册操作种类、具体selection/content ref → 原结果 | 原读取/写入权限与用户意图；无后台通用剪贴板轮询 |
| `browser.perform` | 原BrowserSessionRef+登记action+预期navigation/version → 原结构化观察 | WebContents owner校验；按原L1/L2能力可用性，不自动换宿主执行 |
| `capture.perform` | 原已登记屏幕/窗口目标与截图许可 → Artifact/Evidence refs | OS授权与Grant各自校验；无权限返回原错误 |
| `osPermission.inspect/request` | 固定OS权限枚举 → 原OS事实 | request仅原本地用户入口；OS允许不等于ToolGrant |
| `external.open` | 原允许URL/资源ref → 原打开回执 | 原scope/协议白名单；不暴露程序启动字符串 |
| `credential.acquire` | providerId、purpose=`provider_request`、当前cognitionRef/model selection → CredentialLease | 仅ModelAdapter专用私有连接；不存在UI/Query获取明文入口 |
| `vault.user.perform` | 原密码库list/reveal/fill/upsert/delete闭集、受准入window/ref与secretIntentRef → 原用户操作结果 | 只保留现有本地用户显式权限；reveal用一次性window私有通道，不进Query/模型/日志 |
| `platform.lookup` | 原invocation/dispatch identity → 已登记Provider observation ref或unknown | 不执行操作；不得用lookup触发第二次截图/写入/打开 |

新平台方法必须先经Manifest/Projection及protocol目录修订，不能在实现阶段选择“缺什么加个通用RPC”。

## 4. Invocation context 与真正准入

Ticket为两个互斥schema：CapabilityInvocationTicket用于实际本地能力，包含下述Projection/Grant/ToolCall/execution绑定；CredentialRequestTicket仅用于既有credential resolver内部的ModelAdapter→Vault seam，绑定provider/purpose/modelSelection/configRevision/modelDispatch与原cognitionRef（attempt或prediction/completion/catalogAuth请求），没有ToolGrant，不进入模型工具目录、不产生ToolResult或批准事实。后者走专用 `assertCredentialRequestCurrent` 只读准入端口；不能强行伪造一个ToolGrant或AgentTask访问模型配置凭据。两者都使用私有channel、generation/nonce/digest/HMAC和一次性消费。

Runtime先完成现行Role/Mode/Projection/Control/Lease/Resource/Grant检查并登记原dispatch，生成唯一invocationId。Broker为此invocation/requestDigest签发5秒有效的一次性nonce（以Broker本地单调时钟计）；Runtime在重检当前准入后，用私有连接key的HMAC-SHA256绑定 `{brokerGeneration,invocationId,dispatchRef,requestDigest,nonce,principalRef,projectionRef,grantRef,execution,policyRevision,controlRevision,leaseEpoch}`。

Broker验签、nonce未消费、digest/方法/范围/generation一致，并通过单独的保留控制端口 `assertInvocationCurrent(invocationId)` 取得当前准入确认，然后立即消费nonce/执行。该端口只读取当前小型准入事实，不依赖正在等待Broker的AgentTurn，也不持聚合锁，避免回调死锁。连接失去Runtime或nonce过期则不开始新执行。

Ticket不是PermissionGrant，只绑定同一已批准调用与运输身份；Broker不能用timer或签名代替Runtime当前Grant检查。已开始的平台执行遇到随后取消/降权，沿原句柄取消/结果收口；物理外部效果不能被倒推为未发生。

Broker的Provider在原dispatch identity下保留实际started/ended/result observation，结果通过同一ToolResult/Evidence commit port耐久保存后才回result ref。Runtime崩溃时仍可提交原调用的历史观察，不能用该权限写当前Plan/控制/释放新claim。若保存失败或Broker也消失，lookup返回unknown，按原对账；不得重放外部效果。原Evidence登记规则与结果真实性不改变。

## 5. CredentialLease

credential.acquire只由合法ModelAdapter请求，固定providerId/purpose/cognitionRef并检查配置/主体及CredentialRequestTicket；有attempt时另绑定attempt，不给纯预测伪造执行身份。Desktop经既有Vault/credential-helper协议获取（原生CLI/Rust Core走ADR 0001 / ADR 132 Helper v1/v2边界）。不适用的OS返回CREDENTIAL_UNAVAILABLE，不将明文写入临时文件或改用弱存储。该端口只解析已配置凭据，不是新本地能力执行或模型可见secret工具。

Lease通过ModelAdapter私有channel提供最小凭据材料，只在内存保留至请求组结束，打开新请求的有效期最长60秒；这不强行中断已建立SSE。Provider要求刷新时重新走原OAuth/credential seam。取消/配置删除后不启动新请求，释放引用并按可行范围清零byte buffers；不声称JS字符串完全可擦除。日志/command journal/Query/Context snapshot永不保存secret。模型切换不能继承另一provider的lease。

API/OAuth凭据与用户密码库的既有显式reveal是不同合同。后者仅在原允许window/用户操作下返回，填充绑定指定Browser对象；不因Runtime拆分扩大到模型/远程/通用读取。secret staging最多32项/1MiB、60秒，绑定connection/window/operation并一次性消费，未使用时清理内存；过期须用户重新提供，不自动取另一条secret。

staging在command accepted后失效时先查原domain dispatch：能证明未派发才以NEEDS_SECRET_INPUT拒绝该命令，用户重新提供时创建新operationId；已派发或不明只lookup/对账，不能在同operationId替换secretIntentRef改变digest。普通窗口开关/拖动等原UI操作使用原window身份与固定方法，不伪造工具执行回执；模型发起的本地能力始终使用CapabilityInvocationTicket。

## 6. 生命周期、故障与退出

启动顺序：DataStore与schema只读检查 → M13/权威库校验 → Runtime私有握手/资源连接 → 各项目原lease/fence → M04/M05 pending control/资源 → M02/M06/M11未决候选对账 → 本项目开放新准入。Query独立启动/重建，不成为输入草稿/可见交互的全局门闩；UI可以显示数据暂不可用，但不得假装任务已恢复。

Query崩溃只重启Query，退避1s/2s/5s，60秒内最多3次，之后结构化unavailable和显式重试；Runtime崩溃按同退避但每次先执行原恢复，不能因启动成功自动重发模型/工具。Storage worker失败由原operation lookup决定重prepare或对账；Platform失败不自动替换调用宿主。启动超时和已做的副作用单独记录，保留失败候选。

退出：先关闭新command/dispatch admission，保留lookup/控制/读取 → 原control drain与terminal barrier（默认30秒）→ 取消纯查询/重建 → 等已开始的原子提交/记录未结ref → dispose subscriptions/SDK/worker → release原lease（只有合法交接）→ 关闭私有ports。到期限不把unknown强改settled；显式用户退出可结束受管进程，但记录/原claim保护保留。只取消工作不退出整个Runtime。

worker与host的recorder保存真实bootId/pid/pidStart/hostId/epoch。main死、Runtime死、worker死和外部工具死分别是不同事实；不得拿父PID替代实际执行者证明。

纯CPU/rebuild job每完成1MiB或1秒报告progress cursor；10秒无进展或客户端已取消且无其他等待者时，Host取消该registered job，先请求停止、2秒后终止该受管纯worker，再等3秒实际exit。只有exit确认才回收compute permit；无法确认返回COMPUTE_WORKER_STOP_UNCONFIRMED，仅阻塞该计算许可并给明确Host恢复入口，不触碰业务claim。该机制不能用于杀尚在canonical commit的Store进程或推断工具已停。stream tokenizer每16KiB检查一次片预算/取消，不因一个巨大scalar一直占用worker消息循环。

## 7. 跨平台构建与资源实现

Desktop过渡期若启用`utilityProcess`查询隔离，须固定打包静态入口并校验asar清单哈希；Worker只eval构建时生成的静态已校验source，不eval模型/文件内容。Node/Electron CPU worker受192MiB heap预算约束。按`ADR 133`接入独立Rust Core进程后，核心运行时与存储worker能力由自包含的原生Rust二进制承担，Windows/macOS/Linux均封装为受管继承pipe/MessagePort或私有受控本地信道，不假设额外POSIX FD可继承。任何不支持的打包/IPC/worker能力必须使该平台候选失败，不能实现时降级在main同步执行。

过渡期SQLite与Store读写维持现有Adapter不引入第二数据库；终局随`ADR 131` / `ADR 133`统一至原生Rust Store与同一物理锁/CAS语义。共享计算许可在原设备资源库的独立table，以真实worker身份占用4槽、generation/退出回执回收。

每宿主固定两个Store写入边界，控制1个、普通1个；M13 AggregateCommitScheduler只持轻量ref并确保同aggregate只有一个实际commit。它们独立于Runtime/Query生命期，具有更窄Store方法白名单，可在Runtime失联后保存原调用历史结果/提交事实，不能开始新执行。CPU/prepare在共享QR pool；Store写入边界不承担全历史解析或索引重建。不同宿主仍以原物理Store锁/事务排序，不新建全数据根业务互斥。

macOS签名/notarization和Windows/Linux包都要验证真实spawn、SQLite、凭据可用性、child退出、取消、asar入口和恢复。设计已固定Adapter选择；这些是实现验证项，不是留到实现时再选体系。
