# 自动上下文压缩与 Agent Run 续接技术方案

创建时间：2026-07-04
最后更新：2026-07-04
状态：技术方案 / Phase 1、Phase 2 核心语义已在 `peer_agent` 落地
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）
关联文档：

- `knowledge/decisions/17-local-context-compaction.md`
- `knowledge/decisions/21-pending-task-resume.md`
- `knowledge/decisions/22-stream-reattach-on-reload.md`
- `knowledge/decisions/26-agent-loop-termination.md`
- `knowledge/decisions/42-context-display-vs-trigger-accounting.md`
- `knowledge/decisions/43-conversation-runtime-state-bucketing.md`
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主压缩持久化共享与算法分叉治理
- `knowledge/architecture/23-compaction-path-root-governance.md` — 压缩路径根治理(入口收敛、口径下沉、CLI 一致性)

本文定义 Peer Agent 在自动上下文压缩场景下的发送、排队、运行续接和 UI 状态协议。

核心判断：

```text
自动压缩是 Agent Runtime 的透明续航机制，不是用户交互边界。

用户消息可以先落库和展示，但它对应的模型请求必须先进入待发送队列；
如果 preflight 判定需要压缩，则先压缩旧上下文，再携带最新用户原文自动发送。
```

换句话说，应该 hold 的不是 UI 上的消息，而是这条消息对应的 provider request。

## 一、问题背景

长会话或长流程中会出现两类压缩触发点：

1. **用户刚发送消息时触发压缩**
   - 用户输入一句话后，Runtime 发现 `历史上下文 + 当前用户消息 + 回复预留` 超过阈值。
   - 如果直接发送，可能 prompt too long，或者把过大的上下文送给 provider。
   - 正确行为是：当前用户消息先落库、排队，压缩旧上下文后再自动发送。

2. **Agent 长流程中自动触发压缩**
   - Agent 已经在执行多轮 model/tool loop，中间不断产生工具结果和 evidence。
   - 下一次 provider request 前发现上下文超限。
   - 正确行为是：checkpoint 当前 run，压缩可压缩历史，然后继续同一个 run。
   - 压缩完成不能被当成任务结束，也不能要求用户手动说“继续”。

当前已有 ADR 分别处理了本地压缩、任务续传、流式重连、终止语义、显示口径、会话状态分桶。
本方案补齐的是这些能力之间的端到端 Runtime 协议。

## 二、代码核实后的现状

本节基于 2026-07-04 对 `peer_agent` 当前代码的核实。结论：现有实现已经具备“压缩期间不断流、按会话显示压缩态、压缩后继续 provider loop”的一部分能力，但**不满足“最新用户消息保持原文”的关键语义**。

### 2.1 已具备的能力

1. **发送入口已经先持久化用户消息和 assistant placeholder**
   - `apps/desktop/renderer/src/chat/components/ChatSurface.tsx`
   - `submitMessage()` 先把 user message 和空 assistant message append 到 conversation，再生成 `streamId`，登记 `streamId -> conversationId`，最后调用 `chatSend`。
   - 因此用户体验上不是“压缩前消息不可见”，而是“消息已发送，provider request 可能被压缩 preflight 延后”。

2. **provider request 前已有统一 preflight compaction**
   - `apps/desktop/electron/main/chat-runtime/openai-agent-loop.mjs`
   - `apps/desktop/electron/main/chat-runtime/anthropic-agent-loop.mjs`
   - `apps/desktop/electron/main/chat-runtime/gemini-agent-loop.mjs`
   - 三个 agent loop 都在每轮 provider request 前调用 `runCompactionCheck()`，压缩后用返回的 `compaction.messages` 继续本轮 loop。

3. **prompt-too-long 已有 emergency compact and retry**
   - `runCompactionCheck({ emergency: true, force: true })` 已在 provider 返回 `context_length_exceeded` / `prompt_too_long` / `413` 等情况后触发。
   - 成功后 `continue` 同一个 loop，失败才发 error。

4. **压缩态已按 conversationId 管理**
   - `apps/desktop/electron/main/chat-runtime/compaction-registry.mjs` 以 `conversationId` 记录正在压缩的 `streamId` 和进度。
   - renderer `useConversationStreamRouter.ts` 通过 `streamId -> conversationId` 把 `chat:compaction` 事件落到对应会话桶。
   - 切会话时 `ChatSurface` 会调用 `chat:compaction:get` 恢复该会话的压缩横幅。

