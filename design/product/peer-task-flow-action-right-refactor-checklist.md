# 任务流纠偏改造清单（命名 / 首页投影 / 行动权分桶）

> 创建时间：2026-08-09  
> 最后更新：2026-08-13  
> 文档状态：**实现清单（对照 `peer_agent` 现状）**  
> 产品真源：`design/product/peer-task-flow-action-right-correction.md`  
> 关注的讨论：`design/product/followed-discussions.md`  
> 关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）  
> 对照基线：`design/product/peer-2-0-gap-analysis.md` §11、`peer-2-0-workbench-flow.md`

---

## 0. 改造目标

把工作台从「会话列表 + Goal 卡片」纠回到：

> **委托任务的行动权交接板**  
> 命名稳定、首页按行动权分桶、讨论不再与任务流并列抢心智。

本清单只改知识库交付范围外的**实现指引**；代码改动一律在 `peer_agent` 落地。

---

## 1. 现状结论（证据点）

### 1.1 命名：用户原话直接变成标题

| 位置 | 现状 | 问题 |
|---|---|---|
| `packages/conversation-store/src/index.mjs`（`appendMessage`） | 无 title 时：`meta.title = message.content.slice(0, 50)` | 首条用户原话 = 讨论名 |
| Agent `goal_create_plan` 入参 `title` | 模型自拟；弱约束 | 易写成原话 / 确认语 / 过长句 |
| `apps/desktop/electron/main/task-overview-aggregator.mjs` | 有会话时：`title: normalizedTitle(conversation.title, projected.title)` | **主标题优先 conversation 原话**，压过 `plan.title` |
| 同上 | `currentGoalTitle: projected.title` | UI 副行「当前目标 · …」直接绑 plan 名；若 plan 名差则二次污染 |

### 1.2 首页投影：任务桶 + 最近讨论并列

| 位置 | 现状 | 问题 |
|---|---|---|
| `apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx` | 三桶任务 + `DISCUSSION_PREVIEW_LIMIT` 最近讨论 | 讨论与行动权主轴视觉对等 |
| 同上 `WorkItem` | `当前目标 · {currentGoalTitle}`、`GoalPlan x / y · statusLabel` | 系统腔 + 过程句 |
| 同上 | `source === 'conversation'` 卡片文案「继续讨论…」 | 强化「聊天产品」心智 |
| aggregator | 已有 `projectedPlanConversationIds` 去重 | 有 plan 的会话不再双投；**但标题仍用会话原话**；无 plan 的讨论仍占首页主视觉 |

### 1.3 行动权分桶：协议层大体就绪，展示层未收口

| 位置 | 现状 | 问题 |
|---|---|---|
| `packages/protocol/src/task-overview.ts` | `TaskActionRight` / `TaskNextAction` / item 契约 | 契约可用 |
| `task-overview-aggregator.mjs` | `projectGoalPlan` + `isPlanResultAccepted` + 排序 | `completed` 未验收 → `result_ready` 路径已有 |
| `TaskOverviewPage.tsx` | 按 `needs_you` / `peer_advancing` / `result_ready` 过滤 | 过滤正确，**文案与讨论区未服从主轴** |
| `HomePage.tsx` | `filter={(item) => item.actionRight !== 'terminal'}` | 正确；依赖上游 item 质量 |

---

## 2. 改造原则（实现时不可违反）

1. **主标题真源**：有活跃 GoalPlan → 用 **`plan.title`**；无 plan → 用生成/中性讨论名，**禁止**用户原话全文。  
2. **副行真源**：当前步骤 / nextAction，**不是**「当前目标 · 确认语」。  
3. **首页主轴**：仅行动权三桶；讨论区定稿为次级 **「正在讨论」**（未读 + 无任务投影）。  
4. **去重**：同一 `conversationId` 有活跃行动权 → 只出现在任务桶，永不并行进「正在讨论」。  
5. **不改** gap-analysis §11 的状态映射优先级，除非验收字段契约变更。

---

## 3. 改造项清单

### P0 — 命名（先修真源，再修展示）

#### P0-1 会话标题：禁止原话切片当永久名

- **仓**：`peer_agent`
- **文件**：`packages/conversation-store/src/index.mjs`
- **现状**：`appendMessage` 首条 user → `slice(0, 50)`
- **改法**：
  1. 首条消息可写 **临时** `titleDraft` 或仍写 title，但标记 `titleSource: 'user_snippet' | 'generated' | 'plan' | 'manual'`
  2. 更好：首条只写 `titleDraft`，列表展示走 `displayTitle` 解析：  
     `plan.title` > `generatedTitle` > 中性「未命名沟通」> 截断 draft（≤16 字 + …）
  3. **禁止**把 50 字原话当最终产品标题
