# ADR 119：用户停止、认知续跑准入与宿主收尾

创建时间：2026-11-03
最后更新：2026-11-07（文末说明已接受的 ADR 124 只收窄「不增加工具通道」草案中的三件义务工具。本文仍未接受）
状态：Proposed（用户要求先写完整 ADR；尚未批准实施，未改变运行行为）
级别：A（停止范围、认知准入、控制回执、持久恢复与版本契约），B（协调调度、Provider 重试及交付），C（同源状态表达）。

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[架构治理](../architecture/20-architecture-governance.md)、ADR [85](85-project-agent-hosts-inputs-and-surfaces.md)、[91](91-project-bot-autonomous-coordination.md)、[94](94-reply-attempts-silent-wait-and-recovery.md)、[95](95-progress-driven-execution-policy.md)、[99](99-authoritative-reply-receipts-and-model-recovery.md)、[102](102-unified-task-lifecycle-projection.md)、[110](110-follow-up-responsibility-and-current-list.md)、[111](111-project-agent-duplex-supervision-and-continuity.md)、[113](113-checkpoint-content-addressed-storage-and-retention.md)、[116](116-session-control-and-resource-settlement.md)、[117](117-intent-driven-coordination-and-goal-closure.md)。

## 1. 决策摘要

用户停止后，**保留收尾责任不产生继续调用模型的资格**。沿现有协调日志和 Session Control，补齐覆盖主 Bot 的持久认知准入屏障；停止、跟进责任、资源保护、历史执行结果与公开回执分别收口。

1. 停止当前回复、暂停工作、撤回工作、取消当前 Bot 全部在途工作有明确且不同的范围。范围内的自动认知从宿主耐久接受控制时关闭，不等停止回执、清理或模型总结完成。
2. `followUp.owner=bot` 继续表示 Peer 承担责任；不能再作为主 Bot 自动续跑条件。唯一生命周期投影同时说明下一步由模型、宿主、用户还是无人处理。
3. `stop_unconfirmed`、停止对账、资源结清、交付补偿由宿主确定性处理。它们不能进入技术返修列表、Provider 自动重试或目标覆盖复核来重新启动模型。
4. 模型请求、能力派发和结果交付都检查同一控制代次；旧事件、计时器、checkpoint、迟到结果及旧 `finally` 不能解除屏障。
5. 回复引用只建立事实关联，不能取得任务处理权。缺失 `origin.workId` 的旧会话通过既有 Session Control 收尾，不因被新取消回复引用就转成新工作的返修义务。
6. “已接收停止”“已封住新操作”“受管执行已停止”“委托已撤回”“历史结果未知”分别有结构化回执。取消摘要由宿主事实生成，助手文字不能声明其尚未成立的完成状态。
7. 撤回不清除未知调用、用量、产物、核验或 Evidence，不自动回滚或释放资源。执行停稳及资源交接继续遵循 ADR116。
8. 不增加模型监督者、第二个任务系统、权限系统或工具通道。日常只做内容/diff 审阅；最终发布候选执行完整验证。

## 2. 问题、证据与归因边界

### 2.1 本次现场

只读核对安装包 `0.1.0-rc.35`、规范 Conversation、coordination-v2 追加记录及检查点。下表使用北京时间；文件只记录定位所需的结构事实，不保存私有任务正文、机器绝对路径、凭据或原始工具内容。

| 时间 | 可确认事实 | 含义 |
| --- | --- | --- |
| 2026-11-03 09:15:43 | canonical 用户输入要求取消全部任务 | 本次有真实用户控制来源 |
| 09:18:02 | 一项子任务取得取消回执 | 不证明其他子任务或父协调工作已经收口 |
| 09:20:18 | 公开回复称全部取消且不会自行恢复 | 这是已发生的表达，不能作为控制事实 |
| 09:20:25 | 同一父 work 仍为 `runnable`，`repairSessionIds` 包含一条旧会话 | 公开取消回复没有关闭后续认知准入 |
| 后续检查点 | 旧会话 `status=cancelled`，同时 `followUp={owner:bot, reason:stop_unconfirmed}` | 待确认的停止责任被转换为模型返修责任 |
| 09:20:28—09:31:09 | 同一父 work 又执行五个模型回合；期间连接超时并自动重试 | 不是单纯界面状态延迟；没有新的 canonical 用户输入 |
| 09:31:09 | work 进入 `blocked_system/end=no_progress` | 最后由无进展保护停止，用户控制本身未形成完整屏障 |

可定位身份：workspace `6eaaec31-ea74-4ec2-999e-37f12ce7f478`，Conversation `ac44a8bd-2579-4cb3-8fae-6644a61e0921`，input `1b5a2d8b-a3e4-480c-8ec1-5ff81dad5db6`，父 work `work-42f1a299ada289c5b9b1c1bc84123a1acab16a81e5cc1cf92a05c1edd55fe8f0`，旧 session `7c10a13d-b459-494f-8b5d-03287d8043d9`。规范对话定位行为 1422—1433；协调追加记录全局 revision 4917 保存回复后的 runnable，4980 保存最终 no_progress。定位身份不是恢复授权或新的 Evidence。

这次能证明主 Bot 再次调用模型、查询和尝试控制；不能据此声称旧 Worker 已重新写文件、所有外部动作已停，或用户点击过“继续尝试”。现场输入是文字取消；停止按钮的独立作用范围由本 ADR 一并约束，不能冒称该按钮竞态已在现场复现。

### 2.2 已有机制与实际缺口

