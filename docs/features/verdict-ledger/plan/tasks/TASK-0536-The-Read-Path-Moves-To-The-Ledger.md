---
type: "[[task]]"
id: TASK-0536
aliases: ["TASK-0536"]
title: "`acceptance.load` and `Item` take the verdict from the ledger, and a guard test fails on any frontmatter read"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The read path

65 `mark` sites in `acceptance.py`.

## Definition of Done

- [ ] `acceptance.load(platform)` joins notes to the ledger for that platform.
- [ ] `Item.checked` / `reconciled` / `excepted` / `failed` / `question` / `needs_rerun` derive from the latest terminal entry, not from a field.
- [ ] `Item.settled` keeps its `command:`-passing clause ([[ADR-0031]] d3) alongside the ledger clause.
- [ ] `LEGACY_MARKS` and the character aliases move to the migration, not the reader.
- [ ] **A guard test fails if any module reads `mark` from frontmatter.**

## Notes

The guard is not ceremony. A surviving frontmatter read does not raise — it returns a stale scalar that looks exactly like a verdict, so the failure is silent and indistinguishable from success. That is the case a guard exists for, and this migration touches too many sites to be verified by reading.
