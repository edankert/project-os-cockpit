---
type: "[[feature]]"
id: FEAT-0049
aliases: ["FEAT-0049"]
title: "The review desk gains its record — every acceptance test, and every reviewed item"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
goal: "The desk is currently queue-only: it shows what is waiting and, when the queue empties, nothing. It gains two registers beneath the queue — the full acceptance-test register, and the reviewed items whose verdicts already live in note frontmatter — so the surface still says something when there is nothing to decide."
requirements: []
tasks: ["[[TASK-0241-Tests-Register]]", "[[TASK-0242-Reviewed-Register]]"]
release: ""
related: ["[[PHASE-010-Surface-Ownership]]", "[[FEAT-0041-Review-Desk]]", "[[ISS-0063-Dead-Stat-Tiles]]", "[[FEAT-0050-Library-Reduction]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# FEAT-0049 — The review desk as record

## Goal

Two gaps, same shape: the desk shows the transient and hides the durable.

**Tests.** The desk already has a "Test runs" group, but `_is_manual_test` gates it to manual tests at `ready` (`cockpit.py:1662-1669`) — a queue slice of about four rows out of 21. The register lives only in Library, and the overview's Tests tile navigates nowhere ([[ISS-0063]]).

**Reviewed items.** The desk shows a `Reviewed · N` tally with an outcome breakdown (`renderer.ts:3896`), derived from `store.outcome_counts()`. The items behind those counts are never rendered — `review_queue_payload` only ever emits `open_requests()`. And the store is the weaker of two sources: `_MAX_REQUESTS = 200` is a sliding window applied on every save (`review.py:91`), so resolved requests age out silently. **62 notes in this repo carry a non-empty `review_verdict`**, stamped with `reviewed_by` and `review_date` by `note_writes.py:338-340`. Nothing in the UI lists them.

A further six notes declare `review_verdict: ""`. Those are *not* reviewed items and must not list — an empty verdict is the absence of one, and counting them would inflate the register with exactly the unearned verification ADR-0010 exists to prevent.

The notes are the right source, and `review.py`'s own opening doctrine says so: durable verdicts live in notes, transient pending-ness lives in the store.

## Scope

- A **Tests** register on the desk: every `[[test]]` note with status, `last_verified`, and staleness — not just the runnable slice.
- A **Reviewed** register sourced from note frontmatter (`review_verdict` / `reviewed_by` / `review_date`), most recent first.
- The overview's Tests stat tile navigates to `~review`.
- The store's outcome tally stays exactly where it is — it is the ADR-0007 measurement, and it answers a different question ("did review change anything") than a list of reviewed items.

## Out of Scope

- **Changing the per-scope Verification panel** ([[TASK-0211]]). "Does *this* feature pass" and "what do we verify at all" are different questions; the panel keeps the first, the register adds the second.
- Making the desk a test *runner* for automated tests. `passing`/`failing` are written by the runner from an exit code (ADR-0010) and the desk must not learn to assert them.
- Backfilling `review_verdict` onto the notes that lack it. The validator already warns on those with an ADR-0011 deadline of 2026-10-23; the register will simply not list them, which is accurate.

## Acceptance

- The register lists every test note in the corpus, and the count matches `index.notes_by_type("test")`.
- The reviewed register lists items sourced from note frontmatter, so nothing ages out of it.
- The desk with an empty queue is still worth opening.
- The Tests tile navigates to `~review`.

## Links

- Parent surface: [[FEAT-0041-Review-Desk]]
- Tasks: [[TASK-0241-Tests-Register]], [[TASK-0242-Reviewed-Register]]
