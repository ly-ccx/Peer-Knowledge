# Peer 2.0 产品体系说明书

> 创建时间：2026-08-01  
> 最后更新：2026-08-22（当前改造镜头见总纲 v2；本文仍是更早的 2.0 战略总纲）  
> 文档状态：2.0 产品总纲 / 战略与实施基线  
> 适用范围：Peer Desktop、CLI/TUI、Local Runtime、Cloud Runtime 与后续协作能力  
> 关联代码仓：`peer_agent`  
> 当前改造总纲：`design/product/peer-transformation-charter.md`  
> 壳层决策：`knowledge/decisions/67-task-shell-workbench-radar.md`

---

## 0. 文档目的与阅读约定

这不是一份功能愿望清单，也不是把 Agent、Canvas、Memory、Computer Use 等热门概念拼在一起的路线图。它要回答五个更根本的问题：

1. Peer 为什么应该存在，它替用户承担的到底是哪一种责任？
2. 在模型能力快速趋同、Agent 产品愈加拥挤的市场里，Peer 占据什么独特位置？
3. Workspace、Task、Conversation、GoalPlan、Workflow、Workbench、Canvas、Evidence、Memory 与 Skill 如何组成一个一致的产品，而不是九个互不相干的功能？
4. 当前产品已经具备什么，2.0 必须建设什么，哪些只能作为远期探索？
5. 如何把愿景落实成可验证的实施顺序、增长飞轮和商业结果？

### 0.1 能力状态标记

全文使用三种明确标记，防止愿景冒充现状：

- **【当前已实现】**：代码仓已有主链路或可实际使用的能力。
- **【2.0 建设项】**：Peer 2.0 为完成核心闭环必须落地的能力。
- **【远期探索】**：建立在 2.0 可靠性和用户验证之上的扩展方向，不进入近期承诺。

“已有设计文档”不等于“当前已实现”；“底层接口存在”也不等于“产品闭环已完成”。

### 0.2 核心结论

Peer 2.0 的品类定义是：

> **一个以 Workspace 为执行边界、以任务委托为基本单位、以 GoalPlan 与 Workflow 持续推进、以 Evidence 验收结果、并通过可治理记忆与 Skill 进化形成长期复利的本地工作委托系统。**

面向用户的表达是：

> **把工作交给 Peer，只在真正需要你的时候回来。**

Peer 的核心不是“替用户点击更多按钮”，而是建立一种新的工作关系：

> **用户负责目标、边界与关键判断；Peer 负责让工作持续向前，并在交还之前证明结果。**

---

# 第一篇：产品理念与独特定位

## 1. 从“使用 AI”到“托付工作”

### 1.1 当前 Agent 产品的共同问题

今天绝大多数 AI 产品仍然建立在“人推动每一轮”的交互范式上：

```text
用户提出要求
  → AI 回答或执行一段操作
  → 用户阅读结果
  → 用户判断遗漏
  → 用户发送下一条指令
  → 再次等待
```

即使产品已经能够读写文件、运行命令或调用浏览器，用户仍然承担着隐性的项目经理职责：

- 把复杂目标拆成下一条 Prompt；
- 记住任务做到哪里；
- 在多个会话之间切换；
- 判断 Agent 是否遗漏；
- 发现 Agent 只是“声称完成”；
- 在中断后重新解释上下文；
- 把有效经验人工搬到下一次任务。

这不是完整的委托，而是“用户借助 AI 亲自完成工作”。AI 提升了局部操作效率，却没有接管工作连续性和结果责任。

### 1.2 Peer 要完成的范式迁移

Peer 2.0 的基本单位不是一条消息、一次工具调用或一张待办卡，而是：

> **一段可以被托付、持续推进、暂停恢复、关键交接并最终验收的真实工作。**

它的标准闭环是：

```text
委托 Delegation
  → 对齐 Alignment
  → 计划 Plan
  → 执行 Execution
  → 验证 Verification
  → 交接 Handoff
  → 验收 Acceptance
  → 沉淀 Learning
```

这条闭环中，聊天只是表达意图和处理例外的沟通介质，不再是工作状态的唯一载体。

### 1.3 Peer 的责任边界

Peer 不承诺替用户决定一切。它承诺的是：

1. **不丢失目标**：跨轮次、跨压缩、跨重启仍知道任务为何存在。
2. **不虚报完成**：没有实际执行和证据，不把推测写成事实。
3. **不把微观调度甩回用户**：能自行推进的步骤持续推进。
4. **只在高价值节点打扰**：关键决策、权限、异常与验收才交还。
5. **不偷偷扩大权限**：学习工作方式不等于获得更多权力。
6. **不隐藏不确定性**：失败、阻塞、未验证项和成本均可见。
7. **结果可以被接手**：用户或其他 Agent 能从状态、产物和 Evidence 继续工作。

因此，Peer 不是“完全自治”的神话，而是“可被长期托付”的工程系统。

## 2. 市场定位：Delegation OS

### 2.1 Peer 不是什么

Peer 不应被定位为：

- 又一个 ChatGPT 桌面客户端；
- 单纯的 Coding Agent；
- 多模型聚合器；
- MCP 工具商店；
- 多 Agent 角色扮演平台；
- AI 版 Jira、Linear 或 Notion；
- 通用 RPA；
- 以无限白板为中心的协作工具。

这些品类要么容易被基础模型平台吞并，要么不能表达 Peer 的真正价值。

### 2.2 Peer 占据的独特层

Agent 市场可以分为五层：

| 层级 | 提供者 | 核心价值 |
|---|---|---|
| 智力层 | 基础模型 | 理解、推理、生成 |
| 工具层 | MCP、API、Shell、Browser | 对外部世界采取动作 |
| 执行层 | Coding Agent、Automation | 完成局部操作 |
| 管理层 | Task / Project 工具 | 记录和分配工作 |
| **关系与治理层** | **Peer** | **承载长期委托、人机交接、验证、恢复和经验复利** |

Peer 的机会不在于拥有不可替代的模型，而在于成为模型与用户之间的**长期工作关系层**。模型、工具和执行器可以替换，但下列资产持续留在 Peer：

- 用户托付过的任务及其状态；
- Workspace 的事实、规则和工作现场；
- 已验证的 GoalPlan、Workflow 与 Evidence；
- 人机交接历史和权限决策；
- 被证明有效的程序性记忆与 Skill 版本；
- 用户对重要工作的信任记录。

### 2.3 与相邻品类的根本差异

#### 相对通用聊天 AI

通用 AI 的基本单位是“回答”；Peer 的基本单位是“可验收的委托”。前者依赖用户持续发起下一轮，后者负责维护下一步行动。

#### 相对 Coding Agent

Coding Agent 通常围绕一个代码 Session 优化；Peer 围绕跨代码、文档、浏览器、发布和决策的完整工作生命周期优化。代码是重要场景，但不是产品边界。

#### 相对项目管理工具

项目管理工具记录“谁应该做什么”，状态通常由人维护；Peer 本身是执行主体之一，状态由真实运行、验证与 Evidence 驱动，而非手工拖卡。

#### 相对多 Agent 平台

多 Agent 平台强调创建多少 Agent、如何编排角色；Peer 对用户只呈现一个对结果负责的协作者。子 Agent 是内部执行组织，不是用户需要管理的虚拟团队。

#### 相对自动化/RPA

RPA 重复确定流程；Peer 面向不完全确定的知识工作。它需要规划、判断、验证和人机交接，同时把稳定部分逐渐沉淀为 Workflow 与 Skill。

### 2.4 战略护城河

Peer 的壁垒由四层共同构成：

1. **信任壁垒**：完成必须有 Evidence，未知必须明确，风险必须受治理。
2. **连续性壁垒**：长任务可恢复，多个任务可并行，状态不依赖聊天窗口存活。
3. **上下文壁垒**：Workspace 中积累的是可追溯的工作事实，而非无边界聊天向量。
4. **程序性壁垒**：成功方法转化为可版本化 Skill，下一次更快、更准、更少打扰。

健康粘性不是“数据锁死”，而是：

> 用户随时可以导出和离开，但重新培养另一位协作者的机会成本越来越高。

## 3. 目标用户与切入市场

### 3.1 第一目标用户

2.0 不服务“所有需要 AI 的人”，而优先服务：

> **同时维护多个本地 Workspace、每天推进代码、文档、研究和发布工作的独立开发者、技术负责人和技术型创作者。**

他们通常具有以下特征：

