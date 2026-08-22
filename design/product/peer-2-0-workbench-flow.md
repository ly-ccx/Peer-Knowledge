# Peer 2.0 工作台完整动线与语义

> 创建时间：2026-08-08  
> 最后更新：2026-08-22（壳层以改造总纲为准；本文仍管分桶与行动权投影）  
> 文档状态：**分桶 / 行动权投影真源；壳层目标态已被覆盖**  
> 适用范围：Desktop 工作台（TaskOverview）、任务抽屉、历史抽屉、GoalPlan / Automation 行动权投影  
> 关联代码仓：`peer_agent`  
> 关联文档：  
> - `design/product/peer-transformation-charter.md`（**当前改造总纲 v2**：任务是家，工作台是雷达）  
> - `knowledge/decisions/67-task-shell-workbench-radar.md`（原型 A 锁定）  
> - `design/product/first-run-onboarding-guidance.md`（首启主路径是空任务，不是工作台）  
> - `design/product/peer-2-0-product-system.md`（更早的 2.0 战略总纲）  
> - `design/product/peer-2-0-gap-analysis.md`（Gap 与 §11 映射契约）  
> - `design/visual/previews/peer-2-0/`（高保真原型）  
> - `design/product/task-identity-conversation-carrier.md`（身份层：打开的是任务现场，主键仍是 conversationId）

> **2026-08-22 覆盖说明：** 下列目标态已作废，以总纲与 ADR 67 为准——「工作台是唯一主入口」「继续讨论用会话抽屉、不切主区」「结果抽屉只读可选」。阶段 A 已交付：主区默认当前任务；从雷达点 `result_ready` 进验收对照抽屉，其余进原任务；点工作区只激活落点。本文 §2.1 / §14 的会话抽屉目标态不要再当实现合同。分桶（需要你 / 待验收）与 `actionRight` 投影仍以本文为准。

---

## 0. 文档目的

这份文档回答一件事：

> **工作台上每一块区域、每一个入口、每一次点击，应该对应什么语义？现在实际是什么？差在哪里？**

它不是愿望清单，也不是实现笔记堆。它是：

1. **导航 / 分桶 / 验收 / 历史** 的产品语义真源  
2. 后续改 UI 与聚合层时的 **验收标准**  
3. 解释当前「混乱感」的 **因果链**（文案、过滤、投影、持久化各卡在哪）

约定标记：

- **【目标态】**：产品应对齐的语义（以本文件为准）  
- **【现状】**：代码仓当前真实行为  
- **【缺口】**：目标态 − 现状，需改实现或补协议

---

## 1. 一句话定位

| 对象 | 一句话 |
|---|---|
| **工作台** | 不是任务仓库，而是「下一步行动权」的动态投影：**只处理真正需要你的事** |
| **任务抽屉** | 当前 Workspace 下**未结束**的工作清单（含推进中、待你处理、待验收） |
| **历史抽屉** | **已结束且不再需要验收**的记录（已验收 / 取消 / 失败等） |
| **会话抽屉** | 从工作台 / 任务 / 历史 / 结果视图「继续讨论」时浮出的会话现场；**可关闭**，不把主区硬切成 Chat |
| **会话 + Goal 面板** | 单任务现场：决策、执行、验收动作的发生地（可出现在主区，也可出现在会话抽屉内） |

产品口号（与总纲一致）：

> 把工作交给 Peer，只在真正需要你的时候回来。

---

## 2. 信息架构（IA）

### 2.1 【目标态】导航

> 壳层目标态已迁到 `peer-transformation-charter.md`。下面这段是 2026-08-15 旧稿，**不再作为实现合同**。

```
侧栏（一级）
 └─ 工作台                    ← （旧）唯一主入口（Delegation OS 首页）
      ├─ 需要你处理
      ├─ Peer 正在推进
      └─ 结果待验收
           ├─ 确认验收         → 工作台一键确认（落库 accepted → terminal）
           ├─ 查看结果         → 结果抽屉（只读，可选）
           ├─ 继续讨论         → 会话抽屉（可关闭，绑定原 conversationId）
           ├─ 查看全部任务 →   → 任务抽屉
           └─ 查看历史 →       → 历史抽屉

侧栏不出现「任务 / 历史」一级 tab
Canvas / Result / Automation 中心不抢工作台主轴
继续讨论不跳主 Chat，用会话 Drawer 浮层
零任务时工作台给首启让路：只保留一个「发起任务」入口，不讲 0/0/0
首启教育落在空会话，工作台仍是日常 Delegation OS 主入口
```

