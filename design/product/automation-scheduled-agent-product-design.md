# Automation 定时 Agent 产品方案

> 创建时间：2026-08-04
>
> 最后更新：2026-08-04
>
> 文档状态：产品设计冻结 / P0 实施基线
>
> 适用范围：Peer Desktop（macOS 优先）、Local Runtime、Task Center、Conversation、Workspace
>
> 关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）
> 关联文档：
> - `design/product/peer-2-0-product-system.md`
> - `design/product/status-bar-task-center.md`
> - `design/product/task-completion-system-notification.md`
> - `design/product/agent-mode-default-and-adaptive-planning.md`
> - `knowledge/decisions/21-pending-task-resume.md`
> - `knowledge/decisions/27-workspace-switch-and-cross-workspace-running.md`
> - `knowledge/decisions/49-cancel-path-hard-sandbox.md`

---

## 0. 文档目的与结论

本文冻结 Peer Automation 的产品定位、对象边界、信息架构、核心流程、页面规格、安全授权、调度恢复、Git Worktree、通知回流、状态模型、P0 范围和验收标准。

本文是产品基线，不代表代码已经实现。后续领域模型、IPC、持久化、调度器和界面实现必须以本文为输入；若实施发现产品契约不可成立，应先修订本文或新增 ADR，不应在代码中静默改变语义。

### 0.1 一句话定义

> **Automation 是一种可以按时间规则重复创建并执行 Agent Run 的长期委托。**

它不是“定时发送一条 Prompt”，也不是节点式工作流系统。完整闭环是：

```text
创建长期委托
  → 到点或手动触发
  → 创建独立 Run
  → 在受控权限与执行环境中运行 Agent
  → 保存不可变结果与证据
  → 通知并精确回流
  → 用户审核、处理或重跑
```

### 0.2 P0 产品承诺

Peer P0 提供本地优先的 Scheduled Agent：

- 用户可从对话或 Automation Center 创建定时委托；
- Peer 在本机后台常驻且本机可用时执行；
- 每次触发创建独立 Fresh Run 和 Conversation；
- 只读任务直接读取绑定工作区；
- Git 写入任务默认在隔离 Worktree 中修改和验证；
- 每次运行产生可审计、不可变的结果收据；
- 需要输入、权限或发生失败时精确通知用户；
- 不自动 push、创建 MR、合并、发布或执行其他高风险操作。

### 0.3 已冻结的十三项决策

| # | 决策 | 冻结结论 |
|---|---|---|
| 1 | 创建入口 | 对话与 Automation Center 双入口，统一确认页 |
| 2 | 信息架构 | Automation Center 为全局一级导航 |
| 3 | Center 首页 | 轻量概览条 + 主列表 |
| 4 | 创建流程 | 结构化单页 + 最终确认 |
| 5 | Automation 详情 | `Overview + Runs` 双页签 |
| 6 | Run 与会话 | 结果收据页 + Conversation 双向回流 |
| 7 | 权限模型 | 安全预设 + 高级自定义，分期实现 |
| 8 | 调度输入 | 自然语言理解 + 可视化规则确认 |
| 9 | 运行上下文 | Fresh Run + 受控历史摘要，分期实现 |
| 10 | 通知策略 | Attention-first + 可配置成功通知 |
| 11 | 后台模型 | Peer 后台常驻，本机可用时运行 |
| 12 | 写入位置 | 只读直接工作区；Git 写入默认隔离 Worktree |
| 13 | P0 能力 | 只读 + Git Worktree 隔离写入 |

---

# 第一篇：产品定位与边界

## 1. 用户问题

Peer 已经可以在一次会话中规划、调用工具、修改文件并验证结果，但用户仍需在合适的时间主动回来发起任务。以下重复工作不应持续依赖人工启动：

- 每个工作日检查失败 CI；
- 每周扫描依赖与安全风险；
- 每天整理指定项目的变化；
- 定期查询日志、指标、缺陷或合并请求；
- 定时生成报告；
- 在安全边界内尝试本地修复并运行验证。

用户需要的不只是准时触发，而是能够回答：

1. Peer 将做什么、在哪做？
2. 什么时候执行，时区是什么？
3. 无人值守时允许它做什么？
4. 电脑休眠或应用退出后如何处理？
5. 上一次还没完成时怎么办？
6. 它实际做了什么，如何证明结果？
7. 出现风险或歧义时如何让用户接管？

## 2. 品类定位

Automation 是 Peer 2.0“持续委托”能力的一种触发方式：

```text
Automation Definition（长期规则）
        │
        ├── scheduled trigger
        ├── manual trigger
        └── retry trigger
        ▼
Automation Run（单次任务实例）
        ├── Conversation（执行过程与人工交互）
        ├── Execution Workspace（工作区或 Worktree）
        ├── Grant Snapshot（权限快照）
        └── Run Receipt（结果与证据）
```

### 2.1 Automation 与 Task 的区别

| 对象 | 生命周期 | 主要问题 |
|---|---|---|
| Automation | 长期存在、可启停、可修改 | 未来应按什么规则反复做什么？ |
| Run / Task | 每次触发创建、最终终结 | 这一次正在发生什么、结果如何？ |
| Conversation | 跟随单次 Run，可继续人工交互 | Agent 如何执行、哪里需要用户回答？ |

因此：

- Automation Center 管“规则与未来”；
- Task Center 管“运行与现在”；
- Conversation 管“过程与人工交互”；
- Run Detail 管“结果、证据与审计”；
- Workspace 管“资源与作用域”。

### 2.2 Automation 与 Workflow 的区别

P0 Automation 只有一个 Agent 委托，不提供节点、连线、条件分支、循环或 DAG。用户表达目标，Agent 自主规划本次 Run 的内部步骤。

未来若提供 Workflow，它可以成为 Automation 的执行目标之一，但不能反向把 P0 Automation 创建页演化为低代码画布。

## 3. 设计原则

### 3.1 委托优先，而非配置优先

对话应允许用户自然表达“做什么、什么时候做”；系统再把意图转换成结构化草稿。用户不应先学习 Cron 和内部权限 ID。

### 3.2 明示长期授权

会话里的临时权限不能自动变成长期无人值守授权。创建前必须让用户看懂：

- 自动允许什么；
- 哪些操作会暂停询问；
- 哪些操作始终阻止。

### 3.3 每次运行可重现、可审计

Automation 定义可以变化，但历史 Run 必须保留当时实际使用的 Prompt、时间规则、权限、模型、工作区、Git 基线和结果证据。

### 3.4 本地优先，诚实表达可用性

P0 不承诺离线云执行。只有本机开机、Peer 进程运行且所需资源可用时，Automation 才能执行。

### 3.5 异常优先，避免通知疲劳

需要用户行动的状态优先于普通成功结果；成功通知可以关闭，但待处理事项必须在 Automation Center 中持续可见。

### 3.6 隔离优先，避免污染当前工作

Git 写入任务默认使用独立 Worktree，不直接修改用户正在使用的工作副本。

## 4. 目标与非目标

### 4.1 P0 目标

1. 用户能在两分钟内创建一个可理解、可控的定时委托；
2. 同一计划时刻至多创建一次 Run；
3. 应用重启、电脑唤醒后能按约定恢复调度；
4. Agent 能在只读或隔离写入模式下完成任务；
5. 每次 Run 都有独立会话、配置快照和结果收据；
6. 权限不足、失败和用户输入能形成稳定待办；
7. 用户能暂停、恢复、立即运行、取消和重跑；
8. 用户明确知道本机退出或休眠期间不会执行。

### 4.2 P0 非目标

- 节点式工作流、DAG、条件分支、循环；
- Webhook、Git 事件、文件变化等事件触发；
- 云端 Runner 或关机后继续执行；
- 非 Git 工作区的无人值守自动写入；
- 永久延续同一个 Conversation；
- 自动 push、创建 MR、合并、审批或发布；
- 数据库写入、付款、下单等高风险外部副作用；
- 团队共享、多设备同步和企业审批流；
- 完整 Skill/MCP 权限编辑器；
- 秒级、高频或实时调度。

---

# 第二篇：信息架构与核心对象

## 5. 全局信息架构

```text
Peer
├── Conversations
├── Workspaces
├── Tasks
├── Automations
│   ├── Automation Center
│   ├── Create / Edit Automation
│   ├── Review & Confirm
│   └── Automation Detail
│       ├── Overview
│       └── Runs
│           └── Run Detail
├── Skills
└── Settings
```

Automation Center 是全局一级入口，默认跨工作区展示。Workspace 可在后续提供该工作区关联 Automation 的投影，但不建立第二套管理系统。

