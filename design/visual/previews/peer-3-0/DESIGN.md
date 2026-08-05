# Peer 3.0 高保真原型设计说明

> 创建时间：2026-08-03  
> 最后更新：2026-08-03

## 核心定位

Peer 3.0 不是任务管理器，也不是给聊天客户端增加若干 AI 功能。它是一套 Workspace Intelligence / Delegation OS：用户把结果交给 Peer，Peer 在明确边界内持续执行、验证、恢复，并把经过验收的经验沉淀为项目认知与可审查能力。

原型同时呈现三条闭环：

```text
委托闭环：决策 / 权限 / 验收 → Task → Result Package
可信执行：Workflow → Agent Run → Computer Use → Evidence / Checkpoint
长期复利：Result → Memory Candidate → Cognition Review → Skill Patch
```

## 信息架构

### 跨任务层

- **行动**：只显示必须由用户处理的交接点，不重复任务索引。
- **任务**：所有未结束委托的事实索引，展示行动权、GoalPlan、Run、Evidence 与认知影响。
- **项目认知**：Workspace 认知图谱、Memory 和认知变更审查。
- **自动化**：Workflow、触发器、运行实例、Checkpoint、权限与恢复。
- **Skills**：当前挂载能力、作用域、版本、质量趋势和 Skill Patch 审查。

### 单任务层

- **Conversation**：目标、约束和例外沟通。
- **Task Canvas**：项目认知图谱与当前任务有关的切片，投影 Goal、Decision、Knowledge、Agent Run、Automation、Artifact、Evidence 与 Memory Candidate。
- **Run & Evidence**：Explorer、Executor、Verifier 的受控任务树与运行事实。
- **Workbench**：绑定当前任务的 Plan、Browser、Files、Documents 资源工作现场。
- **Computer Use**：观察、操作、断言、恢复和留证。
- **Result Package**：目标对照、交付物、Evidence、风险和学习候选的统一交还。

## 统一对象与真源

原型使用一个演示状态对象连接所有页面。产品落地时，各页面只建立 Read Model，不拥有第二份事实：

- Workspace 是执行环境、认知和能力挂载边界。
- Task 以 Conversation 为当前实现载体。
- GoalPlan / Goal Runner 是执行目标、步骤与进度真源。
- Run / Checkpoint 是 Workflow 与 Agent 执行事实。
- Artifact / Evidence 是结果和完成事实。
- Memory 与 Skill Patch 必须经过独立审查，不能因一次聊天自动写入。

## 关键状态同步

1. 首页批准 Decision 后，行动项减少，Task Canvas Decision 节点同步为已批准。
2. 自动化获得权限后，从 Checkpoint 恢复，对应首页权限项消失。
3. Computer Use 完成断言后生成 Evidence，而不是只展示操作动画。
4. Result Package 被接受后，结果项消失，Memory Candidate 与 Skill Patch Candidate 进入审查。
5. Cognition Review 接受后 Memory 计数增加；Skill Patch 批准后进入可回滚灰度。

## 视觉原则

- Chrome 层（Sidebar、顶部栏、Workbench）使用 Frost 毛玻璃。
- Content 层（任务、图谱节点、Result Package）使用近实色 Paper。
- 中文 H1 使用 Serif，保持至少 30px；正文使用 Sans。
- 主 CTA 使用 Graphite；Azure 只表达运行、选中和轨迹。
- 状态同时使用图标、颜色和文案，不只依赖颜色。
- 页面主体使用连续列表、关系图和工作现场，不做指标卡片墙。
- 圆角保持克制：普通容器 8–12px，不使用胶囊化大卡。

## 原型页面与截图

1. `01-action-inbox.png`：行动收件箱
2. `02-task-index.png`：任务索引
3. `03-project-cognition.png`：项目认知图谱
4. `04-automation.png`：自动化运行与恢复
5. `05-skills.png`：Skills 与 Patch 审查
6. `06-memory.png`：Workspace Memory
7. `07-task-canvas.png`：单任务 Canvas + Workbench
8. `08-computer-use.png`：Computer Use 验证轨迹
9. `09-result-package.png`：Result Package 与学习候选

## 边界说明

- 本原型展示的是 Peer 3.0 产品目标态，不宣称所有后台能力已经落地。
- 当前真实能力包括 Workspace、Conversation、GoalPlan、Evidence 引用和 Workbench 四入口；项目认知、长期 Memory、Workflow 控制面、Skill Patch 与完整 Computer Use 是需要建设的产品层。
- 不新增 Project、父任务、顶层 Goal 或用户手工维护的复杂层级。
- 子 Agent 对用户保持透明但不成为主要产品角色；Peer 对最终结果负责。