- 同时推进 5—30 个长短不一的任务；
- 工作跨越终端、代码仓、浏览器、文档与桌面应用；
- 已经高频使用一个或多个 Agent；
- 对自动化有需求，但对误操作和幻觉敏感；
- 重视本地数据、权限和可控性；
- 经常跨天恢复任务；
- 愿意为可靠节省时间付费，而不是只为更多 Token 付费。

### 3.2 首批高价值场景

Peer 应优先打透四类可验证委托：

1. **问题定位与修复**：调查根因、修改、测试、真实环境验证、交付证据。
2. **跨文件工程改造**：规划依赖、分步实施、处理回归、恢复中断。
3. **发布与运维准备**：运行检查、识别阻塞、请求关键确认、生成发布证据。
4. **研究与文档交付**：收集资料、交叉验证、形成结构化文档和引用依据。

它们共同具备：价值明确、步骤较长、需要工具、可定义完成标准、适合沉淀经验。

### 3.3 暂不优先的用户

- 只需要轻量问答的普通用户；
- 追求完全无人监管高风险自动交易的人；
- 只按固定表单重复操作、无需推理的纯 RPA 用户；
- 以企业复杂审批和团队排期为第一诉求的大型组织。

这些方向并非永不进入，而是不应稀释 2.0 的产品焦点。

## 4. 产品价值主张

### 4.1 对用户的直接价值

Peer 2.0 要让用户感受到五个变化：

1. **少解释**：Workspace 已理解项目结构、规则和验证方式。
2. **少盯守**：Peer 能持续推进，只有例外才回来找人。
3. **少切换**：首页直接告诉用户哪里需要行动，不用逐个翻会话。
4. **少怀疑**：完成有测试、截图、日志、文件或其他 Evidence。
5. **越用越顺**：经验证的经验转化为记忆和 Skill，而不是每次从零开始。

### 4.2 最重要的产品变量：行动权

传统任务系统围绕“待办、进行中、完成”组织；Peer 应围绕“下一步行动权在谁手里”组织：

```text
轮到用户：待审批 / 待确认 / 待补充 / 待验收
轮到 Peer：规划中 / 执行中 / 验证中 / 自动修复中
一轮结束：已验收 / 已归档 / 已取消 / 失败终止
```

“进行中”没有告诉用户是否需要介入；“Peer 正在推进”明确表示用户可以离开。“已完成”可能只是机器声明；“结果待验收”明确说明工作已经交回。

### 4.3 产品原则

1. **目标优先于消息**：消息是过程，目标和完成标准是主语。
2. **交接优先于状态**：任何状态都应回答下一步由谁行动。
3. **证据优先于声明**：没有验证的结果不能进入可信完成。
4. **例外打扰优先于过程打扰**：默认不要求用户微观管理。
5. **真实对象优先于展示副本**：Canvas 和首页只是投影，不拥有第二份执行真相。
6. **恢复优先于并行炫技**：先保证一个长任务可靠续接，再扩大并发。
7. **治理优先于自治口号**：权限、成本、数据和进化必须可见、可撤销。
8. **复利优先于功能数量**：每个完成任务都应让下一次委托更容易。

# 第二篇：产品对象模型与核心动线

## 5. 统一对象模型

Peer 2.0 的复杂度不应通过添加更多顶层实体解决。对象越多，用户越需要学习系统内部概念。正确方式是让每个对象回答一个不可替代的问题，并明确唯一数据真源。

### 5.1 对象总览

| 对象 | 回答的问题 | 用户心智 | 数据真源 |
|---|---|---|---|
| Workspace | 工作发生在哪里、受什么规则约束？ | 工作环境 | Workspace 配置、文件系统与能力挂载 |
| Task | 用户托付的工作是什么？ | 一项持续委托 | 当前由 Conversation 承载的任务身份 |
| Conversation | 双方说了什么、为何改变方向？ | 沟通线程 | 消息与上下文历史 |
| Goal | 最终要达到什么结果？ | 目标 | GoalPlan.goal / 目标契约 |
| Plan | 准备通过哪些步骤完成？ | 执行路径 | GoalPlan.tasks 与依赖 |
| Run / Workflow | 这一次具体如何运行？ | 运行实例 | Runner、Run Trace、Checkpoint |
| Evidence | 什么证明一步或结果已经发生？ | 事实凭证 | Evidence artifact 与验证结果 |
| Artifact | 产生了哪些可消费结果？ | 交付物 | 文件、文档、截图、报告、浏览会话 |
| Decision | 哪个关键判断由人做出？ | 交接记录 | 用户确认、审批和选择 |
| Memory | 哪些事实与偏好值得跨任务保留？ | 已确认经验 | 可追溯记忆条目 |
| Skill | 这类事情以后应该怎样做？ | 可复用工作方法 | 版本化 Skill 包与运行记录 |
| Canvas | 如何共同理解复杂任务？ | 共享任务现场 | 对上述对象的引用、布局和批注 |

### 5.2 Workspace：执行世界，而非文件夹标签

Workspace 决定：

- 文件、代码仓和工作目录；
- 项目级指令、架构规则和 source of truth；
- 可挂载的本地 Skill、Plugin、MCP 与命令；
- 权限、凭据和敏感数据边界；
- Browser、Files、Documents 等 Workbench 资源上下文；
- 任务记忆的隔离范围；
- 新建任务默认落点。

因此切换 Workspace 不是普通筛选，而是切换执行世界。跨 Workspace 总览可以存在，但真正执行前必须明确目标 Workspace；涉及两个 Workspace 的任务必须显式记录 `originWorkspacePath` 与 `targetWorkspacePath`，而不是默默在错误目录行动。

**【当前已实现】** Workspace 切换、Workspace 内 Conversation 列表、跨 Workspace 运行可见性、GoalPlan 的 origin/target workspace 字段、Workspace Skill 挂载基础。  
**【2.0 建设项】** Workspace 记忆、权限策略、任务总览投影、健康度与能力清单。  
**【远期探索】** 多 Workspace 原子事务与跨环境协作图。

### 5.3 Task 与 Conversation：产品正名而非新增父层

当前“新建任务”创建的是 Conversation。2.0 不再虚构 Project → Task → Conversation 的三级结构，而采用：

> **一个 Conversation 就是一项 Task 的持续沟通与执行载体。**

Task 是用户心智，Conversation 是实现载体。Task 除消息外还投影：

- 所属 Workspace；
- 当前 Goal 与 Plan；
- Peer / 用户的行动权；
- 运行、压缩、等待、失败和完成状态；
- Artifact 与 Evidence；
- 相关 Memory 与 Skill；
- 最后更新时间和未读结果。

只有在真实团队协作和组合目标得到验证后，才评估 Project 或 Portfolio；2.0 不用新层级掩盖任务扫描问题。

### 5.4 Goal、Plan 与 Run：不要压成一张进度卡

- **Goal** 描述结果、边界和成功标准，原则上稳定。
- **Plan** 描述当前已知路径，可以随新事实调整。
- **Run** 记录一次实际执行，包括工具调用、子 Agent、重试、自我修复和 Checkpoint。

同一 Goal 可以经历多个 Run；一次 Run 失败不等于 Goal 失败。Plan 变化必须可解释，不能覆盖历史。进度必须由叶子步骤聚合，不能让模型手填百分比。

### 5.5 Evidence 与 Artifact：事实和交付物必须分开

Artifact 是用户可以消费的结果，例如文件、页面、报告、截图；Evidence 是证明某个声明成立的依据，例如测试通过日志、文件哈希、浏览器断言或用户确认。

一份截图可以同时是 Artifact 和 Evidence，但语义不同。系统不能因为“生成了文件”就判定“目标完成”，也不能因为“测试通过”就假设产品方向正确。

### 5.6 Memory 与 Skill：知道什么，与会做什么

- Memory 保存事实、决策、偏好、教训及来源。
- Skill 保存可复用的执行程序、工具选择、验证方式和回退策略。

Memory 为本次工作提供上下文；Skill 把上下文转化为行动方法。两者都不能直接拥有权限，也不能绕过 Workflow 和 Evidence。

### 5.7 Canvas：投影真实对象，不成为第二份真相

Canvas 保存：

- 对 Goal、Step、Decision、Agent Run、Artifact、Evidence 的引用；
- 空间布局、批注、比较关系和视图状态；
- 用户在共享现场中做出的选择。

Canvas 不复制 GoalPlan 状态，不手工维护完成率，不自己发明 Workflow。任何执行状态改变来自底层对象；用户在 Canvas 上的审批、重试或取消则通过正式命令驱动底层运行。

