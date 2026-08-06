# Automation 执行结果查看 · peer_agent 实施任务清单

> 创建时间：2026-08-06
> 最后更新：2026-08-06
> 文档状态：已实施（2026-08-06）
>
> 实施结果：P0、P1、P2 已落地到 `peer_agent`。`Run.receipt` 作为结果真相；Overview、Runs、Run Detail、origin workspace 会话投影、Conversation → Run、变化通知、历史对比和 Tray 最近结果入口均已接通。保持 Fresh Run、worktree、权限与不可变 Receipt 语义。
>
> 验证记录：相关 Automation / Tray / Renderer / Conversation Store 专项测试 26 项通过；Desktop TypeScript 类型检查和生产构建通过。Desktop 全量测试执行时被外部取消，取消前另见既有非本改造范围测试失败，故不将“全仓测试全绿”记为本次结论。
> 代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）
> 依据：
> - `design/product/automation-run-result-viewing-redesign.md`（交互改造方案）
> - `design/product/automation-scheduled-agent-product-design.md`（产品基线）
> - 本机复现：Run `b2e4d352-…` 已 succeeded，但 `receipt.summary` 空、会话挂在 worktree

---

## 0. 使用说明

### 0.1 目标

把「结果查看」从：

```text
自动化 → 任务 → 记录 → 打开会话
```

收敛为：

```text
任务 Overview / Runs 列表 → 直接看到结论
（打开会话 = 可选深挖）
```

### 0.2 边界

| 做 | 不做 |
|---|---|
| 在 `peer_agent` 按任务改 runner / store / UI / 会话投影 | 本知识库不直接改代码 |
| 对齐既有对象模型（Automation / Run / Receipt / Conversation） | 不推翻 Fresh Run / worktree 隔离 |
| 每个任务含落点、依赖、验收、建议测试 | 不在此清单改调度并发语义 |

### 0.3 现状对照（2026-08-06 代码阅读）

| 区域 | 现状 | 含义 |
|---|---|---|
| Runs 列表 | 已渲染 `run.receipt?.summary ?? failureReason ?? blockedReason ?? '—'` | **UI 位已有，数据常空** |
| RunReceipt | 已有 Summary 面板：`receipt?.summary ?? … ?? copy.noSummary` | **UI 位已有，数据常空** |
| Overview | 指令 / 计划 / 权限 / 健康；`lastRunAt` 展示 | **缺「最近一次结果」模块** |
| Runner 终态 | `receipt.summary: outcome?.summary` | outcome 无 summary → 写空 |
| 会话列表 | `listConversationsByWorkspace` **精确匹配** `meta.workspacePath` | worktree 会话不在 origin 列表 |
| `lastRunAt` | store 支持字段；scheduler once 完成会写；manual 成功路径易漏 | 健康区「上次运行」可能一直空 |

---

## 1. 推荐实施顺序（总览）

```text
P0-1  summary 回填契约（数据）
  → P0-2  列表/详情非空展示兜底（UI 文案强化，依赖 P0-1 但可并行小改）
  → P0-3  Overview「最近一次结果」（UI）
  → P0-4  状态实时刷新（订阅/轮询）
  → P0-5  lastRunAt / 定义健康字段回写
P1-1  会话 origin workspace 投影
P1-2  会话头回跳 Run
P1-3  Center 列表一行最近摘要
P2-*  通知策略 / 结果对比 / 托盘快览
```

**关键路径：** 先保证 **数据有 summary**，再补 **Overview 捷径**；会话侧栏是 P1，不阻塞「在 Automations 里看结果」。

---

## 2. P0 任务（体验止血）

### T-P0-1 · Runner 终态保证可读 `receipt.summary`

