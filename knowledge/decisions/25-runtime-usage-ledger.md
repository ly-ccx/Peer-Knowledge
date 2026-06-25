# Runtime Usage Ledger

## Status

Implemented locally on 2026-06-11.

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

If the terminal payload contains billable usage and a `conversationId`, main
calls `conversationStore.addUsage(conversationId, usage)` before forwarding the
event to renderer. The forwarded event is enriched with authoritative
`lifetimeUsage`.

Renderer no longer writes the usage ledger during normal chat. It only:

- renders active per-request usage during streaming;
- renders `lifetimeUsage` returned by main on terminal events;
- keeps a compatibility fallback for older runtimes that send usage without
  lifetime usage.

## Boundaries

The ledger is not a UI concern. Renderer must not be the source of truth for
session billing or token history.

Provider adapters parse usage. Agent loop aggregates usage across tool turns.
Main runtime persists usage to the conversation ledger. Renderer displays the
ledger and transient active usage only.

This keeps the chain aligned with:

```text
Provider Usage -> Agent Loop Usage -> Runtime Ledger -> Renderer Display
```

## Error Semantics

If provider usage exists before a terminal error, the ledger records it. This
includes empty model responses after a provider already returned usage.

If no provider usage exists, no ledger entry is written.

## Tests

Regression tests cover:

- completed stream usage is written by main before `chat:stream:done` reaches
  renderer;
- `chat:stream:error` with provider usage is also written to the main ledger and
  forwarded with `lifetimeUsage`.
