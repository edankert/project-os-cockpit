---
type: "[[task]]"
id: TASK-0176
aliases: ["TASK-0176"]
title: "Overview progress counts terminal-resolved items — retired requirements + superseded features are complete"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
parent: "FEAT-0023"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0128]]"]
tests: ["[[TST-0012]]"]
---

# TASK-0176 — progress counts retired/superseded as complete

The overview progress never reaches 100% for a phase that contains terminal-resolved items (user report 2026-07-20: stuck at 98%). The completion sets in `cockpit.py` omit `retired` and `superseded`: `DONE_REQ` lacks `retired`, and `DONE_FEAT` + `DONE_PHASE_BUCKET` lack `superseded`. So a retired requirement (e.g. REQ-0009/0010/0011) or a superseded feature (e.g. FEAT-0004) is bucketed as backlog and counts against completion even though it is a terminal, resolved outcome.

Fix: add `retired` and `superseded` to `DONE_REQ`, `DONE_FEAT`, and `DONE_PHASE_BUCKET` (a note that was fulfilled-then-retired, or replaced by a successor, is done for progress purposes — the same rationale that already includes `cancelled` in the phase bucket).

Verification: unit test that a scope with a retired requirement and a superseded feature reports 100% done (hero counts + phase bucket), and that the PHASE-002 scoped stats reach 100%.

## Verification

`DONE_FEAT`, `DONE_REQ`, and `DONE_PHASE_BUCKET` now include `superseded`/`retired`. Test `test_retired_and_superseded_count_as_done` (hero + phase bucket + drill-down incl. loose items) — passes with the fix, fails without it. Real data: PHASE-002 now reports requirements 9/9, features 2/2, and every superseded feature / retired requirement buckets as `done` (was ~98%). Full suite 221 passed. While verifying, also repaired two frontmatter corruptions from earlier edits this session that had broken `Index.build` parsing — a stray control character in the CHG-20260720-Usage-Freshness title and a malformed `tasks:` list in FEAT-0007; the index now builds cleanly (417 records, no parse-failed warnings).
