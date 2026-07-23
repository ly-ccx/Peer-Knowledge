# Tool Call Duration Accounting

- 创建时间：2026-07-23
- 最后更新：2026-07-23

## Status

Implemented locally on 2026-07-23.

## Problem

The assistant message already persists `durationMs`, but that value is the whole turn wall-clock duration. It cannot explain how much time local tools consumed, and presenting it near tool activity can make users assume it is pure tool or model time.

Tool calls currently cross the governed runtime chain and emit structured `tool-call` / `tool-result` events, but those events and persisted tool segments carry no lifecycle timestamps.

## Decision

Treat tool timing as factual execution metadata produced by the desktop main process, not as a renderer estimate.

Each tool-call segment may carry three optional epoch-millisecond fields:

- `startedAtMs`: captured immediately before the main process emits `tool-call` and begins authorization/execution;
- `endedAtMs`: captured when the main process has a terminal result, including denial, cancellation, failure, or success;
- `durationMs`: `max(0, endedAtMs - startedAtMs)`.

The fields travel on the existing structured tool events and existing message `segments`; no separate execution path or renderer-owned timing truth is introduced. They are optional so histories written by older versions remain valid.

## Aggregation Semantics

A single tool card displays its own `durationMs`.

The turn-level “tool time” is wall-clock occupancy, not the sum of individual durations. The renderer takes every valid completed interval `[startedAtMs, endedAtMs]`, sorts intervals by start, merges overlaps, and sums the merged lengths. Therefore parallel calls are counted once rather than double-counted.

When an older segment has only `durationMs`, it can display a per-call duration but is excluded from wall-clock aggregation because its placement relative to other calls is unknowable. Running calls without an end timestamp are also excluded from the completed summary.

## Boundaries

This is an A-level metadata extension because tool lifecycle facts cross main/IPC/persistence boundaries. It does not alter capability projection, permission decisions, execution routing, or Evidence production. The desktop remains the timing authority; renderer only formats and aggregates persisted facts.

## Compatibility

All new fields are optional. Loading old histories leaves them undefined and retains existing rendering. Stream reattachment and persistence must preserve fields when present.

## Verification

Focused tests cover main-process lifecycle timestamps, serial and overlapping interval aggregation, exceptional terminal results, stream merge preservation, and old history without timing metadata.
