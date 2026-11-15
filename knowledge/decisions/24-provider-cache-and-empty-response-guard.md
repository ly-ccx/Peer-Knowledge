# Provider Cache And Empty Response Guard

## Status

Accepted（2026-06-11 本机落地实现；最后更新：2026-11-15，修正治理基线相对路径链接）

## Problem

Anthropic-compatible requests now use prompt caching. The first implementation put
the history cache breakpoint on the second-to-last message's last content block.
That works for plain text turns, but tool loops often end the previous assistant
message with a `tool_use` block and the latest user message with `tool_result`.

Putting `cache_control` on a capability contract block blurs two boundaries:

- `tool_use` / `tool_result` are execution ledger objects, not prompt text.
- provider cache hints are provider request encoding details.

The observed failure mode was an empty provider response immediately after
successful tool results. The persisted conversation showed completed tool calls,
then `empty_model_response`; no tool execution failure was recorded.

## Decision

Anthropic cache breakpoints are allowed only on text blocks:

- `system` remains cacheable as a text block.
- history cache scans backward from the second-to-last message to the nearest
  cacheable text block.
- `tool_use`, `tool_result`, image blocks, and other structured capability blocks
  never receive `cache_control`.

The agent loop also performs one bounded recovery for empty responses after real
tool results:

- if the latest API message is an OpenAI `tool` message or an Anthropic user
  message containing `tool_result`, append a correction and retry once;
- if the response is empty before any tool result, keep reporting
  `empty_model_response`;
- if the retry is exhausted, keep reporting `empty_model_response`.

## Per-Gateway Cache Capability (2026-06-12)

Not every Anthropic-compatible gateway actually reuses prompt caching. The
idealab Anthropic gateway (`idealab.alibaba-inc.com` + `/api/anthropic`, which
also forces `thinking.type: adaptive`) was measured with a two-request probe:
both requests reported large `cache_creation` (cache write) and zero
`cache_read` (cache hit). On that link a cache breakpoint is pure write-only
cost at the higher cache-write unit price, with no reuse benefit.

### First cut: baseUrl heuristic (superseded)

The initial fix hardcoded `resolveAnthropicPromptCaching(baseUrl)` to return
`false` for the idealab adaptive gateway and `true` otherwise. This worked but
inferred a gateway capability from a URL string inside the adapter.

### Current: declared provider capability (2026-06-12)

Prompt caching is now a declared provider capability field, not a baseUrl guess:

- `LlmProviderConfig.supportsPromptCaching?: boolean` (protocol), persisted by
  `llm-config-store` (`toView` / `addProvider` / `updateProvider`), and editable
  in `LlmSettingsPanel` as a checkbox alongside `supportsReasoning` /
  `supportsVision`. It mirrors how reasoning/vision capabilities already flow
  config -> store -> chat service -> agent loop -> adapter.
- Default is `false`. A gateway only writes cache breakpoints when an operator
  has confirmed it actually reuses cache. This is the safe default because a
  gateway that writes but never reads cache is pure cost.
- `llm-chat-service` passes `supportsPromptCaching` into `agentLoopAnthropic`,
  which forwards it as `promptCaching` to `sendAnthropicMessagesStream`.
- The adapter passes `promptCaching` into `encodeAnthropicMessagesRequest`. When
  `promptCaching` is `false` the encoder returns the body before applying any
  `cache_control` breakpoints, so `system` stays a plain string and no message
  block carries `cache_control`. The cached prefix degrades to ordinary input
  (lower unit price than cache write).
- The encoder default for `promptCaching` stays `true` so encoder-level unit
  tests of cache breakpoints remain meaningful; the runtime default-off lives at
  the adapter boundary (`promptCaching = false`) and is driven by config.

This keeps the cache decision behind the provider encoder/adapter seam and moves
the truth into the provider capability contract instead of a URL heuristic. It
does not add `capabilityId` branches to central hosts and does not change tool,
permission, or Evidence paths.

## Empty Response Must Not Persist A Capability Downgrade (2026-06-14)

The empty-response recovery above also downgrades native reasoning for the
*current turn*: when high effort returns an empty response, the agent loop sets
`effectiveSupportsReasoning = false` and retries the same turn without a
`thinking` request block. That is correct in-session self-healing.

An earlier implementation went one step further: the
`onNativeReasoningFallback` callback called
`llmConfigStore.updateProvider(provider.id, { supportsReasoning: false })`,
persisting the downgrade into the provider config.

This was wrong. An empty response is a transient event (rate limiting, network
jitter, near-full context, deep-mode edge cases). It is not proof that the
provider lacks reasoning support. Persisting it turned one transient event into a
permanent capability flag, so the deep-effort tier got silently and permanently
disabled even though the user never touched settings. It surfaced after the
OpenAI subscription OAuth work because that path exercised the fallback more
often, but the root cause was this write-back, not OAuth.

### Decision

- The empty-response fallback is **session-scoped only**. It changes the live
  request for the current turn and never writes the provider config.
- `onNativeReasoningFallback` is now a pure observability hook
  (`noteNativeReasoningFallback`) that logs the per-turn downgrade and leaves the
  `supportsReasoning` capability flag unchanged.
- A persistent `supportsReasoning = false` may only come from explicit user
  configuration or from a deliberate, separately-designed capability-probe path,
  not from incidental loop control flow.

This keeps the provider capability flag (a contract/config truth) separate from
in-session control-flow recovery (a kernel concern), matching the layer rules in
[20-architecture-governance.md](../architecture/20-architecture-governance.md).

A regression test in `llm-chat-service.test.mjs`
(`falls back to plain mode for the turn but does NOT persist
supportsReasoning=false on an empty response`) asserts the fallback never calls
`updateProvider` with a `supportsReasoning` patch.

## Boundaries

This is not a renderer behavior. It does not add new stream event types and it
does not render textual tool claims as execution.

Provider encoder owns provider-specific cache hint lowering. Agent loop kernel
owns bounded control-flow recovery. Tool execution, permission, and Evidence stay
in the existing capability path.

## Tests

Regression tests cover:

- cache hints on `system` and text history;
- no cache hints on `tool_use` / `tool_result`;
- backward scan when the second-to-last message is tool-only;
- empty response retry after OpenAI tool results;
- empty response retry after Anthropic tool results;
- unchanged error behavior for ordinary empty responses;
- adapter omits all `cache_control` breakpoints when `promptCaching` is disabled
  (runtime default-off);
- adapter keeps `cache_control` breakpoints when `promptCaching` is enabled.
