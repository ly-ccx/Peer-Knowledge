# Automation 执行结果查看交互改造方案

> 创建时间：2026-08-06
> 最后更新：2026-08-06
> 文档状态：交互改造提案（知识库文档，不改代码）
> 关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）
> 关联文档：
> - `design/product/automation-scheduled-agent-product-design.md`（Automation 产品基线 / P0 冻结）
> - `design/product/status-bar-task-center.md`
> - `design/product/conversation-search-palette.md`
> - `knowledge/decisions/27-workspace-switch-and-cross-workspace-running.md`

---

## 0. 文档目的与结论

### 0.1 一句话结论

> **看结果应以「Run 收据」为一级入口：列表即见摘要，详情即见结论；打开会话是深挖过程的二级动作，而不是看结果的必经之路。**

### 0.2 为什么写这篇

用户在本机使用「每日更新回顾」后反馈：

1. 点「立即运行」后 Run 页像停在「已计划」；
2. 想看执行记录时，路径像是：
   `自动化中心 → 选任务 → 选记录 → 打开会话`；
3. 会话列表里找不到对应自动化会话。

本机证据（2026-08-06）表明：

| 事实 | 证据 |
|---|---|
| Run `b2e4d352-65b5-…` 实际已 `succeeded` | `~/.peer-agent/automations/runs/b2e4d352-65b5-492c-8d2f-abd700612c41.json` |
| 耗时约 14s，有 conversationId | 同上；会话 `2bba45f0-82c5-…` |
| `receipt.summary` 为空 | 同上 receipt 字段 |
| 会话存在且有完整回答 | `~/.peer-agent/conversations/2bba45f0-….jsonl` |
| 会话 `workspacePath` 挂在 automation worktree | `conversations/index.jsonl` |
| 侧栏按当前 workspace 过滤 | conversation store `listConversationsByWorkspace` |
| 产品基线本就要求 Run 列表一行摘要 + Run Detail RESULT | 主设计文档 §18 / §19 |

因此：**不是“用户不会用”，而是实现与产品基线之间的结果查看链路断裂。**

本文只做交互与信息架构改造方案，**不改代码**；实施应回代码仓 `peer_agent`，并优先对齐既有冻结决策，而不是另起第二套系统。

### 0.3 与冻结基线的关系

`automation-scheduled-agent-product-design.md` 已冻结：

- Automation Center 为全局一级入口；
- Automation Detail = `Overview + Runs`；
- Run Detail = **不可变结果收据**；
- Conversation = 执行过程与人工交互；
- 通知 / Task Center / Center 多入口回流携带 `automationId + runId`。

本改造**不是推翻对象模型**，而是：

1. 把基线里已写但未兑现的「摘要可见」补成可感知体验；
2. 缩短「我想看最近一次结果」的点击路径；
3. 修正 worktree 会话在侧栏“消失”的可达性问题。

---

## 1. 问题重写（系统语言）

### 1.1 problem_rewrite

**层：结果消费链路（Run Receipt 展示 + Conversation 可达性 + 列表过滤）**

**可观察症状：**

1. 成功 Run 的收据页缺少最终摘要（`receipt.summary` 空），用户误以为“没结果 / 还没跑完”；
2. 完整结论只在 Conversation 里，而自动化会话常挂在 worktree 路径，不在当前 workspace 侧栏；
3. 用户必须走多级导航才能看到结果，体感路径过长。

### 1.2 约束

| 类型 | 约束 |
|---|---|
| 产品 | 保持 Automation / Run / Receipt / Conversation 分离；Run 完成后收据不可被后续聊天改写 |
| 工程 | Fresh Run + 独立 Conversation；Git 写入默认 worktree 隔离 |
| 平台 | 侧栏会话列表按 workspace 过滤是既有模型，不能粗暴变成全局混排 |
| 验收 | 用户在 **≤2 次点击** 内看到最近一次成功结果的可读摘要；打开会话为可选深挖 |

### 1.3 根因假设

| # | 假设 | 如何证伪 |
|---|---|---|
| **H1（主）** | 结果主视图应在 Receipt，但实现未可靠回填 `summary` / 列表未渲染一行结果 | 查 runner 终态写 receipt 逻辑 + Runs 列表字段 |
| **H2** | 会话 `workspacePath` 写成执行 worktree，侧栏按 origin workspace 过滤 → 列表不可见 | 对比 index 中 `workspacePath` 与 definition.workspacePath |
| **H3（次）** | UI 状态刷新滞后，创建瞬间 `scheduled` 徽章停留过久 | 复现手动 Run 并观察 IPC/store 推送 |
| H4（排除） | “Run 根本没执行” | 本地 run 文件已是 `succeeded`，可排除 |

**source_of_truth（改造后）：**

