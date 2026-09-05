---
type: "[[issue]]"
id: ISS-0278
title: "CLAUDE.md states the stale-verdict backlog as 49 notes; it is 70, and the file that describes the problem now understates it"
status: triage
phase: "[[PHASE-999-Future]]"
owner: unassigned
created: 2026-09-05
updated: 2026-09-05
source: ["Measured while drawing DES-0013; the design needed a real number for its review-queue mocks"]
severity: low
component: docs
parent: ""
related: ["[[DES-0013-Nine-Ways-To-Read-The-Record]]", "[[ISS-0253-A-Verdict-Is-Answered-Not-Flipped]]", "[[project-os-dev#ADR-0011]]"]
tests: []
---

# The recorded stale-verdict count is out of date

## Problem

`CLAUDE.md` tells every session that **49 notes carry `review_verdict: changes-requested` and 43 of them are at a terminal status**, measured 2026-08-20. Today the same query returns **70 and 61**. The file that exists to describe the problem now understates it by 21 notes, and it is the first thing an agent reads.

This is not a defect in the rule `CLAUDE.md` states — "a verdict is answered, not flipped" is unchanged and correct. It is that the rule's supporting measurement is a hand-written number in a file nothing re-measures.

## Repro

```
grep -rl "review_verdict: *changes-requested" docs --include='*.md' | wc -l          # 70
# of those, count the ones whose status: is done|fixed|merged|implemented|passing|released|closed
```

Measured 2026-09-05 in `project-os-cockpit`.

## Expected

Either the number is current, or the text does not carry one. Three options, in increasing order of cost:

1. **Restate it as a floor** — "at least 49 notes, measured 2026-08-20 and rising" — which stays true without maintenance and is honest about being a snapshot.
2. **Re-measure at close-out** and update the line, which is the same manual step that has already failed once.
3. **Derive it.** `REVIEW-STALE` already computes exactly this set in the validator, so the count exists at runtime; the file could name the check instead of the number.

Option 3 is the only one that cannot go stale again, and it is also the one that changes a template-adjacent file, so it is a decision rather than a fix.

## Evidence

- `CLAUDE.md`, "A verdict is answered, not flipped": *"Measured 2026-08-20: **49 notes carried `changes-requested` and 43 of them were at a terminal status**"*
- 2026-09-05: 70 and 61.
- The `REVIEW-STALE` warning window closes 2026-11-18, at which point the same set becomes an error — so the number matters more, not less, over the next ten weeks.

## Notes

Filed under LIFECYCLE "Scope of a change": found while drawing [[DES-0013]], not asked for, and not fixed in that diff. `triage` because which of the three options is right is Edwin's call, and option 1 is a one-line edit anybody can make today.
