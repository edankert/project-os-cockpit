---
type: "[[task]]"
id: TASK-0324
aliases: ["TASK-0324"]
title: "The lease — a claim that refuses a second worker, heartbeats, and expires loudly"
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

# The lease

## Definition of Done

- `.cockpit/lease.json`: worker id, item, acquired, heartbeat. Acquisition refuses while a live lease exists; the refusal names the holder.
- A lapsed heartbeat expires the lease as an **escalation event** — surfaced on the landing, never silently taken over.
- The lease never enters git (a claim is state, not record) and never substitutes for `focus` (the statement remains documentation, per ADR-0009's frame).

## The decision this task also makes

DES-0009's open question (added 2026-08-05 from the t3.codes comparison): **refuse a second worker, or isolate it in its own git worktree?** T3 does the latter and treats the worktree as a property of a thread.

This task ships the refusal and **records why** — the constraint here is judgment, not throughput, and a worker outrunning its supervisor's reading is not a win. The reversible choice goes first. If a later round wants throughput, worktrees reopen as their own work with the merge and per-tree-validation costs stated up front.

## Done — 2026-08-11

`.cockpit/lease.json` — worker id, item, acquired, heartbeat.

**A refusal names the holder.** "Refused" with no name is a dead end; with a name it is a question somebody can answer.

**An expired lease is an escalation, never an opening.** A worker that silently took over a stale lease would make *two workers on one repo* indistinguishable from *one worker with a slow heartbeat* — and those need opposite responses. Acquisition refuses with the expiry reason in hand, so taking over is a separate decision somebody makes deliberately.

An unreadable lease expires rather than being trusted: a heartbeat that cannot be parsed is not a heartbeat.