Task Center 只投影：

- 正在运行的 Automation Run；
- 等待权限或输入的 Run；
- 失败、超时或刚完成且未读的 Run。

## 6. 概念对象

### 6.1 Automation Definition

长期存在、可编辑的委托定义，至少包含：

- `automationId`；
- 名称；
- 指令 Prompt；
- 绑定 Workspace；
- Schedule；
- Grant；
- 执行副本策略；
- 错过运行策略；
- 重叠运行策略；
- 通知策略；
- 预算与超时；
- 生命周期状态；
- 创建、更新和下一次运行时间。

### 6.2 Schedule

真实保存的是结构化规则，不是自然语言字符串。已冻结的 P0 规则类型：

- `once`；
- `hourly`；
- `daily`；
- `weekdays`；
- `weekly`；
- `monthly`；
- `custom_cron`。

Schedule 必须保存时区。自然语言只是输入方式，可视化规则和未来运行预览才是用户确认的事实。`custom_cron` 位于 Advanced，仅支持分钟级 Cron，不接受秒字段；保存前同样必须解析并展示未来三次运行。

### 6.3 Automation Grant

Automation 独立的长期授权，不继承当前 Conversation 权限。P0 预设：

- `observe`；
- `work_in_workspace`。

### 6.4 Automation Run

某次触发产生的不可复用运行实例。Run 必须记录：

- `runId`、`automationId`；
- `scheduledAt`、`createdAt`、`startedAt`、`finishedAt`；
- 触发来源；
- 幂等键；
- Run 状态与阻塞原因；
- Definition、Schedule、Grant 快照；
- Workspace、Git 和模型快照；
- Conversation ID；
- Worktree 信息；
- 结果、证据、用量和费用。

### 6.5 Conversation

每个 Run 创建独立 Conversation，用于：

- 展示完整 Agent 过程；
- 用户回答 `waiting_user`；
- 用户在 Run 后继续人工跟进。

Run 完成后的 Conversation 后续消息不能反写或修改旧 Run 收据。

### 6.6 Run Receipt

Run Detail 展示的不可变结果，包括：

- 最终摘要；
- 文件变化；
- Diff；
- 验证命令和结果；
- 工具活动；
- 错误与阻塞信息；
- Token、费用和耗时；
- 当时的上下文与授权快照。

## 7. 对象关系与不变量

```text
Workspace 1 ── N Automation
Automation 1 ── N Run
Run 1 ── 1 Conversation
Run 0..1 ── 1 Worktree
Run 1 ── 1 Grant Snapshot
Run 1 ── 1 Receipt
```

必须保持以下不变量：

1. Automation 与 Run 分离；
2. 修改 Automation 不改变历史 Run；
3. 每个 Run 只属于一个 Automation；
4. 每个 Run 有独立 Conversation；
5. 同一 `automationId + scheduledAt` 至多创建一个 Run；
6. 完成后的 Run 收据不可被继续聊天修改；
7. 扩大 Automation Grant 必须显式重新确认；
8. P0 同一 Automation 不并行；
9. P0 同一 Workspace 的写入型 Run 串行；
10. Git 写入型 Run 默认不修改原工作副本。

---

# 第三篇：端到端用户流程

## 8. 从 Automation Center 创建

```text
Automations
  → New automation
  → 填写结构化单页
  → Review automation
  → 检查 What / Where / When / Access / Notify
  → Create & enable
  → Automation Overview
```

关键规则：

- 未点击 `Create & enable` 前只存在草稿；
- 下一次运行时间必须在确认页可见；
- 如果工作区、权限或调度无效，不能启用；
- 创建成功后显示明确反馈与下一次运行时间。

## 9. 从 Conversation 创建

用户可以表达：

> 每个工作日上午 9 点检查这个项目的失败 CI，如果能安全修复就修复并运行测试。

Peer 从当前上下文提取：

- 建议名称；
- Prompt；
- 当前 Workspace；
- `weekdays 09:00`；
- 当前系统时区；
- 基于意图建议 `observe` 或 `work_in_workspace`；
- 默认通知、补偿与重叠策略。

会话内只生成草稿卡：

```text
Automation draft ready

每日 CI 巡检
Every weekday at 09:00 · Asia/Shanghai
Workspace: peer_agent
Access: Work in workspace

[Review & create]
```

不允许在聊天里通过一句自然语言直接启用。用户点击后进入统一结构化配置和确认流程。

## 10. 手动立即运行

入口：

- Automation Center 列表 `Run now`；
- Automation Overview `Run now`。

规则：

- 手动运行使用当前已保存 Definition 和 Grant；
- 创建独立 Run；
- `triggerSource = manual`；
- 与定时运行使用相同 Runner、权限、Worktree 和收据链路；
- 如果已有活跃 Run，按重叠策略处理，并明确告知用户；
- 手动运行不改变下一次计划时间。

## 11. 失败后重跑

入口：Run Detail 或 Runs 列表中的 `Retry`。

重跑会创建新 Run：

```text
triggerSource = retry
sourceRunId = previousRunId
```

默认使用 Automation 当前配置，而不是盲目复刻旧配置。确认提示应说明：

- 若当前配置与原 Run 不同，显示“将使用当前 Automation 配置”；
- 原 Run 保持不变；
- 新 Run 在历史中与来源 Run 建立关联。

## 12. 暂停、恢复与删除

### 12.1 Pause

- 停止未来调度；
- 不取消当前已经运行的 Run；
- 下一次运行时间显示为 `Paused`；
- 手动 `Run now` 是否可用：P0 保留可用，但需明确“这不会恢复自动调度”。

### 12.2 Resume

- 从当前时间重新计算下一次运行；
- 暂停期间不累计 missed runs；
- 恢复后不补跑暂停期间的计划。

### 12.3 Delete

删除是高影响操作：

- 首先暂停调度；
- 不删除历史 Run 收据；
- 不删除仍有未处理变更的 Worktree；
- P0 使用软删除/归档语义更安全；
- 确认文案明确“历史运行仍保留用于审计”。

## 13. 全局 Pause all automations

入口：

- 菜单栏；
- Automation Center 顶部更多菜单。

语义：

- 暂停所有未来调度；
- 不取消当前 Run；
- 不改写每个 Automation 原本的 active/paused 配置；
- 恢复时仅恢复全局暂停前本来为 active 的 Automation；
- 全局暂停期间不累计补跑；
- 页面和菜单栏持续显示全局暂停状态。

---

# 第四篇：页面与交互规格

## 14. Automation Center

### 14.1 页面结构

```text
Automations                                      [+ New automation]

[Active 12] [Running 2] [Needs attention 3] [Paused 1]

[Search] [All workspaces ▾] [All schedules ▾]

! 每日 CI 巡检
  peer_agent · Weekdays at 09:00
  Waiting for permission · 8 minutes ago
  [Review request] [Run now] [···]

● 依赖安全检查
  peer_agent · Every Monday at 10:00
  Last run: Succeeded 2d ago
  Next run: Monday at 10:00
  [Run now] [···]
```

### 14.2 概览条

概览条是状态摘要，也是过滤器：

- `Active`：生命周期为 active；
- `Running`：存在活跃 Run；
- `Needs attention`：存在未处理的权限、输入、失败或配置阻塞；
- `Paused`：用户暂停、连续失败自动暂停或全局暂停影响的任务。

计数必须来自同一状态事实源，不应在各组件独立推断。

### 14.3 默认排序

```text
Needs attention
→ Running
→ 即将运行
→ 其他 Active
→ Paused
→ Disabled / Archived
```

同一优先级内按最近关注事件或下一次运行时间排序。

### 14.4 列表项必备信息

- 名称；
- Workspace；
- 人类可读调度；
- 当前健康状态；
- 上一次 Run 状态与时间；
- 下一次 Run 时间；
- 主要动作；
- 更多菜单。

不得用 Automation 生命周期状态替代 Run 状态。例如 Automation 可以仍为 active，但最新 Run 正在 `waiting_permission`。

### 14.5 搜索与筛选

P0 支持：

- 名称搜索；
- Workspace；
- 生命周期状态；
- 健康状态；
- Schedule 类型。

筛选应反映在 URL/导航状态中，通知回流后返回列表时尽量保留。

### 14.6 空状态

```text
Automate work you repeat

Schedule Peer to inspect, report, or safely work in a Git workspace.
Automations run locally while Peer is running.

[Create automation]
```

同时提供可点击示例，但不直接创建：

- 每个工作日检查失败 CI；
- 每周生成项目变化摘要；
- 每天检查待处理代码评审。

