# 任务形态收口：流转是任务，承载仍是会话

创建时间：2026-08-15
最后更新：2026-08-15
状态：设计草案（可评审；本仓库只落知识，代码改动在 `peer_agent`）
关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）
关联实现：
- `packages/protocol/src/task-overview.ts`
- `apps/desktop/electron/main/task-overview-aggregator.mjs`
- `apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx`
- `apps/desktop/renderer/src/chat/state/conversationStore.ts`
- `packages/runtime-node/src/goal-intake-convergence.mjs`
关联文档：
- `design/product/peer-2-0-product-system.md`（对象模型：Task 是心智，Conversation 是载体）
- `design/product/peer-task-flow-action-right-correction.md`（首页主轴是行动权，不是讨论容器）
- `design/product/peer-2-0-workbench-flow.md`（工作台 / 抽屉 / 会话现场）
- `knowledge/architecture/task-lifecycle-and-acceptance-flow.md`（副作用必须先有 GoalPlan）
- `knowledge/architecture/intake-convergence.md`（intake 契约：未成立的委托不能当任务）
- `design/product/goal-plan-run-execution-graph-technical-design.md`（Goal Thread）
- `design/product/composer-at-context-picker.md`（`@` 仍停在会话层）
- `design/product/followed-discussions.md`（讨论区与任务桶互斥）

---

## 0. 一句话

**用户看见并流转的是任务；系统存消息、挂附件、做深链的仍是会话。不要再造一张 Task 表。**

Peer 2.0 总纲已经定过：不虚构 `Project → Task → Conversation` 三级结构。一个 Conversation 就是一项 Task 的持续沟通与执行载体。昨天问「我们是不是已经以任务形态流转了」，答案是半句对：

- **对的半句**：首页、行动权、验收、Goal Thread 追问派生，已经按任务在转。
- **没换掉的半句**：消息、附件、`@`、不少 IPC、卡片深链，仍以 `conversationId` 为第一身份。

这份文档把这两层收成同一套合同：什么已经成立、什么只是投影、还剩哪些会话身份泄漏、按什么顺序补。它不重写行动权，不重写验收准入，不重写 Goal Thread；它只补**身份层**。

---

## 1. 现在到底是什么形态

```text
用户心智          任务 / 目标线 / 下一步谁该动
                  ▲
                  │ 投影（TaskOverview）
                  │
执行事实          GoalPlan + GoalRunner + Automation
                  ▲
                  │ 绑在
                  │
沟通载体          Conversation（消息、附件、模型上下文）
                  ▲
                  │ 落在
                  │
执行世界          Workspace
```

四套东西不要互相冒充：

| 层 | 对象 | 回答什么 | 现在的真源 |
| --- | --- | --- | --- |
| 心智 | Task / Goal Thread | 用户托付的是哪一件事 | **没有独立表**。由 Conversation + 其上的 GoalPlan 族共同投影 |
| 流转 | 行动权 | 下一步谁该动 | `TaskOverviewItem.actionRight`，main 进程唯一聚合 |
| 执行 | GoalPlan / Runner / Automation | 怎么推进、证没证完 | GoalPlan store、Runner、Automation store |
| 载体 | Conversation | 双方说了什么、附件和上下文在哪 | 会话库；主键仍是 `conversationId` |

所以「已经是任务形态」说的是**流转层和首页心智**，不是「会话已经消失」。

### 1.1 已经按任务在转的

- 首页是 `TaskOverviewPage`，不是会话墙。分桶是需要你处理 / Peer 正在推进 / 正在讨论 / 结果待验收。
- 有副作用的工作，执行前必须有持久化 GoalPlan（Micro Plan 也算）。无 plan 的写文件会被拒。
- 纯问答走 intake 收敛：回合正常结束且未升级为 GoalPlan，契约删除，不进任务桶。
- 验收后追问可挂 `parentPlanId` + `sourceTaskId`，形成 Goal Thread，不再默认平铺成新的顶层目标。
- 侧栏一级入口只剩工作台；任务 / 历史是抽屉，不是第二套会话列表。
- 「继续讨论」的目标态是会话抽屉，不把主区硬切成 Chat。

### 1.2 还停在会话上的

- 「新建任务」底层仍是 `conversationsCreate`。首条消息发出前，常常还没有 GoalPlan。
- 卡片、搜索、通知的深链主键仍是 `conversationId`。
- `@` 只搜其他会话，把 transcript 当附件；不认文件，更不认当前 Goal / Thread。
- 无 GoalPlan 的未读沟通，仍 `projectConversation`，`source: 'conversation'`，进「正在讨论」。
- 同会话通常只有一条活跃计划；Goal Thread 的派生 plan 也共享这条会话。
- 一部分实现仍会「关抽屉 + 切主 Chat」，和抽屉目标态不一致。

