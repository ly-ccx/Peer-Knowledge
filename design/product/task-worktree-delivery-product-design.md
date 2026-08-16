# Task 独立 Worktree 与跨仓交付产品方案

> 创建时间：2026-08-12
> 最后更新：2026-08-13
> 文档状态：现状校准后的目标方案 / 待分期实施
> 代码审计基线：`peer_agent` / `PeerAgent/0.0.4` / `aa770e8`（2026-08-12）
> 阅读约定：第 2 章描述当前真实实现；第 4 章起描述目标态，未明确标注“已实现”的能力均不可视为当前产品事实
> 适用范围：Peer Desktop、Agent / Plan / Automation 运行、Task Center、本地 Git 仓库
> 关联代码仓：`peer_agent`（本知识库只存知识，代码改动一律在该仓落地）
> 关联文档：
> - `design/product/agent-mode-default-and-adaptive-planning.md`
> - `design/product/goal-mode-ultrathink-workflow.md`
> - `design/product/goal-quality-review-repair-loop.md`
> - `design/product/automation-scheduled-agent-product-design.md`
> - `design/product/status-bar-task-center.md`
> - `design/product/workspace-sandbox-evolution-comparison.md`
> - `knowledge/decisions/27-workspace-switch-and-cross-workspace-running.md`
> - `knowledge/specifications/15-goal-plan-lifecycle-governance.md`

---

## 1. 方案摘要

本文在 Peer 当前产品能力之上提出代码任务隔离与交付目标模型，不把尚未实现的交付链误写成现状：

> **当前 Peer 已有 GoalPlan 治理、Goal 级跨工作区执行、Automation 独立 Worktree、TaskOverview 行动权投影和 Goal 结果验收；目标是复用这些基础，把执行型代码任务升级为带明确目标分支、独立任务分支与 Worktree、并可通过合并队列验收交付的工作单元。**

目标态的对象关系是：Conversation 作为交流与回流入口，Goal 作为目标和跨仓路由边界，执行型代码任务作为单仓执行与交付单元。这里的“代码任务”不等同于当前 GoalPlan 中所有叶子 `GoalTask`；第 5 章将给出兼容现有模型的渐进物化规则。

它解决五个问题：

1. 多个 Agent Task 同时修改代码时互相覆盖、切分支或污染用户工作目录；
2. 错误地固定从 `main` 创建任务，导致忽略实际开发集成分支上的最新改动；
3. 用户不知道任务基于哪个仓库、哪个分支，以及最终交付到哪里；
4. 从知识仓发起、到代码仓落地时，把入口工作区误当成交付仓库；
5. Worktree 只隔离执行，却没有解决并发任务依次合并时的陈旧基线与语义冲突。

P0 的核心规则：

- 不是每条消息都创建 Goal 或 Task；普通问答只存在于 Conversation；
- 一个执行型叶子 Task 最多写一个 Git 仓库；
- 一个代码 Task 自动绑定一个任务分支和一个 Worktree；
- Task 从它明确绑定的目标分支创建，并最终交付回该分支，不固定为 `main`；
- 分支必须以“仓库 + 分支”成对展示和保存；
- 同一仓库、同一目标分支的 Task 可以并行执行，但必须串行进入合并队列；
- 自动合并是“满足门禁后自动尝试”，不是无条件强推；
- 跨仓 Goal 可以有多个独立交付，但不存在跨 Git 仓库原子提交。

---

## 2. 当前产品与代码基线

本章只陈述 2026-08-12 在 `peer_agent` 分支 `PeerAgent/0.0.4`、提交 `aa770e8` 上由代码与测试确认的事实。后续目标方案不得反向改写这些现状。

### 2.1 产品主线：委托、行动权与结果验收已经成立

Peer 当前不是单纯的聊天执行器。现有产品主线已经包含：

- Conversation 保存交流历史、入口工作区和结果回流上下文；
- Agent 按复杂度决定是否物化 GoalPlan，普通问答不必创建正式计划；
- GoalPlan 持久化目标、子任务、依赖、成功标准、Evidence 和 Runner 状态；
- TaskOverview 将 Conversation、GoalPlan、Automation Run 和后台 Shell 聚合为统一工作视图；
- protocol 层投影 `needs_you`、`peer_advancing`、`result_ready`、`paused`、`terminal` 等行动权，renderer 不另造状态机；
- Goal 完成后可进入 `result_ready`，用户确认验收会回写持久化 `resultAcceptance`，不是只播放完成动画。这是当前实现；目标态要求质量评审过线后才能进入该状态。确认验收仍是收口，确认的是意图，不再承担第一轮质检。详见 `design/product/goal-quality-review-repair-loop.md`。

这意味着本方案应扩展现有“委托 → 推进 → 验证 → 质量过线 → 确认验收 / 交付”主线，而不是另建一套 Task 产品和状态中心。

代码证据：

- `packages/protocol/src/goal.ts`
- `packages/runtime-node/src/goal-plan-store.mjs`
- `packages/runtime-node/src/goal-runner.mjs`
- `packages/protocol/src/task-overview.ts`
- `apps/desktop/electron/main/task-overview-aggregator.mjs`
- `apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx`
- `apps/desktop/renderer/src/App.tsx`

### 2.2 Goal 级跨工作区执行已经实现

GoalPlan 已持久化并投影：

```text
conversationId
originWorkspacePath
targetWorkspacePath
```

当 Goal 绑定 `targetWorkspacePath` 时：

- 工具 cwd 与项目指令切换到目标仓库；
- 目标仓库成为主要可写根；
- 来源工作区仍作为只读上下文；
- 工作区运行状态优先按 `originWorkspacePath` 归属，切换 UI 工作区不会改变任务来源。

因此“从知识仓发起、到代码仓执行”不是纯愿景，当前已经有 Goal 级跨工作区链路。它的限制是绑定单位只有一个 GoalPlan 和一个目标路径，不包含仓库分支、上下文 commit 快照或父 Goal 内多条交付路由。

代码证据：