## 15. Create / Edit Automation

### 15.1 页面结构

```text
New automation

Name
[ 每日 CI 巡检 ]

What should Peer do?
[ 多行任务指令 ]

Workspace
[ peer_agent ▾ ]

Schedule
[ Every weekday ▾ ] [09:00] [Asia/Shanghai ▾]

Next runs
Tomorrow at 09:00
Wednesday at 09:00
Thursday at 09:00

Access
○ Observe
● Work in workspace

Working copy
● Isolated Git worktree

Notifications
☑ Needs attention
☑ Failed
☐ Succeeded

Advanced settings ▸

[Cancel]                                  [Review automation]
```

### 15.2 Name

- 可由 Peer 根据 Prompt 自动建议；
- 用户可编辑；
- 推荐 2–40 个字符；
- 不要求全局唯一；
- 列表中名称重复时以 Workspace 和 Schedule 区分。

### 15.3 Prompt

Prompt 应描述目标和完成标准，而不是鼓励用户编写底层步骤。辅助提示：

```text
Describe the recurring outcome, relevant constraints, and what counts as done.
```

可展示示例结构：

```text
检查什么
发现问题时怎么处理
需要运行哪些验证
什么情况下应暂停询问
```

### 15.4 Workspace

- 必须绑定一个已知本地 Workspace；
- 展示名称和绝对路径；
- 创建时验证路径存在；
- 路径消失后不自动改绑其他目录；
- Git 写入模式验证是否为受支持 Git 仓库；
- P0 不支持单个 Automation 跨多个 Workspace 写入。

### 15.5 Schedule

普通用户使用可视化规则。P0：

- Once：日期 + 时间；
- Hourly：每 N 小时，在指定分钟触发；
- Daily：每天 + 时间；
- Weekdays：周一至周五 + 时间；
- Weekly：一个或多个星期几 + 时间；
- Monthly：每月指定日期或可解释的月度规则 + 时间；
- Custom cron：Advanced 中的分钟级 Cron；
- Timezone：IANA 时区；
- 未来三次运行预览。

自然语言解析后必须填入上述结构；解析不确定时标记待确认，不能猜测启用。Hourly 和 Custom cron 同样受全局并发、预算与最低调度间隔保护；P0 不支持秒级触发。

### 15.6 Access

P0 两种预设：

```text
Observe
Read workspace files, inspect connected systems, and create reports.

Work in workspace
Modify files in an isolated Git worktree and run tests or builds.
```

访问摘要必须说明实际能力，不能只展示内部枚举值。

### 15.7 Working copy

- `Observe`：直接读取绑定 Workspace；
- `Work in workspace`：默认并固定为 Isolated Git worktree；
- P0 若不是受支持 Git Workspace，禁用写入模式并解释原因；
- 不提供“直接修改原工作副本”的 P0 入口。

### 15.8 Notifications

P0：

- `Needs attention`：默认开启，至少保留 Center badge；
- `Failed`：默认系统通知；
- `Succeeded`：默认关闭，可开启。

### 15.9 Advanced settings

P0 可包含：

- Provider / Model；
- 最大运行时间；
- 单次 Token 或费用预算；
- Missed run policy；
- Overlap policy；
- 成功通知开关。

P0 默认值：

```text
Missed run: Run latest
Overlap: Skip
Timeout: 使用全局安全默认值
Provider/Model: 使用明确保存的选择，不随当前聊天切换
```

### 15.10 编辑与重新确认

创建和编辑复用同一页面。以下变更必须进入 Review：

- Prompt；
- Workspace；
- Schedule；
- Access；
- 执行副本；
- Provider/Model；
- 预算和超时；
- Missed/Overlap 策略。

名称和通知等低风险字段也可统一走 Review，以保持 P0 交互一致；后续再优化为直接保存。

编辑提交采用原子替换：确认成功后生成新的 Definition 版本并重新计算 `nextRunAt`。已经创建的 Run 永远继续使用自己的 Definition、Grant 与执行环境快照，不因 Automation 被编辑、暂停或改绑 Workspace 而中途改变。若用户希望当前 Run 停止，必须单独执行 Cancel。

编辑过程中尚未确认的草稿不影响当前生效版本；若编辑期间调度点到达，仍按当时已生效版本创建 Run。确认页应在版本冲突时要求用户刷新，不允许用旧草稿静默覆盖更新后的定义。

## 16. Review & Confirm

### 16.1 目标

确认页不是重复表单，而是长期委托授权书。必须用人类可理解的摘要回答：

- WHAT：做什么；
- WHERE：在哪里做；
- WHEN：什么时候做；
- ACCESS：允许、询问、阻止什么；
- RECOVERY：错过和重叠如何处理；
- NOTIFY：何时通知。

### 16.2 页面规格

```text
Review automation

每日 CI 巡检

WHAT
检查最近一天失败的 CI，分析根因。如果可以安全修复，
则在隔离工作副本中修改代码并运行测试。

WHERE
peer_agent
/Users/.../peer_agent
Git worktree — isolated from your current files

WHEN
Every weekday at 09:00 · Asia/Shanghai
Next: Tomorrow 09:00, Wednesday 09:00, Thursday 09:00

ALLOWED AUTOMATICALLY
✓ Read repository files
✓ Modify files in an isolated worktree
✓ Run tests and builds

WILL PAUSE AND ASK
? Operations outside the saved grant
? Unapproved external write operations

ALWAYS BLOCKED
✕ Push or merge code
✕ Deploy to production
✕ Database writes
✕ Privileged or destructive commands

RECOVERY
If Peer was unavailable: Run the latest missed occurrence
If the previous run is active: Skip the new occurrence

NOTIFY
Failures and anything that needs attention

[Back to edit]                         [Create & enable]
```

### 16.3 确认约束

- 必须显式点击 `Create & enable`；
- 不使用默认焦点或 Enter 意外提交高影响授权；
- 如果 Write 模式无法建立隔离边界，禁止启用；
- 创建成功反馈包括下一次运行时间和本地运行限制；
- 修改授权后使用 `Review changes`，并突出新增能力。

## 17. Automation Detail：Overview

### 17.1 Header

```text
Automations / 每日 CI 巡检

每日 CI 巡检                                      Active
peer_agent · Weekdays at 09:00

                         [Run now] [Pause] [Edit] [···]

[ Overview ] [ Runs ]
```

### 17.2 内容区

- Health；
- Task；
- Schedule；
- Workspace / Working copy；
- Access；
- Notifications；
- Budget / Timeout；
- Recent runs。

Health 区优先显示：

- 当前是否可执行；
- 最近一次 Run；
- 下一次 Run；
- 连续失败次数；
- 是否存在待处理 Run；
- Runtime 是否处于 Ready / Paused / Offline。

### 17.3 操作

- `Run now`；
- `Pause / Resume`；
- `Edit`；
- 更多：Duplicate、Archive/Delete；
- 待处理时显示最高优先级恢复动作。

## 18. Automation Detail：Runs

### 18.1 列表字段

- Run 状态；
- 计划时间和实际时间；
- Trigger source；
- 耗时；
- Token / 费用；
- 一行结果或错误摘要；
- 主要动作。

### 18.2 筛选

P0：

- 状态；
- Scheduled / Manual / Retry；
- 时间范围。

### 18.3 行为

- 点击行进入 Run Detail；
- Failed / Timed out 提供 Retry；
- Waiting permission 提供 Review request；
- Waiting user 提供 Open conversation；
- Completed Run 不提供“继续修改本次结果”。

## 19. Run Detail：不可变结果收据

### 19.1 正常完成态

```text
Automations / 每日 CI 巡检 / Run #42

Succeeded
Scheduled today at 09:00 · 12m 36s

                  [Open conversation] [Run again] [···]

RESULT
发现 2 个失败 CI。修复了测试隔离问题，相关测试已通过。

CHANGES
3 files changed · +42 −18
Branch: PeerAgent/automation-ci-fix/run-42
                  [Review diff] [Open worktree] [Apply changes]

VERIFICATION
✓ pnpm test runtime-node
✓ pnpm typecheck

RUN CONTEXT
Workspace     peer_agent
Model         GPT-5.6
Access        Work in workspace
Trigger       Scheduled
Scheduled     09:00:00
Started       09:00:03
Finished      09:12:39
Usage         84k tokens · $0.42

ACTIVITY
09:00  Run started
09:01  Read CI results
09:04  Modified 3 files
09:10  Tests passed
09:12  Run succeeded
```

### 19.2 失败态

顶部必须先回答：

