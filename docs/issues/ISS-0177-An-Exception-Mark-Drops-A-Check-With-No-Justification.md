---
type: "[[issue]]"
id: ISS-0177
aliases: ["ISS-0177"]
title: "`- [!]` removes a check from the release gate with no justification, nothing owed and no record — the escape hatch shipped without the accountability half TESTING.md requires"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Independent review of PHASE-034, 2026-08-16, finding P6 — verified by execution", "Edwin 2026-08-16, on what to do about it: 'Keep it, file the gap'"]
severity: high
component: cockpit-server
parent: ""
related: ["[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[ISS-0141]]", "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]"]
tests: []
---

# An exception mark drops a check with no justification

## Problem

`acceptance.py` admits `!` as a mark and counts it **settled**, so `blocking()` drops it from the release gate. Verified by execution: hand-write `- [!]` on any Tier 1/2 check and the gate's count falls by one — with no justification, no release-note entry, and nothing owed anywhere.

`TESTING.md` line 113 is explicit that this is not allowed: *"A test may be marked as a release exception if it cannot be completed … **Exceptions must be documented in the release note with justification.**"*

## Why it is open rather than reverted

[[FEAT-0104]] designed both halves — the mark, and an `Justify` obligation counting any `[!]` with no matching release-note entry ([[TASK-0436]]). Only the permissive half shipped. The accountability half is blocked behind [[ISS-0175]], because the interaction that would capture a justification is keyed on which rendered checkbox is which check, and that correspondence does not hold.

Edwin's call, 2026-08-16: **keep the escape hatch and file the gap.** It is useful now — there are checks in 2.1.7's gate that genuinely cannot be walked — and the risk it carries is that one leaves the gate silently.

[[FEAT-0104]] reads `backlog`, which conceals that a live part of it is already in the code. That is its own small defect: a feature whose permissive half ships while its status says nothing has.

## Expected

Either:

1. `[!]` counts as **blocking** until a justification exists — it marks intent without granting the exception; or
2. [[TASK-0436]]'s `Justify` obligation lands, so an unjustified exception is counted and named.

Until one of them, a check can leave the release gate with no reason recorded, which is the single thing the gate exists to prevent.


## Deferred 2026-08-16

Edwin's explicit call on 2026-08-16 was *'Keep it, file the gap'* — the escape hatch is useful now and the accountability half waits on work this phase is not doing. Deferred rather than carried open into a closing phase, so the record says parked rather than forgotten.


## Re-homed to [[PHASE-999]] on 2026-08-16

[[PHASE-034]] closed and this is parked, not resolved — `deferred` is not a resolved status, so carrying it inside a closing phase would fire `PHASE-CHILDREN` and, worse, would let a closed phase claim work it did not do. The sentinel is where work without a concrete delivery phase lives. Its origin and its reasoning stay above.

## Fixed 2026-08-17 — at the source, and the residue is named

The gap was that `[!]` shipped its permissive half: hand-write one and a check left the release gate with no justification and nothing owed.

`[!]` is now **never offered** — measured across every acceptance suite in the fleet it is written in zero of them, while `~` and `F` are the record's own, and Edwin's call was *"I have no problem using ~ instead."* It stays readable so nothing already using it breaks.

What replaces it closes the gap at the source rather than accounting for it afterwards: `[~]` and `[F]` are **refused without a reason**, as one write. There is no sequence of clicks that produces an undocumented exception.

**The residue, stated rather than assumed away:** a `[~]` typed into a suite by hand still carries no justification and nothing asks for one. A source-level refusal cannot reach a text editor. That is narrower than what this issue opened on — it now requires deliberately editing the file — and [[TASK-0436]] records why the registry-counting approach was cancelled in favour of prevention.