ADR110 已有撤回、停止未确认和唯一责任投影；ADR116 已规定先封准入、宿主确定性收尾与无变化不调用模型；ADR117 已区分根目标、回复与阶段责任。因此，本决策是这些契约在父协调认知路径的补全，不把现有系统描述成没有取消机制。

核对代码仓原工作树 `5f78fb7992e122549b7f762a276e5dd6d86ba127`、fetch 后开发线 `4a58e2846875f85de69915764a127096721c5b0d`，并直接读取 RC35 安装包中的对应模块。知识参考固定为 `origin/main=f952a447fc46a325f7c5b79267f35df21e5643b1`。这些身份只描述设计核对来源，不是本 ADR 的实现或验收候选。

| 代码锚点（相对代码仓） | 已确认行为 | 需要补齐 |
| --- | --- | --- |
| `packages/protocol/src/task-overview.ts:decideFollowUp` | 未决停止留在当前责任列表，owner 为 bot | 保守保留责任不能转换成默认可调用模型 |
| `packages/runtime-node/src/project-agent/repair-ownership.mjs` | bot 责任中除 live_execution 外均可进入 repairSessionIds | 区分语义处理、宿主收尾和事实不足 |
| 同文件 `ownedSessions` | 已报告 sources 可关联旧 session；旧记录缺 workId 时允许匹配 | 事实引用不能转移处理权；旧身份必须显式适配 |
| `runner-coordination.mjs:finish/recoverySelection` | 回复后可因返修责任重设 runnable，再由检查点恢复 | 统一检查有效控制、认知代次与合法触发原因 |
| `runner.mjs:stopResponse/completeStoppedTurn` | 原停止以活动 AbortController 和当前 turn 为入口；父工作还可能等待子任务 | 停止回复需要跨 attempt/重启的范围约束 |
| `work-control.mjs`、`session-cancellation.mjs`、`session-control.mjs` | 工作取消和子执行屏障已存在 | 衔接父认知、控制请求自身的收口和缺 workId 的旧任务 |
| `recovery-policy.mjs` 及 Provider 内重试 seam | 可重试失败沿既有预约继续 | 每次物理请求前重新检查控制，停止后不靠失败保护收口 |
| `reply-composer.mjs` | 校验 sources/statusClaims 等事实 | cancelled 字符串不能单独证明全部停稳；需控制摘要契约 |

## 3. 决策范围与非目标

适用 Desktop、TUI、CLI 共享 Runtime；远程入口只能提交其既有授权范围内的结构化控制，不能新增远程权限。覆盖主 Bot、Worker、Verifier、Explorer、目标覆盖复核、回复修正及其重试中**属于被停止范围的认知调用**。

不改变模型的目标理解与方法选择职责。自然语言取消仍由原主 Bot 回合理解并经现有协调能力提交；不增加关键词/正则分类器，不把收件箱事件或附件文字识别成用户控制。明确按钮/命令可直接提交其已有 typed 用户控制，无需额外模型解释或再次确认。

不自动回滚文件、删除 worktree、杀任意系统进程、取消其他 Bot、关闭全局模型服务或吊销用户全局 PermissionGrant。不暂停无关任务、输入预测等独立功能；这些功能也不能借自身入口恢复已停止的目标。新本地能力继续走唯一能力链。

## 4. 作用范围与恢复语义

| 用户动作 | 关闭的认知范围 | 执行及责任 | 合法恢复 |
| --- | --- | --- | --- |
| 停止当前回复 | 当前 work 的 replyChain：正文生成、自动修正、父协调续接及同链重试 | 保留原委托；已授权子任务按原边界继续，结果落盘但不自动启动该父回复链 | 用户显式继续该链，或新输入形成经校验的新处理决定 |
| 暂停这项工作 | 该 root work 的协调与专属执行后代 | 目标保留；Session Control 停稳受管执行，资源按 ADR116 处理 | 用户显式 resume，重新检查版本、资源、权限和预算 |
| 取消/撤回这项工作 | 该 root work 及其专属后代、返修、替换候选和恢复预约 | 撤回目标，停止收尾归宿主；共享依赖仅解除本工作的使用关系 | 不能普通 retry/resume 复活；需要新的真实用户委托，关联旧历史 |
| 取消当前 Bot 全部在途工作 | 接受控制时该 Bot 的当前根工作集合及各自专属后代；包含尚无 session 的协调工作 | 不要求逐项再次确认；根控制聚合子停止回执；无关 Bot 不受影响 | 新输入可建立独立新工作，不解除旧根的撤回 |

replyChainId 是跨重试/切片稳定的回复链身份，由宿主绑定既有 work/公开回复关系，不能每个 turn 新造 UUID 来逃离停止。新消息不自动清除旧停止：先允许新输入自身被处理；只有明确指向旧链的恢复决定才给旧链新代次。询问原因、查看历史不恢复执行。

“全部在途”包括当前根的 queued、running、waiting、retry_wait、返修和已准备替换；已签收历史保持原事实。当前 Bot 以 workspace/parentConversation 身份限定，不等同整台设备。共享依赖仍有其他有效使用者时不能被级联停止。

持续目标和独立定时计划不因“取消当前任务”被静默删除或永久关闭。与被撤回根绑定的触发器不能重建同一委托；独立长期目标若仍启用，回执必须明确其未来触发仍有效。用户要求连持续目标/定时计划也停下时，范围必须包含其既有 pause/close 控制引用，全部停止回执必须等待这些来源也被封住。不得在取消后用新 workId 将同一根自动重新委托。

## 5. 真值、Module 与 Interface

