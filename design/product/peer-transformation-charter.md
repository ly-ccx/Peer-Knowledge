# Peer 改造总纲

创建时间：2026-08-22
最后更新：2026-10-23（项目代理壳进入 RC 收敛；接入产品体验规范与当前改造工作包）

> 版本：v3
> 状态：壳层与改造阶段真源；当前是已落地的项目代理壳，0.1.0 进入 RC 收敛，GA 尚未宣布。理念以 `peer-product-alignment.md` 为准。
> 范围：产品动线、信息架构、任务治理、证据链、Workspace Git 工作线、运行时演进  
> 原则：改造服务于「可治理的任务闭环」，不为追插件热度或对标而改。  
> 关联代码仓：`peer_agent`（远程 `https://github.com/ly-ccx/Peer-Agent`）  
> 关联决策：`knowledge/decisions/67-task-shell-workbench-radar.md`  
> 关联实现：  
> - `apps/desktop/renderer/src/chat/components/Sidebar.tsx`  
> - `apps/desktop/renderer/src/app/components/ConversationResultView.tsx`  
> - `apps/desktop/renderer/src/App.tsx`  
> - `packages/protocol/src/task-overview.ts`  
> 关联文档：  
> - `design/product/peer-product-alignment.md`（**产品链路唯一对齐方向**：理念、人群、价值、委托链路）  
> - `design/product/peer-2-0-product-system.md`（更早的 2.0 战略总纲；与对齐文档冲突时以对齐文档为准）  
> - `design/product/peer-2-0-workbench-flow.md`（工作台分桶；壳层以本文为准）  
> - `design/product/task-identity-conversation-carrier.md`（产品面说任务，存储主键仍是 conversation）  
> - `knowledge/architecture/task-lifecycle-and-acceptance-flow.md`（副作用必须先有 GoalPlan）

前身是本机草案 v1（2026-08-22）。A–E 的原型 A 历史保留；v3 将当前默认壳与历史实现分开。当前工作包和证据基线见 [产品改造计划](peer-product-renovation-plan.md)；产品理念以 `peer-product-alignment.md` 为准。

---

## 0. 当前方向

**每个项目一个项目代理。用户交代目标与边界，代理自己开任务、持续推进和验证；需要判断时递卡片，交还时先给结论与限制，细节和 Evidence 按需打开。**

当前默认壳是机器人列表 + 项目代理对话 + 按需档案/任务现场。任务仍是深度工作的单位，独立工作台页与侧栏任务树属于历史原型 A 和经典入口，不再作为新壳改造目标。任务、GoalPlan、Conversation 的现有身份与关系保留。

三拍不变：目标带着边界被签收 → 能力在授权下执行 → 完成用证据关闭。验证归代理，签收按既有策略，人工确认用于真正的例外；代码交回源头是另一件事。

## 1. 责任与产品识别度

优化少解释、少盯守、少切换、少怀疑和越用越顺。竞争力是任务闭环、Evidence、一条受治理能力链，以及可嵌入的同一套 Runtime；不以更多工具、代理角色、工作台卡片或特效数量衡量进展。

最新体验基线是 [Peer Frost](../../knowledge/specifications/peer-product-experience-standard.md)：安静委托，清晰交接。用中性冷灰、石墨操作、冰湖青印记与共享连续曲线表达；[人机交互契约](../../knowledge/specifications/peer-human-agent-interaction-contract.md)和[动效规范](../../knowledge/specifications/motion-system.md)约束具体行为。

不重回企业工单台、Cloud CEO 客户端、虚拟团队、无限白板中心或普通工具聊天壳。模型是认知角色，本机持有能力、授权和 Evidence，Renderer 只表达。

## 2. 当前心智与行动权

