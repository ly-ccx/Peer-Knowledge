# 05 存储、提交与已有状态恢复

创建时间：2026-11-11
最后更新：2026-11-11
状态：A 级详细设计候选。新增设备内command交付日志与计算许可属于ADR128明确新增的边界；不建立第二份任务/权限/Evidence真源。

## 1. 物理归属与注册

| 数据 | 逻辑owner / 写入口 | 物理位置与scope |
|---|---|---|
| 命令接收/交付/对账 | M01 Command Delivery | `project-runtime/command-delivery.sqlite`，device，新增DATA_STORE_ENTRIES项 |
| Work/Intent/Control/dispatch等 | 原各M02/M04等owner | 原每项目coordination-v2及其manifest/fence，不改变真源 |
| GoalPlan/结果/核验/签收 | 原GoalPlan/M11 | 原goal-plans与其index/change journal |
| Conversation/sidecar/terminal | 原Input/M06/交付owner | 原conversations、stream sidecar和精确message identity |
| BotPolicy/Approval/Grant | 原M10 | 原policy/approval设备库与记录，不是cache |
| 资源claim/unknown/计算许可 | 原M05；计算许可独立表 | 原execution-resources.sqlite；新增compute_permits，不影响业务claim |
| 读模型/缓存/查询manifest | M12 | 03的cache/read-models/runtime-v1命名空间，cache |
| UI表达状态 | M00 ClientState | 现有input-drafts、draft blobs、布局/阅读位置；device，不是command或模型上下文 |
| 重启待发送输入 | M02 Input handoff | 原pendingTask文件保留；交接step/原InputReceipt引用在command journal，不因peek/claim先删除 |
| Runtime兼容能力/迁移回执 | M14 | `project-runtime/runtime-layout.json`、`runtime-migration/<migrationId>.json`，device，新增登记 |

新增权威库不由cache恢复器重建为空。command journal丢失/损坏返回COMMAND_JOURNAL_UNAVAILABLE，普通命令停止接收，原业务读/控制诊断仍保留；不能通过删除库制造“未执行”。资源库亦沿原对账/恢复规则。导出不携带设备许可/接收权威；备份SQLite使用consistent backup与WAL规则，不直接copy活跃主文件。

## 2. Command Delivery schema 1

固定表：`meta(schema,rootId)`、`commands(actor,scope,operationId PK组合,method,digest,receivedSeq,payloadOrRef,acceptedAt,delivery,ownerHost,ownerGeneration,domainRefs,errorRef)`、`steps(commandKey,stepId PK,dispatchIdentity,sourceBefore,domainReceiptRef,state)`、`receipt_events(commandKey,seq,kind,ref,digest)`。accepted/settled等只描述命令交付；任务/工具成败必须看domainRefs指向的原记录。

Node/Electron过渡期用现有node:sqlite Adapter，终局与原生Rust CLI按`ADR 131` / `ADR 133`共同对齐至Rust SQLite与同格式。`journal_mode=WAL`、`synchronous=FULL`、`foreign_keys=ON`，写者只在受控Storage写入事务执行。每事务最长20ms设计预算；忙等待不是20ms同步睡眠，使用timeout=0与04的异步退避。FULL fsync实际耗时不伪称可强制20ms，超预算记录并对控制队列隔离。

同key/digest事务幂等插入；认领需当前项目lease，CAS owner generation。原owner仍有活lease时不能“超时接管”命令。原owner失效后，新合法项目owner先reconcile其steps，再决定是否继续；普通读实例不能claim dispatching。没有项目作用域的设置命令使用原配置Store的CAS/锁，不授予项目lease。

## 3. Repository 方法目录

所有读/写异步返回必要事实/refs/CommitReceipt，不传整份Store状态。逻辑Owner只能调用自己的命名操作，私有prepared mutation不会进入客户端协议。

