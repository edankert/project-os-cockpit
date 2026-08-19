---
type: "[[task]]"
id: TASK-0540
aliases: ["TASK-0540"]
title: "A check reads the documented vocabulary and the corpus, and fails when a live value is undocumented"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The drift check

## Definition of Done

- [ ] A validator rule parses `TAXONOMY.md`'s vocabulary table and every live value in the corpus, and errors on a live value the document does not define.
- [ ] Legacy values are exempt by being declared legacy, not by being absent.
- [ ] **Proved by introducing an undocumented value and observing the failure** — a check nobody has watched fail is a check nobody knows the direction of.

## Notes

This is the actual fix for [[ISS-0218]]. Rewriting the table fixes today; this stops tomorrow.

The drift lasted three weeks in four repos and **failed nothing**, because `acceptance.py` accepts both forms — correctly, since a suite mid-migration must keep working. Tolerance in the reader plus silence in the gate is the combination. This removes the silence and keeps the tolerance; they are separable, and the migrations depend on the tolerance staying.