## 6. 核心委托闭环

### 6.1 阶段一：委托与对齐

用户通过自然语言、文件、截图、链接或已有任务表达目标。Peer 需要提取：

- 期望结果；
- Workspace 与作用范围；
- 不可越过的边界；
- 已知约束和 source of truth；
- 成功标准；
- 风险与需要用户决定的事项。

简单任务直接执行；中等任务生成 micro-plan；复杂任务创建持久 GoalPlan；高风险任务先审批。规划深度应由任务风险和不确定性决定，而不是由用户理解内部模式。

### 6.2 阶段二：计划与准入

Peer 根据 Workspace Memory 和适用 Skill 形成 Plan，并明确：

- 每个步骤的产出；
- 依赖与可并行部分；
- 哪些交给 Explorer、Executor 或 Verifier；
- 每步的权限与预算；
- 自动检查和人工验收条件；
- 失败后的恢复路径。

用户不需要审批每个 Plan。只有高风险动作、关键产品判断、成本超阈值或权限扩大需要准入。

### 6.3 阶段三：持续执行

Workflow 驱动主 Peer：

1. 获取下一可执行步骤；
2. 读取必要上下文与 Memory；
3. 调用 Skill、工具或有边界子 Agent；
4. 写入 Run Trace 与 Checkpoint；
5. 产生 Artifact 和 Evidence；
6. 更新 Plan 的权威状态；
7. 满足条件则继续，否则进入修复、等待或交接。

用户关闭窗口、切换 Workspace、网络短暂中断或上下文压缩不应结束 Goal。

### 6.4 阶段四：例外交接

只有以下情况将行动权交回用户：

- 需求存在实质性歧义；
- 多个方案涉及产品或商业取舍；
- 需要新增权限、凭据或费用；
- 操作不可逆或高风险；
- 自动验证与目标冲突；
- 达到验收节点。

交接卡必须包含：发生了什么、Peer 已尝试什么、需要用户决定什么、选项影响、默认建议和不行动后果。禁止只问“怎么办”。

### 6.5 阶段五：验证与自动修复

完成声明前执行多层验证：

```text
静态检查 / Test / Build
  → API 或状态断言
  → Browser / Desktop Computer Use
  → 独立 Verifier（按风险启用）
  → 产品性人工验收（必要时）
```

失败不直接结束任务，而是形成诊断 → 修复 → 再验证循环；循环受次数、成本和风险预算约束。

### 6.6 阶段六：交付与验收

Peer 交付的不是一句摘要，而是一个 Result Package：

- 目标与最终结论；
- 完成和未完成范围；
- 关键变更；
- 可打开的 Artifact；
- 支撑结论的 Evidence；
- 剩余风险；
- 建议的下一步：接受、继续、回退、归档。

用户验收后，任务进入已接受；若提出新要求，系统判断是同一 Goal 的修订、新 Run，还是新的 Task。

### 6.7 阶段七：学习与沉淀

任务结束后生成候选 Memory 和 Skill Patch，但不静默生效。系统解释：

- 学到了什么；
- 来源于哪些 Evidence 和用户决策；
- 适用范围；
- 与旧规则是否冲突；
- 建议保存、修改、仅本次使用或拒绝。

## 7. 产品界面体系

### 7.1 首页：跨任务交接台

首页不是数据仪表盘，也不是会话表换皮。它首先回答：

1. 现在轮到我处理什么？
2. Peer 正在替我推进什么？
3. 哪些结果已经到达，等待验收？

主结构：

```text
需要你处理
  - 审批计划
  - 确认高风险操作
  - 补充信息
  - 查看失败

Peer 正在推进
  - 当前 Goal 和步骤
  - 进度与最近 Evidence
  - 是否阻塞、预计下一交接点

结果已到达
  - Result Package
  - 验证状态
  - 查看 / 继续 / 归档

所有任务
  - 搜索、置顶、Workspace 筛选、归档
```

首页状态不是手工看板列，而是由 Conversation、GoalPlan、Runner、确认请求和未读结果派生。

### 7.2 Conversation：意图与例外沟通

Conversation 负责：

- 委托目标；
- 澄清与纠偏；
- 解释关键判断；
- 接收人机交接；
- 形成最终自然语言总结。

聊天流不堆叠完整工具 JSON、每步进度日志和子 Agent 噪音。持续状态进入 Goal/Canvas，资源进入 Workbench，证据进入 Result Package。

### 7.3 Workbench：具体资源工作现场

Workbench 是单个任务的资源操作面：

- **Plan**：Goal、Plan、当前步骤、Runner 和控制；
- **Browser**：内嵌网页与 Computer Use 会话；
- **Files**：Workspace 文件树和定位；
- **Documents**：文件预览、源码、Diff、报告与 Evidence。

Workbench 不是首页，也不承担跨任务管理。它与当前 Conversation 绑定，并恢复会话级资源状态。

### 7.4 Task Canvas：共享认知与复杂任务操控面

Canvas 适用于包含多方案、多 Agent、多 Artifact 或多个决策点的复杂任务。它支持：

- 将输入自动整理为 Goal、约束、未知项和成功标准；
- 显示 Workflow 的关键分支，而非全部底层调用；
- 并排比较方案、截图、文件和证据；
- 在决策节点直接批准、选择、批注或打回；
- 查看谁在行动、哪里阻塞、哪些结果已验证；
- 任务结束后提炼 Memory 与 Skill Patch。

Canvas 的价值不是自由拖拽，而是将聊天中隐含的共识、分歧和验证显性化。

### 7.5 CLI/TUI：同一状态源的紧凑客户端

CLI/TUI 不复制桌面信息架构。它复用同一 Goal、Run、Evidence 和交接状态，但以紧凑状态行、命令、临时 Picker 和可折叠 Goal 区呈现。用户从 Desktop 切到 CLI，任务身份与运行状态不改变。

## 8. 一条完整产品动线示例

用户提出：“重构 Peer 的任务工作台，并确认在真实桌面端可用。”

```text
1. Peer 识别目标 Workspace 和现有产品事实
2. Explorer 并行调查 Sidebar、GoalPlan、Workbench 与 Token
3. Canvas 整理产品目标、对象关系、方案和验收标准
4. 用户只确认关键产品方向
5. Peer 创建 GoalPlan，拆成设计、实现、测试、真实应用验收
6. Executor 修改代码，Workflow 持续记录 Checkpoint
7. Test / Typecheck / Build 先验证工程正确性
8. Computer Use 启动 Electron，切 Workspace、搜索任务、审批 Plan
9. Verifier 独立检查动线、布局和 Evidence
10. 首页将任务从“Peer 正在推进”移动到“结果待验收”
11. 用户查看 Result Package 并接受
12. 系统建议保存 UI 验收 Skill Patch 与 Workspace 设计规则
```

这条动线中，用户面对始终是一个 Peer；子 Agent、Workflow 和 Computer Use 是内部能力，而不是需要用户编排的产品负担。

# 第三篇：核心能力体系

## 9. 可信执行内核

### 9.1 Verification Contract

任何复杂委托开始前，都应形成可执行的完成定义：

- 哪些结果必须存在；
- 哪些命令或测试必须通过；
- 哪些界面行为需要真实操作验证；
- 哪些属于产品判断，必须人工确认；
- 哪些风险允许保留；
- 哪种 Evidence 足以支撑完成。

成功标准分为：

| 类型 | 示例 | 判定者 |
|---|---|---|
| 文件事实 | 文件存在、包含指定内容 | 系统检查 |
| 工程事实 | Test / Build / Typecheck 通过 | 命令结果 |
| 状态事实 | API 返回、数据库状态变化 | 集成断言 |
| 界面事实 | 点击后进入正确状态、无溢出 | Computer Use |
| 产品事实 | 信息架构是否符合目标 | 用户 / Reviewer |

Goal 只有在所有自动标准有 Evidence、人工标准得到确认后，才允许进入可信完成。

### 9.2 Evidence Gate

Evidence Gate 是 Peer 与普通 Agent 的关键差异：

- 子任务标记完成时必须绑定 Evidence；
- Evidence 必须可定位到真实工具结果或 Artifact；
- Evidence 有类型、来源、时间、Workspace、敏感级别和保留策略；
- 过期或环境变化可使 Evidence 失效；
- Verifier 可以推翻 Executor 的完成声明；
- Renderer 只投影状态，不得自行构造“通过”。

### 9.3 诊断—修复—再验证循环

当验证失败时，系统不应表面补丁式重试。它先生成 Diagnosis：

