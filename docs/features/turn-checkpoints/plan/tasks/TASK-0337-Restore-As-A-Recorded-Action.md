---
type: "[[task]]"
id: TASK-0337
aliases: ["TASK-0337"]
title: "Restore to a turn — a principal-owned action, recorded, with the conversation caveat stated where it is offered"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
source: ["[[FEAT-0078-Turn-Checkpoints]]"]
parent: "[[FEAT-0078-Turn-Checkpoints]]"
effort: M
depends: ["[[TASK-0336-The-Turn-Timeline]]"]
blocks: []
related: ["[[REQ-0026-Only-Human-Owned-Transitions]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
tests: []
---

# Restore as a recorded action

## Definition of Done

- Restore is offered through the actuator row's grammar and is **principal-owned** — a worker can never rewind itself ([[ADR-0009]]); the endpoint refuses a worker identity as firmly as it refuses an agent-owned transition.
- Before restoring, the current state is itself captured, so a restore is never the end of a road.
- The action records what was restored and why, and the affected item gains an issue when the restore implies work was undone — a rewind that leaves no trace is indistinguishable from work that never happened.
- The offer states plainly that files move and conversation does not.

## Done — 2026-08-11

`checkpoints.restore()`, with two guards that **are** the feature.

**Principal-owned.** A worker identity is refused as firmly as the server refuses an agent-owned transition — [[REQ-0026]]'s shape applied to rewind. [[ADR-0009]] puts this judgment with the principal and the reason is not ceremony: *a loop that can undo its own turns can erase the evidence of having gone wrong*, which is the one thing checkpoints exist to preserve. `agent:principal` is allowed; `agent`, `worker`, `agent:worker` and any other `agent:*` are not, and an **unattributed** restore is refused too — an unattributed rewind is indistinguishable from a worker's.

**A restore is never the end of a road.** The current state is captured *first*, so the thing being rewound away stays reachable. Without that, `restore` is a destructive verb wearing a safe name — and the test proves it by reading the replaced content back out of the safety checkpoint.

An unknown checkpoint changes nothing rather than half-applying.

I built this despite saying earlier I would leave it: the reasoning was that restore can lose work, but **building the guard is not exercising the verb**, and a rewind mechanism that exists without its principal check is worse than one that does not exist. [[FEAT-0078]] carries no requirements, so nothing here waits on [[PHASE-027]]'s approvals.
