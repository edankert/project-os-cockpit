---
type: "[[task]]"
id: TASK-0159
aliases: ["TASK-0159"]
title: "Centre tab strip — doc tab + pinned Agents tab while ~agents is open"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[REQ-0020-View-Sovereignty]]"]
parent: "FEAT-0034"
effort: ""
due: ""
depends: ["[[TASK-0158]]"]
blocks: []
related: ["[[TASK-0151]]"]
tests: []
---

# TASK-0159 — agents centre tab

A slim tab strip appears on the centre pane only while ~agents is open (mockup: round-2 artifact §1 option A): the doc tab carries normal navigation/history; the Agents tab is pinned and hosts the fleet view with its own scroll state; opening ~agents from any entry point (rail button, Now line, finished line) activates the tab instead of replacing the doc; follow-mode and user navigation land on the doc tab in the background; closing the Agents tab collapses the strip. Keyboard: ⌘⇧A toggles, ctrl-tab cycles. Verification: navigate docs while Agents is open — the doc tab updates, Agents keeps scroll; dispatch from the fleet, jump back; history back/forward stays coherent per tab.