| Module | 持有的 Interface 与不变量 | Implementation / Seam |
| --- | --- | --- |
| 协调控制 Kernel | 工作/回复控制的来源、范围、单调代次、CAS 与最终处置 | 深化既有 coordination/work-control；纯 reducer 不执行工具 |
| Cognition Admission | `inspect/reserve/assertCurrent/settle`：按请求用途判断能否实际调用模型 | 共享 runtime seam；合并停止与调度准入，不做语义规划或签发 PermissionGrant |
| Session Control | 现有 request/reconcile/readFacts、StopBarrierReceipt | 沿 ADR116 中断并等待受管执行、处理资源保护；不另建取消器 |
| Coordination Runner / Recovery | 持久责任的选择、等待和续接 | 消费有效处理方式与准入决定，不能从 owner/state 单字段推导执行权 |
| Provider / Executor Adapter | 冻结请求身份、实际句柄、每次物理 dispatch、用量和结果 | Provider 内退避重试也通过同一准入 seam |
| Lifecycle / FollowUp Projection | 状态、责任、处理方式、合法动作 | 保持 decideLifecycle 唯一产品出口，查询无副作用 |
| Reply Delivery | 控制摘要、公开消息提交、补偿和历史保留 | 复用原 canonical 消息/outbox，不为通知启动模型 |
| Desktop/TUI/CLI | 提交 typed 命令，投影控制状态 | 不持有停止真值，不自行定时重试或读写运行账本 |

“停止执行”“还有谁负责”“能否调用模型”“是否允许使用某个能力”“能否释放资源”分别回答不同问题。不得新增一份 Task 状态表把它们压成 running/done；本决策的深度在于调用方使用统一准入及回执，不再自行组合停止标记、owner 和计时器。

所有模型发起的能力保持：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

宿主控制调用的取消/idle/句柄查询属于现有生命周期控制端口，只能处理已登记的本操作与执行体。收尾若需要新文件读取、Shell、MCP 或外部查询，必须另有仍有效的受治理任务/用户来源，并经既有能力链及授权；不能沿被撤回工作的旧执行资格开展新调查。缺少这些依据则保留具体阻碍，不能借“维护”建立执行旁路。

## 6. 协议与持久化契约

以下为本 ADR 的目标接口；实现可按仓库命名风格调整符号，字段含义、所有权与顺序不得简化。扩展既有 coordination-v2，不新增数据库或存储目录。

### 6.1 WorkControlOperation

在既有工作控制日志中记录工作/回复层控制。它聚合 ADR116 的 SessionControlOperation 引用，不复制 session 的停稳、资源或验收真值。已有 pendingControl/lastControl 迁为该记录的兼容投影。

| 字段 | 契约 |
| --- | --- |
| operationId / requestDigest / revision | 宿主生成稳定身份；同 ID 同参数幂等，异参数拒绝；CAS 防旧回调覆盖 |
| workspaceId / parentConversationId | 必须与当前控制入口及目标一致 |
| kind | stop_reply / pause_work / withdraw_work / withdraw_bot_current / resume_reply / resume_work |
| scope | reply：workId+replyChainId；work：rootWorkId；bot_current：Bot 身份+根集合截点+目标集合引用 |
| authorityRef / source | 真实 typed 用户操作或 canonical user_input；合法自动纠偏另记 project_agent 来源，不伪造用户撤回 |
| expectedControlRevision / expectedGoalRevision | 控制和目标各自当前性；计量变化不令语义 revision 失效 |
| revokedGeneration / admittedGeneration? | 关闭旧认知代次；resume 才能产生新的准入代次，不能用新 turnId 替代 |
| phase / outcome | recorded → draining → reconciling → settled；无需对账可跳过 reconciling；settled 为 applied/superseded/rejected |
| targetSetRef / pendingTargets / childControlRefs | 有界分页目标与子控制引用；集合未穷尽不得报告全部完成 |
| admissionClosedAt / settlementRef / blockerRefs | 耐久封准入、最终摘要和未决依据；时间不是授权或停稳证明 |

每个 work/reply 只索引当前 controlRef 与认知代次，权威事实来自同一日志 reducer；不能同时维护另一个 renderer 控制布尔值。控制代次与 hostEpoch、executionEpoch、goalRevision、attemptId 各司其职，不互相代替。

有效准入是 Bot 范围屏障、root 控制、reply 控制和适用的 Session Control 的合取；任一覆盖本请求的控制关闭，即不得派发。不能挑选其中时间最新的一条作为放行依据。请求携带覆盖这些引用的 controlSnapshotRef/版本摘要，真实派发时重新展开并验证当前性。自动纠偏只沿有效 mandate 处理其范围，不能给用户已停止的回复/工作签发 resume 或新的准入代次。

bot_current 在同一项目 writer 下先提交根集合截点和封闭谓词，再分页枚举。截点之前已承接根的迟到 spawn/replace 仍继承旧控制，不能通过创建时间或新 UUID 逃逸。截点之后独立真实用户输入可创建新根。涉及持续目标时其触发准入也必须纳入同一封闭谓词，底层控制按既有端口补偿；不宣称跨外部系统原子。

### 6.2 CognitionRequestBinding 与准入结果

每次实际模型请求绑定 workspace、parentConversation、work/root、replyChain（适用时）、role/purpose、controlRef、cognitionGeneration、goalRevision、hostEpoch、attemptId、触发来源与被观察事实版本。Worker/Verifier 还携带既有 SessionExecutionIdentity。身份在请求创建时冻结；旧回调不能读取新代次后冒充新请求。

