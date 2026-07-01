# ADR 42：上下文计数口径分离（显示口径 vs 压缩触发口径）

- 创建时间：2026-06-30
- 最后更新：2026-07-01
- 状态：已采纳并落地（方案 A，实现完成，已验证）
- 关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

## 背景与现象

用户反馈：**「压缩了之后，上下文计数没变。」** 在对话模式手动 `/compact`、以及计划/目标模式（Goal Runner）连续 tick 自动压缩后，界面顶部上下文进度条（`contextTokens / contextWindow`）仍停在高位，没有随压缩回落。

## 根因（已用代码证据钉死）

现有实现把**两种本应分离的口径强行统一成「完整会话量」**，并在多处刻意维持这个高位数字：

1. **三个 agent-loop 喂给 `getContextInfo` 的是完整会话副本，而非实际发送切片。**
   - `chat-runtime/anthropic-agent-loop.mjs:58-100`：`getContextInfo: () => computeContextInfo({ messages: apiMessages, ... })`，且代码注释明确写着「回合结束权威快照与完整会话量同口径，避免回合结束后数值从 ~200k 跳到 ~100k」——即**刻意**不让它回落。
   - `openai-agent-loop.mjs:63`、`gemini-agent-loop.mjs:52` 同样传 `apiMessages`（完整会话），而真正送给 provider 的是压缩后的 `sendMessages` 副本。
   - `apiMessages` 在回合内只增不减（push 工具结果），压缩只作用于发送副本、不回写。

2. **`computeContextBudget` / `computeContextInfo` 的 `contextTokens` 完全由传入 `messages` 估算决定**（`chat-runtime/compaction-coordinator.mjs`：`estimateTokensFromMessages(messages) + estimateToolsTokens(tools)`）。喂完整会话 → 必然得到完整会话量。

3. **目标模式发送链路不按 compaction 边界切片。**
   - `main.mjs:329` `toRuntimeMessages()` 只按 role 过滤，不切片；`runGoalTurn` 每个 tick 把压缩前全量历史重新喂回 `sendMessage`，靠 agent-loop 内部再压一次兜底。
   - 配合 `persistCompaction` 默认 `keptCount<=0` 时保留全部原文供 UI 回看，导致每 tick 重复喂全量 + 重复压缩。

4. **渲染层用 `Math.max(authoritative, live)` 把数字锁在高位。**
   - `ChatSurface.tsx:567` `estimatedContextTokens = Math.max(authoritativeContextTokens, liveContextTokens)`。
   - 主进程 done 下发的 `authoritativeContext` 本身就是完整会话量（见根因 1），即使压缩后本地 `live` 估算变小，`Math.max` 仍取高位的权威值。
   - 渲染层确实有「压缩完成后 `setAuthoritativeContext(null)` 回落到 live」的补偿（`ChatSurface.tsx:828`、`1048`），但目标模式连续 tick 的 done 会**重新下发高位权威值**，把刚清掉的值再次顶上去。

> 一句话：**显示口径被钉死成「完整会话量」是设计性 bug**，压缩的减量发生在发送副本上，从未反映到上报与显示。

## 决策：口径分离（方案 A）

把「显示给用户看的上下文大小」与「决定是否压缩的预算」拆成两个独立数：

### A. 显示口径（界面进度条分子 `contextTokens`）
表示**本回合实际发送给模型的上下文大小**，压缩后应自然变小。取值优先级：

1. **优先：provider 真实 usage 快照**——最后一轮请求的 `inputTokens + cacheReadTokens`。
   - 来源已确认：anthropic adapter 在 `message_start` 即推送 `chat:stream:usage`，带 `inputTokens / cacheReadTokens / cacheWriteTokens`，**每请求覆盖、不累加**，正是「实际发送的 input」。
   - ⚠️ 约束：**不要用 kernel 的累加 usage**（`agent-loop-kernel.mjs` 里 `usage += ...` 是跨轮累加，用于计费 ledger）。显示口径要的是**最后一轮的 input 快照**，不是 lifetime 累加值。
