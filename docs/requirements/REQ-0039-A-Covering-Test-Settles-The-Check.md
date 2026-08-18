---
type: "[[requirement]]"
id: REQ-0039
aliases: ["REQ-0039"]
title: "A passing covering test settles the acceptance test it covers — automating a check must discharge it, which is the whole reason for the merge"
status: draft
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