用途必须区分协调、工作执行、核验、覆盖复核、回复修正；不得将同一目标改为“总结”“恢复”用途绕开停止。纯宿主通知没有模型请求身份。

准入返回 allowed，或带 discriminator 的 held/rejected，原因至少包括 user_stopped_reply、work_paused、work_withdrawn、host_settlement_only、stale_control、no_actionable_change 及既有租约/预算/权限/unknown 错误。返回 currentControlRef、nextHandler 和可用动作；禁止调用者收到 rejected 后无条件重建任务。

准入只增加一道必要约束，不能替代模型路由、预算、Runtime Projection、PermissionGrant、资源和执行代次检查。停止不吊销无关工作的同一账户或全局能力许可。

### 6.3 责任与处理方式

在唯一 FollowUp 投影中增加 `handling`，作为当前权威事实的只读推导，不新增可独立写入的责任状态：

| handling.kind | 必要依据 | 能否据此调用模型 |
| --- | --- | --- |
| model | 有效 work/目标、已准入 decision 或新事件、事实版本和合法认知代次 | 仍须通过 Cognition Admission |
| host | 原控制/交付/恢复操作引用、等待对象及当前事实版本 | 不能；宿主仅执行确定性下一步 |
| user | 真实 request/approval/恢复动作引用 | 不能自动继续；明确交给用户 |
| none | 已结清或无当前责任 | 不能 |

owner 仍为 bot/user/none，inCurrentList 仍由同一投影决定；bot 表示 Peer 对用户负责，handling.host 表示本机 Runtime 正在承办。stop_unconfirmed、资源对账、停止清理以及缺停止事实的旧记录默认 handling.host，不能落到 model。活动子任务等待也不是父模型调用理由；有效目标的新语义结果沿 ADR94/117 才能进入 model。

事实不足保持保守可见，同时关闭自动认知；“fail closed”不能解释成“交给模型一直查”。需要人做决定时有真实请求，不能把内部处理方式字段直接展示成新的审批任务。

### 6.4 事件与回执身份

工作控制、认知代次变更、子控制承接、停止观测、摘要提交沿原 journal/outbox 追加；事件带 operationId、目标、预期代次及事实版本。处理至少一次、稳定 ID 去重，禁止靠时间戳先后覆盖更高版本事实。

重试预约、native checkpoint、prepared reply 和续跑决定都绑定旧代次。封闭后记录失效原因但保留历史；work.state 即使遗留 runnable，实际准入仍拒绝。所有者迁移/合并沿原根与控制引用继承屏障，不能借 continuationOwnerWorkId/coalesced work 解除停止。

## 7. 停止时序与线性化点

1. **验证控制来源与范围。** typed 停止按钮校验当前 Bot/work/reply；文字取消经原模型回合提交合法协调控制。范围不清时只停止已明确对象，针对歧义请求信息；不能先宣称全部已停。
2. **耐久封闭准入。** 在项目 writer 内提交 WorkControlOperation、旧代次失效及目标范围。该提交是接受控制的线性化点，接收回执必须说明范围与阶段。持久化失败不发成功；本宿主可立即 best-effort abort 并保守停止新派发，恢复后核对同操作。
3. **中断与清理预约。** 向范围内实际认知请求传播 abort；停用旧队列项、退避、重试预约和未送达的普通模型回复。清理仅是优化，遗漏计时器也必须被代次检查挡住。
4. **收口受管执行。** 工作暂停/撤回沿 ADR116 的 Session Control、句柄、idle 与资源账本处理。等待期间释放 writer，不能因控制调用等待自己当前认知 attempt 而死锁；发起取消工具的回合通过既有 terminal control 成对返回结果并让出，不再发下一次模型请求。
5. **条件提交。** 回到 writer 重新检查控制/来源/目标/宿主版本，追加停止、撤回或待核对事实。旧 finally 只结算原 attempt/资源，不能把当前 work 写回 runnable。
6. **投影和送达。** 宿主提交控制摘要；普通完成交付失败只重试 outbox，不重跑取消模型。新用户输入和不冲突工作继续处理。

封闭与真实模型/能力 dispatch 的登记在同一有效准入代次上串行化。排队或 reserve 不代表已 dispatch，不能持预约穿过停止屏障；最终准入重检和派发登记必须在同一受治理临界区完成。封闭前已登记的请求算 in-flight，必须取消或等待其实际状态；封闭后旧代次不能新增派发登记。网络传输与外部计算不具备跨系统原子性，不能将本地登记边界描述成所有外部动作瞬间停止。

Provider 内重试、fallback、工具后的下一轮、Verifier/Explorer 再调用及覆盖复核在每次物理 dispatch 前重新检查，不只在外层 pump 看一次。本地能力执行器也校验冻结的根/回复控制身份，工作屏障提交到子 Session Control 生效之间不能出现派发空窗；原 PermissionGrant 有效也不能覆盖停止约束。合法控制工具自身的成对返回和受限宿主收尾是结算原操作，不是新的业务派发。

取消无法撤销已经交给 Provider 的计算或外部副作用，已消费用量照实记账；不能承诺点击即物理停机或取消即免费。迟到 usage/Tool Result/Evidence 沿原身份结算，停止后的模型正文不继续流入公开回复。封闭前已公开的正文保留并标明中断；封闭后的部分结果可以作为历史事实保留，不能推进或关闭当前新目标。

## 8. 宿主收尾、模型推进与唤醒规则

### 8.1 唯一推进判断

`repairOwnership` 只为 handling.model 且认知准入允许的会话产生模型处理项；handling.host 绑定原控制/恢复待办。`stateAfterReply` 不能因 owner=bot、stop_unconfirmed 或普通 sources 直接返回 runnable。root 仍有义务时保留原责任和具体 wait，不伪造 fulfilled。

