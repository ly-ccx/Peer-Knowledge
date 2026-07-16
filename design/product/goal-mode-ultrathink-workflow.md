# 真正的 Goal 模式设计：ultrathink + workflow 自驱闭环（完整技术文档）

> 创建时间：2026-06-30
> 最后更新：2026-07-04
> 状态：已定稿（Approved）— 首批落地已完成（2026-07-03，三态 ChatMode、wire 值迁移、防偏航 re-anchor/drift/verification gate；ADR 41 已按 B2-b 修订为 plan/goal 批准后执行段合一，共用自驱 Runner）。**自驱编排两切片已落地（2026-07-03）：Slice A（DoD-as-Code：结构化 SuccessCriterion[] + 完成门吃可自动验证 criterion 结果 + 弱 DoD 告警）、Slice B（hooks 阶段一：goal 模式 pre-act 写盘范围守卫 + 不可逆动作逐动作确认）。详见第十八章「实现落地记录」。**
> 关联代码：`peer_agent`（本知识库只存知识，代码改动一律在该仓落地）
> 关联文档：
> - `knowledge/decisions/41-rename-goal-mode-to-plan-mode.md`（先正名腾出 "Goal" 名字；迁移已完成）
> - `knowledge/specifications/15-goal-plan-lifecycle-governance.md`（生命周期治理 / 防僵尸计划）
> - `knowledge/specifications/09-high-risk-write-scope.md`（高风险写盘范围）
> - `design/product/goal-runner-explorer-task-list.md`（Runner + Explorer 实施切片，含现状记录）

---

## 阅读指引

- 第一～四章：**核心机制**（定义、状态机、数据模型、explore→plan→act→verify 闭环、ultrathink）。
- 第五～八章：**防偏航系统**（目标契约、re-anchor、偏航检测、no-progress、停止条件、hooks 闸门、DoD/完成门）。
- 第九～十七章：**工程落地**（最少打扰、MODE_COPY 文案、闸门差异、Explorer、UI、测试、文件级落地范围、已收敛的设计决策）。
- 术语约定：**Plan 模式**＝现状已上线的“先规划、经批准、再执行”模式（wire 值 `'plan'`，ADR 41 正名后，历史 `'goal'` 已一次性归并至此）；**Goal 模式**＝本文设计的自驱目标模式（**复用 `'goal'` wire 值**——历史 `'goal'` 迁移并入 `'plan'` 并取消兼容映射后，`'goal'` 字面量腾干净重新赋自驱语义）。

---

## 一、定义与边界

### 1.1 一句话定义

> 给定**目标**和**可验证的成功标准**，Agent 用最深的推理自主跑 `explore → plan → act → verify` 的闭环，自己开 subagent、自己纠错，跑到成功标准满足再回来——而不是写完计划就停下等批准。

Plan 模式以“**批准计划**”为中心；Goal 模式以“**验证完成**”为中心。这是两者最本质的分界。

### 1.2 与 Plan 模式的根本差异

| 维度 | Plan 模式（现状/正名后） | Goal 模式（本设计） |
| --- | --- | --- |
| 交付物 | 一份计划 + 审批门 | **目标达成**（计划只是内部脚手架） |
| 控制权 | 用户主导，逐步把关 | Agent 主导，用户设边界 |
| 节奏 | 线性、每步卡审批 | 自驱循环，跑到验证通过 |
| 计划作用 | 外部审批对象 | 内部动态导航，可被 verify 反馈修订 |
| 思考深度 | 普通 effort | **ultrathink 级**推理预算（`xhigh`） |
| 中断策略 | 强制审批门 | **最少打扰**，仅在硬边界/不可逆/歧义处停 |
| 纠错 | 依赖用户介入 | **自我验证 + 自我纠错** |
| 子任务调查 | 顺带 | **subagent 并行隔离上下文** |
| 确定性约束 | Prompt 软约束 | **hooks 式硬约束**（确定性闸门） |
| 完成依据 | 子任务完成记录 + 审批 | DoD 达标 + Evidence + Verification Gate |

灵感来源是 Claude Code 的工作流范式（explore-plan-code-commit + subagents + hooks + thinking budget），但落到 Peer Agent 自己的 System Context 分层、`GoalPlan + runner` 状态模型与运行时闸门体系上。

### 1.3 适用与不适用

- **适用**：目标明确、成功标准可验证、用户授权 Agent 自主推进（“把 bug 修好并让测试通过”“把这套文档整理到可发布”）。
- **不适用**：需求本身未定；用户想逐步把关每一步；成功标准无法客观判定。这类应走 Plan 模式。
- **本文范围（in-scope）**：Goal 模式的完整技术设计与在 `peer_agent` 的落地范围建议。
- **本文范围外（out-of-scope）**：在 `peer_agent` 仓实际写代码（另起 ADR/计划）；Plan 模式自身行为的再改动；商业化/定价等非机制议题。

---

## 二、完整状态机

沿用 task-list 已确认的**收窄版状态模型**：不新增独立 `GoalSession` / `GoalRun` 表，当前 conversation 下仍活跃的最新 `GoalPlan` 即为 active goal。状态分三层：

### 2.1 三层状态

**① `GoalPlan.status`（目标/计划整体生命周期）**

