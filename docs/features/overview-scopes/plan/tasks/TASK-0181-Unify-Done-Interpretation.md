---
type: "[[task]]"
id: TASK-0181
aliases: ["TASK-0181"]
title: "Unify done interpretation — phase boxes use the same per-type done sets as the hero counts"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: []
parent: "FEAT-0023"
effort: ""
due: ""
depends: ["[[TASK-0176]]"]
blocks: []
related: []
tests: ["[[TST-0012]]"]
---

# TASK-0181 — unify done interpretation

The phase progress boxes (`_status_bucket` / `phase_buckets`) used one broad, type-agnostic union set `DONE_PHASE_BUCKET`, while the hero/summary counts use per-type sets (`DONE_FEAT`/`DONE_TASK`/`DONE_REQ`). They contain different statuses, so a filled box and the summary count could disagree (e.g. a task with `accepted`/`passing`/`complete`/`released` renders done in a box but not-done in the count). User report 2026-07-21: "docs completion is interpreted differently … in the rendering of the little boxes."

Fix: route the boxes through the same per-type done sets the hero uses — a single `_is_done(record)` keyed on the note type (`DONE_BY_TYPE`: feature→DONE_FEAT, task→DONE_TASK, requirement→DONE_REQ, issue/risk/test/change/phase → their terminal sets, union fallback). `_status_bucket` and `phase_buckets` call `_is_done`; `DONE_PHASE_BUCKET` is removed. Boxes and counts now agree by construction (a box is filled iff the item counts done).

Verification: unit test that the phase-bucket/drill-down `bucket` matches the hero done-classification for the same item across types (including a status that used to diverge); project-os-cockpit boxes unchanged (its statuses don't hit the old mismatch).
