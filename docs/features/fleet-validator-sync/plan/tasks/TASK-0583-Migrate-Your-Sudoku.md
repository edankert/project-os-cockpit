---
type: "[[task]]"
id: TASK-0583
aliases: ["TASK-0583"]
title: "Migrate `your-sudoku` — the first repo where the gate has something to say"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0582"]
blocks: ["TASK-0584"]
related: []
tests: []
---

# Migrate `your-sudoku`

## Definition of Done
- [x] `your-sudoku` runs upstream's validator: `grep -c _acceptance_is_settled tools/scripts/validate-docs.py` is non-zero.
- [x] `bash tools/scripts/validate-docs.sh` exits 0 in `your-sudoku` — from **194** errors under upstream's rules (186 `PARENT-BACKLINK`, 8 `SNAPSHOT-MEMBERSHIP`).
- [x] `python3 tools/scripts/sync-snapshot.py --check` passes.
- [x] The pre-commit hook passes, and the migration is committed **locally** in `your-sudoku`. Nothing is pushed.

## Notes

604 corpus: 604 notes.

**The first repo where the gate does something.** 57 acceptance checks (this note said 59 until independent review recounted them from `level: acceptance` frontmatter), and 10 `VERIFY-ACCEPTANCE` findings appear the moment upstream's validator runs here — `FEAT-0025` against `TST-0028..0033` and `FEAT-0028` against `TST-0018..0021`. They arrive as **warnings**: upstream grandfathers the rule until **2026-11-20**. Installing the gate and having it block are two different dates, and [[ISS-0209]]'s 'done when' reads as one. Its 32 orphan lines are [[ADR-0030]]'s `CHK`/`checks` collection, which [[ADR-0031]] retired.