主 Bot 的“取消指令处理 work”在工具返回 pending 后可以交付宿主“已接收/仍在收尾”摘要，并把后续责任交给原控制操作；该控制 work 不需要不断执行 coordinate_work/assess/post_reply 才能结束。撤回沿 ADR117 withdraw 控制处置，不要求把“停止所有任务”伪装成已核验业务结果的 covered/return；取消成功不等于目标完成或结果验收。

### 8.2 唤醒矩阵

| 触发 | 原认知已停止/撤回 | 原认知仍有效 |
| --- | --- | --- |
| 进度、心跳、重复 stop_unconfirmed、相同错误 | 更新原历史/诊断，不调用模型 | 沿既有去重/静默等待，不周期询问模型 |
| 停止回执、句柄终结、资源释放 | 宿主继续原收尾、更新摘要；不恢复模型 | 宿主先收口；只有另一个合法目标确有语义下一步才重新准入 |
| 子任务完成/异常 | 原事实落盘；已停止回复不自动重开 | 有效目标、来源版本和语义处理资格满足时可唤醒 |
| 网络恢复、retry timer、模型切换 | 旧预约失效，不重新生成预约 | 按既有重试/路由政策和当前代次检查 |
| 宿主重启、租约切换、checkpoint 找回 | 先恢复屏障与收尾；重启不是用户继续 | 当前事实与原 ADR 恢复条件全部满足才可调用 |
| 用户查看历史、展开详情、点击任务引用 | 只读取 | 只读取，不作为续跑依据 |
| 用户点击继续/明确输入恢复 | 校验当前控制和动作资格；回复/暂停可获新代次，撤回必须新委托 | 按原合法控制处理 |

宿主对同一操作、阶段、事实摘要只处理一次；等待有具体句柄/事件/持久预约。停止诊断期限沿 ADR116，不新增无限轮询。到期显示未确认，保持保护；后来收到新停止事实仍可恢复收尾，不能把暂时超时变成永久拒绝。

宿主无法通过既有句柄/事实核对时，保留 scoped blocked/reconciling 和实际缺口，不调用模型反复查看相同日志。用户日后明确要求调查原因可以建立独立只读工作，不能暗中恢复原委托或解除资源保护。

## 9. 引用、所有权与旧会话

公开 reply.sources、任务引用、报告阅读和状态查询只建立观察关系。处理所有权只来自当前 work/mandate 的执行绑定、已核验的原 anchor，或经过 Kernel 的显式责任转移；不得由“用户看得到”“回复提到过”或 sessionIds 合并推导。

对旧 session 缺少 workId：

- 有可核对的原 anchor、计划及规范输入时建立一次加法 legacy binding，记录依据与范围；绑定不能创建 mandate 或新的执行授权。
- 当前用户可直接通过原 Session Control 取消该 session，回执关联本次聚合控制；不要求先造一个可执行 work，也不能因 work_not_found 退回无限模型修复。
- 缺少合法工作绑定仍可作为取消摘要的事实来源；它不进入新取消 work 的 repairSessionIds。
- 无法证明停止/来源时保持 host 收尾或明确缺口，不凭 cancelled 字符串、历史助手承诺、无 live token 或文件时间伪造已停。

同一规则适用于取消后归并、事件再投递、回复恢复以及遗留有 sources 而无业务委托的协调 work。目标关系迁移必须在真实派发前完成验证，不能先开执行再补来源。

## 10. 控制摘要、结果表达与交付

新增 typed `ControlOutcomeSummary` 投影，字段包含 operation/scope、目标集合版本及是否枚举完成、认知准入已关闭的范围、受管停止已确认/未确认、子控制完成/未决数、委托处置、unknown/资源/清理阻碍引用、摘要版本与可用动作。它引用原控制与资源事实，不成为新的 Tool Result 或停止证明。

“全部取消完成”的后置条件为：范围已穷尽；所有目标停止/撤回控制达到本动作所需的 applied；范围内没有旧代次可派发资格或未确认的受管活体；所有未决资源/历史 unknown 已按 ADR110/116 安置并在摘要中准确披露。必要清理未完成时，摘要区分“受管执行已停止”与“仍有清理”，不能称所有事项已结清。

历史 unknown 可以在用户撤回已成立后保留，不因此无限阻止委托退出；但只能说“委托已撤回，历史结果仍未确认”，不能说“所有外部影响已停止”。共享资源 hold 不因摘要显示取消而解除。

| 当前事实 | 第一层表达 | 后续处理 |
| --- | --- | --- |
| 控制已耐久接受，尚未停稳 | 已接收停止，已阻止范围内的新操作 | 显示真实未决数量/范围；host 收尾 |
| 回复链已停止，子任务继续 | 已停止本轮回复；已有子任务仍在运行 | 查看任务、继续回复或按原入口取消工作 |
| 部分目标停止未确认 | 还有若干任务的停止尚未确认 | 展示具体对象/阻碍，不给笼统继续尝试 |
| 委托已撤回，历史 unknown | 委托已撤回；历史结果仍未确认 | 退出业务跟进，保留历史与保护入口 |
| 已满足本范围的最终条件 | 当前范围内的工作已取消，不会自动恢复 | 新委托需新用户来源；不承诺无关定时目标也被停用 |

宿主用同一摘要生成稳定的控制回执消息/卡片。模型如补充解释，只能引用其版本并声明对应结构化 controlClaims；已有 statusClaims 继续校验各 sources，不能把相同 cancelled 状态当作停止屏障证明。语义正文无法靠正则完整证明；权威摘要始终单列且同源，不能因助手一句话修改它。

