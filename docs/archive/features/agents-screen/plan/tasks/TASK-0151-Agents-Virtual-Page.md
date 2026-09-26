---
type: "[[task]]"
id: TASK-0151
aliases: ["TASK-0151"]
title: "~agents virtual page — fleet rows, aggregate header, jump actions"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[REQ-0019-Agent-Fleet-Visibility]]"]
parent: "FEAT-0032"
effort: ""
due: ""
depends: ["[[TASK-0150]]"]
blocks: []
related: []
tests: []
---

# TASK-0151 — ~agents virtual page

`~agents` joins the `~overview`/`~session` virtual-page family (mockup: review artifact §P3). One row per workspace (state + elapsed, prompt, last file, dispatch origin, queue depth, ctx/$, actions: terminal / session / queue); header aggregates burn, active count, rate budget. Entry points: rail button, inbox popover header, Now one-liner. Sessions-feed entry point moves here from ~overview. Verification: navigate, rows live-update on state SSE/IPC, jumps land correctly, history back/forward works.