1. 将问题改写成系统层症状；
2. 列出平台、产品和工程约束；
3. 提出主要根因假设与证伪方式；
4. 确认 source of truth；
5. 找到需要改变的因果链节点；
6. 定义复验方式；
7. 列出不做的症状疗法。

连续两次相同表面修复无进展时，自动提升规划深度或交由用户，而不是继续消耗。

## 10. Workflow：工作的运行骨架

### 10.1 Workflow 的职责

Workflow 负责把 GoalPlan 变成可恢复执行：

- DAG 步骤与依赖；
- 串行、并行和条件分支；
- 输入输出契约；
- Checkpoint、重试、回退和补偿；
- 人工审批与权限门；
- 时间、Token、费用和并发预算；
- 子 Agent 调度；
- 每步验证要求；
- 暂停、继续、取消与超时；
- 版本与运行历史。

### 10.2 Skill、Workflow、GoalPlan 的关系

```text
Skill：某类工作通常怎样做
  ↓ 结合 Workspace、Memory 与本次目标实例化
Workflow Template：多个能力如何协作
  ↓ 生成本次任务的具体路径
GoalPlan：本次委托的目标、步骤、状态与完成标准
  ↓ 实际执行
Run：工具调用、Agent 活动、Checkpoint 与 Evidence
```

Skill 可以由多个 Workflow 片段组成；GoalPlan 也可以在运行中动态生成局部 Plan，但动态计划必须挂在触发节点下，不创建失控的顶层 Goal。

### 10.3 可恢复性是第一优先级

完整 Workflow 的最低承诺：

- App 重启后知道下一步；
- Context Compaction 不结束 Goal；
- 网络或 Provider 失败后从 Checkpoint 恢复；
- 已完成且有 Evidence 的步骤不会重复执行；
- 外部副作用具有幂等键或补偿策略；
- 用户纠偏绑定当前 Goal，并进入 Run Trace；
- 状态由 Plan 与 Checkpoint 共同恢复，而非让模型凭摘要猜测。

## 11. 子 Agent：内部执行组织

### 11.1 单一责任主体

用户面对的是一个 Peer。主 Peer 对目标、权限、成本、状态与最终结果负责。子 Agent 不能各自与用户争夺注意力，也不能并发写入同一权威状态。

### 11.2 首批角色

#### Explorer

- 严格只读；
- 调查代码、配置、文档和历史事实；
- 输出结构化发现与 Evidence；
- 不执行副作用，不修改 Goal 状态。

#### Executor

- 在明确 Workspace 和写权限下执行一个边界清晰的子任务；
- 只能使用投影给它的工具；
- 返回 Artifact、Evidence 和未解决问题；
- 不擅自扩张任务范围。

#### Verifier

- 独立对照成功标准复核；
- 尽量不继承 Executor 的自我解释；
- 可运行测试、读取产物和操作真实界面；
- 只能通过、打回或指出证据不足，不能替 Executor 静默改结果。

### 11.3 子 Agent 委托契约

每次派发必须包含：

```text
目标与非目标
Workspace 与路径范围
只读 / 可写权限
允许工具
输入 Artifact
输出格式
Evidence 要求
时间与成本预算
是否可派生下级 Agent
取消和超时规则
```

### 11.4 并行原则

只并行互不争用状态且能真正缩短关键路径的任务。以下情况不并行：

- 多个 Agent 修改同一文件区域；
- 后续任务依赖尚未稳定的设计决定；
- 并行产生的上下文合并成本高于收益；
- 风险需要单一责任链。

多 Agent 的衡量标准不是数量，而是总完成时间、冲突率、Evidence 质量和用户干预次数。

## 12. Computer Use：真实环境验证能力

### 12.1 产品定位

Computer Use 不是演示“AI 会点鼠标”，而是让 Peer 在交付前亲自观察真实结果。它与 Test、API 验证互补：

- 代码检查证明实现结构；
- 状态断言证明系统变化；
- Computer Use 证明用户真实可见的流程；
- 人工判断证明产品方向。

### 12.2 能力阶梯

#### L1 内嵌 Browser【当前已实现基础】

- 操作 Workbench 中用户可见的 Webview；
- 导航、点击、输入、截图和 DOM 读取；
- 与 Conversation、Workspace 和 BrowserSession 绑定；
- 适合本地页面、Web 产品和登录后网页验证。

#### L2 受控外部浏览器【2.0 建设项】

- Playwright/CDP 管理的 Chrome/Chromium；
- 用户明确授权的 Profile 和 Session；
- 多页面、下载、权限弹窗、网络日志和自动断言；
- 与内嵌 Browser 共享 Observation / Action / Evidence 协议。

#### L3 操作系统 UI【远期探索】

- macOS Accessibility、ScreenCapture 与键鼠注入；
- 原生窗口、菜单、文件选择器和桌面应用；
- 高风险授权、敏感区域遮蔽、动作预览与紧急停止。

### 12.3 完整验证闭环

Computer Use 需要六类能力：观察、操作、同步、断言、恢复、留证。定位优先使用 DOM/Accessibility 等语义信息，坐标仅作降级；失败后重新观察，而不是盲点重试。

### 12.4 风险治理

- 付款、发布、删除、发送、权限变更默认确认；
- 凭据只通过安全填充，不进入模型文本；
- 截图和 DOM 按敏感级别存储；
- 用户随时可暂停和接管；
- 每个动作标记执行主体、目标应用和 Evidence；
- Computer Use 不得绕过 Local Tool Host 与 PermissionGrant。

## 13. 记忆体系：可追溯的工作认知

### 13.1 四层记忆

#### 任务工作记忆

Goal、Plan、Checkpoint、当前阻塞、下一步和近期协议现场，服务当前任务恢复。

#### Workspace 事实记忆

项目结构、命令、架构决策、source of truth、风险规则和验证方法，严格按 Workspace 隔离。

#### 用户协作记忆

语言、交付粒度、常用偏好和重复确认的协作习惯。权限、费用和敏感数据策略不能通过隐式学习扩大。

#### 程序性记忆

被成功验证的工作路径，例如“renderer UI 修改后运行哪些检查并如何截图验证”。它是 Skill 进化的主要输入。

### 13.2 记忆不是聊天向量库

聊天历史可以用于检索上下文，但不能自动晋升为可信记忆。候选记忆必须具有：

```ts
type MemoryItem = {
  kind: 'fact' | 'decision' | 'preference' | 'procedure' | 'lesson'
  scope: 'task' | 'workspace' | 'user'
  statement: string
  sourceRefs: string[]
  evidenceRefs: string[]
  confidence: number
  status: 'candidate' | 'active' | 'stale' | 'revoked'
  validFrom: string
  lastValidatedAt: string
  supersedes?: string[]
}
```

### 13.3 记忆晋升链

```text
任务过程
  → 候选经验
  → 绑定 Evidence
  → 分类与作用域判断
  → 冲突和敏感性检查
  → 用户确认或满足保守自动规则
  → 激活
  → 下一任务调用
  → 观察效果
  → 强化、修订、过期或撤销
```

记忆系统必须同时具备遗忘、过期、来源追踪、冲突解释和导出能力。

### 13.4 使用透明度

任务开始时说明本次将采用哪些重要记忆，并允许暂停；任务结束时说明产生哪些候选记忆。高影响记忆被调用时必须能回答“为什么这样做”。

## 14. Skill 体系与受治理自进化

### 14.1 Skill 的定义

Skill 是版本化、可运行、可验证的工作方法，不只是 Prompt 文件。完整 Skill 包含：

- 适用条件与禁用条件；
- 所需输入与预期输出；
- 推荐步骤或 Workflow 模板；
- 工具、MCP 和 Plugin 依赖；
- 权限需求；
- 成功标准与 Evidence 要求；
- 回退和异常策略；
- 版本、来源、作用域与历史表现。

### 14.2 Skill 作用域

- 全局 Skill：跨 Workspace 的个人通用方法；
- Workspace Skill：项目特定流程和命令；
- 临时 Skill：从本次任务生成，只在当前 Run 使用；
- 团队 Skill【远期探索】：组织审查后共享。

Workspace 版本可以覆盖全局版本，但必须显示来源；未挂载 Skill 不进入运行时。

### 14.3 Skill 进化闭环

```text
Skill v1 执行
  → Run 与 Evidence
  → 发现失败、重复步骤或用户纠偏
  → 生成 Skill Patch
  → 自动回放或沙箱验证
  → 展示差异、依据和预期收益
  → 用户 / 治理策略批准
  → Skill v1.1
  → 灰度调用与效果评估
  → 保留、回滚或继续迭代
```

