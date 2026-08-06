---
type: "[[issue]]"
id: ISS-0104
aliases: ["ISS-0104"]
title: "Switching model mid-session discards the whole warm prefix, and nothing anywhere says so"
status: fixed
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
severity: medium
component: "agent-hooks"
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[FEAT-0019-Agent-Hook-Ingestion]]"]
tests: []
---

# Switching model mid-session discards the whole warm prefix, and nothing anywhere says so

## Problem

Prompt caching is a prefix match, and the cache is **model-scoped**. Changing the model mid-conversation invalidates the entire cached prefix — the next turn re-writes every token of the history at the cache-write rate (2× base input on the 1-hour TTL this fleet's sessions use) instead of reading it at 0.1×. On a large session that is a 20× swing on the input side of one turn.

The switch is easy to make by accident. `CLAUDE.md` already documents one route: a resumed session keeps the model its transcript was saved with, so `/model` gets used to correct it — after the context is large. The model-routing hook adds a second nudge in the same direction.

Nothing in the cockpit, the terminal, or Claude Code itself mentions the cost. The turn simply gets more expensive, and the evidence is buried in a `usage` block in a 30MB JSONL nobody reads.

## Repro

1. Run a session until it carries a substantial prefix (measured examples below run to 700k–900k tokens).
2. Switch model — `/model`, or resume a session saved under a different model.
3. Read the next assistant turn's `usage` in the transcript: `cache_read_input_tokens: 0`, `cache_creation_input_tokens` ≈ the whole prefix.

## Expected

The cost of discarding a warm prefix is visible at the moment it is incurred, so the choice to switch is an informed one.

## Actual

Silent. The only signal is the bill.

## Evidence

Measured 2026-08-06 across 38 transcripts under `~/.claude/projects/` (21,607 deduplicated assistant turns), by scanning for full-prefix re-writes — `cache_read_input_tokens == 0` with `cache_creation_input_tokens > 5000` on a turn that is not the session's first.

- **17 full re-writes occurred after under 60 minutes idle**, so TTL expiry does not explain them: 8.5M tokens, ≈$100 at the 2× write rate.
- **11 of those 17 carried a different `model` than the immediately preceding turn.** Model switching is the single largest identified cause of non-TTL cache invalidation in this history.
- For scale: TTL expiry (idle >60 min) accounts for 41 events, 19.0M tokens, ≈$236. Total input-side spend across the same transcripts is ≈$6,731, of which cache reads are ≈$5,287.

Figures are API-equivalent. Under a subscription the same tokens land as usage-limit consumption rather than dollars; the arithmetic is unchanged.

## Scope note

The cockpit cannot *prevent* a model switch — it does not own the Claude Code session. This issue asks for the switch to be **named and priced where it happens**, not blocked. Fixed by [[TASK-0345-Model-Switch-Named-Where-It-Happens]].

## Next Actions

- [x] Quantify against real transcripts rather than reasoning from the pricing table
- [x] Detect the switch from the transcript and report the discarded prefix with its cost
- [x] Carry the same figure in the retrospective scan so the pattern is visible over time