| 项 | 内容 |
|---|---|
| **目的** | 成功/失败 Run 的收据必有用户可读结论，不再依赖打开会话 |
| **优先级** | P0 / 最高 |
| **依赖** | 无 |
| **主要落点** | `apps/desktop/electron/main/automation-runner.mjs`（终态 `receipt: { summary: outcome?.summary, … }`） |
| **可能协作** | outcome 生成处（agent/chat 完成回调）、`automation-runner.test.mjs` |
| **改动要点** | 1. 终态组装 receipt 时：优先 `outcome.summary`；2. 若空，从会话最终 assistant 正文截取 1–5 行/≤N 字；3. 仍空则规则兜底（成功：「已完成，无结构化摘要」；失败：`failureReason`/`error`）；4. 失败态保证 `error`/`failureReason` 与 summary 至少其一非空 |
| **非目标** | 不改模型 prompt 结构为强制 JSON（可后续增强） |
| **验收** | 新成功 Run 的 run JSON 中 `receipt.summary` 非空；失败 Run 有 summary 或 failureReason；旧 UI 列表不再长期显示 `—`/`无摘要` 作为成功常态 |
| **建议测试** | unit：mock outcome 无 summary → 从 assistant 消息回填；e2e/手动：跑「每日更新回顾」类只读任务，查 `~/.peer-agent/automations/runs/*.json` |
| **估时** | M（0.5–1.5d） |

---

### T-P0-2 · Runs / RunReceipt 摘要展示强化（非空策略）

| 项 | 内容 |
|---|---|
| **目的** | 即使历史数据缺 summary，也给出可理解占位与动作引导 |
| **优先级** | P0 |
| **依赖** | 与 T-P0-1 可并行；完整体验依赖 P0-1 |
| **主要落点** | `apps/desktop/renderer/src/automations/AutomationCenter.tsx`（`RunsTable` ~L734、`RunReceipt` ~L741+） |
| **可能协作** | `automationI18n.ts` / presentation 文案 |
| **改动要点** | 1. 成功且无 summary：展示明确占位 +「打开会话查看全文」（而非冷冰冰 `—`）；2. 失败优先 `failureReason`/`blockedReason`；3. 摘要多行截断 + title 悬停全文（可选）；4. 打开会话按钮副语义保持「完整过程」 |
| **验收** | 空 summary 的历史成功 Run 不再被误解为未执行；新 Run 显示 P0-1 写入的正文 |
| **建议测试** | renderer 组件/快照或 presentation 单测；手动点进 `b2e4d352` 类历史 Run |
| **估时** | S（0.5d） |

---

### T-P0-3 · Overview「最近一次结果」模块

| 项 | 内容 |
|---|---|
| **目的** | 进入任务后 ≤2 次点击看到最近结论（常为 1 次：打开任务即见） |
| **优先级** | P0 |
| **依赖** | T-P0-1（有摘要才有信息密度）；UI 骨架可先做 |
| **主要落点** | `AutomationCenter.tsx` → `AutomationDetail` overview 分支（当前为 instructions / schedule / access / health 网格） |
| **可能协作** | 汇总 `runs[0]` 或 store 查询最近 run 的 selector；i18n |
| **改动要点** | 1. Overview 顶部或主栏增加「最近一次结果」卡片：状态、触发源、时间、耗时、摘要；2. 动作：`查看收据` / `打开会话` / `再运行一次`；3. 无 Run 空态：引导立即运行或展示 `nextRunAt`；4. 有活跃 Run 时显示进行中状态而非旧成功摘要（或并列） |
| **验收** | 从 Center 点进任务 Overview，无需切 Runs 即可读最近结论 |
| **建议测试** | 组件测试：给定 summary+runs fixture 渲染摘要与按钮；手动：跑一次后回 Overview |
| **估时** | M（1d） |

---

### T-P0-4 · 手动运行 / 进行中状态实时刷新

| 项 | 内容 |
|---|---|
| **目的** | 消除「点了立即运行仍像已计划/没动静」 |
| **优先级** | P0 |
| **依赖** | 无（可与 P0-1 并行） |
| **主要落点** | `AutomationCenter.tsx` 数据订阅；electron 侧 run 更新事件 / IPC（application-service `runNow` 后 `void runner.run`） |
| **改动要点** | 1. Run 状态迁移时推送或短轮询刷新当前 detail/runs；2. 创建后若停留在新 Run 收据页，徽章从 scheduled → queued/preparing/running → 终态；3. runner `.catch(() => {})` 至少打日志或表面失败（避免静默） |
| **验收** | 手动 Run 过程中 UI 状态 30s 内可见推进；失败有可见错误 |
| **建议测试** | 手动点立即运行观察；可选集成测 mock runner 步进状态 |
| **估时** | M（0.5–1d） |

---

### T-P0-5 · 定义级 `lastRunAt` / 健康字段回写