- `apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs`
- `apps/desktop/electron/main/chat-runtime/projected-tool-executor.mjs`
- `apps/desktop/electron/main/llm-chat-service.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-goal-provider.mjs`

### 2.3 当前 GoalTask 不是独立执行容器

当前 GoalPlan 中的叶子 `GoalTask` 主要承载：

- 标题、状态和依赖；
- Evidence 与结果摘要；
- 阻塞、失败与等待用户原因；
- delegated 子 Goal 引用。

它没有以下执行绑定：

```text
repoId
targetBranch
baseCommit
taskBranch
worktreePath
mergePolicy
```

整个 Goal 共享一个 Runner 会话和一个执行工作区。派生子 Goal 可以拥有自己的 plan 级 `targetWorkspacePath`，但这不等于父 Goal 中每个叶子 Task 自动拥有独立 Worktree。因此，本文不能把“每个现有 GoalTask 已是单仓执行容器”写成现状。

代码证据：

- `packages/protocol/src/goal.ts`
- `packages/runtime-node/src/goal-plan-store.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-goal-provider.mjs`

### 2.4 Automation Worktree 已实现隔离执行的半条链

Automation 的写模式已经为每个 Run 创建：

```text
PeerAgent/automation-<automationId>/run-<runId> 分支
独立 Worktree
触发时 workspace 当前 HEAD commit 基线
```

Run 完成后会：

- 收集 changed files、numstat 与 binary patch artifact；
- 有改动时保留任务分支和 Worktree 供审查；
- 无改动时自动删除 Worktree 与分支；
- 在 Automation 结果视图展示基线分支、commit、任务分支、Worktree、文件变化和留存状态；
- `observe` 模式不创建 Worktree。

这套实现是后续通用 Task Worktree Provider 的直接复用基础，不应另写一套 Git 生命周期管理器。

当前限制：Automation 从触发时工作区当前 `HEAD` 创建隔离分支，尚未拥有独立 `targetBranch` 交付契约，也没有同步最新目标分支、合并前复验、合并队列和“交付到开发分支”动作。

代码证据：

- `apps/desktop/electron/main/automation-worktree-adapter.mjs`
- `apps/desktop/electron/main/automation-runner.mjs`
- `apps/desktop/electron/main/automation-worktree-adapter.test.mjs`
- `apps/desktop/electron/main/automation-result-e2e.test.mjs`

### 2.5 TaskOverview 与结果验收已实现，但结果包仍较薄

TaskOverview 已是统一工作事实投影，而不是第二套任务数据库。Goal 的 completed 状态在未验收时可投影为 `result_ready`，用户一键验收后写入 `resultAcceptance`。

目前 Result Review 仍主要复用：

- Conversation 执行详情；
- Goal 进度与成功标准；
- Evidence 引用；
- 由 plan progress 推导的“标准通过 / 无已知风险”等摘要。

全仓尚无结构化 `ResultPackage` 对象。结果视图也没有稳定表达目标仓库、目标分支、任务分支、Worktree、最终 commit、未交付 Diff 和合并状态。Automation 成功结果目前直接按终态展示，不复用 Goal 的 `result_ready` 验收语义。

代码证据：

- `packages/protocol/src/task-overview.ts`
- `apps/desktop/electron/main/task-overview-aggregator.mjs`
- `apps/desktop/renderer/src/app/components/ConversationResultView.tsx`
- `apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx`

### 2.6 尚未实现的交付契约

当前全仓没有形成以下产品与运行时能力：

- Goal / Task 的 `targetBranch`；
- 通用代码任务的 `baseCommit`、`taskBranch` 和 `worktreePath`；
- 交互式 Agent / Goal 自动使用 Worktree；
- `(repoId, targetBranch)` 维度的合并队列；
- 同步最新目标分支、冲突处理、合并后重新验证；
- “等待合并 / 合并中 / 已交付”的统一状态；
- 多仓独立交付记录与“部分交付”聚合状态；
- 目标仓库和目标分支在 TaskOverview / Result Review 中的持续可见性。

当前交互式 Goal 对 `targetWorkspacePath` 的写入直接发生在该目录；如果它是用户正在使用的代码工作区，就仍可能混入或影响用户现场。Automation 虽然隔离写入，但结果停在“保留供审查”，没有交付闭环。

### 2.7 当前能力地图

| 能力 | 当前程度 | 结论 |
|---|---|---|
| Conversation 交流与回流 | 已实现 | 保留，不升级为 Git 边界 |
| Agent 自适应物化 GoalPlan | 已实现 | 继续作为创建判断入口 |
| GoalPlan / Runner / Evidence / DoD | 已实现 | 直接复用，不另建任务引擎 |
| Goal 级 `originWorkspacePath / targetWorkspacePath` | 已实现 | 扩展为明确仓库路由，而非推倒重来 |
| GoalTask 独立执行容器 | 未实现 | 当前叶子任务只是计划与证据节点 |
| Automation Worktree | 已实现 | 提炼为通用 Worktree Provider |
| 交互式 Agent / Goal Worktree | 未实现 | 应接入通用 Provider |
| TaskOverview 行动权投影 | 已实现 | 增加交付事实，不另建状态中心 |
| Goal 结果验收 | 已实现 | 扩展为结构化 Result Package |
| Automation 结果变更留存 | 部分实现 | 有 Diff / Worktree，无交付动作 |
| 目标仓库可见性 | 部分实现 | 运行时有 target path，主要 UI 未持续展示 |
| 目标分支与任务分支契约 | 未实现 | 需新增 Delivery Binding |
| 合并队列与同步复验 | 未实现 | 需新增 Delivery Coordinator |
| 多仓独立交付 / 部分交付 | 未实现 | 需基于派生子 Goal 与交付记录建设 |

审计时运行了 Goal binding、Automation Worktree/Runner、TaskOverview 和结果验收相关测试，共 152 项通过；这证明上述现有链路稳定，但不证明目标交付能力已经实现。

---

## 3. 背景、问题与产品机会

### 3.1 当前隔离缺口

当前交互式 Goal 直接在 `targetWorkspacePath` 执行。如果多个代码目标共享该目录，仍可能出现：

