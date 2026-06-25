# Mode-Scoped Tool Projection

## Status

Implemented locally on 2026-06-18.

## Problem

Conversation mode (`chat` / `goal`) is a per-conversation runtime fact that
flows through `chatSend → IPC → mode-source` into System Context as the
`L6_MODE_REMINDER` layer (see Goal mode design and ADR 19). Before this change,
mode influenced **only** two things on the send path
(`llm-chat-service.sendMessage`):

1. `toolContext.mode = mode` — consumed by the execution-layer goal gate.
2. `buildSystemContext(..., { mode })` — rendered as a prompt reminder.

Mode never reached the Runtime Projection. `createRuntimeToolRegistry`
unconditionally spreads `...GOAL_TOOL_DEFINITIONS`, and
`createRuntimeProjectionFromToolRegistry` / `createProjectedToolRegistry`
filtered capabilities **only** by `capability.health`. `buildRuntimeTools`
did not even accept a `mode` argument.

As a result, the goal tools (`goal_create_plan`, `goal_update_task`,
`goal_get_plan`) were projected to the model in **every** mode, including
`chat`. In chat mode the only thing discouraging their use was the prompt text
"goal mode only" plus the execution-layer gate. But `goal_create_plan` carries
`permissionPolicy.kind = 'goal-create'`, projected as `L0_inert` (no side
effects), so the execution gate does not block it. The model could — and did —
call `goal_create_plan` while the user was in chat mode.

This violates the governance baseline rule: *"Do not rely on prompt
instructions as the only enforcement for capability limits."* Mode-based
capability scoping must be enforced at the Runtime Projection seam, not only in
the system prompt and not only at execution time.

## Decision

Tool exposure is **scoped by conversation mode at the Runtime Projection
layer**. A tool may declare the modes in which it is available; the projection
excludes any tool not available in the current mode before the provider tool
list is materialized.

- Goal tools declare `availableInModes: ['goal']`. They are projected only when
  the turn's mode is `goal`.
- Tools without an `availableInModes` declaration are available in all modes
  (unchanged behavior for legacy local tools, interaction tools, and MCP
  tools).

The mode is threaded `sendMessage(mode) → buildRuntimeTools(mode) →
createRuntimeToolProjection(mode) → createRuntimeProjectionFromToolRegistry(mode)`.

## Mechanism (reuse existing health Seam)

Mode exclusion reuses the existing capability-`health` filter instead of adding
a parallel filtering path:

- `createRuntimeProjectionFromToolRegistry(registry, { mode })` evaluates each
  tool's `availableInModes` during `manifestFromTool`. A tool excluded by mode
  is emitted with `health: 'mode_excluded'`.
- `isAvailable` already gates `createProjectedToolRegistry`; `mode_excluded`
  is not in the available set, so the tool drops out of the materialized
  OpenAI/Anthropic tool list automatically.

This keeps a single projection→materialization path and avoids `if (name ===
'goal_...')` branches in the central chat host. The mode predicate is
declarative data on the tool definition (depth behind a small interface), so new
mode-scoped tools opt in by declaring `availableInModes` rather than by editing
the host.

## Boundaries

- The Runtime Projection is now the **primary** enforcement of mode-scoped
  capability exposure. The execution-layer `toolContext.mode` gate remains as a
  second line of defense (defense in depth) and continues to govern the goal
  "plan-before-side-effects" rule *within* goal mode. It is not removed.
- The default (non-runtime) registry and `DEFAULT_RUNTIME_PROJECTION` keep their
  current behavior; mode scoping applies on the chat send path where a turn mode
  exists. Callers that pass no mode get the all-modes view (no goal tools are in
  the default legacy registry, so this is a no-op there).
- No new cross-process payload is introduced. Mode already crosses IPC on the
  send path; this change only forwards the existing value into the projection.
- The prompt-level `L6_MODE_REMINDER` is unchanged and still describes the
  active mode to the model. It is now backed by real capability scoping rather
  than standing alone.

## Consequences

- In chat mode the model no longer sees `goal_create_plan` /
  `goal_update_task` / `goal_get_plan`; it cannot call them. The reported
  behavior (goal plan created during a chat-mode turn) can no longer occur.
- In goal mode the goal tools are projected exactly as before.
- Future capabilities that should be mode-specific declare `availableInModes`
  on their tool definition and require no host changes.

## Tests

`tool-registry.test.mjs` covers:

- goal tools are present in the runtime projection / materialized tools when
  `mode = 'goal'`;
- goal tools are absent from the materialized tools when `mode = 'chat'`
  (and present capabilities are marked `mode_excluded` in the projection);
- non-goal tools (e.g. legacy local tools) remain available in both modes;
- omitting `mode` preserves the all-modes view (backward compatibility).