### 14.4 可以进化与不可自行进化的内容

可以优化：

- 拆解顺序；
- 工具选择；
- 验证步骤；
- 重试与回退；
- 输出格式；
- 低风险默认动作；
- 何时请求 Explorer 或 Verifier。

不可自行修改：

- 用户目标和非目标；
- 权限边界；
- 费用上限；
- 敏感数据策略；
- 什么算最终人工验收；
- 系统安全红线。

原则是：

> **进化工作方法，不进化用户意图；提升执行能力，不自行扩大权力。**

### 14.5 Skill 质量指标

- 成功率与 Evidence 完整率；
- 平均用户干预次数；
- 平均完成时间与成本；
- 回滚率和负面结果；
- 跨环境适用性；
- 与旧版本相比的显著收益。

低调用量或高风险 Skill 不允许仅凭单次成功自动升级。

## 15. Canvas：共享任务认知层

### 15.1 为什么需要 Canvas

Conversation 是线性时间轴；复杂任务是空间化关系网络。多个方案、子 Agent、Artifact、Evidence 和决策都塞进聊天后，用户仍需自己重建全局状态。

Canvas 提供一个“共同看着同一件工作”的界面：

```text
Goal
 ├─ Constraints
 ├─ Decisions waiting for user
 ├─ Workflow branches
 │   ├─ Explorer findings
 │   ├─ Executor output
 │   └─ Verifier result
 ├─ Artifacts
 └─ Evidence and acceptance
```

### 15.2 首版节点类型

2.0 首版只支持真实对象：

- Goal；
- Step；
- Decision；
- Agent Run；
- Artifact；
- Evidence。

不做任意便签、通用图形库和自由工作流编程器。

### 15.3 核心交互

1. **自动结构化**：从输入和 Plan 生成初始 Canvas。
2. **聚焦当前交接**：突出需要用户判断的节点。
3. **方案比较**：并列展示影响、证据和成本。
4. **结果验收**：需求、改动、截图、测试在同一视图对照。
5. **深入 Workbench**：资源节点打开对应 Browser、Files 或 Documents。
6. **驱动 Workflow**：批准、选择、重试和取消通过命令作用于真源。
7. **提炼经验**：结束时从决策和 Evidence 生成 Memory / Skill Patch。

### 15.4 Canvas 的反目标

- 不让用户手工维护 Plan 进度；
- 不展示所有工具调用和 Agent 内心独白；
- 不用动画头像制造“忙碌感”；
- 不成为 Miro/Figma 替代品；
- 不复制 Artifact 内容形成版本分叉；
- 不要求简单任务进入 Canvas。

## 16. 能力成熟度总表

| 能力 | 当前已实现 | 2.0 建设项 | 远期探索 |
|---|---|---|---|
| Workspace | 切换、运行可见、路径上下文 | 记忆、权限、全局任务投影 | 跨 Workspace 事务 |
| Task/Conversation | 新建任务、列表、搜索、置顶归档 | 行动权投影、任务工作台 | 团队 Portfolio |
| GoalPlan | 状态、进度、Evidence、Runner | Goal/Plan/Run 完整产品化 | 组合 Goal 网络 |
| Workflow | Goal Runner 与恢复基础 | 通用 DAG、补偿、模板 | 分布式执行 |
| 子 Agent | 只读 Explorer 基础 | Executor、Verifier、预算治理 | 专业 Agent 市场 |
| Computer Use | 内嵌 Browser 工具 | L1 完整闭环、L2 受控浏览器 | L3 OS UI |
| Workbench | Plan/Browser/Files/Documents | Result Package 与 Evidence 深联动 | 多人共同现场 |
| Memory | Conversation/Goal 状态与知识库基础 | 四层可治理记忆 | 团队知识图谱 |
| Skill | 本地 Skill 作用域与挂载 | 运行评估、Patch、版本进化 | 生态分发与市场 |
| Canvas | 无正式产品能力 | 真实对象 Task Canvas | 多人实时协作 |

# 第四篇：产品与技术架构

## 17. 分层架构

Peer 2.0 采用“一个执行内核、多个客户端、能力可替换”的结构：

```text
体验层
  Desktop / CLI-TUI / Notifications / Future Mobile Companion

产品投影层
  Task Workbench / Conversation / Canvas / Workbench / Result Package

委托控制层
  Goal Contract / Planning Policy / Handoff / Acceptance / Governance

执行编排层
  Workflow Engine / Goal Runner / Scheduler / Checkpoint / Sub-agent Broker

认知与复利层
  Context Assembly / Memory Store / Skill Registry / Skill Evolution

能力运行层
  Local Tool Host / MCP / Plugin / Shell / Browser / Computer Use

事实与证据层
  Conversation Store / Goal Store / Run Ledger / Evidence / Artifact / Audit

平台层
  Local Runtime / Cloud Runtime / Provider Gateway / Auth / Sync
```

上层可以更换界面，下层可以更换模型，但 Goal、Run、Evidence 与权限真相保持稳定。

## 18. 单一数据真源

### 18.1 真源分配

| 事实 | 唯一拥有者 | 其他界面行为 |
|---|---|---|
| Conversation 消息 | Conversation Store | 搜索、摘要、引用 |
| Goal 与 Plan 状态 | Goal Store | 首页、Canvas、Workbench 投影 |
| 下一执行位置 | Checkpoint / Runner | 客户端显示，不自行猜测 |
| 工具调用与执行 | Run Ledger | Timeline 和审计投影 |
| 完成依据 | Evidence Store | Result Package、Verifier 引用 |
| 文件与文档内容 | Workspace / Artifact Store | Workbench、Canvas 引用 |
| Memory | Memory Store | Context Assembly 选择性注入 |
| Skill 版本 | Skill Registry | Runtime Projection 挂载 |
| 权限 | PermissionGrant / Policy Store | UI 请求与状态展示 |
| Canvas 布局 | Canvas View Store | 不复制业务状态 |

### 18.2 投影而非复制

Task Workbench 是跨对象 read model，可以将 Conversation、Goal、Runner、等待确认和未读结果聚合成任务行，但不拥有状态。Canvas 只保存引用和布局。任何为了前端方便而复制权威进度的做法都会导致迟早不一致。

### 18.3 事件与派生视图

2.0 建议建立统一 Domain Event：

```text
TaskCreated
GoalActivated
PlanChanged
RunStarted
StepCompleted
EvidenceAttached
UserActionRequired
UserDecisionRecorded
RunPaused / Resumed / Failed
ResultReady
TaskAccepted / Archived
MemoryProposed / Activated / Revoked
SkillPatchProposed / Released / RolledBack
```

事件用于刷新 read model、通知和审计，但权威状态仍由对应 Store 持有。事件消费必须可重放、幂等并支持 schema version。

## 19. Local-first 与 Cloud-enhanced

### 19.1 本地优先原则

本地是 Peer 差异化的重要组成：

- Workspace 文件和项目规则默认不离开设备；
- Shell、文件系统、内嵌 Browser 和凭据操作由 Local Tool Host 执行；
- 本地任务状态可以离线查看；
- 敏感 Evidence 可只存本地；
- 用户拥有导出、删除和迁移权。

### 19.2 云端适合承担的职责

- 模型与高级推理路由；
- 多设备同步的非敏感元数据；
- 云 Skill 编排和受控分发；
- 团队协作与策略管理；
- 长时云端 Agent 运行【后续阶段】；
- 聚合匿名质量指标（明确授权）。

### 19.3 混合运行的边界

任何云端 Tool Call 必须通过 Runtime Projection 到授权客户端；本地能力不能被云端绕过。断网时待回传结果进入本地队列，恢复后幂等 flush。用户应清楚看到任务目前由本机还是云端运行，以及本机离线后会发生什么。

## 20. Context Architecture

### 20.1 按需组装而非全量塞入

每次 Agent Run 的上下文由统一 Context Assembler 组装：

```text
System Policies
+ Goal Contract
+ Current Plan / Checkpoint
+ Recent Protocol Tail
+ Relevant Workspace Facts
+ Applicable User Preferences
+ Mounted Skill Instructions
+ Retrieved Evidence / Artifact Summaries
+ Tool Projection
```

Conversation 全历史、所有 Memory 和所有 Skill 都不应无差别进入上下文。

### 20.2 上下文压缩原则

