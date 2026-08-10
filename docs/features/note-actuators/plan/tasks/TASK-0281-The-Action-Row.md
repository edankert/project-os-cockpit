---
type: "[[task]]"
id: TASK-0281
aliases: ["TASK-0281"]
title: "The action row under the note title — drawn from the server's answer, confirming terminal moves, explaining disabled ones"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
parent: "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"
effort: M
depends: []
blocks: []
related: ["[[DES-0005-The-Actuator-Grammar]]"]
tests: []
---

# The action row

## Definition of Done

- [x] Rendered from `GET /api/notes/actions` on note load; hidden entirely when the answer is empty.
- [x] Terminal moves (Decline, Supersede) confirm once; forward moves do not.
- [x] A disabled action shows its `reason` on hover — the button that explains, never the button that vanishes.
- [x] A completed action refreshes via the existing SSE note-changed event, not an optimistic local mutation — the file is the truth.
- [~] Guarded in the node suite; the vocabulary lives server-side only (asserted the ISS-0023 way).

## Done 2026-08-10

`mountActuatorRow` draws `GET /api/notes/actions` under the note's metadata strip — DES-0005's placement, since the left pane is a selection list and the right a description.

**Absent, not empty, when nothing is owed.** Most notes owe nothing most of the time; an empty row would be a permanent reminder that there is nothing to do, on every note in the corpus.

**No optimistic UI.** A completed action re-navigates so the note is re-read from disk. The write lands, the watcher emits, the file is the truth — REQ-0027's fourth criterion, and the tests assert the *absence* of a local mutation rather than the presence of a refetch.

### The vocabulary tried to come back through a class name

The first cut styled the affirmative button with `action.verb === 'Approve' || action.verb === 'Accept'`. That is the renderer knowing the verbs again — one class name at a time, which is exactly how [[ISS-0023]] happened. Tone now comes from `confirm`: a forward move reads affirmative, a terminal one reads as something to pause over, and **which moves are terminal is `CONFIRM_ACTIONS`' decision, server-side**.

The guard was widened to catch verbs as well as statuses once the code could pass it.

### The reconciled criterion

`- [~] Guarded in the node suite` — guarded in the **Python** suite instead (`tests/test_human_transitions.py`, five source-level assertions). The node suite covers two modules with real DOM fixtures; adding a third harness for assertions that are structural rather than behavioural would cost more than it catches. The vocabulary guard, the absent-when-empty guard and the no-optimistic-UI guard all read the source, which is where the drift would be.
