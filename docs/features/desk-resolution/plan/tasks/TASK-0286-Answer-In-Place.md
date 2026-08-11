---
type: "[[task]]"
id: TASK-0286
aliases: ["TASK-0286"]
title: "Answer a queue question inline — resolved with the answer as outcome, delivered to the asking session"
status: cancelled
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0062-Desk-Resolution-Flows]]"]
parent: "[[FEAT-0062-Desk-Resolution-Flows]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Answer in place

## Definition of Done

- A question entry renders an answer field; submit calls `review-resolve` with the answer as `note`.
- A live asking session receives the answer over its dispatch channel; a dead one degrades to the answer displayed for copy — stated, not silent.
- The resolved entry leaves the queue and survives in the ledger with its answer.
