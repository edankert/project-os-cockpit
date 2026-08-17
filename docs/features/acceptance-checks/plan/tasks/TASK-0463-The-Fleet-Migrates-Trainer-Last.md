---
type: "[[task]]"
id: TASK-0463
aliases: ["TASK-0463"]
title: "The fleet migrates, trainer last — your-sudoku, then your-trainer only after the schema has survived a real sweep"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: M
depends: ["[[TASK-0461-Pilot-This-Repo]]", "[[TASK-0462-The-Delta-Reads-Two-Shapes]]", "[[TASK-0467-The-Impact-Sweep-At-Close-Out]]"]
blocks: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tests: []
---

# The fleet migrates, trainer last

`your-sudoku` (56 rows), then `your-trainer` (579 rows, 60 blocking, the only corpus that ships) — deliberately last, and gated on the schema having survived a real close-out sweep in the pilot repo, because a schema defect discovered against 579 live rows is a migration re-run in the one repo where the record is load-bearing.

## Done when

- [ ] Both repos migrate with the parity assertions green; `your-trainer`'s blocking number is unchanged across the cut.
- [ ] `your-trainer`'s obligation badge total is measured before and after and has not risen — the [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] guarantee, checked at the moment it is most at risk.

## Outcome, 2026-08-17 — half done, and the reason is not the schema

**`your-sudoku` migrated and is committed there** (`87a1ff7`): 56 rows, parity green, blocking 56 before and 56 after, obligations 12 before and 12 after with **zero** of them a check. The check type reached its own template-owned copies first, byte-identically to upstream, and its adapters were regenerated — its pre-commit hook caught that they were stale, which is the hook doing exactly its job.

**`your-trainer` is not migrated, and its dry run is green**: 579 rows, 513 settled, 60 blocking, parity asserted, ids `CHK-0001..CHK-0579`.

What stopped it is the state of its working tree: **102 uncommitted files** of parallel work. Writing 579 notes and deleting one into that tree means a commit whose pre-commit hook re-stages a `SNAPSHOT.yaml` somebody else is mid-edit on — which is precisely the failure `close-out-commit.sh` was written to prevent, measured on this very repo (*"`your-trainer` carried 44 uncommitted files and `your-health` 8, none of them the work in hand"*). Named paths do not save it, because the hook adds one of its own.

So the leg is **ready and waiting on a clean tree**, not blocked and not unknown. Run it when that repo is quiet:

```
.venv/bin/python tools/scripts/migrate-acceptance-checks.py --repo-root ~/Dev/repos/your-trainer --apply
```

…then its `sync-snapshot.py`, its validator, and the badge measurement before and after (32 → must not rise *because of checks*; it will rise by the number of its in-flight features with no `acceptance_impact:`, which was 4 at measurement).

## Done, 2026-08-17 — the fleet is migrated

`your-trainer` migrated on Edwin's instruction: **579 rows**, `CHK-0001..CHK-0579`, commit `1acc3850` there. The numbers a release is decided by are identical across the cut — **579 rows, 513 settled, 60 blocking, 53 stale**, `missing_issue_refs` 73 — and the [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] guarantee holds exactly: **37 obligations before, 37 after, view by view, and zero of them a check** in the repo that holds 579 of the fleet's 669.

**Nineteen rows were uncommitted and their notes say so.** The working tree held 579 against 560 at `HEAD`, so nineteen checks would have carried `migrated_from: … @ 5976a658` — a sha that does not contain them, wrong in precisely the field that exists because blame cannot cross a migration commit. The script now diffs the working tree against `HEAD` on tier+name and stamps those `(uncommitted at migration)`. **This was found by being asked to run the command after saying it should wait**, which is the useful order: the objection turned into a feature rather than a delay.

**`SNAPSHOT.yaml` was deliberately not staged.** It carries 41 lines of live work — PHASE-020, FEAT-0104, TASK-0779..0783 — and `counters.CHK: 579` sits in it uncommitted, to travel with the rest of that edit. The other 100 dirty files in that repo were untouched.

Fleet-wide: **669 rows in three suites, all now notes.** The four frozen per-release documents in `your-trainer` are untouched by construction, and one of them turned out to be a defect — [[ISS-0192-A-Frozen-Release-Suite-Still-Offers-Live-Marks]].

## Eleven tests went silent and said the repo was missing

The most useful thing this leg found, and it was found by counting: the suite went from **2 skipped to 13** the moment `your-trainer` migrated, every one of the eleven reporting *"../your-trainer is not present"*.

The repo was present. Four test modules keyed their skip on `(TRAINER / "docs" / acceptance.SUITE_REL).exists()` — the presence of **one storage shape** — under a reason that described **the repo**. So when the shape changed, eleven guards stopped running and explained themselves with a sentence that was false. **Six of them were `test_gate_delta.py`**, which is the release-gate delta — precisely what this phase's own exit criterion says must still compute at every real `your-trainer` tag after the cut. They would have skipped through it.

The condition now asks what it means — `acceptance.load(...).exists`, either shape — and nine of the eleven are running again against the note corpus, which is far better coverage than they had before. The remaining two genuinely have no subject: they render a file-shaped suite and assert the treeprocessor addresses its rows. They carry their own marker with a true reason naming [[ISS-0192-A-Frozen-Release-Suite-Still-Offers-Live-Marks]], and they go when that plumbing goes.

*A skip condition that names one storage shape expires when the storage changes — **silently, and with a false reason**, which is worse than failing, because a red test gets read. Counted, not noticed: `1633 passed, 13 skipped` reads like success.*
