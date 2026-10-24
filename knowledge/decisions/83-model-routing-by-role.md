# 83. 模型分工：档位 + 角色，用户说了算，开任务时冻结

创建时间：2026-09-24
最后更新：2026-10-24（补齐档位参数、角色继承覆盖与请求通道）

## 状态

Accepted（2026-09-26，P0-2）。实施与验收以代码、实施卡及本文补充记录为准。档位 + 角色、复核优先不同源、「自动」只在用户给定的池内挑选，均按本文执行。

默认值：只有一个可用模型时，四个档位都指向它，所有角色跟随档位，行为与今天一致。多个模型时，`strong` 指向当前默认模型，`fast` 与 `economy` 在用户改设置之前也指向它，`vision` 指向第一个能看图的模型。普通会话仍走会话级模型绑定；`compactor` 角色只用于项目代理体系。

## 级别

A 级。改变模型绑定契约（从「一个会话一个模型」到「按角色解析」）、Provider 故障切换的约束、任务快照内容、新增用户可见设置与调度工具。

## 关联

- `knowledge/decisions/80-project-agent-delegation-model.md`（项目代理、任务、子 agent 三层）
- `knowledge/architecture/project-agent-capability-layers.md` §3.2（`AgentProfileRegistry.defaultModelBinding`，本 ADR 落实）
- `knowledge/architecture/project-agent-delegation-runtime.md` §13 未决问题 2（代理与任务是否默认用不同模型，本 ADR 回答）
- `knowledge/decisions/30-provider-recovery-broker.md`（故障切换，本 ADR 加约束）
- `knowledge/decisions/37-provider-channel-and-wire-protocol-separation.md`（Provider 渠道与协议）
- `knowledge/decisions/25-runtime-usage-ledger.md`（用量账本，本 ADR 加角色维度）
- `knowledge/decisions/81-project-agent-memory-system.md`、`82-project-objectives-and-watches.md`（记忆提取、目标探测的模型）

## 背景

现状：会话上存一个 `modelProviderId`，`resolveConversationModelProviderId` 负责解析；任务内的 Explorer、Verifier、视觉复核都继承所属任务会话的模型。问题：

1. 项目代理要快、要会分诊，干活的任务要强，后台探测和记忆提取要省——一个模型兼顾不了。
2. 视觉复核要求模型能看图；任务模型不支持时直接报 `visual-review-vision-unavailable`，而不是换一个能看图的模型。
3. 复核用和执行同一个模型，容易「同一个错犯两遍还看不出来」。
4. 用户想指定「这个任务用哪个模型」「以后复核都用某家」，没有地方说。

## 2026-10-24 补充：全局角色的思考强度

用户要求补齐“模型分工”缺失的思考强度选择。思考强度是角色设置的可选维度，适用于 fixed、tier、auto；设置强度不得把跟随档位悄悄改成固定模型。未设置时沿用最终选中模型的已声明默认值；显式值只覆盖该角色，不修改模型目录或其他角色。模型/范围/能力解析顺序、项目覆盖与任务冻结保持本 ADR 原规则。

复用 RoleSetting 的可选 reasoningEffort 字段，旧配置无需迁移。主进程持久化前校验新值；纯解析器对最终选中模型校验实际支持值，不支持时返回 reasoning 失败，不静默改档或伪造支持。UI 的跟随档位/自动候选取实际合格候选支持值的交集；没有声明或没有公共档位时解释原因，仍可清除旧的失效覆盖。只有一个模型也可以设置角色强度。切换模式/模型保持仍兼容的显式值；不兼容时显示不可用并允许恢复模型默认，不自动把用户值替成另一个强度。

已保存配置的解析预览显示最终模型及其实际思考强度；读取/保存失败沿既有表单草稿、反馈和重试，不以本地选中值冒充写入成功。沿既有 model-routing IPC/设置存储，不新增能力、许可、Evidence、Context Source 或新持久路径。全局配置修改仅影响下一次解析/新任务，已冻结任务不改变。该补充为 A 级可选契约扩展，先登记本决策，再实现共享解析与宿主/界面适配；完整验证继续遵循当前用户授权范围和发布门禁。

## 2026-10-24 补充：档位参数与角色覆盖

