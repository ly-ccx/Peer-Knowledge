# Goal 质量评审与自我修复环

> 创建时间：2026-08-13
> 最后更新：2026-08-13
> 用户文案：界面只说检查记录，不说关卡；内部四层检查名仅供研发对齐
> 文档状态：目标方案 / 待分期实施
> 适用范围：Peer Desktop Agent / Goal / Plan 执行段、TaskOverview、Result Review
> 关联代码仓：`peer_agent`（本知识库只存知识，代码改动一律在该仓落地）
> 代码审计基线：`peer_agent` / `PeerAgent/0.0.4` / `aa770e8`（2026-08-12）
> 关联文档：
> - `design/product/goal-mode-ultrathink-workflow.md`
> - `design/product/goal-mode-codex-cc-workflow.md`
> - `design/product/agent-mode-default-and-adaptive-planning.md`
> - `design/product/task-worktree-delivery-product-design.md`
> - `design/product/peer-2-0-workbench-flow.md`
> - `design/product/peer-task-flow-action-right-correction.md`

---

## 1. 方案摘要

本文补齐 Peer 在现有 Goal 完成门之上缺失的 **PDCA Check / Act**：

> **过程完成不等于结果够好，质量过线也不等于用户已接受。Goal 必须先过完成门，再过质量评审；不够好就自己返工。有副作用的 Goal 过线后进入「结果待你验收」，确认验收仍是收口；「还不行」打开这条任务对应的会话，用户在对话里说明哪里不对，Peer 据此返工。用户验收确认的是意图，不再承担第一轮质检。**

它不另建任务系统。现有对象继续各司其职：

| 对象 | 继续负责 | 不再误用为 |
|---|---|---|
| GoalPlan / Runner | 目标、任务、推进、修订 | 质量过线或用户已接受的唯一依据 |
| `verificationGate` | 过程完成：叶子完成、Evidence、可自动验证标准 | 结果质量裁判 |
| Quality Review | 对照目标与产物，判断能不能交卷 | 用户可见的第六步向导 |
| Repair Loop | 把差距写成修复项并回到 Do；也承接会话里「还不行」的说明 | 无限重试、伪装完成，或另开意见表 |
| `result_ready` / `resultAcceptance` | 过线后的意图确认收口；点确认验收才算完成 | 第一轮质检 |

用户侧看到四态，后两态都要人，但职责不同：

```text
Peer 正在处理     实现、自检、自行返工
结果待你验收      Peer 认为可以交卷，请确认是不是你要的
已完成            你点了确认验收
需要你            执行中无法自判的一个业务问题
```

质量评审和自我修复发生在「正在处理」内部，对用户默认无感。  
确认验收不能省；「需要你」也不能和「待验收」并成一层。

---

## 2. 为什么现有闭环不够

### 2.1 当前真实流程

现有产品主线已经成立，而且和设计文档一致：

```text
发起任务
→ 判断要不要 Goal
→ 生成 GoalPlan
→ Runner 执行
→ verificationGate
→ result_ready
→ 用户确认验收
```

这很符合 Plan 模式的收尾，也符合当前工作台第三桶「结果待验收」的语义：`completed` 且未写入 `resultAcceptance` 就投影为 `result_ready`。

对照 PDCA：

| PDCA | 当前实际 | 缺口 |
|---|---|---|
| Plan | 生成 Goal、拆任务、翻译 `successCriteria` | 有 |
| Do | Runner 按任务推进，可修订计划 | 有 |
| Check | 叶子完成 + Evidence + 部分 command/test/file 门 | 只问「做没做完」 |
| Act | 过门后等人验收；验证失败才回到 executing | 没有对照产物的自我修复环 |

### 2.2 现有完成门检查什么

`evaluateVerificationGate` 已经落地，且必须保留。它检查：

- 叶子任务是否 `completed` 且带 `evidenceRefs`；
- 非 `manual` 的 `successCriteria` 是否有 `passed=true` 且带 `evidenceRef` 的 `CriterionResult`；
- `manual` 是否在 `pre-finish` 做过一次人工确认；
- 全 `manual` 时发出弱 DoD 告警，但不拦住完成。

这些能防止「假装完成」。它们不能回答：

- 原始目标有没有被真正解决；
- 有没有只改了半条链、漏了主路径；
- 产物和内部状态是否一致；
- 同步最新目标后再验是否仍成立；
- 用户最可能打回的点是什么，能不能自己先修。

