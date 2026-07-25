# ADR 56：Provider 实测优先的精确上下文记账

- 创建时间：2026-07-25
- 最后更新：2026-07-25
- 状态：已采纳，核心发送管线已落地，协议/UI 清理继续
- 关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）
- 取代：ADR 52 中“本地估算是上下文权威值、provider usage 只用于诊断”的决策
- 保留：ADR 52 关于最终请求投影 seam、跨端 `_compaction` 分界、单 Runtime 入口和 revision 防乱序的决策

## 一、问题

一次 Grok 500K 上下文会话已经取得以下 provider 证据：

```text
上一成功请求 input usage：498,138 tokens
下一请求被 provider 拒绝：501,244 tokens > 500,000 tokens
当时 CLI 显示：53%
```

这不是普通估算误差，而是上下文真值所有权错误：

1. Runtime 已经收到 provider 对真实请求的 token 计量；
2. UI 和压缩协调器没有把这份实测结果作为权威事实；
3. 本地启发式估算漏计或错计最终 wire payload，仍覆盖实测证据；
4. 因此系统一边显示 53%，一边实际发送超过 500K 的请求。

ADR 52 把 `nextRequestInputTokens` 的本地估算定义成唯一权威值，并规定上一请求 usage 不得参与 UI 主值和压缩判断。该决策在“最终请求投影必须统一”这一点上是正确的，但在“谁拥有 token 真值”这一点上是错误的。

## 二、决策

### 2.1 真值只来自两类精确证据

上下文容量链路只接受：

1. **Provider observed usage**
   - provider 对已经真实处理的请求返回的 usage；
   - 由 provider adapter 归一化为该请求的实际输入占用；
   - 是最近一次已发送请求的最终权威事实。
2. **Provider-aligned exact count**
   - 对即将发送的最终 canonical request 进行精确计数；
   - 必须使用 provider 的 count API、同源 tokenizer，或与当前模型和 wire 协议严格绑定且经过实测校验的编码器；
   - 是发送前判断下一请求是否装得下的权威事实。

字符数比例、CJK/英文启发式、JSON 长度折算、按消息固定开销和 renderer 历史扫描都不是上下文真值。它们不得进入：

- 用户可见上下文百分比；
- soft/hard limit 判断；
- 自动压缩触发；
- provider request 放行；
- 跨端持久化的权威快照。

### 2.2 两个时间点，不是两套互相竞争的口径

协议明确区分：

```text
lastObservedInputTokens
  最近一次真实发送并由 provider 计量的请求输入

nextCountedInputTokens
  当前 canonical next request 经精确计数后的输入
```

二者描述同一条请求链上的不同时间点，且都必须携带：

- `requestFingerprint`：绑定具体 canonical request；
- `contentRevision`：绑定会话内容版本；
- `modelKey`：绑定 provider、model 和 tokenizer/version；
- `source`：只能是 `provider_usage`、`provider_count_api` 或 `provider_tokenizer`；
- `observedAt` 或 `countedAt`。

不得用 `Math.max(actual, estimate)` 合并，不得让旧请求实测覆盖已经精确计数的新请求，也不得让本地估算覆盖任何实测值。

### 2.3 Provider usage 必须按 provider 语义归一化

不同 provider 的 cache 字段语义不同，不能在共享层盲目执行：

```text
input + cache.read + cache.write
```

例如某些 provider 的 `inputTokens` 已经包含 cached input，另一些 provider 则把 cache read/create 单列。共享 Runtime 只消费 adapter 归一化后的：

```text
normalizedInputTokens
```

每个 adapter 必须通过 fixture 固化字段关系，证明不会漏计或重复计算 cache。累计计费 usage 继续归 ADR 25 管理，不得直接充当上下文占用。

### 2.4 精确计数对象必须是最终 wire request

发送前计数发生在所有转换完成之后、网络发送之前：

```text
持久化会话
  -> active history / _compaction 分界
  -> system context 装配
  -> tool call / tool result 结构化
  -> tools schema
  -> 附件与图片转换
  -> microcompaction / artifact reference
  -> provider-specific message mapping
  -> canonical wire request
  -> exact count
  -> 容量决策
  -> send
```

计数器与发送器必须消费同一个 immutable canonical request。禁止“统计一份 projection、发送时重新组装另一份 payload”。

`toolCalls[].arguments`、工具结果、system prompt、tools schema 和 provider wrapper 都必须由最终编码器自然纳入；不能依赖各层维护一张人工成分清单。

### 2.5 容量判断

