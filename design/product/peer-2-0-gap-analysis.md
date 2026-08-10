# Peer 2.0 多任务工作台 Gap 分析基线

> 日期：2026-08-07
> 依据：`design/visual/previews/peer-2-0/index.html` + `design/product/peer-2-0-product-system.md` 对照 `peer_agent` 代码仓实测
> 用途：作为 TaskOverview 契约、导航骨架、数据投影落地的唯一基线

## 1. 方法与结论速览

对原型三个一级页面（首页/任务/历史）+ 两个二级视图（Task Canvas / Result Review）逐一拆解所需数据与交互，对照代码仓实测现状，分为：

- **已有**（代码已存在，可直接复用）
- **需改造**（存在但不满足投影语义）
- **缺失**（代码仓中 0 匹配）

总体结论：**后端事实源（GoalPlan 状态机、IPC、广播）已就绪 70%，但前端是"单会话中心"结构，无跨任务聚合层，无页面路由。Gap 集中在协议层的"行动权投影"定义与 renderer 的"多页面骨架"。**

---

## 2. 全局事实：代码仓现状

| 事实 | 证据 | 状态 |
|---|---|---|
| GoalPlanStatus 9 态（drafting/awaiting_approval/approved/accepted/executing/paused/completed/cancelled/failed） | `packages/protocol/src/goal.ts:20-29` | ✅ 已有 |
| GoalRunnerStatus 10 态（idle/running/compacting_context/resuming_after_compaction/paused/exploring/blocked/budget_exhausted/completed/failed） | `packages/protocol/src/goal.ts:278-287` | ✅ 已有（推进态的事实源） |
| ExecutionStatus 仅 6 态（pending/running/completed/failed/cancelled/waiting_user），无 blocked/awaiting_approval | `packages/protocol/src/goal.ts:54` 引用 execution.ts | ⚠️ 需改造：审批态在 Plan 层不在 Task 层 |
| GoalAskUserReason 已定义 8 类原因（ambiguous_goal/product_decision/high_risk/irreversible/missing_permission/missing_credentials/verification_conflict/scope_drift） | `packages/protocol/src/goal.ts` | ✅ 已有（可复用为"待确认原因"） |
| `goalPlans:list` IPC handler | `apps/desktop/electron/main/ipc/register-goal-ipc.mjs:39` | ✅ 已有 |
| `goalPlans:changed` 双通道广播 | `apps/desktop/electron/main/goal-plan-change-bridge.mjs:18` + `main.mjs:399` (broadcastToAllWindows) | ✅ 已有 |
| 任务事件通知中介 | `apps/desktop/electron/main/task-notification-broker.mjs:209` | ✅ 已有（可挂投影） |
| Automation 双层状态机：Definition 6 态（draft/active/paused/completed/disabled/archived）× Run 12 态（scheduled/queued/preparing/running/waiting_permission/waiting_user/succeeded/failed/cancelled/skipped/timed_out/blocked） | `packages/runtime-node/src/automation-store.mjs:15-20` | ⚠️ 需改造：Definition 与 Run 需联合判断 |
| TaskOverview 跨任务聚合 | 全仓 0 匹配 | ❌ 缺失 |
| renderer 页面路由 | `App.tsx:64` 仅 `type AppPage = 'chat' \| 'automations' \| 'tools' \| 'settings'`，纯 useState | ❌ 缺失（首页/任务/历史是第 5-7 页） |
| Result Package / 交付包 | 全仓 0 匹配 | ❌ 缺失 |
| Conversation 终态/归档字段 | `archivedAt` 搜索仅命中归档 artifact/邮件，会话层无 | ❌ 缺失 |

---

## 3. 首页（Home）Gap

原型要素：三栏行动权投影（需要你处理 / Peer 正在推进 / 结果待验收）+ 统计条（活跃 N · 待验收 N · 今日交接 N）+ 跨任务对话条 + 空态。

