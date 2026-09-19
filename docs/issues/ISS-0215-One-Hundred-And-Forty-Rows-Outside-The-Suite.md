---
type: "[[issue]]"
id: ISS-0215
aliases: ["ISS-0215"]
title: "49 checklist rows in three of your-trainer's test notes never reach the checks page or the release gate"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-09-19"
reported_by: agent
severity: high
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ISS-0213-Acceptance-Tests-Carrying-Level-System]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[PHASE-038-A-Verdict-Is-An-Event]]"]
---

# 49 checklist rows in three your-trainer notes are outside the checks page and the gate

Three test notes in your-trainer still hold their acceptance checks as checklist rows inside one note, so the checks page and the release gate cannot see those 49 rows. The largest of the original four, the iOS parity list, has since been split into check notes.

Found 2026-08-19 while levelling the five `level: system` manual tests ([[ISS-0213]]). Two were single procedures and were relevelled. The other three are **checklist documents in the pre-migration shape**:

| note | checklist rows | `level:` | why the suite cannot see it |
| --- | --- | --- | --- |
| `TST-0013` iOS parity acceptance | **107** | `system` | pre-migration shape, filed under `docs/tests/` |
| `TST-0011` Android BLE hardening acceptance | 18 | `system` | same |
| `TST-0012` iOS BLE hardening acceptance | 15 | `system` | same |
| `TST-0014` Android edge-to-edge inset acceptance | 16 | `system` | same — **added 2026-08-19, see below** |

**156 rows.** Each is an acceptance check by any reading — *"Manual acceptance coverage for everything the iOS parity push implemented, so Edwin can verify each new rider-facing surface before the iOS release"* — and not one of them is in `docs/tests/acceptance/`, so:

- the release gate cannot see them;
- `blocking_for` cannot scope them to a feature or a release;
- they carry no `mark:`, so nothing records whether they were run;
- the tests view shows three rows where there are 140 obligations.

[[PHASE-035]] migrated `ACCEPTANCE_TESTS.md` — the document the suite was named after — and these three were never in it. They were filed as ordinary `TST-*` notes under `docs/tests/`, so every sweep of *the suite* passed over them.

## Why this is not simply "run the migration again"

`TST-0013`'s 107 rows are the iOS parity push, batches 1–33. Splitting them needs a **surface** for each ([[FEAT-0130]]) and a `covers:` naming what each verifies — neither of which the rows carry today. Migrating them into 107 unattributed checks would move the problem rather than fix it, and would add 107 rows to a gate that fails closed on unattributed checks.

## Corrected 2026-08-19 — the count was 140 and it is 156

**`TST-0014-EdgeToEdgeInsetAcceptance.md` is a fourth note in the same shape**, carrying 16 more checklist rows: `status: ready`, `level: system`, no `command:`, named `…Acceptance`, filed under `docs/tests/`.

It was missed because this issue's population came from [[ISS-0213]], and [[ISS-0213]]'s five came from the **`Needs a walk` list**. `TST-0014` is not on that list: its only subject is `FEAT-0007-DevicePairingUI`, which is `done`, so [[ADR-0028]]'s in-flight rule suppresses it into `Resting`. It is owed by its type and quiet by its subject — working exactly as designed, and invisible to a measurement taken from the screen.

**The lesson is about the measurement, not the note.** A population counted from a surface inherits that surface's filters. The next count of this class should come from the frontmatter — *manual, system or acceptance level, filed outside `docs/tests/acceptance/`, containing checklist rows* — which is a query, not a reading.

`TST-0014` also carries `platform: "android"`, which is the [[ADR-0037]] case in miniature: 16 rows whose verdicts are Android-only, in a note with one place to put a result.

## Done when

- [ ] Each of the 156 rows is a check note, with a surface and a `covers:`.
- [ ] Or: a recorded decision that a named subset is retired instead, with the reason.
- [ ] The gate delta is measured and stated before it lands.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** A person preparing an Android or iOS release is not asked to walk the BLE-hardening or edge-to-edge checks, and the release gate can pass with them undone.

Evidence: in ../your-trainer on 2026-09-19, `docs/tests/TST-0011-AndroidBleHardeningAcceptance.md` (18 rows), `TST-0012-IosBleHardeningAcceptance.md` (15 rows) and `TST-0014-EdgeToEdgeInsetAcceptance.md` (16 rows) are `status: ready`, `level: system`, filed under `docs/tests/` and not under `docs/tests/acceptance/` (row count by `grep -cE '^\s*- \[.\]'`). `TST-0013-IosParityAcceptance.md` is now `status: retired` with 0 rows; its split landed in your-trainer 65344d40 (2026-08-25, "the iOS parity walk split"). This is **bigger**: each row needs a check note with an `area:` and `covers:`, authored in your-trainer, and the gate change measured first.

**Belongs to:** no open feature; the authoring happens in your-trainer. **Next:** split the three notes into check notes (or record which rows are retired), measuring the gate before and after.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
