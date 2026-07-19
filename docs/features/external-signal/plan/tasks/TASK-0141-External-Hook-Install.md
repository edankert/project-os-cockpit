---
type: "[[task]]"
id: TASK-0141
aliases: ["TASK-0141"]
title: "External agent-state hook + managed ~/.claude install/uninstall"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0027-External-Session-Signal]]"
effort: "M"
depends: []
blocks: []
related: []
tests: ["[[TST-0015]]"]
---

# External agent-state hook + managed ~/.claude install/uninstall

## Definition of Done
- [x] Generated Python hook (userData/external-hook/): no-op outside project-os repos; POSTs to the sidecar via `.cockpit/url` when present; else writes `.cockpit/agent-state.json` atomically with `source: external-hook`.
- [x] Install adds marker-identified entries to `~/.claude/settings.json` (one-time backup); uninstall removes exactly ours; malformed user settings abort untouched.