### 2.2 【现状】导航

| 点 | 现状 |
|---|---|
| 侧栏 | 仅「工作台」一级入口（任务/历史已从侧栏移除） |
| 任务 / 历史 | 由工作台链接打开 **Drawer**（`collectionDrawer: 'tasks' \| 'history'`） |
| 卡片点击 / 继续任务 | 有 `conversationId` → 关抽屉、切主区会话（【缺口】目标态应为会话抽屉） |
| 关闭抽屉 | 必须走 `requestClose`，保留退场动画 |

### 2.3 非目标（明确不做）

- 工作台做成「全部 GoalPlan 仓库」或仪表盘卡片墙  
- 侧栏恢复「工作台 + 任务 + 历史」三个一级 tab  
- 前端二次解析 GoalPlanStatus / Runner 状态机（只消费 `TaskOverviewItem.actionRight`）  
- 用会话名 / `goal` 全文代替 plan 名做卡片主标题  

---

## 3. 行动权（Action Right）——唯一主轴

### 3.1 五态

与 Gap §11 / 协议 `TaskActionRight` 一致：

| actionRight | 用户语义 | 工作台呈现 |
|---|---|---|
| `needs_you` | 决策 / 权限 / 阻塞，**你必须出手** | 「需要你处理」 |
| `peer_advancing` | Peer 在推进，你可盯可不盯 | 「Peer 正在推进」 |
| `result_ready` | 结果已出，**等你验收** | 「结果待验收」 |
| `paused` | 暂停（可进任务表筛选） | 任务抽屉 / 筛选 |
| `terminal` | 真正结束，**不进工作台主轴** | 历史抽屉 |

### 3.2 GoalPlan → 行动权（协议投影，判定顺序自上而下）

| 条件 | actionRight | nextAction（示意） |
|---|---|---|
| cancelled / failed | `terminal` | — |
| completed **且已验收** | `terminal` | — |
| completed **且未验收** | `result_ready` | `review_result` |
| blocked / 需决策 | `needs_you` | `decide_blocked` / `approve_plan` … |
| paused | `paused` | `resume` |
| executing / accepted / approved 等推进中 | `peer_advancing` | — |

> **关键分界**：`completed` 本身不等于历史。  
> **未验收** → `result_ready`；**已验收** → `terminal`。

### 3.3 【现状】投影与聚合的关键事实

| 事实 | 代码位置（peer_agent） | 含义 |
|---|---|---|
| 展示名 = `plan.title` | `task-overview-aggregator.mjs` | 不用 `goal` 全文、不用会话名 |
| `accepted: false` 写死 | 同上 `toGoalSnapshot` | 过渡期：**没有真正的 USER ACCEPTANCE 字段** |
| completed 未验收 → `result_ready` | `packages/protocol/src/task-overview.ts` `projectGoalPlan` | 协议正确 |
| completed 已验收 → `terminal` | 同上 | 协议正确，但现状几乎达不到 |
| 工作台默认排除 cancelled/failed | `isGoalPlanInScope` | 历史终态不进工作台 |
| completed 进工作台 | 存量 vs 新完成 | **上线前 completed 祖父化为已结束**；**上线后**未确认 completed 进 `result_ready` |
| 验收状态 | `isPlanResultAccepted` | 显式 `resultAcceptance` **或** `updatedAt < RESULT_ACCEPTANCE_REQUIRED_SINCE` |
| 活跃任务 7 天窗 | `DEFAULT_ACTIVE_WITHIN_MS` | 推进中 / 待你处理 |
| 首页合计 limit 48 | `DEFAULT_HOME_LIMIT` | 总上限（三桶合计；result_ready 本身不单独限条） |

---

## 4. 三入口语义（必须对齐）

这是混乱的根源表。**以【目标态】列为准。**

