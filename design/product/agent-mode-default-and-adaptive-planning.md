# Agent 默认模式重构：自适应规划（L0–L3）

> 创建时间：2026-07-28
> 最后更新：2026-07-28
> 状态：设计定稿（待实现）— 产品方案 **A**：默认模式正名为 **Agent**，执行哲学对齐现有 Goal 自驱闭环，并引入任务复杂度分级规划
> 关联代码仓：`peer_agent`（本知识库只存知识，代码改动一律在该仓落地）
> 关联文档：
> - `design/product/goal-mode-ultrathink-workflow.md`（Goal 自驱闭环、DoD-as-Code、hooks、Runner）
> - `knowledge/decisions/41-rename-goal-mode-to-plan-mode.md`（Goal→Plan 正名与执行段合一）
> - `knowledge/specifications/15-goal-plan-lifecycle-governance.md`（防僵尸计划）
> - `knowledge/specifications/engineering-rigor-paradigm.md`（工程严谨范式与落地闸门）
> - `knowledge/architecture/00-engineering-philosophy.md`（本地优先 / 证据优先总哲学）

---

## 一、背景与动机

### 1.1 用户体感问题

对比 Codex 类代理时，Peer 常被感知为：

1. **默认入口太松**：`chat` 可直接动手，不强制问题重写、根因诊断、可验证完成标准。
2. **能力其实已有，但默认没用上**：`goal` 已具备 `explore → plan → act → verify`、GoalPlan、证据完成门、弱 DoD 告警。
3. **命名与心智错位**：用户要的是「自动规划并执行的 agent」，不是「先闲聊的 chat」；`goal` 名字又偏产品内部术语。
4. **一刀切风险**：若所有任务都走完整 GoalPlan 面板，小改与问答会被过度工程化，并放大僵尸计划噪音。

### 1.2 设计结论（一句话）

> **默认模式改为 Agent：以 Goal 的自驱执行哲学为内核，以 Chat 的低摩擦为入口体验，按任务复杂度在 L0–L3 自适应规划深度；Plan 模式保留为显式人审刹车。**

不是把 `chat` 和 `goal` 粗暴合并成一个无差别大模式，而是：

- **产品层**只暴露清晰的 Agent / Plan（Ask 可选二期）
- **运行层**复用现有 goal runner / plan store / gates
- **策略层**增加诊断门闸 + 规划深度路由

---

## 二、产品定义

### 2.1 用户可见模式

| 模式 | 一句话 | 何时用 |
| --- | --- | --- |
| **Agent（默认）** | 自动规划并执行；必要时才打断你 | 日常开发、修复、实现、排查 |
| **Plan** | 先出正式计划，你批准后再动 | 高风险、大范围、需要共审方案 |
| **Ask（可选二期）** | 只读问答，不改环境 | 纯咨询、代码解释、方案探讨且禁止副作用 |

### 2.2 Agent 的正式定义

> **Agent 模式：默认自动规划并执行的工程代理。**  
> 小任务直接做；中任务自动建立脚手架计划并自驱推进；大/高风险任务升级为可审批计划。  
> 完成以证据与成功标准为准，不以口头宣称。

### 2.3 Plan 的正式定义

> **Plan 模式：显式人机共审模式。**  
> 任何副作用执行前必须先有用户批准的正式计划；批准后的执行段可与 Agent/Goal 共用 Runner。

### 2.4 与现状三模式映射

| 现状 wire / 心智 | 重构后 |
| --- | --- |
| `chat`（默认自由执行） | **退役为兼容别名** → 行为升级为 Agent；UI 默认显示 Agent |
| `goal`（自驱目标闭环） | **并入 Agent 的 L2（及部分 L1/L3 升级）内核**；wire 可短期保留 `goal` 作为 Agent profile，或迁移为 `agent` |
| `plan`（先批再做） | **保留**，语义不变 |

> 实现阶段 wire 字面量迁移策略见第十章；产品文档与 UI 文案以 **Agent / Plan** 为准。

---

## 三、核心机制：自适应规划深度（L0–L3）

### 3.1 为什么要分级

| 只做「永远无计划 chat」 | 只做「永远完整 goal 计划」 |
| --- | --- |
| 缺根因、缺 DoD、用户当 QA | 小任务过重、面板噪音、创建成本高 |
| 像助手，不像代理 | 像流程引擎，不像顺手工具 |

分级目标：

1. **顺滑**：简单事不啰嗦  
2. **严谨**：复杂事不跳诊断与验收  
3. **可治理**：计划生命周期仍受现有 store / gate 约束  

### 3.2 四级定义