- 并行目标同时写同一文件；
- Agent 的修改混入用户未提交变更；
- 一个运行的依赖、构建产物和临时文件影响另一个运行；
- 取消或重试时无法按代码任务恢复完整现场。

Automation 已证明 Worktree 可以解决执行现场隔离，但仅引入 Worktree 仍不完整。若 A、B 都从开发分支的同一个旧提交启动，A 先合入后，B 必须基于更新后的目标分支重新同步并验证，否则“各自测试通过”不等于“依次合并后仍正确”。

### 3.2 `main` 不是通用开发基线

真实开发通常是：

```text
main（稳定 / 发布）
  └─ develop 或 feature-x（本次开发集成分支）
      ├─ task-a（独立分支 + Worktree）
      └─ task-b（独立分支 + Worktree）
```

因此目标系统不能静默从 `main` 创建 Task。Task 的基线与交付位置必须来自该仓库明确的目标分支，例如 `develop`、`release/2.x` 或 `feature/task-runtime`。

### 3.3 入口仓库不等于交付仓库

典型场景：用户从 `peer-knowledge` 的设计文档发起目标，但要求修改关联代码仓 `peer_agent`。此时：

- `peer-knowledge @ branch/commit` 是上下文来源；
- `peer_agent → targetBranch` 是交付目标；
- 两个仓库的分支名、提交历史和生命周期彼此独立；
- 知识仓分支不能用来推断代码仓目标分支。

当前 `originWorkspacePath / targetWorkspacePath` 已经验证了来源与执行目标可以分离；下一步是补齐仓库身份、上下文版本与目标分支，而不是重新发明跨仓执行。

### 3.4 产品层根因

当前实现分别拥有“目标治理”和“隔离执行”，但尚未由统一交付契约连接：

```text
GoalPlan / Runner / Evidence / Result Acceptance
                         ×
Automation Branch / Worktree / Diff Retention
```

缺失的中间层是：

```text
Delivery Binding（交付意图）
+ Worktree Provider（隔离执行）
+ Delivery Coordinator（同步、复验、合并）
+ Result Package（结果验收）
```

本方案的产品机会不是新建一个任务系统，而是把现有两条成熟链路接成可信的委托交付闭环。

---

### 3.5 产品目标与非目标

#### 产品目标

1. **执行隔离**：每个代码 Task 在独立 Worktree 中读写、运行命令和测试。
2. **路由明确**：用户在执行前和执行中都能看到“仓库 + 目标分支”。
3. **不扰用户现场**：不切换、不 stash、不清理用户原工作目录。
4. **并发安全**：允许 Task 并行开发，对相同交付目的地串行合并和重新验证。
5. **跨仓清晰**：区分上下文来源和改动交付，支持一个 Goal 编排多个仓库级交付。
6. **状态可信**：完成、自检通过、等待合并、已合并和已清理是不同事实。
7. **可恢复审计**：应用重启或任务中断后可恢复 Task、Worktree、分支和合并状态。

#### 非目标

P0 不做：

- 自建 Git 托管平台或替代远端 MR / PR；
- 跨仓原子提交或自动回滚已经合入的另一个仓库；
- 无条件自动解决业务语义冲突；
- 把普通问答、分析步骤、Explorer 或每个工具调用都变成 Worktree Task；
- 强制所有仓库采用相同分支命名；
- 静默推送远端、创建 MR、删除远端分支；这些仍需独立策略或权限；
- 用 Worktree 替代 Goal 边界、权限审批和高风险动作确认。

---

## 4. 核心对象与术语

### 4.1 Conversation（对话）

Conversation 仍然存在，负责：

- 保存用户与 Peer 的交流历史；
- 记录入口工作区和后续语义上下文；
- 承载普通问答及一个或多个 Goal；
- 提供状态卡、结果和待处理事项的回流位置。

Conversation **不是** Git 分支、Worktree 或交付边界，也不拥有唯一开发分支。切换工作区或关闭对话，不应改变已启动 Task 的仓库与分支绑定。

### 4.2 Goal（目标）

Goal 是一次可验证目标的编排边界。当前已经拥有目标、成功标准、GoalTask 依赖、Evidence、Runner、`originWorkspacePath / targetWorkspacePath` 和结果验收；目标态在此基础上增加仓库路由与交付聚合，不替换 GoalPlan。

一个 Goal 可以引用多个上下文仓库。涉及多个可写仓库时，优先把每个仓库级交付派生为已有 delegated 子 Goal，使每个运行实例继续维持单一目标工作区；父 Goal 只编排依赖并聚合多仓结果。待运行时具备稳定的多路由能力后，再评估是否需要让单一 GoalPlan 直接持有多个可写路由。

### 4.3 Task（任务）

当前 `GoalTask` 是计划、依赖和 Evidence 节点，并不天然对应独立执行环境。目标态引入一种**代码交付执行单元**，但不要求所有 GoalTask 都物化：

| GoalTask 性质 | 示例 | 是否物化代码交付执行单元 | 是否绑定 Worktree |
|---|---|---|---|
| 认知型 | 调研、分析、只读审查 | 否 | 否 |
| 编排型 | 等待依赖、汇总验收、人工确认 | 否 | 否 |
| 同一交付内的实现步骤 | 分析模型、修改文件、补测试 | 默认否，继续由一个 Runner 顺序推进 | 共享所属交付单元 |
| 可独立并行或独立验收的代码交付 | 修改一个仓库并形成独立结果 | 是 | 是 |
| 跨仓交付 | 代码仓实现、知识仓更新 | 派生为仓库级 delegated 子 Goal | 每个子 Goal 一个 |

本文后续“代码 Task”是产品层简称，准确含义是已物化的代码交付执行单元，而不是当前协议中的每一个叶子 `GoalTask`。P0 最小路径可以先做到“一个有代码副作用的 Goal / delegated 子 Goal 一个 Worktree”，再在确有并行价值时下沉到叶子级，避免为每个小步骤反复创建环境。

### 4.4 Repository Route（仓库路由）