| 对象 | 作用 | 用户要知道什么 |
|---|---|---|
| Workspace | 项目、数据、权限和执行世界 | 这件事发生在哪里 |
| 项目代理 | 默认对话对象；理解、调度、汇报 | 我把目标交给谁 |
| 任务 | 被托付的一件事、目标与证据的单位 | 这次工作做到哪里、怎么继续 |
| 机器人列表 | 跨项目行动权与最近交流 | 现在是否需要我 |
| 对话 / 任务详情 | 意图、结论、决定与现场 | 下一步是谁、依据在哪 |

行动权消费 main/runtime 的统一投影；列表、卡片、详情不各算一份。未读不等于需要你，执行结束不等于验证通过，策略签收不等于代码已经合回。

## 3. 当前信息架构

```text
机器人列表：身份、最近交流、需要你 / 未读 / 进行中、搜索
  → 当前项目代理对话：输入、连续公开回复、需要你、结论
      → 原任务现场：目标 / 计划、当前决定、任务执行
      → 按需档案：概况 / 任务 / 目标 / 记忆 / 设置
      → 按需详情：过程 / 验证 / 产物 / Evidence
全局设置与经典入口：保留已有合法能力，复用共享部件
```

主区稳定、细节按需。旧原型 A 的工作台职责已由机器人列表、Attention 和原任务入口承接；不能另开一份无历史工单。任务内部子 Agent 是执行手段，不升成新的默认对话主语。

## 4. 当前主路径与收敛顺序

```text
进入或绑定项目 → 向项目代理表达目标
  → 持久接收 / 排队回执（保住未确认输入）
  → 轻量问答直接回复；真实委托开任务并锚定原输入
  → 确认目标、边界与成功标准；按既有策略批准计划
  → 在有效授权与执行隔离下推进
  → 缺信息 / 权限 / 冲突时把行动权交给人
  → 代理验证 / 必要修正 → 运行时形成结论
  → 策略签收或人工例外 → 交还结果与限制
  → 可选 Git 交回 → 继续追问或派生下一轮
```

规划深度 L0–L3 留在 Runtime，项目代理输入框不重新暴露 Agent/Plan 管理开关。停止回复、取消任务、拒绝授权、关闭面板分别处理。身份、授权、验证和恢复不能靠助手文本或动画推断。

当前 R0–R4 的具体工作见 [改造计划](peer-product-renovation-plan.md)：先事实与在途集成，再输入与可信交接，再焦点/滚动和共享组件，最后跨入口日用与最终候选验收。普通开发只做内容/diff 审阅；完整测试和产品回归在发版前，用户明确要求时才提前运行。

---

## 5. 阶段与交付

阶段 A–E 是已交付的历史轨迹，保留原规则和证据。当前以 F 的项目代理壳与最新 ADR 为准，不重新实施旧入口。每次收敛仍检查：用户能否少盯守、正确判断，并让真实工作带着依据交还？

### 阶段 A · 可见的治理闭环 — **已交付（2026-08-22，`peer_agent` `0.0.6`）**

产品第一优先。代码已落地，不改 protocol、不改 Git 闸门。

已交付：

- 侧栏工作台常驻 `需要你 N · 待验收 M`（排除 `source === 'conversation'` 的轻量问答）
- Workspace 下挂任务树；默认只展开当前区或当前任务所在区，其余折叠
- 点工作区只激活落点，不跳走；点任务进主区任务
- 任务列表后台续页，不再露出「加载更多」
- `result_ready` 先打开验收抽屉；页脚「继续追问 / 确认归档」
- 验收页只对照标准 × 证据，外加可打开产物与交卷前自检；不再摊进度、子任务、整段对话
- 工作台卡主按钮是「查看进度」，确认归档只出现在看过依据之后
- 空态「发出任务 / 继续这条任务」
- 默认落地保持任务页（`chat`）
- 去掉任务顶栏「待用户验收 · 任务详情」胶囊（与工作台雷达重复）