| Repository | 读取 | 写入/提交 | 原子边界 |
|---|---|---|---|
| Input/Inbox | `readPendingPage(workspace,cursor,limit)`、`lookupInput(inputId)` | 原`submit/consume/appendEvent`，保留inputId/eventId与消费cursor | 原输入与消息幂等、原cursor提交顺序 |
| Coordination | `readWorkHead/readControl/readDispatch/readRecoveryCandidatesPage/readAuditPage` | 原`commitCoordinationEvent`及owner命名控制/意图操作 | 每workspace原journal/fence/CAS |
| GoalPlan | `readPlanHead/readCriteriaPage/readResultRef/readReview/readAcceptance` | 原create/revise/control镜像/qualityReview/resultAcceptance；不暴露任意patch给UI | 原plan/version/索引提交与change事件 |
| Conversation | 原`listMeta/getWindow/readInteractionContext/readProcessPage/lookupMessage` | 原`append`、`patchStreaming`、准确`commitStreamingMessage`及显式编辑命令 | 原index→conversation锁序；terminal prepare/commit/barrier |
| Policy/Approval | 原`resolve/readPendingPage/lookupGrant` | 原`updatePolicyCAS/decideApproval/recordGrant/revoke` | 原policy/approval事务与revision |
| ExecutionResource | 原`inspect/readClaim/readReceipt/readUnknown` | 原reserve/activate/settle/close/reconcile；compute permit操作另列 | 原设备资源事务，不与project事务假装全局原子 |
| Evidence/Artifact | `findByRef/findByPlan/findByConversation/readBodyRef` | 原Provider result/evidence注册与artifact提交 | 原引用完整性与Evidence登记规则 |
| Feature stores | memory/objective/config/resource原typed读取 | 原各owner的CAS/版本化操作与回执 | 保留当前功能的schema/权限/导出政策 |

ReadReportSource读取原worker报告和criteria/evidence引用；不得调用完整Session.get/Acceptance。getWindow产品接口没有full=true。诊断full读取是单独授权入口，也受worker/分页/输出refs约束，不回main。

## 4. 锁与写顺序

1. 每个业务聚合一个逻辑提交队列，多个项目可并发。原Store物理锁仍是跨进程权威，内存队列不取代它。
2. Conversation沿现有index→conversation锁序；资源SQL事务不与Plan/coordination/file锁嵌套持有。跨聚合先释放当前锁，再按step receipt推进。
3. prepare读取source token、在worker做有界计算/临时文件；期间不持主线程会等待的锁。PreparedRef含operation/step、expectedVersion、temp handle与digest，只能由原owner验证，不包含完整history。
4. commit进入原短锁/事务后重检source、当前lease/writer fence/control与目标身份。相同版本才原子替换/提交，随后更新原index/contentRevision并清理匹配sidecar，最后发布commit receipt/revision hint。
5. 冲突丢本次temp，不丢canonical/sidecar；终态最多4次重准备且总30s，持续冲突明确失败。commit开始后不取消一半；取消关闭后续准入并lookup当前step。
6. command journal的accepted先于domain派发；domain receipt先于journal settled；terminal commit先于done/release；通知从不先于事实。其他跨Store步骤不宣称事务原子，按原idempotency/补偿协议恢复。

各Store保留自己的权威事件与原发布顺序；没有强行增加一个“全局业务outbox”替代已有日志。Query通知即使丢失也可从原index/journal version追赶。

Store写入分为 `StateTransition` 与 `HistoricalObservation`。前者始终要求当前lease/control/fence/CAS；后者只允许原已耐久dispatch绑定的Provider producer，在原call身份下追加不可变ToolResult/Evidence/handle观察，不要求旧执行仍有新派发权。它不能改Plan、Grant、Control、acceptance或释放claim。同observationId/digest幂等；同ID不同digest保留冲突诊断并拒绝成为已结算结果。该区分保证降权/失去lease后真实迟到事实仍可保留，同时旧epoch不能推进新任务；不是允许旧writer修改当前业务状态。

## 5. 大记录与内存

读取按1MiB byte块处理UTF-8和JSON token边界，不把完整journal或单条巨JSON先转成一个JS字符串。legacy大行使用流式tokenizer，跟踪嵌套路径/转义/数组索引并选择所需字段，将不需要的rounds/checkpoint正文按原字节范围跳过；必须验证完整JSON结构和record schema，不能只用正则抓字段或丢坏行。

