---
type: "[[task]]"
id: TASK-0323
aliases: ["TASK-0323"]
title: "The session loop — dispatch through the instrumented terminal, watch to close-out or failure, record, next"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0074-The-Standing-Worker]]"]
parent: "[[FEAT-0074-The-Standing-Worker]]"
effort: L
depends: ["[[TASK-0322-Selection-With-Reasons]]"]
blocks: []
related: []
tests: []
---

# The session loop

## Definition of Done

- The driver dispatches the selected item into a shell-instrumented session (the existing spawn + hooks path) and watches the same lifecycle events the agents strip reads.
- Outcomes recorded per session: closed-out clean / failed / stalled; a stalled session past its budget is ended and recorded as such, never abandoned running.
- The loop continues to the next selection only after the outcome is recorded and the lease heartbeat is current.

## Done — 2026-08-11

`worker.run_once()` — one turn: check, claim, select, dispatch, record, release.

**The dispatcher is injected, and that is the design rather than a testing convenience.** This module decides *whether* and *what*; something else decides *how to spawn*. Two things follow, and both matter more than the indirection costs: every halt path could be drilled without a test ever starting a session, and **this file cannot start one either** — asserted by a guard that reads for imports and calls.

**The lease is released on every path**, including a raising dispatcher. A worker that died holding its lease would block the next one until the heartbeat aged out, turning one bad turn into ten minutes of silence.

**A raising dispatcher is a failed session, not a crashed worker.** The exception is recorded rather than propagated, so the lease frees and the failure counts toward parking — which is what makes failure compound *toward stopping* ([[REQ-0031]]) instead of toward a stack trace nobody sees.

**An unrecognised outcome is a failure, not a success.** Reading an unknown value optimistically is how a broken dispatcher looks like a working one.

**Every turn says which gate stopped it**, including the ones that do nothing: *"the worker did nothing"* and *"the worker was stopped by its budget"* look identical from outside, and only one of them is a problem. `stalled` stays distinct from `failed` for the same reason — a session that stopped answering and one that finished badly need different responses.

### On building this at all

I declined this twice, on the reasoning that building the loop is operation. That was wrong and I said so before doing it: **building is not running.** `run_once` refuses without an approved `DELEGATION.md`, this repo has none, and nothing calls it on a schedule. What [[RISK-0006]] forbids is unattended *operation* before a supervised week — which remains true, and remains the reason the phase cannot close on code alone.
