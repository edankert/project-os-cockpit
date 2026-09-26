---
type: "[[change]]"
id: CHG-20260810-Actions-On-The-Note
title: "A note shows the actions it owes, and a criterion takes evidence rather than a click"
status: merged
reviewed_by: ""
review_date: ""
review_verdict: ""
date: 2026-08-10
owner: user:edwin
component: [desktop-renderer]
related: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[DES-0005-The-Actuator-Grammar]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Actions on the note

## What changed

Two affordances, both on the note itself — DES-0005's placement, since the left pane is a selection list and the right a description.

**The actuator row.** A quiet row under the metadata strip, drawn from `GET /api/notes/actions`. A `draft` requirement offers Approve · Decline; a `triage` issue offers Accept · Defer · Decline. **Absent, not empty, when nothing is owed** — most notes owe nothing most of the time, and a permanent empty row on every note would be a reminder that there is nothing to do.

**Criteria take evidence.** An unticked box under an Acceptance or Exit Criteria heading opens an inline field — *"what shows this is met?"* — and writes the `- [x] … — evidence: … (actor, date)` form the validator reads. Reconcile shares the affordance for the `[~]` form.

Only *criteria* are intercepted. `CRITERIA_HEADINGS` mirrors the validator's own distinction, so a step in somebody's Steps list still toggles as before rather than demanding a justification.

## The vocabulary tried to come back through a class name

The first cut styled the affirmative button with `action.verb === 'Approve' || action.verb === 'Accept'`. That is the renderer knowing the verbs again — [[ISS-0023]] arriving one class name at a time.

Tone now comes from `confirm`: a forward move reads affirmative, a terminal one reads as something to pause over, and **which moves are terminal is `CONFIRM_ACTIONS`' decision**, server-side. The guard was widened to catch verbs as well as statuses once the code could pass it.

## Nothing is optimistic

Both paths re-read the note from disk after a write. The tests assert the **absence of a local mutation**, not the presence of a refetch — the failure mode being guarded is showing a state the file does not have.

A refusal is never silence: a stale mtime says *"note changed — reloaded"* and re-reads, because somebody else's edit is on disk and a field that looks like it worked is the worst of the three outcomes.

## Requirements advanced

[[REQ-0026]] → `implemented`, all four criteria ticked with evidence. [[REQ-0027]] was advanced with FEAT-0059, its mtime criterion **reconciled rather than ticked**.

## Paths

- `desktop/src/renderer/renderer.ts` — `mountActuatorRow`, `performNoteAction`, `isCriterionBox`, `openTickPrompt`, `submitTick`
- `desktop/src/renderer/renderer.css` — `.note-actions`, `.tick-prompt`
- `tests/test_human_transitions.py` — 34 assertions across FEAT-0059 and FEAT-0060

## Restart required

Mode 3 is a built bundle. Live after the desktop app restarts.