```text
drafting → awaiting_approval → approved → executing → (paused) → completed
                                                    ↘ cancelled
                                                    ↘ failed
```

**② `GoalPlan.runner.status`（自驱推进器运行态）**

```text
idle / running / exploring / paused / blocked / completed / failed
```

> 注：`budget_exhausted` 状态自 2026-07-01 起**弃用**——次数/轮次预算熔断（`maxTurns`/`maxToolCalls`）已从 `peer_agent` 移除，不再作为停止条件。防失控改由 **no-progress 检测 + `blocked` + 权限拒绝 + Evidence 强制** 兜底（见第五、七章）。枚举保留仅为向后兼容旧数据。

**③ `GoalPlan.tasks[].status`（子任务 Evidence 进度）**

```text
pending / running / completed / failed / cancelled / waiting_user
```

`completed` 必须带 `evidenceRefs`（存储层强制，见 goal_update_task 契约）。

### 2.2 runner 状态迁移图

```text
        approve
 idle ──────────► running ──────────────────► completed   (DoD 达标 + Verification Gate 通过)
                   │  ▲
        need facts │  │ report back
                   ▼  │
               exploring
                   │
     no-progress / │ permission-deny /
     ambiguity /   │ irreversible-needs-confirm
     out-of-scope  ▼
                blocked ───(用户澄清/放行)──► running
                   │
        unrecoverable error
                   ▼
                failed
```

- `running ⇄ exploring`：需要更多事实时派 Explorer，返回后回到 running。
- `running → blocked`：命中停止条件（第五章）时转 `blocked` 并附 `blockedReason`，等待用户。
- `blocked → running`：用户澄清/放行后恢复。
- `running → completed`：**仅当** DoD 全部达标且 Verification Gate 通过（第八章）。
- `* → failed`：不可恢复错误。
- `paused`：用户手动暂停；可恢复。

---

## 三、数据 / 协议模型

以 task-list 的 `GoalRunnerState` 草案为基线，本文补充目标契约、成功标准、偏航/进展跟踪三组设计增量字段。**标注**：✅=已在 `peer_agent` 落地；🆕=本设计新增建议。

### 3.1 runner 运行态（基线，✅ 已落地主体）

```ts
export type GoalRunnerStatus =
  | 'idle' | 'running' | 'paused' | 'exploring'
  | 'blocked' | 'completed' | 'failed'
  | 'budget_exhausted'; // ⚠️ 弃用，仅兼容旧数据

export type GoalRunnerIntent =
  | 'execute' | 'verify' | 'explore' | 'synthesize' | 'block';

export interface GoalRunnerState {
  readonly enabled: boolean;
  readonly status: GoalRunnerStatus;
  readonly intent?: GoalRunnerIntent;
  readonly currentTaskId?: string;
  readonly turnCount: number;         // ✅ 仍作可观测计数，但不再触发熔断
  readonly toolCallCount: number;     // ✅ 同上
  readonly explorerCount: number;
  readonly maxExplorers: number;      // ✅ 并发 Explorer 上限（保留）
  readonly blockedReason?: string;
  readonly lastError?: string;
  readonly updatedAt: string;
  // maxTurns / maxToolCalls 已移除熔断语义（2026-07-01）
}
```

### 3.2 目标契约（🆕 防偏航核心）

```ts
export interface GoalContract {
  readonly goal: string;                        // 原始目标，冻结，runner 不得改写
  readonly successCriteria: SuccessCriterion[]; // 可验证的 DoD（见 3.3）
  readonly inScope: string[];                   // 授权范围（路径/模块/动作类别）
  readonly outOfScope: string[];                // 明确边界，命中即停
  readonly reanchorEvery: number;               // 每 N 个 act 周期 re-anchor 一次；默认自适应 clamp(ceil(taskCount/3), 2, 6)
  readonly createdAt: string;
}
```

`GoalContract` 在进入 Goal 模式（计划批准）时**冻结**。runner 只能在契约内自主行动；任何对 `goal` / `outOfScope` 的“改写”都视为偏航信号（第五章）。

### 3.3 成功标准（🆕 DoD-as-Code）

```ts
export type SuccessCriterion =
  | { kind: 'command'; cmd: string; expectExitCode: number }    // 跑命令查退出码
  | { kind: 'file-contains'; path: string; pattern: string }    // 读文件断言
  | { kind: 'file-exists'; path: string }
  | { kind: 'test'; cmd: string }                               // 测试通过
  | { kind: 'manual'; assertion: string };                      // 只能人判定（降级）

export interface CriterionResult {
  readonly criterionIndex: number;
  readonly passed: boolean;
  readonly evidenceRef: string;   // Tool Result ref，禁止自我断言
  readonly checkedAt: string;
}
```

#### 3.3.1 录入形态（✅ 已拍板）

采用**混合式录入**，不强制用户手写断言：

1. **用户只给自然语言目标**（"把这个 bug 修好并让测试通过"）。
2. **Agent 在 plan 阶段翻译**：把目标拆成 `SuccessCriterion[]`，尽量落到可自动验证的 `command` / `test` / `file-contains` / `file-exists` 上。
3. **契约冻结时一并确认**：翻译出的 `successCriteria` 作为 `GoalContract`（3.2）的一部分，在**契约冻结（计划批准）时**呈现给用户核对——这是用户校正 DoD 的唯一集中入口，冻结后 runner 不得擅改。

