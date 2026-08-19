---
type: "[[task]]"
id: TASK-0531
aliases: ["TASK-0531"]
title: "The migration script — strip the fields, emit the ledger entries, refuse to run twice, list what it could not convert"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The migration

## Definition of Done

- [ ] `tools/scripts/migrate-verdicts-to-ledger.py`, dry-run by default, `--apply` to write.
- [ ] Refuses to run against a repo that already has a ledger, the way `migrate-acceptance-checks.py` refuses a populated checks directory.
- [ ] Emits the ledger and strips the fields **in one commit**, so no state exists where both hold a verdict.
- [ ] Anything it cannot convert is **listed**, not skipped silently.
- [ ] `automation:`'s 203 values and their prose provenance are written to a seed file for [[FEAT-0138]] before the field is removed.

## Notes

The prior migration's `problems` list is the pattern to copy — and [[ISS-0216]] is what happens when a script drops input rather than reporting it. Six notes in `your-trainer` are truncated and the migration reported nothing.

**Do not run this before [[TASK-0532]].** The splitter fix is a [[PHASE-038]] exit criterion for exactly this reason.
