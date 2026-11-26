# ADR 139：Worker 单步推理重试、用量缺失与原地恢复

创建时间：2026-11-26
最后更新：2026-11-26（项目主人审定转为 Accepted）
状态：Accepted（2026-11-26 项目主人审定通过，解锁 Wave 2 A 级实施；代码落地与发布验收另行独立核实）
级别：A（Worker 恢复准入、跨宿主活动投影、冻结模型一致性）；Wave 1 Track 1 的共享重试与脱敏分类按 B 级并行推进

## 1. 背景与问题

2026-11-26 对 Peer Desktop `v0.1.0 RC 45` 的现场取证与源码审计记录了三个缺口。Worker 通用推理路径缺少同模型单步重试。供应商通过 SSE 发出的错误事件经过宿主后仅剩 `model_provider_error`，瞬时故障与不可重试拒绝难以区分。失败请求留下 `unknownUsage=true` 时，即使工具已全部结算，Worker 也会被拦在原地恢复入口。

同日本机 Codex CLI `0.172.0` 对照观察到 WebSocket 断开后约 200 ms 自动重连。该观察只描述当次本机行为。Peer 的退避参数、订阅端点协议支持和传输收益须各自验证。

**模型负责认知 · 本地负责能力 · 界面负责表达 · 契约负责边界 · 证据负责治理。** Rust Core 持有单步重试事实和执行准入。负责结算的模块按各自权威账本记录用量与工具效果，RPC 和界面只消费活动投影。[架构治理](../architecture/20-architecture-governance.md) · [ADR 133](./133-unified-rust-core-and-dual-host-architecture.md)

## 2. D1：账务观测与执行副作用分别结算

`unknownUsage=true` 表示某次失败的模型物理调用缺少供应商 token 用量观测。已知部分由用量账本提交，未观测部分继续标为未知。工具副作用的 `Unknown Outcome` 由派发记录、句柄、资源账本及结果回执判定。两个事实可以同时出现，各自沿原路径处理。[ADR 56](./56-provider-observed-context-accounting.md) · [ADR 127](./127-unknown-outcome-reconciliation-and-delegated-resolution.md)

**停稳的 Worker 经既有入口原地续作，必须同时满足以下六项条件。**

1. `runtimeExecution.phase == "stopped"`，且匹配旧执行身份的停止收据齐全，`runnerIdle && admissionClosed && handlesEnded`。
2. `pendingTools` 为空，且没有活跃后台 handle、进程或未结清执行资源 claim。
3. `usageCommitted == true`，已有可观测用量已提交。
4. 当前续作范围没有 `execution_outcome_unknown`、`RetainedUnknown` 或资源、策略硬阻断。
5. 宿主租约有效，工作区、渠道和模型代次通过 D3 一致性校验。
6. 委托仍有效，用户尚未撤回，且 `!cancelled && !superseded`。

Session Control 和 Supervisor 在现有控制与调度路径中读取权威收据、账本和计划，绑定相同的工作区、会话、计划和执行代次，在实际准入前重检。旧检查结果、空字段、过期租约、未结束句柄或缺失收据均不得作为放行依据。取消、撤回或换代与恢复竞争时，关闭准入的控制优先，旧代次回调只归原历史。排队或协调回执完成后，仍须等实际执行开始的事实才可显示已恢复。

任何未结算工具、活跃后台进程或执行副作用未知都继续拦截自动续作，交原控制与对账路径处理。需要用户决定时走 `ask` 逐项确认。已有用户委托的 `bot_verified` 仅按既有探针证据和宿主风险校验收口。受控闭包可以按 ADR 126 释放目录 claim，但不得把保留的未知记录变为成功回执，也不得借原地续作重放该调用。对无关新操作的资源准入仍按设备账本判定。[ADR 116](./116-session-control-and-resource-settlement.md) · [ADR 126](./126-execution-resource-claim-closure-and-unknown-retention.md) · [ADR 127](./127-unknown-outcome-reconciliation-and-delegated-resolution.md)

