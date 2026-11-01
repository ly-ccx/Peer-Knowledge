# ADR 110：跟进责任收口与当前待办列表判定

> 2026-11-01 实施衔接：[ADR 117](117-intent-driven-coordination-and-goal-closure.md) 在隔离交付分支区分子任务 followUp 与根目标协调责任：阶段 accepted 仍可退出子任务当前列表，剩余目标由既有 coordination work 承接。根关闭不反向签收子任务、不释放资源，也不把已签收子任务伪装为 running；未增加 Renderer 列表状态或改变当前 followUp 来源。本文唯一生命周期投影、撤回、未知历史结果及停止回执契约保留。接口见 ADR 117 §14，源码自测与未执行的产品验收见[实施回执](../../playbook/v0.1.0/intent-driven-coordination-self-test.md)。

创建时间：2026-10-28
最后更新：2026-11-01（关联 ADR 117 实施边界）
状态：Accepted（用户在“责任收口＋当前列表判定”设计中明确批准本节不变量）
级别：A（生命周期/责任投影契约），B（宿主投影与列表、计数消费端）
关联：ADR93（核验续接与修复责任）、ADR102（任务生命周期单一投影）、ADR103（核验收口与停滞治理）、ADR84（Bot 列表外壳）。

## 0. 一句话

“结果就绪”“核验中”“技术阻塞”“用户已停止”“被完成替换承接”都必须由宿主同一处判定**谁还要跟进**，列表与计数只消费这个判定，不再按 `status` 字符串各自过滤。

## 1. 问题（系统语言）

- `apps/desktop/renderer/src/project-agent/state/botWorkState.ts` 的 `FOLLOW_UP` 把全部 `result_ready` 当作当前待办；`backgroundWork()` 与计数都建立在同一份 renderer 本地状态表上。
- 于是：普通技术核验（Bot 自己能收口的结果）与真正的人类验收门在列表里长得一样；用户已明确停止、且没有活动执行/未决停止回执的工作仍以“待办”形态留着；被完成替换承接的旧阶段可能继续独立占一条待办。
- 根因不是文案，而是**责任判定缺一层**：ADR102 的 `decideLifecycle` 只回答“生命周期状态是什么”，没有回答“这一行现在归谁跟进、是否属于当前列表”。状态表退化成第二套判定。

## 2. 决策

### D1 责任判定并入唯一生命周期出口

在 `packages/protocol/src/task-overview.ts` 的既有 `decideLifecycle` 出口内新增 `followUp` 投影（内部先算原结论，再补 `followUp`，不新开第二套状态机）：

```ts
export type FollowUpOwner = 'bot' | 'user' | 'none';
export interface FollowUpProjection {
  readonly owner: FollowUpOwner;      // bot=主 Bot 跟进；user=真实人工/策略门槛；none=退出当前待办
  readonly inCurrentList: boolean;    // 恒等于 owner !== 'none'
  readonly reason: FollowUpReason;    // 可核对的判定依据
}
```

`LifecycleDecision` 增加只读字段 `followUp`；`LifecycleFacts` 不新增“由文案推断”的事实来源，只加一个由宿主判定的布尔事实 `humanGate`（真实人工/策略门已由既有 close gate 放行）。其余仍用既有权威事实：`executionOwnership`、`accepted`、`superseded`、`needsUser`、`verificationActive`、`blockedReason`、`cancellationPhase/takeoverPhase`。

> 实施中发现并已纠正的第二根因：`session-supervisor.mjs` 的 `project()` 对**每个**会话都传 `acceptance: 'confirm'`，所以 `acceptance==='confirm'` 是策略模式常量，不是“现在需要用户确认”的证据；按它判定会把全部普通结果重新变成“需要你确认”。因此人工门只认宿主 close gate 判定（`decideSessionAcceptance(...).mode==='confirm' && closeGatePassed`），经 `WorkSessionConversationMeta.resultConfirmationRequired` 传入，并在同一函数内复用同一份判定（不再调用两次）。

### D2 事实 → 责任判定表（同一行必须同源）