5. **流式续接和终态保留已具备**
   - `llm-chat-service.mjs` 的 `activeStreams` 累积正文、thinking、segments，并支持 `chat:stream:reattach`。
   - 终态记录会保留一段时间，切回已结束后台轮次也能回放完整快照。

6. **Goal Runner 已按 compaction boundary 切历史**
   - `main.mjs toRuntimeMessages()` 按最后一条 `_compaction` 边界切掉压缩点前原文。
   - `runGoalTurn()` 把压缩摘要经 `continuityContext` 注入 system context，避免每个 tick 重复喂全量历史。

### 2.2 当前关键差距

#### 差距 A：当前轮 user message 会被真·全量压缩吞进 summary

这是最高优先级问题。

当前 `context-compactor.mjs splitForCompaction()` 明确采用“真·全量压缩”：

```text
旧消息全部摘要，连当前轮原文也不保留。
cutIndex = convMsgs.length
keep = []
old = 全部非 system 消息
```

测试也明确断言：

```text
flushes the current turn too — nothing original is kept
```

这意味着当用户刚发送一句话并触发自动压缩时，最终 provider request 可能是：

```text
system
user: [上下文交接 - 共压缩 N 条消息] ... summary ...
```

而不是：

```text
system
runtime.continuity / handoff summary
user: 当前用户原文
```

这和本方案核心不变式冲突。正确语义应改为：

```text
preflight_send:
  old = 当前用户消息之前的历史
  keep = 当前用户消息

agent_loop_turn:
  old = 已闭合的历史
  keep = 当前未完成语义边界所需的 raw tail
```

#### 差距 B：没有显式 runId / dispatchStatus

当前主链路以 `streamId` 承载一次运行：

- renderer 创建 `streamId`；
- main `activeStreams` 记录运行态；
- compaction event 和 stream event 都依赖 `streamId` 路由。

这足以支撑当前 UI 续接，但缺少两个更稳定的 Runtime 概念：

- `runId`：表示同一个 agent run，可跨 compaction、provider retry、stream reattach 追踪。
- `UserMessageDispatchStatus`：区分“用户消息已落库”和“已被模型消费”。

因此当前可以做到“看起来续上”，但难以精确回答：

- 哪条 user message 正在等待 compaction？
- 压缩完成后哪条 raw message 被 dispatch？
- crash 后哪些消息已落库但未被模型消费？

#### 差距 C：renderer queue 只覆盖“忙时再输入”，不覆盖“本轮 preflight hold”

`ChatSurface.handleSend()` 在 `isStreaming || isCompacting` 时会把新输入放入 composer queue，空闲后自动出队。

但本轮消息的 preflight hold 发生在 `chatSend` 之后、provider request 之前：

```text
submitMessage
  -> append user + assistant placeholder
  -> set isStreaming true
  -> chatSend
  -> agent loop preflight
  -> runCompactionCheck
  -> provider request
```

也就是说，当前用户消息没有独立的 `blocked_by_compaction` 状态，只能通过整轮 `isStreaming/isCompacting` 间接表达。

#### 差距 D：压缩 persistence 保留 pending assistant，但不保留 pending user raw

`persistCompactionToConversation({ preservePendingAssistant: true })` 会通过 `conversation-compaction-persistence.mjs` 保留末尾 assistant placeholder，避免压缩后后续 delta 找不到落点。

但 provider request 的消息切分仍由 `compactIfNeeded()` 的 `keep` 决定；目前 `keep=0`，所以 pending user raw 不会进入压缩后的 provider request。

## 三、修订后的落地原则

基于代码现状，本方案的落地不应从零引入完整 Job 系统，而应先修正一个核心语义，再分层补强：

```text
第一优先级：让 preflight 自动压缩排除最新用户消息，并把它原文作为 keep tail 发给 provider。
第二优先级：让 agent loop 自动压缩只发生在安全边界，并保留必要 raw tail。
第三优先级：再引入 runId / dispatchStatus / compaction job checkpoint，解决崩溃恢复和可观测性。
```

## 四、目标与非目标

### 4.1 目标

1. 用户发送消息后，如果需要压缩，消息不丢、不改写、不乱序。
2. 最新用户消息保持原文参与模型请求，不被吞进 compaction summary。
3. 自动压缩完成后，Runtime 自动恢复并继续同一个 agent run。
4. `chat:stream:done` 只表示模型产生终态回复，不被 compaction completion 误用。
5. 工具调用结构保持合法，不切断 assistant tool call 和 tool result 配对。
6. 压缩结果持久化，崩溃或重载后可以恢复到一致状态。
7. UI 能表达“排队中 / 整理上下文 / 续接中 / 流式生成中”，但不需要用户手动续上。

