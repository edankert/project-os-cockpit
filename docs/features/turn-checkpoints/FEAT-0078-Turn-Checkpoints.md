---
type: "[[feature]]"
id: FEAT-0078
aliases: ["FEAT-0078"]
title: "Turn checkpoints — the workspace captured per agent turn, so a wrong judgment is rewound to the turn before it instead of reverted whole"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
source: ["Comparison against t3.codes, 2026-08-05: CheckpointStore captures workspace state per turn to hidden git refs, with CheckpointDiffQuery for computed diffs and restore"]
goal: "Capture the workspace to a hidden ref at each agent turn, expose the turn timeline with its diffs, and make restoring to a chosen turn a recorded, human-owned action — so an unattended worker's compounding error costs one turn rather than a session."
requirements: []
tasks:
  - "[[TASK-0335-Capture-Per-Turn]]"
  - "[[TASK-0336-The-Turn-Timeline]]"
  - "[[TASK-0337-Restore-As-A-Recorded-Action]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[RISK-0006-The-Unattended-Worker]]", "[[FEAT-0074-The-Standing-Worker]]", "[[FEAT-0055-Git-Assist]]"]

---

# Turn checkpoints

## Goal

[[RISK-0006]]'s first hazard is **compounding judgment**: a wrong assumption at hour one is the context of every decision after it, and unattended wrongness compounds until the digest is read. Today the only unit of undo is the close-out commit — the whole session's work, or nothing.

T3 Code solved this with per-turn capture to hidden git refs: each user-to-assistant cycle leaves a restorable point, diffable against its neighbours. Adopting it turns "the worker went wrong somewhere in three hours" from an archaeology problem into a slider.

## Why this belongs to PHASE-027 rather than PHASE-021

[[FEAT-0055]] is about *publishing deliberately* — commits at close-out, pushes by a person. Checkpoints are the opposite concern: **pre-commit, private, and disposable**, existing only so a supervisor can rewind. They must not appear in history, must not survive a close-out, and must never be pushed. Filing them under git assist would blur exactly the line FEAT-0055 drew.

## Out of Scope

- **Provider conversation rollback.** Restoring the workspace does not un-say what an agent said; the checkpoint is filesystem state, and the note must say so wherever it is offered.
- **Checkpoints as a record.** They are ephemeral supervision state, pruned by age and count — the record is the notes and the close-out commit, unchanged.
- **Automatic restore.** A worker never rewinds itself: that is a judgment, and judgments belong to the principal ([[ADR-0009]]).

## Acceptance

- [x] A turn boundary captures the working tree — **untracked files included**, since an agent's damage is often a file it added ([[TASK-0335]])
- [x] Refs live outside `refs/heads` and every push path, pruned by count with the limit stated where it is set
- [x] The real index is untouched — capture runs against a temporary `GIT_INDEX_FILE`, so a safety net is not a second actor
- [x] A session's turns list with files grouped by kind, **sharing [[ISS-0096]]'s implementation** rather than growing a second one ([[TASK-0336]])
- [x] Turns are newest-first even within one second — the order lives in the ref name, because `creatordate` ties
- [x] Restore is **principal-owned**: a worker can never rewind itself, and an unattributed restore is refused ([[TASK-0337]], [[ADR-0009]])
- [x] A restore captures the state it replaces first, so it is never the end of a road

## Verification

`tests/test_checkpoints.py` — 16 tests.

**Built ahead of the rest of [[PHASE-027]] because it mitigates [[RISK-0006]] rather than being part of it.** The risk's first hazard is compounding judgment; the only undo unit today is the close-out commit — the whole session or nothing. This makes the unit a turn. It carries no requirements, so nothing here waited on the phase's approvals.

One bug worth the record: the timeline first rendered **reversed**, because git's `creatordate` has second granularity and two checkpoints in one second tie. Every turn's changes were attributed to its neighbour — for a "where did it go wrong" slider, out-of-order turns point confidently at the wrong place. The guard writes four checkpoints as fast as the loop runs.
