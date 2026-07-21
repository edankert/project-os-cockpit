---
type: "[[task]]"
id: TASK-0178
aliases: ["TASK-0178"]
title: "Overview declutter — drop agent surfaces; session history moves to the ~agents screen"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: []
parent: "FEAT-0022"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0127]]", "[[TASK-0148]]", "[[FEAT-0032-Agents-Screen]]"]
tests: []
---

# TASK-0178 — overview declutter, session history to ~agents

The overview page duplicated agent information now that agents have dedicated homes (rail dots, activity strip, attention inbox, the `~agents` fleet screen, session-detail pages). Per user (2026-07-21): drop the right-pane "Agents" one-liner and the "Agent sessions" feed column from the overview so it is purely project-focused — but keep a session-history list reachable somewhere.

Change:
- Overview right pane no longer renders the agent one-liner (`buildNowSection` removed from `renderOverviewRightPane`; the `updateOverviewNowCard` refresh and its caller removed). Scope pane still shows Linked/Backlinks; project scope shows Pinned.
- Overview feeds grid drops the sessions column — `buildFeedsGrid` renders a single full-width "Recent activity".
- Session history relocates to the `~agents` fleet screen: `renderAgentsPage` appends the existing session list (`buildSessionsFeed`) as a "Recent sessions" section below the fleet rows (the "fleet log" the code already anticipated). The agent-activity SSE refresh that re-fetched the sessions feed now targets `~agents` instead of `~overview`.
- The live-session banner under the hero is unchanged (only shows during an active session).

Verification: CDP — overview right pane has no Agents line and no sessions column (single Recent-activity feed); the `~agents` screen shows the fleet plus a "Recent sessions" list.

## Verification

CDP: the Overview right pane has no Agents line (no #ov-right-now / .now-oneliner), the feeds area is a single full-width Recent activity column (.ov-feeds-single, no sessions h3); the ~agents screen shows the fleet list plus a "Recent sessions" section (.agents-sessions) with the session history (6 rows). tsc clean; build OK.
