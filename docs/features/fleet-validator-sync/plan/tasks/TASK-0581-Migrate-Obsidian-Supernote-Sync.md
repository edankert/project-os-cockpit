---
type: "[[task]]"
id: TASK-0581
aliases: ["TASK-0581"]
title: "Migrate `obsidian-supernote-sync` — the rehearsal, at 3% of the hard repo's size and with nothing to lose"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0580"]
blocks: ["TASK-0582"]
related: []
tests: []
---

# Migrate `obsidian-supernote-sync`

## Definition of Done
- [x] `obsidian-supernote-sync` runs upstream's validator: `grep -c _acceptance_is_settled tools/scripts/validate-docs.py` is non-zero.
- [x] `bash tools/scripts/validate-docs.sh` exits 0 in `obsidian-supernote-sync` — from **16** errors under upstream's rules (12 `PARENT-BACKLINK`, 4 `SNAPSHOT-MEMBERSHIP`).
- [x] `python3 tools/scripts/sync-snapshot.py --check` passes.
- [x] The pre-commit hook passes, and the migration is committed **locally** in `obsidian-supernote-sync`. Nothing is pushed.

## Notes

88 corpus: 88 notes.

**The rehearsal.** 0 acceptance checks, so it gains nothing directly; that is the point. It proves the route end-to-end where a mistake costs 88 notes rather than 2519. Its post-baseline validator delta is 23 lines and **every one of them is already in upstream HEAD**, so this is the repo where `--force` is provably free.
