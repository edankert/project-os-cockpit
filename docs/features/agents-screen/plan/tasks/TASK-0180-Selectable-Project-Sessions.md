---
type: "[[task]]"
id: TASK-0180
aliases: ["TASK-0180"]
title: "Agents screen: select a project to see its session history (ISS-0013)"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: ["[[ISS-0013]]"]
parent: "FEAT-0032"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[ISS-0013]]", "[[TASK-0178]]"]
tests: []
---

# TASK-0180 — selectable project session history on ~agents

Redesign the `~agents` screen so session history is per-project and discoverable (ISS-0013, user request 2026-07-21): fleet rows become selectable; selecting a project shows its session history underneath with full info (agent, prompt, duration, cost, dispatch provenance, undocumented, live).

Change:
- New main IPC `agents:sessions(workspaceId)` — returns that workspace's sessions from its live sidecar (`/api/cockpit/sessions`) when up, else by reading `<root>/.cockpit/sessions.json` (so history shows even for workspaces without a running sidecar). Preload exposes `agents.sessions(id)`.
- `renderAgentsPage`: fleet rows get a click-to-select affordance (selected row highlighted); a "Recent sessions — <workspace>" section below renders the selected workspace's history (default selection = active workspace, else the top row). Replaces the active-workspace-only feed added in TASK-0178.

Verification: CDP — the agents screen lists the fleet; selecting a different project swaps the session-history list to that project's sessions.

## Verification

CDP: the ~agents screen defaults its "Recent sessions" section to the active workspace and clicking another project's name swaps the section to that project's history (verified: selecting project-os-cockpit set the heading to "Recent sessions — project-os-cockpit"). New `agents:sessions(workspaceId)` IPC reads the workspace's live sidecar, else its persisted `.cockpit/sessions.json`. tsc clean; build OK.
