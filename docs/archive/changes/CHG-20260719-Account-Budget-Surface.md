---
type: "[[change]]"
id: CHG-20260719-Account-Budget-Surface
aliases: ["CHG-20260719-Account-Budget-Surface"]
title: "Account budget surface — 5h/7d bars in the left pane, burn projection; strip goes session-pure"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
impacts: ["agent strip (5h pip removed)", "attention panel (budget block added)"]
issues: []
features: ["[[FEAT-0035-Account-Budget-Surface]]"]
related: ["[[TASK-0160]]", "[[TASK-0161]]", "[[TASK-0149]]"]
---

# Account budget surface (FEAT-0035)

## Summary

**TASK-0160.** The 5h/7d rate-limit budgets — account-scoped facts — moved from the session strip (where the TASK-0149 pip was a scope violation) to a block at the foot of the attention panel: thin bars (green <60%, amber ≥60%, red ≥85%), used %, and a "5h resets HH:MM" caption. The freshest `rate_limits` sample from any live session's statusline feeds it (`noteRateLimits`); the panel shows the block whenever budget data exists, even with zero attention rows. The session strip now carries only session-scoped meters (ctx%, $).

**TASK-0161.** Burn projection: a 15-minute ring of `(ts, used%)` samples per window; when the slope is positive and the window would hit 100% before it resets, the caption appends "~Xh Ym left at this rate" (suppressed when the reset comes first).

## Verification

CDP end-to-end: budget block renders 5h (76%, amber, 76% bar) + 7d (31%) with the reset caption; `#agent-strip-rl` is gone; feeding rising 5h samples over ~64s produced "~1m left at this rate". `tsc` clean.

Files: `desktop/src/renderer/{index.html,renderer.ts,renderer.css}`.
