# ADR 127：未知执行结果的对账协议、策略化自主收口与资源范围收敛

创建时间：2026-11-09
最后更新：2026-11-15（同步 ADR 126 为 Accepted，明确列出对 ADR 116 / 124 的部分取代条款及已退役条目的设置/诊断入口边界）
状态：Accepted（2026-11-09 用户评审通过，含评审修订：仅保留 `ask` / `bot_verified` 两档，`auto` 取消；2026-11-15 与 ADR 126 配套对齐；实施未开始，不表示已实现或已发布）
级别：A（执行结果、授权边界、证据与资源占用契约）；实施包含 B 级协议/宿主/持久化和 C 级状态表达。

关联：[产品北极星](../../design/product/peer-product-alignment.md)、[架构治理](../architecture/20-architecture-governance.md)、[委托运行时](../architecture/project-agent-delegation-runtime.md)、[人机交互契约](../specifications/peer-human-agent-interaction-contract.md)、ADR [91](91-project-bot-autonomous-coordination.md)、[101](101-bot-owned-access-policy.md)、[110](110-follow-up-responsibility-and-current-list.md)、[116](116-session-control-and-resource-settlement.md)、[120](120-runtime-facts-disposition-and-resource-wait.md)、[124](124-legacy-stop-obligation-controlled-resolution.md)、[126](126-execution-resource-claim-closure-and-unknown-retention.md)。

本文与正式接受的 [ADR 126](126-execution-resource-claim-closure-and-unknown-retention.md) 共同构成现行“执行资源 claim 闭包与未知执行结果收口”契约，并非推翻停稳与审计基线，而是对部分旧条款做如下**显式部分取代**：

- **延续 ADR 126**：claim 闭包、`RetainedUnknown`、计划镜像、死亡证明、`user_panel` 确认（对应 `ask` 档）及隔离 clone 逃生继续有效；两者现均处于 Accepted 契约态。
- **扩展 ADR 126**：在逐条 `user_panel` 确认的 `ask` 档之上，增加用户按项目 / Bot 主体预先委托给主 Bot 的 `bot_verified` 策略化收口（由宿主核验对账探针证据与风险包络，仍保留人工兜底；`auto` 档已取消）。
- **部分取代 ADR 116**：§6.1 / §12 的“仅目录粒度锁定、不做细粒度 scope”由本文 §5.7 按声明范围（文件 / 子目录 / Git ref / 远端对象）收敛 claim 所取代；§6.2–§6.3 的“只能凭匹配停稳回执释放占用、未知结果转长期目录 hold”由 ADR 126 + 本文的 `RetainedUnknown` 留存与 `ask / bot_verified` 受控闭包所部分取代（`stopReceipt` 仍是停止证明与自动结清的唯一依据）。
- **部分取代 ADR 124**：§1.5 / §4.1 / §6.2 / §8.3 / §13 中“永不通过闭包放开目录 / 每条仅允许 `user_panel` 确认 / 不新增设置页入口”等条款，由 ADR 126 + 本文的 `ask / bot_verified` 策略设置与受控闭包出口所部分取代。对于已按 ADR 124 写入 `disposition=indexed`（脱离日常任务列表）但仍留有陈旧 `ask` 档未闭 claim 的条目，**不恢复顶层「待核实」任务列表分区**，而是通过设置/诊断入口以及实际堵塞新任务时的资源等待提示直接暴露对账与闭包/策略入口，避免永久死锁。

## 1. 问题与用户判断

ADR 126 解决的是“锁永远解不开”：用户可以在看到未知调用后确认释放。但它不是根本解，用户对此的判断是准确的：

1. **unknown 仍然会发生**。派发已发出、结果没有落盘时，系统只能记未知；当前没有从源头把它压到接近零。
2. **收口权仍然在用户手里**。即使主 Bot 已经做完核对，仍要每次生成卡片、等用户点确认；主 Bot 没有“按用户已给的策略自主做对的事”的权力。
3. **锁的范围过大**。一个未知调用会保护整个目录；用户明明只需要继续改另一个文件，也被整仓库挡住。
4. **人工判断没有协议**。用户看到的是调用 id 和几句说明，不是宿主可复核的核对结论；每次确认都像重新做一次事故判断。
5. **永久性没有上限**。旧记录可以无限期占着目录，系统没有“到期必须核对、必须给出结论”的责任。

