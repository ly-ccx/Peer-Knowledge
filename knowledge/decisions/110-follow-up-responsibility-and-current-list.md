# ADR 110：跟进责任收口与当前待办列表判定

创建时间：2026-10-28
最后更新：2026-10-29
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

体验契约：用户目的是停止并移出当前跟进，历史仍可查；处理中/结果未知由 Bot 负责，真实停止回执后才退出。草稿、焦点、阅读位置与动效链不变。恢复沿现有取消回执及范围回执，不重跑原任务、不自动验收。日常只做源码与 diff 审阅并补回归用例；测试、构建、截图、真实模型及安装包覆盖待发布，不沿用此前候选的通过结论。
