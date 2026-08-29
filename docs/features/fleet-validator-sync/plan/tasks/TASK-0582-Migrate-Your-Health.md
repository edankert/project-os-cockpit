---
type: "[[task]]"
id: TASK-0582
aliases: ["TASK-0582"]
title: "Migrate `your-health` — the second rehearsal, now at real corpus scale"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0581"]
blocks: ["TASK-0583"]
related: []
tests: []
---

# Migrate `your-health`

## Definition of Done
- [x] `your-health` runs upstream's validator: `grep -c _acceptance_is_settled tools/scripts/validate-docs.py` is non-zero.
- [x] `bash tools/scripts/validate-docs.sh` exits 0 in `your-health` — from **271** errors under upstream's rules (257 `PARENT-BACKLINK`, 14 `SNAPSHOT-MEMBERSHIP`).
- [x] `python3 tools/scripts/sync-snapshot.py --check` passes.
- [x] The pre-commit hook passes, and the migration is committed **locally** in `your-health`. Nothing is pushed.

## Notes

782 corpus: 782 notes.

**Second rehearsal, real scale.** 0 acceptance checks, 782 notes. This is where the backlink reconciliation is first exercised at a size a person could not do by hand. Its four orphan lines against upstream are comment wording, not behaviour. Distinct from the others in one way: its sync baseline is `5037e13`, not `40b2649`.