确认验收的作用：在 GoalPlan 上写下 `resultAcceptance`（谁、何时认了这笔结果）。签字后离开待验收；若该线已经拉出任务子分支并改过代码，签字才是交回**当前** Workspace 源头分支的闸门。它不批准计划、不继续推进。

未纳入 A、也不该回退的：

- 独立工单页、Cordis、把默认落地改回工作台
- 默认 worktree / 并行隔离（阶段 D）

### 阶段 B · 关闭闸门变硬 — **已交付（2026-08-22）**

A 级：关闭时强制 `evidenceRefs` 校验。写 `resultAcceptance` 必须经过协议层 `evaluateAcceptanceCloseGate`；store 是真值，界面只是先挡住。

已交付：

- 批准卡与 Goal 面板在待批准时可编辑成功标准（改描述、加减条目；新条为 `manual`）
- 关闭闸门：每条成功标准必须通过，且 `evidenceRef` 能在计划持有引用或 EvidenceIndex 里解析；人工标准可用后来的 `manual_dod` 批准代替
- 无成功标准的计划仍可验收（空集合为真）
- 验收页是签字包：对照标准、改了什么、签字前仍成立的阻塞；不是执行日记，不摊授权时间线或 Goal Runner 过程
- 对照不过线时禁用「确认归档」，并说明缺哪类依据

未纳入 B：Git 工作线、独立依据页、密码学证据链

### 阶段 C · Git 工作线 MVP — **已交付（2026-08-22）**

Workspace 源头分支是 settings 层的 `baseBranch`，不是新的 protocol 字段。绑定仍走已有 `deliveryBinding`；任务子分支先写 ref，不建 worktree。

已交付：

- Git 设置里为当前工作区选择源头分支；未固定时绑定当前 HEAD，不猜 `main`
- 切换源头只写 settings，不改已有 plan 的 `targetBranch` / `baseCommit`
- Plan 批准或 `accepted_goal` 且将写入仓库时，按分支前缀建任务子分支；工作区干净才 checkout
- 纯聊 / intake / 待批准不建线
- `executionIsolation === 'none'` 不再默认建 worktree；只有显式 `worktree` 才走隔离目录
- 验收页展示 `taskBranch · from <创建时源头>`、当前建议合入分支，以及 `baseCommit..taskBranch` 的 range diff
- 确认验收后的交回目标是**当时**的 Workspace `baseBranch`，创建时快照只作对照

未纳入 C：默认 worktree、清理策略、IDE/Finder 打开现场、中途升级为隔离线（阶段 D）

### 阶段 D · 并行隔离 — **已交付（2026-08-22）**

不默认 worktree。用户声明隔离时，给**已有任务子分支**挂 worktree，不另建 automation 风格分支。打开现场由 main 解析路径，不把隔离目录当成工作区相对路径交给 renderer。交回后只收隔离目录，保留任务分支名；删除这条线必须二次确认。

已交付：

- 新任务可在草稿 composer 勾选「隔离执行」；默认关闭，意图先记在任务上，有可写交付线后再走既有 `isolatePlan`
- 「隔离执行」把当前任务线升级为独立 worktree；主工作区若正占用该分支且干净，先切回源头
- 主工作区占用任务分支且有未提交改动时，拒绝隔离，不自动 stash
- 「打开现场 / 在编辑器打开」走 `goalPlans:open-site`，隔离目录优先，否则打开目标仓
- 交回成功后只 `worktree remove`，保留 `taskBranch`；未改动的 automation 线仍整段清掉
- 「删除这条线」以及取消推进后的第二次确认，才会删隔离目录和未合入的本地分支

未纳入 D：默认对所有任务建 worktree、自动 stash、清理已合入远端分支

### 阶段 E · 开发体验与可嵌入 — **已交付（2026-08-22）**

先迁能力注册层。不改 protocol 字段、Evidence 白名单、Goal 状态机、Projection 核心规则。

已交付：