一句话对照：

> 流转层已经是任务，承载层还是会话。要补的是泄漏，不是换皮，更不是新建父层。

---

## 2. 红线：不另起 Task 身份层

`peer-2-0-gap-analysis.md` 曾把「已验收加在哪一层」列为待决。后续已经用事实答过，这里写成死规定：

1. **不新建 Task / Project 表。** Task 是用户心智，不是第三份数据库。
2. **已验收加在 GoalPlan 上**（`accepted` / 验收事实），不是加在 Conversation 上，也不是新 Task 实体。`GoalPlanStatus.accepted`（计划被接受去执行）和「用户已验收结果」不是同一个词，文档必须写全称。
3. **首页不去 Conversation 里猜任务状态。** 不解析「已完成」「改好了」这类助手文案。
4. **一 Conversation 对应一条用户能理解的任务线。** 派生工作用 Goal Thread 挂在原线上，不靠再开一个会话假装新任务；明确的新委托才新建 Conversation。
5. **纯问答可以只有 Conversation，没有 Task 心智。** 它们可以进「正在讨论」，不能进需要你处理 / 推进中 / 待验收。

违反任何一条，都会把已经纠偏过的行动权主轴再扭回去。

---

## 3. 委托何时成立

Conversation 随时可以存在。Task 心智不是点「新建任务」就成立。

```text
用户开口
  │
  ├─ 纯问答 / 咨询 / 闲聊
  │     Conversation 留下
  │     intake 回合结束 → 契约删除
  │     首页最多进「正在讨论」（未读时）
  │
  └─ 委托成立
        条件（满足任一）：
        - 用户要改、修、实现、落地
        - 将产生本地或外部副作用
        - 结果需要验证或验收
        - 用户明确要 Peer 持续推进一件事
        │
        ▼
      持久化 GoalPlan（可从 intake 升级，或 Micro Plan）
        │
        ▼
      这条 Conversation 开始作为该 Task 的载体被投影
```

判定口诀：

- **用户原话 ≠ 任务。** 原话是输入；任务在委托成立时才有。
- **有 Conversation ≠ 有任务。** 没 GoalPlan 的会话只是沟通线程。
- **有 GoalPlan ≠ 可以忘掉。** `completed` 且未验收是 `result_ready`，不是历史。
- **有派生 Plan ≠ 新任务。** 同一 Goal Thread 上的下一轮，仍是这件事。

Intake 中断不能当成「原来只是聊天」删掉。中断过的 intake 必须留在任务流（执行中断），否则用户会在「正在讨论」里找一件已经开过工的事。这条已在 `intake-convergence.md` 修过，收口时不得回退。

---

## 4. 一条任务线里有什么

用户以为的「一个任务」，内部其实是一捆对象：

```text
Conversation（载体，稳定 id）
  ├─ 消息 / 附件 / 压缩摘要 / 模型绑定
  ├─ 当前活跃 GoalPlan          ← 同会话单活跃
  ├─ 派生 GoalPlan…             ← Goal Thread（parentPlanId + sourceTaskId）
  ├─ 若干 Run / Checkpoint
  ├─ Evidence / Artifact
  └─ 可选 Automation 关联（定时委托是另一条源，投影进同一工作台）
```

对外只讲三个词：

| 用户看见 | 内部是什么 | 不能说成 |
| --- | --- | --- |
| 任务 | Conversation + 其上 Goal Thread 的投影 | 「又一个 Chat」 |
| 目标线 | `rootPlanId` 下的派生计划族 | 互不相关的多张卡片 |
| 讨论 | 同一载体上的消息流 | 和任务并列的第二套工作 |

Goal Thread 的产品含义：

- 验收后的追问、返工、补洞，默认挂到刚完成的那条线上。
- 只有用户明确另起一件事（或模型判断主题已经跳开），才 `conversationsCreate` + 新的顶层 GoalPlan。
- 首页「结果待验收」按目标线分组，不把同一件事的 3 个 plan 平铺成 3 件无关工作。

同会话单活跃计划仍然成立：**同一时刻只有一条 plan 在 executing**。派生是时间上的下一轮，不是同会话并行开打。

---

## 5. 投影合同：首页只认行动权

工作台不是任务仓库，也不是会话管理器。它只投影「下一步谁该动」。

| 阶段 | actionRight | 用户心智 | 载体上通常有什么 |
| --- | --- | --- | --- |
| 意图未构成委托 | 不进任务流 | 只是沟通 | 仅 Conversation，无活跃 GoalPlan |
| 对齐 / 审批 / 权限 / 提问 | `needs_you` | 需要你处理 | intake 或活跃 GoalPlan |
| 计划已确认，Runner 在干活 | `peer_advancing` | Peer 正在推进 | 活跃 GoalPlan + Runner |
| 做完但人还没点头 | `result_ready` | 结果待验收 | GoalPlan `completed` 且未验收 |
| 暂停 | `paused` | 已暂停 | 任务抽屉可见 |
| 已验收 / 取消 / 失败 | `terminal` | 历史 | 历史抽屉 |