- **结果结论** → `Run.receipt`（摘要、证据、用量、状态）
- **过程细节** → `Conversation`（工具轨迹、人工问答）
- **列表投影** → Automation Detail Runs / Center / Task Center，均从 Run 投影，不从会话反推

### 1.4 因果链（将改动的节点）

```text
Runner 终态
  → 写入 receipt.summary / evidence（数据契约）
  → Runs 列表渲染一行结果（列表投影）
  → Run Detail 默认展示 RESULT 区（收据页）
  → Overview「最近一次结果」快捷入口（任务级捷径）
  → 会话可达：origin workspace 可见 或 Run 内一键打开（导航）
  → 通知点击落到 Run Detail 且摘要已就绪（回流）
```

### 1.5 non_goals

- 不做「永久共用一个 Conversation 的自动化」；
- 不把所有 worktree 会话无过滤塞进侧栏制造噪音；
- 不在本方案改调度器语义、权限模型、并行策略；
- 不把 Run Detail 改成可编辑聊天区。

---

## 2. 当前路径 vs 目标路径

### 2.1 当前主路径（用户体感）

```text
Automations
  → 进入某个 Automation
    → 切到 Runs / 点某次 Run
      → Run Detail（常只有状态/元数据，无正文）
        → Open conversation
          → 才看到完整结论
```

附加摩擦：

- 侧栏找不到 `Automation: …` 会话；
- 成功时若未开成功通知，几乎没有“结果找我”的推力；
- 状态徽章可能短时停在「已计划」。

### 2.2 目标主路径（改造后）

**路径 A — 看最近一次结果（默认）**

```text
Automations / 任务卡片 或 Automation Overview
  → 「最近一次结果」或 Runs 首行摘要
    → 已可读结论（成功/失败/阻塞原因）
```

**路径 B — 看某次历史**

```text
Automation Detail → Runs
  → 行内一行摘要 + 状态
  → 点入 Run Detail 看完整收据
```

**路径 C — 深挖过程 / 继续跟进**

```text
Run Detail → 打开会话
```

**路径 D — 被通知/任务中心拉回**

```text
通知 / Task Center
  → 直达对应 Run Detail（摘要已在）
  → 可选再打开会话
```

### 2.3 点击预算（验收用）

| 用户意图 | 目标点击次数 | 必须看到 |
|---|---:|---|
| 最近一次是否成功、结论是什么 | ≤ 2 | 状态 + 可读摘要 |
| 某次历史失败原因 | ≤ 2 | 状态 + 错误/阻塞摘要 |
| 工具怎么跑的 / 继续追问 | ≤ 3 | Conversation |

---

## 3. 信息架构（不改对象，改投影）

### 3.1 三层信息分工（冻结）

| 层 | 职责 | 用户问题 |
|---|---|---|
| **Automation Overview** | 健康度 + 最近一次结果入口 + 下次运行 | 这事现在怎样？ |
| **Run Receipt（Detail）** | 不可变结论、证据、用量、上下文快照 | 这次到底怎样？ |
| **Conversation** | 过程轨迹、等待输入、人工跟进 | 它怎么做的？我怎么接着做？ |

### 3.2 关键字段契约（产品侧）

Run 在进入终态时，Receipt **至少**应具备：

| 字段 | 要求 | 说明 |
|---|---|---|
| `status` | 必有 | 与 UI 徽章一致，刷新及时 |
| `summary` | 终态必有 | 1–5 行中文可读结论；失败时写失败原因摘要 |
| `errorSummary` / `blockedReason` | 异常态必有 | 列表与详情共用 |
| `evidenceRefs` / 关键验证 | 尽力 | 有则展示，无则折叠 |
| `durationMs` / tokens | 有则展示 | 次要信息 |
| `conversationId` | 有会话则必有 | 支撑「打开会话」 |
| `originWorkspacePath` | 建议补齐投影 | 用于侧栏/搜索归属，不等于 execution worktree |

> 若模型未产出清晰 summary：应用规则兜底生成（例如「已完成，无结构化摘要；请打开会话查看全文」+ 首段截断），**禁止空白 RESULT 区**。

### 3.3 会话可见性策略

**原则：** 执行隔离路径（worktree）与**用户心智归属路径（origin workspace）**分离。

| 概念 | 含义 |
|---|---|
| `originWorkspacePath` | Automation 绑定的工作区（用户创建时的仓库） |
| `executionWorkspacePath` | 实际执行目录（可能是 worktree） |

**侧栏 / 搜索投影规则（建议）：**

1. 自动化会话默认按 **`originWorkspacePath`** 归入用户工作区列表；
2. 标记 `automationOrigin`（已有字段可复用），列表可用小徽章「自动化」；
3. 可选：默认折叠为「自动化会话」分组，避免刷屏；
4. 仍允许从 Run Detail 一键打开，不依赖侧栏；
5. **不**把 execution worktree 路径当作用户主工作区切换目标（除非用户显式「打开 worktree」）。