| 级别 | 名称 | 触发（启发式） | 计划形态 | 是否进右侧正式计划面板 | 是否等人批准 | 完成标准 |
| --- | --- | --- | --- | --- | --- | --- |
| **L0** | Direct | 纯问答、解释、只读查阅、无副作用 | 无 | 否 | 否 | 答对即可 |
| **L1** | Micro-plan | 单点低风险修改、范围清晰、1–2 文件级 | **会话内短计划**（3–6 步，可 ephemeral） | 默认否（可折叠摘要） | 否 | 轻量自检 + 必要 evidence |
| **L2** | Auto Goal | 多步骤功能/修复、跨文件、需闭环验证 | **正式 GoalPlan 脚手架** | 是 | **否**（自驱） | successCriteria + evidence + 现有完成门 |
| **L3** | Gated Plan | 高风险、需求模糊需关键决策、大范围重构、不可逆操作 | **正式 Plan** | 是 | **是** | 批准后执行 + 同 L2 验证 |

### 3.3 路由规则（产品契约）

Agent 在动手前必须做一次 **深度判定**（可在第一轮工具探索后修正上/降级）：

```text
if 无副作用且纯信息任务:
  L0
elif 高风险写盘 / 不可逆 / 权限敏感 / 用户显式要求先审:
  L3
elif 需求关键分叉未收敛（缺选型且会显著改实现）:
  先 request_user_input；仍大范围未知 → L3
elif 多步骤或需可验证成功标准或跨模块:
  L2
else:
  L1
```

#### 强制升级（L1 → L2/L3）

- 发现影响面大于最初估计（模块边界、协议、数据迁移）
- 需要持续多 turn 的 verify/adjust
- 出现平台资源管线 / 性能 / 状态机类「症状背后是系统问题」
- 用户说「太糊/不对/不准」第二次仍未关闭 → 至少升到 L2，并触发诊断门（见范式文档）

#### 强制降级（L2 → L1/L0）

- 目标已收敛为单点确认或纯解释
- 计划任务被证明过度拆分且无独立验收价值

#### 禁止项

- L0/L1 **禁止**为「显得专业」强行创建完整 GoalPlan
- L2 **禁止**跳过 successCriteria 空壳建计划
- 任意级别 **禁止**在已有活跃执行计划时无故新建并行计划（遵守生命周期治理）

### 3.4 与 Codex 行为的对齐点

| Codex 体感 | Peer Agent 对应 |
| --- | --- |
| 自动形成执行序列 | L1 micro-plan / L2 GoalPlan |
| 不没事就问 | 最少打扰；仅缺关键决策/高风险时打断 |
| 边做边用工具证据校正 | act → verify → adjust；evidence 完成门 |
| 卡住才打断 | no-progress / 升级 L3 / request_user_input |

---

## 四、诊断门闸（Diagnosis Gate）与工程严谨嵌入

Agent 不是「会跑工具的 chat」，必须嵌入工程严谨范式（详见 `engineering-rigor-paradigm.md`）。

### 4.1 何时强制诊断门

以下任务在 **首次副作用前** 必须产出诊断块（可写在 micro-plan 或 GoalPlan 元数据中）：

- 用户描述为症状（糊、慢、不准、偶发、坏了）
- 涉及像素/图标/托盘/菜单栏等平台呈现
- 涉及性能、启动路径、占用口径、状态同步
- 任何 L2/L3 的 bugfix / 回归

### 4.2 诊断块最小字段

```text
problem_rewrite:  系统语言重写后的真正问题
constraints:      平台/产品/工程/验收约束
root_cause_hypotheses: 主假设 + 可证伪点（L1 可简写）
source_of_truth:  改完后唯一真相源是什么
causal_chain:     将修改的链路节点（资源/加载/状态/打包/测试…）
success_checks:   如何证明修好（命令/预览/日志/测试）
non_goals:        明确不做的症状疗法
```

### 4.3 与 brainstorming / design-before-implementation 的关系

| 机制 | 作用 |
| --- | --- |
| Brainstorming source | 非平凡「建设/新行为」先对齐设计 |
| Diagnosis Gate | 非平凡「症状/修复/质量」先对齐根因 |
| Adaptive L0–L3 | 决定计划重量与是否人审 |

三者叠加顺序：

```text
接收任务
  → 判定 L0–L3
  → 若建设型非平凡：brainstorming / 设计批准
  → 若症状型非平凡：diagnosis gate
  → 再建 plan / 执行
```

---

## 五、计划形态与生命周期

### 5.1 L1 Micro-plan（轻计划）

**目的**：给模型与用户一个短导航，不制造面板债务。

建议内容：