### 2.3 用户验收被误当成质检官

工作台当前把 `result_ready` 解释为「结果已出，等你验收」。主按钮是「确认验收」。

这在产品上把质量责任推给了用户：

```text
代理：任务勾完了
用户：帮我看这结果到底够不够好
```

高质量代理的责任划分应相反：

```text
代理：对照目标和产物，我认为已经过线
用户：我知道了 / 我接受这个结果
```

用户验收必须保留，而且对有副作用的 Goal **确认验收仍是收口**。它确认的是意图，不是替 Peer 做第一轮质检：

```text
质量环证明「像样，可以交卷」
确认验收证明「对，这是我要的」
```

测试绿了、改动复查过了，都不等于交互、隐含偏好和没写进需求的约束也被满足。代理不能自己盖章说已经完成。

### 2.4 和 Claude Code / Codex 的差距

Claude Code 与 Codex Goal 的强项不是「更会写计划」，而是：

```text
看结果
→ 判断差距
→ 自己再改
→ 再看结果
→ 过线后才交给人确认
```

Peer 已有 `explore → plan → act → verify` 的设计语言，也有 re-anchor、偏航检测、no-progress 和完成门。缺的是 verify 之后的正式裁判：

> **有验证门，没有评审官；有完成态，没有反思态。**

---

## 3. 产品目标与非目标

### 3.1 产品目标

1. **结果负责**：Peer 对交付质量负责，人只处理代理无法安全判断的例外。
2. **两套标准分离**：过程完成与结果质量是两道门，不能互相替代。
3. **默认无感**：质量评审和自行返工发生在「正在处理」内，不做成用户向导；过线后仍要停在待验收。
4. **可停止**：同一类失败重复出现、预算耗尽或必须人判断时，进入「需要你」，不无限改。
5. **复用主干**：继续使用 GoalPlan、Runner、Evidence、TaskOverview 和 `resultAcceptance`。
6. **与隔离交付兼容**：质量过线后的产物，才进入目标分支同步、复验和交付。

### 3.2 非目标

- 不另建平行任务系统或第二套工作台；
- 不把质量评审做成第六步用户向导；
- 不要求用户理解 Quality Review、Repair Loop 或 PDCA 术语；
- 不用用户验收替代自动质量评审；
- 不让弱 DoD 或全 `manual` 标准蒙混进入已完成；
- 不在无 oracle 时假装已经过线；
- 不把每次机械测试失败都升级成「需要你」。

---

## 4. 核心对象

### 4.1 Quality Review（质量评审）

一次对照「原始目标 + 成功标准 + 实际产物」的结果裁判。它发生在过程完成门之后、`result_ready` 之前。

评审对象至少包括：

- 原始用户目标与 Goal 契约；
- 当前计划与已完成任务；
- 实际产物：diff、文件、命令输出、测试结果、关键界面或日志；
- 已知风险、未决假设和未覆盖路径。

评审结论只能是：

| 结论 | 含义 | 下一步 |
|---|---|---|
| `passed` | 四层检查都过 | 进入「结果待你验收」；有交付绑定时可进入交付队列 |
| `repairable` | 有可自动修复的质量差距 | 进入 Repair Loop |
| `needs_user` | 无法自判或必须人决策 | 进入「需要你」 |
| `exhausted` | 同因失败触顶或预算耗尽 | 进入「需要你」，附带已尝试事实 |

### 4.2 Quality Finding（质量差距）

一条可执行的差距，不是散文总结。每条至少包含：

```text
findingId
gate            意图 / 机械 / 产物 / 集成
severity        blocker / major / minor
claim           哪个目标或标准没有被满足
evidence        产物或检查中的事实
repairHint      建议修什么，而不是再写一遍计划
autoFixable     是否可由 Repair Loop 自行处理
```

`minor` 可以进入结果包作为已知风险，不阻止过线。  
`blocker` 和未处理的 `major` 不能过线。

### 4.3 Repair Loop（自我修复环）

把 `repairable` 的 Finding 写成 Goal 内修复项，回到 Do，再重新经过完成门和质量评审。

规则：