### 4.2 非目标

本方案不做：

- 长期记忆系统。
- 向量检索系统。
- 改写 compaction 摘要算法本身。
- 改 provider wire protocol。
- 允许压缩绕过权限、工具或 Evidence 链路。
- 把用户最新输入自动学习进长期偏好。

## 五、核心不变式

1. **最新用户消息不被压缩**
   - 当前触发发送的 user message 必须以 raw content 进入最终 provider request。
   - compaction 可以把它作为摘要关注点，但不能把它纳入 summary source range。

2. **压缩不是终态**
   - `compacting_context` / `resuming_after_compaction` 是运行中间态。
   - 不允许因为压缩完成而发 `chat:stream:done`。

3. **同一个任务继续使用同一个 runId**
   - 自动压缩前后的 agent run 身份不变。
   - stream 可以重建或延迟创建，但 run continuity 必须保持。

4. **发送前必须 preflight**
   - 每次 provider request 前估算实际将发送的上下文。
   - 超过 soft limit 可自动压缩，超过 hard limit 必须压缩或失败，不能盲发。

5. **工具结构必须成对保留**
   - 不能让保留窗口从 tool result 开始。
   - 不能保留 assistant tool call 却丢失对应 tool result。
   - 如果无法成对保留，必须整体转成 handoff block 或 artifact ref。

6. **压缩结果先持久化，后 dispatch**
   - compaction snapshot / continuity context 写入成功后，才能发下一次 provider request。
   - 避免压缩成功但重启后又加载未压缩历史。

7. **会话内串行写，跨会话可并行**
   - 同一 `conversationId` 内 user messages、compaction、model stream 必须按序落库。
   - 不同 conversation 可以独立运行。

## 六、运行时状态模型

### 6.1 Conversation Run 状态

建议引入或显式建模 `AgentRun`：

```ts
type AgentRunStatus =
  | 'queued'
  | 'preflighting'
  | 'compacting_context'
  | 'resuming_after_compaction'
  | 'dispatching_provider'
  | 'streaming_model'
  | 'executing_tool'
  | 'waiting_permission'
  | 'requires_user_input'
  | 'completed'
  | 'failed'
  | 'cancelled';

type AgentRun = {
  runId: string;
  conversationId: string;
  workspacePath: string;
  status: AgentRunStatus;
  triggerMessageIds: string[];
  streamId?: string;
  contextEpochId?: string;
  compactionEpochId?: string;
  createdAt: string;
  updatedAt: string;
};
```

关键语义：

- `completed` 只能由模型终态回复驱动，对应 ADR 26。
- `failed` 对应 provider、tool、permission、runtime 或 compaction 不可恢复错误。
- `compacting_context` 和 `resuming_after_compaction` 不会暴露成任务终止。
- `requires_user_input` 只用于真正需要用户决策的情况，例如权限确认、歧义选择、压缩失败后需要用户选择降级策略。

### 6.2 User Message 发送状态

用户消息需要从“UI 已出现”与“模型已消费”之间拆出状态：

```ts
type UserMessageDispatchStatus =
  | 'persisted'
  | 'queued_for_model'
  | 'blocked_by_compaction'
  | 'dispatching'
  | 'consumed_by_model'
  | 'failed';

type UserMessageRecord = {
  id: string;
  conversationId: string;
  role: 'user';
  content: string;
  sequence: number;
  dispatchStatus: UserMessageDispatchStatus;
  runId?: string;
  createdAt: string;
  updatedAt: string;
};
```

用户点击发送后：

- UI 可以立刻展示该消息。
- 数据库必须立刻持久化。
- 但 provider request 要等 preflight 和可能的 compaction 完成后才能发出。

### 6.3 Compaction Job 状态

```ts
type CompactionJobStatus =
  | 'pending'
  | 'running'
  | 'persisting'
  | 'completed'
  | 'failed';

type CompactionJob = {
  compactionJobId: string;
  conversationId: string;
  runId: string;
  reason: 'preflight_send' | 'agent_loop_turn' | 'manual' | 'emergency';
  status: CompactionJobStatus;
  sourceMessageRange: {
    fromSequence: number;
    toSequence: number;
  };
  excludedMessageIds: string[];
  focusMessageIds: string[];
  tokenBefore?: number;
  tokenAfter?: number;
  snapshotId?: string;
  errorCode?: string;
  createdAt: string;
  updatedAt: string;
};
```

