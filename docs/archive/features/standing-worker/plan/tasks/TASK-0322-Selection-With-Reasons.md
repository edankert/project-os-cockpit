---
type: "[[task]]"
id: TASK-0322
aliases: ["TASK-0322"]
title: "Selection with reasons — LIFECYCLE step 2 as code, every choice explained in the ledger"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0074-The-Standing-Worker]]"]
parent: "[[FEAT-0074-The-Standing-Worker]]"
effort: M
depends: []
blocks: ["[[TASK-0323-The-Session-Loop]]"]
related: []
tests: []
---

# Selection with reasons

## Definition of Done

- The picker implements LIFECYCLE step 2: the focus item when workable, else backlog by phase order, severity and the dependency graph; items parked by failure backoff are skipped.
- Every selection writes one ledger line: what was chosen and why, what was passed over and why — an unattended system's first duty is to be explainable afterwards.
- Given an empty workable backlog the picker returns idle, which is a stop condition, not a busy-wait.

## Done — 2026-08-11

`worker.select()` — LIFECYCLE step 2 as code, and **it explains itself**.

Order: the focus item when workable (a decision somebody already made; overriding it silently discards that), else phase order, then severity, then id. Parked items are skipped — an item that has failed twice would otherwise be chosen forever, which is the direction [[REQ-0031]] forbids failure from compounding.

**Every selection records what it passed over and why**, not just what it chose. *"Why not that one?"* is the question a person actually asks when a worker's choice looks wrong, and it cannot be answered from the choice alone — which makes the pass-over list the load-bearing half of an unattended system's explainability.

```
chose ISS-1 — first by phase order, then severity, then id | passed over:
TASK-3: status done is not workable; TASK-4: blocked on TASK-9; TASK-2: ranked below the choice
```

**An empty workable backlog returns `idle`, which is a stop condition** rather than a busy-wait: a loop that spins looking for work it will not find burns budget to discover nothing, repeatedly.

`review` and `blocked` are deliberately not workable — they are states where somebody else is mid-thought, and picking one up is taking work off a *person* rather than off a queue.

**The picker runs nothing.** It returns a choice and a reason; dispatching it is [[TASK-0323]], which is gated on [[RISK-0006]]'s supervised week.
