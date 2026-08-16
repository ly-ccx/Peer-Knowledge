# Peer Agent 任务生命周期与验收流转

> 状态：已实施并通过代码验证
>
> 适用范围：Desktop Agent、GoalPlan、首页工作台、任务详情与最近讨论
>
> 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`
>
> 验证日期：2026-08-11
>
> 身份层补充：`design/product/task-identity-conversation-carrier.md`（委托成立才有 Task 心智；会话仍是载体，不另起 Task 表）

## 1. 问题与目标

当前系统已经能把持久化 GoalPlan 的未验收结果投影到首页“验收”区，但默认 Agent 允许在没有 GoalPlan 时直接执行写文件等有副作用能力。此类工作只有 conversation，没有任务事实；执行结束后首页只能把会话投影到“最近讨论”，用户看不到“待用户验收”关口。

要修复的不是讨论区样式，而是任务准入契约：**凡产生本地副作用、需要交付结果或需要验收的工作，执行前必须先建立持久化 GoalPlan。** 首页只消费持久化任务状态，不根据助手文案、最后一条消息或工具调用痕迹猜测任务是否完成。

## 2. 设计原则

1. **持久化 GoalPlan 是任务生命周期的唯一事实来源。** Conversation 只记录活动，不承担任务状态。
2. **执行结束不等于用户验收。** Agent 完成本轮、叶子任务完成、Plan 执行完成和用户验收通过必须分开表达。
3. **自动验证属于执行完成条件。** 声明了可自动验证的 Definition of Done 时，未取得通过证据不能完成 Plan。
4. **用户验收是独立持久化事实。** 通过 `resultAcceptance.acceptedAt/acceptedBy` 记录，不从聊天文本推断。
5. **首页是投影层，不补造状态。** main 进程从 GoalPlan 事实投影 `actionRight`；renderer 只按投影展示。
6. **讨论活动与任务状态正交。** 同一会话可以出现在最近讨论，同时对应任务仍在推进或待验收。

## 3. 核心事实模型

### 3.1 GoalPlan 执行状态

沿用现有 `GoalPlanStatus`，不新增与 `completed` 平行且语义重叠的 `awaiting_acceptance`：

| 状态 | 含义 | 当前行动权 |
| --- | --- | --- |
| `drafting` | 目标或计划仍在形成 | Peer / 用户，取决于缺失信息 |
| `awaiting_approval` | Plan 模式等待批准 | 用户 |
| `executing` | Agent 正在执行或可继续执行 | Peer |
| `waiting_user` | 缺少决策、权限或人工信息 | 用户 |
| `paused` | 已暂停，可恢复 | 用户 |
| `failed` | 执行失败，保留证据与恢复入口 | 用户 |
| `cancelled` | 用户取消或被新目标取代 | 无 |
| `completed` | 执行和自动验证已完成；若未验收则为待用户验收 | 用户或无 |

`completed` 必须结合 `resultAcceptance` 解读：

```text
plan.status = completed
resultAcceptance 缺失
=> 执行完成 / 待用户验收

plan.status = completed
resultAcceptance.acceptedAt 存在
=> 用户已验收 / 可归档
```

### 3.2 子任务状态

| 状态 | 语义 |
| --- | --- |
| `pending` | 尚未开始 |
| `running` | 正在执行 |
| `waiting_user` | 该步骤需要用户输入 |
| `completed` | 该步骤有 Evidence 证明完成 |
| `failed` | 该步骤失败且有失败原因 |
| `cancelled` | 该步骤不再执行 |

子任务标记 `completed` 必须附 Evidence。计划声明的自动验证标准必须有真实检查结果，不能由助手文本替代。

### 3.3 验收事实

```ts
resultAcceptance?: {
  acceptedAt: string;
  acceptedBy: 'user';
}
```

验收事实属于具体 GoalPlan，而不是 Conversation。一个会话存在多个未验收 Plan 时，应逐 Plan 展示，不能按 conversation 去重吞掉验收项。

## 4. 标准状态流转

```text
用户提出请求
  |
  +-- 纯问答 / 只读查询 ------------------------------> Conversation 活动
  |
  +-- 任何有副作用或可交付工作
        |
        v
     建立 GoalPlan（目标、边界、步骤、验收标准）
        |
        +-- Plan 模式 --> awaiting_approval --拒绝--> cancelled
        |                  |
        |                  +--批准----------------------+
        |
        +-- Agent 模式 accepted_goal ------------------+
                                                           |
                                                           v
                                                       executing
                                                           |
                         +---------------------------------+------------------+
                         |                                 |                  |
                         v                                 v                  v
                    waiting_user                        failed             paused
                         |                                 |                  |
                    用户补充/授权                       重试/继续           恢复
                         +---------------------------------+------------------+
                                                           |
                                                           v
                                                   自动验证与 Evidence
                                                           |
                                     +---------------------+-------------------+
                                     |                                         |
                                   失败                                      通过
                                     |                                         |
                                     v                                         v
                                  failed                                  completed
                                                                               |
                                                                      待用户验收
                                                                               |
                                              +--------------------------------+----------------+
                                              |                                |                |
                                           验收通过                         需要调整          继续讨论
                                              |                                |                |
                                              v                                +-------+--------+
                                  resultAcceptance 写盘                                |
                                              |                                        v
                                              v                                    executing /
                                         完成归档                                  waiting_user