**`manual` 类的降级规则**：

- `manual` 允许存在，但标记为**不可自动验证**；它**不参与** `post-act` 自测循环（第七章），避免"无法客观判定"的标准反复空转。
- `manual` 标准改为在 **`pre-finish` 完成门**（第七/八章）强制转成**一次用户确认**——即把它降级为"完成前的人工裁决"，而非执行途中的阻塞点。
- **弱 DoD 告警**：若某目标的 `successCriteria` **全部**为 `manual`（无任何可自动验证项），判定为**弱 DoD**并在契约冻结时告警，提示用户"该目标无法自动验证完成，Goal 模式将退化为人工确认收尾"，由用户决定是否继续或补充可验证标准。

### 3.4 进展与偏航跟踪（🆕）

```ts
export interface ProgressLedger {
  readonly lastCriteriaPassCount: number;  // 上轮达标数
  readonly noProgressStreak: number;       // 连续无进展轮数（见 5.4）
  readonly filesTouched: string[];         // 累计写过的文件（越界检测用）
  readonly taskCountAtStart: number;       // 计划初始任务数（任务膨胀检测用）
  readonly reanchorCountdown: number;      // 距下次 re-anchor 的剩余周期
}
```

> 落地建议：3.2–3.4 作为 `GoalPlan` 的伴随字段持久化，随 runner patch 一起写回；旧数据缺字段时按默认值降级读取（沿用 task-list 已验证的“缺 runner 字段仍可读取”约定）。

---

## 四、explore → plan → act → verify 自驱闭环

### 4.1 闭环总览

```
┌─────────── Goal Loop（自驱，直到 DoD 满足或触达硬边界/停止条件） ───────────┐
│                                                                            │
│  EXPLORE  ── 只读调查现状（可并行 Explorer subagent），先理解再动手         │
│     │                                                                      │
│     ▼                                                                      │
│  PLAN     ── 内部生成/修订计划（脚手架，不强制审批门）                       │
│     │                                                                      │
│     ▼                                                                      │
│  ACT      ── 执行最小步；副作用受 hooks 闸门（pre-act）约束                  │
│     │                                                                      │
│     ▼                                                                      │
│  VERIFY   ── 对照成功标准自测（post-act）；不达标 → 回 EXPLORE/PLAN 纠错     │
│     │                                                                      │
│     ├── DoD 全达标 ──► pre-finish 闸门 ──► 汇报 + Evidence ──► completed    │
│     └── 命中停止条件 ──► blocked（最少打扰式提问）                          │
└────────────────────────────────────────────────────────────────────────────┘
```

要点：
- **explore 优先**：动手前只读理解（复用 `request_explorer` 只读子agent、`batch_search` 并行检索）。
- **plan 降级为内部脚手架**：不再是“写完就停等批准”的终点，而是循环里可被 verify 反馈持续修订的中间产物。
- **verify 是一等公民**：每轮 act 后必须对照成功标准自检——这是与 Plan 模式最大的区别。

### 4.2 单轮循环伪代码

```text
loop(contract, ledger):
  # 0. 周期性 re-anchor（防目标漂移，见 5.2）
  if ledger.reanchorCountdown <= 0:
      reanchor(contract)                 # 重述 goal/successCriteria/scope
      ledger.reanchorCountdown = contract.reanchorEvery

  # 1. EXPLORE（按需）
  if facts_insufficient():
      dispatch_explorers()               # 只读、隔离上下文
      set runner.status = exploring
      return  # 等 Explorer 报告回来再进入下一 tick

  # 2. PLAN（按需修订脚手架）
  plan = revise_plan(contract, latest_evidence)

  # 3. 偏航检测（动手前，见 5.3）——命中则不 ACT，转 blocked
  drift = detect_drift(plan, contract, ledger)
  if drift: return block(drift.reason)

  # 4. ACT（最小步）——pre-act hooks 闸门（见七章）
  step = next_minimal_step(plan)
  if hooks.pre_act(step) == DENY: return block(step.deny_reason)
  result = execute(step)                 # 走既有权限审批流
  ledger.filesTouched += result.written_files

  # 5. VERIFY——post-act hooks 自动触发
  results = check_success_criteria(contract.successCriteria)  # 用 Tool Result
  passCount = count(results, passed=true)

  # 6. no-progress 检测（见 5.4）
  if passCount <= ledger.lastCriteriaPassCount and no_new_evidence(result):
      ledger.noProgressStreak += 1
  else:
      ledger.noProgressStreak = 0
  ledger.lastCriteriaPassCount = passCount

  if ledger.noProgressStreak >= 3:       # N=3 双信号
      return block("no-progress: 连续3轮无达标推进且无新证据")

  # 7. 完成判定——pre-finish 闸门（见八章）
  if all(results, passed=true):
      if hooks.pre_finish(contract, results) == OK:
          return complete(evidence=results)
      else:
          return block("verification gate 未通过")

  ledger.reanchorCountdown -= 1
  continue                               # 未达标，带失败证据回循环纠错
```

### 4.3 与既有运行时的契合

- `request_explorer` = EXPLORE 阶段的只读子agent（独立上下文，返回结构化报告 + evidence refs）。
- `goal_create_plan` / `goal_update_task` = PLAN 脚手架与 Evidence 写回。
- 既有权限审批流 = ACT 阶段执行本地能力的统一入口，Goal 模式不绕过。

