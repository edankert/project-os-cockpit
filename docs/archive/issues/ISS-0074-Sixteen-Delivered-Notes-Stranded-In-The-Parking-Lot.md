---
type: "[[issue]]"
id: ISS-0074
aliases: ["ISS-0074"]
title: "16 of the 19 notes naming PHASE-999 are terminal, so the phase strip draws 16 `delivered` squares inside a phase titled 'Future / Unphased'"
status: fixed
severity: medium
phase: "[[PHASE-015-Phase-Hygiene]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin, 2026-07-30: 'if a feature is complete but it was never planned, it will for always stay in the unplanned/future phase'"]
component: docs-system
related: ["[[ISS-0069-Review-Verdict-Vocabulary-Is-Unguarded]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]", "[[ADR-0009]]"]
fixed_by: ["[[CHG-20260730-Phase-Hygiene]]"]
tests: []
---

# The parking lot is 84% graveyard

## Measured

```
19 notes name PHASE-999
16 TERMINAL   FEAT-0045 · REQ-0019 · REQ-0020 · TST-0016
              ISS-0032 · ISS-0059 · ISS-0060 · ISS-0061
              TASK-0111 · 0112 · 0113 · 0213 · 0230 · 0232 · 0233 · 0234
 3 parked     FEAT-0029 (backlog) · TASK-0045, TASK-0065 (deferred)
```

`stats_payload` renders that phase as `{'delivered': 16, 'deferred': 2, None: 1}` — sixteen shipped squares under a heading that says the work has not been planned yet.

**One feature's tasks are in two phases.** [[FEAT-0044]] closed in [[PHASE-013]] with [[TASK-0231]]; its sibling [[TASK-0230]] stayed in `PHASE-999`. Same feature, same close-out, same day.

**The parking lot did not know its residents had left.** Its `features:` list still named [[FEAT-0018]] and [[FEAT-0028]] after both went `done` and were re-phased. Hand-kept membership beside self-declaring members, and nothing compares them — the dual-write [[ADR-0009]] removed for statuses.

## Cause

`phase:` answers a **plan-time** question that is never re-asked as a **record** question. Before the work: *which phase will deliver this?* — "not planned yet" is valid. After: *which push shipped it?* — "not planned yet" is a category error, not a stale value.

`PHASE-999`'s own note documents only the forward exit ("when the item gets serious planning, re-phase it"). The exit that happens most — the item gets built — is not written anywhere, and close-out does not re-ask. Stuck **by construction**.

## Fixed where?

The rule belongs **upstream**: `LIFECYCLE.md`, `STATUSES.md` and `validate-docs.py` are template-owned, and this repo holds the validator byte-identical ([[ISS-0026]] / [[TST-0019]]). Filed as `project-os-dev` ISS-0027 with the proposed check — the mirror of `PHASE-CHILDREN`, reusing `PHASE_RESOLVED`.

This issue is the **local** half: correct the sixteen, and add a guard to this repo's own suite so the corpus cannot silently refill while the template rule is decided.

## Expected

No terminal note names the parking-lot phase.


## Fixed 2026-07-30

Sixteen re-homed, three left. The per-note attribution table and its evidence are in [[CHG-20260730-Phase-Hygiene]]; fifteen resolved from a link already in the note, one ([[FEAT-0045]]) needed [[PHASE-014]] written for it.

```
before   19 name PHASE-999   16 terminal, 3 parked
after     3 name PHASE-999    0 terminal, 3 parked
                              FEAT-0029 backlog · TASK-0045, TASK-0065 deferred
```

Those three are what the sentinel is for.

Guarded by `test_no_terminal_note_sits_in_the_parking_lot`, plus `test_the_parking_lot_still_holds_the_work_it_is_for` — because emptying the sentinel would satisfy the first while destroying the thing it makes visible. Both mutation-verified.

The rule that stops this recurring is **upstream** (`project-os-dev` ISS-0027) and open: the validator is template-owned and held byte-identical here ([[ISS-0026]]), so what lands locally is a guard rather than a gate. Same split [[ISS-0069]] took.
