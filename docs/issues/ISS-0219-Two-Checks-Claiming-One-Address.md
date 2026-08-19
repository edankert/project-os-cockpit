---
type: "[[issue]]"
id: ISS-0219
aliases: ["ISS-0219"]
title: "An acceptance check authored outside the migration has no `section:`/`ordinal:`, so every one of them addressed as `.0` — two checks claiming one address, and the gate delta was already carrying both"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: cockpit-server
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
related: ["[[ISS-0214-A-Note-Whose-Id-Contradicts-Its-Filename]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[TASK-0507-Decide-A-Level-For-The-Five-System-Manual-Tests]]", "[[TASK-0532-Fix-The-Splitter-Before-Anything-Migrates]]"]
---

# `.0` is not an address

## Problem

`Item.number` was `f"{self.section}.{self.ordinal}"` unconditionally. Every check carrying neither field renders as **`.0`** — so any two of them are *two checks claiming one address*, which is [[ISS-0214]]'s class in a different field.

It is not a display nicety: `number` is emitted as the row identity in the acceptance payload (`acceptance.py:1428`) and read as the row's id wherever a note id is absent (`cockpit.py:4332`).

## How it surfaced

`tests/test_gate_delta.py::test_the_delta_against_your_trainers_real_tags` went red on `main`, asserting *"a row cannot be in two groups at once"* — 62 keys, 61 distinct.

**The test was right and the assertion was about the wrong thing.** No row was in two groups; two different rows had one address.

The second one arrived on 2026-08-19: [[TASK-0507]] relevelled `TST-0015` and `TST-0018` to `level: acceptance`. Both live in `docs/tests/` rather than `docs/tests/acceptance/`, were authored years before the migration, and therefore carry no `section:` and no `ordinal:` — nothing gave them one, because those fields exist to record a position in a document neither was ever in.

**Until there was a second such note, the collision could not fire.** One check at `.0` is an odd address; two are a defect. That is the whole reason this sat unseen.

## Fix

`number` returns the note's **id** when there is no position, and the positional address otherwise:

```python
if not self.section and not self.ordinal and self.note_id:
    return self.note_id
return f"{self.section}.{self.ordinal}"
```

This is what [[ADR-0030]] decision 4 already said the address should become — *"ordinal is display-only and sparse … which retires the shifting section-ordinal address for good"*. The positional form survives only because twelve historical tags hold file-shape suites where it is the only address there is.

## Why it is filed rather than folded into the phase silently

Found while running the suite before touching anything for [[PHASE-038]], and **it was red on `main` before any of this phase's code existed** — verified by stashing. A phase that starts against a red suite has no regression signal, and a fix that arrives inside an unrelated commit is a fix nobody can find later.

[[ADR-0037]] removes the need for the positional form entirely — a ledger entry keys on the check's id — but that is not a reason to leave two checks sharing an address in the meantime.

## Fixed 2026-08-19

- [x] `Item.number` falls back to `note_id`.
- [x] `tests/test_gate_delta.py` green, and its uniqueness assertion now asserts something true.
- [x] Full suite green: 1685 passed, 4 skipped.
