# Conversation Delete Cascades to Goal Plans

创建时间：2026-06-18
最后更新：2026-11-15（收窄硬删除适用范围至经典空闲对话，补充 0.1.0 资源锁/未知义务边界）

## Status

Accepted（2026-06-18 本地实施；2026-11-15 补充 0.1.0 适用边界）。

## Problem

Goal mode persists each plan as a durable Evidence/artifact in the goal-plan
store (`index.jsonl` + `${planId}.json`, see ADR for the goal-plan store). Each
plan embeds the owning `conversationId` as a foreign key so plans can be listed
per conversation (`listPlansByConversation`).

Deleting a conversation only cleans up the conversation itself
(`conversation-store.deleteConversation`: drop the index row + delete the
message file). It does not touch the goal-plan store. As a result, every plan
that belonged to the deleted conversation becomes orphaned on disk: the owning
conversation no longer exists, but the plan files and their index rows remain.
They can never again be reached through `listPlansByConversation` (the
conversation is gone), yet they keep occupying storage and still surface in the
"all plans" view.

The goal-plan store originally left this gap explicit ("conversation deletion
vs. plan lifecycle cascade is not yet defined"). This document records the
decision that closes it.

Linking the two store lifecycles crosses a storage boundary and defines a new
cross-store lifecycle contract, which is an A-level change under the governance
baseline.

## Decision

Deleting a conversation **hard-deletes every goal plan owned by that
conversation**. When a conversation is removed, all plans whose embedded
`conversationId` matches are removed from the goal-plan index and their plan
files are unlinked from disk. No orphan plans are retained.

The cascade is **orchestrated at the IPC handler layer** (`main.mjs`,
`conversations:delete`), which already holds both store instances in the same
scope. The handler first deletes the conversation, then asks the goal-plan store
to delete that conversation's plans.

`conversation-store` does **not** import or depend on `goal-plan-store`, and
vice versa. The two stores stay independent and unit-testable; only the IPC
composition layer knows about both. This preserves the existing seam where each
store depends only on `fs`/`path`/`crypto` and never imports Electron.

## Boundaries

- New store capability: `goal-plan-store` gains
  `deletePlanByConversation(conversationId)`. It atomically rewrites the index
  with the matching plans removed, unlinks each removed plan file, fires the
  existing `onChange` Seam (so `goalPlans:changed` is broadcast once), and
  returns the remaining plan list. A `null`/empty `conversationId` is a no-op
  that deletes nothing.
- IPC orchestration only: `main.mjs` `conversations:delete` calls
  `conversationStore.deleteConversation(id)` then
  `goalPlanStore.deletePlanByConversation(id)`. No reverse store dependency is
  introduced.
- Change notification reuses the goal-plan store `onChange` Seam; the renderer
  goal-plan panel refreshes through the same `goalPlans:changed` broadcast it
  already listens to. No new cross-process payload type is added.
- Hard delete is intentional under decision A: plans tied to a deleted
  conversation are not preserved as standalone Evidence. Plans not owned by any
  conversation (e.g. created without a `conversationId`) are unaffected because
  they do not match the deleted conversation's id.
- **0.1.0 Project Bot & Resource-Settlement Scope (aligned 2026-11-15):** Direct hard-unlinking of `${planId}.json` applies **only** to idle standalone classic chats with no unsettled resource claims, `RetainedUnknown` records, or unconfirmed stop/control obligations. In Project Bot mode ([ADR 80](80-project-agent-delegation-model.md)) or whenever any linked plan holds active execution, active/reconciling claims ([ADR 116](116-session-control-and-resource-settlement.md)), `RetainedUnknown` history ([ADR 126](126-execution-resource-claim-closure-and-unknown-retention.md) / [ADR 127](127-unknown-outcome-reconciliation-and-delegated-resolution.md)), or pending obligations ([ADR 120](120-runtime-facts-disposition-and-resource-wait.md) / [ADR 124](124-legacy-stop-obligation-controlled-resolution.md)), deletion must first traverse Session Control settlement / controlled closure or fail closed rather than silently unlinking active claim/unknown evidence.

## Consequences

- Deleting a conversation no longer leaves orphan plan files or orphan index
  rows; the "all plans" view stays consistent with the surviving conversations.
- The deletion is irreversible for plans, consistent with conversation deletion
  itself being a hard delete. There is no undo and no recycle bin for cascaded
  plans.
- Because the cascade lives in the IPC handler, any future non-IPC caller of
  `conversationStore.deleteConversation` would bypass the cascade. The handler
  is the single governed entry point; new conversation-deletion paths must route
  through the same orchestration.

## Tests

Unit coverage on the goal-plan store asserts that `deletePlanByConversation`:

- removes only the plans owned by the target conversation and leaves plans of
  other conversations intact (multi-plan / multi-conversation case);
- unlinks the removed plan files from disk and drops their index rows;
- is a safe no-op for an empty/`null` conversation id and for a conversation id
  that owns no plans (orphan / empty case);
- fires the `onChange` notification so the broadcast still happens.
