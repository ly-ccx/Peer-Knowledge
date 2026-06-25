# 30. Provider Recovery Broker

## Status

Accepted locally on 2026-06-15.

## Context

ChatGPT subscription traffic uses the OpenAI Responses transport at
`chatgpt.com/backend-api/codex/responses`. In enterprise networks this transport
can fail before it reaches the model service, for example with a 403 domain
blocking response from the local security gateway or with a Node `fetch failed`
transport exception.

The previous runtime had only a single direct provider adapter path:

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
but retries the same HTTP request through a platform-native connection adapter
when Node fetch cannot establish the connection. The initial desktop adapter is:

```text
node fetch -> Electron net.fetch
```

This handles local trust-store differences such as enterprise TLS interception
where Node reports `SELF_SIGNED_CERT_*` but Chromium/Electron can use the
system trust store.

The second layer is provider recovery. It is only reached after connection
recovery cannot produce a provider response.

The broker builds a provider candidate chain from configured runnable providers:

```text
default configured provider
  -> other configured providers with the same model id in store order
```

Provider recovery is model-locked. It may switch connection strategy, base URL,
or compatible provider adapter only when the requested `model` remains the same.
It must not turn a failed `gpt-5.5` request into a Claude, Gemini, or any other
different-model request.

For each provider attempt, the runtime:

1. Resolves that provider's credential in main.
2. Rebuilds System Context with that provider/model as the active provider
   target.
3. Runs the existing OpenAI/Anthropic agent loop and adapter.
4. Lets the provider adapter exhaust connection candidates for that same
   provider/model.
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

- Node `fetch failed` and common undici/network causes;
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
connection layer retries the encoded request through another connection adapter;
the provider broker selects another provider only after that path fails. Neither
layer manually translates message payloads outside the existing encoder seams.

## Consequences

- A blocked ChatGPT subscription transport first tries a same-model connection
  fallback. For example, `gpt-5.5` over the subscription Responses adapter can
  retry with Electron `net.fetch` after Node fetch reports a corporate TLS
  certificate failure.
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