---

## 五、防偏航系统

自主性越强越容易漂移。核心原则：

> **Goal 模式允许 Agent 自主执行，但不允许 Agent 自主改目标。**

### 5.1 两类“歪”

- **目标漂移**：做着做着目标变了（把“设计清楚 Goal 模式”做成“顺手重构 runtime”）。根因是把“有帮助”误当成“属于目标”。
- **路径漂移**：目标没变，但执行越来越发散（修一个 bug 却铺开无边界重构）。

### 5.2 目标契约 + 周期性 re-anchor

- **目标契约**（3.2）在批准时冻结 `goal` / `successCriteria` / `inScope` / `outOfScope`。
- **re-anchor**：每 `reanchorEvery` 个 act 周期，runner 必须重述原始目标与成功标准，并对照“我现在做的事是否仍服务于原目标”。这是对抗长任务上下文漂移的确定性动作，不靠模型自觉。
- **频率（✅ 已拍板）——随任务规模自适应**：`reanchorEvery` 默认取 `clamp(ceil(taskCount/3), 2, 6)`（任务越多、跨度越大，re-anchor 越频繁，但夹在 2–6 周期之间避免过密或过疏）；允许在 `GoalContract` 上显式覆盖为固定值。此外，下列事件**强制立即 re-anchor**（不等周期到点）：①计划被修订（增删任务 / 改 DoD）；②Explorer 返回结论回灌主上下文。二者都是漂移高发点，需即时对齐原始目标。
- runtime reminder 中的“goal runner context”快照即为 re-anchor 的载体（现状已有目标快照回灌机制，可复用）。

### 5.3 偏航检测（动手前拦截）

| 信号 | 判据 | 处置 |
| --- | --- | --- |
| 目标改写 | 计划/子任务偏离冻结的 `goal` 语义 | 转 `blocked`，请用户确认是否变更目标 |
| 文件越界 | `filesTouched` 命中 `outOfScope` 路径 | 拒绝该 act，转 `blocked` |
| 任务膨胀 | 任务数相对 `taskCountAtStart` 异常膨胀（如 > 2× 且新任务与 DoD 无映射） | 暂停扩张，re-anchor 后再判 |
| 成本异常 | 单轮工具调用/写文件量显著偏离历史均值 | 记录并降速；连续异常转 `blocked` |
| DoD 无映射 | 新增动作无法映射到任一 `successCriterion` | 视为疑似发散，要求先补 DoD 映射或放弃该动作 |

### 5.4 no-progress 检测（防死循环，替代预算熔断）

- **双信号**：一轮内既没有新的成功标准达标（`passCount` 未增），也没有产生新证据（工具结果无实质变化）。
- **阈值 N=3（✅ 已拍板，可配置）**：默认连续 3 轮双信号触发；阈值 `noProgressThreshold` 可在 `GoalContract` 上按目标复杂度覆盖（建议区间 2–5），不改默认心智。
- **达阈处置（✅ 已拍板）——停下问人，绝不冒充完成**：达阈值后一律转 `blocked`（**不**静默产出"尽力而为的 `completed`"）。`blockedReason` 中**附带一份尽力而为小结**作为参考材料，包含：已尝试的路径、已产生的证据（`evidenceRef`）、哪些 `successCriteria` 仍未达标；并给出**结构化选项**（换提示重试 / 放宽范围或改目标 / 交回用户接手）。即"尽力而为结论"只作为 `blocked` 的**附件**，绝不改写为 `completed` 状态。
- 这是 2026-07-01 移除次数/轮次熔断后的**主兜底**，比"跑够 N 次就停"更贴合"有没有真在推进"。

### 5.5 停止条件（转 blocked / 需要用户）

runner 必须在以下情况停到明确状态，而非硬闯：
1. 目标 / 成功标准有歧义，无法自洽推断；
2. 命中 `outOfScope` 硬边界；
3. 不可逆 / 高风险操作需放行（删除、覆盖、`git` 强制、push、release 等）；
4. 权限被拒绝或需要外部凭据；
5. no-progress 连续 N=3；
6. 当前证据与目标冲突，需用户裁决。

runner **不**做的事：不把每步伪装成用户消息；不绕过权限审批；不跳过 Evidence；不直接执行本地能力（一律走既有能力/审批通道）。

---

## 六、防偏航—闸门—完成门的关系

- 第五章＝**软/半确定性**的偏航与进展判断（模型可参与判断，但阈值确定）。
- 第七章＝**确定性 hooks 闸门**（不依赖模型自觉，命中即拦）。
- 第八章＝**完成门**（DoD + Verification Gate + Evidence）。

三者叠加：偏航检测防“方向错”，hooks 闸门防“危险动作”，完成门防“假装完成”。

---

## 七、hooks 式确定性闸门

把“必须做 / 绝不能做”从 Prompt 软约束升级为**确定性闸门**（借鉴 CC hooks 的 deterministic control 思想）。与 Plan 模式的区别：Plan 是“**每步**都停等批准”，Goal 是“**只在闸门命中时**才停”。

