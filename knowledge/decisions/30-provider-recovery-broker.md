# 30. Provider Recovery Broker

创建时间：2026-06-15

最后更新：2026-07-30

## Status

Accepted locally on 2026-06-15. Revised on 2026-07-30 to make Electron
`net.fetch` the sole Desktop provider transport.

## Context

ChatGPT subscription traffic uses the OpenAI Responses transport at
`chatgpt.com/backend-api/codex/responses`. In enterprise networks this transport
can fail before it reaches the model service, for example with a 403 domain
blocking response from the local security gateway or with a transport exception.

The original runtime had only a single direct provider adapter path:

```text
selected provider -> adapter fetch -> terminal done/error
```

That made transport failures indistinguishable from model failures in the chat
surface. It also left the user without the platform-level recovery behavior that
Codex-like hosts provide when a streaming transport is blocked or reconnects.

## Decision

Add two recovery layers in main process, before provider/transport failures
become terminal renderer errors.

The first layer is connection recovery. It keeps the same provider and model,
but retries the same HTTP request on the authoritative Desktop transport:

```text
Electron net.fetch -> bounded retry on Electron net.fetch
```

Desktop provider traffic must not probe or fall back to raw Node fetch.
Electron `net.fetch` follows Chromium's proxy resolution and the macOS trust
store, which keeps chat, OAuth, quota, model catalog, context count, pricing
backfill, and connection-test requests on the same network policy. If Electron
transport is unavailable in the Desktop main process, the request fails closed
instead of silently changing stacks.

The TUI is a separate host and retains its own Bun/Node transport policy. This
decision does not require Electron outside the Desktop runtime.

The second layer is provider recovery. It is only reached after connection
recovery cannot produce a provider response.

The broker builds a provider candidate chain from configured runnable providers:

```text
default configured provider
  -> other configured providers with the same model id in store order
```

Provider recovery is model-locked. It may switch base URL or compatible provider
adapter only when the requested `model` remains the same.
It must not turn a failed `gpt-5.5` request into a Claude, Gemini, or any other
different-model request.

For each provider attempt, the runtime:

1. Resolves that provider's credential in main.
2. Rebuilds System Context with that provider/model as the active provider
   target.
3. Runs the existing OpenAI/Anthropic agent loop and adapter.
4. Lets the provider adapter exhaust bounded retries on Electron `net.fetch`
   for that same provider/model.
5. Buffers only terminal `chat:stream:error` until replay safety is known.
6. Replays the same user turn on the next same-model provider only when the
   failure is a transport-level/provider-reachability failure and no
   replay-unsafe stream event has been observed.

Replay-unsafe events are:

- model text or thinking deltas;
- tool-call, tool-progress, tool-result, and permission-request events;
- provider usage events.

Once any of those events has reached the stream, the runtime must not replay the
turn on another provider. This prevents duplicated local tool execution and keeps
PermissionGrant / Evidence truth single-sourced in the existing capability path.

## Failure Classification

The first recovery classifier is intentionally narrow. It treats these as
transport/reachability failures:

- Electron `net::ERR_*`, timeout, connection reset/refused, proxy, DNS, HTTP/2,
  and QUIC transport failures;
- compatible Bun/Node transport errors when the same module is hosted outside
  Desktop;
- HTTP 403 or "unexpected status 403 Forbidden" with enterprise domain blocking
  text;
- connection reset/refused, DNS failure, and timeout codes.

It does not recover semantic provider errors such as empty model responses,
prompt-too-long responses, unsupported tool claims, or permission/tool failures.

## Runtime Event

When provider recovery happens, main emits:

```text
chat:stream:provider-recovery
```

When connection recovery happens without changing provider/model, main emits:

```text
chat:stream:connection-recovery
```

Both are runtime status events only. They are not assistant text, not Tool
Result, and not Evidence. The renderer may display them as transient notices,
but it must not treat them as model output or persist them as assistant content.

## Boundaries

This recovery layer does not add a separate local capability path. Local tools
continue to flow through:

```text
Capability Provider -> Manifest -> Runtime Projection -> Tool Call -> PermissionGrant -> Evidence
```

The broker only replays the provider request before that chain has started for
the attempted turn. After tool intent or output is visible, the existing stream
continues to own terminal truth.

Provider-specific wire formatting remains behind provider encoders/adapters. The
connection layer retries the encoded request on the same Electron transport; the
provider broker selects another same-model provider only after that path fails.
Neither layer manually translates message payloads outside the existing encoder
seams.

## Consequences

- A transiently blocked ChatGPT, Grok, Gemini, Anthropic, OpenAI, or Qoder
  request retries on Electron `net.fetch` without switching proxy or certificate
  behavior mid-request.
- Desktop requests no longer let a guaranteed-to-fail raw Node fallback replace
  the useful Electron error with a misleading `SELF_SIGNED_CERT_IN_CHAIN`
  terminal message.
- Switching to another configured provider is only allowed when that provider is
  configured for the exact same model id. Cross-model fallback is deliberately
  disallowed because it changes the effective reasoning/runtime contract of the
  turn.
- Prompt snapshots are recorded per attempt with `recoveryAttempt`, so the
  effective provider target for the recovered request remains auditable.
- The first implementation is provider failover, not stream reattach to a
  service-side run id. Reattach remains ADR 22's existing in-process stream
  snapshot behavior.
- If all candidate providers fail, or if the first failure is not replay-safe,
  the original terminal error is emitted unchanged.