- 发生了什么；
- 是否产生副作用或未处理变更；
- 用户现在可以做什么。

```text
Failed
Provider request timed out after 3 attempts.
No files were changed.

[Retry] [Edit automation] [Pause]
```

如果已产生 Worktree 变更，不得笼统显示“No changes”；应保留并展示未完成变更。

### 19.3 Waiting permission

```text
Needs permission

Peer wants to perform an operation outside this Automation's saved grant.

Operation
[命令或能力摘要]

Impact
[目标、风险、作用域]

[Deny] [Allow once]
```

`Allow once` 只对当前 Run、当前能力请求有效，不扩大未来授权。

### 19.4 Waiting user

Run Detail 展示问题摘要，并把回答动作引导至 Conversation：

```text
Needs your input
Peer found two possible target branches.

[Open conversation to respond]
```

### 19.5 与 Conversation 的双向回流

- Run Detail → `Open conversation`；
- Conversation Header / Run card → `View run receipt`；
- 成功/失败通知 → Run Detail；
- Waiting user 通知 → Conversation 对应消息；
- Waiting permission 通知 → Run Detail 授权区。

继续聊天属于人工跟进，不修改已经终结的 Run。需要重新自动执行时使用 `Run again`。

---

# 第五篇：调度、后台与恢复语义

## 20. 调度规则

### 20.1 时间事实

每个 Automation 至少维护：

```text
lastScheduledAt
lastRunAt
nextRunAt
timezone
```

每次计划触发使用幂等键：

```text
automationId + scheduledAt
```

同一幂等键不能创建两个 Run。

### 20.2 时区

- 使用 IANA 时区，如 `Asia/Shanghai`；
- 默认使用创建时系统时区；
- 保存后不随旅行自动漂移；
- 页面始终展示时区；
- 夏令时语义为当地墙上时间；
- 修改时区后重新计算未来运行，不改历史 Run。

### 20.3 未来三次运行

创建、编辑和确认时展示未来三次具体时间，用于验证规则。若无法生成、时间已过或规则异常，禁止启用。

### 20.4 调度精度

P0 是分钟级用户体验，不承诺秒级准点。实际开始时间与计划时间分别记录，便于解释延迟。

## 21. Missed Run

P0 提供：

- `run_latest`：恢复后最多补跑最近一次；
- `skip`：不补跑，只记录错过事实。

默认 `run_latest`。

明确不做 `run_all`，避免多日关机后批量回放产生费用和副作用。

以下情况视为不可用窗口：

- Peer 显式退出；
- 电脑关机；
- 电脑休眠；
- Runtime 未成功启动。

恢复时：

1. 读取启用的 Automation；
2. 计算不可用期间计划点；
3. 按策略创建零个或一个 Run；
4. 使用原计划点作为 `scheduledAt`；
5. 记录实际恢复触发时间和 `missedRecovery = true`；
6. 重新计算 `nextRunAt`。

用户主动 Pause 和全局 Pause 期间不累计 missed runs。

## 22. Overlap

P0 支持：

- `skip`：默认，已有活跃 Run 时跳过新计划；
- `queue_latest`：可作为后续能力，P0 不必开放。

P0 不允许同一个 Automation 并行。重叠跳过应产生可追踪的 Run/事件，原因是 `overlap`，但不计入失败和连续失败。

## 23. Peer 后台运行

### 23.1 产品承诺

> Automations run locally on this Mac while Peer is running. If the Mac is asleep or Peer is unavailable, the latest missed run can start when Peer becomes available again.

### 23.2 窗口与进程

- 关闭主窗口：Peer 保持菜单栏后台运行；
- 显式 Quit：停止 Automation Runtime；
- 重新打开窗口：展示后台运行状态与任务；
- 当前 Run 不因主窗口关闭而中断。

### 23.3 首次启用提示

首次启用 Automation 时提示：

```text
Keep Peer running in the background

Scheduled automations run on this Mac.
Closing the window will not quit Peer.

[Enable background runtime]
```

### 23.4 退出提醒

存在 active Automation 时显式退出：

```text
Quit Peer?

3 automations are enabled. They will not run while Peer is closed.

[Cancel] [Quit anyway]
☐ Don't ask again
```

不得声称 Peer 退出后任务仍会执行。

## 24. 菜单栏

菜单栏建议提供：

```text
Peer Agent
Automations: Ready / Paused / Needs attention

Next run
每日 CI 巡检 · Tomorrow 09:00

Running
依赖巡检 · 4m

Open Automation Center
Pause all automations / Resume all automations
Quit Peer
```

菜单栏是状态投影和快捷入口，不承担完整 Automation 编辑。

## 25. 系统与资源变化

### 25.1 电脑唤醒

- 重新读取当前时间；
- 执行 missed run reconciliation；
- 不依赖旧的长 `setTimeout`；
- 去重后再创建 Run。

### 25.2 系统时间或时区变化

- 自动重算所有 `nextRunAt`；
- 保存的 Automation 时区不自动改变；
- 防止时钟回拨导致重复触发；
- UI 更新未来运行预览。

### 25.3 Workspace 消失

- 不自动切换到同名目录；
- Run 进入 blocked / needs attention；
- 通知用户重新绑定或恢复目录；
- Automation 可保持 active，但不会无限重试消耗资源。

### 25.4 Provider、凭证或工具失效

- 运行前检查；
- 产生明确阻塞原因；
- 不把认证失败包装成通用 Agent 失败；
- 用户修复后可 Retry。

---

# 第六篇：权限、安全与隔离执行

## 26. Automation Grant

### 26.1 独立授权原则

```text
Automation Grant ≠ Conversation Local Access
```

创建 Automation 时不能永久继承当前会话的 `full_local`、`session_local` 或一次性审批。Automation Grant 绑定 Automation Definition，每个 Run 保存一份不可变快照。

扩大长期授权只能通过：

```text
Edit automation
  → 修改 Access
  → Review changes
  → 显示新增能力
  → 用户确认
```

处理某次异常时的 `Allow once` 不得暗中扩大未来 Run 权限。

### 26.2 P0：Observe

允许自动执行：

- 读取绑定 Workspace；
- 搜索文件和代码；
- 查询 Git 状态、历史和 Diff；
- 执行已授权的只读查询；
- 生成报告与结果收据。

默认不允许：

- 修改任何文件；
- 执行产生本地写入的命令；
- 外部系统写操作；
- 发布、合并或删除。

如果某些“读取”命令会产生缓存、锁文件或其他副作用，应由能力分类器按实际风险判断，不能仅凭命令名称视为只读。

### 26.3 P0：Work in workspace

允许自动执行：

- 读取绑定 Git Workspace；
- 在本次 Run 的隔离 Worktree 内修改文件；
- 运行测试、类型检查和构建；
- 创建本地 Diff 和验证证据。

P0 不自动允许：

- 修改原工作副本；
- 写入绑定仓库与本次 Worktree 以外的位置；
- Git push、merge、rebase 远端共享分支；
- 创建或批准 MR；
- 部署、发布、数据库写入；
- 特权、破坏性或凭证导出操作。

### 26.4 三段式权限摘要

产品必须把能力呈现为：

```text
ALLOWED AUTOMATICALLY
WILL PAUSE AND ASK
ALWAYS BLOCKED
```

禁止只展示 `workspace_write`、`L3` 等内部术语。摘要应根据实际 Provider、Skill、MCP 和工具投影计算，而不是静态营销文案。

### 26.5 未预授权操作

运行中遇到可审批但未预授权操作：

```text
running
  → waiting_permission
  → 创建 attention event
  → 系统通知 / Center badge
  → Allow once 或 Deny
  → running / failed / cancelled
```

审批请求至少展示：

- 具体操作；
- 目标资源；
- 参数摘要；
- 风险和可能副作用；
- 它为何是完成当前 Run 所必需的。

### 26.6 始终阻止的动作

P0 不提供无人值守或临时审批入口：

- `sudo` 或等效提权；
- 大规模或不可恢复删除；
- 凭证、Cookie、Token 导出；
- 生产发布；
- 数据库写入或结构变更；
- 付款、下单；
- 自动审批或合并；
- 绕过现有权限系统。

若 Agent 需要这些动作，应停止并解释，不伪装成成功。

## 27. 权限与能力漂移

Automation 创建后，环境可能变化：

- MCP 被重装或换身份；
- Skill 更新并增加新工具；
- Provider 行为变化；
- Workspace 路径或 Git remote 变化；
- 授权凭证被替换。

规则：

