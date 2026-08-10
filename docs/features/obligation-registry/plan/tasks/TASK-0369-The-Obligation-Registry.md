---
type: "[[task]]"
id: TASK-0369
aliases: ["TASK-0369"]
title: "One module enumerates every obligation kind with its predicate, owning view and verb"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
parent: "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0370-Badges-On-The-View-Buttons]]"]
related: ["[[TASK-0357-Obligation-Groups-And-Verbs-In-The-Payload]]", "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]"]
tests: []
---

# The obligation registry

## Definition of Done
- [x] The registry is enumerated **by note type**, not by desk element — every type declares either an obligation kind (predicate, owning view, verb) or an explicit `none` with its reason
- [x] **A type present in the corpus with neither fails a test.** This is the completeness guarantee; without it the registry is a list someone has to remember to finish
- [x] All 17 current types are declared: adr, architecture, change, dashboard, design, feature, glossary, issue, phase, plan, reference, release, requirement, risk, task, test, workflow
- [x] `task` and `plan` declare `none` **with the reason** — tasks are agent-owned end to end, a plan's status follows its parent — so deliberate silence is distinguishable from an omission
- [x] A kind names exactly one owning view; two views claiming one type fails a test
- [x] `QUEUE_INTAKE_STATES` is replaced by it, not duplicated alongside it
- [x] A settled subject is never owed — [[ISS-0121]]'s predicate lives here
- [x] No obligation vocabulary in TypeScript

## Steps
- [x] Write the registry beside `statuses.py`, which is the same shape of single-source and the precedent that earned it
- [x] Serve it, and give each view its own slice
- [x] Port `review_queue_payload`'s intake states across, deleting the originals
- [x] Test in the style of `tests/test_status_vocabulary.py`, plus the completeness sweep: read the types the corpus actually uses and assert each is declared

## Notes
Carries forward the one idea worth keeping from the superseded desk board: [[TASK-0357]] specified *"the verb ships in the payload beside the group; no obligation vocabulary in TypeScript."* Same rule, wider scope.

`change` is the kind [[ADR-0020]] originally missed — 116 notes, **76 without a review verdict**, a `GATE_BEARING_TYPE` whose warnings become errors on 2026-10-23. Its owning view is the Overview, per the ADR's amendment. Whether the historical ones count as owed is left open there; the registry should make that a **parameter** (a cutoff date) rather than a hard-coded answer, so the decision can be taken with the count in view.

## Why by type, and not by kind (amended 2026-08-10)

This task first listed seven obligation kinds by name. That list was drawn from **the desk's contents**, and it was wrong three times in one day — each time found by Edwin asking "what about X?", never by anything failing:

| missed | notes | why it was invisible |
|---|---|---|
| `change` | 116, **76 unreviewed** | never on the desk |
| `release` | 1 | never on the desk |
| `risk` · `workflow` · `phase` | 40 | never on the desk |

A fourth pass would find a fourth gap. Enumerating **by type** inverts it: the corpus supplies the checklist, and an undeclared type is a test failure rather than something someone has to notice. `change` and `release` cost two ADR amendments; the remaining three are [[ISS-0128]].

**`none` must be explicit and carry its reason.** `task` (381 notes) and `plan` (52) genuinely owe nothing — that is correct and load-bearing, and it is exactly what an omission looks like from the outside. Writing it down is what makes the completeness test meaningful rather than a formality.

**One type, one view.** [[ISS-0128]] records `risk` currently claimed by two — it renders in the Issues navigator today and [[FEAT-0087]] lists it for Intent. The assertion is what would have caught that at the point the scope was written.

## Done 2026-08-10

`src/project_os_cockpit/obligations.py`. **18 types declared, 8 owed, 10 explicit `none`.**

| view | answerable for |
|---|---|
| intent | adr · decision · design |
| features | requirement · feature |
| issues | issue |
| tests | test |
| overview | change |

### The completeness guarantee is the point

`test_every_type_in_the_corpus_is_declared` reads the types the notes actually use and fails on any without an entry. That is what would have caught `change`, `release`, `risk`, `workflow` and `phase` — all five found by Edwin asking rather than by anything failing, because a list written from one surface cannot know what was never on it.

### `none` carries its reason, and the test enforces it

`test_every_none_carries_its_reason` requires more than 40 characters, and **it caught two of my own entries** — `architecture` and `glossary` said only *"a standing document; see `reference`."* A cross-reference is not a reason. Both were rewritten rather than the threshold lowered.

That matters because `task` (381 notes) and `plan` (52) owe nothing *correctly*, and an unexplained absence is exactly what an omission looks like from the outside.

### [[ISS-0128]]'s four answers, and their reasoning

Asserted by `test_the_four_ISS_0128_answers_are_recorded`, which checks the **reasoning** survived and not just the verdict:

- **risk** → Intent, owes nothing. *"`open` is a risk's resting state. A risk is a hazard the project has decided to CARRY, and carrying one is not a debt."*
- **workflow** → owes nothing. *"workflows document the TOOLING, not this project's lifecycle."*
- **phase** → owes nothing. *"closing a phase is a PROCEDURE that follows the work"* — proposed as an obligation on Features, argued down, and the argument held: every other entry is discharged by one transition, and there is no verb an actuator could offer.
- **release** → owes nothing; the gate is a **test** obligation, per [[ADR-0020]] amendment 11.
