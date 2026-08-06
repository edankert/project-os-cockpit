---
type: "[[task]]"
id: TASK-0344
aliases: ["TASK-0344"]
title: "The strip says what the session weighs and whether its cache is warm, cooling or cold"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: ["[[TASK-0343-The-Cache-Reader]]"]
blocks: []
related: ["[[FEAT-0020-Agent-Activity-Surfaces]]"]
tests: []
---

# The strip says what the session weighs and whether its cache is warm, cooling or cold

## Definition of Done
- [x] The agent snapshot carries a `cache` block for the live session, so the strip renders without a second fetch.
- [x] The strip shows prefix weight in tokens beside the existing `ctx %` — the fill ratio and the absolute weight are different facts and both are wanted.
- [x] The strip shows `warm`, `cooling <n>m`, or `cold`, derived from elapsed time against the known 1h TTL.
- [x] When cold, the strip names the estimated re-write cost of the next turn (`~$1.40`), derived from the measured prefix rather than a constant.
- [x] `GET /api/cockpit/session-cache` serves the retrospective scan for the workspace.
- [x] The strip degrades silently when there is no transcript, no usage data, or an unreadable file — hidden, never an error state.
- [x] Estimates read as estimates: `~` prefix, hard rounding.
- [x] No polling loop is added; the block rides the snapshot that already refreshes.

## Steps
- [x] Wire `session_cache` into `AgentTracker.snapshot()` behind the existing mtime memoisation.
- [x] Serve the endpoint in `server.py` alongside `/api/cockpit/sessions`.
- [x] Extend `AgentCostSnapshot` / add a `cache` interface in `renderer.ts`; render in `renderAgentStripCost`'s neighbourhood.
- [x] Markup + CSS for the badge, matching the existing `meter-hot` treatment for the cold state.

## Notes
The strip is session-scoped by an existing decision (FEAT-0035/TASK-0160 moved account-global rate limits out of it to the left pane). Cache state is session-scoped, so it belongs here; the retrospective per-repo figure is **not**, which is why it gets an endpoint and no strip real estate in this task.

`ctx 62%` and `640k tokens` are not redundant: the first is fill against the window and drives compaction anxiety, the second is what a cold turn re-writes and drives the cost.