互斥（已经写进 `followed-discussions.md`，这里升级为身份规则）：

- 同一 `conversationId` 不能同时出现在任务桶、正在讨论、关注的讨论。
- 有活跃行动权的会话，必须从「正在讨论」退出。
- `source: 'conversation'` 只用于「无任务事实的沟通」，动作是打开 / 继续讨论，不是验收。

Automation 是另一条源（`source: 'automation'`），进同一块行动权板，但不冒充 Conversation。点进去走 Automation 结果视图；需要续聊时再打开或创建绑定会话。

---

## 6. 身份泄漏清单（真正要补的）

这些不是「再做一个任务系统」，而是把已经成立的任务心智，从还露着会话骨头的表面收进去。

### 6.1 创建

| 现状 | 目标态 |
| --- | --- |
| 按钮写「新建任务」，API 是 `conversationsCreate` | 文案保持「新建任务」；实现仍创建 Conversation，这没问题 |
| 首条消息前没有 GoalPlan | 允许。委托未成立前只是空白载体 |
| 模型把闲聊做成 GoalPlan | intake 收敛继续删；禁止为了「看起来像任务」强行建 plan |

### 6.2 打开

| 现状 | 目标态 |
| --- | --- |
| 部分入口关抽屉、切主 Chat | 从工作台 / 任务 / 历史 / 结果进来，一律会话抽屉；主区仍是工作台 |
| 深链只有 `conversationId` | 深链继续用 `conversationId`（载体主键不变），但打开的是「任务现场」：消息 + Goal 面板 + 当前行动权 |
| 有 `planId` 的通知只跳会话顶部 | 能落到对应 plan / 验收卡 / 提问点 |

### 6.3 列表与搜索

| 现状 | 目标态 |
| --- | --- |
| `⌘K` 搜会话并跳转 | 搜的是任务线：标题优先用 GoalPlan.title，没有 plan 再用会话题 |
| `@` 只出会话 | `@` 先钉工作区文件，会话降为 Chats；P2 才允许钉当前 Goal / Thread 的标题 + id |
| 侧栏不再堆会话，但搜索结果仍像聊天记录 | 结果行要带行动权标签（推进中 / 待你处理 / 待验收 / 讨论） |

### 6.4 命名

| 现状 | 目标态 |
| --- | --- |
| 卡片标题经常是用户原话、`commit`、`测试一下` | 委托成立后，标题以 GoalPlan.title 为准；用户原话只做创建时的草稿 |
| 内部计数泄漏（`GoalPlan 0 / 1`） | 用户面只说当前步骤和行动权，不说内部对象名 |

### 6.5 跨端

Desktop / TUI / CLI 共用 Conversation + GoalPlan。从 Desktop 切到 CLI，**任务身份不变**，只是呈现从抽屉变成状态行。TUI 的 `@` 按文件引用设计，Desktop 按会话引用实现——这是口径分裂，必须在 Composer 方案里收齐，不能一边钉文件一边钉会话。

---

## 7. 分层怎么改，存什么不改

```text
不改（真源）
  Conversation.id              载体主键
  GoalPlan.*                   执行与验收事实
  parentPlanId / sourceTaskId  目标线
  actionRight 聚合             流转

要改（投影与入口）
  打开方式                     抽屉而不是切主 Chat
  列表标题                     plan.title > thread root title > conversation.title
  搜索 / @                     按任务线和文件，而不是只按会话
  深链附加参数                 conversationId + planId + attention
  用户文案                     任务 / 目标线 / 讨论，不说 Conversation
```

协议上**可以**给投影加只读字段，但不把它们提升成新实体：

```ts
// TaskOverviewItem 已有 / 应补齐的身份投影
{
  id: string;                 // 投影 id（plan / automation / conversation）
  conversationId?: string;    // 载体，深链用
  planId?: string;
  rootPlanId?: string;
  parentPlanId?: string;
  actionRight: TaskActionRight;
  source: 'goal_plan' | 'automation' | 'conversation';
  title: string;              // 用户可见任务名
  rootPlanTitle?: string;     // 目标线名
}
```

`source: 'conversation'` 长期保留，专门表示「还没成为任务的沟通」。不要为了报表好看，把所有会话都标成任务。

---

## 8. 和相邻方案怎么接