用户的要求可以概括为：**主 Bot 应该在用户委托的范围内自主行动，而不是每个技术细节都被推回给人。** 这个方向成立；需要补的是“自主”的定义、证据和责任，而不是增加一个 `force` 开关。

## 2. 目标与非目标

### 2.1 目标

- 从源头减少 unknown：派发先登记，结果与 Evidence 同事务落盘；宿主可监管的进程记录退出与终止。
- unknown 发生时，宿主能执行一套**可复核的对账协议**，而不是只等人判断。
- 用户可以按项目/Bot 委托“核对后收口”的权力；在该策略下，主 Bot 可以自主完成收口，不再逐次弹卡。
- 对账和收口都留下结构化证据与 receipt；不把 unknown 说成成功，不重放，不删除历史。
- claim 按**实际影响范围**保护；范围未知时才保守到工作区，并仍然有有界的收口路径。
- 任何 unknown 都有 owner、年龄、下一步和终止条件；不能无限期静默占用。

### 2.2 非目标

- 不允许模型用一句话、`force` 参数或完全访问档位把 unknown 改成已知。
- 不自动回滚外部副作用，不重放旧调用，不删除未知数组或 Evidence。
- 不把远端未围栏效果、真实 live 执行、未结束句柄纳入自主收口。
- 不新增第二套任务系统、全局解锁按钮或跨设备执行同步。
- 不改变 ADR 101 的 Bot 主体、ADR 116 的停止屏障和 ADR 126 的闭包语义。
- 本文不要求一次实现全部卡片；先写清楚授权与证据边界，再分阶段落地。

## 3. 核心判断：三种事实不能混在一起

| 问题 | 谁能回答 | 不能由什么替代 |
| --- | --- | --- |
| 发生了什么 | 宿主执行回执、进程/句柄、文件与 Git 观测 | 模型叙述、用户猜测、聊天里的“应该没事” |
| 谁有权结束占用 | 用户委托的策略 + 宿主授权 | 模型自称、`full_access`、一段解释 |
| 用户看到什么 | 状态投影和证据展示 | 把内部协商写成已确认事实 |

主 Bot 的权力应该是**行动权 + 核对权 + 提议权**；它可以在用户委托的策略内**决定收口**，但不能**发明执行结果**。这是“结果带着依据交回”的前提，也是主 Bot 的报告能被信任的原因。

因此“根本解”不是让模型拥有无限权力，而是：

1. 让 unknown 很少发生；
2. 发生了也能被宿主和主 Bot 用证据收敛；
3. 收敛的决定权可以按用户策略委托，而不必每次人工。

## 4. 现状与缺口

代码基线为 Peer-Agent 开发线（2026-11-09 前后，rc.40 线）。实施时须重新定位源码。

| 现状 | 代码锚点（相对代码仓） | 缺口 |
| --- | --- | --- |
| 派发与结果分离 | `packages/runtime-node/src/project-agent/work-budget.mjs` 的 `uncertainDispatches` / `pendingTools`；执行侧 `runner*` | 结果未落盘即 unknown；缺少“先登记、后派发”的统一回执 |
| 资源 claim | `execution-resources.mjs` 的 `inspect`/`reserve`/`protect`/`settle`/`closeClaim` | claim 以工作区目录为主；unknown 没有自动对账，只靠人工闭包 |
| 停止与死亡证明 | `session-control.mjs` 的 `recorder`、`proveRecorder`、`deadRecordingHost` | 只覆盖停止；不对 unknown 的工具结果做能力级探针 |
| 授权 | `execution-obligation.mjs` 的 `inspect`/`requestAuthorization`/`resolve`；ADR 126 的 `close_claim` | 必须 `user_panel` 确认；主 Bot 没有按策略自主收口的路径 |
| 资源范围 | `execution-scopes.mjs` 的目录与 Git scope | 现有 claim 可保护整个工作区，未按 dispatch 声明收窄 |
| 计划镜像 | `delegationOrigin.executionClaimClosure` | 闭包可持久化；但没有“策略收口”的授权与证据字段 |

