---
type: "[[issue]]"
id: ISS-0094
aliases: ["ISS-0094"]
title: "An agent's permission prompt is detected but not answerable, so the one thing most likely to stall an unattended worker sits outside the queue the stall alarm watches"
status: open
severity: high
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Comparison against t3.codes, 2026-08-05: T3 persists ProjectionPendingApprovals — approval requests as durable, queryable state answerable from any surface"]
component: server
related: ["[[FEAT-0076-Escalation-With-Defaults]]", "[[FEAT-0062-Desk-Resolution-Flows]]", "[[RISK-0006-The-Unattended-Worker]]"]
fixed_by: []
tests: []
---

# Permission prompts are detected but not answerable

## What

`agent_hooks.py` maps `PermissionRequest → needs-input` and the landing shows an amber "waiting for your input" card. That is **detection**. Answering still means finding the terminal and typing into it.

T3 Code models the same event as durable state — `ProjectionPendingApprovals`, with an approval id, thread, turn, status and decision, persisted through restarts and answerable from any client including the phone. The prompt is a first-class record there; here it is a colour.

## Why this is a hole and not a wish

[[FEAT-0076]] establishes the invariant **nothing in the system can wait silently without bound** — timeouts per queue kind, proceed-on-assumption, the stall alarm. Every one of those mechanisms watches *the review queue*.

**A tool-permission prompt is not a queue entry.** So the most likely way an unattended worker stops — an agent asking "may I run this command?" — is precisely the way the alarm cannot see. The worker is not idle, not failed, not budget-exhausted; it is blocked, and the loop's own supervision is blind to it.

That makes this a defect in something already designed rather than a new feature: FEAT-0076 does not deliver its own acceptance criterion while this is true.

## Fix

Promote permission requests to the same footing as queue entries:

1. Persist them (id, session, prompt text, options, status, decision, timestamps) so they survive a restart and can be queried.
2. Surface them on the desk beside questions — the obligation grammar already exists.
3. Answer from the cockpit, delivered to the waiting session over the dispatch channel [[FEAT-0062]] already uses for answers.
4. Bring them under FEAT-0076's clock: a timeout, a policy default where one is safe (never for anything the delegation reserves), and the alarm when there is none.

## Evidence it is fixed

A permission prompt raised by a dispatched agent can be answered without touching the terminal, survives a cockpit restart, and appears in the stall alarm's coverage drill alongside the queue kinds.