2. **回退：对实际发送切片 `sendMessages` 的估算**（当 provider 未回传可用 usage，如部分 openai/gemini 路径或测试桩）——`estimateTokensFromMessages(sendMessages) + estimateToolsTokens(tools)`，注意是发送切片而非 `apiMessages` 完整会话。

### B. 压缩触发口径（阈值判定）
保持现状语义：对**将要发送的消息**做估算，与 `COMPACTION_CONFIG` 阈值比较，决定 `compactionSuggested / overSoftLimit / overHardLimit`。此口径**不改**，确保触发时机不被显示口径改动带偏。

### C. contextWindow 分母口径
进度条分母继续用**与触发判定同一个 `contextWindow`**（`computeContextBudget` 的 `normalizedWindow`），避免 provider 配置窗口与触发窗口不一致造成百分比错位。分母口径**不变**。

## 受影响函数与文件清单（实现锚点）

| 层 | 文件:符号 | 改动 |
|---|---|---|
| 协调器 | `chat-runtime/compaction-coordinator.mjs` `computeContextBudget` / `computeContextInfo` | 拆出 trigger budget 与 display 两个口径；display 接受「真实 usage 快照」或「发送切片估算」 |
| agent-loop | `anthropic-agent-loop.mjs:58-100` / `openai-agent-loop.mjs:63` / `gemini-agent-loop.mjs:52` | `getContextInfo` 改用发送切片 / 真实 usage，删除「刻意维持完整会话量」逻辑 |
| kernel | `chat-runtime/agent-loop-kernel.mjs` `sendDone` / `getContextInfo` 拼装 | done 下发的 `contextTokens` 反映实际发送上下文；display 取最后一轮 input 快照而非累加 |
| 目标发送链路 | `main.mjs:329 toRuntimeMessages` / `runGoalTurn` | 按 compaction 边界切片（与 `toApiMessages` 同口径）；按需补传 `continuityContext`，消除每 tick 重复喂全量/重复压缩 |
| 渲染层 | `ChatSurface.tsx:567 estimatedContextTokens` | 复核 `Math.max(authoritative, live)`：压缩后 authoritative 用新口径或按压缩世代失效旧值，不再锁高位 |
| 渲染层 | `useChatStreamSubscription.ts:146 onChatStreamDone` | 消费新口径 `contextTokens`；与 `chat:stream:usage` live 口径对齐 |

## 回归风险（子任务 1 须守住）

1. **进度条分子被新口径带偏**：分子改用「实际发送」后，必须确认它仍与分母 `contextWindow` 同窗口，百分比语义一致。
2. **压缩触发阈值被误改**：触发口径（B）必须与显示口径（A）解耦，触发时机不变。否则会出现「显示很低但仍频繁压缩」或反之。
3. **缓存命中率/计费 ledger 显示**：显示口径取 input 快照，不能污染 `runtime-usage-ledger`（ADR 25）的 lifetime 累加。
4. **对话模式既有行为**：手动 `/compact`、emergency 压缩、回合结束自动压缩三条路径回落行为不退化。
5. **目标模式重复压缩竞态**：切片改造后须确认不再每 tick 重复压缩，且 `continuityContext` 不丢失跨 tick 必要上下文。

## 范围边界

- **范围内**：上述上报口径 + 目标模式发送切片 + 渲染读数；补/改单测；全量测试 + typecheck/build 验证。
- **范围外**：不改压缩算法本身（`compactIfNeeded` 摘要生成）、不改权限/工具链路、不动 provider wire 协议。

## 验证标准（done 的定义）

- 对话模式 `/compact` 后，进度条 `contextTokens` 明显回落。
- 目标模式连续 tick 自动压缩后，数字回落且不再每 tick 反弹到高位。
- 压缩触发阈值语义不变；对话模式既有压缩行为无回归。
- 全量单测 + typecheck/build 通过。

## 实现落地结果（2026-07-01 完成）

> 以下为实际改法与验证证据，覆盖上文「实现锚点」的最终落点（部分行号/API 与规划阶段略有出入，以此节为准）。

### 主进程 / 运行时