目标态的仓库路由是“从哪里读、向哪里交付”的统一事实源。P0 不必先引入复杂的多路由表：可兼容扩展当前 `originWorkspacePath / targetWorkspacePath`，为单一交付增加 repo identity、context revision 和 target branch；多仓由父 Goal + delegated 子 Goal 聚合。成熟后再规范化为路由集合：

```text
上下文来源
peer-knowledge @ docs-branch @ contextCommit（只读快照）

改动交付到
peer_agent → feature/task-runtime（可写目标）
```

每条路由至少说明：仓库身份、角色、版本 / 分支、权限和对应 Task。

### 4.5 Target Branch（目标分支）

Task 创建时明确绑定、完成后交付回去的仓库内分支。UI 对外称“目标分支”或“交付到”，不称“主开发分支”，避免与 `main` 混淆。

### 4.6 Task Branch（任务分支）

Peer 为一个 Task 创建的独立分支，例如：

```text
peer/task-284-worktree-runtime
```

分支名应稳定、可审计，并包含 Task 短 ID；标题仅作可读后缀，不能作为唯一标识。

### 4.7 Worktree（执行环境）

任务分支对应的独立 Git Worktree。该 Task 的文件修改、命令、测试和提交都在这里发生。Worktree 路径是系统细节，默认折叠展示。

### 4.8 Merge Queue（合并队列）

以 `(repoId, targetBranch)` 为队列键的串行交付器。它负责同步目标分支、冲突检查、重新验证、原子更新目标分支和记录结果。

---

## 5. 核心关系与不可变规则

```text
Conversation（现有）
└─ Parent GoalPlan（现有治理与聚合）
   ├─ GoalTask（现有计划 / 证据节点）
   └─ delegated Delivery Goal 0..N（复用现有派生能力）
      ├─ origin / context（扩展现有绑定）
      ├─ one writable repo + frozen targetBranch（新增 Delivery Binding）
      ├─ one taskBranch + Worktree（复用 Automation Worktree）
      └─ Delivery Record + Result Package（新增交付与验收事实）
```

不可变规则：

1. Conversation 可包含多个 Goal，不保存唯一目标分支。
2. 普通 GoalTask 不因存在于计划树中就自动创建 Worktree。
3. 一个已物化的代码交付执行单元只写一个仓库，并拥有一个目标分支和一个 Worktree。
4. 同一 Git 分支不得被多个 Worktree 共同 checkout。
5. 目标分支在执行开始后不得被 Conversation、当前 workspace 或 UI 分支切换静默改写。
6. 多仓交付优先使用父 Goal 编排多个 delegated 子 Goal，每个子 Goal 保持单一可写仓库。
7. Worktree 隔离执行，Delivery Coordinator 治理同步、复验和交付；两者缺一不可。
8. “代码已生成”不等于“验证通过”，“验证通过”不等于“已交付”，“用户已验收”是另一独立事实。
9. 上下文仓库与交付仓库可以相同，也可以完全不同。
10. 跨仓交付没有全局原子性，必须暴露每个仓库的独立结果。

---

## 6. 何时创建 Task 与 Worktree

### 6.1 普通咨询

用户问“这种方案合理吗”时，Peer 直接回答：

- 不创建 Goal；
- 不创建执行型 Task；
- 不创建分支和 Worktree；
- 可以提供“按此方案实施”的后续操作。

### 6.2 单一明确改动

用户说“按这个方案改 Task 执行逻辑”，Agent 仍按现有复杂度规则决定是否物化 GoalPlan。只要目标会在 Git 仓库产生副作用，执行开始前为本次代码交付建立 Delivery Binding 和 Worktree；Goal 内的分析、实现、测试步骤共享该环境，不为每个步骤重复创建 Worktree。

### 6.3 多步骤或跨仓目标

同一仓库、同一交付结果下的多步骤继续放在一个 Goal / Runner 中。只有能够独立并行、独立验收或写入不同仓库的交付才拆分：

```text
Parent Goal：实现 Task 隔离并更新设计
├─ delegated Code Goal：peer_agent → feature/task-runtime
└─ delegated Docs Goal：peer-knowledge → design/task-runtime
```

只读调研、验证汇总和等待依赖保留为普通 GoalTask，不创建 Worktree。这个规则直接复用当前 delegated 子 Goal 能力，也避免引入与现有 GoalTask 平行的新任务树。

### 6.4 非 Git 工作区

若写入位置不属于 Git 仓库，P0 不伪造 Worktree：

- 明确显示“直接写入目录，不支持分支隔离”；
- 按权限与 Goal 边界执行；
- 自动合并能力不可用；
- 高风险或多任务并发时要求用户确认，或阻止并行写入。

---

## 7. 目标分支发现与确认

### 7.1 发现优先级

对于每个可写仓库，按以下顺序提出目标分支候选：

1. 当前 Goal 已确认的该仓库路由；
2. 用户本轮明确指定的仓库与分支；
3. 延续同一 Goal 的既有未完成 Task 目标分支；
4. 该仓库当前工作区所在分支；
5. 仓库配置的默认开发分支；
6. 无法可靠判断时，让用户选择。

`main`、`master` 或远端默认分支只能作为候选，不能作为静默兜底。

### 7.2 首次写入前确认

以下情况必须在首次副作用前确认路由：

- 从入口仓库跨到另一个仓库写入；
- 候选分支有多个且无可靠优先级；
- 当前分支是 detached HEAD；
- 目标分支不存在或仅远端存在且拉取策略不明确；
- 用户意图与 Goal 已绑定路由冲突。

确认卡：

```text
Peer 将跨仓库执行此目标

上下文来源
peer-knowledge · docs/worktree@a82c11f · 只读快照

改动交付到
peer_agent · feature/task-runtime              [更改]

将从该分支创建任务分支和独立 Worktree，
完成后通过合并队列交付回该分支。

[确认并开始]
```

同一 Goal 中已确认的路由可被后续 Task 继承，不重复打扰。

### 7.3 启动后冻结

Task 启动时冻结：