| 入口 | 【目标态】收什么 | 【目标态】不收什么 | 【现状】 | 【缺口】 |
|---|---|---|---|---|
| **工作台** | 当前 WS：`needs_you` + `peer_advancing` + **上线后未确认** `result_ready`（不限条数） | `terminal`（已验收/存量祖父化/取消/失败）；他仓噪音 | 存量不进待验收 | 脏标题仍噪音 |
| **任务抽屉** | 未结束：`needs_you` / `peer_advancing` / `result_ready` / `paused` | `terminal` | `includeTerminal: false`，表内可含「等待验收」 | 与工作台第三桶职责重叠，需文案区分「清单 vs 投影」 |
| **历史抽屉** | `terminal`：已验收 completed + cancelled + failed（+ 将来 archived） | 未验收的 completed；推进中 | `includeTerminal: true` 拉数，但 UI **只渲染 `actionRight === 'terminal'`**；而聚合层 `accepted` 恒 false → completed 几乎全是 `result_ready` → **列表为空** | **P0 语义/实现双 bug** |

### 4.1 「查看历史」按钮的正确语义

| | 内容 |
|---|---|
| **【目标态】** | 打开**已结束记录**：你不再需要验收的东西 |
| **【不是】** | 「所有曾经 completed 的 plan 仓库（含未验收）」 |
| **【也不是】** | 「结果待验收的完整列表」——待验收在工作台第三桶 + 任务抽屉筛选 |

### 4.2 完成 → 验收 → 历史 状态机（产品）

```
进行中
  needs_you / peer_advancing / paused
        │
        ▼ plan 跑完（status = completed）
结果待验收
  actionRight = result_ready
  用户下一步 = 验收结果
        │
        ▼ 用户验收通过 / 明确归档
历史
  actionRight = terminal
  工作台不再展示
```

一句话：

- **工作台** = 现在要你管的（决策 + 验收）  
- **任务** = 所有未结束（含推进中与待验收清单）  
- **历史** = 已经结束且不需要再验收  

---

## 5. 端到端数据动线

```
GoalPlan / Automation Definition×Run
        │
        │  listPlanDetails + automations
        ▼
task-overview-aggregator
  · workspacePath 过滤
  · isGoalPlanInScope / isAutomationInScope
  · title = plan.title.trim() || planId
  · accepted = false（过渡期）
  · result_ready 短窗 + limit
        │
        │  snapshot
        ▼
protocol: projectGoalPlan / projectAutomationRun
  · 产出 TaskOverviewItem
  · actionRight / nextAction / actionLabel / conversationId …
        │
        │  IPC taskOverview:list / changed
        ▼
useTaskOverview(workspacePath, includeTerminal, …)
        │
        ├─ HomePage / TaskOverviewPage（工作台 hero 三桶）
        ├─ TasksPage（Active Tasks 表）
        └─ HistoryPage（Task History 列表，仅 terminal）
```

**前端纪律**：分桶与按钮只读 `TaskOverviewItem`，不解析底层状态机。

---

## 6. 工作台页面动线（UI）

### 6.1 区块结构（对齐原型精神）

```
topline     工作台 / 日期 · 当前 Workspace
hero        标题 + 说明 + 统计（待你处理 / Peer 推进 / 结果待验收）
section     需要你处理     交接行：任务 · 行动权 · 事由 · 主按钮
section     Peer 正在推进  双列工作卡 + 进度
section     结果待验收     卡片叠放（非表格墙）+ 「查看历史 →」
```

### 6.2 点击动线

| 用户操作 | 【目标态】 | 【现状】 |
|---|---|---|
| 决策 → / 处理阻塞 | 进会话 + 露出 Goal 决策 UI | 有 `conversationId` 则切会话 |
| 推进中卡片 | 可进会话查看进度 | 可点进会话 |
| **确认验收**（主按钮） | 工作台一键确认：落库 `resultAcceptance` → `accepted=true` → `terminal`，卡片离开待验收、进历史 | **目标实现**；副操作可「查看结果」进会话 |
| 查看结果 / 进会话 | 可选深链看证据，**不是**验收必经 | 有 `conversationId` 可跳 |
| 查看全部任务 → | 任务抽屉 | ✅ |
| 查看历史 → | 历史抽屉，见已结束项 | 抽屉打开但**常为空**（见 §7） |

### 6.3 标题字段