Runtime 使用 provider/model 声明的窗口和输出预留计算输入预算：

```text
inputBudget =
  min(
    providerMaxInputTokens（若存在）,
    contextWindow - requiredOutputReserveTokens
  )
```

放行规则：

```text
nextCountedInputTokens < inputBudget
```

压缩规则：

```text
nextCountedInputTokens >= compactionThresholdTokens
或
lastObservedInputTokens >= compactionThresholdTokens
```

后一条保证：即使下一请求尚未完成精确计数，只要上一请求实测已经接近窗口，也必须先压缩，不能无视已经拿到的高水位证据。

`lastObservedInputTokens` 的触发资格受 `compactionEpoch` 约束：它只能保护产生该 usage
时的 active history epoch。压缩 handoff 持久化成功后进入新 epoch，旧 usage 保留为审计证据，
但标记为 `superseded_by_compaction`，不得在新 epoch 中重复触发压缩。

压缩完成后必须重新构造 canonical request、生成新 fingerprint、重新精确计数。旧计数不能按压缩比例推导；若 provider 只有 observed usage，新 epoch 在首次成功请求前显示“已压缩，待 provider 计量”。

### 2.6 UI 显示规则

UI 只显示带来源的精确状态：

| 状态 | 主值 | 展示 |
|---|---:|---|
| 最近请求已返回 usage，当前内容未变化 | `lastObservedInputTokens` | `498K / 500K · Provider 实测` |
| 下一请求已完成精确计数 | `nextCountedInputTokens` | `472K / 500K · 待发送精确值` |
| 有新内容，但尚未完成精确计数 | `lastObservedInputTokens` | `498K 已实测 · 有待计量内容` |
| 压缩已进入新 epoch，尚无新证据 | 无 | `已压缩 · 待 provider 计量` |
| provider 无 usage，且无精确计数能力 | 无 | `上下文占用未知` |

禁止把“未知”渲染成 0%、53% 或其他伪精确百分比。Renderer 不解析历史消息、不计算 token、不自行决定取最大值，只消费 Runtime 快照。

草稿预览可以显示字符数或“待计量”，但不得伪装成 token 百分比，也不得写回权威快照。

### 2.7 Provider 不具备精确计数能力时

Provider adapter 必须显式声明：

```ts
type ContextCountCapability =
  | { kind: "provider_count_api" }
  | { kind: "provider_tokenizer"; tokenizerVersion: string }
  | { kind: "observed_usage_only" }
  | { kind: "unavailable" };
```

对于 `observed_usage_only`：

- 已返回的 usage 仍是权威事实；
- 新增内容标记为“待计量”，不得估算成百分比；
- 上一实测达到压缩阈值时直接压缩；
- 仍可能因单次大增量首次撞到 provider 上限，因此必须保留 prompt-too-long 自动恢复。

对于 `unavailable`：

- UI 显示未知；
- 不持久化数值型权威快照；
- provider overflow 成为最后安全闸门；
- 产品可以限制该 provider 的自动长程运行能力，但不能用启发式数字冒充正确计量。

## 三、运行时状态机

```text
1. BUILD
   构造 immutable canonical request

2. COUNT
   使用 provider-aligned exact counter
   产出 requestFingerprint + nextCountedInputTokens

3. DECIDE
   与 inputBudget / compactionThreshold 比较

4. COMPACT（如需要）
   持久化 _compaction handoff
   回到 BUILD，禁止复用旧 count

5. SEND
   只允许发送与 count fingerprint 相同的 payload

6. OBSERVE
   接收 provider usage
   adapter 归一化为 lastObservedInputTokens

7. VERIFY
   对比同一 fingerprint 的 counted 与 observed
   发现漂移则记录 provider/model/tokenizer 级故障，
   使该 exact counter 降级，不得静默继续宣称精确

8. RECOVER
   provider 返回 prompt-too-long 时：
   分类 -> emergency compact -> rebuild -> recount -> retry once
```

所有普通对话、工具循环、Goal Runner、Desktop 和 CLI/TUI 必须经过同一个状态机。宿主不能复制计数或阈值逻辑。

### 3.1 统一的是整条管线，不只是共享原语

以下状态转换必须由一个共享深模块拥有：

```text
ContextAccountingCompactionPipeline
  BUILD
  -> COUNT
  -> DECIDE
  -> COMPACT
  -> REBUILD
  -> RECOUNT
  -> SEND
  -> OBSERVE
  -> VERIFY / RECOVER
```