按用户授权扩展已有模型分工契约（A 级），沿原设置存储、typed model-routing IPC 和 Provider encoder seam。每个 ModelTierBinding 增加可选 reasoningEffort 与 fastMode；无字段继续使用模型默认强度与正常通道。RoleSetting 三种模式均可覆盖：reasoningEffort 未提供时跟随所选档位，null 明确恢复最终模型默认，合法字符串为显式强度；fastMode 未提供时跟随所选档位，false 明确正常，true 明确快速。fixed/auto 没有档位，未提供即模型默认/正常。旧的显式强度和固定模型 fastMode 保留，不迁移或自动改写已有配置。

共享纯解析先决定模型，再按“角色显式值 > 所选档位值 > 模型默认/正常”解析参数。快速支持沿现有 OAuth ChatGPT/Grok 通道准入，不因为模型名相似、fast 档位或模型声称支持就创建快速能力；不支持返回 fast_mode 失败，不静默变正常或换模型。显式强度仍按真实模型声明校验。失败恢复候选亦须满足相同有效强度/快速约束；冻结选择保存实际参数（含显式正常），执行器传递到既有 Provider encoder，不改变已运行任务。

Renderer 复用共享菜单及 capability 投影：档位提供模型/默认强度/正常或快速；角色默认继承并可单独覆盖或恢复模型默认/正常。不支持选项保留说明，失效显式值可见并允许清除；保存错误保留草稿，预览取宿主已保存事实，读取不提交默认值。每次更新仅验证被修改的角色/档位参数，已有失效配置不得阻断不相关编辑；修改模型不自动清除显式参数。原权限、Evidence、System Context、角色优先级与预算规则保持不变。

本地开发交付只更新必要运行产物与实验室进程，不发布、不写用户已有模型配置；补契约/解析/候选约束与保存用例，按当前 Validation Scope 不运行测试或回归，发布 E13 再验收真实通道和冻结恢复。

## 决策

### 1. 两层配置：档位 + 角色

**档位**是用户一次性配好的抽象层，把能力需求映射到具体模型：

| 档位 | 用途 |
|---|---|
| `strong` 强 | 写代码、复杂推理、复核 |
| `fast` 快 | 对话、分诊、汇报 |
| `economy` 省 | 后台探测、记忆提取、压缩、只读探查 |
| `vision` 视觉 | 截图对比、看界面 |

每个档位可以配一个主模型和若干备选（按顺序），用于故障切换与「自动」挑选。

**角色**默认指向某个档位，也可以单独覆盖：

| 角色 | 默认 | 硬性要求 |
|---|---|---|
| `project_agent` 项目代理 | `fast` | 工具调用 |
| `session_worker` 任务 | `strong`；任务类型为界面时要求能看图 | 工具调用 |
| `explorer` 只读探查 | `economy` | 工具调用；上下文不小于阈值 |
| `verifier` 独立复核 | `strong`，**优先与执行模型不同源**（§3） | 工具调用 |
| `visual_verifier` 视觉复核 | `vision` | 看图 |
| `memory_curator` 记忆提取 | `economy` | 结构化输出 |
| `objective_probe` 目标探测 | `economy` | 工具调用 |
| `compactor` 上下文压缩 | `economy` | 上下文不小于待压缩内容 |

每个角色的取值是三选一：**跟随档位**（默认）/ **固定模型** / **自动**（在允许的模型池里由代理按难度挑，§4）。

### 2. 解析顺序与作用域

从高到低，第一个有值的生效：

1. 本次指定：用户说「这个任务用 X」→ 代理在 `spawn_session` 带 `modelPreference`。
2. 本任务 / 本目标：在任务现场或目标卡上改。
3. 本项目：项目设置覆盖全局。
4. 全局：档位映射 + 角色默认。

每一层的结果都要过两道过滤：

- **能力过滤**：不满足角色硬性要求的模型剔除（例如视觉复核剔除不能看图的）。
- **范围过滤**：项目允许的模型 / Provider 范围（如「只用本地模型」「只用公司网关」）。范围只能收紧：项目层可以缩小全局范围，本次指定不能突破项目范围。

过滤后为空时不静默降级：开任务失败并告诉用户缺什么（例如「本项目只允许本地模型，但没有能看图的本地模型，视觉复核无法进行」）。

### 3. 不同源复核

