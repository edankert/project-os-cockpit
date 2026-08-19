---
type: "[[issue]]"
id: ISS-0217
aliases: ["ISS-0217"]
title: "TESTING.md and SCHEMAS.md in your-trainer and your-sudoku still describe the `[[check]]` type and the `CHK-####` path ADR-0031 retired — and those two repos hold all 637 acceptance notes"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: docs
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
related: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[TESTING-MODEL]]"]
---

# The contract is right where the data is not

## Problem

[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] retired the `[[check]]` type and the `CHK-*` id space on 2026-08-18. The instruction documents an agent reads as contract were updated **here** and **upstream**, and not in the two repos that hold every acceptance note in the fleet.

Measured 2026-08-19:

| repo | acceptance notes | `TESTING.md` describes | `SCHEMAS.md` describes |
| --- | --- | --- | --- |
| `your-trainer` | **581** | `type: [[check]]`, `CHK-*`, `check.md` | `## check.md (type: [[check]])` |
| `your-sudoku` | **56** | same | same |
| `project-os-cockpit` | 34 | `TST-*` at `level: acceptance` ✓ | "There is no `check` type" ✓ |
| `project-os` (upstream) | 0 | current ✓ | no check section ✓ |

`your-trainer/tools/instructions/TESTING.md:65` still reads *"One check per note, `type: [[check]]`, id `CHK-*`, at `docs/tests/acceptance/CHK-####-Slug.md`, scaffolded from `../../docs/__templates__/check.md`"* — against a directory containing 579 `TST-*` notes and no `check.md` template.

## Why this matters more than ordinary staleness

**An agent working in `your-trainer` reads that file as the contract and builds the retired thing.** [[TESTING-MODEL]] already recorded exactly this failure once, from the other direction: `sweep._write_new_check` authored `type: "[[check]]"` notes that `acceptance.load` could not see in a migrated repo, so a swept check was invisible to `~checks`, to the tiers, and to the gate. The sweep is withdrawn ([[ADR-0036]]), but the instruction that would produce the same note by hand is still sitting in both repos.

**And it corrects the source proposal.** The [[ADR-0037]] source described this as drift to fix "in the same sweep", implying it lives here. It does not. Fixing `project-os-cockpit` fixes nothing where the checks are.

## This is [[ISS-0209]] wearing a different hat, and it is not the same fix

[[ISS-0209]] is about the **validator** being ~690 lines behind upstream in the fleet repos, and it cannot be closed by copying a file — pulling upstream's validator pulls every rule added since the last sync, which is a migration per repo.

**This one can be.** `TESTING.md` and `SCHEMAS.md` are prose; syncing them breaks no pre-commit and reports no new errors. They are template-owned and `sync-project-os.sh` already copies exactly these paths. The two issues share a cause and not a remedy, which is why this is filed separately rather than folded in.

## Expected

The instruction documents in every repo describe the type that repo's notes actually use.

## Next actions

- [x] Run `tools/scripts/sync-project-os.sh` for `TESTING.md` and `SCHEMAS.md` into `your-trainer` and `your-sudoku`, and diff before committing — these repos may carry deliberate local content in them (`your-trainer`'s tier definitions are its own and are cited by [[DES-0012]] D3).
- [x] Confirm no `check.md` template remains in either repo's `docs/__templates__/`.
- [x] Re-measure and record, so the next reader can see whether the fleet's instruction drift is closing or growing — the same closing condition [[ISS-0209]] carries.

## Fixed 2026-08-19

`TESTING.md`, `TAXONOMY.md`, `SCHEMAS.md` and `test.md` synced into `your-trainer` and `your-sudoku` from upstream `project-os@ce789d7`; `check.md` deleted from both.

**Diffed before copying, because that is what this issue is about.** The only lines lost are the four stale `[[check]]`/`CHK-*` paragraphs — the tier definitions [[DES-0012]] D3 cites are byte-identical in all three repos, so nothing local was destroyed. What remains matching `CHK` is the tombstone (*"there is no `check` type"*), which is the record rather than the drift.

**No note was touched in either repo, and neither is migrated.** The synced schema says so itself: the verdict fields are refused *in a repo that keeps ledgers*, and these keep scalar marks. That conditional is what let the instruction files go ahead of the data instead of waiting for it.

**Left uncommitted in `your-trainer`**, which now carries 64 files of work in flight belonging to somebody else. `your-sudoku` was clean and its four files are the only change in it.

The divergence measurement this issue asked for, repeated: the *instruction* drift is closed in both. The **validator** divergence ([[ISS-0209]]) is untouched and is a different fix — these are prose and sync cleanly; that one pulls every upstream rule added since the last sync.