## 5. 决策

### 5.1 从源头消灭 unknown

1. **先登记，后派发**：每次工具调用在真实 dispatch 前耐久写入 `dispatchId`、`toolCallId`、attempt、conversation/stream、capability、声明范围；结果、Evidence 和终态在同一事务提交。
2. **进程可监管**：宿主可监管的 Shell 记录启动、退出码、stdout/stderr、结束时间；进程被杀记录 `terminated`，不是 `unknown`。无法监管的 Provider/外部动作必须声明“不可围栏”，不能伪装成可确认。
3. **幂等与可核对**：有外部副作用的操作带幂等键或可核对的远端回执（push、PR、远端 ref）。可核对的副作用优先走“观察后确认”，而不是猜。
4. **声明范围**：dispatch 必须声明文件/目录/Git ref/远端对象范围；claim 和 unknown 按声明范围保护。声明缺失才 conservative 到工作区。

这一层是根本解的主体：unknown 应该是异常，不是常态。

### 5.2 结果状态

宿主只承认以下状态，模型不能写：

| 状态 | 含义 |
| --- | --- |
| `not_dispatched` | 有登记证据证明没有发出 |
| `confirmed_success` | 有该调用的结果/证据回执 |
| `confirmed_failure` | 有明确失败回执 |
| `effect_observed` | 没有原调用回执，但宿主探针证明效果已发生（如目标文件/远端 ref 已变） |
| `no_effect_observed` | 宿主探针在声明范围内没有观察到效果 |
| `unknown` | 证据不足，无法判定 |
| `unfenced_external` | 外部动作无法围栏/观察，永远不能自动判定为无效果 |

`effect_observed` / `no_effect_observed` 是**核对结论**，不是“调用成功/失败”的替代；它们只用于决定资源能否继续使用，仍保留 `unknown` 原始记录。

### 5.3 对账协议

宿主提供 `reconcileUnknownOutcome(claim, scope)`，执行有界、只读、可审计的探针：

- 进程/句柄：recorder 死亡证明、PID/启动时刻、未结束 handle；
- 工作区：`git status`、目标路径存在性/mtime/hash、声明的文件范围；
- Git：本地 ref、远端 ref、PR/远端对象（若能力允许）；
- 日志/回执：宿主已有的 tool result、Evidence、delivery receipt、日志。

输出：

```text
ReconciliationEvidence {
  execution, claimId, claimRevision, scope,
  probes: [{ kind, ref, result, observedAt, digest }],
  verdict: 'no_effect_observed' | 'effect_observed' | 'inconclusive' | 'unfenced_external',
  evidenceDigest
}
```

约束：

- 探针由宿主执行或读取；模型可以请求探针、解释结果，但不能伪造 `result` 或 `verdict`。
- 探针必须有界：只读声明范围，不启动新 Side Effect，不重放旧调用，不读凭据/隐私内容。
- `inconclusive` 不释放 claim；`unfenced_external` 不进入自主收口。
- 同一 evidence digest 幂等；证据变化后旧授权失效。

### 5.4 策略化自主收口

新增按项目/Bot 的本地策略 `unknownOutcomePolicy`：

| 策略 | 行为 |
| --- | --- |
| `ask` | 保持 ADR 126：用户卡片逐条确认后才可 `close_claim`，默认值 |
| `bot_verified` | 主 Bot 在**用户已委托**的前提下，对符合条件的 claim 执行/请求对账；宿主校验证据和风险包络后直接收口，不再弹卡 |

评审决定（2026-11-09）：**不设宿主静默自动收口档**（原提案的 `auto` 取消，理由见 §11.6）。授权语义只有“问你”与“主 Bot 凭宿主证据核对后收口”两档。

