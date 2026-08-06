---
type: "[[issue]]"
id: ISS-0109
aliases: ["ISS-0109"]
title: "The bounded tail read is an acceptance criterion with no guard — replacing it with a full-file read leaves all 26 tests green, including the one whose docstring claims boundedness"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: medium
component: "tests"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[TASK-0343-The-Cache-Reader]]", "[[CHG-20260806-Session-Cache-Economics]]"]
tests: []
---

# The bounded tail read has no guard

## Problem

FEAT-0081's acceptance list ends with:

> Reading a 30MB transcript for live state does not read 30MB: the live path reads a bounded tail.

PLAN.md calls it a **design constraint**: "a full read there would be a performance bug shipped as a cost feature". TASK-0343's DoD ticks "it reads a bounded tail, not the file".

Nothing tests it. `test_live_state_does_not_read_whole_file` builds a file larger than `TAIL_BYTES`, asserts the size exceeds the budget, and then asserts only that the last turn resolves — which it would whether the read was 512KB or the whole file. Its docstring says "the read is bounded"; its body never observes a byte count, a seek offset, or an elapsed time.

## Repro (mutation testing, 2026-08-06)

Against `tests/test_session_cache.py` + `tests/test_session_cache_surface.py` (26 tests):

| mutation | result |
|---|---|
| `_read_tail`: `start = max(0, size - budget)` → `start = 0` (**always reads the entire file**) | **survived** |
| `TAIL_BYTES = 512 * 1024` → `1024` | **survived** |
| `WRITE_MULT_5M = 1.25` → `99.0` | **survived** |
| `FULL_REWRITE_MIN = 5_000` → `1_000` | **survived** |
| cooling threshold `ttl * 0.75` → `ttl * 0.30` | **survived** |
| live switch detection: drop `and last.read == 0` | **survived** |
| live switch detection: drop `and last.write >= MODEL_SWITCH_MIN_DISCARD` | **survived** |
| dedupe by `message.id` removed | killed |
| `MODEL_SWITCH_MIN_DISCARD` 50k → 300k | killed |
| `READ_MULT` 0.1 → 0.5 | killed |
| cache hit returns stale age (no `_with_age`) | killed |
| `gap > turn.ttl_seconds` → `gap > 0` | killed |

The core arithmetic and the dedupe are well guarded. The **bounded read** — the constraint the two-entry-point design exists for — is not guarded at all, and neither are three of the module's five tuning constants or the live model-switch preconditions.

## Expected

A guard that fails when the read stops being bounded. The cheapest honest one: monkeypatch `open`/`os.path.getsize` or wrap the file object and assert the number of bytes read for a 5MB fixture is under `TAIL_BYTES_FALLBACK`. A weaker but still real one: assert `_read_tail` returns fewer lines than the file has.

## Actual

A test whose name and docstring assert boundedness and whose body cannot detect its loss.

## Notes

Not currently a live performance problem — measured 2026-08-06, `live_state` on a 155MB transcript takes 2.1 ms and `history` 0.40 s, so the tail read is working. The defect is that nothing would say so if it stopped.

Related, minor: `desktop/tests/cache-temperature.test.mjs`'s "a future timestamp is warm, not cold" also survives deleting the branch it names — the fallthrough already returns `warm` for a negative age, so the assertion holds with or without the guard it is testing.

## Next Actions

- [ ] A byte-counting or line-counting guard on the live path
- [ ] Widen the classification tests so `FULL_REWRITE_MIN` and the cooling threshold have a boundary either side
- [ ] Cover the 5m write multiplier, or delete it as untested speculation