| | 规则 |
|---|---|
| **【目标态 / 现状读取】** | 卡片主标题 = **`GoalPlan.title`**（核对后的 plan 名） |
| 副文案 | 可用进度、workspace、相对时间；**不要**把 `goal` 全文当主标题 |
| 脏标题根因 | 创建时常 `title = draft.title \|\| goal`，用户原话写入 title → 看起来像「取错字段」，实为**写入侧**问题 |
| 后续可选 | 创建时生成短 title；展示层对无意义 title（`1`/`commit`）做降级策略（产品需另决策） |

---

## 7. 已知缺口与混乱因果链（P0）

### 7.1 历史空列表（用户已复现）

**现象**：点「查看历史」→「已完结的任务一条都没有」。

**因果链**：

1. HistoryPage 过滤：`item.actionRight === 'terminal'`  
2. 协议：`completed + accepted=false` → `result_ready`（不是 terminal）  
3. 聚合：`accepted: false` 恒写死，无 USER ACCEPTANCE 持久化  
4. 因此几乎所有 completed **永远进不了** History 列表  
5. cancelled/failed 若还受活跃窗口 / workspace / 数量影响，也可能很少  

**结论**：不是「没有完成过任务」，而是 **「完成」被永久锁在待验收语义，历史只认 terminal**。

### 7.2 验收无闭环

| 步骤 | 目标 | 现状 |
|---|---|---|
| plan completed | 进 result_ready | ✅（+ 36h 短窗） |
| 展示待验收 | 工作台第三桶 | ✅（卡片叠放，聚合 ≤3） |
| 用户点验收 | 持久 accepted / 归档 | ❌ 仅跳会话 |
| 离开待验收 | 不再出现在第三桶 | ❌ |
| 进入历史 | terminal 可见 | ❌ 见 7.1 |

### 7.3 文案与实现不一致

| 文案/用户心智 | 实现 |
|---|---|
| 查看历史 = 看做完的事 | 只看 terminal（已验收等） |
| 结果待验收 = 需要我点头的完成项 | completed 未验收，但无验收落库 |
| 任务表里的「等待验收」 | 与工作台第三桶同一 actionRight，双入口 |

### 7.4 限流叠限流（曾导致「有 3 个只显示 1 个」）

| 层 | 规则 |
|---|---|
| 聚合 | 36h + `DEFAULT_RESULT_READY_LIMIT = 3` |
| UI（已修） | 曾 `FEATURED_RESULT_READY_LIMIT = 1`，现已改为渲染全部聚合结果 |
| 角标 | 应等于**当前列表真实条数**（工作台第三桶 = 聚合返回的 result_ready 数） |

### 7.5 脏数据放大噪音

- 本地可有上千 completed plan  
- title 大量为用户原话 / `commit` / `测试一下`  
- 无验收闭环时，任何「completed 进待验收」策略都会在数量与观感上翻车 → 才引入 36h + limit 止血  

---

## 8. 目标态验收标准（Definition of Done for 动线）

改实现时用下列清单自检；**未满足不得宣称工作台动线完成**。

### 8.1 导航

- [ ] 侧栏只有工作台主入口；任务/历史仅 Drawer  
- [ ] 关闭 Drawer 有退场动画（requestClose）  

### 8.2 分桶

- [ ] 工作台三桶只消费 `actionRight`  
- [ ] `terminal` 不出现在工作台主列表  
- [ ] `result_ready` **不限条数、不限短窗**（凡未验收 completed 均展示；靠一键确认清空队列）  

### 8.3 标题

- [ ] 主标题读取 `GoalPlan.title`  
- [ ] 不与会话 title、goal 全文混用  

### 8.4 历史

- [ ] 历史抽屉非空条件：存在 cancelled/failed，**或** 已验收 completed  
- [ ] 用户能理解：未验收完成项在「结果待验收 / 任务」，不在历史  

### 8.5 验收闭环（最小版 = 产品已确认）

- [x] **工作台直接展示结果卡**（标题 + 进度摘要），无需先跳会话才能看到「做完了什么」  
- [x] **主按钮 = 一键确认**（不是「验收结果 →」跳会话）  
- [ ] 落库字段：`GoalPlan.resultAcceptance = { acceptedAt, acceptedBy: 'user' }`（经 `goalPlansRevise`）  
- [ ] 聚合层读取该字段 → 投影 `accepted: true` → `terminal`  
- [ ] 确认后：卡片立即离开「结果待验收」，历史抽屉可见  
- [ ] 副操作「查看结果」可选进会话；**不是**验收必经路径  
- [ ] 未点确认：不得仅因 completed 就进历史主列表（与 §4 一致）  

