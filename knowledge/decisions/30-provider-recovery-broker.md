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


## 2026-11-07 Shared provider diagnostics and SDK hosts

Status: accepted under the user's KXT repair request; local implementation and focused validation completed, unreleased. Installed-build and native-platform validation remain pending; real host/channel results are recorded below. This extends optional runtime error metadata, not replay permission, tool authorization or provider failover. ADR 56 retains provider-backed token authority; ADR 65 retains the shared CLI runtime and its permission boundary.

Goal and scope: fix missing string-shaped JSON errors and unsafe raw HTTP bodies in the compatible chat, Responses and chat adapter paths. Add a bounded diagnostics reader and an immutable compatible-chat request encoder shared by preflight and actual send. The runtime SDK preserves optional safe structured diagnostics in failed results/events while retaining existing reason strings. KXT integrates the source SDK, not the independent CLI executable.

Decisions: errors carry allowlisted code/source/status/request ID and numeric limit facts; arbitrary provider text, HTML, prompt echoes and credentials are not diagnostic truth. Read body size/time bounds apply before parsing. Transport cancellation remains cancellation. Known safe diagnostic categories may be displayed, unknown detail is omitted. Final encoded request bytes are available without network side effects. No blanket 400 retry or history discard.

Compatibility/risk: existing error status/providerId, human-readable reason and runtime.error event code remain available; new metadata is optional. Structured metadata may not invent retry authority. Shared compaction split remains runtime-core-owned; KXT retains archives/Evidence and its v1 checkpoint. No installed app, personal session or release change.

| Acceptance | Scenario / operation | Expected result / verification |
| --- | --- | --- |
| D1 | HTTP JSON object error, string error, top-level message, plain/HTML/empty/oversized/stalled body | Bounded reader, typed status and stable allowlisted code; no credentials, prompt echo or raw HTML; provider unit matrices |
| D2 | Throw a typed provider error through the real pipeline | Failed state/reason survive; optional safe diagnostic survives in event/result; SDK regression |
| D3 | Encode tool/message/reasoning requests then send | Captured actual wire body equals preflight encoding byte for byte; provider encoder integration |
| D4 | Old errors and cancellation | Legacy message/status behavior for safe categories; arbitrary exceptions do not gain retry policy; abort remains cancellation; focused regressions/type checks |
| D5 | Responses and adapter non-JSON errors | Same bounded safe diagnostic seam, stream success behavior unchanged; provider path regressions |

Actual checks/results and outstanding installed-build/real-model coverage will be appended after implementation. No release or push of unrelated changes is authorized.

Implementation refinement before code: a generic `invalid_request_error` code/type must not hide a narrowly recognized context-length assertion in the same response. Specific auth/model/quota codes remain authoritative. Add generic-error-with-context and ordinary-invalid-request counterexamples in the shared reader and host gateway before normalization changes. No additional replay policy.

### 2026-11-07 implementation results

Implemented in the isolated code checkout, branch `fix/provider-history-recovery-20261107`, based on `4b476e69aa5a483b3a7b6a55361b617a827ab771` / rc.37. The original Peer checkout and its unrelated pending work were preserved. The source is an uncommitted worktree snapshot, not a new release. KXT rebuilt the selected source SDK; bundle SHA-256 `2c12fd1ca28f2b51cbb4a7fb912ddf236202638ab51e4d9feb7418a2099188ac`, 314 input hashes, workingTreeSnapshot=true.

D1–D5 focused validation: 49 provider/SDK tests and 4 SSE lifecycle tests passed, including the same request encoder/wire body, optional diagnostic result/event preservation, cancellation, bounded error bodies and all three HTTP paths. runtime-node and runtime-sdk typechecks, package builds and architecture governance passed. A generic invalid_request_error plus a definite context assertion failed first and passed after normalization; plain invalid requests stayed generic. Arbitrary body text remained omitted.

The runtime-node expanded suite initially recorded 2008 passes and 2 Electron import failures out of 2010 entries in the isolated worktree. After reusing the matching local Electron 41.7.1 test dependency, those two files passed all 15 checks without an override. This was a scoped recheck, not a single successful full-suite rerun. KXT exercised a real SDK→worker→HTTP gateway→Go error path, 600 actual file tool calls and recovery of a copy of the captured 514-message checkpoint. Real models were unverified in that initial rc.37 candidate. Installed applications, native Windows/Linux and the complete independent Peer CLI/Desktop release gates remain unverified. No release, runtime upgrade, live task modification or push occurred. See the KXT ADR-0005 validation record `docs/validation/peer-context-recovery-20261107.md` for per-scenario evidence and partial acceptance.

