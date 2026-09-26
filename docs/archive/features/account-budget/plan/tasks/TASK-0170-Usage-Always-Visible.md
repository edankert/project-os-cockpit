---
type: "[[task]]"
id: TASK-0170
aliases: ["TASK-0170"]
title: "Usage block always-visible — persist the last reading, load on startup"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
parent: "FEAT-0035"
effort: ""
due: ""
depends: ["[[TASK-0169]]"]
blocks: []
related: []
tests: []
---

# TASK-0170 — usage block always-visible

The usage block is account-global, so it should always be visible — but it only appeared once a reading existed in memory, so it was hidden on a fresh launch and whenever the active workspace had no session (user report 2026-07-20). Fix: persist the freshest reading (`{rate_limits, captured_at}`) to localStorage on every adopt, load it on startup so the block renders immediately (with an honest "as of Xh ago"), and kick a `pollUsage()` on startup + after the first workspace opens so it refreshes from any live sidecar. The block still hides only when no reading has EVER been received (nothing truthful to show); once seen, it persists across restarts and workspace switches.

Verification: CDP — seed a reading, relaunch → block visible immediately from persistence with an aged "as of"; a fresh statusline updates it.
