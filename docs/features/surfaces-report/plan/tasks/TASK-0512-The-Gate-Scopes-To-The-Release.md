---
type: "[[task]]"
id: TASK-0512
aliases: ["TASK-0512"]
title: "When a release names contents, its gate reports what blocks THAT release"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# When a release names contents, its gate reports what blocks THAT release

`blocking_for(subjects)` already exists with a production caller. This passes the release's own feature ids.

Must not widen or narrow any existing release's gate: absence of named contents keeps the whole-suite gate.

## Done 2026-08-20 — but not as written, because [[ADR-0040]] overtook it

**This task describes the reading the decision rejected.** *"When a release names contents, its gate reports what blocks THAT release"* is the **divide** rule, and `blocking_for(subjects)` — which the task points at — implements exactly that: pass the subjects, get back only the checks covering them.

ADR-0040 chose **subtract**, and the measurement is the argument. On `your-trainer` (working tree, 2026-08-20): 59 blocking rows, 39 covering a `FEAT`, and **36 of those 39 cover a feature the release does not carry**. Dividing takes the gate to 23 *on the first render, by nobody's decision*, and empties the `chronic` bucket whose entire purpose is keeping long-carried debt visible.

So the new method is `Suite.blocking_minus(deselected)`. A check is dropped **only** when every subject it names is a feature somebody explicitly held back:

| the check covers | under subtraction |
|---|---|
| nothing at all | **gates** — the fail-closed clause `blocking_for` already carries |
| an `ISS-*` / `REQ-*` / `PHASE-*` | **gates**, untouched: no feature list speaks for it. **20 of your-trainer's 59** are in this class |
| a held-back feature **and** a carried one | **gates** — any carried subject is enough |
| held-back features only | dropped |

**The same 23, and that is the point.** Holding back those six features by hand gives `blocking_minus` → **23**, identical to what dividing produces automatically. The number is not the difference; the *cause* is. One is a default nobody chose, the other is a recorded act — which is exactly the distinction ADR-0040 exists to preserve.

## The invariant, asserted first

*"Must not widen or narrow any existing release's gate: absence of named contents keeps the whole-suite gate."* `blocking_minus(None)` and `blocking_minus(set())` both return `blocking()` — 59 against 59 on the live corpus, and asserted on constructed input as well. Eleven historical releases depend on it.

## Constructed input, deliberately

No release names contents yet — the picker is [[TASK-0511]] and [[TASK-0558]] — so **the corpus cannot exercise this rule at all** and a guard built on it would never fire. Five tests on built fixtures instead, including the mixed cell, which was written before the rule and is why it reads `not feats <= deselected` rather than testing intersection.

Three mutants run; **one of them was not a mutation.** Changing `if not deselected` to `if deselected is None` passed, and it should have: with an empty set the loop reaches the same verdict for every row, so the two are behaviourally identical. Recorded rather than counted as a pass — a mutant that cannot change the answer proves nothing, and calling it a third caught mutation would have overstated the guard. The two that do differ — dropping on intersection, and letting selection reach a non-feature subject — both fail, as does ignoring `deselected` entirely.

## Wired end to end, 2026-08-20

No longer dormant. `gate_payload` takes `deselected`, and `release_payload` computes it: a release that **names** contents has, by naming them, held back every derived feature it did not name.

Proved against `your-trainer` in both directions:

| | blocking |
|---|---|
| names nothing (the eleven-historical-releases case) | **59** |
| names 3 of 32, none of which carry blocking checks | **59** |
| holds back `FEAT-0047`, which carries one | **58** |

**And the first wiring could never fire.** It read `held.get("features")` — and `_releases()` builds `id/title/status/version/date/platform` with **no `features` key**, so `named` was empty every time. The invariant test passed either way; it is the **positive** case that caught it. It reads the note's own frontmatter now, and a guard asserts that against the block rather than the whole function — the frozen branch reads `held.get("features")` legitimately, and a blanket search forbade it.
