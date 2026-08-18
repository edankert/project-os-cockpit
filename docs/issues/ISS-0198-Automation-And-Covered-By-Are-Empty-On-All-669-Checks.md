---
type: "[[issue]]"
id: ISS-0198
aliases: ["ISS-0198"]
title: "`automation:` and `covered_by:` are empty on 669 of 669 checks while 203 bodies name their covering test in prose — the bridge ADR-0030 defined was never populated"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: docs
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[ISS-0195-Two-Types-Carry-One-Act]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[REQ-0039-A-Covering-Test-Settles-The-Check]]", "[[TASK-0485-Backfill-Automation-From-The-Prose]]"]
---

# The automation bridge is empty everywhere

[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] defined `automation:` (`full`/`partial`/`manual`) and `covered_by:` so a check could say *a machine already covers me* — the mechanism TESTING.md's Tier 2 → Tier 3 promotion rule depends on.

Measured 2026-08-18 across all three suites: **`automation: manual` on 669 of 669, `covered_by: []` on 669 of 669.**

Meanwhile **203 of `your-trainer`'s 579 bodies carry the migration's parenthesised annotation** (181 `(partially automated`, 22 `(automated`, zero `(fully automated`), and 221 mention automation at all. ADR-0030 recorded 201 annotated rows pre-migration, so the annotation survived the migration **as text** and was never moved into the field defined to hold it.

## What it costs today

The `~checks` filter bar offers no automation axis at all: the backend emits a single-valued facet and `buildCheckFilters` drops any axis with fewer than two values, deliberately and correctly. So the one question *"which of these does a machine already do?"* cannot be asked of the corpus that answers it in prose 203 times.

And it is not only a filter. **15 of the 60 checks blocking `your-trainer`'s release say in their own bodies that a machine already covers them** — `CHK-0505` describes its manual walk as *"difficult to reproduce on real hardware"* and names the automated test that does it — and none of that reaches the gate.

## Independent of the type question

This is a data-quality defect that would be worth fixing whether or not [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] is accepted. It is scheduled under [[TASK-0485-Backfill-Automation-From-The-Prose]] because the backfill is only useful once [[REQ-0039-A-Covering-Test-Settles-The-Check]] makes the field mean something — but if the merge is declined, this should be re-homed rather than dropped.

## The decision inside it

The annotations name **JVM test classes** (`LicensingManagerTest`, `RiderCardTest`), not `TST-*` ids. So the backfill needs a rule: record the class in a form the gate can check, or create a `TST-*` for the class and name that. Choosing wrong produces 203 notes of plausible data the gate cannot use.

## Next actions

- [ ] Decide the class-vs-id rule before writing anything.
- [ ] Backfill what resolves; **list** what does not rather than skipping silently.

## Fixed 2026-08-18 — one field, and why not the other

**`automation:` is populated**: 181 `partial` + 22 `full` in `your-trainer`, from the annotations the document migration had carried across as prose. The `~checks` automation filter renders for the first time.

**`covered_by:` stays empty, on measurement rather than on omission.** The 203 bodies name **54 distinct JVM test classes** and **none names a `TST-*` id**. Filling the field would mean inventing 54 test notes whose gradle command nobody can execute — and since [[TASK-0482-Covered-By-Reaches-The-Gate]] made this field decide a release gate, an unrunnable claim in it is worse than an empty one. `cover_check` refuses exactly that, so the field is empty *because the guard works*.

What would close the remaining half is somebody with the Android toolchain writing a `TST-*` per class that a runner can actually execute. That is real work in `your-trainer`, not in this phase.
