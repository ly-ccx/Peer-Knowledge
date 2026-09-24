# 83. 模型分工：档位 + 角色，用户说了算，开任务时冻结

创建时间：2026-09-24
最后更新：2026-09-24

## 状态

Proposed。三项核心选择由用户拍板（2026-09-24）：档位 + 角色默认；独立复核默认优先不同源模型；角色设为「自动」时代理可在用户允许的模型池内挑选。实现未开工。

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

- `verifier` 默认优先选择与该任务执行模型**不同 Provider 家族**的候选（来自 `strong` 档位的备选或用户固定的复核模型）。
- 没有不同源候选时，退回同模型，但仍是独立上下文；验证详情里标明「同源复核」。
- 不同源与否写进 `VerificationVerdict`（ADR 80 决策 8）的 `independentVerifier` 旁：`verifierModel`、`sameFamilyAsWorker`。签收策略不因同源而改变，但结论标记与验证报告要如实显示。

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