1. 目标一句话  
2. 步骤 3–6 条  
3. 自检方式 1–3 条  
4. 风险/不做项（可选）  

存储建议：

- **默认**：会话内结构化短记录（可挂 turn metadata / 不进 goal-plans 重列表）
- **升级 L2 时**：再物化为正式 GoalPlan，并 supersede 轻计划

### 5.2 L2 Auto Goal（正式脚手架）

复用现有：

- `goal_create_plan` / `goal_update_task` / `goal_set_active_plan`
- goal-mode-gate / intake convergence
- DoD-as-Code successCriteria
- Runner + explorer 能力（既有设计）

增强（与范式对齐，实现可分期）：

- 计划元数据增加 `diagnosis`（可选但 bugfix 强制）
- `tasks` 尽量映射因果链，而非纯文件清单
- 弱 DoD 时阻断「宣称完成」

### 5.3 L3 Gated Plan

复用现有 Plan 模式：

- 正式计划 + `awaiting_approval`
- 批准后执行段与 Goal/Agent 共用 Runner（ADR 41 B2-b）

Agent 路由到 L3 时的 UX：

- 明确提示：「该任务风险/不确定性较高，已切换为需你批准的计划」
- 用户也可在 Agent 中显式说「先出计划让我批」强制 L3

### 5.4 防僵尸计划（硬约束）

继续遵守并强化 `15-goal-plan-lifecycle-governance.md`：

1. 同会话新计划默认 supersede 旧 awaiting/executing 草稿  
2. 微调方案 ≠ 新开计划  
3. 完成/取消必须收尾 status  
4. L1 不进重列表，从根源减少噪音  

---

## 六、模式闸门与工具策略

### 6.1 权限与副作用

| 级别 | 读 | 写 | 高风险写 | 网络 |
| --- | --- | --- | --- | --- |
| L0 | ✅ | ❌（默认） | ❌ | 按需只读 |
| L1 | ✅ | ✅ 小范围 | 触发升级或确认 | 按策略 |
| L2 | ✅ | ✅ | hooks 守卫 + 必要时确认 | 按策略 |
| L3 | ✅ | 批准后 ✅ | 同现有 plan/goal hooks | 按策略 |

> 不发明第二套权限系统；复用 high-risk write scope 与 goal hooks。

### 6.2 最少打扰策略（Agent）

允许打断的唯一正当理由：

1. 缺关键产品/技术决策且无法安全默认  
2. 高风险 / 不可逆  
3. 验证失败且自动调整耗尽  
4. 需要用户本地感知确认（且 Agent 已做完可做的自检）  

禁止：

- 把本可自检的视觉/日志验收甩给用户当第一步  
- 每一步都问「是否继续」  

### 6.3 与 mode-copy / system-context 的关系

实现时需更新：

- `packages/system-context` 的 mode copy / mode source  
- brainstorming 与（新建）diagnosis / adaptive-planning source  
- runtime reminder：当前为 Agent，以及当前估计深度 Lx  
- Desktop UI 模式切换文案与默认模式  

Prompt 层原则：

> **Agent = Goal 执行哲学 + 自适应深度 + 诊断门；不是旧 chat 文案换皮。**

---

## 七、UX 与信息架构

### 7.1 模式切换器

- 默认选中 **Agent**
- 次要：**Plan**
- （可选）Ask

历史会话：

- wire `chat` → 显示为 Agent（兼容）
- wire `goal` → 显示为 Agent（自驱中/历史）
- wire `plan` → Plan

### 7.2 右侧计划面板

| 深度 | 面板 |
| --- | --- |
| L0 | 不出现计划 |
| L1 | 默认不占重面板；可在时间线显示「本轮步骤」短卡片 |
| L2 | 现有 Goal 计划面板 + 进度/证据 |
| L3 | 现有 Plan 审批面板 → 批准后同执行面板 |

### 7.3 用户可见的「自动规划」表达

Agent 开场推荐结构：

1. **我把它理解为…**（problem rewrite，非复读）  
2. **深度：L1/L2/L3**（一句话原因）  
3. **计划/步骤**  
4. **开始执行 / 请批准**  

避免：

- 「我先随便改改你看看」  
- 无深度说明就创建巨型计划  

---

## 八、成功标准（本设计本身的 DoD）

本重构落地完成后，应满足：