> **产品决策（2026-08-08 用户确认）**  
> 1. 最小闭环 = **直接看结果 + 一键确认**（工作台完成，不强制会话）  
> 2. **上线后**新完成项 `result_ready` 不限条数；靠确认清空  
> 3. **存量 completed 祖父化**：功能上线前（`RESULT_ACCEPTANCE_REQUIRED_SINCE`）一律视为已结束，**不进待验收、不让用户白点**  
> 4. Gap §11.5「completed 直接进历史」对**新完成**仍否决；对**存量**用祖父化等价为已结束

---

## 9. 与 Gap / 总纲的关系

| 文档 | 关系 |
|---|---|
| `peer-2-0-product-system.md` | 品类与原则；本文件是其 **Desktop 工作台切片** |
| `peer-2-0-gap-analysis.md` §11 | 行动权映射契约；本文件补 **入口语义 + 现状偏差 + 验收/历史分界** |
| 高保真 `design/visual/previews/peer-2-0/` | 视觉与信息架构参考；结果区为卡片式重点验收，不是无限列表墙 |
| 代码 `task-overview.ts` + aggregator + 三页 | 实现真源；与本文件冲突时：**先改代码或改本文件并记录决策**，禁止静默分叉 |

---

## 10. 推荐修复顺序（对齐后再动代码）

| 优先级 | 项 | 说明 |
|---|---|---|
| **P0** | 取消 result_ready 限流 | 去掉 36h / 最多 N 条；未验收 completed 全量进工作台 |
| **P0** | 一键确认落库 | `goalPlansRevise` 写 `resultAcceptance`；聚合读 accepted |
| **P0** | 确认后进历史 | `result_ready` → `terminal`；历史抽屉可见已验收项 |
| **P1** | 历史 cancelled/failed 可见 | 修正时间窗，勿误伤终态 |
| **P1** | 三入口文案 | 工作台 / 任务 / 历史副标题对齐 |
| **P2** | 创建侧短 title | 减少脏标题 |
| **P2** | Result Package | 真正的证据包与深验收 UI（总纲建设项） |

---

## 11. 术语表

| 术语 | 含义 |
|---|---|
| TaskOverview | 跨 GoalPlan/Automation 的行动权投影列表协议 |
| actionRight | 下一步谁行动：你 / Peer / 验收 / 暂停 / 终态 |
| result_ready | 结果已出、等待用户验收 |
| terminal | 已结束且不需要再验收（历史） |
| accepted（投影字段） | 是否完成 USER ACCEPTANCE；**不是** GoalPlanStatus 的 `accepted`（那是计划被接受执行） |
| GoalPlan.title | 计划名（卡片主标题） |
| GoalPlan.goal | 完整目标描述（详情，不当主标题） |
| 短窗 | completed 进入工作台待验收的时间窗口（现状 36h） |

> 命名碰撞警告：GoalPlanStatus 含 `accepted`（计划已接受、将执行），与投影字段 `accepted`（用户已验收结果）**不是同一概念**。文档与代码注释必须写全称语境。

---

## 12. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-08 | 首版：对照 product-system、gap §11、aggregator/protocol/三页实现，落库工作台完整动线与语义；记录历史空列表根因与验收闭环缺口 |
| 2026-08-08 | 产品确认：工作台一键确认 + `result_ready` 不限制；更新 IA/DoD/修复顺序与 §13 决策表 |
| 2026-08-08 | 存量祖父化：上线前 completed 不进待验收；仅上线后新完成项需一键确认（消白点队列） |
| 2026-08-08 | Automation 方案 A：succeeded → terminal，不进结果待验收；Goal 验收仅 goal_plan |
| 2026-08-10 | **继续讨论 = 会话 Drawer**：从工作台/任务/历史/结果续接时打开可关闭的会话抽屉，不再「关抽屉 + 跳主 Chat」；§14 重写打开/关闭/互斥/验收标准；文案优先「继续讨论」 |

---

## 13. 已确认的产品点（2026-08-08）