| 原型需求 | 现状 | Gap |
|---|---|---|
| 三栏按行动权分桶 | ❌ 无 | **缺失**：需定义"行动权投影"契约，把 GoalPlanStatus × Automation Run status × Conversation 状态统一映射到 `needs_you / peer_advancing / result_ready` |
| 卡片：标题/Workspace/标签/状态/下一步 | ⚠️ 部分 | **需改造**：GoalPlan 有 title/planId/status，但无 workspaceId 关联（conversation 才有），无"下一步行动"文本字段 |
| 统计条聚合 | ❌ 无 | **缺失**：需跨任务聚合接口 |
| 卡片点击深链到任务/验收 | ❌ 无 | **缺失**：需"从首页跳到指定 conversation + 打开 GoalPlan 面板"的路由动作 |
| 待我处理 = awaiting_approval + waiting_user | ✅ 可推导 | 已有 `useAwaitingGoalPlans` 先例：只认 `plan.status`，renderer 不解析自由文本 |
| 结果待验收 = Result Package 就绪 | ❌ 无 | **缺失**：Result Package 概念不存在（全仓 0 匹配），只有 manual criterion 确认门 |

---

## 4. 任务页（Tasks）Gap

原型要素：过滤器（全部/待我处理/Peer 推进中/待验收/已暂停）+ 任务行（标题/Workspace/标签/状态/Plan 进度 x/y/最近活跃时间/动作按钮）。

| 原型需求 | 现状 | Gap |
|---|---|---|
| 列出所有未结束任务 | ⚠️ 部分 | **需改造**：`goalPlans:list` 按 conversationId 查单会话，无"跨会话列出所有活跃 Plan"接口 |
| Plan 进度 x/y | ✅ 已有 | GoalPlan 有 `progress.percent` 和 tasks 树（goal.ts:721） |
| 已暂停状态 | ⚠️ 部分 | **需改造**：GoalPlanStatus 有 `paused`，但 Automation Run 无对应态；需统一定义"任务级暂停"语义 |
| 最近活跃时间 | ⚠️ 部分 | **需改造**：GoalPlan 有 `updatedAt`，但无"最后活动"跨模型统一字段 |
| 动作按钮（查看/继续/处理/验收） | ❌ 无 | **缺失**：需定义任务级动作协议（批准计划/恢复暂停/打开验收） |
| 跨 Workspace 显示 | ❌ 无 | **缺失**：当前 goalPlans 查询需 conversationId，无 workspace 维度聚合 |

---

## 5. 历史页（History）Gap

原型要素：终态过滤器（全部/已验收/已归档/已取消/失败）+ 终态时间 + 动作（重开结果包/创建新 Run）。

| 原型需求 | 现状 | Gap |
|---|---|---|
| 终态任务列表 | ❌ 无 | **缺失**：Conversation 无终态字段；GoalPlan 有 completed/cancelled/failed，但无"已验收/已归档" |
| 已验收（accepted） | ❌ 无 | **缺失**：代码仓只有"人工确认 manual criterion"事件，无任务级"验收"状态 |
| 已归档（archived） | ❌ 无 | **缺失**：Conversation 无 archivedAt；仅 artifact 有归档概念 |
| 终态时间 | ✅ 部分 | GoalPlan 有 `updatedAt`，Automation Run 有 `completedAt` |
| 重新打开结果包 | ❌ 无 | **缺失**：Result Package 不存在 |
| 同一任务创建新 Run | ⚠️ 部分 | **需改造**：Automation 支持手动运行（automationsRunNow），但 Goal 模式无"在同一会话再开一个 Run"的原语 |

---

## 6. Task Canvas（二级视图）Gap

原型要素：左侧节点流（Goal/Decision/AgentRun/Artifact/Evidence）+ 右侧节点详情。

| 原型需求 | 现状 | Gap |
|---|---|---|
| 节点类型：Goal | ✅ 已有 | GoalPlan.goal |
| 节点类型：Decision | ⚠️ 部分 | **需改造**：只有 `HumanConfirmationDecision`（批准计划用），无任务内"决策点"节点 |
| 节点类型：AgentRun | ✅ 部分 | `packages/runtime-node/src/goal-runner-explorers.mjs` 有 Explorer 结构；Automation 有 Run |
| 节点类型：Artifact | ❌ 无 | **缺失**：GoalPlan 协议无 Artifact 节点类型（artifact 在 Evidence Index 里，但不挂在 Plan 树上） |
| 节点类型：Evidence | ✅ 已有 | `packages/runtime-node/src/evidence-index.mjs` 登记，但前端未可视化 |
| 节点状态环 | ⚠️ 部分 | **需改造**：GoalTask 有 ExecutionStatus，但无 Decision/Artifact 的状态 |

