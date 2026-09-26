---
type: "[[task]]"
id: TASK-0173
aliases: ["TASK-0173"]
title: "Fix phase-activity title truncation — scoped feed rows land the title in the id column"
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
related: ["[[TASK-0129]]"]
tests: []
---

# TASK-0173 — phase-activity title truncation

On a phase-specific overview page, the "Activity in this phase" rows truncate the title with an ellipsis far too early (user report 2026-07-20). Root cause: `.ov-feed-list li` uses a fixed five-column grid (`88px 64px 90px 1fr auto` — date, type, id, title, tag), but `buildScopedTiles` renders scoped activity rows with only three cells (date, optional type, title) and no id cell. Grid auto-placement therefore drops the title into the fixed 90px *id* column while the `1fr` title column sits empty, clipping the title at ~90px.

Fix: give the scoped activity list its own column template (`88px 64px 1fr` — date, type, title) via a modifier class, and always emit the type cell (empty placeholder when a record has no type) so placement is deterministic regardless of which rows carry a type.

Verification: CDP on a phase detail page — the "Activity in this phase" title spans the full remaining row width (title cell width ≫ 90px; no early ellipsis on a long title).

## Verification

CDP on a phase detail page (PHASE-001): the "Activity in this phase" list carries `.ov-feed-scoped`; the `.ov-feed-title` cell measures 377px (was clamped to the 90px id column) and a long title now fills the full remaining row width, ellipsizing only at the real edge. `tsc` clean; build OK.