- 用户固定的模型与渠道必须原样使用；执行、探查、复核可以全部使用同一模型、同一渠道。独立复核指独立执行上下文和宿主记录的复核运行，不要求另购渠道或另选模型。
- `verifier` 默认优先选择与该任务执行模型**不同 Provider 家族**的候选（来自 `strong` 档位的备选或用户固定的复核模型）。
- 上述偏好只对用户配置的多个合格候选排序；不能覆盖固定模型，不能扩大允许池。代理不得因“独立复核”自行更换模型或要求用户更改配置。用户本次明确指定、配置的自动池与已配置故障切换仍按 §2、§4、§5 执行。
- 没有不同源候选时，退回同模型，但仍是独立上下文；验证详情里标明「同源复核」。
- 不同源与否写进 `VerificationVerdict`（ADR 80 决策 8）的 `independentVerifier` 旁：`verifierModel`、`sameFamilyAsWorker`。签收策略不因同源而改变，但结论标记与验证报告要如实显示。

#### 失败诊断与来源元数据（2026-10-20）

现场主 Bot 将 `independent_verifier=failed` 与 `sameSource=true` 推断为“同模型不独立，必须换通道”。原始记录分别是产品回归审查证据缺失、复核轮次耗尽，并非同源拒绝。现有 `get_verification_detail` 只返回笼统 failed/missing 与来源标记，丢失具体复核诊断，促成错误归因。

- `sameSource` / `sameFamilyAsWorker` 仅描述路由来源，不是失败原因，也不推导复核是否通过。Provider family 目前来自配置类型，不能把它宣称为已验证的模型供应商血缘。
- 既有验证事实接口补充有界 `reviewAttempts`：最多三个已持久化的计划级终态复核记录，含真实运行 ID、状态、结束时间、错误、未满足标准、缺失证据与建议。模型报告内容仍是事实数据，不提升为 System Context 指令。
- 历史诊断显式标记 `diagnosticOnly=true`，依据版本绑定记录显示 `matchesCurrentSource=true/false/null`（null 为未绑定）；它既不成为验收真值，也不改变现有 Evidence、版本新鲜度与人工签收门禁。较早失败不能覆盖新的成功，缺少诊断必须报告原因未知。
- 项目代理与 verifier 的既有 Context Source、委托工具说明同步澄清：读取具体失败，不从同源标记臆造原因；沿用冻结模型；不因同源要求用户决定或换模型。无新增能力执行通道、权限或 Renderer 存储。
- 验证覆盖：有异源候选且偏好启用时固定同模型仍原样解析；同模型复核通过后可完成并签收；同模型的真实证据缺失仍拒绝；历史错误和当前结论分开；诊断有界、版本过期、未知原因与伪造模型自述不能成为通过依据。
- 本次实现还移除委托工具内部未由用户配置驱动的 `preferDifferentSource=true` 提示参数；实际宿主一直使用冻结快照，故这不是修复一个已确认的路由覆盖，而是消除错误暗示。保留用户显式设置的候选排序偏好。
- RC22 已发布并用未修改的公开 macOS 签名包验证：同模型、同渠道、执行/复核均为 max，宿主记录 `independentVerifier=passed`、计划 completed 且策略签收成功；真实诊断回复没有要求换模型。1100 计划与约 185 MB 协调日志的完整真实任务、取消、长回复和交互门槛通过。见[公开包验收记录](../../playbook/v0.1.0/evidence/rc22-model-selection-verification-20261020.json)。记录保留实施者自审、合成数据、隔离运行及各平台覆盖限制。
- 验证记录（2026-10-20）：78 项定向测试、41 项 System Context 包测试及全仓 typecheck / architecture:check 通过。另用源码生产 Electron、隔离合成任务记录和真实 DeepSeek 请求验证：所有角色固定同一模型/渠道与 max，实际只调用 `get_verification_detail`、`post_reply`，回答证据缺失及旧 12 轮上限，并明确无需换模型。角色配置保持原值，没有重跑任务；测试凭据副本已清理。该记录不代表安装版验收、完整任务执行或视觉产品回归。准备阶段的快照夹具错误和本地测试 helper 超时均未计作通过，改正夹具并使用 RC21 打包 helper 后完成上述真实请求。

### 4. 「自动」：代理在池内挑

- 角色设为「自动」时，用户给一个允许的模型池（默认是该档位的主模型 + 备选）。
- 代理开任务时根据任务类型与难度在池内选择，并在 `spawn_session` 里给出 `modelChoiceReason`（一句话）。
- 运行时校验所选模型在池内且通过能力与范围过滤；不在池内直接拒绝。
- 代理不能扩大池子，不能修改档位映射与角色设置。

