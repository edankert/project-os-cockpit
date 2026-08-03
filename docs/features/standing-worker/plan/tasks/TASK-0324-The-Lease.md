---
type: "[[task]]"
id: TASK-0324
aliases: ["TASK-0324"]
title: "The lease — a claim that refuses a second worker, heartbeats, and expires loudly"
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

# The lease

## Definition of Done

- `.cockpit/lease.json`: worker id, item, acquired, heartbeat. Acquisition refuses while a live lease exists; the refusal names the holder.
- A lapsed heartbeat expires the lease as an **escalation event** — surfaced on the landing, never silently taken over.
- The lease never enters git (a claim is state, not record) and never substitutes for `focus` (the statement remains documentation, per ADR-0009's frame).