1. 新增能力不自动继承；
2. Run 使用创建时可解析的当前能力，但受保存 Grant 上限约束；
3. 身份或目标资源变化且风险上升时进入 `needs_attention`；
4. 用户必须重新审核才能扩大未来授权；
5. 历史 Run 保留原能力与身份快照。

## 28. Git Worktree 执行模型

### 28.1 适用范围

- `observe`：直接读取绑定 Workspace，不创建 Worktree；
- `work_in_workspace`：P0 仅支持有效 Git Workspace，并默认创建隔离 Worktree；
- 非 Git Workspace：P0 只能创建 Observe Automation。

### 28.2 Run 启动流程

```text
读取 Automation 与 Workspace
  → 验证 Git 仓库
  → 记录基线 commit / branch / dirty state
  → 创建本次 Run 专用分支
  → 创建隔离 Worktree
  → 准备执行环境
  → 启动 Agent
```

分支名必须遵守代码仓配置的分支规则；在当前 Peer 项目中，新分支使用 `PeerAgent/` 前缀。通用产品层应由仓库策略提供前缀，不硬编码特定项目约束。

### 28.3 基线语义

默认从绑定 Workspace 当前 `HEAD` 创建，不包含原工作副本未提交修改。创建页和确认页必须说明：

> Isolated runs start from the saved Git revision and do not include uncommitted changes in your current workspace.

如果 Workspace 有未提交修改：

- Observe 仍可读取当前工作副本；
- Write Automation 仍从 Git 基线创建 Worktree；
- 不把用户未提交内容复制进 Worktree；
- Run 收据记录基线 commit，避免误解。

### 28.4 Worktree 生命周期

| Run 结果 | 有无变更 | 默认处理 |
|---|---:|---|
| Succeeded | 无 | 可自动清理 Worktree |
| Succeeded | 有 | 保留，等待用户审核或应用 |
| Failed / Timed out | 无 | 可自动清理 |
| Failed / Timed out | 有 | 保留并标记未完成变更 |
| Cancelled | 无 | 可自动清理 |
| Cancelled | 有 | 保留，直到用户明确丢弃 |

不得自动删除用户尚未处理的变更。

### 28.5 Run Detail 动作

有变更时提供：

- `Review diff`；
- `Open worktree`；
- `Apply changes`；
- `Discard changes`。

P0 不提供：

- 自动 push；
- 自动 MR；
- 自动 merge；
- 自动覆盖当前 Workspace。

### 28.6 Apply changes

`Apply changes` 是显式用户动作，不属于无人值守 Run。执行前：

- 检查原 Workspace 是否仍存在；
- 检查当前 Git 状态；
- 预测冲突；
- 明确展示目标文件和影响；
- 冲突时不强制覆盖，转为人工处理。

应用成功后，Run 收据追加一条“用户在何时应用”的审计事件，但不得改写原始 Run 结果和 Diff。

### 28.7 依赖与环境准备

P0 不应默认执行不受控安装。策略建议：

- 优先复用仓库已有依赖缓存；
- 若测试缺少依赖，按 Grant 判断是否允许；
- 安装命令若涉及网络或脚本执行，必要时暂停询问；
- 环境准备失败应单独标识，不能误报为代码验证失败。

## 29. 并发与资源保护

### 29.1 同一 Automation

P0 同一时间只允许一个非终态 Run。新计划到达时默认产生 `skipped_overlap` 记录，不启动第二个 Agent。

### 29.2 同一 Workspace

- Observe Run 可按全局并发额度并行；
- Worktree 写 Run 默认按 Workspace 串行；
- 即使 Worktree 文件隔离，也要避免同时消耗过多 CPU、网络和 Provider 配额；
- P0 不承诺多个写 Run 并行。

### 29.3 全局并发

需要全局 Runner 并发上限和队列。达到上限时 Run 进入 `queued`，而不是静默丢失。排队时间计入审计，但不计入 Agent 实际执行耗时。

### 29.4 预算

P0 至少支持安全默认值：

- 单 Run 最大运行时间；
- 单 Run Token / 费用上限；
- 每日运行次数保护；
- 连续失败熔断。

达到预算时进入明确终态或待处理状态，不能继续无界消耗。

---

# 第七篇：状态模型与异常语义

## 30. Automation 生命周期状态

```text
draft
active
paused
completed
disabled
archived
```

| 状态 | 含义 | 是否计算 nextRunAt |
|---|---|---:|
| `draft` | 尚未确认启用 | 否，仅预览 |
| `active` | 自动调度已启用 | 是 |
| `paused` | 用户或系统暂停 | 否 |
| `completed` | 一次性计划已经消费，不再自动调度 | 否 |
| `disabled` | 配置无效、能力被移除等导致不可运行 | 否 |
| `archived` | 不再调度，仅保留历史 | 否 |

“连续失败 3 次自动暂停”应使用 `paused` 并携带 `pauseReason = consecutive_failures`，而不是创造无法解释的新生命周期。

一次性 Automation 在唯一计划点成功创建 Run 后即消费 Schedule，并在该 Run 进入终态后转为 `completed`，不因 Run 失败而自动再次调度。用户可在 Run Detail 中 Retry，或编辑 Automation 选择新的日期后重新启用。若计划点因不可用而采用 `run_latest`，补跑的 Run 即为该一次性计划的唯一消费；若采用 `skip`，记录 skipped 后同样转为 `completed`。

## 31. Automation 健康状态

生命周期与健康状态分离。健康状态是当前投影：

```text
healthy
running
needs_attention
degraded
paused
offline
```

优先级：

```text
needs_attention
→ running
→ degraded
→ offline
→ healthy
→ paused
```

健康状态由当前 Runtime、最近 Run、待处理事件和生命周期共同计算，不能持久化为另一套互相冲突的事实源。

## 32. Run 状态机

P0 Run 状态：

```text
scheduled
queued
preparing
running
waiting_permission
waiting_user
succeeded
failed
cancelled
skipped
timed_out
blocked
```

主路径：

```text
scheduled
  → queued
  → preparing
  → running
  ├── waiting_permission → running
  ├── waiting_user       → running
  ├── succeeded
  ├── failed
  ├── timed_out
  └── cancelled
```

调度侧路径：

```text
scheduled
  ├── skipped(overlap)
  ├── skipped(missed_policy)
  └── blocked(preflight reason)
```

### 32.1 终态

```text
succeeded
failed
cancelled
skipped
timed_out
blocked
```

`waiting_permission` 和 `waiting_user` 不是终态，必须可恢复或由用户终止。

### 32.2 Blocked reason

至少区分：

- `workspace_missing`；
- `workspace_not_git`；
- `git_baseline_invalid`；
- `provider_unavailable`；
- `auth_expired`；
- `capability_missing`；
- `grant_invalid`；
- `budget_exhausted_before_start`；
- `runtime_unavailable`。

### 32.3 Skipped reason

至少区分：

- `overlap`；
- `missed_policy`；
- `automation_paused`；
- `global_pause`。

Pause 期间可以只记录调度审计事件而不创建大量 Run 行；无论采用哪种存储方式，产品不得把 skipped 计为失败。

## 33. 运行前检查

创建 Agent 前执行：

1. Automation 仍 active；
2. 幂等键尚未消费；
3. Workspace 存在；
4. Write 模式下 Git 仓库有效；
5. Provider、模型和凭证可用；
6. 所需工具能力存在；
7. Grant 仍可解释；
8. 无活跃重叠 Run；
9. 未超过并发和预算；
10. 能创建并持久化 Run 与 Conversation。

只有检查通过后才进入 Worktree 准备与 Agent 执行。检查失败仍要留下可解释记录。

## 34. 取消与超时

### 34.1 Cancel

- 用户可取消 queued、preparing、running、waiting 状态；
- 尽力终止工具与模型请求；
- 保存截至取消时的活动和变更；
- Worktree 有变更时保留；
- 取消不计入连续失败。

### 34.2 Timeout

- 超时包括 Agent 执行时间，不应把无限用户等待计入模型运行时；
- `waiting_user` / `waiting_permission` 可另设最长保留期；
- 超时后保存结果和未完成变更；
- `timed_out` 计入连续失败。

## 35. 重试策略

只有明确的瞬时基础设施错误可自动重试，例如：

- Provider 5xx；
- 短暂网络失败；
- 限流且存在安全退避；
- 临时工具连接失败。

以下不自动重试：

- 已发生不可幂等外部副作用；
- 权限被拒绝；
- 用户输入缺失；
- 测试真实失败；
- 工作区或配置无效。

自动重试发生在同一个 Run 内并记录 attempt；用户点击 Retry 则创建新 Run。