结构化声明与当前事实不一致时，不提交误导性的控制结果；返回可核对冲突并直接送达真实宿主摘要。是否属于控制结果由宿主记录的输入/操作关系决定，不能通过省略 sources/controlClaims 或改为普通无来源文本绕过摘要。自由文字的全部语义无法由类型系统证明，本契约保证权威回执与准入事实，不宣称能自动识别所有错误措辞。

控制类回复不启动反复模型“改口”循环。已公开的错误承诺保留，追加一次绑定原消息的更正回执，不改写历史、不伪造 assistant 推理。摘要内容未变化不重复发消息。

普通 prepared 回复：封闭前已提交的保留；尚未提交且属于旧代次的失效，不在停止后补投旧结论。控制摘要具有受限的 host_delivery 用途，只能送达该操作的真实状态，不得借此续接模型、发工具或接受结果。送达失败按原 outbox 幂等重试，消息提交与停止/验收分别记录。

## 11. 重启、竞争与故障语义

恢复顺序为：HostLease/Writer Fence 与格式能力 → 工作认知屏障及范围 → Session Control/资源/unknown → 队列和预约失效 → 确定性收尾/交付 → 对仍合法的工作开放认知。任何 pump、预算恢复、repair custody、reportedWait 变化或原生续接都不能先于屏障还原运行。

| 竞争/故障 | 必须结果 |
| --- | --- |
| 接受停止前崩溃 | 不曾承诺耐久接受；同请求身份重试，核对是否已提交 |
| fence 已落盘、abort 尚未发送 | 旧代次不能 dispatch；新宿主从原控制补 abort/drain |
| 停止与模型请求并发 | 依登记线性化点区分 in-flight/拒绝；用量不漏记 |
| 停止与 Worker spawn/返修/替换并发 | 目标根屏障继承到后代，不能新代次逃逸；已开始的受管执行继续停稳 |
| 停止与普通完成/return 并发 | 已提交事实保留；控制之后的旧决定不能覆盖停止或签收新目标 |
| 停止与用户恢复并发 | 按来源及 expected revision CAS；过期 resume 拒绝；撤回根不能普通恢复 |
| 最后子任务回报恰逢停止 | 结果保留但不重开已停止回复链；合法无关工作正常处理 |
| 资源已结清，摘要尚未送达 | 补送摘要，不调用模型，不重跑取消 |
| 旧 finally/计时器/租约回调 | 只处理原身份，不写回新代次、当前资源或 runnable |
| journal/控制引用损坏 | 关闭可证明受影响范围的认知/执行，提供恢复诊断；不能靠删除控制恢复 |
| 一项停止长期未确认 | 保留该项保护与具体责任，不冻结其他不冲突任务和新输入 |

控制 accepted、停止 requested、model request cancelled、managed execution stopped、delegation withdrawn、resource settled、reply delivered 是不同事实。任何前一项不能自动创建后一项；计时器、动画、关闭窗口和普通读取都不创造这些事实。

## 12. 存储、兼容与遗留迁移

沿已登记 projectRuntime 的 coordination-v2 journal/blob 追加 WorkControlOperation、目标集合和摘要引用；WorkReceipt/checkpoint 只保留必要索引及代次。设备资源 DB、PermissionGrant、Conversation、GoalPlan、Evidence 和用量继续保持原所有权，不建立平行停止账本。未决控制与屏障引用纳入 ADR113 的可达保留集合，不被普通 checkpoint GC 清除。

当前联合特性门槛为 9。本提案预留 `user_stop_cognition_admission_v1` 能力，并在首次写入前同步提升 minimum reader/writer/executor 至 10；实施前如编号被其他主线变更占用，先更新本节及兼容矩阵再实施。数值较大不代表兼容，必须具备原 7/8/9 reducer 与新语义。head、manifest、重建、portable 导入与只读投影均不能降低门槛。

迁移由正常取得宿主权的兼容 Runtime 执行，先完成只读盘点与格式准入，再加法提交；开发时不直接编辑生产 JSON。迁移判断如下：

| 旧形态 | 迁移 |
| --- | --- |
| 有 canonical 用户停止回执/原 stopScope，但 runnable/retry_wait 与之矛盾 | 建立匹配范围屏障，失效旧预约，保留原工作历史；宿主核对未决停止 |
| cancelled/stop_unconfirmed 的旧会话被取消回复 sources 吸入新 work | 拆开观察与执行处理关系，追加 custody 修正；收尾留在原控制，不能自动派模型 |
| 有完成停止回执又保留 takeover/interruption | 沿 ADR110/116 核对来源和代次，幂等补控制与投影；不清 unknown、不重跑 Worker |
| 只有助手文字“已取消”或时间戳 | 不生成用户控制；事实缺口归 host 诊断，不伪造原取消来源 |
| 无停止迹象、仍有合法持续委托 | 保留 ADR95/117 的正常持续推进，不全量暂停历史工作 |
| 真实撤回后又有新的用户委托 | 新根引用旧历史；旧根仍关闭，按新目标重新准入 |

旧不支持门槛的运行时不得接管新活跃数据；只读历史按兼容规则提供。回滚先封准入、停稳并保留全部事实，使用支持此控制语义的修复版本；不得删字段、降版本或改回 owner=bot 即 runnable 的旧路径。跨设备复制旧租约/代次不产生当前执行权。

## 13. 方案比较与后果