- `CapabilityProviderRegistry` 增加 `unregister` / `replace`；Desktop 网关包装层同步，热替换不必重建进程
- Evidence 导出只打包已承认的 refs、授权摘要与索引记录，不带 runTrace 事件；IPC `goalPlans:export-evidence` 与 `examples/external-host` 可写 JSON，不作为验收页签字动作
- `examples/external-host` 演示 Provider 热替换 + 导出文档，不依赖 Desktop / CLI

未纳入 E：插件市场热加载、把产物文件打成 zip、密码学证据链、默认对所有任务建 worktree

### 阶段 F · 项目代理壳 — **已落地，进入 RC 收敛（2026-10-23 核对）**

A 级。决策见 `knowledge/decisions/80-project-agent-delegation-model.md`，运行时契约见 `knowledge/architecture/project-agent-delegation-runtime.md`，界面与分期见 `design/product/project-agent-workbench.md`。

已有交付的关系：用户主要和项目代理对话，任务由它开出；代理验证并按策略交还，只有真正需要人的决定才打扰。Beta1–5 与后续 RC 记录证明已有实现，不把设计 Accepted 或历史“未开工”标签当作当前交付状态。精确版本与覆盖范围见 [当前改造计划](peer-product-renovation-plan.md)及 [RC26 固定记录](https://github.com/ly-ccx/Peer-Knowledge/blob/43fece5fde940d60009158382450b0a5533374c5/playbook/v0.1.0/rc26-candidate.md)。

范围：

- 每个 Workspace 一条常驻项目代理对话；`project_agent` 模式严格白名单，只读 + 调度。
- 调度能力走同一条能力链：`spawn_session` / `message_session` / `cancel_session` / `list_sessions` / `get_session_report` / `spawn_subagent`（只读）。
- 任务 = 子 Conversation + GoalPlan，由现有 Goal Runner 推进；验收、关闭闸门、Git 线不变。
- 权限、决策、计划批准以同一条待处理请求冒泡到代理对话；代理不能替用户批。
- 多任务并行时第二条写仓库任务起强制 worktree。
- 主动开口过「值得打扰」评估，用户可调主动性档位（ADR 80 决策 9）；项目目标与定时 / 事件驱动推进（ADR 82）；记忆体系（ADR 81）。
- 验证归代理、签收按策略、细节按需：运行时算验证结论，低风险且通过时代理汇报即策略代签；例外时「需要你确认」；合入默认一键确认；关闭闸门不松。
- 壳（ADR 84）：即时通讯式机器人列表（头像、名字、预览、需要你 / 未读 / 进行中，按最近活动排序，顶部「需要你」筛选与搜索）+ 机器人对话 + 按需滑出的档案；新建机器人可绑定已有文件夹或建受管文件夹 `~/Peer/<名字>/`；不做市场。独立工作台页、侧栏任务树、代理输入框的 Agent / Plan 切换器退场。

P0–P5 的早期分解和 feature flag 迁移保留为历史；旧 0.0.19–0.0.26 排期不再执行。当前是 0.1.0 RC 的一致性、恢复与体验收敛，工作包 E00–E14 及批次 R0–R4 见 [改造计划](peer-product-renovation-plan.md)。新规范不授权新权限、存储或能力边界；需要移动时仍先 ADR。

不纳入 F：多个常驻专职代理、代理间群聊、代理直接做小改动、新建 Task / Project 存储实体。

---

## 6. Git 工作线（历史 C / D 与当前项目代理壳）

| 议题 | 默认 |
|------|------|
| 默认合入 | 验收时的当前 Workspace `baseBranch` |
| 创建时源头 | 对比基线与说明，不是默认合入目标 |
| 自动 worktree | 经典任务保留原选择；项目代理任务按当前调度/隔离契约安排，F 中并行写任务的隔离要求继续有效 |
| 切换源头 | 只影响之后新建任务线 |
| 拒收 / 取消 | 停 runner；删除 worktree / 分支要二次确认 |

历史 C / D 的 UI 最小露出：Workspace 主开发分支下拉；新任务草稿可勾选隔离执行；任务标题与输入栏可见绑定/源头分支；任务行 `feat/… · from develop`；待验收卡展示 diff 与建议合入分支；任务卡可「隔离执行 / 打开现场 / 删除这条线」。

---

## 7. 证据不变量（不因阶段 A 而松）

1. 摘要 ≠ 证据。
2. 模型输出不能自我注册为证据。
3. 无授权则无合法副作用；结果必须能回溯到 Grant。

关闭闸门（阶段 B 已强制，写在 `revisePlan`）：

```text
∀ successCriterion
  ∃ 可解析的 evidenceRefs
    且状态允许、与标准语义匹配
```

写入仍只走 `EvidenceSink`。阶段 A 的验收页只做**可读对照**；阶段 B 起对照不过线不能落 `resultAcceptance`。

---

## 8. 当前决策与历史沿革

| 议题 | 默认 | 状态 |
|------|------|------|
| 产品面称谓 | 只说任务，不说会话 | 已锁 |
| 主壳 | 当前项目代理壳；原型 A 保留历史/经典入口 | F 已落地，RC 收敛；GA 未完成 |
| 工作台 | 行动权雷达，非唯一入口、非默认落地 → 阶段 F 不再是页面，职责落到机器人列表与档案（ADR 84） | F 已落地，RC 收敛 |
| 项目代理 | 每个项目一个；只读 + 调度；任务由它开出；用户可介入任务 | F 已落地，原决策 2026-09-24 |
| 模式切换器 | 仅 Agent / Plan → 阶段 F 从代理输入框退场，由代理判断是否先批计划 | 项目代理输入框已退场；经典入口按兼容保留 |
| 计划完成 | 禁止 UI 手勾，Evidence 聚合 | 保持 |
| 待验收入口 | 查看进度，看过再确认归档 → 阶段 F：验证归代理，低风险验证通过的由策略代签（`acceptedBy: 'policy'`），只有例外进「需要你确认」；依据按需展开 | F 已落地，RC 收敛（ADR 80 决策 8） |
| 关闭闸门 | 成功标准都有可解析证据才写 `resultAcceptance` | 已交付 B |
| 成功标准 | 待批准时可编辑 | 已交付 B |
| 验收默认合入 | 当前 Workspace `baseBranch` | 已交付 C |
| 自动 worktree | 经典入口按 D；项目代理并行任务按 F 和当前调度契约，不继承旧“始终不默认”表述 | 已有实现，按场景保持隔离 |
| 能力热替换 | 注册层 `replace`，不重建 Runtime | 已交付 E |
| 证据导出 | 只打包已承认 refs | 已交付 E |
| 证据密码学 | 后置 | 保持 |
| Cordis | 先能力层，不整核替换 | 保持 |

与壳层决策冲突的需求，先改本文决策表，再改代码。与理念、人群、品类、主轴冲突的需求，先改 `peer-product-alignment.md`。

---

## 9. 文档使用

产品理念、人群、品类、价值点和委托链路以 `design/product/peer-product-alignment.md` 为准。本文只锁当前壳层与改造阶段。近/中/远景与部署面排期见 `design/product/peer-product-roadmap.md`。

本文是壳层总纲，不是执行卡。当前工作包统一见 [改造计划](peer-product-renovation-plan.md)；拆卡时明确用户目标、事实源、状态、输入/焦点/滚动控制、恢复和共享组件，涉及边界先按 A/B 分级。文档与普通实现不自动触发测试，发布统一门禁。

`peer-2-0-workbench-flow.md` 与原型 A 的入口是历史。新壳默认当前项目代理对话，列表上的需要你回到同一原任务/当前决定，验证与 Evidence 按需打开。不能用旧工作台页或“所有结果人工验收”覆盖现行委托链。