- Plan 保存事实；
- Checkpoint 保存下一步；
- Evidence 证明已发生；
- Summary 保存原因和决策；
- Recent Tail 保存协议局部性；
- Compaction 不结束 Goal。

压缩产物必须可追溯到原始材料，并支持按需回捞。

### 20.3 防污染

- Workspace 记忆默认不跨域；
- 外部网页内容视为不可信输入；
- Skill 与 Memory 注入有来源标签；
- 被撤销或过期信息不得进入运行上下文；
- Prompt Injection 防护贯穿 Browser、MCP、Artifact 和 Memory 晋升。

## 21. 权限、风险与安全治理

### 21.1 风险分级

| 风险 | 示例 | 默认行为 |
|---|---|---|
| R0 只读 | 搜索、读取、截图 | 自动执行，留审计 |
| R1 可恢复写入 | 新建文件、小范围编辑 | 在任务边界内执行 |
| R2 外部副作用 | 发消息、提交、发布预览 | 明确策略或一次确认 |
| R3 高影响 | 删除、正式发布、付费、权限变更 | 强制确认与预览 |
| R4 禁止 | 绕过安全、隐蔽持久化、未经授权敏感操作 | 不提供能力 |

风险由动作语义、目标环境、可逆性、数据敏感度和用户策略共同决定，不能只按工具名判断。

### 21.2 权限不是永久同意

PermissionGrant 包含：

- 授权主体和执行 Agent；
- 工具与具体动作；
- Workspace / 域名 / 路径范围；
- 时间、次数和费用限制；
- 是否可委托子 Agent；
- 撤销方式；
- 对应用户决策与 Evidence。

Skill、Memory 和 Workflow 都只能请求权限，不能拥有权限。

### 21.3 审计与隐私

- 每个副作用可追溯到 Goal、Run、Agent 和授权；
- 日志与 Evidence 分级存储、保留和删除；
- Secret 不进入模型上下文和普通日志；
- Screenshot/DOM 支持敏感遮蔽；
- Memory 可以逐条查看、修改、撤销和导出；
- Skill Patch 显示完整 Diff 和行为变化。

## 22. 可靠性与运行治理

### 22.1 状态机而非 Prompt 自觉

关键运行行为必须由代码状态机保证：

- Plan 审批；
- Goal 激活；
- Runner phase；
- 子任务完成门；
- UserActionRequired；
- 重试预算；
- 完成门和计划生命周期；
- 防止僵尸计划和重复 Goal。

### 22.2 幂等与副作用

所有可能重复投递的操作必须具有：

- Invocation ID；
- 幂等键；
- 执行前状态；
- 执行后 Evidence；
- 可用时的补偿动作；
- 未知状态时禁止盲目重试。

### 22.3 预算治理

每个 Goal 可设置：

- 最大运行时长；
- Token / 金额预算；
- 子 Agent 并发数；
- Computer Use 操作次数；
- 自动修复轮数；
- Evidence 存储上限。

预算耗尽前应预警并说明已取得进展，而不是突然停止。

### 22.4 可观测性

内部指标包括：

- Run phase 与耗时；
- 工具成功率和重试原因；
- Checkpoint 恢复率；
- 上下文压缩次数与回捞；
- Evidence 完整率；
- 用户交接原因；
- Skill 版本表现；
- Computer Use 定位与断言失败类型。

用户界面只展示与判断有关的摘要，技术详情按需展开。

## 23. API 与数据模型演进建议

### 23.1 TaskOverview Read Model

2.0 首页需要统一接口，而不是 Renderer 对每个 Conversation 发起 N+1 Goal 查询：

```ts
type TaskOverview = {
  taskId: string
  conversationId: string
  title: string
  workspacePath: string
  updatedAt: string
  pinnedAt?: string
  archivedAt?: string
  actionOwner: 'user' | 'peer' | 'none'
  state: 'idle' | 'planning' | 'executing' | 'verifying' |
         'waiting_user' | 'result_ready' | 'failed' | 'accepted'
  currentGoal?: GoalSummary
  attention?: AttentionSummary
  artifactSummary?: ArtifactSummary
  unreadResult: boolean
}
```

该模型由后端聚合并支持 Workspace、状态、游标、排序与搜索。

### 23.2 Run 与 Workflow

在兼容现有 GoalPlan 的前提下逐步引入：

- `workflowTemplateId` 与版本；
- `runId` 和父子 Run；
- Step input/output refs；
- Checkpoint refs；
- Agent assignment；
- Retry / compensation state；
- Verification result；
- Budget ledger。

### 23.3 Memory 与 Skill Patch

Memory、Skill、Patch 必须是独立可审计实体，不能混在 Conversation metadata。所有 schema 引入 version 和 migration；删除 Workspace 时按策略处理其私有记忆与 Evidence。

## 24. 架构非目标

2.0 不追求：

- 一次性重写现有 Electron + Runtime；
- 让所有状态采用 Event Sourcing；
- 自研基础模型；
- 让 Canvas 成为数据库；
- 无边界跨设备远程控制；
- 无限层级子 Agent；
- 把每种工具包装成独立微服务；
- 为展示先进性而引入分布式复杂度。

架构判断标准始终是：是否让真实委托更可靠、更可恢复、更可验证。

# 第五篇：产品方向、增长与商业

## 25. 产品战略主线

Peer 2.0 的战略不应围绕“支持更多模型和工具”展开，而应围绕三条递进主线：

### 25.1 Trust：先让用户敢交出去

目标：用户敢把一个真实任务交给 Peer，并短暂离开。

关键能力：

- Evidence Gate；
- 可恢复 Goal Runner；
- 明确 Workspace 和权限；
- 真实环境验证；
- 失败与未验证项透明；
- 高价值人机交接。

### 25.2 Throughput：再让用户同时交更多

目标：用户从一次委托扩展到多个并行任务，而不增加管理负担。

关键能力：

- 任务工作台；
- 行动权与通知；
- 子 Agent 和 Workflow；
- 预算、优先级与调度；
- Result Package；
- 跨 Workspace 全局巡视。

### 25.3 Compounding：最后让每次委托产生复利

目标：同一 Workspace 的后续任务更快、更准、更少干预。

关键能力：

- 可治理 Memory；
- Skill 进化；
- 成功 Workflow 复用；
- 用户协作偏好；
- Canvas 中的结构化决策；
- 质量评估和回滚。

顺序不能倒置。没有 Trust 的 Memory 会放大错误；没有可靠 Workflow 的多 Agent 会放大混乱；没有真实任务量的 Skill Evolution 只是自我修改表演。

## 26. 用户粘性飞轮

```text
用户委托真实任务
  → Peer 可靠执行并减少监督
  → Evidence 提升验收信任
  → 用户愿意托付更重要、更长的任务
  → 产生高质量决策、Artifact 与程序性经验
  → Workspace Memory 和 Skill 更准确
  → 下一次更少解释、更少打扰、更高成功率
  → 用户在 Peer 中承载更多真实工作
```

粘性来自“工作关系资产”，不是消息历史数量。最强留存信号是：用户开始把风险更高、跨度更长、跨更多工具的工作交给 Peer。

## 27. 北极星指标与指标树

### 27.1 北极星指标

> **每周经证据验收的委托任务数（Weekly Verified Delegations, WVD）**

一项任务只有满足以下条件才计数：

1. 用户表达了具有结果导向的委托；
2. Peer 执行了至少一个实质步骤；
3. 完成声明具有符合要求的 Evidence；
4. 用户接受，或所有预先约定的自动标准通过且无需人工验收；
5. 同一目标的重复 Run 不重复计数。

### 27.2 激活指标

- 首个 Workspace 成功连接率；
- 首次委托到首个可信结果的时间；
- 首次任务 Evidence 完整率；
- 首次完成后 7 日内第二次委托率；
- Onboarding 中需要用户手工配置的步骤数。

### 27.3 信任指标

- 用户接受率；
- 完成后回滚率；
- 虚假完成率（声明通过但复验失败）；
- 平均每任务高价值干预次数；
- 无价值打扰率；
- Checkpoint 恢复成功率；
- 高风险动作未授权执行数（目标必须为 0）。

### 27.4 效率指标

- 委托到结果的主动时间与日历时间；
- 用户实际参与分钟数；
- 自动修复成功率；
- Explorer 并行带来的关键路径缩短；
- 单个可信任务的模型与计算成本；
- N+1 工具调用和重复调查比例。

### 27.5 复利指标