```text
repoId
targetBranch
targetRef / remoteTrackingRef
baseCommit
taskBranch
worktreePath
contextSnapshotIds
mergePolicy
```

用户后来切换入口工作区、Conversation 或仓库当前分支，只影响之后创建的 Task，不改变已启动 Task。

---

## 8. 跨仓上下文与交付模型

### 8.1 路由角色

| 角色 | 含义 | 行为 |
|---|---|---|
| `context` | 只读依据 | 记录快照，不创建可写 Worktree |
| `delivery` | 改动交付 | 创建 Task 分支与 Worktree |
| `context+delivery` | 同仓既读又写 | 上下文读取与 Task 写入均固定版本 |

### 8.2 上下文快照

Goal 启动时记录：

```text
repoId
workspacePath
branch
commit
uncommittedPatchSnapshot（如纳入上下文）
capturedAt
```

如果入口工作区有未提交文档并且用户要求以其为设计依据，应明确把该 Diff 纳入快照，而不是假装它属于某个 commit。

运行期间用户继续修改知识仓时，执行中的 Task 不静默刷新。用户可选择“刷新上下文”，系统生成新快照并记录哪些 Task 采用了新版本；必要时重新验证。

### 8.3 一个 Goal 修改多个仓库

拆成多个执行型叶子 Task，并在 Goal 卡显示交付矩阵：

```text
交付进度
✓ peer_agent / feature/task-runtime    已合并 b83d219
● peer-knowledge / docs/task-runtime   等待合并
```

可设置仓库间依赖，例如先合代码再更新文档，或要求全部验证通过后依次进入合并队列。但 UI 必须说明这只是编排顺序，不是跨仓原子事务。

### 8.4 部分交付

若代码已合并而文档失败，Goal 状态为“部分交付 / 需要处理”，不得显示整体成功。用户可重试剩余 Task；已合并仓库不自动回滚，除非另建显式回滚 Task。

---

## 9. 端到端交互

### 9.1 Goal 顶部：显示仓库路由，不显示全局唯一分支

```text
┌ 实现 Task 与 Worktree 隔离
│
│ 上下文来源
│ peer-knowledge · docs/worktree@a82c11f · 只读
│
│ 改动交付到
│ peer_agent · feature/task-runtime             [更改]
│
│ 任务 4 · 运行中 2 · 等待合并 1
└
```

Conversation 顶部只显示入口工作区和活跃 Goal 数，不宣称“本次开发分支”。

### 9.2 Task 创建

```text
┌ 实现 Worktree 生命周期
│ 仓库       peer_agent
│ 交付到     feature/task-runtime               [更改]
│ 执行环境   独立 Worktree
│ 完成后     合并前确认                         [自动交付]
│
│ [开始执行]
└
```

低风险且路由已确认的 Agent 自驱 Task 可自动开始；用户仍能在任务详情看到相同事实。

### 9.3 准备环境

系统依次执行：

1. 校验仓库和 Git 状态；
2. 获取目标分支最新可用引用；
3. 记录 `baseCommit`；
4. 创建唯一任务分支；
5. 创建 Worktree；
6. 初始化依赖或复用安全缓存；
7. 将 Task 状态置为执行中。

不会切换或 stash 用户原工作目录。

### 9.4 执行中

```text
┌ 实现 Worktree 生命周期                  执行中
│ peer_agent → feature/task-runtime
│ 任务分支  peer/task-284-worktree-runtime
│ 环境      独立 Worktree
│
│ ✓ 分析现有模型
│ ● 实现生命周期
│ ○ 添加测试
│
│ [查看改动] [打开 Worktree] [暂停] [取消]
└
```

折叠卡仍保留：

```text
实现 Worktree 生命周期 · 执行中 · peer_agent → feature/task-runtime
```

### 9.5 自检完成

```text
┌ 实现 Worktree 生命周期                  等待合并
│ peer_agent → feature/task-runtime
│ 修改      8 个文件，+426 / -31
│ 检查      24/24 通过
│ 目标变化  较任务基线新增 3 个提交
│
│ [查看 Diff] [合并到 peer_agent / feature/task-runtime]
│ [继续修改] [放弃交付]
└
```

### 9.6 合并完成

```text
┌ 实现 Worktree 生命周期                  已合并
│ 已交付到  peer_agent / feature/task-runtime
│ 结果提交  b83d219
│ 检查      全部通过
│ Worktree  24 小时后清理
│
│ [查看提交] [立即清理] [保留环境]
└
```

---

## 10. Worktree 生命周期

### 10.1 创建

- 默认存放在 Peer 管理目录，不挤占用户仓库目录；
- 路径按 `repoId/taskId` 唯一；
- 创建前检测同名分支、残留 Worktree 和锁；
- 若发现可恢复的同 Task 环境，优先恢复而非再创建一份；
- 分支与 Worktree 创建必须幂等。

### 10.2 使用

- 该 Task 的写文件、shell cwd、测试、格式化和提交均落在 Worktree；
- 读取其他上下文仓库不改变可写根；
- Explorer 默认只读，不继承写能力；
- 依赖缓存可共享，但工作目录、构建输出和锁文件修改仍属于 Task。

### 10.3 暂停与取消

暂停：停止 Runner，保留进程可恢复信息、分支、Worktree 和修改。

取消默认行为：

> 停止执行并保留任务环境，不自动删除未交付代码。

随后提供：继续任务、导出 Diff、删除环境。删除有未提交或未合并修改的环境必须二次确认。

### 10.4 清理

- 合并成功后进入清理宽限期，建议默认 24 小时；
- 清理前确认目标提交可追溯、Worktree 无额外未提交改动；
- 先移除 Worktree，再按策略删除本地任务分支；
- 失败或冲突环境不自动清理；
- 应用启动时扫描孤儿 Worktree，提供恢复或清理，而非直接删除。

---

## 11. 合并队列

### 11.1 队列粒度

队列键为：

```text
(repoId, targetBranch)
```

同一仓库不同目标分支可以并行合并；不同仓库也可以并行。只有指向相同仓库和相同目标分支的交付必须串行。

### 11.2 入队条件

