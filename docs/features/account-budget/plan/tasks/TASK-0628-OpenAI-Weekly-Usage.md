---
type: "[[task]]"
id: TASK-0628
aliases: ["TASK-0628"]
title: "Show OpenAI weekly usage beside Claude"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
parent: "FEAT-0035"
depends: []
blocks: []
related: ["[[ISS-0312]]", "[[CHG-20260916-Show-OpenAI-weekly-account-usage]]"]
tests: ["[[TST-0090]]"]
---

# Show OpenAI weekly usage beside Claude

Read the signed-in Codex account's general weekly allowance through `account/rateLimits/read`. Select the 10,080-minute window from either primary or secondary in the `codex` bucket. Show percent used, the existing green/amber/red bar, provider name, reset date, and reading age. Never substitute a model-specific bucket or zero for missing data.

Read in Electron main with a bounded subprocess lifetime and shared two-minute cache. Claude keeps its existing statusline source. An unavailable OpenAI read keeps the last observed reading with its original timestamp; a successful response with no weekly allowance clears the old reading. No Codex thread, prompt, login, or configuration write is requested.

## Verification

See [[TST-0090]].

## Completed 2026-09-16

Desktop build and all eight focused quota/renderer checks pass. The implemented reader returned 43% used with reset `2026-09-23T09:05:27Z`. An isolated Electron window rendered the actual desktop bundle with that live reading beside Claude; the OpenAI bar was green and the reset caption read `7d resets Wed, 23 Sept, 10:05`. The desktop shell was restarted by its verified PID; tmux owns the active terminals.
