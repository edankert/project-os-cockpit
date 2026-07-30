---
type: "[[feature]]"
id: FEAT-0048
aliases: ["FEAT-0048"]
title: "Changes on the overview — recent in the history band, the archive collapsed beneath"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
goal: "CHG notes join the overview's history band, where Activity and Commits already answer 'what happened'. Recent changes render expanded; the existing week/month buckets collapse underneath, so the archive travels with them instead of being left behind in Library."
requirements: []
tasks: ["[[TASK-0239-Changes-Payload]]", "[[TASK-0240-Changes-Tile]]"]
release: ""
related: ["[[PHASE-010-Surface-Ownership]]", "[[TASK-0040-Changes-Hybrid-Buckets]]", "[[FEAT-0050-Library-Reduction]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# FEAT-0048 — Changes on the overview

## Goal

The overview's lower half is already the history band: `buildActivityTile` (weekly sparkbar of note churn) then `buildCommitsTile` (git). CHG notes are the missing middle grain — coarser than a commit, finer than a week's churn count, and the only one of the three that carries a written reason.

## Scope

- A Changes tile in the history band, after Activity and before or after Commits.
- Recent changes expanded by default; the existing hybrid buckets (current week / last week / earlier this month / past months) collapsed beneath them.
- `_changes_subgroups` relocates rather than dies — the bucketing built by [[TASK-0039]]/[[TASK-0040]]/[[TASK-0041]] is load-bearing for a type that accumulates without limit.

## Out of Scope

- **Routing the archive through the Docs tree.** Considered and rejected by the owner: `changes` stays in `DOC_TREE_EXCLUDED_ROOTS` and the archive stays on the surface that owns it. Collapsed-under-recent, not relocated-to-files.
- Merging CHG rows into the Commits tile. Different records — a commit is what git saw, a CHG is what someone decided was worth writing down.
- Phase-scoped changes on the drill-down. Project scope only for now; the scoped overview already carries its own record column.

## Acceptance

- Recent changes are readable on the overview without opening Library.
- Every bucket Library rendered is still reachable, collapsed, from the same tile.
- Bucket structure and labels are unchanged — same code, new home.

## Links

- Tasks: [[TASK-0239-Changes-Payload]], [[TASK-0240-Changes-Tile]]
- Prior art: [[TASK-0040-Changes-Hybrid-Buckets]], [[TASK-0041-Sparse-Month-Flat]]
## Independent review — 2026-07-30, approved

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea`; no access to the authoring session's reasoning.

`test_the_changes_split_is_a_partition` is the load-bearing assertion and it is not tautological: `total` comes from `len(records)` while `seen` is summed over `recent` + buckets + subgroups, and the chain also compares against `len(list(notes_by_type("change")))`. Dropping one item from the open bucket's contribution to `recent` fails it. Rewriting `total` to be derived from the split does *not* make it pass silently, because the third term is independent of the payload. Measured live: total 98, recent 6, buckets partitioning the remaining 92.

The new `GET /api/cockpit/changes` endpoint is additive and the degradation claim (older sidecar → the tile removes itself rather than rendering an empty box) is recorded as observed rather than assumed, which is the right standard.

No findings against this feature. Note for context: the reduction that accompanies it emptied a different overview surface — see [[REQ-0025]] — but nothing in FEAT-0048's own scope is affected.