- 修复项必须映射到既有 Finding，禁止借机扩 scope；
- 优先修订当前 Goal 的叶子任务，不新开平行 Goal；
- 同一 `findingId` 或同一失败指纹连续出现达到上限，升级为 `needs_user`；
- 修复后必须重新跑受影响的机械验证，不能只改文案宣称已修好。

### 4.4 交卷前的四层检查

过线必须同时通过下面四层。这是内部检查模型，**不是用户界面上的关卡名**。

| 内部名 | 实际在查 | 界面怎么说 |
|---|---|---|
| intent | 原始请求的主结果出现了，而且不是旁路交差 | 对照你的目标 |
| mechanical | 相关测试、类型检查、关键命令通过 | 测试 |
| artifact | 重新看自己改了什么：漏文件、假完成、残留调试、半截状态机、界面和后端不一致 | 改动复查 |
| integration | 若要合入目标分支，同步最新目标后再验一次。分开都过、合在一起不过，不能交卷 | 合入后复验 |

`verificationGate` 主要覆盖「测试」里能自动跑的部分。  
Quality Review 负责「对照你的目标」和「改动复查」，有交付绑定时再做「合入后复验」。

界面规则：

- 用户看到的是检查记录，不说「关」「第 N 轮」「Finding」「过线」。
- 出过问题就直说问题和处理，例如：「取消后没法恢复，漏了；已补上再验过。」
- 卡片上只留人能决定要不要点进去的摘要；完整记录放在查看结果之后。

---

## 5. 与现有对象的关系

```text
GoalPlan
  ├─ Contract / tasks / successCriteria
  ├─ Runner                    推进 Do
  ├─ verificationGate          过程完成门
  ├─ Quality Review            结果质量门      ← 新增
  ├─ Repair Loop               Check 失败后的 Act ← 新增
  ├─ Delivery Binding          仓库 / 目标分支 / Worktree
  └─ resultAcceptance          用户确认验收后才完成；不负责第一轮质检
```

不可变规则：

1. 没有通过 `verificationGate`，不得进入 Quality Review。
2. 没有通过 Quality Review，不得进入 `result_ready`。
3. 没有用户确认验收，有副作用的 Goal 不得进入已完成。
4. 用户验收不能把未过线结果变成过线；「还不行」打开对应会话，用户在对话里说明后回到 Repair Loop。
5. Quality Review 不替代 hooks、权限和高风险确认。
6. Repair Loop 不绕过写盘范围和不可逆动作确认。
7. 普通问答、只读调研和 L0 解释不创建质量环。
8. 工作台继续只消费 `actionRight`，不在 renderer 解析质量状态机。

---

## 6. 完整闭环

```text
Plan
  冻结目标、边界、成功标准、风险假设

Do
  在当前执行环境中改（P0 可以是 target workspace；后续接入 Worktree）

过程 Check
  verificationGate：叶子完成 + Evidence + 自动标准

结果 Check
  Quality Review：意图 / 机械 / 产物 / 集成

Act
  passed        → 结果待你验收；有交付绑定则先交付再验收
  repairable    → 写入修复项，回到 Do
  needs_user    → 需要你
  exhausted     → 需要你，并展示已尝试事实
  用户确认验收  → 已完成
  用户还不行    → 打开对应会话；用户说明后回到 Repair Loop
```

对应 PDCA：

| PDCA | Peer 对象 |
|---|---|
| Plan | Goal 契约与计划 |
| Do | Runner 执行与修复项执行 |
| Check | `verificationGate` + Quality Review |
| Act | Repair Loop，或向用户提交一个聚焦例外 |

这把现有 `explore → plan → act → verify` 从「verify 后等人」改成「verify 后若不够好就再 act」。

---

## 7. 状态与用户投影

### 7.1 内部状态

在现有 `executing / verifying / completed / waiting_user` 上增加质量阶段，不替换 GoalPlanStatus：

```text
executing
  → verifying                 过程完成门
  → quality_reviewing         对照目标与产物
  → repairing                 修复环（含会话里「还不行」说明后的返工）
  → result_ready              质量过线，待用户确认验收
  → completed                 用户点了确认验收
  → waiting_user              执行中例外或耗尽
```

`repairing` 对外仍是「Peer 正在处理」。  
只有执行中无法自判的 `needs_user` / `exhausted` 才投影为 `needs_you`。  
`result_ready` 不是「需要你处理一个技术问题」，而是「结果待你验收」。

### 7.2 工作台投影