| # | 问题 | 结论 |
|---|---|---|
| 1 | 历史是否展示「仍未验收的 completed」？ | **否**。未验收只在「结果待验收」；已确认才进历史 |
| 2 | 验收最小闭环放哪？ | **工作台一键确认**；直接看到结果摘要，主按钮确认 |
| 3 | result_ready 是否限流？ | **上线后新完成项不限条数**；靠确认清空，不靠藏 |
| 4 | 历史海量 completed 怎么办？ | **存量祖父化**：`RESULT_ACCEPTANCE_REQUIRED_SINCE` 之前的 completed 视为已结束，**不进待验收、不让用户白点**；功能上线后的新完成才走一键确认 |
| 5 | Automation 成功 Run 要不要进待验收？ | **方案 A：不要**。`run succeeded` 默认 `terminal`（成功即归档）；不套用 Goal 一键验收。Automation 仅 `needs_you`（及可选推进中）进工作台 |
| 6 | 「继续讨论」怎么进会话？ | **会话 Drawer 浮层**，绑定原 `conversationId`；**可关闭**，不跳主 Chat；与任务/历史/结果抽屉同层互斥。详见 §14 |

### 最小闭环交互（规范）

```
结果待验收卡片
  · 主标题 = plan.title
  · 摘要 = 进度 / 标准通过（直接可见，不必进会话）
  · 主按钮「确认验收」→ revise 写 resultAcceptance → 项变 terminal
  · 次按钮「查看结果」（可选）→ 结果抽屉（只读细节）
  · 次按钮「继续讨论」（可选）→ 会话抽屉（可关闭，绑定原 conversationId）
```

---

## 14. 任务续接（同一 Conversation 继续）

### 14.1 模型边界

任务续接沿用产品总纲的既有定义，不增加新的父 Task 实体：

```text
Conversation = Task 的事实身份与持续沟通载体
GoalPlan = Task 内需要持续执行和验证的一段目标生命周期
Run = GoalPlan 的一次执行或续接尝试
Workbench / Result View = 上述事实的操作投影
会话抽屉（Conversation Drawer）= 续接时的会话现场容器（浮层，可关闭）
```

因此：

- 从工作台或结果视图继续，必须绑定该项原有的 `conversationId`；
- 普通追问仍是同一 Conversation 内的 Ask / L0 turn，不因“继续讨论 / 继续任务”自动创建 GoalPlan；
- 需要实施的新输入仍由现有 Goal intake 判断并创建 GoalPlan；
- 当前 Goal 的补充、纠偏或重试仍由既有 GoalPlan / Run 生命周期处理；
- 只有用户的最终托付事项实质变化，才创建新的 Conversation，也就是新的 Task。

### 14.2 续接动作契约

“查看结果”和“继续讨论 / 继续任务”是两个不同动作：

| 动作 | 语义 | 不做什么 |
|---|---|---|
| 查看结果 | 在只读 Result View 中查看消息、计划、进度与验收事实 | 不改变 Conversation，不创建执行 |
| 继续讨论 / 继续任务 | **打开会话抽屉**，绑定原 `conversationId`，展示会话现场并聚焦 Composer | 不预填实施命令，不发送消息，不直接创建 GoalPlan；**不把主区硬切成 Chat** |
| 确认验收 | 写入既有 result acceptance 事实并使投影进入 terminal | 不等同于继续讨论 |

稳定文案：

- 主动作：`继续讨论` / `Continue discussion`（工作台 / 结果视图语境优先）；历史兼容文案 `继续任务` / `Continue task` 语义相同
- 说明：`打开原会话继续追问或发起下一步`
- 关闭：会话抽屉标题栏提供关闭（`×` / Esc / 点遮罩按统一 Drawer 规则），关闭后回到打开前的主区上下文

> **产品决策（2026-08-10）**  
> 继续讨论 = **会话 Drawer 浮层**，不是「关抽屉 + 跳主 Chat」。  
> 用户必须能随时关闭会话抽屉，回到工作台 / 任务列表 / 历史 / 结果视图，不丢上下文。

### 14.3 会话抽屉交互规范

#### 打开

入口（有 `conversationId` 时）：

