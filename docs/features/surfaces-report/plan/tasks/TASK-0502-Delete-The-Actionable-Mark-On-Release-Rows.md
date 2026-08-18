---
type: "[[task]]"
id: TASK-0502
aliases: ["TASK-0502"]
title: "Delete `gateMark`'s `actionable` parameter so no release row can write a check"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Delete `gateMark`'s `actionable` parameter so no release row can write a check

ADR-0035. The parameter is deleted, not defaulted to `false` — one value means the next caller re-litigates the decision. The `quiet` and `stale` groups already pass `false`; every group now renders the token as a plain span. Rows stay links.

Guard: a test that fails if a release page emits an element that can open the mark dialog. The control has now been removed from two surfaces (ISS-0192, then this) and neither removal left a test behind — which is why it came back.
