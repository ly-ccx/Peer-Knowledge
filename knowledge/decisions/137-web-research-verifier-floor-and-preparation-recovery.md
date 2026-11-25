# ADR 137：联网只读任务的独立核验下限与核验准备失败回执

创建时间：2026-11-25
最后更新：2026-11-25
状态：Accepted（2026-11-25 仓库所有者在会话中确认方向并授权实施：只读调研/文档类任务不再强制独立核验，先补 ADR 再改触发条件；核验员的工具参数错误回给模型重试。实现候选 `Peer-Agent` `8451826c` 位于分支 `PeerAgent/pa/research-verifier-floor`，已推送、未并入开发线、未经安装版验收）
级别：A（关闭闸门与验证下限在一类委托会话上的适用范围），B（委派核验面的工具准备失败处置、`spawn_session` 标准描述）
依赖：ADR 80、88、93、95、103、106、116、117、118、131；[委托运行时](../architecture/project-agent-delegation-runtime.md) 验证下限表。

## 1. 现场事实（2026-11-25，本机 RC 42 候选）

1. 同一条只读联网调研任务重跑 5 次。Worker 完成的 2 次之后，5 次独立核验运行全部以宿主错误结束，没有任何一次产生结构化裁决（`failedCriteria`、`missingEvidence`、`risks` 均为空）：
   - 3 次 `conversation_tool_intent_changed`：核验员对本地代码仓库发起全量 `search_files` / `batch_search`，运行 34～52 秒后在落账守卫 `tool_facts` 被拒绝；其中一次 `batch_search` 已成功产出归档结果。具体触发守卫中哪一项检查尚未定位。
   - 2 次 `invalid_line_range`：核验模型给 `read_file` 的行号参数不合法，`prepare` 阶段直接终止整轮核验。
2. 核验运行被记为 `independentVerifier=failed`，`modelReviews` 被清空。计划的 3 条 `model_review` 标准因此无法满足关闭闸门，`decide_session_acceptance` 在人工确认下也不签收；单会话 3 次核验额度用尽后，已完整交付的调研报告永久停在「等待验收」。
3. 核验员的能力上限不含 `local.web.search` / `local.web.fetch`，运行时没有读取 `local-web-artifact://` 证据的路径。联网调研的证据引用几乎全部是网页产物，核验员只能引用、不能打开。核验提示词要求「直接核对改动过的文件和 git 状态」，实际行为是在本地代码仓库里 `git_query` / `search_files`。
4. Worker 完成后只要配置了核验模型或计划含 `model_review` 标准，就自动运行核验，不区分改动类型。`spawn_session` 的标准描述引导主 Bot 为「报告完整性、审计、质量」使用 `model_review` 并说明会由独立核验自动验证；只读联网调研没有可用的机械标准，必然落入该分支。
5. Worker 面的 `tool_arguments_invalid`（`6598c699`）与未投影工具名（`d868e3c0`）以未派发结果回给模型；委派核验面没有这条路径，`prepare` 的任何失败都终止整轮核验。

本机 7 个核验会话中，30 次非搜索工具调用全部正常落账，4 次全仓库搜索失败 3 次；Worker 会话中 145 秒的 `batch_search` 正常落账。落账守卫的误拒是独立缺陷，本决策不修复它，只让受影响的任务不再依赖核验。

## 2. 决策

### D1 联网只读会话的独立核验下限

判定只使用已持久化的宿主事实（`delegationOrigin`），不接受模型参数：

- `readOnly=true`；
- `requiredCapabilities` 含 `local.web.search` 或 `local.web.fetch`（含别名，经既有 `expand_requested_capabilities` 归一）；
- `requiredCapabilities` 不含交互结果发布（`local.interactive.publish` 及其工具别名）。

满足时该会话的独立核验为 `not_required`：

- Worker 完成后不自动运行独立 Verifier，不论是否配置核验模型或计划含 `model_review` 标准。
- `delegationOrigin.independentVerifier` 记 `not_required`；机械标准已判定 `failed` 时保留 `failed`，返修路径不变。
- 不写 `runner.verifierRuns`、`verificationReport`、`modelReviews`。
- 该会话的 `model_review` 标准是告知性的：不被标记通过，不进入关闭闸门的未满足项；核验结论以 `name=model_review`、`reason=not_reviewed` 的检查项如实列出。

本地只读调研（未请求联网能力）的产出在工作区内，核验员读取文件即可复核，维持 ADR 88 §7.1 的既有核验，不在本决策范围内。

### D2 显式复核保留

用户「重新核验」与主 Bot `verify_session` 的 `force` / `focus` 仍走既有 `reverify_session`，结果按既有规则写回；显式复核失败仍记 `failed`。`verify_session` 的默认调用只在状态为 `failed`、`missing` 或缺失时请求新检查；`not_required` 以及没有任何裁决的 D1 类会话都不触发。

