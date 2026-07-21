---
type: "[[task]]"
id: TASK-0169
aliases: ["TASK-0169"]
title: "Usage freshness — 2-min fleet poll, manual refresh, as-of label"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
parent: "FEAT-0035"
effort: ""
due: ""
depends: ["[[TASK-0160]]"]
blocks: []
related: ["[[TASK-0150]]"]
tests: []
---

# TASK-0169 — usage freshness

Two related defects (user reports 2026-07-20): (1) the budget block only updated from the active workspace's live statuslines, so numbers froze when idle and missed newer readings from other workspaces; (2) rate limits are **account-global** but the block showed the *active workspace's* last reading, so switching projects showed different numbers depending on when each last ran a session — which is wrong.

Constraint: the statusline is the only rate-limit source, so a refresh can only surface the freshest reading any session emitted — never query the account directly.

Fix (option A + freshest-wins): the tracker stamps `captured_at` on each statusline cost snapshot; the fleet proxy exposes the full `rate_limits` + `captured_at` per workspace. The renderer keeps a single account-global reading and an `adopt-if-newer` gate — **every** source (the active session's live statusline AND the fleet poll) only replaces the displayed reading when its `captured_at` is newer. So switching workspaces never downgrades to an older reading, and the number is the same on every project. A 2-minute fleet poll (and on demand) picks the newest `captured_at` across all workspaces. A ↻ button sits to the right of the "Usage" title (spins while fetching); an "as of Xm ago" caption greys past 10 minutes.

Verification: CDP — seed rate_limits with a recent captured_at → block shows it with "as of …"; a second workspace with a newer captured_at wins after a poll/refresh; the refresh button triggers a re-fetch.