仅共享 `estimate*`、`microcompact`、`splitMessagesForCompaction`、
`runCompactionSummaryCascade`、`decideContextCompaction` 或
`isPromptTooLongError` 等函数，不算完成统一。只要 Desktop coordinator 与 CLI/TUI
controller 仍分别编排状态转换，就仍然存在双管线和再次漂移的可能。

目标调用关系：

```text
Desktop Host ─┐
              ├─ ContextAccountingCompactionPipeline
CLI/TUI Host ─┘       ├─ ProviderRequestAdapter
                      ├─ ExactCountAdapter
                      ├─ CompactionStrategy
                      └─ HostEffectsAdapter
```

普通发送、agent/tool loop 中途发送、Goal tick、手动 `/compact`、自动 preflight
和 emergency recovery 都是同一管线的不同 command/reason，不能成为独立实现。

### 3.2 允许变化的是 Adapter 与 Strategy

统一管线不要求 Desktop 与 CLI/TUI 拥有相同 UI 或基础设施：

- `ProviderRequestAdapter`
  - 构造 provider-specific canonical request；
  - 精确计数；
  - 发送；
  - 归一化 usage 和 overflow。
- `CompactionStrategy`
  - `LlmSummaryStrategy`；
  - `StructuralStrategy`；
  - 失败降级顺序。
- `HostEffectsAdapter`
  - 持久化 `_compaction` marker；
  - 发布进度和状态事件；
  - Desktop IPC 或 CLI/TUI snapshot 更新。

Strategy 可以因 provider 能力不同而选择不同实现，但切分合同、触发时机、epoch
推进、重新计数、重试上限和终态语义必须由共享管线固定。差异只能通过显式接口注入，
不能通过宿主复制流程实现。

### 3.3 宿主硬边界

迁移完成后：

- Desktop provider loop 不得直接调用压缩判定、切分、摘要或 emergency helper；
- CLI/TUI `chat-controller`、`provider-chat-model` 不得维护私有 preflight、
  `compactModelMessagesMidTurn` 或 PTL retry 流程；
- Renderer/TUI view 不得计算上下文百分比或触发压缩；
- 任何 provider transport 不得绕过共享 SEND gate；
- 手动 `/compact` 也必须提交给同一 pipeline，不能直接执行 strategy。

宿主只提交 command 和 adapters，接收 snapshot、progress 与 result。

## 四、协议

建议以新协议替代把估算值伪装成权威值的旧 `ContextProjection`：

```ts
interface ContextAccountingSnapshot {
  conversationId: string;
  contentRevision: number;
  modelKey: string;
  contextWindow: number | null;
  inputBudget: number | null;
  compactionThresholdTokens: number | null;

  lastObserved?: {
    inputTokens: number;
    requestFingerprint: string;
    compactionEpoch: number;
    source: "provider_usage";
    observedAt: number;
    supersededByCompactionRevision?: number;
  };

  nextCounted?: {
    inputTokens: number;
    requestFingerprint: string;
    compactionEpoch: number;
    source: "provider_count_api" | "provider_tokenizer";
    countedAt: number;
  };

  pendingUncountedChanges: boolean;
  countCapability: ContextCountCapability;
}
```

旧字段迁移规则：

- `nextRequestInputTokens`：只有来源为精确 count 时才可映射到 `nextCounted.inputTokens`；
- `lastActualInputTokens`：迁移为 `lastObserved.inputTokens`，从诊断字段升级为权威事实；
- `contextTokens`、`triggerTokens`、`authoritativeTriggerTokens`：废弃；
- 任何没有 `source`、`fingerprint`、`revision` 的旧数值快照：视为不可信，恢复时丢弃；
- `source: estimate`：协议层禁止进入 `ContextAccountingSnapshot`。

## 五、Prompt-too-long 兜底

精确记账不能替代 provider 错误恢复，因为：

- provider 可能额外注入服务端 prompt；
- 模型配置或 tokenizer 版本可能漂移；
- observed-only provider 无法发送前精确计数；
- 单次工具结果可能在两次请求间剧增。

因此所有 provider 必须归一化以下语义：

```text
ContextOverflowError {
  requestedTokens?: number
  maximumTokens?: number
  provider
  model
  rawCode
}
```

错误文本如：

```text
This model's maximum prompt length is 500000
but the request contains 501244 tokens
```

必须被识别。恢复流程固定为：

```text
捕获 -> 写入实测 requested/max 证据
     -> emergency compact
     -> rebuild + exact recount
     -> retry once
     -> 再失败则结构化终止
```