---

## 7. Result Review（二级视图）Gap

原型要素：Result Package（deliverables/checks/evidence/剩余风险）+ Plan/Browser/Files/Documents 标签 + USER ACCEPTANCE 底部条。

| 原型需求 | 现状 | Gap |
|---|---|---|
| Result Package 对象 | ❌ 无 | **缺失**：全仓 0 匹配；需新增协议类型 |
| 交付物清单 | ❌ 无 | **缺失**：无结构化"deliverables"字段 |
| 验收检查项 | ⚠️ 部分 | **需改造**：GoalPlan 有 successCriteria 与 manual 确认，但无"打包验收"流程 |
| Browser 证据回放 | ⚠️ 部分 | `computer-use` 有 Observation/Action/Assertion/Evidence，但未组装为"验收视图" |
| Files/Documents 标签 | ❌ 无 | **缺失**：无按任务聚合的文件产物视图 |
| USER ACCEPTANCE 动作 | ⚠️ 部分 | **需改造**：现有 manual criterion 确认是单条确认，无"整包验收"动作 |

---

## 8. 关键架构约束（红线）

基于 `AGENTS.md` 与代码仓现状，落地时必须遵守：

1. **投影必须走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence 链**，不得为首页/任务/历史开旁路。
2. **renderer 只消费后端事实**：像 `useAwaitingGoalPlans` 一样只认 `plan.status`，不解析模型文本，不在前端维护任务状态副本。
3. **不大爆炸重写**：现有 Conversation/GoalPlan/Workbench 保留，首页/任务/历史是新增的第 5-7 个 AppPage，通过 `goalPlans:changed` 等已有广播驱动更新。
4. **Task 身份由 Conversation 承载**（产品文档 §5.1）：不新建父层级 Project/里程碑。

---

## 9. 推荐落地顺序

| 阶段 | 交付物 | 依赖 |
|---|---|---|
| 0 | 定义 TaskOverview / 行动权投影契约（protocol 层，含 §11 映射表） | 无 |
| 1 | 后端聚合接口 `taskOverview:list` + 广播 | 阶段 0 |
| 2 | renderer 新增 home/tasks/history 三页面骨架 | 阶段 0 |
| 3 | 首页接真数据 + 深链 | 阶段 1+2 |
| 4 | Result Package 协议与验收流程 | 可与 2-3 并行 |
| 5 | Task Canvas 节点投影 | 阶段 4 之后 |

---

## 10. 风险与待决问题

1. ~~GoalPlan 与 Automation Run 双状态机如何统一映射到"行动权"？~~ **已解决，见 §11**。
2. **"已验收/已归档"状态加在哪一层？** —— GoalPlan 加字段，还是新建 Task 身份层？
3. **Result Package 是持久化对象还是查询时组装？** —— 影响 Evidence 存储设计。

---

## 11. 行动权投影映射契约（阶段 0 核心）

> 解决 §10 待决问题 1。这是首页三栏与任务页过滤器的唯一事实来源。

### 11.1 涉及的状态机（3 套 + 1 个概念）

| 状态机 | 枚举 | 事实源 | 说明 |
|---|---|---|---|
| GoalPlanStatus | drafting / awaiting_approval / approved / accepted / executing / paused / completed / cancelled / failed | `goal.ts:20-29` | 计划生命周期（含审批门） |
| GoalRunnerStatus | idle / running / compacting_context / resuming_after_compaction / paused / exploring / blocked / budget_exhausted / completed / failed | `goal.ts:278-287` | 自驱 Runner 实时态（推进中细节在此） |
| AutomationDefinition.status | draft / active / paused / completed / disabled / archived | `automation-store.mjs:15` | 自动化定义生命周期 |
| AutomationRun.status | scheduled / queued / preparing / running / waiting_permission / waiting_user / succeeded / failed / cancelled / skipped / timed_out / blocked | `automation-store.mjs:17-18` | 单次运行态 |
| Result Package | （概念，尚无状态字段） | — | 待 §10 问题 2/3 决定 |

### 11.2 投影目标：TaskActionRight（行动权）

```typescript
type TaskActionRight = 'needs_you' | 'peer_advancing' | 'result_ready' | 'paused' | 'terminal';
```