- Workspace Memory 被有效调用率；
- Skill 复用率与版本提升收益；
- 同类任务用户干预下降幅度；
- 候选记忆接受、修订、拒绝比例；
- 过期 Memory 触发率；
- 用户从“简单任务”迁移到“长期任务”的比例。

### 27.6 不作为北极星的指标

- 消息数；
- 在线时长；
- 每日打开次数；
- 工具数量；
- Agent 数量；
- Token 消耗；
- Canvas 节点数量。

这些数值可以反映使用，却可能与真正价值负相关。

## 28. 市场进入策略

### 28.1 第一阶段：可信工程委托

选择四种可展示完整 Evidence 的任务，打造公开案例和模板：修 Bug、工程重构、UI 验收、发布前检查。传播内容展示完整委托链，而非模型跑分。

示例故事：

```text
用户只描述一次目标
Peer 调查 3 个真实系统边界
中间只请求 1 次产品决策
修改 7 个文件
运行 12 项检查
真实打开桌面端验证 5 条动线
用户 40 分钟后回来验收
```

### 28.2 第二阶段：个人工作系统

扩展到研究、文档、网页操作和跨 Workspace 工作。重点推广“所有重要工作在一个委托台管理”，而不是“一个聊天框做所有事”。

### 28.3 第三阶段：小团队可信协作

在个人闭环稳定后加入：

- 团队 Workspace 策略；
- Shared Skill 审查；
- 角色与权限；
- Result Package 分享；
- 团队 Evidence 和审计；
- 任务转交与共同验收。

不急于复制项目管理软件；Peer 只承载 Agent 真正执行和交接的部分。

## 29. 商业模式

### 29.1 定价原则

用户为“可靠完成更多真实工作”付费，而不是为按钮或 Agent 头像付费。价格应与可用执行能力、并发、保留和治理价值相关，同时保持模型成本透明。

### 29.2 建议层级

#### Personal Local

- 本地 Workspace、Conversation 和基础 Goal；
- 用户自带模型或有限托管额度；
- 基础 Workbench 与内嵌 Browser；
- 本地 Memory 和 Skill；
- 适合作为免费或低价获客层。

#### Pro Delegation

- 长任务 Runner 与更高预算；
- 多任务工作台；
- 子 Agent 与 Verifier；
- 外部 Browser Computer Use；
- Skill Evolution；
- 高级 Evidence、历史和导出；
- 以月订阅 + 透明计算额度定价。

#### Team Governance

- 团队 Workspace、权限和审计；
- Shared Skill 审批与版本治理；
- 组织级 Provider / MCP；
- Evidence 保留策略；
- SSO、角色和预算控制；
- 按席位 + 执行用量。

### 29.3 不建议的商业路径

- 靠售卖不透明 Token 差价；
- 用锁定格式阻止导出；
- 为提高收入故意增加 Agent 调用；
- 以 Skill 商店数量代替质量；
- 在信任未建立前售卖“完全自主”。

### 29.4 Skill 生态的长期可能

当 Skill 有统一评估、权限和 Evidence 后，可形成：

- 官方可信 Skill；
- Workspace 模板；
- 第三方 Skill 与 Plugin；
- 企业私有 Skill Registry；
- 按成功执行或订阅分成。

但 Skill 市场必须晚于 Skill 质量体系，否则只会成为 Prompt 文件市场。

## 30. 品牌与传播

### 30.1 品牌核心

Peer 的人格不是“无所不能的超级 AI”，而是：

- 有能力但不冒进；
- 主动推进但尊重边界；
- 诚实说明证据和未知；
- 能长期记住共同工作方式；
- 在关键处把判断权还给人。

### 30.2 核心话术

品牌主张：

> **把工作交给 Peer，只在真正需要你的时候回来。**

能力解释：

> **Peer 在你的 Workspace 中持续推进任务，自己验证结果，并把关键决定和可验收成果交还给你。**

差异表达：

> **不是更多 Agent，而是一个越来越懂你、并对结果负责的 Peer。**

### 30.3 内容策略

高价值内容包括：

- 完整委托回放；
- Evidence 驱动的结果对比；
- 失败如何被发现和自动修复；
- Skill 如何从真实任务中进化；
- Local-first 权限和隐私解释；
- 用户从频繁监督到只处理关键交接的变化。

## 31. 产品组织方式

建议产品与研发围绕四条 Value Stream，而不是按前端、后端或“AI 功能”割裂：

1. **Delegation & Handoff**：Task Workbench、Conversation、Goal Contract、通知。
2. **Execution & Verification**：Workflow、Runner、子 Agent、Computer Use、Evidence。
3. **Knowledge & Evolution**：Memory、Skill、Context、评估。
4. **Workspace & Governance**：Local Runtime、权限、Workbench、同步和企业策略。

每条 Stream 都对用户结果和指标负责，平台团队维护共享协议与可靠性。

# 第六篇：实现路线图与预期效果

## 32. 路线图原则

1. 每阶段必须交付一个用户可感知闭环，而非只交付基础设施。
2. 先可靠后扩张：Evidence 与恢复早于多 Agent 和自进化。
3. 先纵向打透场景，再横向增加工具和应用。
4. 兼容现有 Conversation、GoalPlan 和 Workbench，不大爆炸重写。
5. 每个阶段用真实委托指标验证，不以代码量或功能数完成。
6. 后续阶段可以调整，但不得跨过安全与数据真源前置条件。

## 33. Phase 0：事实统一与可靠性基线

### 目标

把当前已有能力收敛成一个可靠内核，为 2.0 上层产品消除状态分叉。

### 核心交付

- Goal / Plan / Run 术语和状态语义统一；
- Plan 生命周期、防僵尸计划和完成门；
- Checkpoint 与 Context Compaction 续接；
- Evidence schema、敏感级别与 artifact 引用；
- Workspace、Conversation、GoalPlan 的关联核清；
- Tool Result、PermissionGrant 和 Evidence 主链路；
- Desktop / CLI 使用同一权威状态。

### 验收场景

一项 30 分钟以上任务经历窗口关闭、上下文压缩或 Provider 恢复后，能够从正确步骤继续，已完成步骤不重复，最终每个完成项有 Evidence。

### 预期效果

- 恢复成功率达到可用基线；
- 虚假完成可以被系统阻止；
- Goal 状态不再依赖 UI 或模型叙述。

## 34. Phase 1：可信单任务委托闭环

### 目标

让首批用户敢把一个真实工程任务交给 Peer 后离开。

### 核心交付

- Agent 默认模式和 L0—L3 自适应规划；
- Goal Contract 与 DoD-as-Code；
- 改进后的 Goal/Plan Workbench；
- Result Package；
- 人机交接卡与行动权状态；
- 内嵌 Browser 的 Observation / Action / Assertion / Evidence 闭环；
- Explorer 调查与高风险任务 Verifier；
- 四种官方任务 Recipe：修复、重构、UI 验收、发布检查。

### 验收场景

用户提交一个 UI Bug。Peer 自行调查、修改、运行工程检查、打开真实页面完成交互验证，只有必要时询问一次，最后交付文件、测试、截图和剩余风险。

### 预期效果

- 首个可信结果时间显著下降；
- 首次任务接受率提高；
- 用户无需充当默认测试员；
- 形成可传播的完整委托案例。

## 35. Phase 2：多任务工作台与吞吐

### 目标

让用户同时托付多个任务，仍能一眼掌握行动权和结果。

### 核心交付

- `TaskOverview` 聚合接口；
- 以“需要你 / Peer 推进 / 结果到达”为主轴的首页；
- 当前与全部 Workspace 视图；
- Attention、Result Ready 和跨 Workspace 跳转；
- 调度预算与并发控制；
- Executor 子 Agent；
- Workflow DAG 基础、并行与条件步骤；
- 低噪音系统通知。

### 验收场景

用户同时运行 5 个任务：2 个在执行、1 个待确认、1 个结果待验收、1 个空闲。用户无需打开所有 Conversation，就能处理关键交接并进入正确 Workbench 位置。

### 预期效果

- 用户可托付任务数提升；
- 无价值会话切换下降；
- 关键交接响应更快；
- WVD 开始成为稳定周指标。

## 36. Phase 3：Workspace Memory 与工作复利

### 目标

让第二次同类委托明显比第一次更容易。

### 核心交付

- Memory Store 和四层类型；
- Candidate → Active → Stale / Revoked 生命周期；
- 来源、Evidence、冲突、过期和撤销；
- 任务开始的 Memory 使用说明；
- 任务结束的候选经验审查；
- Context Assembler 按需注入；
- Workspace 规则、命令、架构决策和用户偏好界面。