`excludedMessageIds` 至少包含当前待发送 user message。多条连续 pending user messages 也必须保持 raw。

## 七、数据持久化契约

### 7.1 Compaction Snapshot

压缩完成后应形成可重放的 snapshot：

```ts
type CompactionSnapshot = {
  snapshotId: string;
  conversationId: string;
  runId: string;
  reason: CompactionJob['reason'];
  sourceMessageIds: string[];
  keptTailMessageIds: string[];
  excludedRawMessageIds: string[];
  continuityContext: {
    title: string;
    userGoal: string;
    recentExplicitRequests: string[];
    completedWork: string[];
    currentState: string[];
    pendingWork: string[];
    keyEvidenceRefs: Array<{
      kind: 'artifact' | 'file' | 'command' | 'tool_result';
      ref: string;
      note: string;
    }>;
    suggestedRetrieval: string[];
    nextStep: string[];
  };
  tokenBefore: number;
  tokenAfter: number;
  createdAt: string;
};
```

Snapshot 写入成功后，conversation history 中应出现明确的 compaction boundary。
已有实现如果使用 `_compaction` 标记或 `runtime.continuity` Context Source，应继续沿用同一口径。

### 7.2 Outbound Queue

同一 conversation 内建议维护一个运行时队列：

```ts
type OutboundQueueItem =
  | {
      kind: 'user_message';
      conversationId: string;
      runId: string;
      messageId: string;
      sequence: number;
    }
  | {
      kind: 'agent_loop_continue';
      conversationId: string;
      runId: string;
      afterToolResultId?: string;
    };
```

队列只负责排序，不负责长期记忆。进程重启后的跨进程恢复仍由 pending-task / stream reattach 等既有机制各自承担，但新 run checkpoint 可以复用同一思想。

## 八、关键流程

### 8.1 用户发送消息触发自动压缩

```mermaid
sequenceDiagram
  participant UI as Renderer
  participant Main as Main Runtime
  participant Store as Conversation Store
  participant Compact as Compaction Coordinator
  participant Loop as Agent Loop
  participant Model as Provider

  UI->>Main: chat:send(userMessage)
  Main->>Store: persist user message(status=persisted)
  Main->>Store: create run(status=queued)
  Main->>Main: enqueue user_message
  Main->>UI: message persisted / queued
  Main->>Main: preflight context budget
  alt compaction needed
    Main->>Store: mark message blocked_by_compaction
    Main->>Compact: compact previous context(exclude current user)
    Compact->>Store: persist compaction snapshot + boundary
    Compact->>UI: chat:compaction:done(runId)
    Main->>Store: mark run resuming_after_compaction
  end
  Main->>Loop: dispatch same run with raw user message
  Loop->>Model: provider request
  Model-->>Loop: stream delta / tool call / final
  Loop-->>UI: chat:stream:* events
```

核心规则：

- 当前 user message 先落库，再 preflight。
- `compact previous context` 的 source range 截止到当前 user message 之前。
- 当前 user message 可以作为 `focusMessageIds` 帮助摘要保留相关事实，但必须出现在 `excludedMessageIds`。
- 压缩完成后无需用户操作，Runtime 自动 dispatch。

### 8.2 Agent 长流程中自动压缩并续跑

Agent loop 中每次准备发下一轮 provider request 前执行 preflight：

```text
model response
  -> maybe tool call
  -> execute tool
  -> persist tool result / evidence
  -> preflight next provider request
  -> if compaction needed:
       checkpoint run state
       compact previous safe range
       persist compaction snapshot
       rebuild request context
  -> continue same runId
```

允许压缩的安全边界：

- 一次完整 model response 已结束后。
- 一个 tool call 的 tool result 已落库后。
- 下一次 provider request 尚未发出前。
- permission 从 `waiting_permission` 恢复后、真正继续 provider 前。

禁止压缩的边界：

- provider 正在 streaming delta 时。
- assistant tool call 已产生但对应 tool result 尚未落库时。
- 正在执行不可中断工具且没有 evidence checkpoint 时。
- conversation write lock 不归当前 run 时。

### 8.3 Emergency compact and retry

如果 provider 返回 `context_length_exceeded`、`prompt_too_long`、`413` 等错误：

