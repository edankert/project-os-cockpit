---
type: "[[task]]"
id: TASK-0118
aliases: ["TASK-0118"]
title: "Activity strip above the terminal — prompt, tool, file, cost/context meters"
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

# Activity strip

## Definition of Done
- [ ] A slim strip above the terminal pane appears whenever an instrumented session is live: current prompt (truncated, expandable), current tool + file, context-fill meter, session cost, rate-limit gauge when available.
- [ ] Idle/waiting/needs-input states render distinctly; strip hidden when no instrumented session.
- [ ] Expanded state shows the "files touched this session" list.

## Steps
- [ ] Subscribe to `cockpit:agent-activity` / extended state SSE in the renderer.
- [ ] Strip DOM + CSS above `#terminal-pane`; meters from statusline snapshot in `/api/cockpit/state`.
- [ ] Wire expand/collapse; persist collapsed preference.

## Notes
Renderer is a non-module script — keep the subsystem in one clearly-delimited section of `renderer.ts` per existing convention.