### 11.3 映射规则表（判定顺序：从上到下，首个命中生效）

| # | 来源状态 | 行动权 | 下一步行动 | 规则说明 |
|---|---|---|---|---|
| 1 | GoalPlan `awaiting_approval` | needs_you | 批准或驳回计划 | 计划审批门 |
| 2 | GoalPlan `drafting` | needs_you | 确认目标范围 | intake 未决 |
| 3 | AutomationRun `waiting_permission` | needs_you | 授权权限 | 对应 `GoalAskUserReason.missing_permission` |
| 4 | AutomationRun `waiting_user` | needs_you | 回答问题 | 对应 `GoalAskUserReason` 其余 7 类 |
| 5 | GoalRunner `blocked` / `budget_exhausted` | needs_you | 决策：调整范围或追加预算 | Runner 主动求助 |
| 6 | GoalPlan `completed` 且未验收 | result_ready | 验收结果包 | 依赖 Result Package 概念落地（§10 问题 2） |
| 7 | AutomationRun `succeeded` 且未验收 | result_ready | 验收运行结果 | 同上 |
| 8 | GoalPlan `executing` | peer_advancing | — | 计划已批准，正在推进 |
| 9 | GoalRunner `running` / `compacting_context` / `resuming_after_compaction` / `exploring` | peer_advancing | — | Runner 活跃中 |
| 10 | AutomationRun `scheduled` / `queued` / `preparing` / `running` | peer_advancing | — | 自动化运行中 |
| 11 | GoalPlan `accepted` / `approved`（Runner 未启动） | peer_advancing | — | 排队等 Runner |
| 12 | GoalPlan `paused` | paused | 继续 | 用户主动暂停 |
| 13 | GoalRunner `paused` | paused | 继续 | 同上 |
| 14 | GoalRunner `idle` 且 Plan `executing` | paused | 查看 | Runner 空闲但计划未完（异常态，需诊断） |
| 15 | AutomationDefinition `paused` / `disabled` | paused | 启用 | 定义级暂停 |
| 16 | GoalPlan `completed`（已验收）/ `cancelled` / `failed` | terminal | — | 进历史页 |
| 17 | AutomationRun `succeeded`（已验收）/ `failed` / `cancelled` / `skipped` / `timed_out` / `blocked` | terminal | — | 进历史页 |
| 18 | AutomationDefinition `completed` / `archived` | terminal | — | 定义级终态 |

### 11.4 关键设计决策

1. **Plan 态优先于 Runner 态**：`awaiting_approval`/`drafting` 时即使 Runner idle 也算 needs_you，因为阻塞点在用户。
2. **needs_you 内部分桶**：首页"需要你处理"栏按 `GoalAskUserReason` 细分为"待批准计划"（rule 1-2）、"待授权/待回答"（rule 3-4）、"待决策"（rule 5），顺序即原型中的"需要你 · 待确认 · 等待权限"三类卡片。
3. **paused 单列**：任务页过滤器"已暂停"对应 rule 12-15；首页不展示 paused（除非用户点开"查看全部"）。
4. **terminal 判定的"已验收"修饰**：rule 6/7 与 16/17 的区别在于是否完成 USER ACCEPTANCE，该状态字段待 §10 问题 2 落地后补充；过渡期可先用 `GoalPlan.completed` 一律进 result_ready，由用户在 Result Review 页手动归档。
5. **异常态兜底**：rule 14 是防御性规则，Runner idle + Plan executing 理论不应出现，若出现说明 Runner 崩溃或丢消息，应提示诊断而非静默。

### 11.5 过渡期简化（第一版可裁量）

若 Result Package 与 USER ACCEPTANCE 尚未落地，第一版可：
- 把 rule 6/7 的 result_ready 改为"GoalPlan.completed 即进历史页，由用户在历史页标记验收"；
- 首页只保留 needs_you / peer_advancing 两栏，第三栏用"最近完成"占位；
- 待 §10 问题 2/3 解决后再启用完整三栏。

---

## 12. 本文档变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-07 | 初版（§1-§10） |
| 2026-08-07 | 修正状态机枚举（GoalPlan 9 态、Runner 10 态、Automation 双层），新增 §11 行动权投影映射契约 |
