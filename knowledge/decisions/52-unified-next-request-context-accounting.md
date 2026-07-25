# ADR 52：统一下一次请求上下文统计

创建时间: 2026-07-23
最后更新: 2026-07-25
状态: Superseded in part by ADR 56
关联代码仓: `peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）
取代: ADR 42 中“显示口径与压缩触发口径分离”的决策

> 2026-07-25 修订说明：本文关于“本地估算是权威当前值、provider usage 只用于诊断”的决策已被
> `56-provider-observed-context-accounting.md` 取代。最终请求投影 seam、跨端 `_compaction`
> 分界、单 Runtime 入口和 revision 防乱序仍然有效。阅读和实施时以 ADR 56 的精确证据链为准。

## Context

ADR 42 为修复压缩后进度条不回落，将上下文拆成两套口径：

- `contextTokens`：最近一次已经发送给模型的输入量，优先采用 provider usage；
- `triggerTokens`：完整会话估算与最近 usage 高水位的较大值，用于发送前压缩。

这解决了当时的局部问题，却让产品和实现出现了两份“当前上下文”：右下角可能描述已经过去的请求，而发送前压缩依据另一份估算。Goal Runner 在一次 tick 内连续追加 assistant 输出、工具结果和 continuation 消息时，差异尤其明显。Renderer 又增加 `authoritativeContextTokens`、`authoritativeTriggerTokens` 等跨层别名，使字段来源与业务语义混在一起。

用户真正需要知道的是：按当前状态继续执行，下一次请求是否接近模型输入上限。右下角展示与 Runtime 发送前决策不应分别回答两个问题。

## Decision

### 1. 唯一核心指标

系统采用唯一的当前上下文指标：

```text
nextRequestInputTokens
```

其定义是：

> 以当前会话状态立即继续执行时，下一次最终发送给模型的请求预计包含的输入 token。

该指标以**下一次最终请求投影**为统计对象，而不是完整持久化历史，也不是上一请求的 usage。

投影必须覆盖该 provider 下一次实际发送的全部输入：

- System Context 最终装配结果；
- 压缩、裁剪和 microcompaction 后仍会发送的消息；
- assistant 内容、tool call 和实际保留的 tool result；
- 当前用户输入，或 Goal Runner 下一条 continuation；
- tools schema、附件转换结果及 provider 可估算的请求包装。

不会进入下一请求的隐藏推理、已裁剪内容、已压缩原文和累计计费 token 不计入该指标。

### 2. 同一投影驱动展示与压缩

右下角上下文占用和发送前压缩协调器必须消费同一个 `nextRequestInputTokens`：

```text
当前会话状态
  -> Provider 请求投影
  -> 最终发送形态（含 microcompaction）
  -> nextRequestInputTokens
     -> Renderer 上下文展示
     -> soft/hard limit 判断
```

不得再以 `contextTokens` 与 `triggerTokens` 表示两套并列的当前上下文。`triggerTokens`、`authoritativeTriggerTokens` 及只为双口径服务的投影字段应在迁移后移除。

### 3. 估算、实测与计费分离

> 本节已被 ADR 56 取代，仅保留用于解释历史实现。

发送前无法获得 provider 对未来请求的精确 usage，因此 `nextRequestInputTokens` 是对最终请求载荷的确定性本地估算。它是产品和压缩判断的权威当前值。

Provider 返回的上一请求输入 usage 可保留为：

```text
lastActualInputTokens
```

它只用于诊断、估算器校准和回归观测，不得覆盖下一请求投影，也不得作为右下角主值或下一次压缩判断的分子。

累计 usage（input/output/cache read/cache write/total）属于计费与调用账本。它可以跨请求累加，不得参与上下文窗口占用计算。

### 4. 跨端压缩分界与恢复投影

完整持久化消息是 UI 历史，不等于下一次 provider 请求历史。Desktop 与 CLI/TUI 必须复用同一个持久化 `_compaction` handoff 作为 active provider history 的分界：

```text
完整持久化 messages
  -> 最后一个 _compaction
     -> 分界前原文：只供 UI / earlier 回看
     -> handoff summary：连续性上下文
     -> 分界后消息：active provider history