```text
provider error
  -> classify as prompt-too-long
  -> mark run compacting_context(reason=emergency)
  -> force compact(targetRatio lower)
  -> persist snapshot
  -> retry same provider request once
```

约束：

- emergency retry 必须有次数上限，建议同一 run 同一 provider request 最多 1 到 2 次。
- 如果 emergency compact 失败，发 `chat:stream:error(context_compaction_failed)`，不得伪装成 `done`。
- 如果压缩后仍超过 hard limit，应失败并提示用户缩小任务范围或手动清理上下文。

## 九、上下文组装规则

最终发给 provider 的上下文应由以下部分组装：

```text
System Context
  + project instructions
  + runtime mode / provider guidance
  + runtime.continuity(compaction snapshot)
  + recent valid message tail
  + pending raw user messages
  + tool schemas
```

其中：

- compaction summary 进入 `runtime.continuity` 或等价系统上下文来源。
- recent tail 保留最后一段结构合法的消息窗口。
- pending raw user messages 按 sequence 原文追加。
- 大工具结果只通过 artifact ref、preview、suggested retrieval 进入上下文。
- provider usage 显示口径继续遵守 ADR 42：显示实际发送切片，触发口径独立计算。

### 9.1 多条 pending user messages

如果用户在压缩期间继续输入：

```text
user A -> triggers compaction
user B -> queued while compaction running
user C -> queued while compaction running
```

处理策略：

- A、B、C 全部原文落库，按 sequence 排队。
- 当前 compaction source range 仍然排除 A/B/C。
- compaction 完成后可以选择：
  - 合并为一次 provider request，包含 A/B/C 三条 raw user messages。
  - 或只发送 A，B/C 继续排队，等当前 run 结束后处理。

默认建议：同一 conversation 内单 active run。A 正在驱动 run 时，B/C 作为后续 user messages 排队，避免用户连续输入与 agent loop 并发改写同一上下文。

## 十、事件与 UI 协议

### 10.1 Runtime events

建议保持现有 `chat:stream:*` 主干，并为 compaction 明确事件：

```ts
type ChatCompactionEvent =
  | {
      type: 'chat:compaction:start';
      conversationId: string;
      runId: string;
      reason: CompactionJob['reason'];
    }
  | {
      type: 'chat:compaction:progress';
      conversationId: string;
      runId: string;
      percent?: number;
      phase: 'summarizing' | 'persisting' | 'rebuilding_context';
    }
  | {
      type: 'chat:compaction:done';
      conversationId: string;
      runId: string;
      snapshotId: string;
      tokenBefore?: number;
      tokenAfter?: number;
    }
  | {
      type: 'chat:compaction:error';
      conversationId: string;
      runId: string;
      errorCode: string;
      recoverable: boolean;
    };
```

### 10.2 UI 展示语义

UI 状态应表达：

- `queued_for_model`：已发送，等待模型处理。
- `blocked_by_compaction`：正在整理上下文。
- `resuming_after_compaction`：正在续接任务。
- `streaming_model`：模型正在回复。
- `waiting_permission`：等待用户授权。
- `failed`：失败，需要用户处理。

不应该出现：

- 压缩完成后消息停在“已发送但无响应”，需要用户手动继续。
- 压缩完成被渲染成 assistant 的最终回答。
- 后台会话压缩事件写入当前前台会话桶。

这部分应复用 ADR 43 的 conversationId 分桶 store：所有 compaction 和 stream events 都必须按 `conversationId/runId/streamId` 路由到对应桶。

## 十一、并发与锁

### 11.1 Conversation Write Lock

同一 conversation 内建议有一个写锁：

```ts
type ConversationRuntimeLock = {
  conversationId: string;
  ownerRunId: string;
  kind: 'model_stream' | 'compaction' | 'tool_execution';
  acquiredAt: string;
};
```

规则：

- provider stream、compaction、tool result 落库都必须持有同一 conversation 的写锁。
- 同一 run 内可以从 `tool_execution` 切到 `compaction` 再切回 `model_stream`。
- 不同 run 争用同一 conversation 时，后来的 run 排队。
- 用户 abort 当前 run 时，释放锁并把队列中后续消息重新调度或标记等待。

### 11.2 Compaction Lock

Compaction lock 是 conversation-scoped：