| 内部事实 | actionRight | 用户看到 |
|---|---|---|
| 执行中 / 过程验证 / 质量评审 / 修复中 | `peer_advancing` | Peer 正在处理 |
| 质量过线且尚未确认验收 | `result_ready` | 结果待你验收 |
| 业务分歧 / 无 oracle / 修复触顶 | `needs_you` | 需要你 |
| 用户已确认验收 | `terminal` | 已完成 / 历史 |

有副作用的 Goal（改仓库、改行为）过线后必须停在 `result_ready`。卡片主按钮是 **查看结果**，点卡也进结果。  
**确认验收**和**还不行**只出现在用户看过结果之后。没看过结果，不能验收，也不能打回。

卡片文案示例：

```text
结果待你验收
Peer 已自检
测试 152 项通过 · 取消后恢复漏了，已补上

[查看结果]
```

结果页文案示例：

```text
交卷前查过
对照你的目标     主结果有了
测试             152 / 152 通过
改动复查         取消后恢复不了，已补上
合入后复验       已通过

[还不行]                    [确认验收]
```

`resultAcceptance` 仍由结果页上的「确认验收」写入。没点验收，就不能假装已完成。

L0 问答、纯解释可以没有验收。一点仓库或行为，验收就要在。

「还不行」打开这条任务对应的会话，焦点落到输入框。用户在对话里说明哪里不对，这句话就是返工依据。不要另开意见表，也不要自动代发空的拒绝消息。

- 人已经在这条对话里：收起结果，把光标放到输入框，必要时给一句占位：「说说哪里不对」。
- 人在工作台：跳回对应会话，同样落到输入框。不要新开空白窗。

Peer 收到这条消息后回到「正在推进」，按这句话改，改完再请用户看结果。没看过结果，卡片上不要出现「还不行」。

### 7.3 主界面不展示的内容

默认不展示：

- 内部检查名（intent / mechanical / artifact / integration）；
- 「关」「第 N 轮」「Finding」「过线」这类工作词；
- Quality Review 内部评分；
- Repair Loop 次数；
- Worktree / 目标分支 / 合并队列。

用户看到的是通俗检查记录。完整记录放在查看结果之后。用户只在例外时看到一个聚焦问题。

---

## 8. 何时进入质量评审

满足全部条件后自动进入，不询问用户：

1. 当前 Goal / 代码交付单元声明已执行完毕；
2. `verificationGate` 通过，或失败原因已被转化为修复项并处理完；
3. 不是 L0 纯问答；
4. 存在可观察产物，或存在可自动验证标准。

以下情况跳过完整四层检查，但仍不得假装可以交卷：

- 纯咨询、解释、方案讨论：没有产物，直接回答，不创建质量环；
- 只读调研：用「结论是否覆盖问题」做轻量「对照你的目标」，不伪造测试；
- 用户明确只要草稿 / 中间结果：标记为中间产物，不进入已完成。

---

## 9. 质量评审怎么做

Quality Review 是一次有结构的自检，不是再生成一段「我已经完成」的总结。

推荐顺序：

1. **重述目标**：用原始用户请求和 Goal 契约，而不是用当前计划标题替换目标。
2. **对照成功标准**：逐条看自动标准的 Tool Result；没有自动标准时，说明用什么产物判断。
3. **阅读产物**：看 diff、关键文件、命令输出、失败日志或界面结果。
4. **找最可能被打回的点**：漏主路径、假完成、半截链路、回归、跨仓只交一半。
5. **给出结论**：`passed` / `repairable` / `needs_user` / `exhausted`。
6. **写下检查发现**：每条都能被 Repair Loop 或用户决策消费。内部仍叫 Finding。

禁止：

- 只用任务勾选状态当过线证据；
- 在未读产物时宣称「改动复查」已通过；
- 把弱 DoD 告警当成可以完成；
- 把「用户可以验收」写成质量通过。

---

## 10. 自我修复怎么做

### 10.1 写入修复项

`repairable` 时，Peer 在同一 Goal 内追加或重启叶子任务：

```text
修复：取消任务后必须保留未交付环境
来自检查发现 F12（改动复查 / major）
验证：相关测试重跑 + 再读取消路径代码
```

修复项必须：

- 指向既有 Finding；
- 写明验证方式；
- 保持在原 Goal 的 scope 内。

### 10.2 停止条件