### 3.4 状态展示规则

| 内部状态 | 中文建议 | 用户应理解 |
|---|---|---|
| `scheduled` | 已计划 | 已登记，尚未开跑 |
| `queued` | 排队中 | 等待 runner |
| `preparing` | 准备中 | 建会话 / worktree |
| `running` | 执行中 | 正在跑 |
| `waiting_user` / `waiting_permission` | 等待你 | 需要动作 |
| `succeeded` | 已成功 | 有结论 |
| `failed` / `timed_out` / `blocked` | 失败/超时/受阻 | 有原因摘要 |

**刷新要求：** 手动「立即运行」后，若停留在该 Run Detail，应在状态迁移时自动更新；不允许长期停在创建瞬间的「已计划」却无任何进度提示。

---

## 4. 页面级改造规格

### 4.1 Automation Center 列表

每行除名称/调度外，增加：

- 最近一次 Run 状态点；
- **一行最近结果摘要**（可截断）；
- 次要：`上次 · 相对时间` / `下次 · 时间`。

点击：

- 主点击 → Automation Detail Overview（落地最近结果模块）；
- 摘要区可提供「查看该次 Run」深链（可选）。

### 4.2 Automation Detail · Overview

新增 **「最近一次结果」** 模块（P0 体验核心）：

```text
最近一次结果
状态：已成功 · 手动 · 今天 10:50 · 14s
摘要：
  peer-knowledge 昨天 1 次提交；peer_agent 12 次提交……
[查看收据]  [打开会话]  [再运行一次]
```

若无 Run：空态引导「立即运行」或展示下次计划时间。

Health 区继续保留：可执行性、连续失败、Runtime 状态等（与基线 §17 对齐）。

### 4.3 Automation Detail · Runs

对齐基线 §18，强制兑现：

- 状态；
- 计划/实际时间；
- 触发来源；
- 耗时；
- **一行结果或错误摘要（非空策略）**；
- 主动作：查看收据 / 打开会话（按状态显隐）。

### 4.4 Run Detail（不可变收据）

对齐基线 §19，默认首屏结构：

1. **状态条**（成功/失败/等待）+ 关键动作
   `打开会话` · `再运行` · 更多
2. **RESULT**（必显，禁止空白）
   成功摘要 / 失败原因 / 阻塞说明
3. **CHANGES / VERIFICATION**（有则展开，无则隐藏整块）
4. **RUN CONTEXT**（工作区、模型、触发、时间、用量）
5. **ACTIVITY**（可选折叠；完整轨迹仍以会话为准）

**明确文案：**

- 打开会话 =「查看完整执行过程 / 继续跟进」
  而不是「才能看到结果」。

### 4.5 会话侧栏与搜索

- 自动化会话可在 origin workspace 出现，带「自动化」标识；
- 搜索 palette 可用标题 `Automation: {name}` 与 run/conversation id 命中；
- 从会话头展示来源条：`来自自动化 · 每日更新回顾 · 某次 Run` → 回跳 Run Detail。

### 4.6 通知与 Task Center

保持基线回流矩阵（§38–40）：

- 成功通知默认可配置；点击 → **Run Detail**（不是空白首页）；
- 失败/等待 → Run Detail 或会话提问锚点；
- Task Center 投影运行中 / 待处理 / 未读完成项，同样落到 Run。

---

## 5. 分阶段落地建议

### 阶段 P0（体验止血，优先）

**目标：** 用户不再必须「打开会话」才能知道结论。

| 项 | 内容 | 验收 |
|---|---|---|
| P0-1 | Runner 终态保证 `receipt.summary`（或兜底摘要）写入 | 任意成功/失败 Run 文件非空 summary 或 errorSummary |
| P0-2 | Runs 列表展示一行摘要 | 列表可见结论，无需进详情 |
| P0-3 | Run Detail 首屏 RESULT 区 | 空白收据消失 |
| P0-4 | Overview「最近一次结果」模块 | ≤2 次点击看到最近结论 |
| P0-5 | 状态实时刷新（至少 Run Detail / Runs） | 手动运行后不长期假性「已计划」 |

**P0 不做：** 大改侧栏信息架构、智能 only-on-change 通知。

### 阶段 P1（可达性与组织）

| 项 | 内容 | 验收 |
|---|---|---|
| P1-1 | 会话按 `originWorkspacePath` 投影 + 自动化徽章/分组 | peer-knowledge 侧栏可见对应自动化会话 |
| P1-2 | 会话头回来源 Run | 双向回流闭环 |
| P1-3 | Center 列表一行最近摘要 | 跨任务扫一眼 |
| P1-4 | 成功通知默认策略评估（可仍默认关，但文案引导） | 用户理解如何被结果找上门 |