```

恢复契约必须分别携带完整 UI `messages` 和已经按最后一个共享分界投影出的 active `modelMessages`。Controller 不得再从全部 UI 消息反向猜测 provider history，否则 Desktop 已压缩的原文会在 CLI 继续时重新进入请求。

CLI/TUI 完成手动或自动压缩时必须写入 Desktop 已识别的 `_compaction` 存储格式，而不是只修改内存中的 provider history 或另造第三种压缩标记。旧原文仍保留在持久化时间线中；后续重复压缩保留历史 handoff，并且只有最后一个分界决定下一次请求。结构化 tool call/result 必须成对留在分界同侧，不得因切分制造孤儿 tool result。

### 5. 计算时机

Runtime 在所有可能改变下一请求的边界重新投影，包括：

- 用户输入、附件或 Goal continuation 加入；
- assistant 输出完成；
- tool call 或 tool result 被保留、截断或替换；
- System Context、模型、provider 或 tools 集合变化；
- 手动或自动压缩完成；
- 每次 provider 调用之前。

实现可以用增量估算提升界面响应，但在发送前必须对**最终请求投影完整重算**。压缩发生后必须重建投影并重新计算，之后才允许发送。

### 5. 窗口与风险语义

`contextWindow` 仍表示 provider/model 的上下文容量。输出预留、安全余量、soft limit 和 hard limit 是 Runtime 策略，不创造新的上下文计数口径：

```text
nextRequestInputTokens + requiredReserveTokens
```

与相应 limit 比较，决定直接发送、先压缩或拒绝超限请求。

Renderer 可以把唯一占用量投影为百分比或安全状态，但不得自行重建另一套 token 预算。用户可见状态必须来自 Runtime 的同一投影与 limit 结果。

## Provider 请求投影 Seam

各 provider 的消息形态不同，但统计必须位于共享的请求投影 seam：

```text
prepare/project provider request
  -> projected messages/system/tools
  -> estimate projected input
  -> compact if required
  -> re-project and re-estimate
  -> encode and send