## 36. 连续失败保护

默认规则：

```text
连续失败 3 次
  → 自动暂停 Automation
  → health = needs_attention
  → 系统通知
```

计入连续失败：

- `failed`；
- `timed_out`；
- 可归因于持续配置问题的 `blocked`。

不计入：

- 用户取消；
- overlap skipped；
- missed skipped；
- 用户拒绝权限；
- 用户主动暂停。

成功一次后计数归零。用户可选择：

- `Run now & resume`；
- `Resume without running`；
- `Edit automation`。

---

# 第八篇：通知、Attention 与回流

## 37. Attention-first 模型

事件分三级：

### 37.1 Action required

必须进入 `Needs attention`：

- waiting_permission；
- waiting_user；
- Workspace 丢失；
- 授权过期；
- 能力或身份漂移；
- 连续失败自动暂停；
- 有未处理 Worktree 变更且需要用户决定。

### 37.2 Failed

默认发送系统通知：

- failed；
- timed_out；
- blocked；
- Runtime 或准备阶段异常。

### 37.3 Succeeded

用户可配置是否系统通知。无论是否通知，Run 都进入历史。P0 不承诺智能判断“有意义变化”；P1 再增加 only-on-change。

## 38. 通知矩阵

| 事件 | Center badge | 系统通知默认 | 点击目标 |
|---|---:|---:|---|
| Waiting permission | 是 | 是 | Run Detail 授权区 |
| Waiting user | 是 | 是 | Conversation 对应提问 |
| Failed / Timed out | 是，未读期间 | 是 | Run Detail |
| Blocked | 是 | 是 | Run Detail / Automation Overview |
| Succeeded | 可选未读 | 关 | Run Detail |
| Consecutive failure pause | 是 | 是 | Automation Overview Health |
| Overlap skipped | 否 | 否 | Runs 历史 |
| Missed skipped | 否 | 否 | Runs / 调度审计 |

## 39. 去重与阅读回执

Automation 通知应复用任务通知体系的 `attentionVersion` 与阅读回执语义：

- 同一关注事件只发一次系统通知；
- 用户在任一入口查看后更新统一阅读状态；
- Center badge、菜单栏和系统通知共享事实源；
- 状态持续不变时不重复轰炸；
- 状态从 waiting → running → waiting 形成新请求时递增版本。

## 40. 多入口回流

```text
系统通知
菜单栏
Task Center
Automation Center
Conversation
```

所有入口都必须携带 `automationId + runId`，必要时再携带 `conversationId + attention target`。不存在目标时展示可恢复错误，不回退到无上下文首页。

---

# 第九篇：运行上下文、历史与结果

## 41. Fresh Run

P0 每次触发：

- 创建独立 Run；
- 创建独立 Conversation；
- 从当前 Automation Definition 生成 Prompt 快照；
- 不携带上一 Run 的完整聊天历史；
- 人工跟进不影响下一次 Run。

这保证成本、失败、权限、证据和上下文边界清楚。

## 42. P1：受控历史摘要

P1 可增加：

```text
Start fresh each time
Use previous run summary
```

历史摘要只能包含有界结构化内容，例如：

- 上一次运行时间与状态；
- 上一次结果摘要；
- 已报告问题指纹；
- 上一次基准值；
- 用户明确保存的长期备注。

要求：

- 有大小上限；
- 用户可查看、清除和重建；
- 不直接注入完整 Conversation；
- 摘要版本进入 Run 快照；
- 摘要生成失败不能污染 Automation Definition。

## 43. Run 快照

Run 创建时冻结：

- Automation name；
- Prompt；
- Schedule 与时区；
- Workspace path / ID；
- Git baseline；
- Grant；
- Provider / Model；
- Skill / MCP 可用集合；
- 预算与超时；
- Missed / Overlap 策略；
- Trigger source。

历史页面展示快照，不从当前 Automation 反查覆盖。

## 44. 结果与证据

Run 收据至少包含：

- 最终状态；
- 摘要；
- 错误或阻塞原因；
- 计划和实际时间；
- 工具活动时间线；
- 文件变化与 Diff；
- 验证命令、退出码与摘要；
- Worktree / branch；
- Token、费用和耗时；
- 审批与用户输入事件。

“Agent 声称测试通过”不是证据。验证结果应来自实际工具执行记录。

## 45. 数据保留

P0 产品原则：

- Automation 定义长期保留；
- Run 元数据和最终收据长期保留，直到用户归档策略处理；
- 大型原始日志、流事件和构建产物可按容量策略清理；
- 清理后仍保留摘要、状态、关键证据和清理说明；
- 有未处理变更的 Worktree 不按普通缓存自动清理。

具体天数和容量由实施阶段结合本地存储策略冻结，不在本产品方案中武断指定。

---

# 第十篇：P0 范围、分期与验收

## 46. P0 功能清单

### 46.1 入口与管理

- 全局 `Automations` 一级导航；
- 对话生成 Automation 草稿；
- Center 从零创建；
- 创建、编辑、启用、暂停、恢复、归档；
- `Run now`；
- `Pause all automations`；
- 搜索和基础筛选。

### 46.2 创建与确认

- Name、Prompt、Workspace；
- Once、Hourly、Daily、Weekdays、Weekly、Monthly；
- Advanced Custom cron（分钟级）；
- IANA 时区；
- 未来三次运行预览；
- Observe / Work in workspace；
- 通知配置；
- Run latest / Skip overlap；
- Provider/Model、超时与预算；
- 统一 Review & Confirm。

### 46.3 调度与 Runtime

- 本地持久化调度；
- 应用重启恢复；
- 电脑唤醒恢复；
- 时间与时区变化重算；
- 幂等去重；
- Peer 菜单栏后台常驻；
- 显式退出提醒；
- 全局并发与队列。

### 46.4 Agent 执行

- 每次独立 Fresh Run；
- 每次独立 Conversation；
- Observe 直接读取 Workspace；
- Git 写入 Run 创建隔离 Worktree；
- 取消、超时、基础设施退避重试；
- 同 Automation 不重叠；
- 同 Workspace 写任务串行。

### 46.5 权限与安全

- 独立 Automation Grant；
- Allowed / Will ask / Blocked 摘要；
- `Allow once / Deny`；
- 高风险动作始终阻止；
- Grant 与能力漂移检测；
- Run 权限快照。

### 46.6 结果与通知

- Overview + Runs；
- Run Detail 不可变结果收据；
- 摘要、错误、Diff、验证、活动、费用和耗时；
- Review diff / Open worktree / Apply / Discard；
- Conversation 双向回流；
- Attention-first；
- 失败默认通知、成功可选；
- 连续失败 3 次自动暂停。

## 47. P1 候选

- 更丰富的月度规则与节假日日历；
- Cron 语法辅助、模板与冲突检查；
- `queue_latest`；
- 受控历史摘要；
- only-on-change 成功通知；
- Skill / MCP / 外部系统精细授权；
- 自定义只读/可写目录；
- 授权有效期；
- Workspace 内 Automation 投影；
- Git 分支或 MR 的显式人工交付动作；
- 更丰富的运行统计与费用趋势；
- 非 Git 写入型 Automation 的安全方案。

## 48. 远期探索

- Git、Webhook、文件变化、告警等事件触发；
- Cloud Runner；
- 团队共享 Automation；
- 多设备同步；
- 审批策略与组织治理；
- Workflow / DAG 执行目标；
- 自动创建 MR（仍需独立授权与策略）；
- 基于历史的异常检测和自适应调度。

远期能力不得提前污染 P0 对象和页面，除非是无法后补的持久化主键或安全边界。

## 49. P0 不做清单

```text
✕ 节点画布
✕ 多步骤 DAG
✕ Webhook / Git / 文件事件触发
✕ 云端离线执行
✕ 秒级任务
✕ 永久共用同一个 Conversation
✕ 非 Git 无人值守写入
✕ 自动 push / MR / merge / approve / deploy
✕ 数据库写入
✕ 团队共享和多设备同步
✕ 默认继承 Full Access
✕ 回放全部 missed runs
✕ 同一 Automation 并行执行
```

## 50. 验收主链路

```text
用户从对话发起“每个工作日 9 点检查失败 CI”
  → Peer 生成结构化草稿
  → 用户进入统一创建页
  → 看到 Workspace、时区和未来三次运行
  → 选择 Work in workspace
  → 确认隔离 Worktree 和权限摘要
  → Create & enable
  → Peer 主窗口关闭后仍在后台
  → 到点仅创建一个 Run
  → Run 创建独立 Conversation 与 Worktree
  → Agent 修改代码并运行验证
  → 保存不可变结果收据
  → 系统按策略通知
  → 点击通知进入对应 Run Detail
  → 用户查看 Diff 和验证证据
  → 用户主动 Apply changes 或 Open worktree
```