| # | 权威事实 | owner | 在当前列表 | reason |
|---|---|---|---|---|
| 1 | `accepted` 真实验收事实（且无活动执行 / 未决停止 / 真实人工请求） | none | 否 | `settled` |
| 2 | `supersededBy` 存在（责任转移给承接方；同样不得盖掉活体执行与人工请求） | none | 否 | `superseded` |
| 3 | `cancelled` 且 `cancellationPhase==='completed'` 且非 live（回执由宿主 abort + waitForIdle 后写入；ownership=unknown 单独不算结束） | none | 否 | `stop_confirmed` |
| 4 | `cancelled` 但无已确认停止回执 | bot | 是 | `stop_unconfirmed` |
| 5 | `stopping` / `awaiting_outcome` | bot | 是 | `stop_unconfirmed` |
| 6 | `waiting_user`：真实人工问题/审批/预算决策 | user | 是 | `human_request` / `awaiting_human_gate` |
| 7 | `waiting_agent`（父代理/技术阻塞） | bot | 是 | `technical_block` |
| 8 | `result_ready` + 宿主 close gate 已放行的真实人工/策略门（`humanGate===true`） | user | 是 | `awaiting_human_gate` |
| 9 | 其余 `result_ready`（普通技术核验；`acceptance` 通常只是模式常量，gate 未放行） | bot | 是 | `awaiting_acceptance_technical` |
| 10 | `failed`（核验失败/缺证据） | bot | 是 | `verification_failed` |
| 11 | `verifying` / `running` / `starting` / `queued` | bot | 是 | `live_execution` |
| 12 | `paused`（用户暂停，等待用户恢复；维持现状） | none | 否 | `paused` |
| 13 | 事实缺失或 `executionOwnership==='unknown'` 且状态无法证明结束 | bot | 是 | `unknown_facts` |

判定顺序**不是**上表顺序：保护性事实（真实人工请求 → 活动执行 → 未决停止回执）先判，任一成立就留在当前列表并保持对应责任人；三者都不成立时，签收 / 承接 / 已确认停止才退出。

事实来源核对：`goal-runner.clear()` 把用户停止的计划标为 `cancelled` 并把 runner 置 `idle`，`executionOwnership` 因此通常是 `unknown`；而 `session-cancellation` 的 `completed` 回执是在 `abort` + `waitForIdle` + `waitForPlanIdle` 之后才写入。所以“已确认停止”的权威事实是**完成回执**，不是 ownership：`unknown` 单独（含 `awaiting_outcome`、无回执）一律留在列表，不能当作结束。

### D3 禁止项

- 不得在 renderer/TUI 自建“隐含终态”：列表、计数、会话/详情必须消费 `followUp`，不再按 `status` 白名单过滤。
- 不得无条件隐藏 `result_ready`：普通结果仍留在当前列表，只是责任人为 bot，不显示“需要你确认”。
- 不得伪造 `accepted`：`followUp.owner='none'` 只表示退出当前待办，不改变原验收事实与未完成阶段。
- 不得用归档/静默渲染遮盖验收链路；历史结果、原核验与未完成事实保留。
- 缺权威事实时 fail closed（留在列表，责任人 bot），不得只凭文案推断“已被承接”或“用户已停止”。
- 不新增数据迁移；`~/.peer-agent` 历史数据不改写。

### D4 消费契约

- `projectWorkSession`（`packages/protocol/src/delegation.ts`）把 `followUp` 原样写入 `WorkSession`；不得二次推导。
- Desktop：宿主下发的会话记录带 `followUp`；`DrawerSession` 读取后由 `botWorkState.backgroundWork()` 用 `followUp.inCurrentList` 决定列表行与计数，旧记录缺字段时 fail closed（保留原有 `FOLLOW_UP` 兜底，仅对缺字段记录生效）。
- 详情与分组使用同一 `followUp`：`SessionDetail` 的 label / hint / question / ended 与 `drawerState.taskGroup` 只读 `followUp.owner/reason`，不再各自判 `status`；旧记录缺字段时才退回原状态表。

## 3. 回归用例矩阵（本次只编写，不执行）