`bot_verified` 的授权来自用户保存的策略，不是模型参数：

- 策略绑定 `(workspaceId, profile.agentConversationId)`，即 ADR 101 的 Bot 主体本身；委托在该 Bot 存续期间跨任务会话持续生效，不随单条会话结束重置；
- 委托入口以**现场委托**为主：`ask` 卡片在主 Bot 已出示完整对账证据时，提供“今后此类由主 Bot 核对后直接收口”的一键升级，由用户点击写入策略；设置页保留同等入口。模型不能发起或代替这次点击；
- 只在用户明确开启时生效；默认 `ask`；可随时撤销；
- 撤销不重开已收口 claim，但阻止后续自主收口；
- `full_access`、Ask、会话许可、`force` 都不能替代策略；
- 模型不能修改策略，只能读取和按策略行动。

### 5.5 风险包络

`bot_verified` 只允许收口同时满足以下条件的 claim：

1. 没有 live 执行、没有未结束句柄；
2. 声明范围在工作区内（或明确为本机单目录），不是外部账户/远端/凭据；
3. 不是破坏性 Git/远端操作，不是 push/PR/发布，不是凭据或密钥写入；
4. 有完整 `ReconciliationEvidence`，且 `verdict` 为 `no_effect_observed` 或 `effect_observed`；
5. 不是 `unfenced_external`；
6. 对 `effect_observed`，证据必须能定位实际效果；对 `no_effect_observed`，探针必须覆盖声明范围，不能只看“进程不在了”。

push / PR / 远端发布是**永久人工门**（评审确认，不随任何策略开放）；远端只读探针留待后续提案另行评审。

`no_effect_observed` 的覆盖承诺按评审收窄：v1 只承诺**声明范围内、工作区内、git 可见（含未跟踪文件）的变化**无效果；忽略文件与工作区外的效果不在承诺内，探针覆盖不足时保持 `unknown` / `inconclusive`，不得表述为“没有影响”。

### 5.6 收口回执

每次收口生成 `UnknownOutcomeResolution`：

```text
{
  resolutionId, claimId, claimRevision, execution, scope,
  verdict, evidenceDigest, tier: 'user_confirmed' | 'bot_verified',
  policyRef?, authorityRef, unknownCalls, at
}
```

- claim 进入 `released`；unknown 调用原样保留在 `RetainedUnknown`；
- 不写 `stopReceipt`，不声称调用成功/失败；
- 计划镜像写收口回执；协调 journal 写审计事件；
- 设备账本、计划镜像和 journal 三者以同一个 resolutionId 幂等；
- 崩溃窗口按 ADR 126 的镜像优先修复，不重复收口。

### 5.7 资源范围收敛

- claim 以 dispatch 声明范围为准：文件、子目录、Git ref、远端对象分别成 claim；能窄就不宽。
- 未知范围时保守保护工作区，但仍保留策略化收口路径；不能因为“范围未知”就永久禁止一切。
- worktree 共享 `.git` 的冲突继续保守；clone 逃生作为不释放原锁的兜底，不替代按范围收口。
- 旧 claim 迁移时保留原范围；无法确定的，按保守范围处理并在诊断中标注。

### 5.8 不允许永久占用

- 每个 unknown claim 必须有 owner、年龄、下一步和终止条件；
- 启动对账和定期诊断会重算证据；证据无变化时不重复调用模型；
- `bot_verified` 下，主 Bot 可以在合理时间后完成对账并收口；
- `ask` 下，超过可解释年龄的 claim 必须在任务详情和诊断中显式展示，不能静默；
- 不存在“时间到了自动放行”；到期只触发核对，不跳过证据。

### 5.9 主 Bot 与界面

主 Bot 可以：

- 读取 unknown、范围和对账证据；
- 请求宿主运行对账探针；
- 在 `bot_verified` 策略下提交核对请求与理由，由宿主计算 verdict 并签发收口；
- 向用户报告：哪些已核对、哪些仍未知、为什么可以/不可以继续。