### D3 核验准备失败回执

委派核验面（`ExecutionSurface::DelegatedVerification`）中，已投影工具的 `prepare` 失败以未派发的 `denied` 结果返回给核验模型，由它在同一次有限运行内更正。这类失败发生在意图、授权、派发之前，没有任何效果发生，也没有发放授权。

- `CANCELLED` 与未投影工具名保持原有终止行为。
- 真实权限拒绝仍立即结束本次核验（ADR 88 §21.2 第 7 条不变）。
- 12 轮 / 128 工具 / 5 分钟等既有上界不变；回执计入核验员的工具预算。
- `invalid_line_range` 附带可操作的更正说明。

Worker 面的 `invalid_line_range` 等准备失败仍按原路径终止，本决策不扩展；同一机制可作为后续 Seam。

### D4 模型可见描述

`spawn_session` 的 `model_review` 描述补充：请求联网能力的只读任务上，`model_review` 只指导报告，不做独立验证。该描述经能力清单进入模型上下文，不新增 Context Source。

### D5 界面表达

`independentVerifier=not_required` 时，任务现场顶部状态条的核验按钮显示「无需核验」且不带「通过」色调，不显示「核验通过」；裁决抽屉的独立复核行显示「无需独立核验」，质量标准行显示「未经独立核验」。事实来源仍是宿主核验结论；界面只表达，不产生核验事实。

实施期间 `codex/native-rust-cli` 的 `ace6b57b` 把子任务视图改为对话优先，原正文里的核验横幅不再存在。本决策的表达因此落在状态条按钮（`verdictStrip`）与裁决抽屉（`TaskVerification`），两处都只读取宿主检查项的 `reason`。

## 3. 修订与澄清的条款

| 文档 | 原条款 | 本决策 |
| --- | --- | --- |
| ADR 88 §7.1 | `model_review` 由受控 Verifier 验证；无效报告、缺证据或对象变化保持未通过 | 对 D1 类会话不再适用：标准保持未核验的事实，但不阻断关闭闸门。其余会话不变 |
| 委托运行时「验证下限」 | 只读调研 / 文档 → 验证闸门（叶子证据） | 不变。明确 D1 类会话按此行执行，不因 `model_review` 标准或核验模型配置而自动上调 |
| ADR 131 NR-04 | 普通 headless 的成功也必须等待独立核验 | 澄清：范围是普通 headless Goal Runner，不覆盖委托 work session |
| ADR 93 §5.3、ADR 103 | 取消 / 权限拒绝 / 超时 / 预算耗尽立即结束 | 不变。D3 的准备失败回执不属于这些类别 |

ADR 117「上述缺口不是放宽授权、删除核验或增加默认累计上限的理由」与架构治理基线「不因收拢展示而取消核验或吞掉失败」继续有效：本决策不删除核验、不放宽授权，只把一类核验员无法读取证据的会话落实到书面下限，并把核验失败如实分列。

## 4. 不变的部分

- 写任务、界面任务、本地只读调研的核验、签收、返修、Evidence、权限、续跑与预算全部不变。
- 核验员能力上限、只读 Worker 能力上限不变。
- 不新增能力、授权、IPC 方法、存储路径或 Context Source。
- 既有计划不迁移、不改写：已完成并记为 `failed` 的 D1 类会话保留失败记录、失败标题与核验历史，不会被自动签收；其未经核验的 `model_review` 不再阻断关闭闸门，用户可以手动签收。显式复核仍可按 D2 进行。

## 5. 取舍

没有选择所有只读调研/文档任务一律免核验：本地只读调研的核验员能读文件，既有用例规定了这条契约，且它确实能发现 Worker 读错。没有选择给核验员联网能力：核验员的只读边界是 ADR 80 / 88 的书面决定，而且用户反馈的是这类核验的成本与阻塞，不是裁决质量。没有选择只修崩溃：即使不崩，核验员对网页证据仍然失明，裁决只能靠猜测。

判定依赖模型填写的 `requiredCapabilities`。只读会话的能力上限保证它写不了文件、跑不了命令，多报联网能力只会让自己的报告不被复核，不会隐藏副作用。

## 6. 验证

先红后绿，覆盖：

- D1 判定矩阵（只读 + 联网、非只读 + 联网、只读无联网、请求交互结果发布）。
- 关闭闸门：D1 类会话的未核验 `model_review` 不阻断；本地只读会话的未核验 `model_review` 仍阻断。
- 核验结论：`not_required` 的 `independent_verifier` 检查项带 `reason=not_required`，`model_review` 检查项为 `not_reviewed`。
- 端到端：联网只读会话完成后核验模型零请求、状态 `not_required`、无核验运行记录；本地只读会话仍由核验员评估 `model_review`。
- D3：核验员先用非法行号调用 `read_file`，收到未派发结果后更正并给出裁决；未投影工具名仍终止。
- 界面：`not_required` 的核验按钮为「无需核验」且无通过色调；裁决抽屉显示「无需独立核验」「未经独立核验」。

