---
type: "[[issue]]"
id: ISS-0278
title: "CLAUDE.md says 49 notes carry a stale changes-requested verdict; today there are 89"
status: open
phase: "[[PHASE-999-Future]]"
owner: unassigned
reported_by: agent
created: 2026-09-05
updated: "2026-09-19"
source: ["Measured while drawing DES-0013; the design needed a real number for its review-queue mocks"]
severity: low
component: docs
parent: ""
related: ["[[project-os-deck#DES-0001]]", "[[ISS-0253-A-Verdict-Is-Answered-Not-Flipped]]", "[[project-os-dev#ADR-0011]]"]
tests: []
---

# CLAUDE.md understates how many verdicts are stale

`CLAUDE.md` tells every session that 49 notes carry `review_verdict: changes-requested`, 43 of them already finished; on 2026-09-19 the counts are 89 and 76.

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

Filed under LIFECYCLE "Scope of a change": found while drawing [[project-os-deck#DES-0001]], not asked for, and not fixed in that diff. `triage` because which of the three options is right is Edwin's call, and option 1 is a one-line edit anybody can make today.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** An agent reading `CLAUDE.md` is told the stale-verdict backlog is about half its real size.

Evidence: `CLAUDE.md:115` still reads "Measured 2026-08-20: **49 notes carried `changes-requested` and 43 of them were at a terminal status**". Counting `review_verdict: changes-requested` under `docs/` gives 89 notes, 76 of them at done/fixed/merged/implemented/passing/released/closed.

**Belongs to:** no feature. **Next:** Small docs fix: replace the number with a pointer to the validator's `REVIEW-STALE` warning (option 3), or restate it as a dated floor (option 1).

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