主 Bot 不可以：

- 自己写 `verdict`、`evidenceDigest` 或 `resolutionId`；
- 在策略未开启时绕过用户卡片；
- 用“我已检查”代替宿主证据；
- 把收口说成成功、回滚或没有发生。

界面：

- 任务详情展示 unknown、范围、证据摘要、当前策略和下一步；
- `ask` 显示确认卡，并在主 Bot 已完成对账时附现场委托入口（§5.4）；`bot_verified` 显示“主 Bot 已核对并收口”的 receipt 和证据入口；
- 策略设置按项目/Bot，明确说明开启后主 Bot 可在证据满足时自主收口；
- 不新增全局“强制解锁”按钮。

## 6. 协议与存储

| 对象 | 归属 | 说明 |
| --- | --- | --- |
| `UnknownOutcomePolicy` | 项目/Bot profile 或本地设置 | `ask` / `bot_verified`（评审取消 `auto`，不做能力类别细分） |
| `ReconciliationEvidence` | 协调 journal / 设备账本 | 探针、verdict、digest；宿主写 |
| `UnknownOutcomeResolution` | 设备账本 + 计划镜像 + journal | 收口回执；幂等 |
| `ExecutionResourceClaim.scope` | 设备账本 | 文件/目录/Git ref/远端对象 |
| `ExecutionResourceBlocker` | Protocol | 增加 `unknownOutcomePolicy`、`reconciliationAvailable`、`scope`、`resolutionTier` |
| 审计事件 | coordination journal | `unknown_outcome_reconciled` / `unknown_outcome_resolution` |

最低 reader/writer/executor 版本按实施时主线占用取下一个可用整数；旧 writer 必须拒绝新语义，不能静默忽略策略字段。

## 7. 安全与证据边界

- 策略是**授权**，不是事实；收口是**结束占用**，不是把结果变成成功。
- `bot_verified` 的 receipt 记录 `authorityRef = policy:<policyId>` 和 `evidenceDigest`；没有这两项不能收口。
- 探针的输入/输出有界、脱敏；不读凭据、不暴露完整路径给模型载荷。
- 未知调用、Evidence、历史、预算、计划状态不删除；收口只改资源占用和处置。
- 外部未围栏副作用永远保留人工门；写操作不进入任何自动判定路径。
- 模型可以“建议收口”，但不能“签发收口”；host 拒绝任何伪造的 evidence digest/verdict。

## 8. 迁移与兼容

1. 默认 `ask`，现有用户行为不变。
2. 已有 claim 按新范围分类；无法确定范围的按工作区保守，并显示诊断。
3. ADR 126 的 `user_confirmed` 闭包保留；新 receipt 加 `tier`，旧记录按 `user_confirmed` 解释。
4. 计划镜像、设备账本、journal 三者按 resolutionId 幂等；重建时从 journal/镜像恢复。
5. 降级前封新准入；旧版本拒绝新策略/新 receipt 语义，不能当作“忽略字段继续跑”。
6. 一次性诊断列出所有 stale unknown；不自动迁移成已收口。

## 9. 实施拆分

| 卡片 | 内容 | 依赖 |
| --- | --- | --- |
| UO-01 | 策略、证据、resolution 的 Protocol 与存储/版本门槛 | 无 |
| UO-02 | dispatch 先登记、结果与 Evidence 同事务；进程监管与幂等 | UO-01 |
| UO-03 | 对账探针与 `ReconciliationEvidence`（进程/句柄/文件/Git/回执） | UO-02 |
| UO-04 | `bot_verified` 策略门、风险包络、resolution 回执、现场委托入口 | UO-01、UO-03 |
| UO-05 | claim 范围收敛与旧 claim 迁移 | UO-01 |
| UO-06 | 任务详情/设置/证据入口与主 Bot 报告约束 | UO-04 |
| UO-07 | 存量诊断、指标（unknown 率、年龄、收口耗时） | UO-03、UO-05 |
| UO-08 | 聚焦测试、崩溃窗口、双宿主与产品回归 | 全部 |

