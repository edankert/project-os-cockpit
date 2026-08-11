---
type: "[[issue]]"
id: ISS-0094
aliases: ["ISS-0094"]
title: "An agent's permission prompt is detected but not answerable, so the one thing most likely to stall an unattended worker sits outside the queue the stall alarm watches"
status: fixed
severity: high
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
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

## Fixed — 2026-08-11

`src/project_os_cockpit/approvals.py` — a permission prompt now has an id, a status, a decision and a clock, persisted in `.cockpit/approvals.json`.

**The hole, closed.** [[FEAT-0076]]'s alarm watches the review queue, and a tool-permission prompt was not a queue entry — so the most likely way an unattended worker stops (*"may I run this command?"*) was precisely the way the alarm could not see it. Not idle, not failed, not budget-exhausted: **blocked, with the supervision blind.** `permission` is now a kind in `DEFAULT_POLICY`, so a stalled prompt reaches `alarm` through the same sweep as everything else. One clock; a second sweep for prompts would drift from the first.

**No default, deliberately, and this is the judgment that matters.** Every other kind lapses into a recorded assumption. A permission request asks to take an action with effects *outside* the record — running a command, writing where the cockpit does not guard — so lapsing it into "yes" would be the system granting itself authority nobody delegated, and lapsing into "no" would silently change what the agent did. It has a one-hour timeout that makes it **alarm**, and never an assumption.

**An agent may not answer its own prompt.** The whole point is that a *different party* decides; an agent answering its own is the loop granting itself the authority the prompt exists to withhold. `agent:*` is refused (except `agent:principal`, [[ADR-0009]]'s delegated role), and an unattributed answer is refused too.

Three smaller properties, each with a test: a retried hook delivery does **not** become a second obligation (the lesson the review store learned when 16 concurrent offers produced 9 indistinguishable rows); a prompt **survives a restart**, because detection that evaporates leaves the worker blocked and the record with no memory of why; and answering twice does not overwrite the first decision — a decision is a record of what somebody chose, not a mutable field.

`GET /api/cockpit/approvals` lists them with their escalation state; `POST /api/cockpit/approve` answers, loopback-guarded like every write path — it changes runtime state rather than `docs/`, but it authorises an agent to act, which is a larger thing than editing a note.

**What is not done here**: delivering the answer back into the waiting session over the dispatch channel. That is the fix's step 3 and it needs the session-side half; the prompt is now visible, answerable and *counted*, which is the part the alarm needed.