- **验收**：
  - 新建会话发「这一段话废话太多了…」→ 首页/列表不出现完整原话作主标题
  - 单测覆盖 `appendMessage` 标题策略

#### P0-2 GoalPlan 标题：创建时质量门 + 稳定不覆盖

- **仓**：`peer_agent`
- **文件**（按实际实现点，优先这些路径排查/改）：
  - Goal 工具入参校验（`goal_create_plan` 处理链，desktop main / tool-orchestrator 一带）
  - `packages/goal-plan-store`（若存在 title 写入）
  - 协议/提示词：要求 title =「动词 + 对象」、10～20 字、禁确认语
- **改法**：
  1. 服务端/校验层拒绝或改写明显坏标题：空、纯确认语（好/就这么做/认可）、过长原话、命令输出
  2. 创建成功后 **默认不**被后续用户消息覆盖
  3. 可选：创建 plan 成功后回写 conversation.title（`titleSource: 'plan'`）
- **验收**：
  - 模型若传入「好，就这么做」→ 落库前被改写或拒绝并重试生成
  - plan 推进中用户再说话 → title 不变

#### P0-3 投影合并：主标题改回 plan.title

- **仓**：`peer_agent`
- **文件**：`apps/desktop/electron/main/task-overview-aggregator.mjs`
- **现状**：
  ```js
  title: normalizedTitle(conversation.title, projected.title),
  currentGoalTitle: projected.title,
  ```
- **改法**：
  1. 有 GoalPlan 时：**`title = plan.title`（projected.title）**
  2. `currentGoalTitle`：**删除，或改为当前步骤标题 / goal 摘要字段且不用于主展示**
  3. 注释已写「展示名固定使用 plan.title」——与代码对齐
  4. 更新 `task-overview-aggregator.test.mjs`：会话原话不得压过 plan 名
- **验收**：
  - conversation.title=用户原话、plan.title=「重构首页任务流投影」→ 卡片主标题为后者

#### P0-4 前端卡片文案去系统腔

- **仓**：`peer_agent`
- **文件**：`apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx`
- **改点**：
  | 函数/UI | 现状 | 目标 |
  |---|---|---|
  | `reasonMeta` | `GoalPlan ${n}/${m} · statusLabel` | `进度 n/m` 或只显示当前步骤名 |
  | `WorkItem` 副行 | `当前目标 · {currentGoalTitle}` | 改为「当前：{currentStepTitle}」；无步骤则省略 |
  | conversation 卡片 | 「继续讨论，或在明确实施时创建 GoalPlan」 | 弱意图区另案；任务桶内不出现此句 |
  | 主按钮语义 | 「继续讨论」抢主轴 | 任务桶用「去处理 / 查看 / 确认验收」 |
- **验收**：截图级 — 不再出现 `GoalPlan 0 / 1`、`当前目标 · 好，就这么做`

---

### P1 — 首页投影与讨论降级

#### P1-1 「正在讨论」定为次级未读入口（方案 A，已定稿）

- **仓**：`peer_agent`
- **产品真源**：`peer-task-flow-action-right-correction.md` §7.2
- **文件**：
  - `TaskOverviewPage.tsx`（布局与 `DISCUSSION_PREVIEW_LIMIT`）
  - 相关 CSS / design tokens
  - 讨论列表数据源（需能判断未读水位）
- **改法**：
  1. 主视觉只保留：需要你处理 / Peer 正在推进 / 结果待验收
  2. 区块改名：**「正在讨论」**（替代「最近讨论」）
  3. **只收未读**：`hasUnread === true`；已读会话不占位
  4. **只收无活跃行动权**：`actionRight` 不在 `{ needs_you, peer_advancing, result_ready, paused }`
  5. 视觉降级：折叠区 / 更低权重 / 更少条数（建议 ≤3～6）
  6. 卡片主 CTA 弱化「继续讨论 →」；读后从列表消失
  7. 空态：无未读时隐藏或极轻空态，**禁止**用已读历史填满
- **验收**：有活跃任务时第一眼只看到三桶；讨论区若有内容，全是未读且非任务会话

#### P1-2 活跃任务 conversation 禁止进「正在讨论」（加固）

