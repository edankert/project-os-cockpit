---
type: "[[requirement]]"
id: REQ-0039
aliases: ["REQ-0039"]
title: "A passing covering test settles the acceptance test it covers — automating a check must discharge it, which is the whole reason for the merge"
status: implemented
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "release gate"
implements: "[[FEAT-0120-The-Automation-Path]]"
acceptance:
  - "[ ] `Item.settled` is true when the mark is settled **or** the note's `covered_by:` names a test that is `passing`."
  - "[ ] A failing covering test un-settles the acceptance test, and the gate says which test and why — never a bare unticked row."
  - "[ ] Adding `command:` to an acceptance test and running `tools/scripts/run-tests.py` moves it out of the blocking set with no human mark written."
  - "[ ] `covered_by:` is refused unless the id resolves to a test that carries a `command:` — the same refusal shape as *Needs re-run* without a change id."
  - "[ ] Measured on `your-trainer` after the backfill: the blocking count falls by the number of checks whose covering test passes, and that number is reported rather than inferred."
covers: []
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[project-os-dev#ADR-0010]]"]
---

# A passing covering test settles the check

This is the requirement the whole programme exists for. Everything else in [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] is plumbing that makes this expressible.

**The direction is what keeps it safe.** A machine's exit code discharges a human's checkbox; a human's mark never writes a runner's status. [[project-os-dev#ADR-0010]] is untouched, and the thing that changes is which of the two facts the gate is willing to accept as evidence.

**Measured motivation:** 15 of the 60 checks blocking `your-trainer` today say in their own bodies that a machine already covers them, and `CHK-0505` says the manual walk is *"difficult to reproduce on real hardware"*. Under this requirement that check clears itself.

## Approved 2026-08-18

Approved with the read path demonstrated end to end and the write path still owed. Three of its five criteria hold today; the two about the *action* ([[TASK-0483-The-Covered-By-Action]]) and the measured fall in `your-trainer`'s blocking count are downstream of work that has not happened, so it does not reach `implemented`.

Independent review corrected the semantics twice before this: coverage is **all** covers passing, not any, and a **manual** covering test is not coverage at all.

## Acceptance criteria

- [x] **`Item.settled` is true when the mark is settled or `covered_by:` names a `passing` test.** Corrected twice by review before it was right: **all** covers must pass, not any, and only an **executable** test counts — a manual `passing` would let one hand-walk launder itself into another's automation.
- [x] **A failing covering test un-settles it**, because the status is resolved at load rather than remembered. Guarded, along with the third state review did not ask for: a `ready` cover settles nothing, since *"not failing"* is not coverage.
- [x] **Adding `command:` moves a check out of the blocking set with no human mark written.** Demonstrated end to end in `test_a_passing_covering_test_settles_the_check`.
- [x] **`covered_by:` is refused unless the id resolves to a test carrying a `command:`** — `note_writes.cover_check`, with three further refusals (unresolvable id, wrong type, `partial` without a reason).
- [~] **Measured on `your-trainer`: the blocking count falls by the number discharged this way.** Reconciled at **zero**, and the zero is the finding rather than a gap: its 203 annotations name 54 JVM test classes and **not one names a `TST-*` id**, so there is nothing the gate can check. Filling the field would mean inventing 54 notes whose gradle command nobody can run — unverifiable claims in the field that decides a release gate, which is precisely what the refusal above exists to prevent. The mechanism is proven; that repo has not been given data it can act on.

## Advanced 2026-08-18

The fifth criterion is the honest one: **the automation path works and nothing in the fleet uses it yet.** Writing 54 unrunnable test notes to make a number move would have been the opposite of what this requirement asks for.