### 阶段 P2（增强）

| 项 | 内容 |
|---|---|
| P2-1 | only-on-change 成功通知 |
| P2-2 | Run 间受控历史摘要（基线 §42） |
| P2-3 | 结果对比（本次 vs 上次） |
| P2-4 | 菜单栏/托盘最近自动化结果快览 |

---

## 6. 实现落点提示（供代码仓，不在此库改）

> 以下为实施导航，非本仓库改动清单。

| 区域 | 可能落点（peer_agent） | 改造点 |
|---|---|---|
| 终态写回 | `apps/desktop/electron/main/automation-runner.mjs` 等 | 从会话最终助手消息/结构化输出生成 summary |
| Run store | automation run 持久化 | 保证 receipt 字段完整；可选 originWorkspace 投影 |
| UI 列表/详情 | `apps/desktop/renderer/src/automations/*` | Overview 最近结果、Runs 一行摘要、Detail RESULT |
| 会话列表 | conversation store + 侧栏加载 | origin workspace 过滤/标记 |
| 文案 | `automationI18n` / presentation | 状态词、打开会话语义 |

**测试建议：**

1. 手动 Run 只读任务 → 列表/详情均有中文摘要；
2. worktree 写入任务 → 会话仍可从 origin workspace 找到或从 Run 打开；
3. 失败 Run → 列表一行错误原因；
4. 停留在 Run Detail 点「立即运行」新 Run → 状态推进可见；
5. 打开会话后继续聊天 → 旧 receipt 不变。

---

## 7. 文案与认知修正

| 现状易误解 | 修正后认知 |
|---|---|
| 「已计划」= 设好了定时 | 「已计划」= **这次 Run 已登记未开跑** |
| 打开会话 = 看结果的唯一办法 | 打开会话 = **看过程 / 继续跟进** |
| 侧栏没有 = 没跑 | 侧栏没有可能是 **worktree 归属**，结果应在 Automations |
| 收据页空 = 失败 | 收据空是 **展示/回填缺陷**，需用 summary 契约修复 |

按钮建议：

- `打开会话` 副文案：「完整过程」
- Overview 主按钮：「查看最近结果」（进收据，而不是直接进会话）

---

## 8. 验收清单（产品）

### 8.1 必过

- [ ] 成功 Run 在 Runs 列表可见一行非空摘要
- [ ] Run Detail 首屏 RESULT 非空
- [ ] Overview 可直接看到最近一次状态 + 摘要
- [ ] 从结果页 ≤1 次点击打开对应会话
- [ ] 会话内继续聊天不修改历史 receipt
- [ ] 手动运行过程中状态会从已计划推进，或明确显示排队/准备/执行

### 8.2 体验目标

- [ ] 「最近一次结论」点击路径 ≤ 2
- [ ] 用户无需理解 worktree 路径也能找到结果
- [ ] 不再出现“成功了但我觉得没动静”的主路径投诉（状态+摘要双可见）

---

## 9. 决策摘要（供评审）

| # | 决策 | 结论 |
|---|---|---|
| 1 | 结果一级入口 | **Run 收据**，不是会话 |
| 2 | 会话角色 | 过程与跟进的二级入口 |
| 3 | 摘要契约 | 终态必须有可读 summary/错误摘要 |
| 4 | 最短路径 | Overview / 列表直达最近结果 |
| 5 | 会话列表 | 按 origin workspace 投影，而非 execution worktree |
| 6 | 范围 | 先 P0 止血，再 P1 可达性，不推翻 Automation 对象模型 |

---

## 10. 附录：本机复现快照（2026-08-06）

| 项 | 值 |
|---|---|
| Automation | 每日更新回顾（`73033acc-…`） |
| Run | `b2e4d352-65b5-492c-8d2f-abd700612c41` |
| 触发 | manual |
| 真实状态 | succeeded |
| 时间 | 10:50:56 → 10:51:10（CST） |
| conversationId | `2bba45f0-82c5-4a47-9e3f-53c519df3a5d` |
| receipt.summary | 空 |
| 会话 workspace | `~/.peer-agent/automations/worktrees/73033acc-…/b2e4d352-…` |
| 绑定 workspace | `/Users/liangyin/Documents/MiaoYan/peer-knowledge` |

该快照用于说明问题，不作为长期测试夹具。

---

## 11. 下一步

1. 评审本文 P0 范围是否同意；
2. 同意后在 `peer_agent` 开实施任务（建议顺序：summary 回填 → 列表/详情展示 → Overview 最近结果 → 状态刷新 → 会话投影）；
3. 若实施发现与冻结基线冲突，先修订本文或主设计文档 / ADR，禁止静默改语义。