| 备选方案 | 不采用原因 |
| --- | --- |
| 只补 prompt：“停止后不要重启” | 不能约束内层重试、宿主恢复和工具派发 |
| 将所有 stop_unconfirmed 直接改成已取消并隐藏 | 隐瞒活体/未知结果，可能提前放开冲突资源 |
| 一律将 followUp.owner 改成 none | 混淆仍需宿主处理的责任，破坏列表与诊断真值 |
| 取消后销毁 Bot 或停用整个项目模型服务 | 范围过大，阻断独立新输入与不相关委托 |
| 不断让模型检查停止状态 | 重复消耗、竞态扩大，可能再次执行被撤回目标 |
| 新建独立取消后台、锁表或任务系统 | 复制控制/资源真值，扩大接口和故障面 |
| 把普通 sources 全部当成处理权 | 读历史或汇报取消都可能接走无关遗留责任 |
| 依赖 no_progress 最后兜底 | 用户控制变成若干额外模型调用后的偶然结果 |

代价是控制代次、请求身份、处理方式、旧记录迁移和版本门槛需要一致落地；它们集中在共享 kernel/admission/现有控制 seam，不分散到页面。收益是用户停止成为可复核的运行边界，宿主仍能完成必要收尾，正常长期委托继续按进展推进。

代价还包括远端请求可能在本地停止后继续产生费用、缺查询句柄时仍可能长期保留具体 unknown，以及停止当前回复后用户需要显式恢复才能让父 Bot 处理子任务新结果。产品必须准确表达这些边界，不把“无模型续跑”称为所有副作用瞬间停止。

## 14. 实施顺序与文件边界

本文为先行设计。以下工作包是后续实施拆分，不构成当前代码授权；各包串行集成，前包协议由后包复用，不跨包重造状态机。

| 包 | 交付内容 | 主要落点（相对代码仓） | 退出条件 |
| --- | --- | --- | --- |
| US-01 | WorkControl、认知请求身份、handling、摘要、纯 reducer、格式门槛 | `packages/protocol/src/`；`runtime-node/src/project-agent/` 原 journal/store/replay/fence | 单一真源、身份/幂等/CAS/兼容规则完整，生成式 worker 从原 canonical 源同步 |
| US-02 | 共享 Cognition Admission、停止/恢复、物理 dispatch 与内层重试接线 | `runner.mjs`、`runner-coordination.mjs`、`recovery-policy.mjs`、原 Executor/Provider seams | 所有范围内模型角色和 fallback/重试均拒绝旧代次，不靠外层状态兜底 |
| US-03 | 宿主收尾分流、取消处理 work、旧会话绑定和 custody 修正 | `work-control`、`session-control/cancellation`、`repair-ownership/custody`、`coordination-lifecycle` | pending 不再模型空转；无 workId 可安全收尾；未知与资源不丢 |
| US-04 | 控制摘要及交付、Desktop/TUI/CLI 同源状态与恢复动作 | `reply-composer/delivery`、原 project facts、typed IPC/Preload、renderer/state、TUI、i18n | 准入与按钮一致；取消状态不能提前成功；更新两份体验矩阵为源码状态 |
| US-05 | 旧数据迁移、崩溃/并发/冷恢复、范围隔离及真实形状夹具 | 同包契约测试及既有产品回归夹具 | 覆盖下一节全部硬性场景，保留可审计来源与未运行项 |
| US-R | 最终联合候选完整验证和安装版观察 | 原发布/产品回归流程 | 精确候选、全部截图人工审阅、真实覆盖与限制完整 |

避免增长中央 `main.mjs`、Chat Runtime 或大型 React Surface。新 seam 必须减少调用方理解停止/重试/责任组合的成本，不能只做转发包装。Context 提示若需要补充，进入原登记 Source；控制/摘要是结构化事实，不提升成新的系统指令层。

体验实施记录：用户目标为“停止后保持停止并知道剩余收尾”；状态来自控制、执行句柄、资源、交付与唯一投影；可控制继续回复、恢复暂停、撤回工作和查看阻碍；失败保留草稿、公开部分结果、阅读锚点和原历史。使用既有 Frost/--ui-*、PeerIcon SVG、共享 motion/transition seam；后台回执不抢焦点、不恢复贴底、不重复播放历史动画。低动效/低透明/API 不可用时保留完整静态状态。只做本文不将交互或 UI/动效/过渡矩阵标记为已实现/验收。

## 15. 验收矩阵与发布阻塞条件

以下是必须编写并在获准早测或发布时执行的行为验证，不是本轮已运行结果。必须走生产 Module/能力链及原存储，不以 stub 返回 cancelled 代替端到端屏障。

