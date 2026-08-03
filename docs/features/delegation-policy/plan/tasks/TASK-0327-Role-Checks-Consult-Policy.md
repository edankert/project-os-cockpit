---
type: "[[task]]"
id: TASK-0327
aliases: ["TASK-0327"]
title: "The actions endpoint answers per caller identity, and a delegate's writes carry their authority"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
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
