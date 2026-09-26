---
type: "[[task]]"
id: TASK-0290
aliases: ["TASK-0290"]
title: "The awaiting-acceptance queue entry resolves through the run"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: S
depends: ["[[TASK-0289]]"]
blocks: []
related: []
tests: []
---

# The awaiting-acceptance queue entry resolves through the run

## Definition of Done

- `Awaiting your acceptance` rows open the runner; a completed run resolves the entry via review-resolve with the run summary as outcome.
- An abandoned run leaves the entry open and the partial run resumable — never silently resolved.

## Done — 2026-08-11, with half of it reconciled

This task was written on 2026-08-03 against **the desk queue**. [[ADR-0020]] retired that surface and [[FEAT-0090]] removed it, so the two halves land differently.

### The entry point — delivered, re-homed

*"`Awaiting your acceptance` rows open the runner."* The obligation now lives with its subject, which is [[ADR-0020]]'s rule: a feature carrying `acceptance: requested` is marked owed by the registry and counted on the Features badge ([[FEAT-0088]]), and the feature note's actuator row now offers **`▶ Accept…`**, opening `~accept/<id>`.

That closes the door-to-nothing [[REL-0001]] named as a reconciled-not-ticked criterion: *"a feature at `acceptance: requested` is marked but offers no run, because FEAT-0063's runner does not exist. A door to nothing teaches the reader the feature works."* It exists now.

### Resumability — delivered

*"An abandoned run leaves the entry open and the partial run resumable — never silently resolved."* Held: every verdict writes immediately through the guarded verbs, so an abandoned run keeps the work already done, and the run state survives navigation — esc pauses rather than discards, and returning to the route continues the walk. Nothing about abandoning a run resolves anything.

### `review-resolve` — reconciled, not delivered

*"A completed run resolves the entry via review-resolve with the run summary as outcome."* That is the desk ledger's verb, for a queue entry that no longer exists. Resolving a ledger entry the desk no longer shows would write to a surface nobody reads — the same reasoning that cancelled [[FEAT-0062]] on the same day ([[ISS-0126]]).

**Measured 2026-08-11: zero features carry `acceptance: requested`** — and unlike FEAT-0062's states, this one is empty because *its producer does not exist yet*: [[FEAT-0064]] is what stamps `requested` at close-out. So the entry point is built and waiting rather than built for nothing, and FEAT-0064 will fill it.