- 同一 conversation 同一时间只能有一个 compaction job。
- 如果 compaction 正在运行，又有新的 preflight 发现需要压缩，不再开第二个 job。
- 新的 pending user message 只追加到 excluded/focus 列表或队列中。

## 十二、失败恢复

### 12.1 压缩失败

失败分层处理：

1. LLM summary 失败：走 structural fallback summary。
2. structural fallback 仍超限：降低 target ratio，减少 recent tail。
3. emergency 仍失败：终止 run，发 `chat:stream:error(context_compaction_failed)`。

禁止行为：

- 不得静默丢弃历史后继续发送。
- 不得把 pending user message 放进 summary 后省略原文。
- 不得把压缩失败标记为 `done`。

### 12.2 进程重启或崩溃

启动恢复时检查：

- `CompactionJob.status in ('pending', 'running', 'persisting')`
- `AgentRun.status in ('queued', 'preflighting', 'compacting_context', 'resuming_after_compaction', 'dispatching_provider')`
- user message `dispatchStatus in ('queued_for_model', 'blocked_by_compaction', 'dispatching')`

恢复策略：

- 如果 compaction snapshot 已写入但 run 未 dispatch：从 snapshot 恢复并自动 dispatch。
- 如果 compaction job 未完成：标记旧 job failed，重新 preflight。
- 如果 provider stream 已创建：优先走 ADR 22 stream reattach。
- 如果进程重启导致 stream 不存在：根据 run checkpoint 标记为 interrupted，并可转入 pending-task 类恢复提示或自动续跑策略。

### 12.3 用户取消

用户取消时：

- 当前 run 标记 `cancelled`。
- 当前 compaction job 尽量 abort；如果不能 abort，完成后丢弃结果或标记 orphaned。
- pending user messages 默认保留在队列，可让用户选择继续发送或取消。

## 十三、统一投影与跨宿主执行基线

截至本轮治理，自动压缩不再由 Desktop、CLI/TUI 或 Renderer 各自计算。宿主无关主链路固定为：

```text
active provider history + system context + projected tools
  -> runtime-core ContextProjection
    -> request_preflight compaction decision
      -> optional compaction + durable handoff
        -> post_compaction projection
          -> provider request
            -> stream_preview projections
              -> tool_result / turn_complete stable projection
```

### 13.1 唯一事实源

`@peer-agent/runtime-core` 统一拥有：

- 消息、CJK、图片、tool call/result 和工具 schema 的 token 投影；
- soft、hard、overflow 阈值与 summary headroom 判断；
- `currentInputTokens`、`nextRequestInputTokens`、`previewInputTokens`、`compactionPressureTokens`；
- `request_preflight`、`stream_preview`、`tool_result`、`post_compaction`、`turn_complete`、`restored` 六阶段生命周期；
- 压力等级、压缩原因和是否应执行的决策。

Desktop 和 CLI/TUI 负责把各自实际发送的 provider messages/tools 投入共享核心，并负责执行摘要、写入共享 `_compaction` handoff 与恢复；不得在宿主中复制阈值或上下文算法。Renderer 不参与真值计算，只展示 Runtime Projection；未提交草稿只能作为明确的本地预览叠加，不能回写 Runtime。

### 13.2 流式进度与压缩安全边界

进行中的 provider 输出必须持续发布 `stream_preview`，所以占用进度会随着 assistant delta 增长。预览以最近稳定投影为基线，只计算尚未稳定写入 active history 的 delta；当 assistant 或 tool result 落入消息后，由稳定阶段全量重算并替换预览，禁止 seed、history 和 provider usage 多路累加。

流式预览越线不直接执行压缩。允许执行自动压缩的唯一时机是下一次 provider 请求前的 `request_preflight`：

- 用户消息已入队，首次 provider dispatch 之前；
- assistant 发起工具调用，工具结果稳定写入后，下一轮 provider dispatch 之前；
- Goal Runner continuation 或其他 agent-loop continuation 发起下一请求之前；
- overflow/retry 路径重新 dispatch provider 之前。

provider 正在 streaming、工具正在执行但结果尚未稳定写入、handoff 尚未持久化时都不是安全边界。压缩完成后必须先写入共享 handoff，再发布 `post_compaction`，然后才能续发请求。压缩事件不能伪装成 `chat:stream:done`；terminal tool 和 Goal handoff 也不能抢发缺少最终投影的裸 done。

### 13.3 快照、切换与恢复