1. **默认模式**在 UI 与文案上为 Agent，不再引导用户「日常请用 chat 随便做」。  
2. 多步骤任务在 Agent 下会 **自动**出现 L1 或 L2 计划，无需用户先手动切 goal。  
3. 纯问答不产生正式 GoalPlan 噪音。  
4. 症状类修复在首次副作用前出现诊断字段或等价输出。  
5. 高风险路径仍可进入 L3 人审，不弱化 Plan。  
6. 计划生命周期指标不恶化（僵尸 executing 不回升）。  
7. 与现有 Goal ultrathink 设计兼容：L2 复用 runner/DoD/hooks，而不是平行实现第二套自驱引擎。  

---

## 九、非目标（YAGNI）

本设计 **不**包含：

1. 重做整个 Agent 循环协议  
2. 立刻删除 wire 历史值而不做兼容  
3. 让所有 L1 都上重面板  
4. 用「更强模型」替代流程闸门  
5. 一次实现完整 Ask 模式（可二期）  
6. 多 Agent 编排大一统（另见 multi-agent 文档）  

---

## 十、实现分期（代码仓落地指引）

> 以下为设计层分期，供后续 goal/plan 实现时拆 PR；**本仓库不写代码**。

### Phase 0 — 文档与契约（本知识库）

- [x] 本文（产品/机制）
- [x] `engineering-rigor-paradigm.md`（思维 + 闸门清单）
- [ ] 实现前补 ADR（建议：`59-agent-as-default-mode.md`）确认 wire 策略

### Phase 1 — Prompt / 产品语义（低风险）

1. UI 默认模式文案：Agent  
2. `MODE_COPY`：Agent 采用 goal 哲学 + L0–L3 路由说明  
3. chat 兼容：行为切换为 Agent 策略（可仍 wire=`chat` 短期）  
4. 注入 diagnosis gate 与 adaptive planning 规则源  

### Phase 2 — 深度路由可观察化

1. turn/plan 元数据记录 `planningDepth: L0|L1|L2|L3`  
2. L2 自动 `goal_create_plan`（Agent 内）  
3. L3 自动转 plan 审批流或强制 approval gate  
4. 生命周期 supersede 规则覆盖自动创建路径  

### Phase 3 — 轻计划与面板

1. L1 micro-plan 存储与时间线短卡片  
2. L1→L2 物化  
3. 弱 DoD / 缺诊断的质量门（bugfix）  

### Phase 4 — Wire 清理（可选）

1. 新 wire `agent`  
2. `chat`/`goal` 读路径兼容映射  
3. 文档与测试全量更名  

---

## 十一、风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 自动 L2 导致计划爆炸 | 严格 L0/L1 条件；supersede；禁止重复建计划 |
| Agent 太主动乱改 | 保留 high-risk hooks；关键决策打断；L3 升级 |
| 与旧 chat 用户习惯冲突 | 默认 Agent 但 L0 仍「像聊天」；设置可记最后模式 |
| Prompt 变长 | L0–L3 规则模块化 source，按模式投影 |
| goal/plan/agent 三套逻辑分叉 | 单一 Runner + 单一 plan store；模式只改「是否批准 / 深度」 |

---

## 十二、与既有文档的关系

| 文档 | 关系 |
| --- | --- |
| `goal-mode-ultrathink-workflow.md` | **L2 内核规范**；本文不重复状态机细节，只定义何时进入 |
| ADR 41 | Plan 正名与执行段合一仍有效；本文解决 **默认入口与 chat 空洞** |
| `15-goal-plan-lifecycle-governance.md` | 自动建计划后更重要，必须遵守 |
| `engineering-rigor-paradigm.md` | 诊断门、证据闭环、DoD 的内容标准 |
| `00-engineering-philosophy.md` | 本地优先/证据优先的总原则；本文是模式层落地 |

---

## 十三、决策记录（设计过程摘要）

1. **采用方案 A**：默认模式正名为 Agent，而不是保留 Chat 名换心智。  
2. **保留 Plan**：人审刹车不可吞进 Agent 的无级别自动执行。  
3. **必须 L0–L3**：反对「全部完整 GoalPlan」与「继续无结构 chat」两种极端。  
4. **先文档后代码**：本篇与工程严谨范式文档构成实现前置契约。  
5. **复用 Goal 基础设施**：不平行发明第二套自驱引擎。  

---

## 十四、开放问题（实现前需在 ADR 收口）

1. wire 字面量：短期 `chat` 行为升级 vs 直接引入 `agent`？  
2. L1 micro-plan 是否落盘到 `goal-plans` 的轻量类型，还是纯会话 metadata？  
3. 用户是否允许设置「Agent 永远先 L3 审批」的保守档？  
4. Ask 模式是否进入第一期 UI？  

> 建议默认实现倾向：Phase 1 用 `chat` wire 承载 Agent 行为 + UI 改名；L1 用会话 metadata；保守档可做设置项；Ask 二期。
