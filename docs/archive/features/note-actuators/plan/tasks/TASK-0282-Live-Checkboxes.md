---
type: "[[task]]"
id: TASK-0282
aliases: ["TASK-0282"]
title: "Criteria checkboxes tick from the note view, with an inline evidence prompt and the reconcile form behind a menu"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
parent: "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"
effort: M
depends: ["[[TASK-0281-The-Action-Row]]"]
blocks: []
related: ["[[TASK-0279-The-Tick-Path]]"]
tests: []
---

# Live checkboxes

## Definition of Done

- [x] Unticked boxes in criteria sections are clickable only where the server reports the tick action legal for this note.
- [x] Click opens an inline evidence field ("what shows this is met?"); submit calls the tick path; the row re-renders from the file.
- [x] Reconcile (`[~]` + reason) reachable from the same affordance's menu.
- [x] A stale-mtime refusal surfaces as "note changed — reloaded", never as silence.

## Done 2026-08-10

An unticked box **in a criteria section** opens an inline evidence field; submit calls `POST /api/notes/tick` and the note re-renders from the file. Reconcile shares the affordance and writes the `[~]` form with its reason.

**Only criteria are intercepted.** `CRITERIA_HEADINGS` mirrors the validator's own distinction — REQ-BOXES reads "Acceptance", PHASE-BOXES reads "Exit Criteria" and deliberately requires the heading because a phase note carries unrelated checklists. Getting that wrong in the other direction would demand evidence for a step in somebody's Steps list, which would make the affordance a nuisance everywhere it appears. Plain checkboxes keep FEAT-0011's toggle.

**A refusal is never silence.** A stale mtime means somebody else's edit is on disk, so it says *"note changed — reloaded"* and re-reads. Silence after a click that appeared to work is the worst of the three outcomes: the reader believes the criterion is ticked and the file says otherwise.

**The evidence is required client-side too**, not because the server would accept an empty one — it refuses — but because a round trip to learn that is worse than a placeholder that says so.
