# ADR 57：Desktop 与 TUI 统一 Canonical Conversation History Projector

创建时间：2026-07-25
最后更新：2026-11-15（跨 ADR 对齐：登记 [ADR 97](97-reasoning-replay-and-continuation-custody.md) / [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 两条窄例外与 mid-turn `_compaction` 冷重载不变量）
状态：Accepted / Implemented
关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`

## 关联决策

- `knowledge/decisions/52-unified-next-request-context-accounting.md`
- `knowledge/decisions/55-shared-system-context-assembler.md`
- `knowledge/decisions/56-provider-observed-context-accounting.md`
- `knowledge/architecture/19-system-prompt-context-architecture.md`
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`

## 一、问题

ADR 55 已把 Desktop 与 TUI 的 System Context 收敛到共享
`@peer-agent/system-context`，但持久化会话到 active provider history 的解释仍有三套
Implementation：

1. Desktop Renderer `toApiMessages()` 把完整 tool segment 回放为结构化
   `assistant tool_call -> tool result`；
2. Desktop Main `toProjectionMessages()` 在会话恢复时把 tool segment 扁平化为
   assistant 文本；
3. TUI `modelMessagesFromStored()` 把同一轮多个 tool call 合并为一个 assistant
   message，再追加多条 tool result。

在同一持久化会话上，三条路径产生不同的消息数、tool-call/result 配对和
microcompaction 输入。已复现的长会话中：

| 路径 | 投影后消息数 | microcompaction 后历史 token 诊断值 |
|---|---:|---:|
| Desktop 实际发送 | 929 | 167,429 |
| Desktop restored | 22 | 195,660 |
| TUI restored | 448 | 164,559 |

这不是 tokenizer 差异，而是请求在进入 tokenizer 之前已经不是同一个结构。
Desktop restored 因把 tool result 嵌入 assistant 文本，无法获得结构化 tool result
相同的 microcompaction 行为，最终把约 34%–35% 的请求错误投影成 42%。

## 二、根因

### 2.1 持久化消息与 provider message 之间没有唯一 Interface

会话存储保存 UI/审计事实：

```text
content
segments(text / thinking / tool-call)
attachments
_compaction
```

Provider Runtime 消费 active model history。过去没有一个共享 Module 独占这段转换，
Desktop Renderer、Desktop Main 和 TUI 各自理解开放袋存储结构，导致相同事实在不同
宿主中被重组。

### 2.2 Electron 进程分层导致复制

Desktop 实际发送的 Adapter 在 Renderer；restored 重投影在 Main。Main 没有复用
Renderer 的纯转换逻辑，而是复制了一个简化版本。后续 Renderer 支持结构化工具历史时，
Main 的副本没有同步演进。

### 2.3 microcompaction 对结构敏感

`role: tool`、tool-call id 和 tool result 是压缩与连续性判断的结构事实。把同样内容改写成
assistant 文本后，压缩器只能把它当普通历史文本处理。共享 token estimator 或共享
microcompaction 原语无法修复上游消息形状分叉。

### 2.4 缺少跨宿主 golden invariant

既有测试分别证明各自 Adapter “可用”，但没有证明：

> 同一持久化 fixture 经 Desktop send、Desktop restore、TUI restore 后，必须得到同一
> canonical active history。

因此注释中的“对齐”没有成为可执行的 Interface 不变量。

## 三、决策

### 3.1 新增唯一深 Module

在 `@peer-agent/runtime-core` 新增 `CanonicalConversationHistoryProjector`。唯一公开
Interface：

```ts
const CANONICAL_HISTORY_PROJECTOR_VERSION: number;

function projectConversationHistory(
  messages: readonly unknown[],
): {
  messages: readonly CanonicalHistoryMessage[];
  continuityContext?: string;
  continuity?: CanonicalHistoryContinuity;
  compactionBoundaryIndex: number;
  projectorVersion: number;
  historyFingerprint: string;
};
```

该 Module 的 Implementation 独占：

- 最后一个 `_compaction` / view compaction 分界；
- 分界前 UI 原文排除与 continuity summary 提取；
- thinking 排除；
- assistant text 顺序；
- 完整 tool-call/result 的稳定 id 与成对回放；
- 不完整 tool segment 的只读历史事实降级；
- user 文本、文本附件、unsupported 附件和图片内容；
- assistant 历史文本中的 legacy tool marker 净化；
- 空消息和仅展示 system row 的过滤。

Interface 小，Implementation 隐藏开放袋兼容、顺序、配对和附件规则，形成高
Leverage；转换规则与故障定位集中在一个 Module，提升 Locality。

### 3.2 Canonical message 不携带 provider wire 差异

Canonical history 使用 provider-neutral 形态：

```text
toolCalls
toolCallId
content: string | text/image parts | null
```

Desktop OpenAI-style `tool_calls/tool_call_id`、Anthropic content block 等差异只允许在
Provider Encoder Adapter 中 lowering。TUI Runtime 可直接消费结构兼容的 canonical
message。

禁止共享 Projector 输出某个 provider 的最终 wire payload；provider-specific encoding
仍属于 ADR 37/56 定义的 Adapter seam。

### 3.3 三条生产路径必须复用同一 Interface

- Desktop 普通发送 / regenerate：
  Renderer 先持久化 user message 与 assistant placeholder，只提交
  `conversationId + dispatch facts`；Desktop Main 从 conversation-store raw rows 调用
  `projectConversationHistory()`，Renderer 不再拥有 provider history；
- Desktop Main restored：
  直接对 canonical history 做 System Context、tools、microcompaction 与诊断投影；
- Desktop Goal Runner：
  从同一 raw store seam 取得 canonical history，再通过显式 Dispatch Adapter 追加 synthetic
  continuation；
- TUI restore：
  直接把 canonical history 交给 controller，不再独立重建 tool messages。
- Desktop 手动 `/compact`：
  压缩输入使用 canonical messages，持久化切片使用 Projector 暴露的 compaction boundary；
  不再过滤 marker 后把全部 raw rows 扁平化重放。

删除生产路径中的 `toProjectionMessages()` 和 `modelMessagesFromStored()` 独立解释逻辑。
删除 Desktop Main 的 `continuityContextFromMessages()` 私有解析；System Context 所需的
continuity metadata 也从共享 Projector 的 canonical continuity lowering。
Renderer `toApiMessages()` 只允许作为 Quick Chat / legacy 非持久化调用的兼容 Adapter，
不得参与 conversation send。

### 3.4 Request Projection 的完整顺序

```text
Persisted Conversation
  -> Canonical Conversation History Projector
  -> active history + continuity
  -> shared System Context Assembler
  -> Runtime Projection tools
  -> attachments / microcompaction
  -> Provider Encoder Adapter
  -> immutable canonical request
  -> exact count / provider send
```

History Projector 是完整 Request Projection 的一个深 Module，不替代 System Context
Assembler、Runtime Projection 或 Provider Encoder。

### 3.5 token 真值继续服从 ADR 56

Projector 统一“统计和发送的对象”，不把启发式 estimator 升级为上下文真值。

- Provider observed usage 与 provider-aligned exact count 仍是唯一容量证据；
- 没有精确证据时应显示未知/待计量，不得因为跨端投影一致就宣称启发式值精确；
- estimator 只可用于迁移期诊断，且统计与发送必须消费同一 canonical request。

### 3.6 持久化快照必须绑定 projector version

`contextSnapshot` 增加：

```ts
projectorVersion: number
```

Desktop/TUI 只信任与 `CANONICAL_HISTORY_PROJECTOR_VERSION` 相同的快照。版本缺失或不匹配
时必须失效并重新投影；不得继续展示由旧历史解释算法生成的百分比。

版本只表达 request shape 兼容性，不替代 ADR 56 的 fingerprint、content revision、
model key 与 evidence source。

Projector 同时返回由 canonical messages、continuity 与 compaction boundary 生成的稳定
`historyFingerprint`，供后续 exact-count / provider-observed evidence 绑定；仅版本相同但
fingerprint 不同的快照仍不可复用。

### 3.7 已登记边界例外与冷重载不变量（2026-11-15 对齐）

在保证单一持久化历史投影语义前提下，登记以下两项经受控审定的窄例外及冷重载约束：

1. **例外 1（Wire 适配层历史推理降维，[ADR 97](97-reasoning-replay-and-continuation-custody.md) §2）**：仅当 DeepSeek thinking + tools 模式遇到缺失原生 `reasoning_content` 的旧历史轮时，允许在 Provider Wire Encoder adapter 层将该历史 assistant 轮与紧随的已配对 tool result 一起表达为带标签普通历史数据以避开 HTTP 400；该处理严格局限在编码发送层，禁止写回修改 canonical 持久化历史，也不适用于保留完整原生字段的新历史。
2. **例外 2（`project_agent` 有界交互读模型，[ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) §4.3）**：`project_agent`（主 Bot）通过 `readInteractionPage` / `readInteractionContext` 消费有界 SQLite 交互读模型与游标切片（Desktop 窗口接缝见 [ADR 121](121-desktop-session-windowing-contract.md)），而非每次冷扫描整份原始记录；该例外仍不得绕过消息配对、continuity 注入顺序与不可信历史隔离边界。
3. **Mid-turn `_compaction` 冷重载不变量**：无论 `_compaction` marker 在回合进行中（mid-turn）还是重连/多端恢复时落盘，Desktop 与 CLI/TUI 冷重载（cold reload / reattach）均须通过共享 `projectConversationHistory()` 严格从最后一个已提交 `_compaction` 分界裁剪活跃历史并绑定最新 `compactionEpoch`（与 [ADR 56](56-provider-observed-context-accounting.md) 不变式 5 一致），禁止将压缩分界前的原文与新活跃历史混装发送。

## 四、不变量

1. 同一 active persisted history 在 Desktop send、Desktop restore、TUI restore 中产生
   相同 canonical messages。
2. tool call 与 tool result 必须成对位于同一 compaction 分界侧。
3. 完整 tool segment 不得降级为 assistant 文本；只有不完整 legacy segment 可进入只读
   historical record。
4. thinking 和 UI-only system row 不进入 active provider history。
5. 最后一个 compaction 之前的原文只供 UI 回看；continuity 只从最后分界注入。
6. Provider Encoder 只能 lowering canonical shape，不得重新解释持久化 segments。
7. microcompaction、诊断投影与实际发送必须消费同一 canonical history。
8. projector version 改变后，旧 context snapshot 必须失效。
9. Renderer/TUI view 不得自行遍历历史重建另一份 provider history；Desktop conversation
   send 的历史真值来自 Main 持有的 conversation-store raw rows。
10. 没有 provider 精确证据时，canonical 一致性不得被表述为 token 精确性。
11. 相同 canonical history 必须得到相同 `historyFingerprint`；任一 active history、
    continuity 或 compaction boundary 变化都必须改变 fingerprint。

## 五、迁移方案

1. 在 `runtime-core` 落共享 Projector 与代表性 golden fixture；
2. Desktop conversation send 下沉到 Main 从 raw store 投影；Renderer 只提交 dispatch facts；
3. Desktop Main restored 删除扁平化 helper；
4. TUI persistence 删除私有 model history 重建；
5. conversation snapshot 增加 projector version，旧快照失效；
6. 增加跨端 Adapter tests 和架构 gate，阻止重复 Projector 回流。

## 六、验收标准

- 代表性 fixture 覆盖 text/thinking、交错 tool calls、缺失 tool result、文本/图片附件、
  `_compaction` 与 legacy marker；
- Desktop send 与 TUI restore 的 canonical history 深相等；
- Desktop restored 不再产生 `[tool] name/args/result` 扁平历史；
- 已知长会话三条历史投影的消息结构一致；
- 同一 canonical history 的 microcompaction 结果一致；
- 缺失或旧 `projectorVersion` 的快照不被 Desktop/TUI 信任；
- canonical history fingerprint 稳定，且 active request shape 变化时同步变化；
- runtime-core、Desktop、TUI 的 focused tests、typecheck 和 build 通过；
- 代码搜索不再存在生产用 `toProjectionMessages()` /
  `modelMessagesFromStored()`。

## 七、后果

### 正向

- 新增或修复一次历史转换规则即可覆盖 Desktop/TUI send/restore；
- 上下文显示、压缩和真实请求不再因消息形状不同而分叉；
- Provider Adapter 只处理 wire 差异，Interface 更小；
- golden test 直接覆盖最容易漂移的跨宿主 Seam。

### 成本

- 共享 Module 必须兼容存量开放袋消息；
- Desktop transport 字段需要薄 lowering Adapter；
- projector version 升级会使旧快照重新计算；
- Provider exact count 尚未覆盖的渠道仍需按 ADR 56 显示待计量/未知。

## 八、实施结果

2026-07-25 已完成：

- `@peer-agent/runtime-core` 提供 versioned canonical history projector 与稳定 fingerprint；
- Desktop 普通发送、regenerate、restored、Goal Runner、手动 `/compact` 均从 Main 的 raw
  conversation store 进入共享 Projector；
- TUI restore 删除私有历史转换，直接消费 canonical messages；
- context snapshot 写入 `projectorVersion=1`，旧快照在 Desktop/TUI 均失效；
- golden tests 覆盖 compaction、continuity、tool pairing、legacy rows/markers、附件与
  fingerprint；
- 架构 gate 禁止 Renderer conversation send 携带 provider history，并阻止旧 helper 回流。

对问题会话 `1eb90e75-66a4-4b31-8c97-0557eadc8b73` 的只读回放结果：

| 项目 | Desktop | TUI |
|---|---:|---:|
| canonical messages | 929 | 929 |
| microcompaction 后历史 token 诊断值 | 167,429 | 167,429 |
| history fingerprint | `history-v1-3978d506` | `history-v1-3978d506` |

该结果证明历史投影与诊断输入已对齐；最终 UI 是否展示精确百分比仍服从 ADR 56 的
provider evidence 规则。