```

Provider adapter 负责其消息编码差异；共享协调器负责统一指标与阈值。不得在 Renderer、Goal Runner 或单个 provider 分支中复制完整预算算法。

Goal Runner 不维护独立上下文账本。它追加 continuation 并走与普通对话、工具循环相同的 Runtime 投影链。

## Protocol and state migration

跨层权威快照应表达明确语义，例如：

```ts
interface ContextProjection {
  nextRequestInputTokens: number;
  contextWindow: number | null;
  compactionThresholdTokens?: number | null;
  hardLimitTokens?: number | null;
  lastActualInputTokens?: number | null;
}
```

其中只有 `nextRequestInputTokens` 是当前上下文主值。迁移期间若协议需要兼容旧字段，旧字段必须由该值单向派生，并标记废弃；不得保留独立计算路径。

Renderer 会话状态只保存 Runtime 投影。草稿尚未进入 Runtime 时，可在界面短暂显示 `nextRequestInputTokens + estimatedDraftTokens` 的发送预览，但它必须明确是草稿预览，不得回写或替代 Runtime 权威值。Goal Runner 无 Renderer 草稿，直接消费 Runtime 投影。

## Invariants

1. 对同一最终请求，UI 主值与发送前压缩分子相等。
2. 新增且会进入下一请求的 assistant/tool/Goal 内容会提高 `nextRequestInputTokens`。
3. 裁剪、microcompaction 或语义压缩删除的内容不再计入下一请求。
4. 压缩完成后先重投影，再更新 UI 和决定是否发送。
5. `[已被 ADR 56 取代]` 上一请求 usage 与 lifetime `totalTokens` 不得把当前投影钉在历史高水位。
6. 普通对话、工具循环和 Goal Runner 使用同一计算入口。
7. 过期 stream/tick 的快照不得覆盖较新的会话投影。
8. 若压缩后的最终投影仍超过 hard limit，必须在 provider 调用前阻止发送并返回结构化失败。

## Consequences

### Positive

- 用户只看到与“下一次会不会装不下”直接相关的单一口径。
- UI 与自动压缩不再出现一个低、一个高的双重事实。
- Goal 连续 tick、工具循环和普通对话的统计自然一致。
- Provider 实测 usage 与计费账本仍可独立保留，不污染容量判断。

### Trade-offs

- 发送前数值是估算而非 provider 事后精确 usage，必须以“预计”语义对待。
- 为避免 microcompaction 前后统计不同，provider loop 需要先形成最终发送投影再进行预算检查；必要时压缩后再次投影。
- 协议字段迁移需要同步 Runtime、Renderer 状态与测试，不能只替换右下角分子。

## Scope

本次实施仅修改：

- Desktop chat runtime 的请求投影、上下文预算与压缩协调；
- Runtime 到 Renderer 的上下文快照；
- Desktop 右下角上下文展示状态；
- 普通对话、工具循环、Goal Runner 与压缩回归测试。

不修改权限、Evidence、Capability Provider 执行链、计费 ledger，也不触碰代码仓中现有的无关 TUI 和测试改动。

## Runtime Projection 生命周期与安全边界

Desktop 与 CLI/TUI 共享 `@peer-agent/runtime-core` 的 `ContextProjection`、token 投影和压缩决策，不允许宿主分别定义阈值或重新解释“当前上下文”。一次 Runtime 生命周期按以下阶段发布同一结构：

1. `request_preflight`：provider 请求前，用即将实际编码的 messages、tools 和 context window 生成稳定投影；自动压缩只能依据这个阶段的 `compactionPressureTokens` 和共享决策执行。
2. `stream_preview`：provider 正在输出时，以最近稳定投影为基线，仅叠加尚未稳定落入消息历史的 assistant delta；该值用于持续展示下一请求预览，不得触发并发压缩。
3. `tool_result`：工具结果纳入 Runtime 消息后，用实际保留的消息重新投影，替换流式预览而不是与其重复累计。
4. `post_compaction`：压缩 handoff 持久化并成为 active provider history 分界后立即重算，使展示、下一轮 preflight 和恢复值同步回落。
5. `turn_complete`：最终 assistant 内容进入 Runtime 后发布本轮最终投影；`done` 必须携带或对应这份快照，不能由 terminal tool 或 handoff 提前发送裸终态。
6. `restored`：切换会话或进程恢复时，从持久化 active model history 重建投影；null 或失效快照必须被替换或清除，不能沿用旧百分比。

稳定边界与预览边界严格分离：流式阶段可以持续更新 UI，但 provider 正在 streaming 时不能启动压缩。压缩只允许出现在下一次 provider 请求之前，包括用户发送后的首次 preflight，以及 agent/tool loop 将发起下一轮请求之前。这样即使流式预览已越过 soft/hard 线，也只表达“下一请求有压力”；真正执行仍由随后同一套 Runtime preflight 投影决定。

Renderer 只展示 Runtime Projection，并可为未提交草稿生成明确的临时预览；它不得遍历完整 UI 历史重建 token 真值，也不得以 UI 百分比触发压缩。Desktop 主进程与 CLI/TUI 只是宿主适配器：它们负责提供实际 messages/tools、执行摘要与持久化，但阈值、压力等级、触发原因和投影算法均来自共享核心。

## Verification

实施完成需证明：

- 普通对话新增回复后，下一请求投影包含保留的回复；
- 工具循环新增 tool result 后，下一请求投影包含实际保留内容；
- Goal Runner 连续 tick 使用累计会话的下一请求投影，而非仅最后请求 usage；
- microcompaction 和语义压缩后，展示与 preflight 同步回落；
- `totalTokens` 或上一请求 usage 的历史高水位不影响当前投影；
- 聚焦测试、工作区 TypeScript 类型检查与架构治理检查通过。
