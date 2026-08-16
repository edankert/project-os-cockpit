---
type: "[[task]]"
id: TASK-0433
aliases: ["TASK-0433"]
title: "The acceptance walker — one check at a time, pass / fail / skip with evidence, ticked back into the suite with a witness"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin's original report: 'it is not really clear how I should execute'", "Edwin 2026-08-16, choosing scope: full walker, with a run record"]
parent: "[[FEAT-0103-The-Gate-Is-Walkable]]"
effort: L
depends: ["[[TASK-0430-The-Suite-Is-Addressable]]", "[[TASK-0432-The-Gate-Lists-Its-Checks]]"]
blocks: []
related: ["[[FEAT-0063]]", "[[ISS-0141]]"]
tests: ["[[TST-0029-The-Walker-Ticks-What-It-Walked]]", "[[TST-0030-Walking-A-Release-Gate-End-To-End]]"]
---

# The acceptance walker

## What

The stepper the `TST-*` runner already has, pointed at a suite section's unchecked rows. One check on screen at a time, its procedure text visible, pass / fail / skip, an evidence field, and a tick written back.

**Reuses the runner's shape and, where it can, its code.** `buildTestRunner` is the desk's one piece of genuine machinery; a second stepper with its own vocabulary would be [[ISS-0023]] with a different noun.

## What a walk writes

- **Pass** → `- [x]`, with a dated witness appended inline: `_(walked 2026-08-16 · user:edwin)_`. `REQ-0028`'s rule is that acceptance names who stood behind it — *"`- [x]` says something was ticked; `accepted in cockpit run, user:edwin` says who stood behind it"*.
- **Fail** → stays `- [ ]`, annotated with what went wrong. A failed walk is evidence of a defect, not of progress, and a walker that ticked on failure would manufacture the claim the suite exists to make.
- **Skip** → nothing written. A check not performed leaves no trace, because a trace would be a claim.

## Definition of done

- [ ] A section can be walked from the gate; the stepper shows one check with its procedure text
- [ ] Pass ticks the row in `ACCEPTANCE_TESTS.md` and appends a dated witness naming the actor
- [ ] Fail leaves the row unticked and records what went wrong
- [ ] Skip writes nothing at all
- [ ] Every write is by section-and-ordinal with a name check and an `mtime` guard ([[TASK-0430]])
- [ ] A `- [~]` row is refused rather than walked
- [ ] Aborting mid-walk leaves the checks already recorded and nothing else — a partial walk is partial evidence, not none and not all
- [ ] Loopback-only; enumerated by `test_every_note_mutating_endpoint_requires_loopback`
- [ ] After a walk the gate's count drops by exactly what was passed, on the badge and in the list, from one computation
- [ ] Walked end to end against a throwaway suite, driving the real control — not asserted from the payload alone
