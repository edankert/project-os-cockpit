---
type: "[[task]]"
id: TASK-0143
aliases: ["TASK-0143"]
title: "Desktop discovery files + poller-side decay"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0027-External-Session-Signal]]"
effort: "S"
depends: []
blocks: []
related: []
tests: ["[[TST-0015]]"]
---

# Desktop discovery files + poller-side decay

## Definition of Done
- [x] Desktop sidecars write `.cockpit/url` (removed at exit) — `cockpit` CLI works against the desktop app from external terminals.
- [x] The poller treats busy/waiting/needs-input older than the decay window as idle (decayed_from preserved).