实施顺序按依赖串行；UO-02 是根本解的主体，不能只做 UO-04 的授权而继续丢结果。UO-03 完成后先服务于 `ask` 卡片（把对账结论放进确认卡），不依赖 UO-04；UO-04 的实现节奏按 UO-07 的 unknown 率数据排期，协议字段在 UO-01 一次定稳。UO-01 须确认只读 dispatch 是否真的产生阻塞 claim，作为风险包络的输入。

## 10. 验收与反例

1. 派发后崩溃、结果未落盘：宿主有登记与进程证据；能证明 `no_effect_observed` 时按策略收口，不能证明时保持 unknown。
2. 结果已落盘：不产生 unknown；不重复调用。
3. `ask`：仍要用户卡片；`bot_verified`：证据满足时主 Bot 可收口，无卡片。不存在第三档自动收口。
4. 模型伪造 evidence/verdict/policy：宿主拒绝并审计。
5. live 执行、未结束句柄、`unfenced_external`：任何策略都不收口。
6. 范围收敛：声明只影响 `a.ts` 的调用不锁整个仓库；范围未知时保守并显示诊断。
7. `effect_observed`：保留原 unknown，只结束占用；不得写成成功。
8. 崩溃窗口：resolution 只写一份；重启/重建后不重复、不复活。
9. 策略撤销：后续回到 `ask`；已收口不重开。
10. 旧 claim：只诊断，不自动判成功；按策略/人工处理。
11. 产品表达：不出现“强制解锁”“已成功”“已回滚”；`bot_verified` 显示证据和策略来源。
12. 指标：unknown 率、stale 年龄、收口中位时间可观测；发布门禁检查。

## 11. 评审决定（2026-11-09）

原未决问题由用户评审拍板如下，实施按此执行：

1. **默认策略**：始终 `ask`，新项目不默认 `bot_verified`。委托以现场入口为主（§5.4）：`ask` 卡片在主 Bot 出示完整对账证据时提供一键委托升级，设置页保留同等入口。
2. **粒度**：项目 + Bot 主体（ADR 101 的 `(workspaceId, profile.agentConversationId)`），跨任务会话持续；不做能力类别细分。
3. **采样要求**：v1 不设最短年龄或二次采样硬门槛；活体维度由 ADR 126 的 recorder 死亡证明 + 无句柄覆盖，是否需要二次采样由 UO-07 指标决定。
4. **Git/远端**：push / PR / 远端发布保持永久人工门，不进入 `effect_observed` 自主收口；远端只读探针留待后续提案。
5. **覆盖证明**：`no_effect_observed` 只承诺声明范围内、工作区内、git 可见（含未跟踪）变化无效果；忽略文件与工作区外效果不承诺，覆盖不足保持 `unknown`。
6. **取消 `auto`**：仅保留 `ask` / `bot_verified`。理由：用户的诉求是主 Bot 在委托内有行动权，不是宿主静默自动；两档在界面上是“问你 / 我核对过了”的清晰二分；未来确需 `auto` 时以新枚举值 + 版本门槛扩展，不伤旧数据。
7. **证据回看**：复用任务详情与证据入口（UO-06）；导出与诊断视图后置。

## 12. 变更记录

- 2026-11-09：创建。回应用户对“unknown 永久锁 + 主 Bot 无自主收口权”的批评；把根本解拆成源头回执、宿主对账、策略化授权、范围收敛和永久性治理；待评审后再进入代码实施。
- 2026-11-09：用户评审通过，状态 Proposed → Accepted。评审修订：取消 `auto` 档，仅保留 `ask` / `bot_verified`；策略绑定 Bot 主体并跨任务会话持续；新增 `ask` 卡片现场委托入口；`no_effect_observed` 覆盖承诺收窄为声明范围 + 工作区 + git 可见变化；push/PR 设为永久人工门；v1 不要求二次采样；UO-03 先服务 `ask` 卡片，UO-04 按 UO-07 数据排期。原 §11 未决问题转为评审决定。