出现任一情况，停止自动修复并进入「需要你」：

- 同一失败指纹连续 3 次；
- 修复轮次达到 Goal 上限（默认 2 轮完整 Review→Repair，可按任务规模上调到 3）；
- 继续修会碰到不可逆或超范围写入；
- 两个都说得通的产品规则；
- 没有自动 oracle，且产物无法判断好坏；
- no-progress / 预算耗尽。

停止时必须展示：

- 已经做过什么；
- 还差什么；
- 为什么不能自己继续；
- 用户现在要决定什么。

### 10.3 和现有 verifier_failed 的关系

当前 Runner 在验证失败时会回到 `executing` 并标 `verifier_failed / repair`。这只覆盖「测试」失败。

Quality Review 之后的 Repair Loop 覆盖更广：

- 测试失败：继续走现有 verifier repair；
- 对照目标 / 改动复查 / 合入后复验失败：走本方案的检查发现 → 修复项；
- 两者都计入同一轮次上限，避免一边修测试一边无限扩功能。

---

## 11. 用户何时被打扰

只问一个聚焦问题，不抛出 Git 文件列表或内部状态机。

允许打扰的类别：

1. **产品规则冲突**：例如取消后保留环境还是立即清理。
2. **成功标准互相打架**：无法同时满足。
3. **无 oracle**：没有测试、没有可观察产物、也无法从 diff 判断好坏。
4. **修复触顶**：同一问题改了上限次数仍失败。
5. **高风险 / 不可逆**：继续修会越权或破坏现场。

不允许打扰的类别：

- 测试红了；
- 漏改一个文件；
- 只写了文档没改代码；
- 状态机自相矛盾；
- 合入最新目标后回归。

这些都必须自己回去改。

---

## 12. 与隔离交付的衔接

质量环和 Worktree / 合并队列是一层，不是两套流程：

```text
理解目标
→ 冻结交付对象
→ 隔离执行
→ 过程完成门
→ 质量评审
→ 不够好就再改
→ 同步最新目标后再验一次
→ 过线后进入交付（如有）并请用户确认验收
→ 确认验收才算完成；还不行则打开对应会话再修
```

规则：

- 没有质量过线，不得进入 Delivery Coordinator；
- 「合入后复验」在存在 `targetBranch` 时强制执行；
- 当前尚未接入 Worktree 时，质量环仍先落地，但必须明确标注「未隔离执行」，不得假装已经做过合入后复验；
- Result Package 同时收录质量评审结论、通俗检查记录、验证 Evidence 和交付记录。

---

## 13. 数据模型建议

```ts
type QualityGateName = 'intent' | 'mechanical' | 'artifact' | 'integration'

type QualityFinding = {
  findingId: string
  gate: QualityGateName
  severity: 'blocker' | 'major' | 'minor'
  claim: string
  evidenceRefs: string[]
  repairHint?: string
  autoFixable: boolean
}

type QualityReview = {
  reviewId: string
  planId: string
  attempt: number
  verdict: 'passed' | 'repairable' | 'needs_user' | 'exhausted'
  gates: Record<QualityGateName, 'passed' | 'failed' | 'skipped'>
  findings: QualityFinding[]
  createdAt: string
}

type RepairAttempt = {
  attempt: number
  sourceFindingIds: string[]
  taskIds: string[]
  startedAt: string
  finishedAt?: string
}
```

约束：

- `QualityReview` 是质量过线的事实源；
- `verificationGate` 仍是过程完成的事实源；
- `resultAcceptance` 记录用户确认验收，是有副作用 Goal 进入已完成的收口事实；不改写 Quality Review 结论；
- renderer 不得自行根据任务勾选推断 `passed`。

---

## 14. 对现有完成语义的修正

| 旧语义 | 新语义 |
|---|---|
| 叶子全完成 + 完成门通过 = 可以完成 | 只等于过程完成，还要过 Quality Review |
| `result_ready` = 请用户做第一轮质检 | 质量过线后的交卷：Peer 认为像样，请你确认是不是要的 |
| 用户验收可省略 / 只是归档 | 有副作用的 Goal 上，确认验收仍是收口 |
| 用户只能点通过 | 用户可以说「还不行」，打开对应会话说明后回到 Repair Loop |
| 弱 DoD 只告警仍可完成 | 无自动标准且无产物 oracle 时不得过线，更不得验收通过 |
| verify 失败才自我纠错 | 质量评审失败，以及验收拒绝，都必须自我纠错 |
| 计划走完就可以等人验收 | 计划走完只是进入评审；过线后才等人确认意图 |

