# Per-Message Turn Duration Persistence

## Status

Accepted（Implemented locally on 2026-06-17；最后更新：2026-11-15，对齐主进程 `append` 持久化边界，标注 `conversations:replace-messages` 在活跃聊天与 Project Bot 主链路已被取代）。

> [!NOTE] 与 ADR 85 / ADR 96 / ADR 121 对齐（2026-11-15）
>
> - 原先由渲染层全量写回历史数组（`conversations:replace-messages`）承担持久化的假设，在活跃对话执行、Goal Runner 与 Project Bot 主链路中**已被宿主侧增量 `append`（`store.appendMessage` / [ADR 121](121-desktop-session-windowing-contract.md) `SessionService.append`，参见 [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 与 [ADR 96](96-task-execution-responsiveness.md) §实施追踪补记）取代**；`conversations:replace-messages` 仅残留在部分显式编辑/重发或历史兼容分支中。
> - 每条助手消息携带可选 `durationMs` 展示元数据、而不并入 `lifetimeUsage` 计费账本（[ADR 25](25-runtime-usage-ledger.md)）的核心契约继续成立，仅改为随宿主 `append` / 终态写入一并落盘。

## Problem

The chat footer now shows a live "elapsed this turn" timer while a turn runs, and
each assistant message keeps a finished `durationMs` trace (whole-turn
wall-clock, from send to the terminal `done` / `aborted` / `error` event). That
work landed as a B-level renderer change.

But `durationMs` lived only in renderer state. On reload, branch, or workspace
switch the conversation messages are re-hydrated from the conversation store, and
the duration trace was dropped because neither the persist projection nor the
load projection carried the field. So a user who reopens a conversation could see
token usage and cost on each message but not how long that turn took.

Persisting a new per-message field crosses a storage boundary, which is an
A-level change under the governance baseline. This ADR records the decision.

## Decision

`durationMs` is **per-message presentation metadata that travels with the
message**, at the same level as the existing per-message `usage` and `timestamp`
fields. It is persisted through the already-existing message carrier
(`conversations:replace-messages`, the renderer-owned open-bag projection), not
through a new channel.

`durationMs` is **not** promoted to a main-owned aggregate ledger. The runtime
usage ledger (ADR 25, `lifetimeUsage` on conversation index meta) remains the
authoritative billing/aggregation truth and is unaffected. Turn duration is a
display fact about a single assistant turn, not a session-level accounting fact,
so it does not need main ownership, aggregation, or compaction-immune storage.

## Boundaries

- Renderer owns the projection. The two explicit projections that form the real
  contract are both in `ChatSurface.tsx`:
  - persist projection (`persistMessages` -> `conversationsReplaceMessages`),
    which now includes `durationMs`;
  - load projection (`loadConversationMessages`), which now reads `durationMs`
    back onto `ChatMsg`.
- Storage stays an open bag. `conversation-store.replaceMessages` rewrites the
  message jsonl as-is with no field allowlist, so it already accepts the field;
  the contract is enforced by the renderer projections, not by the store.
- Main runtime ownership is unchanged. Turn duration does not enter the
  `lifetimeUsage` ledger and is not aggregated by the agent loop.
- The timing source of truth at runtime is `turnStartedAtRef` (set on send,
  read on the terminal event). Persistence only stores the finished value; it
  does not reconstruct elapsed time across restart, and a turn that never
  reached a terminal event has no persisted `durationMs`.

## Consequences

- Reopening a conversation now shows each assistant turn's duration trace, in
  line with how per-message `usage` already survives reload.
- Old conversations recorded before this change simply have no `durationMs` on
  their messages; the field is optional and the UI omits the badge when absent.
- No protocol shape change is required: `conversations:replace-messages` already
  carries `readonly Record<string, unknown>[]`, so the open-bag carrier absorbs
  the new field without a new contract type.

## Tests

Regression coverage asserts that:

- a message carrying `durationMs` round-trips through the persist projection and
  the load projection without losing the value;
- a message without `durationMs` loads cleanly (field stays undefined).