## 51. 功能验收标准

### 51.1 创建

- 对话和 Center 两种入口生成同一种 Draft；
- 未确认前不会进入 active；
- 确认页完整展示 What / Where / When / Access / Recovery / Notify；
- 下一次三次运行与时区正确；
- 非 Git Workspace 不能选择 P0 Write 模式。

### 51.2 调度

- 同一 `automationId + scheduledAt` 不重复创建 Run；
- 重启后 nextRunAt 正确；
- 唤醒后 `run_latest` 最多补跑一次；
- Pause 期间不补跑；
- 时钟回拨不重复执行；
- Overlap 默认跳过并可审计。

### 51.3 执行

- 主窗口关闭不终止 Run；
- 显式退出后不声称任务仍运行；
- 每个 Run 有独立 Conversation；
- Write Run 不修改原工作副本；
- 有变更的失败/取消 Run 不自动删除 Worktree；
- 取消和超时后保存实际证据。

### 51.4 权限

- 不继承当前会话 Full Access；
- 每个 Run 保存 Grant 快照；
- 未授权操作进入 waiting_permission；
- Allow once 不影响未来 Run；
- 始终阻止动作无绕过路径；
- Grant 变化需要重新确认。

### 51.5 结果

- Automation 修改后旧 Run 仍展示旧快照；
- Run 完成后继续聊天不改写收据；
- Diff 与验证来自实际执行；
- Token、费用和耗时可追踪；
- Retry 创建新 Run 并关联来源。

### 51.6 通知

- 同一 attentionVersion 不重复通知；
- Waiting permission 精确进入授权区；
- Waiting user 精确进入 Conversation；
- 失败进入 Run Detail；
- 连续失败 3 次自动暂停；
- 任一入口阅读后统一消除对应未读状态。

## 52. 异常场景验收矩阵

| 场景 | 期望结果 |
|---|---|
| 到点时电脑休眠 | 不执行；唤醒后按 Run latest 最多补一次 |
| 到点时 Peer 退出 | 不执行；重启后按策略恢复 |
| 主窗口关闭 | Runtime 与当前 Run 继续 |
| 同计划重复调度回调 | 幂等键阻止重复 Run |
| 上次 Run 未完成 | 新计划 skipped_overlap |
| Workspace 被删除 | blocked + Needs attention，不改绑其他目录 |
| Git HEAD 失效 | preparing/blocked，保留原因 |
| Provider 凭证过期 | blocked/auth_expired，可修复后 Retry |
| MCP 身份变化 | 不继承新增能力，要求重审 |
| Agent 请求 push | waiting_permission 或始终阻止；P0 不自动 push |
| 测试失败 | Run failed，保留 Diff 与测试证据 |
| 用户取消有变更 Run | cancelled，保留 Worktree |
| 应用变更发生冲突 | 不覆盖原 Workspace，转人工处理 |
| 连续失败三次 | 自动暂停 + 通知 + 恢复动作 |
| 修改 Automation Prompt | 仅影响新 Run，旧收据不变 |
| 成功通知关闭 | 不发系统通知，但 Run 历史完整 |

## 53. 产品指标

P0 上线后关注：

### 53.1 激活

- 创建完成率；
- 草稿到启用转化率；
- 首个 Automation 成功运行率；
- 从对话创建与 Center 创建占比。

### 53.2 可靠性

- 计划触发成功率；
- 重复 Run 率，目标为 0；
- missed recovery 正确率；
- preflight blocked 分布；
- Runtime 崩溃或孤儿 Run 数量。

### 53.3 价值

- 周活跃 Automation 数；
- 每个 Automation 的有效运行次数；
- Run 结果查看率；
- Diff 应用或 Worktree 打开率；
- 用户主动保留 7/30 天的 Automation 比例。

### 53.4 安全与噪音

- waiting_permission 比例；
- Allow once / Deny 比例；
- 高风险阻止次数；
- 通知点击率；
- 成功通知关闭率；
- 连续失败自动暂停数量。

指标不能以提高执行次数为唯一目标；可靠完成、低噪音和无意外副作用优先。

---

# 第十一篇：文案、可访问性与产品一致性

## 54. 核心术语

| 英文 | 中文产品语义 | 说明 |
|---|---|---|
| Automation | 自动化任务 / Automation | 长期委托定义 |
| Run | 运行 | 一次具体执行实例 |
| Observe | 观察 | 只读执行预设 |
| Work in workspace | 在工作区工作 | Git Worktree 隔离写入预设 |
| Needs attention | 需要处理 | 用户必须查看或行动 |
| Run now | 立即运行 | 不改变未来调度 |
| Pause | 暂停 | 停止未来调度，不取消当前 Run |
| Worktree | 隔离工作副本 | 面向普通用户优先用解释性名称 |

产品内中英文应由 i18n 统一管理，本文示例不是最终本地化文案。

## 55. 避免误导的文案

不要写：

```text
Runs anytime in the background
Runs even when Peer is closed
Full access
Safe fix
```

应写：

```text
Runs locally while Peer is running
Closing the window keeps Peer running; quitting Peer stops automations
Can modify files in an isolated Git worktree and run tests
Publishing, merging, and destructive actions are blocked
```

## 56. 可访问性

- 状态不能只依赖颜色；
- 图标、文本和辅助技术标签同时表达状态；
- Run 时间线可用键盘浏览；
- 确认页的 Allowed / Ask / Blocked 有结构化语义；
- 危险动作不把默认焦点放在确认按钮；
- 下一次运行时间使用完整可读文本；
- 相对时间旁可查看绝对时间和时区。

## 57. 响应式与窗口约束

桌面宽窗口可使用双栏详情；窄窗口必须保持：

- Header 动作不遮挡状态；
- Overview / Runs 页签可达；
- Confirm 摘要顺序不改变；
- Diff 和 Activity 可进入独立视图；
- 不依赖 hover 才能发现关键动作。

---

# 第十二篇：实施前需产出的配套设计

## 58. 必需配套文档

进入代码实施前，建议基于本文继续产出：

1. Automation 领域模型与持久化契约；
2. Scheduler / reconciliation / 幂等 ADR；
3. Automation Grant 与现有 Permission Gate 映射；
4. Worktree 创建、保留、应用和清理 ADR；
5. Run / Conversation / GoalPlan 绑定契约；
6. Runtime 后台常驻、退出和唤醒生命周期设计；
7. Automation Center、创建确认页、Run Detail 高保真交互稿；
8. 通知与 `attentionVersion` 接入规格；
9. 数据保留、迁移与损坏恢复策略；
10. 端到端测试矩阵与故障注入计划。

## 59. 实施顺序建议

```text
1. 领域模型、状态机、持久化与幂等
2. Scheduler + 启动/唤醒 reconciliation
3. Run 创建、Fresh Conversation 与后台 Runner
4. Automation Grant + preflight + waiting permission
5. Git Worktree 执行链与证据收集
6. Automation Center + Create/Edit/Review
7. Overview/Runs + Run Detail
8. 通知、菜单栏、Task Center 与深链回流
9. Pause all、连续失败保护、预算和清理
10. 故障注入与完整验收
```

不能先做漂亮的 Cron 表单，再把调度可靠性、权限和收据留作后补；这些是产品成立的主链路。

---

# 第十三篇：最终冻结摘要

Peer Automation P0 的最小正确产品不是“定时 Prompt”，而是：

```text
双入口创建
+ 结构化时间规则
+ 明示长期授权
+ 本地后台调度
+ Fresh Run
+ Git Worktree 隔离写入
+ 不可变结果收据
+ Attention-first 通知
+ 精确回流与人工接管
```

P0 的核心价值闭环是：

> **用户只需定义重复目标和边界；Peer 在本机可用时按计划执行，在隔离环境中完成可验证工作，并只在真正需要用户时回来。**

任何实现若缺少幂等、权限快照、Worktree 隔离、Run 收据或精确回流，都不应以完整 Automation 功能对外发布。

---

# 第十四篇：对话内自动化任务创建

## 60. 目标与产品承诺

用户不应先理解 Automation Center 的表单结构，才能表达“每天回顾开发进度”“每周检查 CI”这类长期委托。Peer 必须支持从普通对话识别周期性执行意图，并在同一会话中完成信息收集、提案确认和创建回执。

本能力的产品承诺是：