| 编号 | 场景 | 必须证明 |
| --- | --- | --- |
| A01 | 本次 RC35 真实形状：取消回复 sources 带缺 workId 的旧 cancelled/stop_unconfirmed | 不增加模型处理权；host 收尾；回复之后额外模型请求数为 0 |
| A02 | 停止当前回复，子任务仍执行 | 父回复链无自动模型调用，子任务不被误取消；结果保留；显式继续后一次准入 |
| A03 | 无子任务的用户工作/协调回合被暂停或撤回 | 不依赖 session 才能封父认知；重启不恢复旧根 |
| A04 | 取消全部，含 queued/paused/retry_wait/替换候选及进行中的 spawn | 集合截点和继承范围完整，不能新 UUID 逃逸；共享依赖和其他 Bot 保留 |
| A05 | 控制与物理 Provider dispatch 的两种先后 | 封闭后新增派发登记数为 0；旧 reserve 不能放行；封闭前 in-flight 可取消/结算，用量完整 |
| A06 | Provider 内部退避、fallback、Verifier/Explorer/覆盖复核 | 每次实际 dispatch 都过屏障，不因外层已接受停止又产生请求 |
| A07 | 同一 stop_unconfirmed/错误/进度反复投递 | 不调用模型、不制造 revision 假进展；重复宿主处理有界 |
| A08 | 30 秒诊断超时后真实句柄终于终结 | 保持保护后可自动补收尾；不需要重复用户取消、不重启模型 |
| A09 | 历史 Shell unknown，无受管活体，用户撤回 | 委托按原契约退出；未知数组、预算和 Evidence 保持；相关 hold 未清除 |
| A10 | 尚有真实 live 或无权查询的外部操作 | 不提前签发停稳/释放资源；具体未确认可见，主 Bot 不轮询 |
| A11 | 子任务回报、prepared reply、旧 post_reply 与停止竞争 | 已发生消息保留，旧代次未交付正文不补投；控制摘要可以独立送达 |
| A12 | 控制摘要送达失败/消息已提交但补偿失败 | 仅重试原 outbox，单次公开回执，不调用模型或重做停止 |
| A13 | 助手声称全部取消但结构化事实仅部分完成 | 拒绝不符声明并送真实摘要；无无限改口循环；历史错误只追加更正 |
| A14 | 缺 canonical 来源、跨 Bot/session/父会话、附件注入控制文字 | 不产生控制权或用户撤回事实，范围不扩大 |
| A15 | 重复控制、同 ID 异参数、旧 resume 与新 cancel 竞争 | 幂等/CAS 正确；撤回根不能普通重试恢复 |
| A16 | 每个崩溃窗口及宿主切换 | 先恢复屏障，再执行宿主补偿；旧 finally 不改新代次或资源 |
| A17 | 普通查询、看历史、打开引用、新独立用户输入 | 读取零副作用；新问题能回答且不解除旧停止；无全 Bot 饥饿 |
| A18 | 有合法目标且无停止，阶段交付后继续/真正语义新结果 | 保留 ADR95/117 自动推进与真实预算，无“一刀切停掉所有 work”回归 |
| A19 | 旧 record/custody/coalesced/checkpoint/预算恢复 | 继承屏障、一次迁移、无旧命令重放；缺证据 fail closed 且可定位 |
| A20 | 独立持续目标与绑定根触发器 | 已撤回根不重建；独立启用计划准确披露；明确全停时其控制也入摘要 |
| A21 | 新格式冷重载、portable 导入、旧 writer/executor 和 GC | 不降门槛，不漏控制引用，不因读旧字段获得执行权 |
| A22 | 同一事实的 get/list/summary/批量读取/详情/计数/动作 | handling、状态、回执与实际准入一致；不出现可点击但注定拒绝的继续 |
| A23 | 生产能力调用及真实 PermissionGrant/Tool Result/Evidence | 停止只是额外约束；不伪造授权、工具成功、验收或副作用停止 |
| A24 | 安装版、主题/窄布局、键盘/IME/草稿/阅读/减少动效 | 用户能辨认作用范围与未确认，停止回执不抢注意力；交互证据独立于静态截图 |

发布硬性阻塞：有效封闭后同范围发生任何新模型 dispatch/能力派发；迟到事件复活；取消误伤无关工作；未知或资源保护被清空；假全部完成；控制回执丢失且无恢复；旧版本能忽略屏障执行。

测试、build、typecheck、架构/IPC 检查、截图/交互回归不在日常文档交付时自动运行。版本/RC 依代码仓 AGENTS：先清空全部开放 PR 门槛，再冻结最终组合候选，完整运行 build/test/type/architecture/IPC 及产品 Capture。执行 AI 必须逐张查看 required 截图并写 review.json，最后 Verify；注明是否独立及真实模型、安装包、辅助技术的覆盖，不继承其他候选结论。

## 16. 决策状态与审阅收据

2026-11-03：完成本 ADR 的方案、契约、状态/竞争、迁移、交付与验收设计；实施者内容/diff 自审，非独立评审。编号已核对 fetch 后知识仓所有可见 origin 引用，118 已占用，本提案使用 119；尚未推送的其他占号无法由本轮证明。

同日补充：[任务链路可靠性审计与收敛计划](../experience/peer-task-chain-reliability-audit.md)将本决策置于“保住原任务执行闭环”的实施顺序中。优先统一停止准入、宿主收尾及引用/处理权，再接齐资源等待与生产事实契约；不能把本 ADR 实现成另一套与现有机制互相覆盖的管理层。该审计不构成实施批准或已通过验收。

知识仓原工作树有无关未提交修改，本文件在从上述 origin/main 建立的独立工作树中编写，不修改既有在制文件。未改变 Peer-Agent 代码、运行中的应用或真实用户数据，未提交停止/恢复命令，未运行测试、构建或产品回归。本文完成不等于 Accepted、Implemented 或故障已修复，也不自动进入下一版本/RC。

## 后续（2026-11-07，本文仍未接受）

[ADR 124](124-legacy-stop-obligation-controlled-resolution.md) 已于 2026-11-07 20:03（Asia/Shanghai）接受并授权实施。它给主 Bot 增加只读核实、出示授权卡和授权后退役跟进三件工具，因此只收窄本文草案里“不增加工具通道”这一句。本文其余条款仍未接受，认知代次仍未授权实施。ADR 124 不实现那些条款，也不占用本文预留的格式门槛 10。聊天文字仍然不是停止证据，也不是授权。接受 ADR 124 不等于接受本文。
