# 上下文圆环长期显示「?」：观测即持久化修复

创建时间：2026-07-29
最后更新：2026-07-29

## 症状

- 会话头部上下文占用圆环长期显示 `?`，tooltip 为 `Context pending measurement / 500.0k`
- 同一会话的 Cache hit / Usage remaining 等费用统计**有数**
- 重启 / 重开会话后依然是 `?`

## 根因（证据链）

以会话 `6ca4d665-dd42-4bec-ab56-cc2c5a1bffe6`（Grok 官方 grok-4.5，`observed_usage_only`）为例：

1. **sidecar 快照无观测**：`.context-snapshots/<id>.json` 里
   `pressureSource=unknown`、`percent=null`、`authoritativeInputTokens=null`、无 `lastObserved`
2. **账单有真实用量**：`usage/requests.jsonl` 有该会话 `usageScope=runtime_turn`、
   13 次 provider 请求、input 219k / cacheRead 245k —— 但 runtime_turn 明确不参与圆环
3. **断点在持久化时机**：context pipeline 在每次 provider 响应时会 `observe()` 出
   `pressureSource=provider_usage` 的快照并通过 `context.accounting` 运行时事件上抛，
   但 sidecar 落盘只发生在 `chat:stream:done` 的 payload 上。
   **turn 被中断（aborted）→ 没有 done → 观测全部丢失**
4. restore（`chat:context:restored`）依赖 `getLatestContextObservation`，
   而它只认 sidecar 的 `lastObserved`（source=provider_usage）→ 无基线可回填 → 永久 `?`

一句话：**费用账（runtime_turn）和圆环账（provider_usage lastObserved）是两条解耦链路；
旧实现里圆环账只在 done 时落盘，中断的 turn 把观测丢了。**

## 修复（代码仓 peer_agent）

### 1. 观测即持久化（主修）

`apps/desktop/electron/main/llm-chat-service.mjs`：
用 `emitRuntimeEventPersistingAccounting` 包装 `emitRuntimeEvent` 传给四个 agent loop，
拦截 `context.accounting` 事件——满足以下条件立即 `updateContextSnapshot` 落盘：

- `snapshot.version === 1` 且 `pressureSource === 'provider_usage'`（estimated/unknown 不落盘，避免噪声覆盖观测事实）
- 有 `conversationId` 且非 `ephemeral` 旁路流

### 2. 终态双写去重

done/error 路径原有的落盘保留，但按 `contextSnapshotPersistKey`
（`modelKey::revision::lastObserved.at`）去重：观测时已写过的同一快照不再重复写。

### 3. restore 防覆盖守卫

`apps/desktop/electron/main/main.mjs` `chat:context:restored`：
当新算出的快照 `pressureSource=unknown` 且 sidecar 已有同 modelKey 的
`provider_usage` 快照时**跳过落盘**——防止「重启 → restore 无 observation →
unknown 落盘」抹掉已有圆环基线。

## 验证

- 新增回归测试：`persists provider_usage context snapshots at observe time, before any terminal event`
  （断言落盘先于任何终态事件、恰好一次、pressureSource=provider_usage）
- `llm-chat-service.test.mjs`：pass 50 / fail 6，失败集与基线（git stash 对照）逐项一致，无新增回归
- `agent-loop-kernel.test.mjs`：pass 20 / fail 0
- `check-architecture-governance.mjs`：退出码 0

## 经验

- **凡「有账单但圆环 ?」先分链路**：runtime_turn（费用）≠ provider_usage（圆环），
  不要用费用账直接填圆环，会破坏 observed_usage_only 契约
- **持久化时机要跟观测对齐**：任何"只在终态落盘"的设计都会在 aborted/crash 时丢证据；
  证据产生时就该落盘，终态只做去重补写
- **restore 空态不能覆盖既有观测**：unknown 是"不知道"，不是"归零"

## 关联

- ADR 56（provider-observed context accounting）
- knowledge/experience/context-occupancy-ring-inaccuracy-root-cause.md（RC10 恢复守卫）
- knowledge/experience/cli-desktop-context-percent-mismatch-during-thinking.md（sticky 显示）