每个稳定投影携带单调 revision，并在消息落盘、压缩落盘和会话切换时遵循同一失效顺序：先使旧快照失效，再基于当前 active model history 发布新值。会话恢复使用 `restored`，不能从完整 UI timeline 反推 provider history；最后一个 `_compaction` handoff 仍是唯一 active history 分界。未知值保持 unknown，不渲染伪造百分比。

### 13.4 落地状态（2026-07-24 四次代码核实，本章主体已实现）

- 已落地：`runtime-core` 六阶段契约与共享估算/阈值（hard 线 0.92 单值）；Desktop 四个 provider loop 的 kernel 持有 per-turn 生命周期，`request_preflight` / `post_compaction` / `tool_result` / `turn_complete` 经 `chat:context:projection` IPC 发布，renderer 以 streamId+revision 序合并；`stream_preview` 由展示侧叠加（Desktop `streamPreviewTokens`、TUI delta flush 重算）；`restored` 经 `chat:context:restored` IPC 按完整成分重算并回写共享快照，renderer 对 `source ≠ 当前宿主` 快照不再采信——**六阶段均有发布者**；TUI 具备 loop 中途 preflight 与 PTL emergency（分类同源 runtime-core `isPromptTooLongError`）；`_compaction` marker 经 `@peer-agent/protocol buildCompactionMarker()` 两端同构。
- 已知偏离：TUI 中途压缩的 marker 在 turn 结束时持久化（非压缩即时，偏离 13.2 「handoff 先持久化再续发」，turn 中 crash 丢失该次记录）；切模型后到下轮稳定投影前分母仍旧窗口。
- 进度台账与下一批优先级见 `knowledge/architecture/23-compaction-path-root-governance.md` 第八节。

## 十四、实现分阶段

### Phase 1：修正 compaction split，保留最新用户原文

目标：在不重构发送链路的前提下，先修正“用户发消息后发现需要压缩”的核心语义。

改动：

- 为 `compactIfNeeded()` / `splitForCompaction()` 增加可选策略，例如：
  - `preserveLatestUserMessage: true`
  - `preserveCurrentTurn: true`
  - 或更明确的 `excludeMessageIds` / `preserveTailPredicate`
- `chat` / `goal` 的自动 preflight compact 默认开启“保留最新 user raw”。
- 手动 `/compact` 可以继续保留“真·全量压缩”语义，因为用户显式要求整理上下文，且没有正在等待发送的新 user message。
- emergency compact 默认先保留最新 user raw；如果保留后仍超过 hard/window，再进入二级降级，并明确记录 fallback reason。
- 修改 `context-compactor.test.mjs` 中“flushes the current turn too”这类断言：手动 force 可全量；preflight send 不可吞最新 user。

验证：

- 构造超阈值历史，发送一句新消息。
- 看到 UI 先显示用户消息和“整理上下文”，随后自动出现模型回复。
- provider request 中包含最新用户原文。
- compaction summary 不包含当前用户消息作为被压缩正文。

### Phase 2：把现有自动续接语义显式化

目标：现有 agent loop 已能在 `runCompactionCheck()` 后继续同一 loop。本阶段不是重写，而是补齐状态和测试，保证“不把 compaction 当终态”。

改动：

- 保持 agent loop 每次 provider request 前走 `runCompactionCheck()` 的现有路径。
- 增加测试覆盖：compaction done 不触发 `chat:stream:done`；done 只在模型终态回复后发出。
- compaction event 继续使用现有 `chat:compaction`，但文档化 stage 语义：
  - `start/progress/done/idle` 是中间维护事件；
  - `chat:stream:done/error/aborted` 才是 stream terminal。
- run 状态可先在 renderer bucket 中补充表达，不必第一步持久化。
- 压缩前 checkpoint run state。
- 压缩完成后继续同一 runId。
- compaction event 不触发 stream terminal。

验证：

- 构造多轮 tool call 任务，中途触发自动压缩。
- UI 显示整理上下文后继续执行工具或继续模型回复。
- `chat:stream:done` 只在最终 assistant response 后出现。
- runId 不变。

### Phase 3：补强 dispatch/run 可观测性

目标：在语义正确后，再解决 crash recovery、消息消费状态和运维可观测性。

改动：

- 引入轻量 `AgentRun` 或先把 `runId` 作为 `streamRecord` 的稳定字段。
- 为 user message 增加可选 dispatch metadata：
  - `queued_for_model`
  - `blocked_by_compaction`
  - `dispatching`
  - `consumed_by_model`
