---
type: "[[task]]"
id: TASK-0158
aliases: ["TASK-0158"]
title: "Following/Manual toggle in the desktop + follow never evicts a virtual page"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[ISS-0011-Follow-Mode-Evicts-Chosen-View]]", "[[REQ-0020-View-Sovereignty]]"]
parent: "FEAT-0034"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0158 — follow toggle + eviction guard

Desktop parity with mode-1's Following/Manual control: a visible toggle (chrome placement near the doc header or footer), persisted per workspace, honoured by the `agent:focus` IPC handler; the tab-state heartbeat reports the real value instead of hard-coding `following: true`. Independent of the toggle, an automatic navigation never replaces a `~` virtual page the user opened — the suppressed jump stays available via the existing "Agent focus → …" toast (made clickable). Fixes ISS-0011. Verification: with Manual set, `cockpit focus` changes nothing but shows the toast; with Following set, focus navigates docs but never off ~agents/~overview/~session.