错误中返回的 `requestedTokens` 是本次失败请求的 provider 实测证据，也必须更新观测和诊断数据，不能被丢弃。

## 六、代码迁移边界

### Runtime core

- 新增 provider-agnostic `ContextAccountingCompactionPipeline`，完整拥有
  BUILD → COUNT → DECIDE → COMPACT → REBUILD → RECOUNT → SEND → OBSERVE/RECOVER；
- 只接收 normalized usage 和 exact count 结果；
- 删除 estimator 对 UI、阈值和放行决策的控制权；
- fingerprint 校验确保 count 与 send 是同一 payload。
- `microcompact`、split、summary cascade、PTL classifier 等原语降为 pipeline 内部实现，
  不再由宿主自由拼装。

### Provider adapters

- 实现 usage 归一化；
- 声明 exact count capability；
- count 与 send 共享 canonical request encoder；
- 归一化 prompt-too-long 错误及 requested/max tokens。

### Desktop / CLI/TUI

- 只消费并展示共享 `ContextAccountingSnapshot`；
- 删除 renderer/TUI 自建历史 token 百分比；
- Desktop 与 CLI/TUI 持久化同一快照结构；
- 恢复旧快照时，没有精确来源即失效，不重算伪值。
- Desktop 的 `provider-request-coordinator` / `compaction-coordinator` / provider loops
  收敛为 pipeline adapters；
- CLI/TUI 的 `context-pressure` 退化为 view formatter，`chat-controller` 与
  `provider-chat-model` 删除私有压缩编排；
- 两端不得直接调用 `decideContextCompaction`、`splitMessagesForCompaction`
  或 `runCompactionSummaryCascade`。

### Estimator

现有启发式 estimator 可以暂时保留给非容量场景，例如成本预览或性能诊断，但必须移出 `ContextAccounting` 命名空间，并通过依赖约束保证它不能被：

- compaction decision；
- provider request gate；
- context ring；
- authoritative snapshot

调用。

## 七、不变式

1. Provider 已返回 498,138 时，任何 UI 和决策路径都不能显示或采用低于该证据的无来源估算值。
2. 发送 payload 与精确计数 payload 的 fingerprint 必须一致。
3. UI 显示的每个 token 数字都能追溯到 provider usage 或 provider-aligned exact counter。
4. 新内容尚未计量时显示“待计量”，不显示伪百分比。
5. 压缩后必须重新构造并重新计数，旧高水位按 `compactionEpoch` 显式失效。
6. Cache token 只在 provider adapter 内归一化，共享层不猜字段关系。
7. Lifetime usage ledger 与 context accounting 完全分离。
8. Prompt-too-long 错误中的 requested/max token 证据必须保留并触发单次恢复。
9. 普通对话、工具循环、Goal Runner、Desktop 和 CLI/TUI 不得拥有私有计数路径。
10. 没有精确证据时允许显示未知，不允许显示错误的确定值。
11. Desktop 与 CLI/TUI 不得拥有私有压缩状态机；共享原语不等于共享管线。
12. 手动、自动和 emergency 压缩只能以 command/reason 进入同一个 pipeline。

## 八、验收标准

### 已知故障回归

- 输入：上一请求 provider usage 为 `498,138`，窗口为 `500,000`；
- 预期：UI 显示约 99.6% 和 `Provider 实测`；
- 预期：下一请求发送前进入压缩，不允许继续以 53% 放行；
- 预期：若 provider 报 `501,244 > 500,000`，错误分类成功并自动压缩重试一次。

### Canonical request 完整性

- `toolCalls[].arguments` 中加入 100K token，exact count 必须相应增长；
- system、tools schema、tool result、附件和 provider wrapper 都有 fixture；
- count fingerprint 与实际 send fingerprint 不同，测试必须失败。

### Provider 归一化

- 每个 provider 至少包含普通输入、cache read、cache write/create、reasoning/output 的 usage fixture；
- 测试证明 cache 不漏计、不重复计；
- counted/observed 漂移会产生显式故障，不会静默覆盖。

### UI 与恢复

- usage 可用时 Desktop 和 CLI/TUI 显示相同实测值；
- usage 缺失且无 exact count 时，两端都显示未知；
- 旧 estimator 快照恢复后被判无效；
- stream/tick 乱序快照不能覆盖更高 revision 的实测或精确计数。

### 架构治理