- **`compaction-coordinator.mjs`**
  - 新增 `contextTokensFromUsageSnapshot(snapshot)` = `inputTokens + cacheReadTokens`（不含 output/cacheWrite；无有效值返回 `null`）。
  - `computeContextInfo({ messages, contextWindow, tools, displayMessages, usageSnapshot })`：
    - `contextTokens` 走**显示口径**回退链：`usageSnapshot` → `displayMessages` 估算 → 完整会话 `messages` 估算。
    - `triggerTokens` / `compactionSuggested` 走**触发口径**（完整会话 budget，`overSoftLimit`），与显示口径解耦。
- **`agent-loop-kernel.mjs`**
  - 新增 `lastTurnUsage`（覆盖式，仅当 `inputTokens>0` 或 `cacheReadTokens>0` 才更新，避免无计费轮次清掉有效快照）。
  - `sendDone()` 改为 `getContextInfo({ usageSnapshot: lastTurnUsage })`；done 事件下发的 `contextTokens` 因此变为显示口径。
  - 保留：`usage` 仍是 lifetime 累加（计费 ledger，ADR 25），未被显示口径污染。
- **`anthropic-agent-loop.mjs` / `openai-agent-loop.mjs` / `gemini-agent-loop.mjs`**
  - `getContextInfo` 改为接收 `{ usageSnapshot }`，并传 `displayMessages`（各自新增 `lastSentMessages`，在 `sendMessages` 计算处记录）+ `usageSnapshot`。
  - anthropic 的 `apiMessages` 不含 system，`displayMessages` 拼 `[{system}, ...lastSentMessages]`；openai/gemini 的 `apiMessages` 已含 system，直接用 `lastSentMessages`。
- **`main.mjs`**
  - `toRuntimeMessages` 新增按最后一条 `_compaction` 边界切片（`lastCompactionIndex` + `slice`，丢弃压缩点前原文、保留其后尾部），与对话模式 `renderer apiMessageMapping.ts` 同口径。
  - `runGoalTurn` 计算 `goalContinuityContext = continuityContextFromMessages(conversation.messages)`，作为 `continuityContext` 传入 `sendMessage`，把压缩摘要 handoff 经 system 注入，避免切片后历史丢失。

### 渲染层

- **`useConversationStreamRouter.ts`**：`onChatCompaction` 完成分支重载 messages 后新增 `setState(cid, { authoritativeContext: null })`，使旧权威快照失效——这正是规划阶段缺失、导致 `Math.max` 锁高的补偿动作。下个回合 `done` 会带来新口径权威值。
- **`ChatSurface.tsx`**：更新 `estimatedContextTokens = Math.max(authoritative, live)` 处注释为本 ADR 语义（显示口径 ≠ 触发口径，`Math.max` 仅用于消除流式→结束瞬时抖动）。`tokenEstimate.ts` 的 live 估算本已按 `_compaction` 切片，无需改。

### 单测

- `compaction-coordinator.test.mjs` 新增 `describe('ADR 42：显示口径与压缩触发口径分离')` 5 用例并全绿：usage 折算取 input+cacheRead、无快照回退 null、显示口径优先 usage 且 < triggerTokens、无 usage 用 displayMessages 估算、触发判定不被小显示口径压制。文件 21/21 通过；原「方案 A：完整会话量口径不变量」块因走完整会话回退口径而兼容未破。

### 验证结论

- `tsc -p tsconfig.json` 退出码 0，覆盖全部 TS 改动。
- `compaction-coordinator.test.mjs` 21/21、`agent-loop-kernel.test.mjs` 全绿。
- 全量单测 488 中 5 个失败**与本次无关**：均为纯 `node --test` 环境下 `SyntaxError: electron 不提供 webContents 具名导出` 的预先存在环境失败，分布于未改动的 `projected-tool-executor` / `request-user-input-signal` / `tool-orchestrator` / `llm-chat-service` 测试文件（这些测试需 electron 运行时或特定 mock）。
- 放弃的旧不变量：`bar ≡ trigger`（显示口径 = 触发口径）被有意放弃，改为口径分离。
