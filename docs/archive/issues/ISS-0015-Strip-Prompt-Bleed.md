---
type: "[[issue]]"
id: ISS-0015
aliases: ["ISS-0015"]
title: "Agent strip shows another project's prompt after switching workspaces (stale stripLastPrompt)"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: ["user-report"]
related: ["[[FEAT-0030]]", "[[TASK-0184]]"]
---

# ISS-0015 — agent strip leaks the previous workspace's prompt

## Symptom

After switching to a workspace (e.g. project-os-cockpit), the agent-state strip at the top of the console shows a prompt that was given to a *different* project (e.g. project-os-dev). Reported 2026-07-21.

## Root cause

`stripLastPrompt` in `desktop/src/renderer/renderer.ts` is a module-level string that `showAgentStrip` only ever assigns (from the live activity prompt or the session's `last_prompt`) — it is intentionally sticky so the strip keeps showing what the agent last did between runs within a workspace. But the workspace-switch reset (`openWorkspace`) clears `lastAgentSnap` and calls `showAgentStrip(null, null)` — which resets `stripSession` but leaves `stripLastPrompt` holding the previous workspace's prompt. When the newly-active workspace's session has no `last_prompt` of its own (an ended/quiet session, or — during the concurrent ISS-0014 investigation — a session with none), `showAgentStrip` falls through to render the stale `stripLastPrompt`, so another project's prompt bleeds into this project's strip.

## Fix

See [[TASK-0184]]: reset `stripLastPrompt` (and the per-session `workTransitions` map, same leak class) when switching workspaces, so the strip starts clean and only shows the active workspace's own prompt.