交互/任务/证据投影使用此选择性解码；需要保留的巨值写现有受保护临时对象/原artifact handle，不跨进程clone。原canonical/native checkpoint格式与refs保留，不据此启用ADR113的CAS/GC。单个请求真的要求完整内容且超出context/heap预算时，返回 `CONTEXT_CONTENT_TOO_LARGE` 与原checkpoint/detailsRef；保留原attempt/工具配对，沿既有压缩/可用模型容量/明确用户恢复入口处理，不能截掉未知调用后重跑。

因此允许存在具体“该native checkpoint无法在现行容量下安全续接”的恢复阻塞，不允许整个应用卡住、不断重试、隐藏历史或清掉它。其他页面与无冲突新任务继续按原资源规则运行。

## 6. 崩溃点和恢复动作

| 崩溃位置 | 恢复时事实 | 固定处理 |
|---|---|---|
| journal accepted前 | 可能没接收/ack丢失 | 先lookup key；无记录才允许原key重发 |
| accepted后、domain派发前 | 原参数/refs在journal，未有dispatch | 当前owner恢复，验证准入后续同operation |
| domain派发登记后、Provider调用前后 | 原dispatch可能unknown | 查原receipt/句柄/127对账，禁止自动再执行 |
| domain已提交、journal未settled | 原domain receipt存在 | 核对身份/版本/digest后补settled，不再次执行 |
| 某step效果无法归属 | 有明确unknown | needs_reconciliation，原owner支持的对账；不能用当前值相等证明原操作 |
| terminal prepare未commit | 原canonical+sidecar仍在 | 清理本operation的temp，原准确messageId重prepare |
| terminal原子提交后 | 新canonical/version可验证 | 补index/receipt/通知，仅清匹配sidecar，不再发模型 |
| Query索引半建/损坏 | canonical未变 | 丢本次派生generation重建；权威库损坏不走此路径 |
| Control关闭准入后未停稳 | 原operation/claim仍未结 | reconcile原执行/recorder；unknown保留；不能新epoch覆盖 |
| worker/owner失联 | 无结束证明 | 关闭新准入，查实际句柄/worker退出；不只按timer释放资源 |

## 7. 兼容、旧writer与已有数据

新Transport/command journal采用schema1；所有新增Store条目先登记DATA_STORE_ENTRIES与备份/导出scope。每个迁移项目把现有coordination受保护writer floor提升为13（当前审查基线最大12）；旧reader/writer不理解13必须拒绝推进。13只在项目切到新Runtime写者前启用，不修改历史ToolResult/Grant/Evidence。若集成基线已占13，必须先修订本规格和ADR编号门槛，不能实现时静默换号。

runtime-layout记录schema1/protocol1/required feature set，不用于代替旧fence。cutover先drain当前项目、确认已登记旧宿主停止写入，取得原lease和物理fence，再提高floor与启用新owner；不自动关闭用户日用进程。发现仍活跃/身份不明旧writer则阻止该项目迁移并给明确owner/版本和受支持交接入口。旧非治理文件工具/旧经典宿主没有新floor检查的情形不能靠一个新manifest声称被围栏：迁移前必须静止这类写者；之后发现外部变更由强版本/原锁拒绝旧prepared commit并进入对账。不同版本并行写同一数据根不是受支持的迁移模式。

legacy记录没有command journal不需要批量伪造accepted；标legacy provenance，仅以原operation/原receipt恢复。旧completed但缺核验保留缺口，禁止回填passed。迁移新增读模型可以重建，原公开交互、控制和未知保护一条不少；读模型比较相同source版本，不双跑工具或命令。

旧pendingTask没有receipt时先检查原目标输入/dispatch身份；无法确定是否发送则保留handoff unknown，给原输入/对账诊断出口，不自动再发送。新claim中崩溃则查同operation/inputId；已接收补finish，确证未接收才续原inputId。坏/跨workspace记录保留隔离诊断，不沿旧helper静默删除。

保留旧canonical物理格式，新增日志只负责新命令交付。回滚前drain新writer并验证旧reader支持floor；旧reader不支持则只允许有原备份/受支持只读恢复，不能降低floor继续写。迁移回执包含源版本、phase、owner、floor、校验摘要与失败ref；phase为prepared/fenced/cutover/verified/blocked，重入按原migrationId处理。
