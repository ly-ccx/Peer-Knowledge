# Runtime Usage Ledger

- 创建时间：2026-06-25
- 最后更新：2026-11-15（跨 ADR 对齐：明确 `requests.jsonl` 与 [ADR 115](115-input-prediction-and-draft-boundary.md) `input_prediction` 账本物理隔离）

## Status

Accepted and implemented. Usage Scope unification completed on 2026-07-26.

## Problem

The chat footer should show session lifetime usage and cost. The previous wiring
made the renderer responsible for calling `conversations:add-usage` after
`chat:stream:done`.

That was the wrong ownership boundary:

- renderer state is presentation, not ledger truth;
- HMR, reload, render failure, or event timing could prevent the ledger write;
- error terminal paths such as `empty_model_response` could have provider usage
  but never reach the renderer-side `done` ledger write;
- during streaming the footer mixed lifetime usage with active transient usage,
  making the display look non-cumulative.

## Decision

Usage ledger writes are owned by main/runtime.

`llm-chat-service` wraps the provider/agent-loop `webContents.send` boundary and
intercepts terminal stream events:

- `chat:stream:done`
- `chat:stream:error`

If the terminal payload contains a tagged, billable `RuntimeTurnUsage` and a
`conversationId`, the host calls
`conversationStore.recordRuntimeTurnUsage(conversationId, ...)`. The shared
store validates scope, updates lifetime usage, and appends the runtime-turn
ledger row before the terminal state is presented.

Renderer/TUI presentation no longer owns ledger semantics. It only:

- renders `ContextAccountingSnapshot` for context capacity;
- renders active `RuntimeTurnUsage` or durable `ConversationLifetimeUsage` for
  billing views;
- renders `lifetimeUsage` returned by main on terminal events;
- keeps a compatibility fallback for older runtimes that send usage without
  lifetime usage.

## Boundaries

The ledger is not a UI concern. Renderer must not be the source of truth for
session billing or token history.

Provider adapters parse one request's usage. Shared runtime accounting
aggregates all requests in a tool-loop turn. The shared conversation store
persists the runtime turn and updates the conversation lifetime. Hosts display
those facts but do not redefine them.

This keeps the chain aligned with:

```text
ProviderRequestUsage -> RuntimeTurnUsage -> Runtime Ledger
                                      \-> ConversationLifetimeUsage
```

## Usage Scope Contract

The original implementation reused the same untagged token shape for three
different lifecycle scopes. That made a runtime-turn billing total look like a
single provider-request observation during context restore, while TUI persisted
only the final provider request of a tool loop.

The ledger contract now distinguishes:

| Scope | Meaning | May seed context accounting |
|---|---|---|
| `provider_request` | Usage returned for one immutable canonical provider request | Yes |
| `runtime_turn` | Sum of every provider request in one user turn / stream | No |
| `conversation_lifetime` | Sum of every completed runtime turn | No |

All hosts use the shared `RuntimeUsageAccounting` Module:

```text
observeProviderRequest
  -> lastRequest (overwrite)
  -> turnTotal (accumulate)
  -> providerRequestCount
```

The context-capacity Module consumes `lastRequest` only. The billing ledger
consumes `turnTotal` only. Conversation metadata accumulates `turnTotal` into
`conversation_lifetime`.

Automatic LLM compaction summaries are provider requests too. They use
`requestPurpose: "compaction_summary"` and contribute to `turnTotal` and
`providerRequestCount`, but `capacityBearing: false` prevents the summary
request from replacing the conversation request used by context accounting.
Failed provider attempts count as requests with null usage; they do not erase
the latest capacity-bearing observation.

Both hosts persist through one conversation-store serialized write seam:

```text
recordRuntimeTurnUsage(conversationId, { usage, attribution })
  -> validate usageScope == runtime_turn
  -> acquire the shared usage-ledger lock
  -> deduplicate by runtime-turn id
  -> increment conversation lifetime
  -> append runtime-turn ledger row
  -> return ConversationLifetimeUsage
```

The lock prevents Desktop and CLI/TUI usage writes from racing. This ADR does
not claim filesystem crash atomicity across the index file and JSONL ledger.
`addUsage` remains only as a compatibility path for legacy/injected stores.
Production Desktop and CLI/TUI must not implement separate lifetime/log writes.

Existing `requests.jsonl` rows have no reliable scope and are treated as legacy
runtime-turn billing rows. New rows carry `usageScope: "runtime_turn"` and
`providerRequestCount`. Context restore must never read this billing file.

> [!NOTE] 与 ADR 56 / ADR 115 对齐（2026-11-15）
>
> `requests.jsonl` 只承接会话 `runtime_turn` 账本行。按 [ADR 56](56-provider-observed-context-accounting.md) 与 [ADR 115](115-input-prediction-and-draft-boundary.md) 2026-11-15 对齐契约，后台 `input_prediction` 预约、结算与基于 UTF-8 字节上界的估算**不得**写入 `requests.jsonl`，而必须独立记录到 `usage/input-prediction.jsonl`（当前 115 首版实现复用 `requests.jsonl` 的代码行为已明确记为迁移债务）。

## Error Semantics

If provider usage exists before a terminal error, the ledger records it. This
includes empty model responses after a provider already returned usage.

If no provider usage exists, no ledger entry is written.

## Tests

Regression tests cover:

- multi-request tool loops accumulate every provider request but retain only
  the final capacity-bearing request for context;
- completed and terminal-error usage follows the same runtime-turn sink;
- TUI and Desktop both append scoped runtime-turn ledger rows and update
  conversation lifetime;
- duplicate runtime-turn ids do not increment lifetime twice;
- automatic LLM summary usage is billed but never becomes context authority;
- context restore never reads the runtime-turn billing ledger.