- 全仓 context capacity 决策调用点只依赖 `ContextAccountingSnapshot`；
- `estimate*Tokens` 不得出现在 compaction gate、context ring 和 authoritative snapshot 调用链；
- 所有 provider request 必须经过统一 BUILD → COUNT → DECIDE → SEND 闸门。
- `decideContextCompaction`、`splitMessagesForCompaction`、summary cascade 和 PTL retry
  在 pipeline 外的生产调用点必须为 0；
- Desktop 与 CLI/TUI 对同一 canonical fixture 必须得到相同 count、decision、
  compaction epoch 变化、marker 结构和 retry 终态；
- 允许 summary 文本因 strategy 不同而不同，但不得改变管线状态语义。

## 九、后果

### 正面

- 已取得的 provider 实测证据不再被忽略；
- UI 数字可解释、可追溯，不再用“权威估算”制造假精确；
- 最终 wire payload 中隐藏较深的 tool call arguments 等内容不会因人工成分表漏计；
- 压缩、显示、发送和错误恢复共享一条证据链；
- tokenizer 或 provider 行为漂移会被检测，而不是长期表现为百分比失准。

### 代价

- Provider adapter 需要承担 usage 归一化和精确计数能力声明；
- 部分 provider 无法提供发送前精确计数，只能显示已实测值加“待计量”，并依赖 overflow 恢复；
- count 与 send 必须共享 canonical request，可能需要调整现有 adapter 边界；
- 旧 `ContextProjection`、持久化快照和 UI 字段需要协议迁移。

这些代价是正确性成本，不能用启发式估算重新进入权威路径来规避。

## 十、实施记录（2026-07-25）

本轮已在 `peer_agent` 落地第一阶段：

1. `runtime-core/context-accounting-pipeline.ts` 成为共享
   BUILD → COUNT/OBSERVE → DECIDE → COMPACT → REBUILD → SEND →
   OBSERVE → OVERFLOW RETRY 状态机，并持有 `compactionEpoch`、
   canonical request fingerprint 与单次 PTL retry。
2. Desktop 的 OpenAI、Anthropic、Gemini、Qoder 四条 loop 均改走
   `executeDesktopProviderRequest()`；各 loop 原有 PTL recovery 状态机删除。
3. CLI/TUI `provider-chat-model.runTurn()` 改走同一个 runtime-core pipeline，
   原 `compactModelMessagesMidTurn()` 与手写 preflight/PTL catch 删除。
4. TUI 将上一轮 provider usage 显式带入下一轮 accounting；`498,138 / 500,000`
   会在下一次发送前触发压缩。
5. Grok `maximum prompt length ... request contains ...` 已纳入共享分类，
   `requestedTokens` / `maximumTokens` 作为 provider error evidence 保留。
6. Desktop 与 TUI 的稳定显示在取得 usage 后均以 `input + cacheRead` 为主值；
   本地 projection 不得覆盖该值。
7. 顶层 OpenAI `toolCalls[].arguments` 已补入旧 estimator 的诊断成分，
   避免迁移期日志继续产生明显漏计。
8. Desktop 手动压缩与 TUI 手动压缩已经复用共享 split/summary strategy，
   但尚未以 `command=manual_compact` 完成同一 pipeline 的入口收敛。

验证证据：

- runtime-core：50 tests 通过，typecheck/build 通过；
- Desktop chat-runtime：208 tests 通过，Desktop typecheck 通过；
- TUI 相关：66 tests 通过；
- TUI 全量 typecheck 仍被既有 `composer-image-paths.ts` 重复函数定义阻塞，
  与本次上下文管线改动无关。

尚未达到本 ADR 的全部退出条件：

- provider-aligned pre-send exact count adapter 尚未逐 provider 接入；
- 无 usage / 无 exact count 的旧 UI fallback 仍需迁移为“待计量”；
- 手动 compact 尚需统一为 pipeline command；
- counted/observed 漂移告警与跨端 canonical fixture 仍待补齐。

## 十一、参考实现

OpenCode 当前实现提供了两个可复用原则：

1. 每个 `step-finish` 把 provider usage 写入 assistant message，并立即以该 usage 检查 overflow；
2. provider 返回 `ContextOverflowError` 时进入 compaction 恢复。

参考：

- [OpenCode overflow.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/overflow.ts)
- [OpenCode processor.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/processor.ts)
- [OpenCode prompt.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/prompt.ts)
- [OpenCode context metrics](https://github.com/anomalyco/opencode/blob/dev/packages/app/src/components/session/session-context-metrics.ts)

Peer Agent 在此基础上增加 canonical request exact count、fingerprint 校验和 counted/observed 漂移检测，避免只依赖上一请求 usage 的一轮滞后。
