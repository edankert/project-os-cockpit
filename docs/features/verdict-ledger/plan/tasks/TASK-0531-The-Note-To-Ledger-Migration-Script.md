---
type: "[[task]]"
id: TASK-0531
aliases: ["TASK-0531"]
title: "The migration script — strip the fields, emit the ledger entries, refuse to run twice, list what it could not convert"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The migration

## Definition of Done

- [x] `tools/scripts/migrate-verdicts-to-ledger.py`, dry-run by default, `--apply` to write.
- [x] Refuses to run against a repo that already has a ledger, the way `migrate-acceptance-checks.py` refuses a populated checks directory.
- [x] Emits the ledger and strips the fields **in one commit**, so no state exists where both hold a verdict.
- [x] Anything it cannot convert is **listed**, not skipped silently.
- [x] `automation:`'s 203 values and their prose provenance are written to a seed file for [[FEAT-0138]] before the field is removed.

## Notes

The prior migration's `problems` list is the pattern to copy — and [[ISS-0216]] is what happens when a script drops input rather than reporting it. Six notes in `your-trainer` are truncated and the migration reported nothing.

**Do not run this before [[TASK-0532]].** The splitter fix is a [[PHASE-038]] exit criterion for exactly this reason.

## Done 2026-08-19 — `tools/scripts/strip-verdict-fields.py`, 34 notes

**The safety property is the whole script**, and it refuses before it writes rather than reporting after: *no verdict may be removed that the ledger does not already carry*. A `mark: done` with no ledger entry is a walked check about to become an unwalked one, silently, with the evidence deleted in the same commit.

Proved by construction — a note whose id the ledger cannot know is refused by name:

```
strip: REFUSING — 1 note(s) carry a verdict the ledger does not, and stripping would delete it:
  - TST-9944: `mark: done` and no entry in the macos ledger
```

**Indexed, for the reason [[TASK-0529]] learned the hard way** — the un-indexed read walks `docs/tests/acceptance/` only, and a check filed anywhere else would be stripped without ever having been backfilled.

**Line-oriented, like every other frontmatter write here.** A YAML round-trip would reformat every note it touched and bury the one real change in a whitespace diff. Block fields take their continuation lines with them, or the note stops parsing — a defect that reads as a missing note rather than as a bad edit.

Applied to this repo only: 34 notes, gate unchanged (0 blocking on `macos`, 34 on any other platform).
