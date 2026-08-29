---
type: "[[task]]"
id: TASK-0584
aliases: ["TASK-0584"]
title: "Migrate `your-trainer` — 625 checks, 2519 notes, and the only repo where release-scoped verification currently pays"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0583"]
blocks: ["TASK-0586"]
related: []
tests: []
---

# Migrate `your-trainer`

## Definition of Done
- [x] `your-trainer` runs upstream's validator: `grep -c _acceptance_is_settled tools/scripts/validate-docs.py` is non-zero.
- [x] `bash tools/scripts/validate-docs.sh` exits 0 in `your-trainer` — from **605** errors under upstream's rules (589 `PARENT-BACKLINK`, 16 `SNAPSHOT-MEMBERSHIP`).
- [x] `python3 tools/scripts/sync-snapshot.py --check` passes.
- [x] The pre-commit hook passes, and the migration is committed **locally** in `your-trainer`. Nothing is pushed.

## Notes

2519 corpus: 2519 notes.

**The prize, attempted last.** 625 acceptance checks — this note and the migration commit both said 628, and independent review recounted them from `level: acceptance` frontmatter — 92% of the fleet's 682 — and the repo whose inability to scope `REL-0013` supplied [[ISS-0209]]'s worked cost. 589 `PARENT-BACKLINK` findings is over half the fleet total; by the time this runs the tool has been exercised three times. [[PHASE-041]]: *'a stalled first attempt is what parked this in PHASE-999-Future for a quarter already.'*
