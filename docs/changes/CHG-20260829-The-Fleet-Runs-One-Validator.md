---
type: "[[change]]"
id: CHG-20260829
aliases: ["CHG-20260829"]
title: "The fleet runs one validator — four repos migrated onto upstream's rules, two new scripts, and the drift is measured from now on"
status: merged
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
features: ["[[FEAT-0143-The-Fleet-Runs-One-Validator]]"]
issues: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
tags: [change, tooling, fleet]
---

# The fleet runs one validator

## What changed

**Two new scripts in this repo:**

| script | what it does |
|---|---|
| `tools/scripts/migrate-fleet-validator.py` | Force-syncs a repo's template-owned validator from upstream, then reconciles the parent/child backlink relationship in the notes and in `SNAPSHOT.yaml`. `--dry-run`, idempotent, add-only. |
| `tools/scripts/fleet-drift.py` | Reports every `SNAPSHOT.yaml`-bearing repo's missing upstream **rule codes**, its line divergence and its acceptance-gate count. Exits 1 when a repo holding acceptance checks is behind, 2 when the comparison could not be made. |

**One optional local hook:** `tools/hooks/pre-commit.local`, chained by `install-git-hooks.sh`. It is not installed by anything — the three lines to install it are in its header.

**Four repos outside this one were migrated, and committed locally.** Nothing was pushed.

| repo | before | after |
|---|---|---|
| `obsidian-supernote-sync` | 16 errors under upstream's rules, gate absent | 0 errors, gate present |
| `your-health` | 271, gate absent | 0, gate present |
| `your-sudoku` | 194, gate absent | 0, gate present, **10 `VERIFY-ACCEPTANCE` findings now fire in its own pre-commit** (57 checks) |
| `your-trainer` | 605, gate absent | 0, gate present, **19 `VERIFY-ACCEPTANCE` findings now fire** (625 checks) |

Fleet validator divergence from upstream went **782 / 817 / 776 / 776 → 0**.

## Why this is a change note and not just a task

Because behaviour changed in repos that are not this one. Four pre-commit hooks now run rules they did not run yesterday, and two of them now report acceptance findings that will **block** from **2026-11-20**, when upstream's grandfather window on `VERIFY-ACCEPTANCE` expires. Anyone committing in `your-sudoku` or `your-trainer` between now and then sees warnings that are not noise: they are the gate arriving.

## Three things a reader needs that are not obvious

**The migration was two rules, not a reconciliation per repo.** [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]] estimated *"a migration per repo — reconcile the notes each new rule reports"*. The census ([[TASK-0579-Count-The-Flood-By-Rule]]) found **1086 errors across four repos and 100% of them were `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP`**, which are one relationship seen from its two ends.

**One rule armed another, and the census could not have predicted it.** In `your-trainer`, `VERIFY` reads a feature's `tasks:` **from the snapshot**; with those lists absent it had nothing to walk. Filling them in — the migration's whole content — made it report 15 findings, three features closed while tasks in their scope are open. Recorded in that repo's `tools/GRANDFATHERED.yaml` (155 → 158) rather than guessed at. **A report-only census counts the rules that can fire against the corpus as it stands, and fixing rule A can arm rule B.**

**`your-trainer` can now derive part of a release's check scope, and the part it cannot is filed.** `REL-0013` needs 32 of 625 checks. Thirteen were authored for `FEAT-0104` and every one said `covers: FEAT-0011`, so the derivation returned zero and the table was written by hand. Fixed. The other nineteen are checks the release *breaks* rather than *builds*, a relation no field carries — [[ISS-0258-A-Release-Cannot-Derive-What-It-Broke]].

## Filed rather than fixed

- [[ISS-0257-The-Sync-Carries-Upstreams-Build-Output]] — `sync-project-os.py` walks upstream's filesystem and copied a gitignored `.pyc` downstream.
- [[ISS-0258-A-Release-Cannot-Derive-What-It-Broke]] — the invalidation leg of a release's check scope.
- [[ISS-0259-Six-Fleet-Repos-Run-Ten-Fewer-Rules]] — six more repos, outside this phase's scope, now measured.
- `your-trainer`'s three grandfathered `VERIFY` items, which are that repo's to settle. **Filed there as `ISS-0378`** — independent review pointed out that this section originally said "filed" while nothing had been, and that `GRANDFATHERED.yaml`'s own header says *"this file only shrinks"*, which three additions on 2026-08-29 contradict.

## Verification

- [[TST-0080-The-Reconciliation-Writes-Only-What-The-Notes-Declare]] — 19 tests, `tests/test_fleet_migration.py`.
- [[TST-0081-The-Drift-Check-Fails-When-The-Fleet-Falls-Behind]] — 12 tests, `tests/test_fleet_drift.py`.
- Nine mutants constructed against the two scripts; each fails a named test. One survived that first pass — deleting the writer's byte-identity guard — and the module now drives that function directly.
- **Independent review then found five more survivors**, and they were the important ones: the add-only merge loop, the partly-populated-list path, `main()` (reached by no test at all, so the dry-run's snapshot preview and ISS-0257's artefact pruning were both unguarded), two `RULE_RE` sub-patterns each of which blinds the drift check to `VERIFY-ACCEPTANCE`, and two live note shapes — a flow list closing at column 0, and CRLF — that made the writer produce unparseable frontmatter or raise mid-migration. All fixed; 42 tests now, and every one of the ten mutants fails a named test.
