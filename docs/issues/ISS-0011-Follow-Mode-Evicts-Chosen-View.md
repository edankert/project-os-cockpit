---
type: "[[issue]]"
id: ISS-0011
aliases: ["ISS-0011"]
title: "Follow mode evicts the user's chosen view (incl. ~agents) — always-on in desktop, no Following/Manual toggle"
status: fixed
severity: medium
component: agent-focus
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
parent: "[[FEAT-0034-Agents-Tab-And-Follow-Control]]"
related: ["[[TASK-0158]]", "[[REQ-0020-View-Sovereignty]]"]
---

# ISS-0011 — follow mode evicts the chosen view

## Problem

User report 2026-07-19: the ~agents page "loses out to project file changes and gets replaced / loses focus." Diagnosis: it is not the file-change soft reload (`scheduleSoftReload` already skips `~`-prefixed virtual pages) — it is **follow mode**. The desktop shell hard-follows every `cockpit:focus` event (`agent-focus.ts` bridge → `agent:focus` IPC → unconditional `navigateTo`), so whenever a working agent runs `cockpit focus <id>` per the LIFECYCLE contract, the centre pane navigates there and evicts whatever the user deliberately opened — a doc they were reading or the ~agents fleet view. The browser cockpit (mode 1) has a Following/Manual toggle for exactly this; the desktop has none and even hard-codes `following: true` in its tab-state heartbeat.

## Impact

Any monitoring or reading activity in the centre pane is interruptible by agent activity — worst on the ~agents screen, whose whole purpose is to be watched while agents work.

## Fix direction

TASK-0158 (FEAT-0034): a Following/Manual toggle in the desktop matching mode-1 semantics (persisted per workspace), plus the REQ-0020 invariant — follow never evicts a virtual page the user opened deliberately, regardless of the toggle. Placement work (the centre Agents tab, TASK-0159) builds on this but the eviction fix stands alone.
