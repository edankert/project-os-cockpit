---
type: "[[plan]]"
title: "Plan — one test type, and one verification link"
status: active
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: []
implements: ["[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]", "[[FEAT-0119-The-Merge-Migration]]", "[[FEAT-0120-The-Automation-Path]]", "[[FEAT-0121-The-Verification-Link-Normalises]]"]
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[ISS-0195-Two-Types-Carry-One-Act]]"]
---

# Plan — one test type, and one verification link

## The gate before anything

**[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] and [[ADR-0032-The-Verification-Link-Has-One-Direction]] are `proposed`.** No note changes type, no id is renumbered and no field is deleted until Edwin accepts them. The phase is documented in full first, exactly as [[ADR-0030]] was, so that the acceptance is about something costed rather than something described.

## Order

1. **[[FEAT-0118-The-Test-Type-Absorbs-The-Check]] — upstream, all of it.** Statuses, schema, discriminator, validator. Synced down before any note moves. Nothing downstream is touched in this leg, which is what makes it safe to land early.
2. **[[FEAT-0121-The-Verification-Link-Normalises]] — before the migration, not after.** It removes VERIFY's ability to see an acceptance test at all, and the migration is what creates 669 of them. Doing it second means a window in which the gate can fire on every migrated note.
3. **[[FEAT-0119-The-Merge-Migration]] — pilot (34), then `your-sudoku` (56), then `your-trainer` (579).** Parity asserted through the reader per repo before any old file is removed. The cockpit cull lands with the last repo, not before — seven modules and 173 renderer sites still have live subjects until then.
4. **[[FEAT-0120-The-Automation-Path]] — last, and non-optional.** Everything above is cost. If the phase stops after step 3 it has moved 669 notes and improved nothing.

## The two things most likely to go wrong

- **The badge.** [[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]] is the highest-risk invariant here: one careless status write puts 669 self-re-arming rows in front of a person, which is precisely what [[ADR-0027]] exists to prevent. Guard it before the migration runs, not after.
- **A second blame break in two weeks.** Accepted knowingly and recorded in [[ADR-0031]]; provenance rides `migrated_from:` plus a new `merged_from:`.

## Independent review

Owed on this whole programme under QUALITY.md — two ADRs, four features moving to `done`, and a `CHG-*`. [[TASK-0490-Independent-Review-Of-The-Merge]] carries it, and it reviews the *result against the corpus*, not this plan.
