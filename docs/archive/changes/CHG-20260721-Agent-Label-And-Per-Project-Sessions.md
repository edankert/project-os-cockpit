---
type: "[[change]]"
id: CHG-20260721-Agent-Label-And-Per-Project-Sessions
aliases: ["CHG-20260721-Agent-Label-And-Per-Project-Sessions"]
title: "Agent label follows the live signal; ~agents screen gets per-project session history"
status: merged
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-21
review_verdict: approved
impacts: ["fleet row + strip agent derivation", "~agents screen session history", "new agents:sessions IPC"]
issues: ["[[ISS-0012]]", "[[ISS-0013]]"]
features: ["[[FEAT-0032-Agents-Screen]]", "[[FEAT-0033-Agent-Signal-Hygiene]]"]
related: ["[[TASK-0179]]", "[[TASK-0180]]"]
---

# Agent label + per-project session history

## Summary (ISS-0012)

The workspace agent/framework label followed a stale `last_session` — a leftover one-off codex session made a live claude workspace appear to be running codex, contradicting the (correct) rail dot. Fixed at the two derivation points: the fleet proxy (`agents-fleet.ts`) now keeps the live poller/agent-state agent and only lets `last_session` override for a genuinely live session; the agent strip (`showAgentStrip`) prefers `activity.agent` (live) over `session.agent`. The rail dot and strip no longer disagree; a genuinely-live codex session still shows codex.

## Summary (ISS-0013)

Session history (moved to `~agents` in TASK-0178) was undiscoverable and only showed the active workspace. The `~agents` screen is now **select-a-project**: fleet rows are selectable (click the name), and the "Recent sessions — <project>" section below shows that project's history with full info (agent, prompt, duration, cost, dispatch provenance, undocumented, live); it defaults to the active workspace. A new main IPC `agents:sessions(workspaceId)` sources sessions from the workspace's live sidecar, else its persisted `.cockpit/sessions.json`, so history shows even for projects whose sidecar isn't running.

## Verification

CDP: strip shows claude for a live claude workspace; fleet row shows the live agent; the ~agents section defaults to the active project and swaps to a clicked project's history. tsc clean; full build OK. (A leftover `codex-smoke` test session that triggered the original report was also cleaned.)

Independent review (opus) approved both fixes; its one worthwhile finding — the ~agents session section rebuilding uncached on every agent-state event (flicker/refetch) — was addressed with a short per-workspace cache on `agents:sessions` (and an async file read).

Files: `desktop/src/ipc/agents-fleet.ts`, `desktop/src/preload.ts`, `desktop/src/renderer/renderer.ts`.
