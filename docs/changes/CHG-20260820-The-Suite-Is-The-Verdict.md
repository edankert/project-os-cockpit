---
type: "[[change]]"
id: CHG-20260820
aliases: ["CHG-20260820"]
title: "An automated test records no verdict, `tier:` is gone, and the Tests view is six derived sections"
status: active
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[FEAT-0139-The-Suite-Is-The-Verdict]]", "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]", "[[FEAT-0141-The-Contract-Says-It-Upstream]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]"]
tags: [change, testing, schema]
---

# The suite is the verdict

## What changed

**A test note that declares a `command:` records that a machine executes it, and nothing about whether it passed.** CI is the verdict. A manual test is unchanged and still records one, because nothing else knows how a person's check went.

**`tier:` is read by no code path.** A check's section is computed: a non-empty `command:` is *Automated tests*, else a `covers:` naming an `ISS-*` is *Regression tests*, else *Feature tests*.

**The Tests view is six sections**, every one derived: `Needs you`, `Feature tests`, `Regression tests`, `Automated tests`, `Broken command`, `Retired`. The eight verdict-state groups are gone.

## Behaviour a reader will notice

| | before | after |
| --- | --- | --- |
| `your-trainer` release gate | 68 open | **59 open** — the nine automated checks leave |
| This repo's automated tests | 37 in one collapsed `Verified` group | `Automated tests`, with their commands |
| An automated check on the generated page | a checkbox and a completed fraction | the command, and *"executed by CI"* |
| A regression check after an overlapping change | re-opened | **completed once, and stays completed** |
| `run-tests.py --write` | wrote `status`, `last_run`, `exit_code`, `updated` | writes nothing; `--write` is accepted and inert |
| Recording a run from the cockpit on an automated note | stamped it | **refused**, with the reason |

## Paths and contracts

- **`tools/instructions/TESTING.md` and `STATUSES.md` are rewritten upstream** in `~/Dev/repos/project-os` and synced to all 12 project-os repos. Instruction files only; no downstream note was migrated by that commit.
- **New validator codes**: `TEST-AUTOMATED-EVIDENCE` (error, zero violations at landing) and `CHECK-SUBJECT` (warning, cutover **2026-11-18**, 44 findings all in `your-trainer`).
- **`ACCEPTANCE-STATUS` widens** from `level: acceptance` to `command:` non-empty — 89 notes to 139.
- **New module** `command_targets.py`, mirrored inside the bundled validator because that file ships stdlib-only to every repo. A parity test asserts the copies agree, and that the two validator files stay byte-identical — which nothing had ever enforced.
- **38 notes in this repo** lost `status: passing`, `last_run:` and `exit_code:`; `tools/scripts/migrate-automated-verdicts.py` is re-runnable per repo and refuses to report success unless its after-census is clean.

## What did not change

- The 582 ledger-tracked acceptance checks: [[ADR-0037]] already moved their verdicts.
- Manual tests, and the staleness clock on them.
- `tier:` in the notes. It stops being read; **removing it from 671 notes is a later, separate migration**, so a bad derivation stays recoverable.
- `run` in the documents. Edwin, 2026-08-19: leave it there, keep it out of the UI.

## Known gaps, stated rather than discovered

- **67 checks still read `area: "Moved from Tier 1 / Tier 2 — Fully Automated"`** — a heading from a deleted document. [[ISS-0238]] stays open for it.
- **`Broken command` has no members anywhere** — 134 of 139 commands resolve, 5 name nothing checkable, none are broken. Proved on constructed input, with the mutant executed, because the corpus cannot prove it.
- **Invalidation narrowing is equally unprovable from the corpus**: zero checks in the fleet carry an invalidation. Same treatment.
- **[[ISS-0209]] is untouched**: the acceptance gate executes in no repo holding a check, so *"CI is green"* guarantees nothing in `your-trainer`, and none of this should be read as evidence that its 91 automated tests pass.