1. 工作台卡片「继续讨论」
2. 任务抽屉 / 历史抽屉列表项「继续讨论」
3. 结果视图 / 任务详情中的「继续讨论」
4. 聊天页头部「任务详情」的反向路径不在此列（那是详情抽屉，不是会话抽屉）

打开行为：

```text
点击「继续讨论」
  → 绑定原 conversationId（不新建 Conversation）
  → 打开会话抽屉（Conversation Drawer）
  → 抽屉内渲染该会话的消息流 + Composer（+ 既有 Goal 面板如有）
  → Composer 获得输入焦点
  → 点击本身不发送消息、不创建 GoalPlan
```

与其它抽屉的关系：

| 规则 | 说明 |
|---|---|
| 同层互斥 | 会话抽屉与任务/历史抽屉、结果抽屉同属 Drawer 层；打开会话抽屉时，**关闭**任务/历史/结果抽屉（或由其退场），避免多层叠压 |
| 主区不变 | **不**强制把主导航切到 Chat / 会话列表；用户仍可感知自己在工作台上下文中打开了浮层 |
| 关闭可逆 | 关闭会话抽屉后，主区回到打开前的页面（工作台 / 任务 / 历史等），不自动选中其它会话 |
| 关闭方式 | 必须走统一 `requestClose`（标题栏关闭、Esc、遮罩点击按现有 Drawer 约定），保留退场动画 |
| 无 conversationId | 不显示「继续讨论」；可降级为打开任务详情 / 结果视图 |

#### 关闭

- 关闭只收起会话抽屉，**不**结束 Task、**不**取消 GoalPlan、**不**归档 Conversation
- 关闭后再次点击同一项的「继续讨论」，应再次打开同一 `conversationId` 的会话抽屉
- 若会话在抽屉内正在运行（streaming / Goal running），关闭抽屉**不中断**后台执行；再打开时看到最新状态

#### 抽屉内能力边界

会话抽屉内应具备与主区会话现场等价的沟通能力：

- 消息流阅读、滚动、引用
- Composer 输入与发送（Ask / Goal intake 同一条链）
- 既有 Goal 面板、权限卡、验收相关 UI（若该会话已有）
- 不新增绕过 Runtime Projection、PermissionGrant 或 Evidence 的发送通道

### 14.4 输入路由

续接入口只恢复 Task 现场，后续输入仍走统一聊天与 Goal intake 链：

```text
继续讨论
  → 打开会话抽屉 + 绑定原 Conversation
  → 聚焦抽屉内 Composer
  → 用户输入下一步
      ├─ 解释 / 追问 / 只读查阅 → Ask / L0，不创建 GoalPlan
      ├─ 当前 Goal 的补充或纠偏 → 续接当前 GoalPlan / Run
      ├─ 当前无活跃 Goal，且输入需要实施 → 同一 Conversation 下创建新 GoalPlan
      └─ 最终托付事项已经变化 → 新 Conversation / 新 Task
```

### 14.5 展示规则

- 有 `conversationId` 的 GoalPlan / 普通 Conversation 投影可以显示「继续讨论」；
- 没有 `conversationId` 的 Automation 等非会话来源不显示该入口；
- `result_ready` 页面同时保留「继续讨论」和「确认验收」，由用户决定先追问/补充还是直接验收；
- terminal 历史结果仍可打开原 Conversation 的会话抽屉追加 Ask 或形成新的 GoalPlan；
- Task 标题与当前 GoalPlan 标题不得因续接动作而相互覆盖；
- 会话抽屉标题优先用 Task / Conversation 标题，可附带轻量状态（讨论中 / 推进中 / 待验收等）。

### 14.6 现状 vs 目标

| 维度 | 【现状】实现 | 【目标】规范 |
|---|---|---|
| 容器 | 关结果/集合抽屉 → 主区切 Chat | **打开会话抽屉**，主区上下文可保留 |
| 关闭 | 无「从续接返回浮层」的对称关闭 | 会话抽屉可关，回到打开前主区 |
| 选中会话 | `selectConversation` 切主区活跃会话 | 抽屉绑定 `conversationId`；是否同步主区活跃会话由实现决定，但**关闭抽屉不得误切到无关会话** |
| 文案 | `继续任务` | 优先 `继续讨论`（语义相同，兼容旧文案） |

### 14.7 验收标准