### 5. 开任务时冻结

- SessionSupervisor 在 `spawn_session` 时解析出各角色模型，写入 `DelegationOrigin.modelSelection`：

```ts
interface ModelSelectionSnapshot {
  worker: RuntimeModelSelection;        // providerId + modelId + reasoningEffort
  explorer: RuntimeModelSelection;
  verifier: RuntimeModelSelection & { sameFamilyAsWorker: boolean };
  visualVerifier?: RuntimeModelSelection;
  source: Record<string, 'this_request' | 'task' | 'objective' | 'project' | 'global' | 'auto'>;
  autoReason?: string;
  resolvedAt: string;
}
```

- 任务运行中不自动换模型（换模型会打掉提示缓存，行为也会变）。用户手动换，从下一轮生效，并记一条 run event。
- 故障切换（ADR 30）只能在该角色**过滤后的候选**里切：同档位备选、满足硬性要求、在项目范围内。切换写入 run event 与用量记录，验证详情可见。

### 6. 用户怎么改

- **设置页「模型分工」**：上半部分档位映射（主模型 + 备选），下半部分角色表（跟随档位 / 固定 / 自动 + 池）。项目设置可覆盖全局并限定范围。
- **对代理说**：「这个任务用 X」→ 本次指定；「以后复核都用 X」「这个项目只用本地模型」→ 代理调用 `set_model_policy` 改设置。`set_model_policy` 必须锚定用户消息，改动在设置页可见、可撤销；代理不能自己改。
- **任务现场 / 验证详情**：显示执行模型、复核模型（是否不同源）、是否发生过故障切换。

### 7. 用量与预算

- ADR 25 的用量账本增加 `role` 维度；用量面板可按角色看花费。
- 每个角色可设日花费上限；超限时该角色停止自动调用并告诉用户（项目代理与必达的需要你除外，改为提示）。

## 后果

- 项目代理响应更快、更省；干活的任务用最强的模型；后台工作不再烧强模型。
- 视觉复核不再因任务模型不能看图而失败，改为自动选能看图的模型。
- 复核更独立，验证报告能说清楚「谁执行、谁复核」。
- 模型绑定从会话级扩展为角色级：`resolveConversationModelProviderId` 保留给普通会话，项目代理体系改走 `resolveRoleModel(role, context)`；需要兼容旧会话（无角色设置时等价于「全部跟随会话模型」）。
- 多了一页设置。默认值要开箱可用：只有一个模型时，所有档位都指向它，行为与今天一致。

## 不做什么

- 不让代理扩大模型池、改档位映射或角色设置。
- 不在任务运行中自动换模型（故障切换除外，且只在过滤后的候选里）。
- 不为了「能跑」而静默突破项目的模型范围。
- 不做按 token 实时比价的动态路由；「自动」只在用户给定的池内按任务难度选。

## 2026-10-18 补充：子任务会话的强度投影

现场任务快照 worker/verifier 为 `max`，而子会话 metadata effort 为从父会话继承的 `high`。执行器优先取冻结角色的 reasoningEffort，任务输入框却读取会话 metadata，造成界面与执行配置矛盾。

- 新建 work_session 时，SessionSupervisor 必须同时传递冻结的 modelProviderId 和 reasoningEffort；Conversation Store 的内部 createChildConversation 接受可选 effort，未提供时保留普通子会话的父级继承。
- 打开现有 work_session 时，Desktop 的会话读取 Module 以与 conversationId、sessionId、workspaceId 匹配的持久任务快照投影模型/强度；不读取当前 Bot 策略冒充旧任务配置，不修改任务执行快照，不批量回写用户数据。
- 同一读取 Module 保留原有 Context Accounting window 投影。Renderer 继续使用既有 conversations:get 契约，不新增能力入口或权限路径。
- 无快照的历史任务保留既有 metadata；普通会话和选区子会话的显式偏好不变。角色快照不是 Provider 实际执行证明；请求编码与回合记录仍应分别核对。
- 验证：父级 high / worker max / verifier low；冻结后改 Bot 配置；重启加载；旧会话 high 投影为冻结 max；跨任务/跨项目不得串配置；Provider 编码仍保留原生 max。