符合六项条件的历史 `unknownUsage=true` 记录可只读识别，经 `resume` 或 `message_session(intent="followup")` 请求原地恢复。仍使用既有控制操作 ID、版本校验及 `followUpEpoch` 防重复派发，保留原会话、工作区、已结算工具、Evidence 和累积账务。续作不得擦除或篡改历史 `unknownUsage=true`，不得把未观测用量写成零，也不得自动放宽费用、轮次或工具预算上限。

| 既有 ADR | 本决策细化的范围 |
|---|---|
| [ADR 73](./73-goal-interruption-suspension-vs-failure.md) | 活执行中的单步退避属于认知步骤内部。停稳后的 `interrupted` 仍沿原恢复入口消费，由 Project Bot 监督技术中断，显式取消终态优先。 |
| [ADR 116](./116-session-control-and-resource-settlement.md) | 原地恢复继续使用唯一停稳屏障与执行代次控制。用量缺失不构成执行效果未知的证据。 |
| [ADR 120](./120-runtime-facts-disposition-and-resource-wait.md) | 统一处置读取各自的运行、控制、资源与账务事实。资源等待、恢复排队、实际开始和执行结果沿原事实分别表达。 |
| [ADR 126](./126-execution-resource-claim-closure-and-unknown-retention.md) / [ADR 127](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) | 保留原 claim、对账与授权闭包。执行未知或 `RetainedUnknown` 继续拦截原地续作。 |
| [ADR 138 §3 D3–D4](./138-project-bot-unified-scheduling-followup-and-natural-reply.md) | 已结束 Worker 的 `resumed_followup` 按六项条件和 D3 校验。`started_fresh` 只在原替代准入允许时使用，不能绕开未知效果、资源或用户控制。终态仍由 `SessionSupervisor` 单源发射。 |

## 3. D2：共享单步纯推理重试与只读重连活动

### 3.1 单步重试与提交边界

- 重试归 `peer-runtime` 的共享推理回路。Provider adapter 解码传输与 SSE 错误并产出结构化分类，Desktop、TUI 和 RPC 共用 Rust Core 的重试判断。Worker 的一次重试锁定同一 provider、账号、渠道、模型、`reasoningEffort` 和 `fastMode`，沿既有网络与信任策略发起请求。[ADR 30](./30-provider-recovery-broker.md) · [ADR 133](./133-unified-rust-core-and-dual-host-architecture.md)
- 仅在当前认知步尚未派发任一本轮本地工具、也未提交本步输出或进入工具授权与执行链时，才可重放该纯推理请求。每次从同一已提交会话边界开始。失败尝试的未提交 delta 只可作为可撤销预览，重试前按尝试身份清除，晚到帧不得拼进新预览。已提交消息、已结算工具结果和 Evidence 保持原身份，历史工具永不重跑，工具派发与本步正式输出至多提交一次。
- 每次物理尝试独立归因并幂等记账，记录实际观测到的用量。逻辑 turn 与工具预算只按逻辑执行结算，真实费用约束仍逐次检查。用量记录不能用来推断工具副作用，已结算的账务也不得回滚来换取重放。
- 使用有限次数、总时间上限、指数退避加 jitter 和共享并发重试限流。有效的 `Retry-After` 约束最早重试时点，若超出本步时限则结束重试。连接、流中断及后续传输回落共享一个物理尝试预算，避免在宿主或 adapter 叠加独立重试。取消信号贯穿排队、退避、建连与读流，取消或执行换代后不得开启下一次尝试。

本节将 ADR 30 的同模型连接恢复落到 Rust Core 的单步执行边界。ADR 30 的经典整轮、跨渠道 broker 重放屏障继续适用其原有路径。可撤销预览只允许当前 Worker 同绑定的纯推理步骤重试，不能为整轮或跨渠道重放提供资格。ADR 83 的显式步骤边界换挡见 D3。