| 项 | 内容 |
|---|---|
| **目的** | Overview 健康区「上次运行」与真实终态一致 |
| **优先级** | P0（偏正确性） |
| **依赖** | runner/outcome 终态路径 |
| **主要落点** | `apps/desktop/electron/main/automation-outcome-controller.mjs`；`packages/runtime-node/src/automation-store.mjs`（字段已支持）；scheduler 中 once 路径已有 `lastRunAt` 参考 |
| **改动要点** | 1. 任意 Run 进入终态（succeeded/failed/cancelled/…）更新 definition.`lastRunAt`；2. 与 `consecutiveFailures` / auto-pause 决策同路径，避免只更新失败计数不更新时间；3. manual 与 scheduled 一视同仁 |
| **验收** | 手动成功后 `definitions.json` 中 `lastRunAt` 非 null，且 UI 健康区显示该时间 |
| **建议测试** | outcome-controller 单测；对照本机当前 `lastRunAt: null` 的回归 |
| **估时** | S–M（0.5d） |

---

## 3. P1 任务（可达性与组织）

### T-P1-1 · 自动化会话按 origin workspace 投影到侧栏

| 项 | 内容 |
|---|---|
| **目的** | 在 `peer-knowledge` 等 origin 工作区侧栏能看到自动化会话（可选分组） |
| **优先级** | P1 |
| **依赖** | 无强依赖；建议 P0 完成后做 |
| **主要落点** | `automation-runner.mjs` 创建会话时写入 `automationOrigin`（已有）+ **originWorkspacePath**（需明确字段或复用 origin）；`packages/conversation-store/src/index.mjs` `listConversationsByWorkspace`；`App.tsx` / bootstrap 拉列表 |
| **改动要点（二选一或组合）** | **A.** 列表过滤：`workspacePath === active` **或**（`automationOrigin` 存在且 originWorkspace === active）；**B.** 创建会话时 `workspacePath` 仍为 execution，但 index 增 `originWorkspacePath` 供过滤；**C.** 不改 list API，侧栏额外 merge「该 workspace 下 automations 的 conversationId」 |
| **推荐** | A/B：保留 execution 路径用于工具 cwd，投影用 origin |
| **非目标** | 不要默认把侧栏变成全局所有 worktree 混排 |
| **验收** | worktree 执行的自动化会话出现在 origin 工作区列表（带「自动化」标识更佳） |
| **建议测试** | conversation-store 单测过滤矩阵；手动跑 work_in_workspace 任务后看侧栏 |
| **估时** | M–L（1–2d） |

---

### T-P1-2 · 会话头「来自自动化」回跳 Run

| 项 | 内容 |
|---|---|
| **目的** | 从会话回到不可变收据，闭环双向导航 |
| **优先级** | P1 |
| **依赖** | `automationOrigin` 字段可用（runner 已写 kind/automationId/runId） |
| **主要落点** | 聊天顶栏/会话 meta UI；导航到 Automation Center Run 视图 |
| **改动要点** | 展示「来自自动化 · {name} · Run」；点击打开对应 RunReceipt |
| **验收** | 自动化会话 → 一键回 Run Detail；普通会话无此条 |
| **估时** | S–M（0.5–1d） |

---

### T-P1-3 · Automation Center 列表一行最近摘要

| 项 | 内容 |
|---|---|
| **目的** | 跨任务扫一眼最近结果，无需点进每个任务 |
| **优先级** | P1 |
| **依赖** | T-P0-1；summary 聚合 API/字段 |
| **主要落点** | Center 列表行组件（`AutomationCenter.tsx` 列表区 ~status/nextRun）；后端 list summaries 是否已带 last run |
| **改动要点** | 每行：状态点 + 一行最近摘要截断 + 相对时间 |
| **验收** | 多任务时列表可读最近结论 |
| **估时** | M（0.5–1d） |

---

### T-P1-4 · 成功通知与回流文案（可选配置）

| 项 | 内容 |
|---|---|
| **目的** | 结果可「找上门」；点击进 Run Detail 且摘要可见 |
| **优先级** | P1 |
| **依赖** | T-P0-1；`automation-outcome-controller` 通知决策 |
| **改动要点** | 核对成功通知 payload 含 automationId/runId；文案带短摘要；默认策略可仍保守，但设置项清晰 |
| **验收** | 开启成功通知后点击落到正确 Run，摘要非空 |
| **估时** | S–M |