| Hook 时机 | 触发点 | 具体规则（命中处置） |
| --- | --- | --- |
| `pre-act` | 每次写副作用前 | ① 高风险写盘范围校验（复用 `specifications/09-high-risk-write-scope.md`），越界→DENY；② `outOfScope` 路径→DENY；③ 不可逆操作→转 `on-irreversible` |
| `post-act` | 每次写副作用后 | 自动触发 VERIFY：跑相关 `successCriteria`（如自动跑受影响测试），结果写入 `CriterionResult` |
| `pre-finish` | 声明完成前 | 强制校验所有 `successCriteria.passed == true` 且各带 `evidenceRef`；否则禁止 `completed`，转 `blocked` |
| `on-irreversible` | 删除/覆盖/`git` 强制/push/release | 一律**最少打扰式确认**，用户放行前不执行 |

**落地粒度（✅ 已拍板）——分阶段，不过早抽象**：

- **阶段一（先拿安全价值）**：只**硬编码 3 条高价值确定性规则**，不建框架——
  1. **写盘范围校验**（`pre-act`，复用 `specifications/09-high-risk-write-scope.md`，越界 DENY）；
  2. **不可逆操作拦截**（`pre-act` → 转 `on-irreversible` 单动作确认）；
  3. **完成门**（`pre-finish`，DoD + Verification Gate + Evidence 齐备才允许 `completed`）。
- **阶段二（等复杂度到位再抽象）**：当确定性规则增至 **≥2 条新增需求**（即超出上述 3 条硬编码、出现反复新增）时，才抽出**最小 hook-point 注册表**（`registerHook(timing, matcher, handler)`），把已硬编码规则平滑迁入。
- **理由**：避免过早抽象——先用 3 条硬编码规则拿到确定性安全价值，框架化推迟到"规则确实在增长"时再做。

---

## 八、成功标准 DoD-as-Code + 完成门

### 8.1 DoD-as-Code

- 进入 Goal 模式时，目标须附带**可验证的成功标准**（`SuccessCriterion[]`，见 3.3）。
- 每轮 VERIFY 用工具**实测**成功标准（跑测试 / 跑 lint / 读文件 / 查退出码），以 **Tool Result 作为达标证据**，而非自我断言。这与项目 Evidence discipline 一脉相承。
- 未达标则带失败证据回循环纠错；达标才允许收口。

### 8.2 Verification Gate（完成前的硬门）

`pre-finish` 闸门执行：

```text
gate(contract, results):
  assert len(results) == len(contract.successCriteria)
  for r in results:
      assert r.passed == true
      assert r.evidenceRef is a real Tool Result ref   # 禁止空/伪造
  assert every task marked completed has evidenceRefs   # 沿用 store 约束
  → 通过才允许 runner.status = completed
```

### 8.3 Evidence 约束

- `completed` 子任务必须带 `evidenceRefs`（存储层已强制）。
- 完成汇报必须给出：达成的 DoD 清单 + 每项对应的 evidence ref + 改动文件清单。
- 只有口头“做好了”而无 evidence → Verification Gate 不通过。

---

## 九、最少打扰策略与中断触发点

Goal 模式默认**推进而非等待**，只在下列触发点打断用户（即第五章停止条件的用户视角）：

1. 目标 / 成功标准歧义；
2. 触达 `outOfScope` 硬边界；
3. 不可逆 / 高风险操作需放行；
4. 权限不足 / 需外部凭据；
5. no-progress 达阈值（默认 N=3，可配置）；
6. 目标与验证结果冲突。

其余情况一律自主继续。打断时给**结构化选项**（复用 request_user_input 的 options），让用户一键决策，而非开放式追问。因 no-progress 达阈值而打断时，附上"尽力而为小结"（已试路径 / 已得证据 / 未达标项）供用户判断，但状态仍是 `blocked` 而非 `completed`（见 5.4）。

---

## 十、MODE_COPY.goal 文案草案

> 落地位置：`peer_agent` 的 `mode-copy.mjs` 新增 `MODE_COPY.goal`。以下为草案文案（中文语义，实际以工程措辞为准）。

```text
Mode: goal.
目标自驱模式。用户给出目标与可验证的成功标准，你在已冻结的目标契约（goal / successCriteria / inScope / outOfScope）内自主推进，跑 explore → plan → act → verify 闭环，直到成功标准全部达标并通过完成门，或命中停止条件。

优先深度推理（effort 默认 xhigh，宁可多想一步）。计划是内部脚手架，可随验证反馈修订，不作为等待审批的终点。

每轮 act 后必须对照成功标准用工具实测（Tool Result 作为证据），不达标就带失败证据继续纠错。禁止自我断言完成：声明完成前必须通过 Verification Gate（所有 successCriteria.passed 且各带 evidenceRef）。

自主执行，但绝不自主改目标。命中以下情况必须停到 blocked 并最少打扰式请求用户：目标/标准歧义、触达 outOfScope、不可逆/高风险操作、权限不足、连续 3 轮无进展、证据与目标冲突。

不把每步伪装成用户消息；不绕过权限审批；不跳过 Evidence；不直接执行本地能力。周期性 re-anchor 原始目标，防止漂移。
```

---

## 十一、运行时闸门与 Plan 模式差异

