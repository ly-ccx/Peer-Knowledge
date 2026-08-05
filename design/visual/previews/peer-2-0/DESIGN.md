# Peer 2.0 高保真原型设计说明

> 创建时间：2026-08-02  
> 最后更新：2026-08-03

## 核心命题

本原型不把 Peer 设计成“更强的聊天框”，而是把一次委托在人和 Peer 之间的行动权迁移做成第一视觉层：

```text
需要你处理 → Peer 正在推进 → 结果待验收
```

## 信息架构

一级导航严格分为三个跨任务页面：

1. **首页**：跨任务行动中心，只回答“现在需要关注什么”。它不是第二份任务数据库，而是 Task、Conversation 与 GoalPlan 状态按下一步行动权形成的动态投影。
2. **任务**：所有未结束任务的索引，支持查看待我处理、Peer 推进中、待验收、已暂停等状态，以及每个任务的 GoalPlan 进度。
3. **历史**：所有终态任务的索引，保留已验收、已归档、已取消和失败记录，并可重新打开结果包或在同一任务中创建新的 Run。

Task Canvas 与 Result Review 不属于一级导航：

- **Task Canvas** 是具体任务的共享认知详情，由任务摘要或任务索引进入。
- **Result Review** 是具体任务的结果验收详情，由待验收任务或历史记录进入。

## 对象与界面职责

- **Task / Conversation**：当前实现中的任务事实与沟通载体。
- **GoalPlan**：目标、步骤、状态和进度的执行事实。
- **Evidence / Artifact**：完成事实与交付结果。
- **首页、任务、历史**：上述事实的读模型，不保存第二份状态。
- **Task Canvas**：投影 Goal、Decision、Agent Run、Artifact、Evidence 与 Step，不成为新状态真源。
- **执行面板**：绑定具体任务的资源工作现场，稳定保留 Plan、Browser、Files、Documents。

因此，具体任务进入 Canvas 或 Result Review 后，右侧执行面板仍然存在；全局集合页在没有选中具体任务时不显示无上下文的完整 Workbench。

## 核心动线

```text
首页行动项 ─┐
任务索引 ───┼→ Task Canvas / Conversation → Peer 推进 → Result Review
历史记录 ───┘                                      │
                                                   ├→ 接受结果 → 历史
                                                   └→ 继续任务 → 同一 Task 的新 Run
```

接受结果会把本轮任务送入历史，而不是无条件返回首页。继续任务不会复制一个新 Task，而是在同一任务事实下继续推进。

## 视觉层级

- **Chrome**：Sidebar、顶部上下文和执行面板使用冷玻璃，表达系统边界。
- **Paper**：任务记录、Goal、Artifact、Evidence 与 Result Package 使用近实色表面，表达可审查对象。
- **Trace**：Azure 只用于行动权、进度和运行轨迹，不承担主 CTA；主操作保持 Graphite。
- **集合页**：采用连续任务表和历史列表，不做卡片墙或指标墙。
- **详情页**：Canvas / Review 与右侧执行面板并列，明确任务认知与资源工作现场的分工。

## 当前真实底座与目标态边界

- 当前真实底座：Workspace、Conversation、GoalPlan、Evidence 引用，以及 Workbench 的 Plan / Browser / Files / Documents。
- 2.0 目标态：Task Canvas 统一投影 Goal、Decision、Agent Run、Artifact、Evidence 与 Step。
- Canvas 不建立第二套存储；所有节点都应来自既有协议对象、运行事件或可追溯衍生状态。
- 原型中的跨任务数据是高保真示例，不宣称当前已经具备无限 Workspace 的全局聚合 API。

## 反目标

- 不做仪表盘卡片墙。
- 不把 Task Canvas 或 Result Review 放入一级导航。
- 不用单个“当前任务”代表多个活跃任务。
- 不做自由白板或手工 Workflow 编辑器。
- 不创建顶层“发起 Goal”。
- 不创建父 Task / Project / 里程碑层级。
- 不让 Canvas 或验收面板取代现有 Workbench。
- 不展示 Agent 思维链、工具 JSON 或无意义忙碌动画。
