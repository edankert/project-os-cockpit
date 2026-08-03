---
type: "[[task]]"
id: TASK-0326
aliases: ["TASK-0326"]
title: "DELEGATION.md — what is delegated, what escalates, approved through the gate it configures"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0075-The-Delegation-Policy]]"]
parent: "[[FEAT-0075-The-Delegation-Policy]]"
effort: M
depends: []
blocks: ["[[TASK-0327-Role-Checks-Consult-Policy]]"]
related: []
tests: []
---

# The policy note

## Definition of Done

- Format per DES-0009: `delegate:` entries (judgment, to whom, threshold) and `escalate:` entries (kind, timeout, default); a template ships with everything commented out — the empty policy delegates nothing.
- The note is approved through the actuator row (requirement-style approve), and only an **approved** policy is consulted; a draft policy is no policy.
- Amending it re-enters draft and re-approval — authority does not drift by edit.