| | Plan 模式 | Goal 模式 |
| --- | --- | --- |
| 运行时闸门 | “未批准即全阻断”所有副作用工具 | **不**走全阻断分支；改为 hooks 按操作类型判定（pre-act/on-irreversible） |
| 审批门 | 强制（计划必须批准才执行） | 无常规审批门，仅硬闸门与停止条件 |
| 默认 effort | 普通 | `xhigh`（ultrathink 语义） |
| 停等粒度 | 每步 | 仅闸门命中 |
| wire 值 | `'plan'`（ADR 41 正名，历史 `'goal'` 已归并至此） | **复用 `'goal'`**（历史 `'goal'` 迁移并入 `'plan'`、取消兼容映射后重新赋自驱语义） |
| 复用资产 | `goal_create_plan` 等工具 | 同一套 plan 工具作内部脚手架 + `request_explorer` + hooks |

**共存**：两者是并列的 `ChatMode`，共享底层 plan/store 设施；差异体现在 ①模式文案（`MODE_COPY`）②是否强制审批门 ③默认 effort ④hooks 闸门策略。用户按任务性质二选一。命名决策已拍板：**新 Goal 模式继续叫 "Goal" 并复用 `'goal'` wire 值**；历史 `'goal'` 别名当前虽被正名兼容映射为 `'plan'`（见 ADR 41），但落地新 Goal 前须先对存量会话做**一次性数据迁移**（持久化 `'goal'`→`'plan'`），随后**取消 `normalizeChatMode` 的 `goal→plan` 兼容映射**，把 `'goal'` 字面量彻底腾干净后重新交给新 Goal 模式（详见第十六章决策 5）。

### 11.1 运行中不自动互转模式（✅ 已拍板）

Goal 与 Plan 是并列 `ChatMode`，**运行途中不做自动模式翻转**，以保持用户心智干净、避免"自主性被意外升/降级"：

- **Goal 途中遇高风险 / 不可逆操作**：**不**静默降级回 Plan 走整模式审批，而是走已有 `on-irreversible` 闸门的**单动作最少打扰确认**（第七章）——只对该动作停一次问一次，放行后仍留在 Goal 自驱。粒度是"逐动作闸门"，比"整模式降级"更轻、干扰更小。
- **Plan 批准后执行段**：Plan 计划批准后**不自动改写 ChatMode / 不静默升格为 Goal 契约**；但按照 ADR 41 的 B2-b 修订，批准后的托管执行段与 Goal 共用同一个自驱 Runner，执行 turn 以 `mode:'goal'` 复用防偏航、Verification Gate 与 pre-act 护栏。这里的“合一”是执行段复用，不是模式翻转。
- **净结论**：运行中模式不翻转。所谓"转换"要么是 Goal 内的**逐动作硬闸门**（高风险确认），要么是**用户显式**切换 `ChatMode`；系统不代替用户改变模式语义。Plan 批准后的自动推进来自用户对计划的批准授权，而不是系统把 Plan 变成 Goal。

---

## 十二、Explorer 只读隔离调度

- 复用 `request_explorer`（只读 Explorer 子agent，独立上下文）。
- Goal 模式**鼓励**把“大范围调查 / 多文件定位 / 交叉验证”拆给并行 Explorer，主循环上下文保持精简，避免被海量检索结果淹没。
- 并发上限由 `runner.maxExplorers` 控制（保留字段）。
- 边界：Explorer 严格只读；写操作只在主循环、受 hooks 闸门约束。
- 调度时机：`facts_insufficient()` 为真时进入 `exploring`，Explorer 报告回来后回到 `running`。

---

## 十三、UI 表达（Goal Dashboard）

Goal 模式的 UI 应始终让用户“看得见方向、随时能打断”：

- **目标契约区**：常显 `goal` + `successCriteria`（含每项达标状态 ✅/⬜）+ `inScope/outOfScope`。
- **当前阶段**：explore / plan / act / verify + `runner.status` + `intent`。
- **进展条**：DoD 达标数 / 总数；`noProgressStreak` 预警。
- **下一步理由**：runner 即将做什么、为什么（可打断）。
- **停止卡片**：`blocked` 时展示 `blockedReason` + 结构化选项（放行/澄清/改目标/停止）。
- **Evidence 抽屉**：完成时列出每项 DoD 的 evidence ref 与改动文件清单。

设计语言遵循本仓 `design/visual/` 的 Peer Frost 规范。

---

## 十四、测试策略

| 层次 | 测试点 |
| --- | --- |
| 状态机 | 三层状态迁移合法性；`blocked ⇄ running`；`budget_exhausted` 弃用后旧数据可读 |
| 目标契约 | 冻结后 runner 不能改写 `goal`；`outOfScope` 命中→拦截 |
| 偏航检测 | 目标改写/文件越界/任务膨胀/成本异常各触发对应处置 |
| no-progress | 连续 3 轮双信号→`blocked`；有进展则清零 |
| hooks 闸门 | pre-act 越界 DENY；on-irreversible 强制确认；pre-finish 未达标禁止 completed |
| 完成门 | 缺 evidenceRef 不得 completed；DoD 未全达标不得完成 |
| Explorer | 只读隔离；报告带 evidence refs；并发不超 `maxExplorers` |
| 向后兼容 | 旧 plan 缺 `runner`/契约字段仍可读取（默认值降级） |
| Fake runtime | 沿用 task-list Slice 2 的 Fake Runtime 驱动 runner 全闭环 |

---