1. 点击「继续讨论 / 继续任务」后绑定的仍是原 `conversationId`；
2. **打开会话抽屉**，而不是仅把主界面切成 Chat；
3. 会话抽屉可关闭（标题栏 / Esc / 统一 Drawer 关闭），关闭后回到打开前主区上下文；
4. 打开会话抽屉时，任务/历史/结果等其它抽屉不叠压残留；
5. Composer（抽屉内）获得输入焦点；
6. 点击续接本身不会发送消息或创建 GoalPlan；
7. 抽屉内后续 Ask、GoalPlan、Run、权限与 Evidence 行为仍由现有生命周期治理；
8. 关闭抽屉不中断后台运行中的会话 / Goal。

---

## 15. Task 上下文与无计划讨论态

> **【覆盖】2026-08-15**：本节早期把「无 GoalPlan 的 Conversation」也写成 Task，并建议 `actionRight = paused`。这已被 `design/product/task-identity-conversation-carrier.md` 覆盖。
>
> - Conversation 仍是**载体主键**，不是用户心智上的任务。
> - 无 GoalPlan 的沟通只是讨论，最多进「正在讨论」；**不进任务桶，也不标成暂停任务**。
> - 委托成立（有持久化 GoalPlan / 明确要推进的工作）之后，这条 Conversation 才作为该 Task 的现场。
> - 不另起 Task 表。下面 15.2–15.5 里与此冲突的句子以身份层为准。

### 15.1 展示目标

Conversation 是讨论与执行共享的持续上下文。没有 GoalPlan 时，界面应让用户看见这是一段仍可继续的**讨论**，而不是用虚构计划填补空白，也不要把它说成「暂停中的任务」。

```text
Conversation / Task
  ├─ 无 GoalPlan → 讨论中
  └─ 有 GoalPlan → 当前目标 + 计划进度 + 历史目标
```

讨论态只表达“当前没有执行计划”，不表示任务失败、暂停或等待执行。

### 15.2 TaskOverview 投影契约

无计划 Conversation 可以通过既有 TaskOverview 投影 seam 出现在「正在讨论」，不新增 Task 存储实体：

- 投影主键仍可用 `conversationId`，这是载体 id，不是「这就是一个 Task」；
- `source = conversation`，明确它不是 GoalPlan 或 Automation 状态机产物；
- **不要**再标 `actionRight = paused`。无计划沟通没有任务行动权，只是讨论；
- `statusLabel = 讨论中`，`planProgress` 与 `planSteps` 必须为空；
- `conversationId` 必须保留，用于打开讨论现场；
- 同一 Conversation 存在可见 GoalPlan 投影时，Conversation 基础投影必须去重，且退出「正在讨论」；
- Automation 仍按独立来源投影，不伪装成 Conversation。

Renderer 只消费聚合后的 `TaskOverviewItem`，不得自行扫描 GoalPlan 判断讨论态。

### 15.3 标题与详情规则

- 委托成立后，用户可见标题以 GoalPlan.title / 目标线名为准；Conversation 标题只是载体草稿；
- 无计划讨论继续用 Conversation 标题，不要假装成任务名；
- 聊天页头部展示轻量 Task 状态与“任务详情”入口；
- 无计划详情展示“当前没有执行计划”的空态；
- 有计划详情展示当前 GoalPlan、步骤进度和同一 Conversation 下的历史 GoalPlan；
- 普通 Ask 不因为打开详情、继续讨论或查看空态而创建 GoalPlan。

### 15.4 工作台分组

讨论态不进入“Peer 正在推进”或“结果待验收”分组。工作台可增加“最近讨论”分组，任务/历史集合则可按现有时间与 Workspace 过滤展示 Conversation 投影。

### 15.5 验收标准

1. 没有 GoalPlan 的普通 Conversation 在聊天页显示“讨论中”，任务详情显示无计划空态；
2. 普通 Conversation 在工作台可见，且没有虚构的计划步骤或进度；
3. 同一 Conversation 创建 GoalPlan 后，工作台只保留一条 Task 表达；
4. 有 GoalPlan 时，任务详情能区分 Task 标题、当前目标和历史目标；
5. 咨询、评估与界面讨论类 Ask 不自动创建 GoalPlan；
6. 协议、存储和 IPC 不新增父 Task 实体。
