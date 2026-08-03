---
type: "[[task]]"
id: TASK-0322
aliases: ["TASK-0322"]
title: "Selection with reasons — LIFECYCLE step 2 as code, every choice explained in the ledger"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
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