## 十五、`peer_agent` 文件级落地范围建议

> 仅为方向建议，正式落地另起 ADR/计划；本知识库不改代码。

| 模块 | 改动方向 |
| --- | --- |
| `preferences.ts` | `ChatMode` 恢复 `'goal'` 为并列合法值（自驱语义，与 `'plan'` 并列）；前置条件：先对存量会话一次性迁移 `'goal'→'plan'`，再从 `normalizeChatMode` 移除 `goal→plan` 兼容映射，避免旧数据被误解析为 Plan |
| `mode-copy.mjs` | 新增 `MODE_COPY.goal`（第十章草案）：explore/plan/act/verify + DoD 自验证 + 最少打扰 |
| 运行时闸门 | Goal 模式**不**走“未批准即全阻断”分支；改为 hooks 式按操作类型判定 |
| effort 默认值 | Goal 模式默认 `xhigh` |
| `GoalPlan` 存储 | 增加 `GoalContract` / `SuccessCriterion[]` / `ProgressLedger` 伴随字段（缺字段降级） |
| runner | 加入 re-anchor、偏航检测、no-progress、Verification Gate 逻辑 |
| Explorer 调度 | Goal 模式放宽/鼓励并行 Explorer（受 `maxExplorers`） |
| 新增 hooks 层 | pre-act / post-act / pre-finish / on-irreversible 确定性闸门（新模块） |
| UI | Goal Dashboard（第十三章） |

---

## 十六、已收敛的设计决策

> 本章原为「开放问题（待评审拍板）」。截至最后更新，问题 1–6 已全部收敛为设计决策（下列条目均标注**已拍板**并给出正文出处）。保留原始问题描述（删除线）以便追溯决策脉络。

1. ~~**成功标准录入形态**：自然语言 + Agent 自行翻译成 `SuccessCriterion`？还是要求用户给明确命令/断言？（`manual` 类如何降级？）~~ → **已拍板**（详见 3.3.1）：采用**混合式录入**——用户给自然语言目标，Agent 在 plan 阶段翻译成 `SuccessCriterion[]`，契约冻结时呈现给用户确认。`manual` 类降级为 **`pre-finish` 完成门的一次人工裁决**（不参与 `post-act` 自测）；若标准全为 `manual` 则判**弱 DoD**并在冻结时告警。
2. ~~**hooks 落地粒度**：先硬编码几条高价值规则（写盘范围 / 不可逆 / 完成门），还是先做通用 hooks 框架？~~ → **已拍板**（详见第七章）：**分阶段**——阶段一只硬编码 3 条确定性规则（写盘范围 / 不可逆操作 / 完成门），不建框架；阶段二当规则确实增长（≥2 条新增需求）时再抽最小 hook-point 注册表。避免过早抽象。
3. ~~**no-progress 阈值**：N=3 是否合适？达阈值后是“停下问人”还是“给尽力而为结论 + 证据”？~~ → **已拍板**（详见 5.4 / 第九章）：保留 **N=3 默认但可配置**（`noProgressThreshold`，建议 2–5）；达阈值后**停下转 `blocked` 问人**，并把"尽力而为小结"（已试路径 / 已得证据 / 未达标项）作为 `blocked` 附件 + 结构化选项，**绝不冒充 `completed`**。
4. ~~**Goal ⇄ Plan 运行中互转**：Goal 跑着遇到高风险，是否降级回 Plan 走审批？反之 Plan 批准后能否升格 Goal 自驱？~~ → **已拍板并被 B2-b 补充**（详见 11.1 与 ADR 41）：**运行中不自动翻转模式**。Goal 途中遇高风险不降级整模式，改走 `on-irreversible` 的**单动作确认**；Plan 批准后不静默改写为 Goal 契约，但批准后的托管执行段与 Goal 共用自驱 Runner。
5. **wire 值归属（已拍板 ✅ 已落地 2026-07-03）**：新 Goal 模式**继续叫 "Goal" 并复用 `'goal'` wire 值**。落地路径（先对存量会话一次性迁移 `'goal'→'plan'` → 取消 `normalizeChatMode` 的 `goal→plan` 兼容映射 → `'goal'` 腾干净后重新承载自驱语义）已在 `peer_agent` 仓完成并验证：`ChatMode = 'chat' | 'plan' | 'goal'`，`conversation-store` 一次性数据迁移（marker 防重复），全链路撤销兼容映射。（原“另起 `'goal-run'` 独立新值”方案已废弃。）
6. ~~**re-anchor 频率**：`reanchorEvery` 固定值还是随任务规模自适应？~~ → **已拍板**（详见 3.2 / 5.2）：**随任务规模自适应**，默认 `clamp(ceil(taskCount/3), 2, 6)`，可在 `GoalContract` 覆盖为固定值；另在**计划修订**与 **Explorer 返回**时强制立即 re-anchor。

---

## 十八、实现落地记录（2026-07-03，自驱编排两切片）

> 本章记录「自驱编排」层两个关键增强在 `peer_agent` 的实际落地，均通过 typecheck（6/6 项目 Done）与 goal 相关测试（148/148 pass）。提交策略：验证通过后向用户展示 diff 再定是否 commit/push。

### 18.1 Slice A：DoD-as-Code（成功标准结构化 + 完成门吃验证结果）