- Task 执行完成；
- Task 分支存在且提交可识别；
- 必需检查在任务基线上通过；
- 交付策略允许自动入队，或用户点击明确的合并按钮；
- 没有未解决的用户确认、冲突或高风险门禁。

### 11.3 出队执行

轮到 Task 时：

1. 获取并锁定当前目标分支头；
2. 将任务变更同步到最新目标分支（具体采用 rebase、merge 或临时集成分支由仓库策略决定）；
3. 检测文本冲突和策略冲突；
4. 在同步后的结果上重新运行必需检查；
5. 确认目标分支头在最终写入前没有再次变化；
6. 以仓库允许的方式更新目标分支；
7. 记录结果 commit、检查证据和合并方式；
8. 释放锁并处理下一个 Task。

若第 5 步发现目标分支再次更新，当前项重新同步和验证，不能覆盖他人提交。

### 11.4 自动交付

两种策略：

- **合并前确认（默认）**：自检后停在等待合并；
- **自动交付**：满足全部门禁后自动进入队列。

自动交付不包含：强推、跳过测试、自动接受语义冲突、静默推送远端。任何门禁失败都转为“需要处理”。

### 11.5 合并方式

产品层支持仓库策略选择：

- merge commit；
- squash；
- fast-forward；
- 通过远端 MR / PR 交付。

P0 必须在入队前确定方式，并在完成卡显示真实结果。若目标分支受保护，系统不得假装本地合并即完成，应转为“MR 已创建 / 等待远端合并”。

---

## 12. 冲突、失败与恢复

### 12.1 文本冲突

```text
┌ Task B                                  需要处理
│ peer_agent / feature/task-runtime 已更新
│ 发现 2 个冲突文件
│ src/task/runtime.ts
│ src/task/task-store.ts
│
│ [让 Peer 尝试解决] [打开 Worktree] [取消合并]
└
```

Peer 可以处理机械冲突；若两侧改动表达不同业务规则，必须请求用户决策。解决后重新运行全部受影响检查。

### 12.2 验证失败

合并前检查失败时：

- Task 回到“修复中”或“验证失败”；
- 保留同步后的环境和日志；
- 修复后重新入队；
- 不阻塞队列中与其无依赖的后续项，可按策略暂时让行。

### 12.3 目标分支被删除或重写

停止交付并显示事实。用户可以选择新目标分支，但这不是修改原 Task 绑定：系统应创建“重新定向交付”记录，重新计算基线并完整验证。

### 12.4 Worktree 丢失

若任务分支和提交仍存在，可重建 Worktree；若只有未提交文件且目录丢失，则标记不可自动恢复，并展示最后备份 / patch 证据。状态不能继续显示“执行中”。

### 12.5 应用崩溃或重启

启动时对账：

- Task 持久化状态；
- Git 分支与 Worktree 注册信息；
- Worktree 文件状态；
- 合并队列锁和目标分支头；
- 实际运行进程。

旧 `running` 不能直接复活为旋转状态。根据事实恢复为可继续、等待处理、已合并待清理或环境丢失。

### 12.6 用户原工作区有未提交修改

Task 创建与执行不触碰原工作区。合并队列也不应通过用户当前 checkout 执行，应使用 Peer 管理的集成环境。只有用户明确要求把结果应用到其未提交工作区时，才进入独立高风险流程。

---

## 13. 状态机

### 13.1 Task 交付状态

```text
draft
  → preparing
  → running
  → verifying
  → ready_to_merge
  → queued
  → syncing
  → merge_verifying
  → merged
  → cleanup_pending
  → cleaned
```

分支状态：

```text
preparing → environment_failed
running / verifying → paused | cancelled | failed
queued / syncing → conflict | target_changed | merge_check_failed
merged → cleanup_failed
any recoverable state → recovering
```

### 13.2 用户文案映射

| 内部状态 | 用户文案 |
|---|---|
| `preparing` | 准备独立环境 |
| `running` | 执行中 |
| `verifying` | 自检中 |
| `ready_to_merge` | 等待合并 |
| `queued` | 合并排队中 |
| `syncing` | 正在同步目标分支 |
| `merge_verifying` | 合并前复验 |
| `conflict` | 存在冲突，需要处理 |
| `merged` | 已交付 |
| `cleanup_pending` | 已交付，等待清理 |
| `cleaned` | 环境已清理 |

### 13.3 Goal 聚合状态

- 所有交付 Task 已合并或按目标完成：Goal 可进入验证完成；
- 任一仓库已合并、任一仓库失败：部分交付；
- 有冲突、权限或用户决策：等待用户；
- 只有代码生成但未交付：Goal 不得显示“已完成”。

Task Center 和状态栏只投影这些统一事实，不自行推断另一套生命周期。

---

## 14. 数据模型建议

### 14.1 Goal 仓库路由

```ts
type RepositoryRoute = {
  routeId: string
  repoId: string
  repoPath: string
  role: 'context' | 'delivery' | 'context_delivery'
  contextSnapshot?: {
    branch?: string
    commit?: string
    patchArtifactRef?: string
    capturedAt: string
  }
  targetBranch?: string
  remoteTrackingRef?: string
  writePolicy: 'read_only' | 'task_worktree'
  confirmedAt?: string
  confirmedBy?: 'user' | 'explicit_user_message' | 'inherited_goal_route'
}
```

### 14.2 Task 执行绑定

```ts
type TaskExecutionBinding = {
  taskId: string
  repoId: string
  repoPath: string
  targetBranch: string
  targetRef?: string
  baseCommit: string
  taskBranch: string
  worktreePath: string
  contextSnapshotIds: string[]
  mergePolicy: 'confirm' | 'auto'
  mergeMethod: 'merge' | 'squash' | 'ff' | 'pull_request'
  createdAt: string
}
```

### 14.3 合并记录

```ts
type DeliveryRecord = {
  taskId: string
  repoId: string
  targetBranch: string
  queueKey: string
  queuedAt?: string
  syncedTargetCommit?: string
  verificationEvidenceRefs: string[]
  resultCommit?: string
  pullRequestUrl?: string
  mergedAt?: string
  status: 'ready' | 'queued' | 'conflict' | 'failed' | 'merged'
}
```