| 用例 | 事实输入 | 期望 |
|---|---|---|
| 普通自动签收 | `result_ready`，非 confirm 门 | owner=bot，在列表，reason=`awaiting_acceptance_technical` |
| 真实人工门槛 | `result_ready`+`humanGate===true` | owner=user，在列表 |
| 核验失败/缺证据 | `failed` / `blockedReason` | owner=bot，在列表，不伪造 accepted |
| 替换完成 | `supersededBy` 存在且无活体/人工请求 | owner=none，退出列表，后续阶段不受影响 |
| 替换未完成 | 旧阶段 superseded + 新阶段 running | 旧 none；新 bot 在列表 |
| 用户停止（已确认） | `cancelled`+`cancellationPhase=completed`+`ownership=ended` | owner=none，退出列表 |
| 用户停止（回执未决） | `cancelled` 无回执 / `stopping` / `awaiting_outcome` | owner=bot，仍在列表 |
| 活动执行 | `running`+ownership=live | owner=bot |
| 未知停止回执/事实缺失 | `ownership=unknown`，状态无法证明结束 | owner=bot，fail closed |
| 交叉：承接 + 活体执行 | `supersededBy` 存在 + ownership=live | owner=bot，仍在列表（不误隐藏） |
| 交叉：承接 + 真实人工请求 | `supersededBy` 存在 + `waiting_user` / `humanGate` | owner=user，仍在列表 |
| 交叉：完成停止 + 执行体未知 | `cancellationPhase=completed` + ownership=unknown（回执权威） | owner=none，退出列表；`awaiting_outcome`/无回执才留在列表 |
| 交叉：历史签收 + 新核验失败 | `accepted` 事实 + `failed` | owner=bot，在列表（旧验收不掩盖新失败） |
| 详情/分组一致 | 同一 `followUp` | 详情 label/hint/question 与分组同源 |
| 重载投影一致 | 同一事实序列重放两次 | `followUp`、列表行、计数一致 |

## 4. 修改顺序与范围

1. 本 ADR（本文）。
2. `packages/protocol/src/task-overview.ts`：`followUp` 类型与判定，并入 `decideLifecycle`。
3. `packages/runtime-node/src/project-agent/session-supervisor.mjs`：宿主唯一人工门事实 `humanGateOf(plan)`（`decideSessionAcceptance(...).mode==='confirm' && closeGatePassed`），`project()` 与 `summaries()` 共用同一份判定。
4. `packages/protocol/src/delegation.ts`：`WorkSessionConversationMeta.resultConfirmationRequired` → `LifecycleFacts.humanGate`；`WorkSession.followUp` 由 `projectWorkSession` 原样透传。
5. `apps/desktop/renderer/src/project-agent/state/drawerState.ts`：读取宿主 `followUp`；`inCurrentList` 与 `owner` 不一致时以 `owner` 为准；`taskGroup` 按 `followUp` 分组。
6. `apps/desktop/renderer/src/project-agent/state/botWorkState.ts`：列表与计数消费 `followUp.inCurrentList`；未列入旧状态表的状态排在已知状态之后。
7. `apps/desktop/renderer/src/project-agent/drawer/SessionDetail.tsx` + `packages/i18n/src/index.ts`：详情 label / hint / question / ended 消费 `followUp`；新增 `projectAgent.chat.work.resultSettling`（技术收口不再写成“待你确认”）。
8. 用例：`packages/protocol/src/follow-up-responsibility.test.ts`、`apps/desktop/renderer/src/project-agent/state/botWorkState.followUp.test.ts`、`apps/desktop/renderer/src/project-agent/state/drawerState.followUp.test.ts`。

### 4.1 生产与消费路径（已逐段核对）

| 路径 | 入口 | 是否同一事实 |
|---|---|---|
| 当前列表 | renderer `clientApi.projectAgentListSessions` → IPC `project-agent:list-sessions` → `application-service.listSessions` → `sessions: supervisor` → `supervisor.list()` → `.map(project)` | 是（无字段白名单，`followUp` 原样过通道） |
| 详情/抽屉 | `supervisor.get()` → `project(plan)` | 是 |
| 批量读取 | `supervisor.listByWorkspaceIds()` → `project(plan)` | 是 |
| 轮次花名册 | `supervisor.summaries()` → 裸 `projectWorkSession`（已补 `humanGateOf`） | 是 |
| 历史重载 | `useBotWorkSessions` 每次挂载/变更都重新向宿主查询，renderer 无本地会话缓存 | 是 |


