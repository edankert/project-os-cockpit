---
type: "[[feature]]"
id: FEAT-0020
aliases: ["FEAT-0020"]
title: "Agent activity surfaces — activity strip, needs-input inbox, live nav trail"
status: in-review
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
goal: "Make the instrumented agent visible: a live activity strip above the terminal (current prompt, tool, file, cost/context meters), a cross-workspace needs-input inbox, and live attribution badges in the nav for notes the agent just touched."
requirements: []
tests: ["[[TST-0011]]"]
tasks: ["[[TASK-0118]]", "[[TASK-0119]]", "[[TASK-0120]]"]
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0013-Agent-State-Signal]]"]
---

# Agent activity surfaces

## Why

FEAT-0019 gives the cockpit a structured feed of what the agent is doing, but the only current visualisations are the rail dots and OS notifications. Competing tools show where the bar is: Warp renders per-tab agent status, Crystal/Nimbalyst pioneered explicit running/waiting-for-input indicators, and Antigravity routes blocked agents to an Inbox. The cockpit is already multi-workspace with per-workspace PTYs — it is the natural place for a cross-project view of agent attention.

## Goal

At a glance, the user can see what each agent is working on, whether any agent needs them, and which notes the agent is touching right now — without switching to the terminal pane.

## Scope

1. **Activity strip.** A slim strip above the terminal pane (visible whenever an instrumented session is live): current prompt text (truncated, expandable), current tool + file being touched, context-fill meter, session cost, and rate-limit gauge when the statusline forwarder provides it. Idle/waiting states render distinctly.
2. **Needs-input inbox.** A cross-workspace queue fed by needs-input events: "your-trainer — Claude wants permission to run `npm test`". Surfaced as a top-bar bell with badge count and a popover list; clicking an entry switches workspace and focuses the terminal. Entries clear when the underlying session unblocks.
3. **Live nav trail.** When the agent edits a note under `docs/`, badge/flash that item in the left nav and right pane (attribution: "the agent touched this, just now") — distinct from the existing SSE soft-reload, which refreshes content but attributes nothing. For files outside `docs/`, maintain a "files touched this session" list, shown in the activity strip's expanded state.
4. **Rail dot refinement.** Extend the existing dot vocabulary so needs-input is visually distinct from busy and waiting across the rail, dock badge, and notifications.

## Out of scope

- Ingestion/wiring (FEAT-0019).
- Session history and traceability (FEAT-0022).
- Any diff rendering — the trail links to notes, not to diffs.

## Acceptance

- During a real Claude Code session, the strip shows the current prompt, updates the touched file live during edits, and the cost/context meters move.
- With agents blocked in two workspaces at once, the inbox lists both, ordered most-recent first, and clicking each jumps to the right workspace terminal.
- Editing a TASK note from the agent flashes exactly that nav row within SSE latency; the badge decays after a short interval.
- No instrumented session → strip hidden, inbox empty, zero visual noise (current behaviour preserved).

## Links

- Tasks: to be broken down (`plan/PLAN.md`)
- Render surface: `desktop/src/renderer/renderer.ts` (terminal pane, rail, nav renderers)
