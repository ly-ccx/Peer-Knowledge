# Peer 改造总纲

创建时间：2026-08-22
最后更新：2026-08-22（阶段 E 已在代码仓落地开发体验与可嵌入）

> 版本：v2  
> 状态：产品与架构改造真源（草案 v1 已吸收；阶段 A 已在代码仓交付）  
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
> - `design/product/peer-2-0-product-system.md`（更早的 2.0 战略总纲，本文件管当前改造镜头）  
> - `design/product/peer-2-0-workbench-flow.md`（工作台分桶；壳层以本文为准）  
> - `design/product/task-identity-conversation-carrier.md`（产品面说任务，存储主键仍是 conversation）  
> - `knowledge/architecture/task-lifecycle-and-acceptance-flow.md`（副作用必须先有 GoalPlan）

前身是本机草案 v1（2026-08-22）。v2 写入本仓后，以本文为准。

---

## 0. 一句话方向

Peer 不是又一个「左边项目、下面挂会话」的 Agent 桌面。

**任务仍是深度工作的家；工作台是跨任务的行动权雷达；Plan 从讨论里长出来；完成必须你对照证据签收；有副作用的任务线可以绑到从 Workspace 源头拉出的 Git 子分支。**

产品面只说**任务**。代码里的 `conversation` 可以继续当实现名，用户看见的一律是任务。

三拍叙事贯穿一切：

> 目标带着边界被签收 → 能力在授权下执行 → 完成用证据关闭。

壳层已锁定为**原型 A：任务壳 + 工作台雷达**。不要做成工单台（原型 B），也不要用顶栏雷达替代独立工作台页（原型 C 可偷计数，不能替代页面）。

---

## 1. 定位与竞争力（不改的主线）

### 1.1 我们优化什么

多数桌面 Agent 优化的是关系连续性，或「能在本地跑工具」。Peer 额外优化：

- **责任与注意力**：现在该处理什么（需要你 / 推进中 / 待验收）
- **完成的可证明性**：Done 是闸门，不是模型口头完成
- **本地权力的可审计性**：Manifest → Projection → PermissionGrant → Evidence

### 1.2 守住的竞争力

1. Task Flow，而不是 Tool Chat
2. Evidence 一等公民（摘要 ≠ 证明）
3. 一条受治理能力链
4. 完全开源 + 可嵌入的同一套 runtime 真值

### 1.3 现阶段不作为主叙事

与 DSH 比插件热度、与 Pi 比极简、与 Claude Code / Codex 比写代码爽感、跨设备云同步密钥。热拔插和自我迭代是手段，用来把治理闭环做稳。

加能力只问一句：它是在强化「任务被正确签收、正确授权、正确证明」，还是只是多干一件事？

---

## 2. 双层心智（产品哲学）

| 层 | 职责 | 用户感受 |
|----|------|----------|
| **任务** | 深度、记忆、讨论、派生 Plan、执行现场 | 「我在这条工作线里继续」 |
| **工作台** | 跨任务聚合行动权：需要你、待验收 | 「现在有什么要我处理」 |
| **Workspace** | 项目边界、源头主开发分支、数据与权限家园 | 「这个仓库当前从哪分叉」 |

必须遵守：

1. 任务是家，工作台不是唯一入口，也不是默认落地页。
2. 从雷达点进去，必须落到原来的任务 + Plan，禁止另起无历史工单页。
3. 轻量问答不必进待验收；有副作用、有成功标准的 Goal/Plan 才进。
4. 点工作区只激活新任务落点，不把人从当前任务赶走。

---

## 3. 目标信息架构（原型 A）

```text
左侧：工作台（需要你 N · 待验收 M）
      Workspace 列表（默认可折叠）
        └─ 该区下的任务树

主区默认：当前任务（ChatSurface）
        └─ 空态：发出任务 / 继续这条任务

工作台页：只回答「现在需要你做什么」
        ├─ 需要你
        ├─ 待验收（先看依据 → 标准 × 证据）
        └─ 弱化：推进中、工作区脉搏

Drawer：全部任务 / 历史 / 验收对照
验收抽屉：对照标准为主；可打开产物为辅；页脚退回补充 / 确认验收
```

打开 App 的第一眼：**保留任务为主壳**。侧栏工作台常驻计数。第一期不因有待办就把默认落地改成工作台。

---

## 4. 主路径