- 持久化 `AgentRun` / `CompactionJob` 必要 checkpoint。
- 启动时恢复 incomplete run 和 queued user messages。
- compaction events 全部按 conversation bucket 路由。
- 多 pending user messages 串行策略落地。

验证：

- 压缩中重载 renderer，UI 重新挂载后能看到正确会话状态。
- 压缩完成后自动继续，不串到前台其他会话。
- A 会话压缩时切到 B，会话状态互不污染。

## 十四、测试矩阵

| 场景 | 期望 |
| --- | --- |
| 发送消息触发 preflight compact | 消息先展示，模型请求延迟，压缩后自动发送 |
| pending user message 被排除在 source range 外 | summary 不吞当前用户输入，provider request 有原文 |
| 压缩期间连续输入多条消息 | 按 sequence 排队，不乱序，不串 run |
| agent loop 工具结果后触发 compact | tool result 已落库，压缩后同 run 继续 |
| tool call 未配 result 时达到阈值 | 不在该边界压缩，等 result 落库后再处理 |
| emergency prompt-too-long | force compact 后重试，失败则 error |
| compaction 失败 | fallback 或 error，不发 done |
| renderer HMR/reload | 通过分桶 store / reattach 恢复状态 |
| 跨会话后台压缩 | events 只落对应 conversation bucket |
| 用户 abort | run cancelled，锁释放，队列状态一致 |

## 十五、验收标准

1. 用户发送超长上下文下的新消息后，无需再次点击或手动“继续”。
2. 长流程自动压缩后，任务继续执行同一个 run。
3. 最新用户消息在 provider request 中保持原文。
4. 压缩前后的 token 显示符合 ADR 42，不再压缩后停在高位。
5. 压缩完成不会产生 assistant final message，也不会发 `chat:stream:done`。
6. 工具调用历史在压缩后仍满足 provider 消息结构要求。
7. 重载、切会话、后台运行时，compaction 和 stream 状态不串会话。

## 十六、一句话决策

```text
用户发送触发压缩时，hold provider request，不 hold UI message；
Agent 长流程触发压缩时，checkpoint run 并自动 resume，同一个 runId 继续到真正终态。
```

## 十七、Phase 1 落地记录

落地时间：2026-07-04

已在 `peer_agent` 完成第一阶段实现：

- `context-compactor.mjs` 新增 `preserveLatestUserTurn` 切分策略。
- 自动 preflight / emergency compaction 保留最新真人 user turn，避免刚发送的用户原文被 summary 代替。
- 手动 `/compact` 默认仍保持“真·全量压缩”语义。
- Anthropic 纯 `tool_result` user message 与 `_compaction` handoff 不会被误判为真人用户输入。
- OpenAI / Anthropic / Gemini 三条 agent loop 的自动压缩路径均启用 `preserveLatestUserTurn`。

验证：

- `node --test apps/desktop/electron/main/context-compactor.test.mjs`
- `node --test apps/desktop/electron/main/chat-runtime/compaction-coordinator.test.mjs`
- `node --test apps/desktop/electron/main/chat-runtime/agent-loop-kernel.test.mjs`

## 十八、Phase 2 落地记录

落地时间：2026-07-04

已在 `peer_agent` 完成第二阶段核心语义：

- `runCompactionCheck()` 将 `preserveLatestUserTurn` 显式透传给 `compactIfNeeded()`，把“自动压缩保留最新用户原文”固定到 coordinator 边界。
- service 层新增端到端测试：自动压缩先完成 `chat:compaction done`，随后同一个 OpenAI turn 继续产生模型 `delta` 和最终 `chat:stream:done`。
- service 层新增失败路径测试：自动压缩持久化失败时，不继续 provider request，不发 `chat:stream:done`，而是发 `chat:stream:error`。
- 修复 coordinator 的持久化失败收尾：只有压缩持久化和 `done` 通知都完成后才标记横幅已结算；若 `persistCompaction` 抛错，catch 分支会补发 `idle` 并释放 compaction registry，避免压缩态悬挂。

验证：

- `node --test apps/desktop/electron/main/chat-runtime/compaction-coordinator.test.mjs`
- `node --test --test-name-pattern "automatic compaction|persistence fails" apps/desktop/electron/main/llm-chat-service.test.mjs`
- `node --test apps/desktop/electron/main/context-compactor.test.mjs`
- `node --test apps/desktop/electron/main/chat-runtime/agent-loop-kernel.test.mjs`