- **数据模型**（`apps/desktop/electron/main/goal-plan-store.mjs`）：`successCriteria` 从「字符串数组」升级为结构化 `SuccessCriterion[]`，`kind ∈ {command, test, file-contains, file-exists, manual}`；新增伴随字段 `criterionResults`（`criterionId + passed + evidenceRef`）。**向后兼容**：纯字符串或缺 `kind` 的存量标准归一为 `manual`，缺字段数据降级读取，不破坏存量计划。
- **工具契约**（`goal_create_plan` schema）：`successCriteria` 允许传结构化对象数组（可选，向后兼容字符串），不破坏 `goal`/`tasks` 必填。
- **完成门**（`evaluateVerificationGate`）：非 `manual` 的 criterion 必须有 `passed=true` 且带 `evidenceRef` 的 `CriterionResult` 才放行；`manual` 降级为 `pre-finish` 一次人工确认；全 `manual` 判**弱 DoD 告警**。
- **提示词接线**（`prompt/sources/goal-runner-source.mjs`）：section 标题升级为 `success criteria (Definition of Done):`，渲染结构化 `- [verify] (kind) description` 与验证状态；明确要求模型 **post-act 对可自动验证标准跑验证并把 Tool Result 作为该 criterion 的 evidence 回写**——模型驱动执行 + 完成门机器校验，**不给 runner 新开跑命令的旁路执行路径**（遵守 AGENTS.md 非协商运行时链）。
- **验证**：`goal-plan-store` / `goal-runner` / `goal-runner-antidrift` / `goal-runner-source` / `goal-plan-source` 合计 112/112 pass。

### 18.2 Slice B：hooks 确定性闸门·阶段一（写盘范围守卫 + 不可逆动作确认）

对齐第七章「阶段一只硬编码规则，不建通用框架」。落点：`apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs` + `projected-tool-executor.mjs`。

- **① pre-act 写盘范围守卫**（`evaluateWriteScope`）：`write_file`/`edit_file` 的目标 `path`——
  - 越出 workspace（绝对路径越界或 `..` 逃逸）→ `goal_scope_out_of_workspace` **DENY**；
  - 命中活跃计划 `boundaries.outOfScope` → `goal_scope_out_of_bounds` **DENY**。仅对「像路径/glob」的边界条目匹配（含 `/`、`*`、`.ext`、或单 word-like token）；纯描述性文字（含空格 / CJK，如「不改审批语义」）豁免，避免误伤。
- **② on-irreversible 不可逆动作确认**（`detectIrreversibleAction`）：`write_file` 带 `allow_overwrite=true`；`bash` 命中 `rm -rf`/`git push`/`git --force`/`git reset --hard`/`git clean`/`npm|yarn|pnpm|tnpm publish`/`git tag` → 标记 `requiresConfirmation`。执行体（`projected-tool-executor`）经 `requestPermission` 逐动作确认，未获批则复用 `buildGoalModeDenial` 以 `goal_irreversible_denied` 结构化失败。
- **③ 完成门**：已由 Slice A 的 `evaluateVerificationGate` 落地，本切片不重复造。
- **模式差异**：goal 模式**不施加**整模式「计划审批门」（那是 plan 模式独占，见 11.1）；goal 只做上述 pre-act 守卫 + 逐动作确认。闸门是 `PermissionGrant` 之前的能力准入判定，不绕过 Runtime Projection。
- **接线**：`evaluateGoalModeGate` 补收 `args`/`workspacePath`/`boundaries`；新增 `resolveActivePlanBoundaries` 从 store 取活跃计划边界；`buildGoalModeDenial` 支持 `detail` + 新增 3 条中英 denial 文案。
- **验证**：`goal-mode-gate.test.mjs` 36/36 pass（原 11 + 新增 25：`evaluateWriteScope` 9、`detectIrreversibleAction` 7、goal 模式 gate 6、`resolveActivePlanBoundaries` 3）。

### 18.3 已知边界与后续

- `projected-tool-executor.test.mjs` 在 plain `node --test` 下因 `electron` 的 `webContents` 导出缺失而失败——**预存在环境问题**（需 electron 测试环境），已 `git stash` 验证未改动 baseline 同样失败，非本次改动引入。
- 阶段二（通用 hook-point 注册表）仍按第七章约定**暂缓**，待确定性规则确实增长（≥2 条新增需求）再抽象。
- UI Goal Dashboard（第十三章）仍未落地，另行规划。

---

## 十七、参考

- 正名前置与迁移现状：本仓 `knowledge/decisions/41-rename-goal-mode-to-plan-mode.md`。
- 现有 Explorer / 任务切片与状态模型：本仓 `design/product/goal-runner-explorer-task-list.md`。
- 生命周期治理 / 防僵尸计划：本仓 `knowledge/specifications/15-goal-plan-lifecycle-governance.md`。
- 高风险写盘范围：本仓 `knowledge/specifications/09-high-risk-write-scope.md`。
- CC 机制出处（Anthropic 官方 `code.claude.com/docs`）：common-workflows（explore-plan-code-commit）、sub-agents、hooks-guide、slash-commands；thinking budget 阶梯见 Anthropic best-practices 与 Simon Willison 对 `cli.js` 反编译（`ultrathink ≈ 31999 tokens`，`think ≈ 4000`）。