| 主题 | 谁说了算 | 这份文档补什么 |
| --- | --- | --- |
| 首页分桶、文案、去重 | `peer-task-flow-action-right-correction.md` | 不改主轴；只要求泄漏入口服从行动权 |
| 工作台抽屉 / 继续讨论 | `peer-2-0-workbench-flow.md` | 把「打开 = 任务现场」写成身份规则；其 §15「无计划也是 Task / paused」已被本文覆盖 |
| 副作用准入、验收 | `task-lifecycle-and-acceptance-flow.md` | 委托成立才有 Task 心智 |
| intake 误删 | `intake-convergence.md` | 中断不是聊天 |
| 验收后追问 | Goal Thread 技术设计 | 派生 ≠ 新任务 |
| Composer `@` | `composer-at-context-picker.md` | `@` 钉对象，不拿会话当唯一身份；Goal 引用放到 P2 |
| 关注的讨论 | `followed-discussions.md` | 讨论不是任务桶的备用仓库 |

`@` 的 P2（钉 Goal / Plan）必须克制：只钉标题 + `planId` / `rootPlanId`，禁止把 runner 状态、子任务列表、整份 evidence 塞进提示词。那是执行事实，不是用户点名的上下文。

---

## 9. 分阶段

### P0 — 先把「打开」收成任务现场

目标：用户从工作台点一张卡，感觉是在处理这件事，而不是被丢进一个聊天页。

1. 所有从工作台 / 任务抽屉 / 历史 / 结果 / 通知进来的续接，走会话抽屉；主区保持工作台。
2. 抽屉标题用任务名（GoalPlan.title 或目标线名），副文案用行动权，不露 `conversationId`。
3. 能带 `planId` 的入口落到对应计划 / 验收点。
4. 搜索结果带行动权标签；无 plan 的会话标明「讨论」。

验收：从首页点「需要你处理 / 待验收」，关抽屉后还在工作台；标题不是裸会话 id。

### P1 — 创建与命名

1. 「新建任务」仍创建 Conversation，但空态文案按委托讲：先说要做什么，而不是「开始新对话」。
2. GoalPlan 一旦创建，回写任务标题；后续首页 / 抽屉 / 搜索都吃这个标题。
3. 禁止再把 `GoalPlan 0 / 1` 这类内部计数露给用户。
4. 明确新主题才新开 Conversation；追问默认走 Goal Thread。

验收：同一件事验收后再追问，首页按目标线归组，不出现第二张无关顶层卡。

### P2 — 入口对齐身份

1. 落地 `@` P0（工作区文件 + 会话），见 Composer 方案。
2. `@` / `⌘K` 的会话命中展示任务标题和行动权，不再只展示聊天名。
3. 允许 `@` 钉当前目标线（标题 + planId），只作引用，不内联执行状态。
4. TUI 与 Desktop 的 `@` 口径对齐：都是钉对象。

验收：用户不会在「任务工作台」里打开一个只认得会话的 `@` 菜单而不知所措——至少文件和任务标题都在。

### P3 — 可选的载体元数据（仍不是新表）

若 P0–P2 之后仍难区分「空白任务载体」和「闲聊」，才允许给 Conversation 加极薄字段，例如 `kind: 'task_carrier' | 'chat'`、`lastPlanId`。这是索引，不是身份层。没有产品证据前不做。

---

## 10. 明确不做

- 不新建 Task / Project / Portfolio 表来「彻底去会话化」。
- 不把所有 Conversation 强制升级为 GoalPlan。
- 不把首页改回会话列表，也不做成全部 GoalPlan 仓库。
- 不让 Canvas、讨论区、`@` 菜单各自维护一份任务状态。
- 不在 renderer 里根据最后一条消息推断行动权。
- 不把 Automation 塞进 Conversation 里冒充普通任务。
- 不把 Goal Thread 做成同会话并行多计划同时 executing。

---

## 11. 成功标准

用户可感知：

1. 工作台上点任何一张有行动权的卡，进来是「这件事」，不是「某条聊天」。
2. 纯问答不会突然出现在待验收。
3. 验收后再问一句，还在原来的目标线上。
4. 想另做一件事，才是「新建任务」。
5. `@` 不再让人觉得 Peer 只认识会话。

工程可验收：

1. 仍然没有独立 Task 表；载体主键仍是 `conversationId`。
2. 有副作用路径无活跃 GoalPlan 时继续被拒。
3. `source: 'conversation'` 只出现在无活跃行动权的沟通投影。
4. 同一 `conversationId` 不同时出现在任务桶和正在讨论。
5. 派生计划带 `parentPlanId` / `rootPlanId`；首页按目标线分组。
6. 从工作台打开的续接可关闭抽屉并回到工作台（P0）。

---

## 12. 给实现的口诀

```text
存：Conversation
做：GoalPlan / Runner
连：Goal Thread
看：行动权
说：任务
```

五件事各管各的。把「说」改成「会话」，用户以为回到了聊天软件；把「存」改成新建 Task 表，会和 2.0 对象模型决裂。正确的收口是：**继续用会话存，继续用计划做，只让用户看见任务在流转。**