关键约束：Goal 路由用于继承，Task binding 是启动后不可静默修改的执行事实，DeliveryRecord 是交付结果；三者不可只存在于消息文本。

---

## 15. 权限、安全与边界

1. Worktree 是隔离机制，不是权限机制；所有写入仍走权限与 Goal boundary。
2. 跨仓绝对路径可被运行时访问，不代表自动获得该仓库写权限。
3. Goal 路由明确标记可读与可写角色；执行型 Task 的写能力仅投影到绑定 Worktree。
4. `git push`、强推、删除分支、覆盖文件、清理未合并环境等继续按高风险动作治理。
5. 用户确认的是可理解的“仓库 + 目标分支 + 交付策略”，不是一串内部路径。
6. 所有创建、同步、验证、合并和清理动作保留 Evidence，支持问题追溯。
7. 凭证、仓库路径和任务正文不进入不必要的遥测。

---

## 16. Automation 与后台任务

Automation 触发的代码目标复用同一模型，不另造执行系统：

- Run 创建 Goal / Task 后，照常解析仓库路由；
- 已预配置且仍有效的目标分支可自动确认；
- 分支不存在、目标漂移、权限变化或跨仓路由不明确时，Run 进入等待用户，不猜测；
- 每次 Run 使用新的 Task 分支和 Worktree，不能复用上次 Run 的脏环境；
- 同一 Automation 的多个 Run 若交付到同一分支，进入同一合并队列；
- Run 结果页展示仓库、目标分支、交付状态和 commit / MR，不只显示会话摘要。

---

## 17. 复用路径与分期

建设原则是连接现有两条链，而不是一次性重写 Goal、Automation 和 TaskOverview：

```text
GoalPlan / Runner / Evidence / Result Acceptance（现有）
                              +
Automation Worktree / Branch / Diff Retention（现有）
                              ↓
Delivery Binding → 通用 Worktree Provider → Delivery Coordinator → Result Package
```

### 17.1 P0-A：先补交付意图与可见性

目标：让系统和用户先明确“向哪里交付”，即使执行暂时仍沿用现有 target workspace。

1. 兼容扩展 GoalPlan 的 `originWorkspacePath / targetWorkspacePath`，新增单一交付的 `repoId`、`targetBranch`、`baseCommit` 与确认来源；
2. 目标分支按第 7 章发现并冻结，不静默使用 `main`；
3. Goal / TaskOverview / Result Review 展示来源工作区、目标仓库与目标分支；
4. 普通 GoalTask 不物化执行环境；有代码副作用的 Goal / delegated 子 Goal 才创建 Delivery Binding；
5. 多仓目标复用 delegated 子 Goal，一仓一个交付绑定；
6. 当前直接写 target workspace 的运行明确标注“未隔离执行”，不伪装为 Worktree。

本阶段不宣称解决并发写入或自动合并，但先消除最危险的隐式路由。

### 17.2 P0-B：通用化 Automation Worktree

目标：把已经验证的 Automation 隔离链下沉为共享 Provider，并接入交互式 Agent / Goal。

1. 从 `automation-worktree-adapter.mjs` 提炼通用 Git Worktree Provider，保留 Automation 兼容适配层；
2. 分支创建从“workspace 当前 HEAD”升级为 Delivery Binding 冻结的 `targetBranch@baseCommit`；
3. 一个有代码副作用的 Goal / delegated 子 Goal 默认共享一个任务分支与 Worktree；
4. 工具 cwd、唯一可写根、项目指令与 Runner 恢复统一绑定 Worktree；
5. 复用现有 changed files、numstat、binary patch、保留 / 清理能力；
6. 补齐取消、重启恢复、孤儿环境对账与延迟清理；
7. Automation Run 与交互式 Goal 共享执行环境事实，但继续保留各自产品入口。

本阶段完成后，Peer 具备一致的隔离执行，但结果仍可停在“等待交付”。

### 17.3 P0-C：Delivery Coordinator 与结果验收闭环

目标：解决并行任务基线陈旧和用户无法确认最终交付结果的问题。

1. 建立 `(repoId, targetBranch)` 维度的串行 Delivery Coordinator；
2. 入队前必须先通过质量评审；未过线不得进入合并队列。详见 `design/product/goal-quality-review-repair-loop.md`；
3. 入队后同步最新目标分支、处理冲突并重新运行受影响检查；
4. 区分质量过线后的 `result_ready`、`ready_to_deliver`、`delivering`、`delivered` 和用户 `accepted`；
5. 将 DeliveryRecord、最终 commit / MR、验证 Evidence、质量评审结论、风险和恢复动作纳入结构化 Result Package；
6. Goal 继续使用现有 `resultAcceptance`，语义是确认验收仍是收口，确认的是意图，不再承担第一轮质检；
7. Automation 成功结果也进入一致的“质量过线 / 结果就绪 / 交付状态”语义，而非直接被视为用户已接受；
8. 多仓父 Goal 聚合 delegated 子 Goal 的独立交付，支持部分交付。

### 17.4 P1

- 受保护分支的 MR / PR 交付；
- 叶子 GoalTask 在确有并行价值时独立物化 Worktree；
- 堆叠交付（B 显式依赖尚未合并的 A）；
- 仓库级 merge / squash / ff 策略；
- 完整上下文 patch 快照和刷新比较；
- 队列优先级、批量暂停与夜间自动交付。

### 17.5 P2

- 多机器 / 远端执行环境；
- 远端合并队列与 CI 状态统一；
- 跨仓发布编排和补偿式回滚建议。

---

## 18. 验收标准

### 18.1 现状守护与创建判断

