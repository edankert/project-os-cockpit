---
type: "[[task]]"
id: TASK-0343
aliases: ["TASK-0343"]
title: "The cache reader — prefix weight and cache state from the transcript, tail for live, full scan for the record"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0344-Warm-Cooling-Cold-In-The-Strip]]", "[[TASK-0345-Model-Switch-Named-Where-It-Happens]]"]
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]"]
tests: []
---

# The cache reader

## Definition of Done
- [x] `src/project_os_cockpit/session_cache.py` exposes a live read (bounded tail) and a full scan over a Claude Code transcript JSONL.
- [x] Assistant turns are deduplicated by `message.id` — one entry per content block otherwise double-counts every turn.
- [x] Live read returns prefix weight (last turn's `cache_read + cache_creation`), last-turn timestamp, last-turn model, and cache age; it reads a bounded tail, not the file.
- [x] Full scan returns full-prefix re-write events classified as session-start / TTL-expiry / sub-hour-invalidation, with tokens and an estimated cost each.
- [x] Both paths memoise against `(path, mtime, size)` so repeated snapshots do not re-parse.
- [x] A missing, unreadable, truncated, or empty transcript yields `None` rather than raising — this runs inside the snapshot path.
- [x] Cost estimation is one table, per model family, with the 2× (1h) / 1.25× (5m) write and 0.1× read multipliers named at the point of use.
- [x] Tests cover: dedupe, tail read finding the last turn, the three classifications, a truncated final line, and an absent file.

## Steps
- [x] Module with `TurnUsage` / `LiveCacheState` / `CacheHistory` shapes.
- [x] Tail read: seek `min(size, TAIL_BYTES)` from the end, drop the first partial line, parse forward, keep the last complete assistant turn.
- [x] Full scan: stream the file line by line; never load it whole.
- [x] Classification: `read == 0 and write > FULL_REWRITE_MIN` → first turn = session-start, gap > TTL = expiry, else invalidation (model recorded so TASK-0345 can split it).
- [x] mtime cache with a small bound.
- [x] Tests under `tests/`, fixtures written inline rather than checked-in 30MB files.

## Notes
Field shapes confirmed against this repo's own transcripts on 2026-08-06: `usage.cache_creation.ephemeral_1h_input_tokens` and `ephemeral_5m_input_tokens` are both present, and this fleet's sessions write 1h exclusively (129.0M vs 0.0M tokens) — so the 2× multiplier is the live case and 1.25× is defensive.

Transcripts in this repo reach 34MB. The tail bound is the whole point of splitting the two entry points; a full read on the snapshot path would be a performance regression shipped inside a cost feature.
