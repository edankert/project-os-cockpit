---
type: "[[task]]"
id: TASK-0161
aliases: ["TASK-0161"]
title: "Burn-rate projection — '~1h 05m left at current burn' from recent usage samples"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0035"
effort: ""
due: ""
depends: ["[[TASK-0160]]"]
blocks: []
related: []
tests: []
---

# TASK-0161 — burn-rate projection

The tracker keeps a short ring of `(ts, used_percentage)` samples per rate-limit window (statusline ticks arrive ≤ every 5s; a dozen samples spanning ~10min suffice); the budget block renders "~Xh Ym left at current burn" when the slope is positive and meaningful, capped by the reset time (whichever comes first wins the label: "resets before you'd hit it" vs the projection). No projection shown for flat/negative slopes. Verification: pytest over the slope math (rising, flat, resets-first cases); fixture-driven render check.
