# ADR 26 — Agent Loop Termination Semantics

## Status

Accepted locally on 2026-06-12（Last updated: 2026-11-15 — 无上限模型驱动终止适用于单回合助手执行循环；Project Agent 自主协调循环、无进展停止与核验门禁另受 [ADR 88](88-project-agent-execution-continuity.md)、[ADR 95](95-progress-driven-execution-policy.md)、[ADR 103](103-verification-settlement-and-progress.md)、[ADR 117](117-intent-driven-coordination-and-goal-closure.md) 约束，流终态落盘屏障见 [ADR 96](96-task-execution-responsiveness.md)）。

## Problem

Agent loop termination was previously coupled to a fixed local turn budget:

```text
for turn < 20:
  call model
  maybe execute tools
send done
```

That made a runtime safety counter indistinguishable from task completion. A
coding task with many legitimate file reads and edits could hit the local
budget and appear to finish successfully even though the model had not returned
a terminal answer.

This violated the runtime boundary:

- the model owns normal task completion;
- runtime owns local execution and terminal event truth;
- renderer only expresses the terminal event it receives.

## Decision

Normal completion is model-driven.

`chat:stream:done` is emitted only when the provider returns a terminal response:

- final assistant text, or
- thinking-only response that contains provider reasoning content and no tool
  request.

Agent-loop turn budget is not a completion signal. The default loop is
unbounded so the model can continue until it chooses to stop, the user aborts,
or a concrete provider/tool/runtime error occurs.

If an operator explicitly configures a finite loop budget, exhausting that
budget emits `chat:stream:error` with `agent_loop_exhausted`. The task is marked
not complete.

## Runtime Contract

Terminal stream events now mean:

- `chat:stream:done`: model produced a terminal response.
- `chat:stream:aborted`: user/runtime cancellation stopped the stream.
- `chat:stream:error`: provider, tool, permission, runtime, or configured budget
  failure stopped the stream.

`agent_loop_exhausted` is a recoverable interruption, not success. The user may
continue the conversation to resume from the persisted conversation history and
tool evidence.

## Safety Boundary

The runtime still supports an explicit fuse via:

```text
PEER_AGENT_AGENT_LOOP_MAX_TURNS=<positive integer>
```

Unset, `0`, `unbounded`, `unlimited`, and `infinite` mean no local turn cap.

This preserves an operational emergency brake without allowing a hidden default
budget to masquerade as task completion.

## Alignment

This keeps the core chain intact:

```text
Model intent -> Tool Call -> PermissionGrant -> Evidence -> Model terminal response
```

The loop does not infer task completion from local counters. Local counters only
diagnose or interrupt execution when explicitly configured.