1. 普通咨询继续不强制创建 GoalPlan、任务分支或 Worktree。
2. 现有 GoalPlan / Runner / Evidence / DoD 与 `resultAcceptance` 语义保持兼容。
3. TaskOverview 继续只消费 protocol 行动权投影，不在 renderer 新建一套交付状态机。
4. Automation 现有 observe 模式、每 Run 隔离、Diff artifact 与有改动保留行为不得回退。
5. 只读调研和普通 GoalTask 不创建 Worktree。
6. 同一交付内的分析、实现和测试步骤默认共享一个 Goal 级 Worktree，不机械地一叶子一步一环境。
7. 一个已物化代码交付执行单元只能绑定一个可写仓库、一个任务分支和一个 Worktree。
8. 一个跨两仓写入的父 Goal 至少派生两个仓库级 delegated 子 Goal，并分别验收交付。

### 18.2 分支路由

5. 系统不会无提示地把 `main` 作为所有 Task 的基线。
6. 首次跨仓写入前，用户能看到上下文来源及“仓库 + 目标分支”。
7. Conversation 或入口工作区切换后，已启动 Task 的目标分支不变。
8. Goal 和 Task 卡均能持续看到交付仓库与目标分支。
9. 合并按钮明确写出交付目的地。

### 18.3 Worktree 隔离

10. 两个并行 Task 不共享工作目录和任务分支。
11. Task 执行不会切换、stash 或混入用户原工作区修改。
12. Task 取消默认保留有修改的 Worktree，并提供显式清理。
13. 应用重启后能从 Git 与持久化记录恢复环境状态。

### 18.4 合并队列

14. 指向同一仓库同一目标分支的两个 Task 串行合并。
15. A 合入后，B 必须同步包含 A 的最新目标分支并重新验证。
16. 目标分支在最终写入前再次变化时，不覆盖新提交，而是重试同步。
17. 冲突或检查失败时不会强推或伪报已合并。
18. 不同仓库或同仓不同目标分支可独立进入各自队列。

### 18.5 跨仓与状态

19. 从知识仓发起并修改代码仓时，知识仓分支不会被当成代码仓目标分支。
20. 上下文快照变化不会静默改变正在执行 Task 的依据。
21. 多仓 Goal 能分别显示每个仓库的验证与交付结果。
22. 一个仓库已合并、另一个失败时显示部分交付，而非整体完成。
23. “执行完成、自检通过、等待合并、已合并、已清理”在 UI 和持久化状态中可区分。
24. Task Center 展示的是统一状态投影，不把 Goal 子步骤、工具调用重复计为独立后台任务。

### 18.6 安全与可恢复性

25. 删除含未交付修改的 Worktree 必须明确确认。
26. 受保护目标分支无法本地写入时，不显示已交付；应转为 MR / PR 或等待处理。
27. 合并、验证和清理均有可追溯 Evidence。
28. 崩溃重启后不存在实际运行实例的旧 Task 不继续显示执行中。

---

## 19. 产品文案基线

推荐：

- “目标分支” / “交付到”，不使用“主开发分支”；
- “独立 Worktree”可在高级详情出现，主界面优先说“独立执行环境”；
- “合并到 `repo / branch`”，不只写“合并”；
- “已生成改动”“检查通过”“已交付”分别表达，不混为“完成”；
- “上下文来源”与“改动交付到”成对出现；
- “自动交付”附带说明：“无冲突且检查通过时自动进入合并队列”。

错误文案必须说明对象和恢复动作，例如：

```text
peer_agent / feature/task-runtime 已更新，当前任务需要重新同步。
发现 2 个冲突文件。你可以让 Peer 尝试解决，或打开独立执行环境手动处理。
```

---

## 20. 实施原则与最终决策

### 20.1 单一事实源

- GoalPlan：继续作为目标、计划、依赖、Evidence、Runner 的事实源；质量过线另见 Quality Review；
- Quality Review：结果是否够好的事实源，过线后才允许进入交付或 `result_ready`；
- Delivery Binding：作为执行仓库、目标分支、基线、任务分支和 Worktree 的新增事实源，P0 兼容挂接在 Goal / delegated 子 Goal；
- Delivery Coordinator / DeliveryRecord：作为同步、复验与交付结果的新增事实源；
- Result Package：汇总目标结果、变更、验证、风险和交付记录，并由现有 `resultAcceptance` 记录用户验收；
- TaskOverview / Task Center：继续只做协议投影与回流，不自行拼接或持久化另一套事实。

### 20.2 最小正确链路

```text
用户目标
→ 判断是否需要执行型 Task
→ 冻结 Goal 仓库路由
→ 冻结 Task 交付绑定
→ 创建任务分支与 Worktree
→ 在隔离环境执行和自检
→ 质量评审过线（不够好就自我修复）
→ 进入 repo + targetBranch 合并队列
→ 同步最新目标分支并复验
→ 交付并记录 Evidence
→ 延迟清理
```

### 20.3 目标方案决策

以下是目标方向，不是当前完成度声明：

1. **Conversation 保持交流、上下文连续性和回流职责，不拥有唯一分支。**
2. **GoalPlan / Runner / Evidence / TaskOverview / resultAcceptance 继续作为产品主干，不另建平行 Task 系统。**
3. **普通 GoalTask 不自动创建 Worktree；一个有独立代码交付价值的 Goal / delegated 子 Goal 才物化 Delivery Binding 与 Worktree。**
4. **代码交付从明确目标分支创建并交付回该分支，绝不固定为 `main`。**
5. **从知识仓发起不等于向知识仓交付；P0 从扩展现有 origin/target workspace 开始表达两者。**
6. **跨仓优先复用 delegated 子 Goal，一仓一个执行环境与交付记录，由父 Goal 聚合。**
7. **Automation Worktree 是通用隔离能力的实现基础，不重新实现一套 Git Worktree 链。**
8. **Worktree 解决执行隔离，Delivery Coordinator 解决交付串行化与最新基线复验。**
9. **自动交付是受门禁保护的自动尝试，不是无条件自动合并。**
10. **结果验收复用现有 resultAcceptance；确认验收仍是收口，确认的是意图。质量过线由 Quality Review 决定，用户不再做第一轮质检。**
11. **跨仓没有原子提交，必须诚实展示部分交付并支持剩余任务恢复。**
12. **建设顺序是先路由可见，再统一隔离，最后完成合并与验收闭环。**