## 5. 未验证 / 剩余限制

- 本轮遵守 AGENTS.md Validation Scope：只编写用例，**未执行**测试、typecheck、build、产品截图回归。
- 宿主 Electron 侧实际下发字段需在发布前用真实运行核对；旧历史记录缺 `followUp` 时走 fail-closed 兜底，属已知过渡态。
- 真实模型行为、安装版升级、长期使用不在本轮覆盖。


本批监督实施采用本决策中必要的共享责任投影及消费者；实际代码、验证范围与未覆盖事项见[实施回执](../../playbook/v0.1.0/code-structure-refactoring.md)。当前列表归属不等同于真实运行数；运行计数仍只统计实际活动执行。

## 6. 已交回结果的用户取消（2026-10-29）

手工试用发现：用户明确要求“不再需要，直接清理掉”，两次 `control_work(cancel)` 实际返回 `work_already_ended`；对应计划均为 `completed`、无签收事实，宿主仍投影为 `result_ready`。只读核对宿主协调读模型发现，两件工作此前都已是 `cancelled + stopScope=work`，并有旧 `lastControl` 成功回执，子任务却没有取消回执。工作调度终态与跟进责任终态不同；拒绝取消工作、跳过 `result_ready/failed` 子任务、以及取消器拒绝 `completed` 三处判断共同形成不可退出的待办。

本次按 A 级扩展既有取消契约，不新增归档能力或 renderer 隐藏状态：

- 当前用户可以通过既有 `control_work(cancel)` 取消所指整件工作的未签收子任务，包含已交回结果、核验失败、未确认停止的任务。`delivered/cancelled` 工作状态不再阻止这项操作；`coalesced` 不追踪到另一件工作。
- `cancel_session` 沿同一个取消器处理单条未签收结果。已签收结果保持原事实；不把放弃结果写成签收或核验通过，不删除历史会话、原报告、核验记录和 Evidence。已完成/失败计划的隔离成果通过既有 `preserveArtifacts` 保留。
- 宿主先关闭工作准入和执行泵，再 abort、等待 Runner 与执行调度器停止，核对不确定副作用，最后写既有 `cancellation.phase=completed`。计划此时转为 `cancelled`，表示委托已取消；此前实际执行与核验记录保留。仅凭计划 `completed`、Runner 残留字符串或工作 `delivered` 都不能跳过停止确认。
- 有未确认执行结果时仍是 `awaiting_outcome`，保留当前列表与 Bot 跟进责任，不回报清理成功。部分取消失败时保留关闭的准入与 `pendingControl`；同一输入只继续未完成子任务，重复成功操作幂等。
- 旧 `lastControl` 回执不能独自证明取消已落实到子任务；重放取消前仍核对所绑定的未结清结果。旧控制器漏掉的结果走正常停止链补齐，不改真实运行数据或伪造迁移成功。
- `coordinate_work(cancel)` 同样不能把 `result_ready` 当成无需处理的成功终态；撤回已交回结果要求当前真实用户输入，普通事件唤醒不能自行放弃结果。替换/交接对既有结果的复用语义不变。
- 当前列表、计数、详情、Desktop/TUI 继续消费原有 `cancelled + completed receipt → followUp.owner=none`，无第二套列表规则。活动执行与未决停止优先级不变。

体验契约：用户目的是停止并移出当前跟进，历史仍可查；处理中/结果未知由 Bot 负责，真实停止回执后才退出。草稿、焦点、阅读位置与动效链不变。恢复沿现有取消回执及范围回执，不重跑原任务、不自动验收。初次交付按日常约定只做源码与 diff 审阅并补用例；用户随后明确要求提前运行及跟进 CI，实际范围以 §6.1 为准，不沿用此前候选的通过结论。

### 6.1 用户要求的合并前验证（2026-10-29）

