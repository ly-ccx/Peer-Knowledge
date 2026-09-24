# 80. 项目代理委托模型：一个项目一个代理，任务由代理开出

创建时间：2026-09-24
最后更新：2026-09-24

## 状态

Proposed。四项核心产品决策已由用户拍板（2026-09-24，见「决策」1–4），运行时契约待评审后转 Accepted。实现未开工。

## 级别

A 级。改变用户的对话对象、任务的创建者、能力暴露（新增调度能力与 `project_agent` 模式）、权限冒泡路径、System Context 新增来源、会话存储的父子关系。

## 关联

- `design/product/peer-product-alignment.md`（§3、§6、§8 已随本 ADR 修订）
- `design/product/peer-transformation-charter.md`（新增阶段 F）
- `design/product/project-agent-workbench.md`（产品动线与分期）
- `knowledge/architecture/project-agent-delegation-runtime.md`（运行时契约）
- `knowledge/architecture/project-agent-capability-layers.md`（七层模块拆分、并发模型、异常分类、建设顺序 M1–M9）
- `knowledge/decisions/67-task-shell-workbench-radar.md`（本 ADR 部分取代）
- `design/product/task-identity-conversation-carrier.md`（身份层：补父子关系，仍不建 Task 表）
- `design/product/goal-mode-multi-agent-orchestration-plan.md`（任务内 Explorer / Verifier，原样保留）
- `knowledge/decisions/35-mode-scoped-tool-projection.md`（模式在投影层强制）

## 背景

原型 A（ADR 67）把「任务」当成用户的家：用户自己新建任务、在任务里对话、切换任务、到工作台雷达看哪条线要自己处理。实际用下来有三个问题：

1. **用户仍在当项目经理。** 拆成几条任务、哪条先做、哪条卡住了，都要用户自己判断和切换。这和对齐文档「用户负责目标、边界与关键判断，Peer 负责持续推进」相反。
2. **工作台雷达是补丁。** 因为用户分散在多条任务里，才需要一个跨任务页面告诉他「现在谁该动」。入口越多，雷达越重要，界面越像工单台。
3. **多 Agent 能力被埋在单任务里。** Goal Runner 已经能派只读 Explorer、Verifier，但并行推进多件事只能靠用户手动开多个任务。

参照对象是 Grok Bot：一个常驻的总管负责和人交流，按需派专职执行者，只在需要判断时把人拉进来。以及 Grok Build 的子会话模型：`spawn_subagent` 开独立子会话，嵌套深度固定。

## 决策

1. **每个项目（Workspace）有且只有一个项目代理。** 项目代理是一条常驻对话，是用户在该项目里的唯一默认对话对象。不做「总管 + 多个专职代理」的团队结构；专职角色以后做成任务模板，不做成第二个常驻代理。
2. **项目代理只读 + 调度，不产生副作用。** 它可以读文件、搜索、查看任务状态、向用户提问、开任务、给任务追加指令、取消任务、开临时只读调研子 agent。它不能写文件、跑 Shell、调用有副作用的 MCP / 浏览器动作。这个限制在 Runtime Projection 层强制（`project_agent` 模式严格白名单），不靠 prompt。
3. **任务由项目代理开出。** 代理调用 `spawn_session` 开出的子会话就是现有意义上的「任务」：一条 Conversation 载体 + 一份 GoalPlan + 可选任务分支 / worktree，由现有 Goal Runner 推进。验收、关闭闸门、Git 交回全部不变。
4. **用户可以直接进入某条任务介入。** 默认经过项目代理沟通；需要时可以点进任务，在任务里直接发消息。介入走任务自己的对话与 Goal 生命周期，不新开通道。
5. **嵌套深度固定为三层。** 项目代理 → 任务 → 任务内临时子 agent（Explorer / Verifier / 以后的 Implementer）。任务不能再开任务；临时子 agent 不能再开任何东西。项目代理自己开的临时子 agent 只能只读。
6. **仍不建 Project 表或 Task 表。** Workspace 就是项目；项目代理和任务都是 Conversation，用 `role` 和 `parentConversationId` 区分与关联。
7. **四条治理不变量**（详见运行时文档）：
   - 副作用必须先有 GoalPlan：`spawn_session` 必须带目标与成功标准；需要批准的计划照旧要用户批准。
   - 权限只降不升：任务的授权面不超过用户对该项目已授予的范围；任务的权限请求以结构化卡片冒泡到代理对话，由用户批准；代理不能替用户批。
   - 代理的汇报不是证据：代理说「做完了」不关闭任何东西；验收读 GoalPlan 关闭闸门与 Evidence。
   - 代理的对话不是状态真源：任务清单、状态、行动权来自 main 进程的 store 投影，不从代理文本里解析。

## 被取代与保留

| ADR 67 条目 | 本 ADR 之后 |
|---|---|
| 产品面只说任务 | **保留**。项目代理之外，用户看见的执行单位仍叫任务 |
| 主区默认当前任务 | **取代**：主区默认当前项目的项目代理对话 |
| 侧栏工作台常驻计数 + Workspace 下挂任务树 | **取代**：侧栏是项目列表，每个项目带「需要你 / 待验收」角标；任务清单移到项目代理旁的右栏 |
| 工作台不是唯一入口、不是默认落地 | **保留并加强**：跨项目雷达降级为角标与全局收件箱，独立工作台页进入退场评估 |
| 从雷达点进去落回原任务 / 验收对照 | **保留** |
| 点工作区只激活落点 | **改写**：点项目就是打开该项目的代理对话 |
| 轻量问答不进待验收 | **保留**：纯问答由代理直接回答，不开任务 |
| 不做原型 B（工单台） | **保留** |

## 后果

- 用户的日常动作从「开任务、切任务、看雷达」变成「和项目代理说话、处理代理递过来的卡片」。
- 每句话多一跳模型调用，延迟和 token 成本上升；项目代理对话常驻，压缩与项目记忆从可选变成必需。
- 对齐文档里「子 Agent 不当产品主语」收窄为「任务内的临时子 agent 不当产品主语」；项目代理本身成为产品面主语。「不是多 Agent 角色扮演」保留：项目代理是委托层级，不是虚拟团队。
- Agent / Plan 模式切换器从项目代理的输入框退场：是否需要先批准计划，由代理在 `spawn_session` 时按复杂度决定并交给用户批准卡。任务内部仍保留 Plan / Goal 的执行语义。
- 旧会话迁移为该项目下的「历史任务」（`parentConversationId` 为空）。
- 手机与远程入口（路线图中景 #4 / #4b）只需对接项目代理一条对话。

## 不做什么

- 不做多个常驻专职代理、代理之间互相发消息的群聊。
- 不让项目代理拥有任何写能力，哪怕是「很小的改动」。
- 不为项目代理另开执行通道：调度能力同样走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。
- 不把任务报告、代理摘要提升为系统指令。
- 不因为引入项目代理而新建 Task / Project 存储实体。