Goal 模式原文「跑到成功标准满足再回来」保持不变，但「满足」分成三层：完成门证明做完，质量评审证明像样，确认验收证明对。

---

## 15. P0 范围与分期

### 15.1 P0：先堵住「做完就验收」

1. Goal 在 `verificationGate` 通过后进入 `quality_reviewing`，不得直接 `result_ready`。
2. 落地四层检查清单，至少强制「对照你的目标 + 测试 + 改动复查」。
3. `repairable` 时在同一 Goal 写入修复项并回到 executing。
4. 同因失败 3 次或 2 轮 Review 后进入 `needs_you`。
5. 全 `manual` / 弱 DoD 且无产物 oracle 时不得过线。
6. 工作台第三桶保留，文案改为「Peer 已自检」；卡片主按钮是查看结果。确认验收和还不行只出现在看过结果之后。
7. 结果页展示通俗检查记录，不展示关卡名。
8. 「还不行」打开对应会话；用户在对话里说明后，回到同一 Goal 的 Repair Loop。

本阶段可以暂不接 Worktree。「合入后复验」在没有目标分支绑定时标为 `skipped`，并在结果包中可见。

### 15.2 P1：和交付闭环接通

- 存在 Delivery Binding 时强制「合入后复验」；
- 质量过线后才允许进入合并队列；
- Result Package 收录评审结论、修复轮次和最终 commit；
- Automation 成功结果也走同一套「过线后待验收」，不再直接当终态。

### 15.3 P2

- 更完整的产物 oracle：界面对比、日志断言、跨仓部分交付评审；
- 按仓库 / 任务类型配置修复上限；
- 把高质量 Finding 沉淀为可复用检查，而不是每次从零散文自检。

---

## 16. 验收标准

1. 普通咨询不创建 Quality Review。
2. `verificationGate` 未通过时，不得出现 Quality Review `passed`。
3. Quality Review 未 `passed` 时，Goal 不得进入 `result_ready`。
4. 有副作用的 Goal 未写入 `resultAcceptance` 时，不得进入已完成。
5. 用户点击验收不能把 `repairable` / `needs_user` 改写成质量过线。
6. 「还不行」打开对应会话；用户说明后回到 Repair Loop，而不是直接失败终态，也不另开意见表。
7. 机械测试失败会进入修复，而不是立即「需要你」。
8. 「对照你的目标」或「改动复查」失败会生成检查发现和修复项，而不是只生成一段完成总结。
9. 同一失败指纹连续 3 次后停止自动修复，并向用户展示已尝试事实。
10. 弱 DoD 且无产物依据时不能过线，更不能验收通过。
11. 用户主界面能区分正在处理、结果待你验收、已完成、需要你。
12. TaskOverview 继续只消费 `actionRight`，不在前端解析 Quality Review。
13. 现有 GoalPlan / Evidence / `resultAcceptance` 字段保持兼容；确认验收仍写 `resultAcceptance`。
14. 有目标分支绑定的代码交付，未做「合入后复验」不得交卷。

---

## 17. 实施原则

### 17.1 单一事实源

- 过程完成：`verificationGate` + `criterionResults` + 任务 `evidenceRefs`；
- 结果质量：`QualityReview`；
- 用户确认：`resultAcceptance`；
- 工作台：`actionRight` 投影。

### 17.2 最小正确链路

```text
执行完毕
→ 过程完成门
→ 质量评审
→ 不够好就修复并重验
→ 过线后进入结果待你验收
→ 确认验收才完成
→ 还不行则打开对应会话再修
```

### 17.3 冻结结论

1. **Peer 现在擅长把事做成计划并执行完；本方案补的是根据结果判断够不够好。**
2. **完成门继续防假装完成；质量评审负责防平庸完成。**
3. **确认验收仍是收口；它确认意图，不再承担第一轮质检。**
4. **自我修复必须可停止，停止理由是质量判断或用户打回，不是计划走完。**
5. **质量环对用户无感，对系统可审计；待验收对用户可见，且必须能打回。**
6. **它与 Worktree / 目标分支交付兼容，但不阻塞先补质量裁判和验收收口。**
