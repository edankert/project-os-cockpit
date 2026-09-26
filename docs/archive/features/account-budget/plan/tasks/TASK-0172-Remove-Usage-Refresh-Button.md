---
type: "[[task]]"
id: TASK-0172
aliases: ["TASK-0172"]
title: "Remove the Usage refresh button — no on-demand source, so it was decorative"
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

# TASK-0172 — remove the usage refresh button

The manual ↻ button (TASK-0169) can't fetch anything fresher than the last statusline any session emitted — there is no Claude API endpoint for the account's 5h/7d usage, and the statusline is the only source. So clicking it re-reads the same value and does nothing visible (user report 2026-07-20). Remove the button and its state/CSS. The 2-minute fleet poll stays (a silent backstop that adopts a newer reading when one appears), as does the "as of Xm ago" freshness caption. The separate question of getting live usage from sessions run outside the cockpit's terminal is a global statusline forwarder — deferred, not part of this task.

Verification: CDP — the budget block renders with the "as of" caption and no `.ws-budget-refresh` element; a newer statusline still updates the value (poll/live path intact).
