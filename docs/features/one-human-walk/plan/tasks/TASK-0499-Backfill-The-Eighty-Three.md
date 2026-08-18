---
type: "[[task]]"
id: TASK-0499
aliases: ["TASK-0499"]
title: "Backfill `covers:` on the 83 acceptance tests that name nothing"
status: backlog
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
