---
type: "[[task]]"
id: TASK-0145
aliases: ["TASK-0145"]
title: "Quit guard for live agents + resume hint after an unclean terminal death"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[ISS-0008-Terminal-Sessions-Die-With-App]]"]
parent: "FEAT-0007"
effort: ""
due: ""
depends: ["[[TASK-0144]]"]
blocks: []
related: ["[[ISS-0008]]"]
tests: []
---

# TASK-0145 — quit guard + death hint

## Goal

Two softer protections around TASK-0144. **Quit guard:** `before-quit` checks the poller's last-known agent states; if any workspace is `busy`/`needs-input` *and* its terminal is not tmux-backed (fallback mode), a sync dialog warns "quitting kills these agents" with Cancel as default — tmux-backed agents survive quits, so no dialog for them. **Death hint:** when a fallback (non-tmux) terminal spawns and the workspace's `.cockpit/sessions.json` shows a recent session with no `SessionEnd`, main fans a display-only line through `terminal:data` — `⚡ previous claude session died with the app — claude --resume <id>` — before the prompt; nothing is typed into the shell.

## Verification

Guard: covered by code review + manual (dialog requires GUI). Hint: exercised by pointing a fallback spawn at a fixture `sessions.json` with an unended entry.