```text
自然语言表达长期委托
  → Peer 识别周期执行意图
  → 缺少关键字段时继续追问
  → 生成结构化自动化任务提案
  → 用户确认
  → 复用 Automation Definition 创建
  → 返回可回流的创建收据
```

它不是关键词触发器，也不是让 Assistant 在 Markdown 中宣称“已创建”。确认前不得写入 Automation Store；创建成功必须来自结构化 Tool Result / IPC Evidence。

## 61. 双入口语义

### 61.1 强入口：从「自动化任务 → 新建」进入

强入口建立显式 `automation_create` 上下文，并跳转到 Chat 新建任务首页。输入框可预填引导模板，但模板只是可编辑的用户草稿；真正的产品语义来自创建上下文。

强入口规则：

- 默认目标就是创建自动化任务，不再重新判断用户是否有创建意图；
- 首轮优先收集“做什么”和“何时运行”；
- 工作区默认绑定当前工作区，时区默认绑定系统时区；
- 信息齐全后必须生成确认提案，不直接创建；
- 用户退出、切换目标或明确取消后，创建上下文结束。

### 61.2 弱入口：普通聊天中的周期任务意图

普通聊天出现明确的长期委托语义时，Peer 可以提出自动化任务建议。识别依据必须同时考虑：

- **动作目标**：需要 Peer 执行的具体工作；
- **重复或未来触发**：每天、每周、定时、周期、到某时执行等；
- **委托意图**：用户希望未来由 Peer 自动执行，而不是讨论如何设计调度功能。

仅出现“每天”“cron”“自动化”等词不能构成创建意图。例如“解释 cron”“设计每日回顾功能”“写一个定时器测试”均不应触发提案。

弱入口规则：

- 高置信度：直接生成可修改的提案卡片；
- 中置信度：先询问“是否要把它创建为自动化任务？”；
- 低置信度：不打断当前任务；
- 用户拒绝后，本轮会话不得反复提示同一提案。

## 62. 单一创建上下文

对话创建过程使用结构化 `AutomationCreateContext`，而不是依赖输入框文本或 Assistant 自述：

```ts
interface AutomationCreateContext {
  source: 'automation_new' | 'conversation_detected';
  conversationId: string | null;
  workspacePath: string;
  timezone: string;
  phase: 'collecting' | 'proposed' | 'creating' | 'created' | 'cancelled' | 'failed';
  proposalId: string | null;
  rejectedFingerprint?: string;
}
```

约束：

- 创建上下文属于会话状态，不属于 Renderer 临时按钮状态；
- `workspacePath` 和 `timezone` 来自当前应用/系统事实，不由模型自由编造；
- Compact Summary 只保持连续性，不能替代提案、确认或创建 Evidence；
- 页面刷新、切页和 Renderer 重挂载不得使 `proposed` 误变成 `created`。

## 63. 结构化提案契约

信息齐全后，运行时生成 `AutomationChatProposal`：

```ts
interface AutomationChatProposal {
  proposalId: string;
  source: 'automation_new' | 'conversation_detected';
  status: 'draft' | 'ready' | 'creating' | 'created' | 'cancelled' | 'failed';
  name: string;
  prompt: string;
  workspacePath: string;
  timezone: string;
  schedule: AutomationSchedule;
  access: 'observe' | 'work_in_workspace';
  timeoutMinutes: number;
  notifySuccess: boolean;
  missingFields: Array<'prompt' | 'schedule'>;
  fingerprint: string;
  createdAutomationId?: string;
  error?: string;
}
```

提案必须作为结构化本地消息段或等价受治理的会话事件持久化。禁止从 Assistant Markdown 反向解析字段。

提案事实来源：

- `prompt`：用户目标与对话澄清结果；
- `schedule`：自然语言理解结果，经用户可见确认；
- `workspacePath`：当前工作区或已有 Automation 的绑定工作区；
- `timezone`：系统 IANA 时区；
- `access`：默认安全预设；
- 其他字段：现有 Automation Definition 默认值与产品规则。

## 64. 状态机

```text
idle
  ├─ 强入口 ─────────────→ collecting
  └─ 弱入口高/中置信度 ─→ collecting / proposed

collecting
  ├─ 缺 prompt ─────────→ ask_task
  ├─ 缺 schedule ───────→ ask_schedule
  ├─ 用户取消 ──────────→ cancelled
  └─ 字段齐全 ──────────→ proposed

proposed
  ├─ 自然语言修改 ──────→ collecting → proposed(new revision)
  ├─ 用户取消 ──────────→ cancelled
  └─ 用户确认 ──────────→ creating

creating
  ├─ create 成功 ───────→ created
  ├─ 可重试失败 ────────→ failed → proposed
  └─ 重复确认 ──────────→ 返回同一创建结果
```

只有 `proposed → creating` 的明确确认动作可以调用 `automationsCreate`。模型文本、页面进入、检测完成、提案渲染均不是确认。

## 65. 聊天内提案卡片

提案卡片是消息流中的原生结构化表达，不是模态大表单。卡片至少显示：

- 自动化任务名称；
- 要执行的工作；
- 运行计划与时区；
- 绑定工作区；
- 权限预设；
- 通知策略；
- 缺失字段或风险提示。

主要动作：

- `确认并创建`：唯一创建入口；
- `修改`：聚焦输入框，允许自然语言修改，例如“改成工作日九点”；
- `取消`：结束当前提案；
- 创建成功后替换为收据，不保留可重复点击的确认按钮。

自然语言修改必须生成新的 proposal revision，并保留同一 `proposalId`；卡片展示最新 revision，旧 revision 不可再确认。

## 66. 确认、幂等与创建收据

确认请求携带：

```text
proposalId + fingerprint + conversationId
```

应用服务必须保证：

- 同一 `proposalId + fingerprint` 最多创建一个 Automation Definition；
- 双击、重试、Renderer 重载不会重复创建；
- 请求中的工作区、时区和权限再次由本地事实校验；
- `automationsCreate` 失败时卡片显示失败状态，不伪造成功；
- 成功后持久化 `createdAutomationId`，后续确认返回同一结果。

创建收据至少包含：

- Automation ID；
- 名称与状态；
- 下一次运行时间；
- 工作区；
- `查看自动化任务` 入口；
- 来源 Conversation ID / Proposal ID。

## 67. 意图识别与模型职责

模型负责认知：理解用户是否表达长期委托、抽取目标与计划、提出必要追问。模型不负责：

- 直接写 Automation Store；
- 决定本地工作区和系统时区事实；
- 绕过权限预设；
- 把自然语言“好的”在无卡片上下文时解释为创建确认；
- 用 Assistant 文本冒充 Tool Result。

P0 可采用本地确定性信号做前置筛选，再调用模型完成语义判断；但最终必须输出结构化提案结果。识别失败不得阻断正常聊天。

## 68. 消息、上下文与能力边界

链路必须遵守：

```text
Automation Intent Context Source
  → Model cognition / structured proposal
    → Renderer proposal card
      → explicit user confirmation
        → existing Automation IPC
          → Automation Definition
            → Evidence-backed receipt
```

规则：

- 强入口上下文通过明确 Context Source 或受治理的会话元数据进入 System Context；
- 普通消息、网页、文件和工具输出不得提升为系统指令；
- 创建动作仍经 Desktop 本地授权、IPC 和 Evidence；
- Renderer 只展示提案并发起结构化动作，不直接访问文件、调度器或 Secret；
- 不新增绕过 Runtime Projection / PermissionGrant / Evidence 的执行路径。

## 69. P0 验收场景

### 69.1 强入口

1. 从「自动化任务 → 新建」进入 Chat 首页；
2. 输入框带可编辑引导模板；
3. 用户说“每天工作日九点检查两个仓库昨天的开发进度”；
4. Peer 生成提案卡片；
5. 确认前 Automation Store 无新增；
6. 确认后只创建一条 Definition，并显示收据。

### 69.2 普通聊天

- “每天回顾 peer_agent 和 peer-knowledge 昨天的开发进度”应产生自动化任务提案；
- “帮我设计一个每日回顾流程”不应自动提案；
- 缺少时间时必须追问，不可默认为任意时间；
- 用户说“不要创建”后不再重复建议；
- 用户说“改成工作日早上九点”时原卡片更新，不创建第二份提案。

### 69.3 可靠性

- 重复点击确认只创建一次；
- IPC 超时或失败时不显示成功；
- 刷新后可恢复提案与收据；
- 成功收据可跳转 Automation Center 详情；
- 所有创建事实均可由 Tool Result / Evidence 追溯。
