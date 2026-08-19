---
type: "[[task]]"
id: TASK-0536
aliases: ["TASK-0536"]
title: "`acceptance.load` and `Item` take the verdict from the ledger, and a guard test fails on any frontmatter read"
status: doing
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

- [x] `acceptance.load(platform)` joins notes to the ledger for that platform.
- [x] `Item.checked` / `reconciled` / `excepted` / `failed` / `question` / `needs_rerun` derive from the latest terminal entry, not from a field.
- [x] `Item.settled` keeps its `command:`-passing clause ([[ADR-0031]] d3) alongside the ledger clause.
- [x] `LEGACY_MARKS` and the character aliases move to the migration, not the reader.
- [ ] **A guard test fails if any module reads `mark` from frontmatter.**

## Notes

The guard is not ceremony. A surviving frontmatter read does not raise — it returns a stale scalar that looks exactly like a verdict, so the failure is silent and indistinguishable from success. That is the case a guard exists for, and this migration touches too many sites to be verified by reading.

## Done 2026-08-19 — `acceptance.apply_ledger`, an overlay

The verdict comes from the ledger for the platform in view. Three properties, each pinned:

* **A repo with no ledger is untouched.** Nine of twelve fleet repos have none and must read exactly as they did.
* **A check with no entry falls to `todo`, not to whatever the note still says.** Once a ledger exists the absence *is* the verdict, and a leftover `mark: done` must not out-vote it ([[REQ-0054]]).
* **The expiry lives in `ledger.resolve`**, not here — one implementation rather than one per surface.

`Suite` now carries the `platform` its verdicts are about, so a surface cannot render a verdict without knowing which platform it belongs to.

**The guard test is not written.** The DoD asks for a test that fails if any module reads `mark` from frontmatter, and the pre-ledger path still legitimately does — so the guard cannot be written until [[TASK-0530]] removes the field. Recorded rather than quietly dropped: this is the criterion that catches a survivor among 87 renderer sites, and it is owed.