- **仓**：`peer_agent`
- **文件**：`task-overview-aggregator.mjs`（已有 `projectedPlanConversationIds`）
- **改法**：
  1. 确认：凡 `actionRight ∈ {needs_you, peer_advancing, result_ready, paused}` 的 conversationId **不得**再 `projectConversation`
  2. 补测：一会话一 plan 执行中 → items 中仅一条 goal_plan，无 conversation 影子
  3. 若前端本地再拼会话列表，删除双源
  4. **即使任务会话有未读更新，也只留任务桶**，不并行进「正在讨论」
- **验收**：单元测试 + 手动：推进中 / 待验收 / 需要你 / 暂停 的任务不出现在「正在讨论」

#### P1-3 无 plan 讨论的展示标题

- **仓**：`peer_agent`
- **文件**：aggregator `projectConversation` + conversation-store 展示策略
- **改法**：
  - 无生成标题时用「未命名沟通」或短摘要（≤16 字），禁止命令行/日志全文
  - 可选后续：后台异步生成 discussion summary title
- **验收**：`> tsc -p ...` 类内容不出现在讨论卡片主标题

#### P1-4（可选）方案 B：首页移除讨论区

- 仅当方案 A 仍噪音过大时启用；讨论只留侧栏会话列表 / 搜索
- 首页纯行动权
- 若选 B，可跳过 P1-1 的弱化，直接删区块

---

### P1 — 行动权分桶收口

#### P1-5 保持 §11 映射，补齐验收字段使用

- **仓**：`peer_agent`
- **文件**：
  - `packages/protocol/src/task-overview.ts`
  - `task-overview-aggregator.mjs`（`isPlanResultAccepted`）
  - 验收 IPC / UI（确认验收按钮）
- **改法**：
  1. 确保新完成 plan 无 `resultAcceptance` → 只进 `result_ready`
  2. 验收后 → `terminal`，离开工作台
  3. 前端待验收主按钮 = 确认验收，次按钮 = 查看结果
- **验收**：与 workbench-flow §3.2 一致；历史抽屉不出现未验收 completed

#### P1-6 needs_you 内部分桶文案

- **文件**：`TaskOverviewPage.tsx`（`ownerLabel` / `reasonTitle` 已有雏形）
- **改法**：按 `needsYouReason` / `nextAction` 稳定中文，不暴露内部 enum
- **验收**：待批准 / 待授权 / 待回答 / 待决策可读

#### P1-7 Automation 与 Goal 分源标注（若首页混排）

- 保持 `source: automation | goal_plan | conversation`
- 自动化成功策略维持「成功即归档不进工作台」（aggregator 注释方案 A）
- 不把 automation 标题逻辑与 conversation 原话策略混用

---

### P2 — 协议与提示词加固

#### P2-1 TaskOverviewItem 字段收敛

- **文件**：`packages/protocol/src/task-overview.ts`
- **建议**：
  - 明确 `title` = 用户可见任务名（plan 优先）
  - `currentStepTitle` 替代或旁路 `currentGoalTitle` 的滥用
  - 若保留 `currentGoalTitle`，文档写明：**不得**渲染为「当前目标 ·」若内容等于确认语
- **验收**：协议注释与 UI 一致；类型变更有编译/测试

#### P2-2 System / tool 提示词

- Goal 创建提示：title 规则写入工具 description
- 明确禁止：用户原话、确认语、路径、命令输出当 title
- 与 `peer-task-flow-action-right-correction.md` §6 对齐

#### P2-3 通知文案同源

- **文件**：`task-notification-policy` / broker 一带
- 通知标题与工作台卡片同一套 displayTitle，避免通知一条、首页一条

---

### P3 — 关注的讨论（另案，不阻塞 P0/P1）

完整规则见 `design/product/followed-discussions.md`。本清单只挂实现入口，避免和「正在讨论」混改。

#### P3-1 未读入口先收口

- **文件**：`TaskOverviewPage.tsx`、`GlobalWorkbenchPage.tsx`、aggregator
- 「正在讨论」只留 `isUnread &&` 无活跃行动权；已读离开；无未读则隐藏
- 全局工作台去掉「最近讨论」文案
- **验收**：不再出现已读卡填满讨论区、三位数会话墙

#### P3-2 独立订阅字段

- **文件**：`packages/conversation-store`
- 新增 `followedAt` / `followedOrder` + follow / unfollow / reorder
- **禁止**复用 `pinnedAt`；follow 不得改 `updatedAt` / `lastReadAt`
- 硬顶 8 条；归档清空字段

#### P3-3 首页主区域关注列表

- 主区域三桶之下增加「关注的讨论」紧凑列表；预览 3 条；查看全部 = 已关注列表
- 「正在讨论」留在次级区，改成瘦未读条
- 与任务桶、「正在讨论」互斥（纠偏文档 §7.3）

