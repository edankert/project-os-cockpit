---
type: "[[task]]"
id: TASK-0540
aliases: ["TASK-0540"]
title: "A check reads the documented vocabulary and the corpus, and fails when a live value is undocumented"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The drift check

## Definition of Done

- [x] A check parses `TAXONOMY.md`'s vocabulary table and compares it to `ledger.MARKS`, erroring when they disagree in either direction.
- [x] **It checks the gate column too.** A document right about the values and wrong about what they *do* is the more dangerous half — that is precisely the shape of the defect [[ADR-0029]] left behind when the release exception moved marks and stopped expiring.
- [x] Legacy values are exempt by being declared legacy under their own heading, not by being absent; `test_the_legacy_values_stay_readable` pins that `normalise_mark` still reads them and that none is a value the ledger accepts.
- [x] **Proved by mutation**: making the table say `excused` blocks fails it, and deleting `question` from the table fails it.

## Done 2026-08-19

It is a **test**, not a validator rule, and that is a deliberate narrowing. The validator walks a repo's own `docs/`; this compares a template-owned instruction file against this repo's *code*, which is a property of the cockpit rather than of any corpus it renders. Putting it in the validator would make every downstream repo assert something about a module it does not contain.

## Notes

This is the actual fix for [[ISS-0218]]. Rewriting the table fixes today; this stops tomorrow.

The drift lasted three weeks in four repos and **failed nothing**, because `acceptance.py` accepts both forms — correctly, since a suite mid-migration must keep working. Tolerance in the reader plus silence in the gate is the combination. This removes the silence and keeps the tolerance; they are separable, and the migrations depend on the tolerance staying.
