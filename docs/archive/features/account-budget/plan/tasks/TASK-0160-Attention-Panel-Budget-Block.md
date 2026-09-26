---
type: "[[task]]"
id: TASK-0160
aliases: ["TASK-0160"]
title: "Budget block at the attention-panel foot — 5h/7d bars + reset clock; strip pip removed"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0035"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0149]]"]
tests: []
---

# TASK-0160 — attention-panel budget block

Foot of `#ws-attention` (mockup: round-2 artifact §2-3): thin bars for the 5h and 7d windows with used %, colour thresholds (green <60, amber ≥60, red ≥85), reset time; visible whenever budget data exists for today, even with zero attention rows; hidden otherwise. Budgets are account-global, so the freshest sample from any live sidecar is authoritative (fleet proxy or active snapshot). Removes the strip's 5h pip (supersedes TASK-0149's placement) — the session rail then carries session facts only. Verification: statusline fixture → bars render with thresholds and reset time; pip absent from the strip; block hidden with no data.