### 验收场景

同一 Workspace 第二次进行 renderer UI 修改时，Peer 自动采用已确认的 Token source of truth 和验证流程，不重复询问；用户可查看为何采用并可撤销。

### 预期效果

- 同类任务准备时间下降；
- 重复解释减少；
- Memory 错误可发现、可纠正；
- 用户开始感知“Peer 了解这个 Workspace”。

## 37. Phase 4：Skill Evolution 与成熟 Workflow

### 目标

把已验证经验转化成可版本化执行能力。

### 核心交付

- 完整 Skill Manifest 与质量指标；
- Skill Run 评估；
- Skill Patch 生成、Diff、审批和回滚；
- Workflow Template Registry；
- 沙箱/回放评估；
- Workspace / Global Skill 覆盖与挂载治理；
- Verifier 作为 Workflow 标准节点；
- 成本和成功率版本对比。

### 验收场景

某 UI Skill 连续三次因缺少真实浏览器验证被打回。Peer 提议增加验证步骤，回放历史任务证明改善，用户批准 v1.1；后续任务自动采用且失败率下降。

### 预期效果

- Skill 复用与成功率提升；
- 用户干预次数下降；
- 工作方法形成可审计资产；
- Peer 的长期差异化开始形成。

## 38. Phase 5：Task Canvas 与复杂任务协作

### 目标

让复杂任务从“难以翻阅的聊天”转变为人和 Peer 共同理解的工作现场。

### 前置条件

- Goal、Run、Evidence、Artifact、Decision 已有稳定 ID 和 API；
- Workflow 状态可订阅；
- Workbench 资源可深链接；
- Canvas 不需复制状态。

### 核心交付

- Goal、Step、Decision、Agent Run、Artifact、Evidence 六类节点；
- 自动布局和当前交接聚焦；
- 方案比较和批注；
- Workflow 操作命令；
- Workbench 深链；
- Result Review 模式；
- 从 Canvas 决策提取 Memory / Skill Patch。

### 验收场景

一个包含三种首页方案、两个 Explorer、一次用户决策和多份截图的任务，用户不翻聊天即可理解选择依据、执行进展和最终验收证据。

### 预期效果

- 复杂任务理解成本下降；
- 用户关键判断质量提高；
- Canvas 成为 Peer 独特的共享认知界面，而不是白板噱头。

## 39. Phase 6：受控外部 Computer Use 与团队治理

### 目标

扩大可委托工作边界，并将个人可信闭环扩展到小团队。

### 核心交付

- Playwright/CDP 受控浏览器；
- Profile、Session 与授权模型；
- 下载、网络、权限弹窗和多页 Evidence；
- Team Workspace、角色与策略；
- Shared Skill 审查；
- 预算、审计与 Evidence 保留；
- Result Package 分享与共同验收。

### 预期效果

- Web 工作流覆盖增加；
- 团队可治理地复用 Skill；
- 商业化从个人订阅进入团队治理价值。

## 40. 远期探索

只有在前述阶段指标成立后再评估：

- macOS 广义 OS Computer Use；
- 云端长时运行与多设备接力；
- 团队实时 Canvas；
- 组合 Goal 与 Portfolio；
- Skill 生态与交易市场；
- 多 Peer 协作网络；
- 企业知识与 Workflow 图谱。

远期探索必须回答：它是否提高可信委托，而不仅是扩大演示范围。

## 41. 优先级决策矩阵

任何新需求按五项评分：

| 维度 | 核心问题 |
|---|---|
| 委托价值 | 是否减少用户亲自推动工作？ |
| 信任价值 | 是否让结果更可信、边界更清楚？ |
| 复利价值 | 是否让下一次任务更容易？ |
| 覆盖价值 | 是否服务目标用户高频场景？ |
| 复杂度成本 | 是否引入新的真源、权限或恢复风险？ |

高演示价值但低委托/信任价值的功能降级，例如无限 Agent 头像、通用白板、海量 MCP 列表。

## 42. 关键风险与应对

### 42.1 产品过度膨胀

风险：Task、Goal、Workflow、Canvas、Memory、Skill 概念过多。  
应对：用户主心智只保留 Workspace、Task、Peer、Result；其余按需渐进暴露。

### 42.2 自主性破坏信任

风险：误操作、过度权限、错误记忆。  
应对：风险分级、Evidence Gate、PermissionGrant、可撤销 Memory、Skill Patch 审批。

### 42.3 Agent 成本失控

风险：多 Agent 和自动修复产生高额调用。  
应对：预算账本、并发上限、关键路径并行、模型路由、成本前置提示。

### 42.4 Memory 污染

风险：错误经验被反复调用。  
应对：Evidence 晋升、作用域隔离、冲突检测、过期、负反馈降级和撤销。

### 42.5 Canvas 成为独立产品

风险：投入大量通用编辑能力，却不改善委托。  
应对：只支持真实对象、自动组织优先、执行状态只读投影、按复杂度启用。

### 42.6 基础模型快速追平

风险：模型厂商补齐任务和工具能力。  
应对：保持模型中立，深耕跨模型持久状态、Workspace 本地能力、Evidence、治理和程序性资产。

### 42.7 本地与云割裂

风险：同一任务在不同宿主状态不一致。  
应对：共享协议、单一真源、运行主体可见、幂等同步和客户端只做投影。

## 43. 2.0 达成后的预期效果

### 43.1 对用户

用户打开 Peer，不再先面对一串会话，而是看到：哪里需要自己，Peer 在推进什么，哪些结果等待验收。用户可以把任务交出去，离开，回来做一次高价值判断，再继续离开。

### 43.2 对任务质量

完成从自然语言声明升级为多层验证和 Evidence；失败从聊天中的一句道歉升级为可恢复的诊断与修复循环；跨天任务不再依赖用户记住上下文。

### 43.3 对产品粘性

同一 Workspace 的事实、决策、验证流程和 Skill 逐渐形成复利。用户留下不是因为无法迁移，而是 Peer 已成为最了解其工作环境、且最值得信任的委托入口。

### 43.4 对市场定位

Peer 从拥挤的“Agent 客户端”中脱离，成为 Delegation OS：模型与工具之上的工作关系和治理层。竞争焦点从“谁更聪明”转向“谁能持续承担真实工作并证明结果”。

### 43.5 对商业

个人用户为更高吞吐和可信自动化付费；团队为权限、审计、Shared Skill 和共同验收付费；Skill 生态在质量体系成熟后成为增量，而非早期主线。

## 44. 2.0 最终 Definition of Done

Peer 2.0 不能以“所有模块上线”定义完成，而应满足以下用户结果：

1. 用户可在一个真实 Workspace 中完成首次可信委托；
2. 长任务跨压缩、重启和短暂故障可恢复；
3. 完成声明均有可定位 Evidence；
4. 首页准确区分用户行动、Peer 行动和结果待验收；
5. 用户可同时托付多个任务而无需逐个翻会话；
6. 至少四类核心场景有高成功率官方 Workflow / Skill；
7. 第二次同类任务能够安全复用已确认经验；
8. Memory 与 Skill 可解释、可撤销、可回滚；
9. Computer Use 能在目标纵向场景中验证真实界面；
10. 用户愿意在首个任务后七天内托付第二项真实工作；
11. Weekly Verified Delegations 成为稳定、可增长的核心指标；
12. 高风险未授权执行保持为零。

## 45. 结语：Peer 要建立的不是功能集合，而是一种工作关系

Peer 2.0 的最终形态不是聊天框、任务表、Canvas、Workflow 或 Agent Swarm 中的任何一个。它们都是为了同一件事服务：

> **让一项真实工作能够在人和 AI 之间被可靠地托付、推进、交接、验收，并让共同完成工作的经验持续复利。**

首页负责交接，Conversation 负责意图，Canvas 负责共识，Workbench 负责现场，Workflow 负责推进，子 Agent 负责分工，Computer Use 负责观察与操作，Evidence 负责证明，Memory 与 Skill 负责下一次做得更好，Workspace 则定义这一切发生的世界和边界。

如果 Peer 只是把这些能力堆在一起，它仍然只是复杂的 Agent 客户端。只有当用户真正产生下面的心智，2.0 才成立：

> **“这项工作我可以交给 Peer。它会持续推进；需要我时会说清楚；交回来时会带着结果和证据；下一次还会做得更好。”**

这就是 Peer 在 Agent 市场中应该占据的位置：

> **不是最喧闹、工具最多或 Agent 数量最多的产品，而是最值得长期托付工作的 Peer。**