实际结果、候选身份与未覆盖范围在实施后补录于下。

## 7. 实施验收记录（2026-11-25）

实现者自审（`independent=false`）。候选为 `Peer-Agent` `8451826c`（合并提交，含实现 `5fc41bf3` 与 `codex/native-rust-cli` 的 `ace6b57b`），分支 `PeerAgent/pa/research-verifier-floor`，已推送。在独立工作树与独立构建目录完成，未触碰原工作树、运行中的 daemon 和用户数据；未并入开发线，未经安装版验收。

**实现候选 `5fc41bf3`（基于 `78bece77`）**

先红后绿：保留测试、把实现还原到基线时，联网调研用例报「不得请求独立核验」，行号更正用例只收到 1 个核验请求即终止；把 D1 判定关掉时，3 个签收单元用例失败；裁决抽屉在基线组件上把「无需核验」显示为「通过」。恢复实现后全部通过。

| 范围 | 结果 |
| --- | --- |
| `cargo check --locked --workspace` | 通过，0 警告 |
| `cargo clippy`（`peer-runtime`、`peer-project-agent`，含测试） | 0 警告 |
| `peer-project-agent` 单元 | 106 通过（基线 102，新增 4） |
| `peer-project-agent` e2e | 54 通过 / 1 失败（基线 51 / 2）。新增 2 个用例，并为既有联网调研用例加上 `not_required` 断言；修复 `aadf11c0` 之后失效的只读上限夹具（只读任务请求写/shell 现在在准入即被拒）。剩余失败 `stopped_turn_persists_agent_stopped_card_and_retry_carries_retry_continuity` 为基线既有，与核验无关 |
| `peer-project-agent` TS/Rust parity | 4 通过（需先构建 TS 产物） |
| `peer-runtime` 单元与集成 | 与基线一致。`model_oauth…reserve_once…` 与 `model_count…fingerprint` 在基线上即失败（后者已在基线 `tool.rs` 上单独复核）；`shell::session…cancellation…` 并行负载下失败、单独运行通过 |
| 桌面 typecheck | 通过，0 错误 |
| 桌面完整测试（已构建 `peer-native`） | 5818 个：5810 通过 / 3 失败 / 5 跳过，在基线构建上结果相同。3 个失败是 `classic-core-bridge` 删除后在线状态断言（负载下失败，基线与本候选单独运行均通过）、`evidence-deliveries` 路径式 ID 校验、Frost CSS token 契约，均不涉及本次改动 |
| i18n 中英键位一致性 | 通过（912 键） |

`architecture:check` 与 `ui:check` 在该基线上因其他提交带入的 CSS（`bot-touchbar.css`、`bot-conversation.css`、`deferred-panel.css`、`bot-list.css` 等）失败，本次未改任何 CSS，检查器对本次改动的 TSX 文件没有报告。

**合并 `ace6b57b` 后的复验（候选 `8451826c`）**

`ace6b57b` 改为对话优先的子任务视图并移除了正文核验横幅，与本次横幅改动在 `TaskWorkspaceView.tsx` 冲突。按 D5 把表达迁到状态条核验按钮（`verdictStrip`）后复验：

| 范围 | 结果 |
| --- | --- |
| `peer-project-agent` 单元 / e2e / parity | 107 通过；54 通过 / 1 失败（仍为 `stopped_turn…`）；4 通过 |
| `cargo check --locked --workspace`、`cargo clippy` | 通过，0 警告 |
| 桌面 typecheck | 通过，0 错误 |
| 桌面完整测试（重建 `peer-native`） | 5818 个：5811 通过 / 2 失败 / 5 跳过。剩余 2 个是路径式 ID 校验与 Frost CSS token 契约；负载下不稳定的删除后在线状态断言本次通过 |

`peer-runtime` 未被该合并触及，沿用上面的结果。

覆盖边界：模型响应由测试控制；文件读取、授权、Evidence、核验会话、签收判定与删除/恢复链路使用生产入口和真实 `peer-native`。没有验证真实模型的裁决质量，未运行产品截图回归、读屏与安装版验收，未替换或重启运行中的应用。

已知未修项：落账守卫 `tool_facts` 在核验面长搜索后的误拒（触发检查项未定位）、`search_files` 逐文件授权复核导致的 30 秒级耗时、Worker 面的 `invalid_line_range` 等准备失败仍终止整轮、核验员请求未投影工具仍终止整轮（后者由用例钉住为现行边界）。
