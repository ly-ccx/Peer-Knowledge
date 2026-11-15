# Mode-Scoped Tool Projection

## Status

Implemented locally on 2026-06-18.

Updated on 2026-07-04 to reflect the later three-mode split (`chat` / `plan` / `goal`) and the runner-only `explorer` profile.

最后更新：2026-11-15（跨 ADR 对齐：演进为 `(mode × role × host × botAdmission)` 四维投影矩阵，补全 `project_agent` / `explorer` 6 工具 / `verifier` 白名单与 [System Context 架构](../architecture/19-system-prompt-context-architecture.md) 链接）

## Problem

Conversation mode was originally `chat` / `goal` and later split into `chat` / `plan` / `goal`; the Runner also uses an internal `explorer` profile for read-only subagents. Mode is a per-turn runtime fact that
flows through `chatSend → IPC → mode-source` into System Context as the
`L6_MODE_REMINDER` layer (see Goal mode design and [ADR 19 / System Context Architecture](../architecture/19-system-prompt-context-architecture.md)). Before this change,
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
- **2026-11-15 对齐扩展（四维投影与严格白名单）**：在 Project Bot 与多宿主运行期（参见 [ADR 80](80-project-agent-delegation-model.md)、[ADR 85](85-project-agent-hosts-inputs-and-surfaces.md)、[ADR 90](90-local-image-capability-and-product-review.md)、[ADR 92](92-scoped-permission-inheritance.md)、[ADR 101](101-bot-owned-access-policy.md)、[ADR 106](106-readonly-git-and-delegation-capability-admission.md)、[ADR 111](111-project-agent-duplex-supervision-and-continuity.md)），Runtime Projection 已由单一 `mode` 过滤演进为 **`(mode × role × host × botAdmission)`** 四维共同决定，遵循同样单链机制：
  - **`project_agent`（主 Bot，严格白名单）**：仅投影只读本机工具（`list_files`、`read_file`、`search_files`、`batch_search`、`goal_get_plan`、`view_image`、`git_query`）、项目协调/委派/正式回复工具（见 [project-agent-delegation-runtime.md §3](../architecture/project-agent-delegation-runtime.md) 与 ADR 111）、`request_user_input` 与记忆工具（`memory_search`、`memory_remember`、`memory_forget`、`memory_explain`，ADR 81）；明确不投影任何写文件、任意 shell、`goal_create_plan` / `goal_update_task` / `request_explorer`、`web_fetch`、外网搜索或 `browser_*` / `browser_external_*`。
  - **`explorer`（只读探查，严格白名单）**：2026-07-04 初版仅允许 `read_file` 与 `search_files`；对齐后续 ADR 90 / 106 / 桌面-CLI 对等基线后，完整 6 工具只读白名单收敛为 `read_file`、`list_files`、`search_files`、`batch_search`、`view_image`（ADR 90）、`git_query`（ADR 106）；写工具、shell、goal 工具与浏览器动作一律 `mode_excluded`（另特定配置允许按 `desktop-cli-local-capability-parity.md` §5 决定 `web_fetch`）。
  - **`verifier`（独立核验，ADR 93 / 103 / 106）**：只投影只读检视（含结构化 `git_query`、`view_image` 及受约束核验/测试检查）与证据输入，不开放源码修改或通用委派，且无工具纯视觉/证据核验路径可收窄至零工具报告。
- Tools without an `availableInModes` declaration are available by default in normal user-facing modes (`chat` / `plan` / `goal`) for backward compatibility, but are **not** available in `explorer` or `project_agent`（strict allowlist profiles）.

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
- In historical initial `explorer` mode (2026-07-04), the materialized tool list was `read_file` and `search_files` (later expanded to the 6 read-only tools `read_file` / `list_files` / `search_files` / `batch_search` / `view_image` / `git_query` per ADR 90 / 106); write tools, shell, goal tools, MCP mutation tools, and browser side-effect tools remain mode-excluded (and `project_agent` / `verifier` enforce strict role allowlists over `(mode × role × host × botAdmission)`).
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