---

## 4. 建议落地顺序

```text
1. P0-3 投影主标题改 plan.title          （最快止血）
2. P0-4 前端去掉 GoalPlan / 当前目标腔   （可见立刻变好）
3. P0-1 会话标题策略                      （断原话源头）
4. P0-2 plan 标题质量门                   （断坏 title 入库）
5. P1-2 去重加固 + 测试
6. P1-1 讨论区降级
7. P1-5/6 验收与 needs_you 文案
8. P2 协议与提示词
9. P3-1 未读入口收口后再做 P3-2/P3-3 关注区
```

---

## 5. 测试矩阵（peer_agent）

| 场景 | 期望 |
|---|---|
| 新会话首条长原话，无 Goal | 不进「正在推进」；讨论名非完整原话 |
| 用户确认「好，就这么做」后创建 Goal | 任务名 ≠ 确认语；主标题 = 合格 plan.title |
| Goal 执行中 | 仅 peer_advancing 一桶一条；「正在讨论」无此会话（即使有未读） |
| 无任务会话有未读 | 可出现在「正在讨论」；打开读完后消失 |
| 无任务会话已读 | 不出现在「正在讨论」 |
| 用户关注一条已读讨论 | 只出现在「关注的讨论」；读完还在；不进「正在讨论」 |
| 已关注讨论产生未读 | 仍只在关注区打角标，不与「正在讨论」双开 |
| 第 9 条关注 | 被拒绝；已有 8 条不少 |
| Goal completed 未验收 | 仅 result_ready；不进历史 |
| 用户点确认验收 | 离开工作台，进历史 |
| conversation.title 很脏、plan.title 正常 | 卡片显示 plan.title |
| 自动化成功 | 不进工作台待验收（维持方案 A） |

**建议测试文件**：

- `apps/desktop/electron/main/task-overview-aggregator.test.mjs`
- conversation-store 标题相关 test
- `TaskOverviewPage` 若有组件测则补文案断言；否则手测清单

---

## 6. 非目标（本清单不做）

- 不重做 Task Canvas / 自由白板
- 不引入父任务 / 项目层级
- 不把首页做成全部 Goal 仓库
- 不在本清单内改 Cloud Runtime
- 不把知识库文档当运行时代码
- 不把侧边栏 `pinnedAt` 倒进首页冒充关注区（见 `followed-discussions.md`）

---

## 7. 完成定义（对照产品纠偏文档 §10）

- [ ] 有活跃行动权的工作不会同时出现在「正在讨论」  
- [ ] 「正在讨论」只含未读 + 无活跃行动权的沟通；已读不占位  
- [ ] 卡片主标题来自稳定任务名，非用户原话/确认语/命令  
- [ ] 无 `GoalPlan x/y` 系统腔主文案  
- [ ] 无「当前目标 · 好，就这么做」  
- [ ] completed 未验收只在待验收  
- [ ] 上述 P0 项在 `peer_agent` 有测试或可重复手测步骤  

---

## 8. 关键文件速查（peer_agent）

| 主题 | 路径 |
|---|---|
| 行动权协议 | `packages/protocol/src/task-overview.ts` |
| Goal 协议 | `packages/protocol/src/goal.ts` |
| 会话标题写入 | `packages/conversation-store/src/index.mjs` |
| 投影聚合 | `apps/desktop/electron/main/task-overview-aggregator.mjs` |
| 聚合测试 | `apps/desktop/electron/main/task-overview-aggregator.test.mjs` |
| 首页壳 | `apps/desktop/renderer/src/app/pages/HomePage.tsx` |
| 工作台 UI | `apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx` |
| Preload 契约 | `apps/desktop/renderer/src/preload/contracts/bootstrapPreloadApi.ts`（task overview API） |
| 通知策略 | `apps/desktop/electron/main/task-notification-policy*.mjs` |

---

## 9. 与产品纠偏文档的映射

| 纠偏文档章节 | 本清单项 |
|---|---|
| §3 行动权主轴 | P1-1, P1-5 |
| §4 对象关系 / 一任务一投影 | P1-2, P0-3 |
| §6 命名规则 | P0-1, P0-2, P0-3, P1-3, P2-2 |
| §7 首页投影 | P0-4, P1-1, P1-2 |
| §7.3 关注分流 | P3-1, P3-2, P3-3 |
| §8 卡片文案 | P0-4, P1-6 |
| §12 落地顺序 | §4 建议落地顺序 |
