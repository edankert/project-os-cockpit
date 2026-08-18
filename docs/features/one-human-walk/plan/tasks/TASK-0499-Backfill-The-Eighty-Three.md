---
type: "[[task]]"
id: TASK-0499
aliases: ["TASK-0499"]
title: "Backfill `covers:` on the 83 acceptance tests that name nothing"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0124-Gating-Is-Derived-From-Covers]]"]
parent: "[[FEAT-0124-Gating-Is-Derived-From-Covers]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Backfill the eighty-three

**83 of 669 carry an empty `covers:`** — 12%, measured 2026-08-18 across all three suites. Under a derived gate they would gate nothing and leave the release without saying so, which is why this is a precondition rather than a clean-up.

**Some of the 83 may legitimately cover nothing** — a check about the product as a whole rather than about one feature. Those must be **stated as such rather than left ambiguous**, exactly as [[REQ-0040-One-Verification-Link]] handles the 25 system-wide tests: an honest empty is a different thing from an unfilled one, and only one of the two is safe to derive a gate from.

**Do not guess.** A backfill that invents a plausible `covers:` produces a gate that fires on the wrong item — worse than one that does not fire, and much harder to notice.

Done when: every acceptance test either names what it verifies or is explicitly recorded as covering nothing, with the count of each reported rather than inferred.

## Done 2026-08-18 — and the 83 turned out to be 9

**The number that mattered was never 83.** Measured by tier: **74 of the 83 are Tier 3**, which does not gate a release at all, and 66 of those sit in an area literally called *"Moved from Tier 1 / Tier 2 — Fully Automated"* — the promotion path TESTING.md describes, already performed by hand before there was tooling for it. **Only 9 are Tier 1/2**, and all 9 are `done`.

So the precondition this task existed to satisfy was a twelfth of its stated size, and none of it blocks anything today.

**They are not backfilled, and that is the decision rather than the omission.** All nine sit in areas that name a behaviour (*Split-Screen & Multi-Window*, *HRM State on User Switch*, *Add Rider with Zero Users*, *Empty Workout History*) and **not one of their area-siblings declares a `covers:` to inherit** — measured: 0 of 83. Writing a plausible feature id would produce a gate that fires on the wrong item, which this task's own instruction forbids and which is worse than one that does not fire.

**So the hole was closed in the gate instead**: `blocking_for` treats a check covering nothing as blocking, always. An unattributable check cannot be discharged by finishing any particular item, so it gates the last item there is. That converts a silent hole into a loud one without inventing data.
