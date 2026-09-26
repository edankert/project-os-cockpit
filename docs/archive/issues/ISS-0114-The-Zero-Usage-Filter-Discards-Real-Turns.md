---
type: "[[issue]]"
id: ISS-0114
aliases: ["ISS-0114"]
title: "The new all-zero-usage rejection discards five real assistant turns in the measured corpus — one of them read 461,787 cached tokens, recorded in `usage.iterations` where nothing looks"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-2"]
severity: medium
component: "session-cache"
related: ["[[ISS-0106-Synthetic-API-Error-Entries-Are-Counted-As-Turns-And-Reported-As-Model-Switches]]", "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Review-Findings-Fixed]]"]
tests: []
---

# The zero-usage filter rejects real turns

## Problem

[[ISS-0106]]'s fix rejects an assistant entry two ways: `model == "<synthetic>"`, and — the part argued for at length — the **shape of the data**:

```python
if not any(_int(usage, k) for k in (
    "cache_read_input_tokens", "cache_creation_input_tokens",
    "input_tokens", "output_tokens",
)):
    return None
```

The justification, in the docstring and repeated in the change note, is:

> an entry that consumed no tokens at all did no work, whatever it calls itself

That premise is false for a shape present in the very corpus the feature was measured from. Claude Code sometimes writes an assistant entry whose **top-level `usage` counters are all zero** while the real accounting sits in a nested `usage.iterations[]` array, which nothing in this module reads.

Measured over `~/.claude/projects/` on 2026-08-06 — 42 transcripts, 21,940 distinct assistant `message.id`s:

| | count |
|---|---:|
| `<synthetic>` ids (correctly rejected) | 33 |
| non-`<synthetic>` ids whose usage is all-zero at the top level everywhere | **5** |

One of the five, `msg_01MaSMVKZzmFuPvqiwssTg65` in `184f4b38-…jsonl` (`claude-opus-4-8`, 2026-06-25):

```
usage.input_tokens                 0
usage.cache_read_input_tokens      0
usage.cache_creation_input_tokens  0
usage.output_tokens                0
usage.cache_creation.ephemeral_1h_input_tokens   3112     <- already non-zero
usage.iterations[0]  input_tokens 420  output_tokens 3461
                     cache_read_input_tokens 461787
                     cache_creation_input_tokens 3112
```

Its content blocks are a real `thinking` block, a real `text` block and a real `tool_use` — 461,787 tokens read from cache. It is not a placeholder by any reading.

## Impact

Small today, and **no quoted figure moves** — verified by re-running `scan-cache-economics.py` with the zero-usage clause removed: every bucket is identical (`model-switch` 8, `other` 6, `ttl-expiry` 44, `$5,352.33` / `$1,448.32`), only the turn count differs, 21,907 against 21,902. The tokens were never counted in either version, because the module reads the top-level rollup and these entries have none.

What changes is the reader's behaviour around them:

1. **They can no longer be `prev`.** `_classify` now measures `gap_seconds` across the dropped turn to an older one, so a re-write following one of these gets a longer gap and a different `prev_model` than the transcript records.
2. **On the live path they are no longer the last turn.** Before, such an entry produced `prefix_tokens == 0` and the strip rendered nothing (`cacheBadge` returns `null` on a falsy prefix). Now `live_state` falls back to the preceding real turn and reports **its** weight and **its** timestamp — an age older than the session actually is, which can read `cooling` or `cold` on a session that has just taken a turn. That is the [[ISS-0108]] failure mode arriving through the [[ISS-0106]] fix: a temperature asserted from a turn that is not the last one.

## Repro

```
python3 - <<'EOF'
# count non-<synthetic> assistant message ids whose top-level usage is all zero
EOF
# (5 in this corpus; the example above is the largest)
```

Remove the four-key `any(...)` clause from `_turn_from_entry` and re-run `tools/scripts/scan-cache-economics.py`: turns 21,902 -> 21,907, every other figure unchanged.

## Expected

Either the shape check reads `usage.iterations` before concluding no work was done, or it is narrowed to what it can actually justify — the sentinel plus, if a shape test is wanted, one that also treats a populated `cache_creation`/`iterations` as evidence of work. A guard on the `iterations` shape either way, since it is in the corpus and nothing currently sees it.

## Actual

A heuristic argued as more robust than the sentinel, contradicted by the data it was derived from, with a test (`test_zero_usage_entry_is_skipped_under_any_model_name`) that pins the over-broad behaviour in place.

## Notes

Filed as medium rather than low because of the live-path consequence in point 2 — a stale age is exactly what this feature exists to avoid — not because of the five turns.

The two-filter argument in the change note ("Both filters are guarded, by a case only each can catch") is correct as far as it goes: `test_synthetic_entry_is_skipped_even_when_it_reports_tokens` and `test_zero_usage_entry_is_skipped_under_any_model_name` do isolate the two. Neither covers the case where the two disagree in the other direction.

## Next Actions
- [x] Decide whether `usage.iterations` is read for accounting or only for the work/no-work test
- [x] Narrow or widen the shape check; correct the docstring and [[CHG-20260806-Review-Findings-Fixed]]'s claim
- [x] A test with an `iterations`-shaped entry as the last turn, asserting the badge is not derived from the turn before it
