---
type: "[[task]]"
id: TASK-0327
aliases: ["TASK-0327"]
title: "The actions endpoint answers per caller identity, and a delegate's writes carry their authority"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0075-The-Delegation-Policy]]"]
parent: "[[FEAT-0075-The-Delegation-Policy]]"
effort: M
depends: ["[[TASK-0326-The-Policy-Note]]"]
blocks: []
related: ["[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]"]
tests: []
---

# Role checks consult policy

## Definition of Done

- `GET /api/notes/actions` takes the caller (`user:…` or `agent:principal`); for a delegate it answers from the approved policy — outside-policy actions are neither offered nor performable (REQ-0030's two layers, the REQ-0026 pattern).
- Every delegate write stamps `(agent:principal, delegation: DELEGATION.md@<sha>)` — the audit answers who, under what authority, as the policy stood when.
- The hardening suite gains the delegate cases: no policy → no actions; draft policy → no actions; outside-threshold → refused with the policy line named.

## Done — 2026-08-11

`legal_actions(note_type, status, *, caller, policy)` — [[REQ-0030]]'s **first** layer.

A human sees the transition table as written. A **delegate** (`agent:*`) sees only what an *approved* policy names, so an out-of-policy action is **never offered** — rather than shown and then refused, which teaches a delegate to try.

| caller | policy | offered on a draft requirement |
|---|---|---|
| human | — | `Approve`, `Decline` |
| `agent:principal` | none | *nothing* |
| `agent:principal` | draft | *nothing* |
| `agent:principal` | approved, names `approve requirement` | `Approve` only |

**The second layer is the write path**, which checks the same policy again, because a display bug must not be able to widen authority. That is [[REQ-0026]]'s pattern applied one level up — and the reason this filter is not *the* guard: it is the offer.

**An unnamed caller is treated as human**, deliberately. Every existing call site passes no caller and keeps working unchanged; it is safe because a delegate is identified by *saying so*, while the guard that actually stops one lives where identity is checked rather than assumed. The alternative — defaulting to delegate — would have broken every human surface to protect against a caller that does not exist yet.

`delegation.stamp()` supplies the attribution a delegate write carries: *who, under what authority, as the policy stood when*. The sha matters because a policy that changed after the write would otherwise make the audit unanswerable.