| 分类 | 典型情况与处置 |
|---|---|
| 可重试 | 经分类确认的瞬时网络错误、超时、中流中断，HTTP `502 / 503 / 504`、边缘 `520–524`，以及由对应 adapter 核实的瞬时 SSE 错误。已明确为短期限流且允许重试的响应仍受 `Retry-After` 和同一预算约束。均须重新检查重放安全。 |
| 不可重试 | 鉴权或权限拒绝、策略拒绝、长周期配额或余额不足、显式上下文或 token 上限、证书与信任校验失败、坏参数、用户取消，以及无法确认瞬时性的 HTTP/SSE 错误。取消按取消路径收尾，其余沿既有错误与处置出口。 |

诊断只允许输出分类、SSE event kind 白名单值、安全 provider code、数字 HTTP 状态、失败阶段、重试次数和解析后的 `Retry-After`。未知值省略详情，保留兼容的通用错误码供旧消费者使用。禁止记录或透传供应商原始错误正文、模型输出、prompt、凭据、私有代理地址、请求头及其他私有代理敏感信息。

### 3.2 活动投影与停止

共享运行时在已准入的退避等待期间，通过既有活动事件流输出 `phase: "reconnecting"`，由 RPC 转发。

| 字段 | 语义 |
|---|---|
| `attempt` / `maxAttempts` | 即将进行的重试序号与本步骤最多重试次数。序号从 1 起，二者均不含首次请求。 |
| `nextRetryAt` | 运行时计划的最早重试时间。并发限流或调度可以推迟尝试，时间戳不承诺恢复，也不触发客户端调度。 |
| `reasonCategory` | D2 的脱敏分类，供界面映射为可读文案。 |
| `cancelable: true` | 当前重试等待可以由既有控制入口中断。任务级操作权仍由 `decideLifecycle` 决定。 |

活动沿现有 workspace/session、执行代次和事件顺序归属到当前步骤。开始下一尝试、停止、耗尽重试或代次失效时清除这段等待活动。重新订阅只投影仍有效的活动，消费者忽略迟到、重复或旧代次事件。该投影不写入任务生命周期，不新增持久化状态或终态，不进入对话正文、Evidence、主 Bot 终态唤醒或权限事实。生命周期继续由 `decideLifecycle` 统一决定，任务终态只消费既有权威事件。旧客户端可以忽略这项可选活动。[ADR 102](./102-unified-task-lifecycle-projection.md) · [ADR 138 §3 D4](./138-project-bot-unified-scheduling-followup-and-natural-reply.md)

Desktop 在同一任务行就地显示「网络波动，正在重连（第 X/N 次）」。已核实的短期限流使用对应文案。界面保留草稿、引用、附件、IME 输入、焦点和滚动锚点，复用既有「停止」入口、操作位置和可访问名称。点击后立即发起原控制请求，Runtime 收到后立即中断退避或在途尝试，且不得再次派发。界面按真实控制回执表达处理中与停稳，动画或倒计时不参与准入、停止或结果判定。重连耗尽后由原生命周期说明原因及合法恢复入口。[Peer 体验规范](../specifications/peer-product-experience-standard.md) · [人机交互契约](../specifications/peer-human-agent-interaction-contract.md) · [过渡规范](../specifications/transition-system.md)

## 4. D3：Worker 启动与原地恢复使用冻结模型快照

- 创建计划时持久化冻结的 `DelegationOrigin.modelSelection`，完整绑定包含 `providerBinding`、`modelId`、`reasoningEffort`、`fastMode`。Worker 首次启动和原地恢复都用该计划快照中的生效绑定装配请求。宿主核对租约、工作区及 worktree、checkpoint 身份、渠道及模型代次。全局角色默认值的后续改动只影响新解析，不能覆盖旧 Worker 的快照。
- ADR 83 §5 允许在步骤边界因模型或渠道不可用作显式换挡，只能在该角色过滤后的允许候选中选择，并验证能力、项目范围和实际请求参数。换挡须持久记录触发原因及旧、新绑定归因，供后续启动和同代恢复使用，原始快照保留供追溯。内部重试不能触发换挡。ADR 99 的 `continuity_model_changed` 仍限定为主 Bot 的重基路径。
- 请求归因由宿主按 adapter 最终生效请求记录，包含任务与执行代次引用、安全的 provider/渠道绑定引用、模型 ID、思考强度、正常或快速模式及必要的换挡来源。归因不记录凭据、私有地址、prompt 或请求内容。
- 仅有 `family/model` 的旧记录可只读适配。只有同一计划及代次的权威 checkpoint、启动或请求归因能唯一还原其余字段且通过一致性检查时，才允许使用该绑定续作。缺失、冲突或无法唯一归因时明确说明原因，拒绝原地续作。若原替代准入仍允许，可沿 ADR 138 的 `started_fresh` 创建有谱系的新会话，重新冻结模型。旧记录不批量回填，现行全局默认值不作为历史证据。[ADR 83 §5](./83-model-routing-by-role.md) · [ADR 99 §2.2](./99-authoritative-reply-receipts-and-model-recovery.md) · [ADR 138 §3 D3](./138-project-bot-unified-scheduling-followup-and-natural-reply.md)

