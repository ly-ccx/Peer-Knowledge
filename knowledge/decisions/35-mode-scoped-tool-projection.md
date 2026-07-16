# Mode-Scoped Tool Projection

## Status

Implemented locally on 2026-06-18.

Updated on 2026-07-04 to reflect the later three-mode split (`chat` / `plan` / `goal`) and the runner-only `explorer` profile.

## Problem

Conversation mode was originally `chat` / `goal` and later split into `chat` / `plan` / `goal`; the Runner also uses an internal `explorer` profile for read-only subagents. Mode is a per-turn runtime fact that
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

- Goal/Plan ledger tools (`goal_create_plan`, `goal_update_task`, `goal_get_plan`, `request_explorer`) declare `availableInModes: ['plan', 'goal']`. They are projected in Plan mode for plan-before-execute governance and in Goal mode for self-driven execution tracking.
- Explorer mode is a stricter internal profile. Only tools explicitly declaring `explorer` are projected there; current allowlist is `read_file` and `search_files`.
- Tools without an `availableInModes` declaration are available by default in normal user-facing modes (`chat` / `plan` / `goal`) for backward compatibility, but are not available in `explorer`.

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
the host. For explorer mode, explicit declaration is mandatory because the
profile is intended to remain read-only.

## Boundaries

- The Runtime Projection is now the **primary** enforcement of mode-scoped
  capability exposure. The execution-layer `toolContext.mode` gate remains as a
  second line of defense (defense in depth). It continues to govern Plan
  pre-approval side-effect blocking and Goal pre-act guards such as workspace /
  outOfScope writes and irreversible action confirmation. It is not removed.
- The default (non-runtime) registry and `DEFAULT_RUNTIME_PROJECTION` keep their
  current behavior; mode scoping applies on the chat send path where a turn mode
  exists. Callers that pass no mode get the all-modes view for backward
  compatibility.
- No new cross-process payload is introduced. Mode already crosses IPC on the
  send path; this change only forwards the existing value into the projection.
- The prompt-level `L6_MODE_REMINDER` is unchanged and still describes the
  active mode to the model. It is now backed by real capability scoping rather
  than standing alone.

## Consequences

- In chat mode the model no longer sees `goal_create_plan` /
  `goal_update_task` / `goal_get_plan` / `request_explorer`; it cannot call
  them. The reported behavior (goal plan created during a chat-mode turn) can no
  longer occur.
- In plan and goal modes, the goal/plan ledger tools are projected. Plan still
  has the pre-approval execution gate; Goal uses the self-driven contract and
  pre-act guards.
- In explorer mode, the materialized tool list is exactly `read_file` and
  `search_files`; write tools, shell, goal tools, MCP mutation tools, and browser
  side-effect tools are mode-excluded.
- Future capabilities that should be mode-specific declare `availableInModes`
  on their tool definition and require no host changes.

## Tests

`tool-registry.test.mjs` covers:

- goal/plan ledger tools are present in the runtime projection / materialized
  tools when `mode = 'plan'` or `mode = 'goal'`;
- goal tools are absent from the materialized tools when `mode = 'chat'`
  (and present capabilities are marked `mode_excluded` in the projection);
- explorer mode materializes only `read_file` and `search_files`;
- write and goal capabilities are marked `mode_excluded` in explorer mode;
- non-goal tools (e.g. legacy local tools) remain available in normal user-facing modes;
- omitting `mode` preserves the all-modes view (backward compatibility).