```text
进入 Workspace
  → 新任务 或 继续长任务
  → 讨论中形成目标
  → 派生 GoalPlan（Plan 模式必经批准；Agent 模式按复杂度升级）
  → 用户批准计划（签收近亲）
  → 若将产生仓库副作用：绑定子分支 / 可选 Worktree
  → 授权下执行
  → 卡住则结构化追问
  → 质量自检（如有代码副作用）
  → result_ready → 工作台待验收
  → 对照成功标准与证据验收
  → 关闭；可选合并子分支回目标分支
```

规划深度 L0–L3 是运行时深度，产品切换器仍只暴露 Agent / Plan。L0 不进待验收。

---

## 5. 阶段与交付

每个阶段仍用同一句验收：用户是否更难「口头完成」、更容易「带着证据关掉一条工作线」？

### 阶段 A · 可见的治理闭环 — **已交付（2026-08-22，`peer_agent` `0.0.6`）**

产品第一优先。代码已落地，不改 protocol、不改 Git 闸门。

已交付：

- 侧栏工作台常驻 `需要你 N · 待验收 M`（排除 `source === 'conversation'` 的轻量问答）
- Workspace 下挂任务树；默认只展开当前区或当前任务所在区，其余折叠
- 点工作区只激活落点，不跳走；点任务进主区任务
- 任务列表后台续页，不再露出「加载更多」
- `result_ready` 先打开验收抽屉；页脚「退回补充 / 确认验收」
- 验收页只对照标准 × 证据，外加可打开产物与交卷前自检；不再摊进度、子任务、整段对话
- 工作台卡主按钮是「先看依据」，确认验收只出现在看过依据之后
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
- 验收页增加授权摘要与依据时间线（授权 / 工具 / 产物 / 拒绝）
- 对照不过线时禁用「确认验收」，并说明缺哪类依据

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
- Evidence 导出只打包已承认的 refs 与索引记录；验收页「导出依据」由 main 选路径写 JSON
- `examples/external-host` 演示 Provider 热替换 + 导出文档，不依赖 Desktop / CLI

未纳入 E：插件市场热加载、把产物文件打成 zip、密码学证据链、默认对所有任务建 worktree

---

## 6. Git 工作线（阶段 C / D）

| 议题 | 默认 |
|------|------|
| 默认合入 | 验收时的当前 Workspace `baseBranch` |
| 创建时源头 | 对比基线与说明，不是默认合入目标 |
| 自动 worktree | 不默认；批准后或用户声明隔离时 |
| 切换源头 | 只影响之后新建任务线 |
| 拒收 / 取消 | 停 runner；删除 worktree / 分支要二次确认 |

UI 最小露出（C / D 已交付）：Workspace 主开发分支下拉；任务行 `feat/… · from develop`；待验收卡展示 diff 与建议合入分支；任务卡可「隔离执行 / 打开现场 / 删除这条线」。

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

## 8. 决策记录

| 议题 | 默认 | 状态 |
|------|------|------|
| 产品面称谓 | 只说任务，不说会话 | 已锁 |
| 主壳 | 原型 A：任务壳 + 工作台雷达 | 已锁并交付 A |
| 工作台 | 行动权雷达，非唯一入口、非默认落地 | 已锁并交付 A |
| 模式切换器 | 仅 Agent / Plan | 保持 |
| 计划完成 | 禁止 UI 手勾，Evidence 聚合 | 保持 |
| 待验收入口 | 先看依据，看过再确认验收 | 已交付 A |
| 关闭闸门 | 成功标准都有可解析证据才写 `resultAcceptance` | 已交付 B |
| 成功标准 | 待批准时可编辑 | 已交付 B |
| 验收默认合入 | 当前 Workspace `baseBranch` | 已交付 C |
| 自动 worktree | 不默认；用户声明隔离时挂到已有任务线 | 已交付 D |
| 能力热替换 | 注册层 `replace`，不重建 Runtime | 已交付 E |
| 证据导出 | 只打包已承认 refs | 已交付 E |
| 证据密码学 | 后置 | 保持 |
| Cordis | 先能力层，不整核替换 | 保持 |

与本文冲突的需求，先改本文决策表，再改代码。

---

## 9. 文档使用

本文是改造总纲，不是 sprint 票。拆票时写清：改的是任务壳、工作台、Plan 闸门、证据，还是 Git 线；是否触碰三条证据不变量；是否改变「任务是家」。

`peer-2-0-workbench-flow.md` 里「工作台是唯一主入口 / 继续讨论用会话抽屉」已被本文与阶段 A 覆盖：主区默认当前任务，从雷达点 `result_ready` 进验收抽屉，其余进原任务。