## 5. D4：Responses WebSocket 与 HTTP/SSE 回落的后续准入

P2 属于后续立项。任何在 `peer-runtime` 引入 Responses WebSocket 的提案，均须同时满足以下五项条件。

1. 连接按 `endpoint + credential identity + proxy route + trust root` 隔离，禁止跨账号、代理或信任根复用。
2. 显式处理 socket 关闭、`401` / OAuth 刷新、代理变更、背压及帧大小上限。认证或路由变更须使旧连接失效，认证拒绝不得当作瞬时传输故障反复重连。满足 D2 安全重放准入时，传输失败可在同一逻辑步骤内回落 HTTP/SSE，沿同一取消路径和剩余重试预算，保持同一绑定与网络策略。
3. 保留现有隐私与数据留存约束。`store=false` 保持生效。采用服务端持久化须另立 ADR 并取得审批。
4. 任何基于事件序号的断点续传均须按序号去重，校验事件归属与顺序，保持输出和终态提交语义，拒绝用迟到或重复帧补造结果。
5. ChatGPT OAuth 等订阅端点先在隔离环境实测协议支持和稳定性收益，再立项实施。Codex CLI 的本机观测仅用于设定对照实验。

连接重试和资源使用必须有界。任何连接池均须先证明上述隔离与失效规则，不能默认启用未经隔离验证的全局连接池。

## 6. 实施索引与验收

Wave 1 Track 1 在 `peer-runtime` 交付共享纯推理重试与错误分类，按既有 B 级范围验收。Wave 1 Track 2 交付本 ADR。项目主人已审定 D1–D4，待在途 PR 合入后启动 Wave 2。下列 A 级变更的代码落地、存量恢复和发布验收须分别核实并记录。

| 实施包 | 验收检查 |
|---|---|
| Wave 2 Track 3 · Rust / 安全重放与取消 | 用 RC 45 故障形状注入建连及流中错误，核对同绑定、次数与总时限、`Retry-After`、并发限制、鉴权及长周期配额零重试、诊断脱敏和耗尽出口。失败预览清除，已提交输出、工具和 Evidence 零重放。物理请求分别记账，逻辑轮次及工具预算无重复扣减。在退避、并发等待和在途请求时取消，验证停止屏障和零后续尝试。 |
| Wave 2 Track 3 · Rust / 原地续作与模型 | 用历史 `unknownUsage=true` 记录经 `resume` 与 `message_session(followup)` 验证幂等原地续作、原账务缺失标记和预算保留。逐项打破六项准入条件，验证未结算工具、活跃句柄、`Unknown Outcome` 和 `RetainedUnknown` 均拒绝自动续作。覆盖并发取消、租约失效、旧结果迟到、冷启动、篡改当前全局默认值、合法步骤换挡、历史绑定可还原及不可还原，核对最终 wire 请求归因。 |
| Wave 2 Track 4 · Desktop UI / RPC | 通过实际 Runtime → RPC → Desktop 路径观察重连、恢复、耗尽及停止回执，验证旧代次事件和重新订阅不会产生重复行或复活提示。重连期间任务行、草稿、焦点及滚动位置连续，键盘可立即操作「停止」，无需等待退避或动效。核对生命周期与终态唤醒仍使用原投影及单一来源。 |