```

## 5. 准入规则

### 5.1 无需 GoalPlan

以下工作可以保持 L0，不建立任务：

- 解释概念、回答问题；
- 读取一个事实并直接回复；
- 不产生本地或外部副作用的只读调查；
- 用户明确只要求建议或方案、没有要求落地。

### 5.2 必须建立 GoalPlan

以下任一条件成立，第一次有副作用的 Tool Call 前必须存在持久化 GoalPlan：

- 写入、编辑、创建或删除文件；
- 执行可能改变工作区、应用或外部系统状态的命令；
- 提交、发布、部署、创建 MR/CR/工单等外部动作；
- 用户要求“修改、修复、实现、落地、直接改”；
- 结果需要自动验证或用户验收；
- 工作虽小，但完成后需要出现在首页推进/验收流程中。

小改动可以使用只有一个叶子步骤的 Micro GoalPlan，不能以“L1 可选计划”为由绕过任务事实。

### 5.3 运行时强制

准入不能只依赖提示词：

1. 默认 Agent（wire `chat`）无 active plan 时，只读与问答能力照常放行；
2. 对写文件、编辑文件和明确的有副作用能力，无 active plan 时结构化拒绝；
3. 拒绝结果指导模型先调用 `goal_create_plan` 建立 Micro GoalPlan；
4. GoalPlan 建立后仍通过 Runtime Projection、PermissionGrant 与 Evidence 链执行；
5. 不新增绕过现有 capability provider 的执行通路。

## 6. 完成与验收条件

### 6.1 执行完成

Plan 只有在以下条件全部满足时才能进入 `completed`：

- 所有叶子任务均处于终态；
- 没有失败叶子任务；
- 每个完成任务都有 Evidence；
- 每个自动验证标准都有真实且通过的检查结果；
- 没有尚待用户输入的步骤。

### 6.2 待用户验收

Plan 成为 `completed` 且没有 `resultAcceptance` 后：

- 首页投影为 `actionRight = result_ready`；
- 状态文案表达“待用户验收”，不是“已结束”；
- 显示改动摘要、Evidence、验证结果和打开任务入口；
- 不因会话已有最近消息而隐藏验收项。

### 6.3 验收通过

用户点击“验收通过”后：

- main 进程原子写入 `resultAcceptance`；
- 工作台验收卡在成功响应后再播放退出动画；
- 任务进入历史/归档；
- Conversation 仍可保留在最近讨论，其含义只是活动记录。

### 6.4 需要调整 / 继续讨论

用户选择继续处理时：

- 清除旧的 `resultAcceptance`（若有）；
- 同一 Plan 从 `completed` 恢复到 `executing` 或 `waiting_user`；
- Runner 状态与 Plan 状态原子一致；
- 原 Evidence、失败记录和运行轨迹保留；
- 首页从验收区移回推进区或“需要你”区。

## 7. 首页投影规则

首页三个区域表达不同维度：

| 区域 | 数据来源 | 语义 |
| --- | --- | --- |
| PEER 推进 | GoalPlan/Automation 投影，`peer_advancing` | Peer 当前持有行动权 |
| 需要你 / 验收 | GoalPlan 投影，`needs_you` / `result_ready` | 用户当前需要决策、补充或验收 |
| 最近讨论 | Conversation 投影 | 最近发生的会话活动，不代表任务终态 |

规则：

- Conversation 与 GoalPlan 可以同时展示，因为维度不同；
- 验收项按 `planId` 唯一，不按 `conversationId` 合并；
- 已验收 Plan 不再进入当前行动区，只进入历史；
- 无 GoalPlan 的副作用工作应被运行时阻止，因此不再出现“只进讨论、不进验收”的新案例。

## 8. 异常与恢复

| 场景 | 处理 |
| --- | --- |
| 自动验证失败 | 保持/进入 `failed`，记录命令输出 Evidence，提供继续入口 |
| 权限缺失 | `waiting_user`，明确所需授权，不伪装完成 |
| 网络或流式中断 | 投影 `paused/resume`，恢复时清除中断事实 |
| 用户取消 | `cancelled`，保留历史 Evidence |
| 新目标取代旧目标 | 旧 Plan 按规则完成、失败或取消，不留下 executing 僵尸计划 |
| 验收接口失败 | 卡片保持待验收，不先行退出或乐观归档 |
| 验收不通过 | 重开同一 Plan，保留旧 Evidence，追加调整步骤或事件 |
| 存量 completed 无验收字段 | 按上线时间祖父化，避免历史任务批量进入验收队列 |

## 9. 落地改动规划

### 9.1 运行时契约

修改默认 Agent 的 Goal mode gate：无 active GoalPlan 时，对有副作用能力返回 `goal_plan_required_for_side_effect`；只读能力不受影响。该规则位于 Runtime Projection 与 PermissionGrant 之间，保证不是提示词约定。

### 9.2 模型引导

同步 System Context 的自适应规划说明：L1 可以使用 Micro GoalPlan，但只要要执行副作用操作，就不再是“formal GoalPlan optional”。模型在首次写入前应创建最小持久化计划，并声明机器可验证的完成标准。

### 9.3 状态与首页

复用现有：

- `GoalPlan.status = completed`；
- `resultAcceptance`；
- `projectGoalPlan(...).actionRight = result_ready`；
- 工作台验收通过与继续讨论动作。

不在 renderer 增加 `capabilityId` 分支，不从消息文本推断“已改好”。

### 9.4 测试

至少覆盖：

1. 默认 Agent 无 active plan 时，只读工具仍可执行；
2. 默认 Agent 无 active plan 时，写文件/编辑文件被拒绝并要求建 Plan；
3. 建立 active accepted GoalPlan 后，同样写操作放行；
4. completed + 无 resultAcceptance 投影为 `result_ready`；
5. 验收后退出当前行动区；
6. 同一 conversation 的讨论项不吞掉 Plan 验收项；
7. 继续讨论重开同一 Plan。

## 10. 实施结果与验收

### 10.1 已落地实现

- `apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs`
  - 默认 Agent（wire `chat`）和 legacy `goal` 无非终态 GoalPlan 时，仅放行规划、提问与只读能力；
  - 副作用能力返回 `goal_plan_required_for_side_effect`，并引导创建单步骤 Micro GoalPlan；
  - `completed`、`cancelled`、`failed` 等历史计划不能为新副作用授权，必须新建或重开计划。
- `packages/protocol/src/task-overview.ts`
  - completed 且未验收的 `result_ready` 投影文案明确为“待用户验收”。
- 测试夹具与断言
  - gate 纯函数、projected-tool executor 真实接线、协议投影和首页验收流转均有回归覆盖；
  - 既有 LLM chat service 测试注入执行中计划事实，继续验证权限、文件边界、循环预算和取消链。

### 10.2 验证结果

- [x] 文档与实现一致；
- [x] 默认 Agent 的副作用操作无法绕过 GoalPlan；
- [x] 小型修改可建立单步骤 Micro GoalPlan；
- [x] 自动验证失败不会进入待用户验收；
- [x] 自动验证通过后进入待用户验收；
- [x] 用户验收通过后才归档；
- [x] 最近讨论仍独立记录会话活动；
- [x] Desktop typecheck 通过：`pnpm --filter @peer-agent/desktop typecheck`；
- [x] Desktop 完整测试通过：2414 tests，2414 pass，0 fail；
- [x] Desktop build 通过：`pnpm --filter @peer-agent/desktop build`。

构建仅保留 Vite 已有的大 chunk 警告，不影响退出码和本次验收。

## 11. 非目标

- 不把每个纯问答都变成任务；
- 不用助手回复中的“完成、已改好”等词判断状态；
- 不用首页临时卡片替代持久化 GoalPlan；
- 不新增第二套文件执行、权限或 Evidence 通路；
- 不强制用户对 Automation 的每次成功运行逐项验收；Automation 继续遵循其独立产品策略。
