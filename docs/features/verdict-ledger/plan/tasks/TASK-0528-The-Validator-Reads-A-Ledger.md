---
type: "[[task]]"
id: TASK-0528
aliases: ["TASK-0528"]
title: "The validator reads a ledger — required fields, reason-bearing marks, and a sealed ledger that cannot change"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The gate on the ledger

## Definition of Done

- [x] An entry missing `check`, `mark`, `date`, `by` or `method` is an error naming the file and the check.
- [x] Every mark but `pass` refused without a `reason`.
- [x] The `excused` expiry is enforced in `ledger.resolve` rather than in the validator — one implementation, not one per surface, and it is `test_an_excused_check_expires_when_its_ledger_seals` that holds it.
- [x] `check` must resolve to a note in this repo.
- [x] An entry may not carry a `platform` that contradicts its file.
- [x] An `evidence` item whose `check` + `date` matches no entry is an error.
- [x] A sealed ledger differing from `HEAD` is an error.
- [ ] Errors land upstream first ([[ADR-0030]] decision 6) — **not done**, same debt as [[TASK-0539]].

## Done 2026-08-19 — six codes, and two guards that caught me

`LEDGER-PARSE`, `LEDGER-ENTRY`, `LEDGER-MARK`, `LEDGER-REASON`, `LEDGER-EVIDENCE`, `LEDGER-SEALED`. Proved by building a ledger with one of each defect and reading the output — every rule fires, and the messages say why rather than what.

**The vocabulary is restated in the validator rather than imported**, deliberately: this script is template-owned and runs in twelve repos, none of which may depend on the cockpit being installed. `test_taxonomy_documents_exactly_the_vocabulary_the_code_writes` keeps the restatement honest.

**Two of this repo's own guards fired on this change, and both were right.**

1. `STATUS-TABLE` — the validator's self-check refused three new module-level string collections until they were registered as non-statuses. Registering them as *statuses* would have asserted the opposite of what they exist to preserve: a verdict is an event, deliberately outside the status vocabulary, which is what keeps 671 acceptance tests off the review gate and off a badge. **The fourth time that guard has earned its keep.**
2. `desktop/tests/fleet-health.test.mjs` — *"every code the validator can emit has a label"*, written to fail *"when it gains a rule rather than when someone notices"*. It did exactly that, and the six codes now have readable labels.

**A limit found while satisfying that second guard:** its scrape is `report.error\("CODE"` on one line, so a `report.error(` with the code on the *next* line is invisible to it. Three of my six codes are written that way and were never checked. The labels are all present, so nothing is missing today — but the guard is weaker than it reads, and that is worth knowing before somebody relies on it.

## Notes

The reason rule is [[ADR-0029]]'s, finally enforceable. Measured 2026-08-19: `verdict_reason:` is non-empty on **0 of 671** notes — the rule has never been tested against anything, because nobody has written one of the four marks that demand it.

Immutability is what makes *"was release R walked?"* answerable. Without it the ledger is a mutable log, which is a scalar with more steps.
