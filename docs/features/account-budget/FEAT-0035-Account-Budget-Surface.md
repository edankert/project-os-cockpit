---
type: "[[feature]]"
id: FEAT-0035
aliases: ["FEAT-0035"]
title: "Account budget surface — 5h/7d rate limits in the left pane with reset countdown; session rail goes scope-pure"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
goal: "The 5-hour and 7-day rate-limit budgets — account-scoped facts — move to a compact block at the foot of the attention panel: thin bars with used %, the reset clock, and (stretch) a projected time-to-cap from the recent burn slope; hidden when no session ran today. The session rail sheds the 5h pip and shows only session-scoped facts (state, tool/prompt, session ctx%, session $). The ~agents header keeps its aggregate copy as the inspection surface."
requirements: []
tests: []
tasks: ["[[TASK-0160]]", "[[TASK-0161]]"]
related: ["[[FEAT-0031-Ambient-Status-Consolidation]]", "[[FEAT-0030-Agent-Inbox]]", "[[TASK-0149]]"]
---

# Account budget surface

## Why

User feedback 2026-07-19: the 5h limit belongs with the inbox in the left pane, with time remaining — and the session rail should carry only that session's information. Correct on both counts: rate limits are account-scoped, so the strip pip (TASK-0149) was a scope violation; this feature supersedes that placement (the pip is removed, not just moved). Mockup: round-2 artifact §2-3.

## Scope

- **TASK-0160:** budget block at the attention-panel foot — 5h + 7d bars (green <60%, amber ≥60%, red ≥85%), reset time, tooltip detail; panel shows the block whenever budget data exists for today even with zero attention rows; strip pip removed.
- **TASK-0161 (stretch):** burn projection — tracker stores a short ring of (ts, used%) samples per window; the block renders "~1h 05m left at current burn" when the slope is meaningful.

## Data

`rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}` already captured per statusline tick and normalised to ISO at ingest; cross-workspace delivery can reuse the fleet proxy or the freshest active-workspace snapshot (budgets are account-global, so any live session's sample is authoritative).