- 代码候选：`5bbf27dbe2b83f807a24630cbf08450d0d64f0b0`（[代码 PR231](https://github.com/ly-ccx/Peer-Agent/pull/231)）。
- Node `25.9.0` 下执行三个变更文件：`work-control.test.mjs`、`coordination-lifecycle.test.mjs`、`session-supervisor.test.mjs`（均在 `packages/runtime-node/src/project-agent/`）。109 项通过，0 失败、0 取消、0 跳过，包含全部新增用例和同文件既有回归。
- 新增场景覆盖旧成功回执漏处理、停止前保留当前任务、结果未知与同输入重试、失败/旧取消记录结清、历史核验保留、当前用户限制、重复取消、无关任务与已签收结果隔离。
- [CI run 40812716318](https://github.com/ly-ccx/Peer-Agent/actions/runs/40812716318)：macOS/Ubuntu 均为 success，完整构建、类型、架构、全量测试与对应平台 Electron 冒烟全部通过；日志未发生失败文件重试。两项 notice 分别是 GitHub runner 容量和 Ubuntu 镜像迁移提示，不是代码失败。
- 知识仓没有已配置的 CI workflow，内容/diff 自审；本轮是实现者自审，非独立审阅。真实模型实际清理、安装包、完整产品截图与读屏仍未覆盖，不把脚本通过当成这些验收。

## 7. 撤回委托与历史执行结果分离（2026-10-29）

再次真实试用仍有一条任务不能退出：工作已取消，子任务保留一条旧 Bash 测试调用的 `uncertainDispatches`。该调用有 Shell 产物结束时间但无退出码，会话只保留 `cancelled_outcome_unknown`，不能证明测试成功；用户重复取消实际得到 `execution_outcome_unknown`，协调取消又被 `work_execution_stopped` 拒绝。

此前错误前提是：**撤回委托之前必须核实每条历史工具调用的副作用。** 四方职责因此失衡：用户的撤回权被挂起；主 Bot 被分配了可能永远无法完成的追溯责任；本机停止控制不能独立收口；Evidence 被迫充当委托取消门。移除这项责任绑定，不移除未知事实或执行准入保护。

本节修订 §6 中“结果未知一律继续占当前列表”的规则，其他不变量保留：

- 当前真实用户通过现有取消工具撤回指定委托时，宿主绑定 workspace、父会话、session、plan、当前 canonical user_input 的 anchor/inputId。模型参数不能自带这份证明；错误作用域、助手文字、网页、事件唤醒不能生成撤回事实。
- 宿主仍须关闭准入、暂停执行泵、abort 并等待受管回合/调度器收口。仍有真实活动执行、停止失败、租约丢失或未确认的当前执行时，不得宣布取消完成或退出当前列表。
- 受管回合停止后，可完成**委托撤回**，即使历史工具结果未知。既有取消回执增加 `withdrawal` 来源引用与 `disposition=user_withdrawn`，`evidenceCalls` 保留未知调用身份，`preserveArtifacts=true`。`completed` 此时只证明撤回控制已应用，不证明历史工具成功、所有外部效果停止、回滚完成或验收通过。
- 原 `uncertainDispatches`、预算、工具/会话记录、原核验与 Evidence 均不清除，不重放旧命令。未来执行仍受原未知结果门约束。自动取消、替换、交接和续跑没有当前用户撤回事实时，继续保留 `awaiting_outcome`，不能借用本例外。
- 共享责任投影增加 `user_withdrawn` 原因；实际 live 与未完成停止仍先保护，明确撤回的委托退出当前列表。详情保留“撤回时历史结果未知，核实前不会重复执行”的提示；主 Bot 汇报必须区分委托已撤回与历史结果未知。
- 已停止工作或已取消 mandate 可接受当前用户的追加取消收口，仍校验版本、来源和 session 范围；不重新打开执行准入、不允许 replace/resume 等其他动作穿过停止边界。重复请求及重启沿已有取消操作和持久化来源引用恢复，不复活任务。

实现沿原 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence 链，不新增模型能力、存储目录、隐藏执行通道或 renderer 业务真源。新增回执字段为可选字段，旧未知账本保留；旧宿主不据此获得执行权。前端仅展示宿主事实，草稿、焦点、阅读和动效规则不变。

验证必须包括本次真实记录的形态：已取消工作、旧 Bash 未知调用、无活动回合、当前用户再次撤回；结论是委托退出列表且未知账本保持原样，不能以手工清空预算来模拟核实。另覆盖无当前用户/伪来源/跨作用域、活动执行/停止失败/租约丢失、重启恢复、幂等、已签收与无关任务隔离。此前 PR231 的 109 项与 CI 通过不证明本节已经通过。

### 7.1 本次验证与限制

- 沿用户此前要求运行取消新增用例的范围，先将真实遗留形态加入回归；旧实现下四项用例按预期失败，包括未知 Bash 撤回、已停止工作追加取消、来源范围与共享责任投影，保留原失败记录。
- 修复后 Node 25.9.0 下 222 项相关回归全部通过，0 失败/取消/跳过。覆盖协议、Supervisor、协调 kernel/lifecycle、Delegation Provider、旧核验未知结果保护、抽屉状态；三个模型工具入口均经真实 Provider → Supervisor 验证，不靠 stub 直接返回取消成功。
- protocol、i18n、runtime-node 构建及 Desktop 类型检查通过；工具说明和 storage worker 源码已按原生成链更新。当前用户撤回后未知账本未清空，自动替换/续跑仍不能跳过它，停止失败和租约丢失的恢复不会重放命令。
- 本轮为实现者自测及内容/diff 自审，非独立审阅；尚未完成本次远端完整 CI、完整产品截图/交互回归、真实模型清理或安装包验收，不继承上一批 CI 结论。真实用户任务记录只读排查，没有直接改写其计划、账本或会话来模拟成功。

首轮 CI 补记：双平台完整构建通过，workspace 类型检查发现 TUI 单参数取消调用被新增上下文参数的必填声明阻塞（TS2554）。已保持上下文参数可选，原调用无当前用户证明时继续保留未知结果门；runtime-node 重建与 TUI 类型检查通过，三项取消兼容回归通过。该修正不改变撤回语义，完整 CI 以代码 PR233 后续结果为准。

### 7.2 撤回终态不能被旧中断与旧接管标记复活

再次试用证明 §7.1 的测试漏掉了真实历史组合：旧 `runner.interruption`、失败叶子、旧 `takeover.phase=stopping` 同时存在。撤回原生工具返回成功、回执已 completed/user_withdrawn，但 GoalPlanStore 的 persist 仍把显式 cancelled 派生回 interrupted，随后投影又被旧 takeover 推成 starting，当前列表继续计数。这不是刷新延迟，不能把已有回执当作链路闭环的证明。

- 持久化规则必须保住显式取消终态：历史 interruption 与失败叶子仍保留，但不能在取消或后续清理/进度写入中把计划改回 interrupted/executing。
- 共享生命周期决策必须承认宿主完成取消回执；没有真实活动执行时，旧 interruption/takeover 字段不能覆盖取消。仍有真实 live 事实时保留当前责任，不凭持久化 Runner 字符串制造活体或隐藏活动。
- 生命周期的 status、actionRight、nextAction、statusLabel、cancelable 必须同源：确认取消后是终态、无执行下一步，不得保留旧 interruption 对应的 paused/resume 提示。
- 取消接口成功的后置条件包括同一权威投影已为 cancelled 且退出当前责任；尚未收口必须返回结构化 pending/error，不能只因写入过回执就回报整件工作已完成。
- 用真实组合验证原生 Provider 取消、落盘原值、get/list/summary/批量读取、索引与冷重载、后续进度/叶子写入、客户端任务分组和计数。已有完成回执的历史记录沿宿主恢复与共享投影正确退出；不要求用户再发相同指令，不手工改运行数据。

实际本地窗口必须核对该任务已退出当前列表、历史仍保留且未知账本未消失；在这一步完成前不再声称当前故障已解决。原 222 项通过记录只证明原测试范围，不涵盖本节遗漏。

### 7.3 历史组合修复与实际窗口核对（2026-10-29）

- 代码后续候选为 `22fd45b94db53e431199ab364dfc26a30dd956c2`（[PR233](https://github.com/ly-ccx/Peer-Agent/pull/233)）。四项真实历史组合用例先复现原故障：原生工具返回成功，落盘为 interrupted，投影为 starting。修复持久化与共享决策优先级后，359 项相关回归通过，零失败、取消或跳过；包含原生 Provider、get/list/summaries/批量接口、磁盘与索引、冷重载、后续叶子/进度写入、实际客户端解析及计数。
- 已完成回执而旧计划为 interrupted 的记录，冷启动通过原生 cancellation recovery 重验已接纳来源并完成收口，无新增用户输入、无命令重放。新增清理阶段活动执行竞争用例确认：责任仍在当前列表时返回 `cancellation_not_settled`，不发成功事件。
- 实际本地开发版加载上述运行逻辑。对 kxt 原记录只读核对：原计划从 interrupted/version25 经宿主恢复为 cancelled/version28，完成回执保留且 cleanupPending=false；原未知账本和预算、失败叶子及中断字段与恢复前完全相同，无签收事实。没有直接编辑用户计划、预算或会话来模拟成功。
- 实际窗口中“当前任务（1）”已移除（空列表收起），历史任务仍显示“已取消”；任务信息显示撤回时仍有一项未知执行且禁止重复执行。额外发现详情的责任文案使用旧 reason 白名单，遗漏 user_withdrawn；现直接消费宿主 followUp.owner，显示“继续追问”，不再分配后续工作。详情新增回归先失败、后四项通过；protocol 与 Desktop 类型检查通过。
- 本轮为实现者自测及实际窗口自审，非独立审阅；未替用户向真实模型发新消息，未验收安装包、全产品交互/截图、读屏、IME 或减少动效。源码修正沿原组件、文案、焦点与动效，不新增交互机制。
- 新增协议用例缺少必填 planId/title 曾令远端 Typecheck 失败，现已补完整公开快照并本地通过20项协议用例；最终双平台完整 CI 待该候选结果，不将359项局部回归替代远端或发布验收。

### 7.4 最终候选五字段一致性与加载核对

- 最终代码候选为 `e6ba6f4f6a1159586bd5c61fb723e74c097bab2c`。补足共享 presentation 的取消终态：旧 interruption 曾在 status 已 cancelled 时仍给 actionRight=paused、nextAction=resume。新增断言先失败，修复后77项协议回归和类型检查通过；原生四种查询也检查 terminal/none/已取消，取消成功后置条件同步要求行动权终态。
- 跨层计数用例归 Desktop 测试侧，原生 fixture 使用编译后宿主模块；runtime 测试不依赖 renderer 资源类型。96项监督回归与完整跨层用例通过，runtime-node 重建、runtime-node/Desktop 类型检查通过。
- 最终标准开发启动重新构建依赖并加载该候选。加载后10项关键回归通过，零失败/取消/跳过，包含真实 Provider、磁盘/索引/冷恢复、所有查询、实际客户端计数、活动执行竞争和详情标签。真实旧计划仍为 cancelled/version28，完整预算（含未知数组）、失败叶子、中断字段与恢复前相同，无签收事实。
- 对原持久记录调用实际 `projectWorkSession`（含完整 origin 元数据）的只读核对返回 cancelled/terminal/none/已取消/cancelable=false，followUp 为 none/false/user_withdrawn。最终本地窗口复查当前任务为空，历史已取消保留；未发新消息、未直接改运行数据或重放原命令。历史助手原文保留，当前状态来自结构化宿主事实。
- 前一候选 `6fcb9c13` 的 [CI run40827446722](https://github.com/ly-ccx/Peer-Agent/actions/runs/40827446722) 双平台全部通过。最终候选 `e6ba6f4f` 的 [CI run40829037910](https://github.com/ly-ccx/Peer-Agent/actions/runs/40829037910) macOS/Ubuntu 均为 success，完整构建、类型、架构、全量测试及对应平台 Electron 冒烟均通过；本节以最终候选实际结果为准。按用户要求先合知识 PR91，再合代码 PR233，不发布新版本。
- 仍为实现者自测与窗口自审，不是独立评审或完整产品/安装包验收；真实模型新请求、读屏、IME及减少动效覆盖限制沿§7.3。