Real-channel failure refinement (before implementation): the saved Zhipu channel returned HTTP 429 / code 1113 even for a minimal request. Official https://docs.bigmodel.cn/cn/api/api-code defines this as account arrears, not transient capacity. Normalize 1113 to insufficient_quota only for the recognized upstream origin open.bigmodel.cn; normalize its documented 1261 to context_length_exceeded at the same seam. Unknown origins cannot assert these numeric codes. Add positive and unknown-origin regressions in KXT and shared Peer diagnostics. No automatic billing action, quota retry or model switch is authorized. Real Zhipu success and cross-channel continuation remain blocked until the account can infer.

Real-verification endpoint correction: 1113 was observed on the saved standard API URL, /api/paas/v4. The user has Coding Plan and provided /api/coding/paas/v4, matching the official quick-start. The standard API balance result does not establish subscription arrears. Retest the subscription URL without mutating online configuration. The final code review branch is based on current development cb7e14c965c9102d49252e5a362457770ea51d14 / rc.38 and contains only the diagnostic/SDK changes, excluding unrelated historical branch commits. Final focused regression: 56 tests, runtime-node/runtime-sdk builds and typechecks, architecture governance passed.

Final review source: Peer commit `9485b26ad411a9def3bbb40a8a81cfc30355c671`, [Peer-Agent PR #298](https://github.com/ly-ccx/Peer-Agent/pull/298), based on current development cb7e14c9 / rc.38. The 17 scoped source files passed 57 provider/SDK/SSE tests, package builds/typechecks and architecture governance. An unrelated upstream generated watch-ledger cache drift was excluded from the commit. KXT's pinned bundle SHA-256 is `c802575f915263ee6a3af5f32329f75a9beb82a2625c5eb6400c6678cbfb43b4`, 314 verified inputs, workingTreeSnapshot=false.

Real host acceptance passed with the saved default deepseek-v4.1-flash and the user's GLM Coding Plan glm-5.3-flash endpoint: each restored synthetic history from 515 to 3 messages before task inference, retrieved original continuity/evidence, and wrote/read a random proof marker through real tools. A default-channel saved session then resumed on Zhipu and wrote a second verified file without changing completed evidence. Synthetic tasks, credentials in process memory and disposable fixture services were used; no original user conversation was sent to the model. The subscription endpoint is confirmed by the [official endpoint reference](https://docs.bigmodel.cn/cn/coding-plan/quick-start). These checks are SDK-host acceptance, not installed-build or full release acceptance.

CI regression refinement before code: both Peer platforms reported the existing visual-response-binding overflow regression. Local reproduction confirms that safe HTTP normalization omitted the anchored provider assertion "This model's maximum prompt length is ...", and its human label alone did not match the shared overflow detector. Recognize that narrow assertion and include the stable context_length_exceeded marker in generated context labels; retain only generated text, not arbitrary bodies. Extend reader regressions and re-run the actual desktop visual-response-binding path plus shared provider tests. Apply the equivalent normalization in KXT's upstream gateway. No replay policy is broadened: only the already-supported definite overflow assertion reaches the existing one-request compaction owner.

The reproduced desktop fixture wraps its HTTP-400 context assertion in SSE choice deltas. Extend the bounded HTTP-error reader to decode complete SSE data frames only on this error path, reassemble text for the same narrow category recognizer, and omit all arbitrary content. Malformed/unknown frames do not become diagnostic truth. This retains the pre-existing overflow owner and visual response-binding assertions without changing the fixture or exposing raw SSE text.

Preserve the known provider assertion's validated integer requested/maximum token facts in the optional actual/limit fields and a generated fixed-format overflow message. The shared capacity parser must still recover the same provider-backed counts after sanitization (ADR-56); no text or inferred token estimate is forwarded. Add assertions for that downstream parse, not just recognition.

CI follow-up source: Peer 5483e4a333dee2b0e3f996094cf3ecf48f09937b / PR #298. The initial 9485b26a revision failed the unchanged desktop visual-response-binding HTTP-400 SSE overflow case on both CI platforms; local reproduction and the reader fix passed all 168 combined provider/SDK/SSE/visual-binding checks, with typecheck and architecture governance passing. The fixed reader preserves provider-backed integer capacity evidence and stable overflow markers without arbitrary raw content. KXT MR !6 pins this source, bundle 0ceb9d809e21012cffee4959d7198e54c92c4d431673b0dae2cce6b9a2d2b902, 314 verified inputs, and repeats real host acceptance. Remote CI is a separate merge gate; no merge or release is authorized. KXT review: https://git.meiyunji.net/kxt/kxt-ai-lab/-/merge_requests/6 .

The next full CI run exposed a second integration regression: the chat adapter's successful-HTTP streaming-error return accidentally referenced an HTTP-error-block-local diagnostic variable. Remove that out-of-scope field; stream errors retain their existing streamError/errorText and partial-output replay guard. Reproduce with the unchanged llm-chat-service no-replay-after-output test, add the direct adapter case, and broaden local validation to the complete affected desktop/runtime-node packages before the next CI push. This is not a new retry or stream-error authority.

Final stream-scope follow-up source: Peer 014b4e04c398f2b330a4cf5437f8d42556d118a4. The original no-replay-after-output regression and direct adapter event case passed in 184 targeted checks; KXT's executable bundle and all 314 input hashes remain identical to the real-verified 0ceb9d80... bytes because the desktop chat adapter is excluded from that host bundle. Expanded local checks: desktop main/renderer/preload 6266 passed, 5 skipped, 0 failed (6271 total). runtime-node 2058/2059 passed in the broad run; the single performance wall-time assertion (870ms vs 500ms, within the algorithmic 144 <=192 call bound) passed unchanged in isolation (109.6ms total). Preserve both attempts and do not call this a single all-green full run. No unrelated implementation or threshold change. Remote CI remains a separate gate.

### Review follow-up: legacy HTTP error construction

Before implementation: the latest review of 014b4e04 identifies that Anthropic, Gemini and Qoder TUI adapters still construct `ModelProviderHttpError(providerId, status, errorText)` without structured diagnostics. Exact-label lookup drops recognized JSON context errors and prevents the existing overflow owner from compacting. This is a compatibility repair under D4, with no new retry, failover or replay authority.

Decision: extract synchronous bounded text classification from the shared HTTP reader and reuse it in three-argument construction. Both entrances use identical JSON/plain/SSE category recognition and generated messages; arbitrary content and HTML are omitted. The constructor must preserve explicitly supplied diagnostics, must not infer trusted gateway origin or provider origin from a body, and must not grant unattempted-request authority. Preserve validated provider token facts and request status. No network work, personal session changes or installed Runtime changes.

Acceptance L1: construct legacy JSON/plain/SSE overflow errors, feed the resulting message to the shared overflow parser, and retain recognized category/token facts without private sentinel text. L2: exercise actual Anthropic/Gemini/Qoder provider entry points with synthetic HTTP failures and check the thrown error still reaches overflow recognition. L3: arbitrary/HTML/oversized/prototype-name details remain generic; explicit structured diagnostics retain precedence; spoofed gateway/numeric-origin facts are rejected. Validate focused runtime/TUI tests, package builds/typechecks and architecture governance, then current-head CI and fresh review. KXT must repin and validate any changed bundle input before claiming those host results cover the new candidate. Results pending.

Legacy follow-up implementation: Peer cba9318b3949290d9f0e0f8758900d80a5cfc655. L1/L3 constructor regressions failed on the old source and passed after shared classification; own-property label lookup also prevents prototype-name details from producing inherited function text. L2 actual Anthropic/Gemini/Qoder TUI provider entrances passed all 16 tests; focused HTTP/provider suite passed 42 and SDK/SSE/recovery suite passed 32. runtime-node build, runtime-node/TUI typechecks and architecture governance passed. Prior follow-up 014b4e04 macOS/Linux CI both passed; cba9318b remote CI and a fresh review are pending. KXT rebuilt the changed shared source as bundle 101c673c34fa230eb1e29cd4ad40be48f9b6e0a0e93a64ef6c25fb53875cb1e3, 314 verified inputs and clean source. Its new real-host verification is recorded separately in KXT; earlier bundle receipts must not be substituted for that candidate.

Before the next classifier revision: cba9318b review found remaining phrases already admitted by runtime-core's overflow predicate (`input is too long`, `exceeds model context window`). The safe classifier must share that existing predicate for category recognition instead of maintaining an incomplete parallel phrase list. Bounded body/HTML rejection and generated labels remain unchanged; recognized category alone does not confer replay authority. Acceptance L4: enumerate every current shared overflow spelling through JSON, plain and legacy construction, verify downstream predicate parity and private sentinel omission, and rerun the unchanged compaction coordinator cases. Include ordinary invalid-request counterexamples. KXT must rebuild and revalidate changed bundle bytes again. This supersedes the narrow recognition subset without broadening runtime-core's established policy.

Overflow parity implementation: Peer ea3c1266294a81b40545f04ac6eb1e5805cdd063. The new vocabulary matrix failed first, then the shared runtime-core predicate passed all 82 provider/compaction tests and 16 TUI entry tests. runtime-node build/typecheck and architecture governance passed. L4 covers all ten established spellings in JSON/plain and three-argument construction, retains known token facts, and omits private sentinel content. Fresh review and CI are pending on this exact head. Earlier bundle and real-model receipts remain historical; KXT rebuilds and rechecks the new executable independently. No new recovery permission or tool execution path is introduced.
