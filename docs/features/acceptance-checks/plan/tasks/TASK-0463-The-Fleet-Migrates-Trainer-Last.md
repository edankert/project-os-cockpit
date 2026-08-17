---
type: "[[task]]"
id: TASK-0463
aliases: ["TASK-0463"]
title: "The fleet migrates, trainer last — your-sudoku, then your-trainer only after the schema has survived a real sweep"
status: doing
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
