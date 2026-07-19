---
type: "[[task]]"
id: TASK-0119
aliases: ["TASK-0119"]
title: "Needs-input inbox — cross-workspace bell + jump-to-terminal"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0020-Agent-Activity-Surfaces]]"
effort: "M"
depends: ["[[TASK-0114]]"]
blocks: []
related: []
tests: []
---

# Needs-input inbox

## Definition of Done
- [ ] Top-bar bell with badge count aggregates needs-input events across all workspaces ("workspace — Claude wants permission to run `npm test`").
- [ ] Clicking an entry switches to that workspace and focuses its terminal.
- [ ] Entries clear when the underlying session unblocks or ends; ordered most-recent first.

## Steps
- [ ] Extend the agent-state poller/SSE fan-out to carry the needs-input message + timestamp.
- [ ] Bell + popover UI in the top bar; badge count.
- [ ] Jump wiring via existing `openWorkspace` + terminal toggle.

## Notes
Antigravity's Inbox is the pattern; ours is local multi-workspace. The `.cockpit/agent-state.json` poller already crosses workspaces — extend its payload rather than adding a new channel.