---

## 4. P2 任务（增强，排期后置）

| ID | 任务 | 说明 | 估时 |
|---|---|---|---|
| T-P2-1 | only-on-change 成功通知 | 与基线 §42 对齐，减少噪音 | M |
| T-P2-2 | Run 间受控历史摘要 | 供模型/用户对比，注意隐私与体积 | L |
| T-P2-3 | 本次 vs 上次结果对比 UI | Overview 或 Run Detail 次级模块 | M |
| T-P2-4 | 菜单栏/托盘最近自动化结果 | 系统级快览 | L |
| T-P2-5 | 结构化 outcome schema | 模型直接产出 summary/evidence，减少截断兜底 | L |

---

## 5. 跨切任务（质量与观测）

### T-X-1 · 日志与静默失败治理

| 项 | 内容 |
|---|---|
| **落点** | `automation-application-service` `runNow` 中 `void getRunner?.()?.run(run).catch(() => {})` |
| **要点** | catch 记录 error；可选写 run failed；开发模式 surface |
| **验收** | runner 抛错后 run 不永久假 scheduled 或有失败原因 |
| **优先级** | 建议并入 P0-4 |

### T-X-2 · 回归测试矩阵（合并到各 PR）

| 场景 | 期望 |
|---|---|
| 只读 observe 手动 Run | summary 非空；Overview 可见；lastRunAt 更新 |
| work_in_workspace + worktree | 收据有摘要；P1 后侧栏 origin 可见会话 |
| 失败 Run | 列表一行错误；Detail 非空 |
| 停留 Run Detail 点再运行 | 状态推进或新 Run 可发现 |
| 打开会话继续聊 | 历史 receipt 不变 |

### T-X-3 · 文档回写

| 项 | 内容 |
|---|---|
| 实施中若改语义 | 更新 `automation-run-result-viewing-redesign.md` 或主设计 / ADR |
| 完成后 | 在代码仓 CHANGELOG / PR 描述链到本清单任务 ID |

---

## 6. 建议 PR 切片（代码仓执行时）

| PR | 包含任务 | 说明 |
|---|---|---|
| PR1 | T-P0-1 + 单测 | 纯数据契约，风险低、收益最高 |
| PR2 | T-P0-2 + T-P0-3 | UI 可见性与最短路径 |
| PR3 | T-P0-4 + T-X-1 + T-P0-5 | 刷新与定义健康字段 |
| PR4 | T-P1-1 + T-P1-2 | 会话可达与回流 |
| PR5 | T-P1-3 + T-P1-4 | Center 扫读与通知 |
| 以后 | P2 | 增强项 |

---

## 7. 任务依赖图

```text
T-P0-1 (summary 回填)
   ├─→ T-P0-2 (展示强化)
   ├─→ T-P0-3 (Overview 最近结果)
   └─→ T-P1-3 (Center 一行摘要)

T-P0-4 (刷新) ──→ T-X-1 (日志)
T-P0-5 (lastRunAt)  ← 与 runner/outcome 终态同 PR 更佳

T-P1-1 (侧栏投影) ──→ T-P1-2 (会话头回跳)
T-P1-4 (通知) 依赖 T-P0-1
P2-* 全部后置
```

---

## 8. 验收总关卡（P0 完成定义）

P0 全部完成后，产品应满足：

1. 新成功/失败 Run 的 `receipt.summary` 或等价错误文案 **非空**；
2. Runs 列表与 Run Detail **直接可读结论**；
3. Overview 有 **最近一次结果** 模块；
4. 手动运行时状态 **会推进** 或失败可见；
5. `lastRunAt` 与真实终态一致；
6. **仍不要求** 必须打开会话才能知道「这次怎样了」。

P1 额外满足：origin 工作区可发现自动化会话，并能回跳 Run。

---

## 9. 明确不在清单内

- 改 grant / 权限模型；
- 取消 worktree 隔离；
- 自动化永久单会话模式；
- 重做 Automation 创建向导；
- 本知识库仓库提交可执行代码。

---

## 10. 下一步

1. 评审本清单 P0 切片（PR1→PR3）是否同意；
2. 在 `peer_agent` 按 PR1 开工：`T-P0-1` summary 回填；
3. 每完成一个任务，用本机「每日更新回顾」或最小 fixture 做一次手动验收。
