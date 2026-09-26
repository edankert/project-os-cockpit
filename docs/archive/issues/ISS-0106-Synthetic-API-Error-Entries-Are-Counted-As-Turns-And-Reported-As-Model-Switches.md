---
type: "[[issue]]"
id: ISS-0106
aliases: ["ISS-0106"]
title: "Claude Code's `<synthetic>` API-error placeholders are read as real turns, so an API reset is reported as a model switch and a TTL expiry is filed as sub-hour invalidation"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: high
component: "session-cache"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]", "[[CHG-20260806-Session-Cache-Economics]]"]
tests: []
---

# `<synthetic>` API-error placeholders are read as real turns

## Problem

When a request fails, Claude Code writes an assistant entry to the transcript with `message.model: "<synthetic>"`, a real `message.id`, and an all-zero `usage` block — the content is `API Error: Unable to connect to API (ECONNRESET)` or similar. There are 33 such entries across the 38 transcripts under `~/.claude/projects/`.

`session_cache._turn_from_entry` accepts them: they are `type: assistant` with a `usage` dict, so they become `TurnUsage` records indistinguishable from real turns. Nothing anywhere in the module filters on `model == "<synthetic>"`, and neither FEAT-0081, PLAN.md nor TASK-0343 mentions the case.

Four consequences, in rising order of harm:

1. **`history().turns` counts them.** The "21,607 deduplicated assistant turns" headline includes error placeholders.
2. **The gap that drives TTL classification is measured from the placeholder**, not from the last real turn. A retry seconds after a reset makes a 151-hour idle gap look like 52 seconds.
3. **`_classify` reports a model switch**, because `prev.model == "<synthetic>" != turn.model`. The event lands in `CAUSE_MODEL_SWITCH` with `prev_model: "<synthetic>"`.
4. **`live_state` puts it on the strip.** `prev = turns[-2]` is the placeholder, so the badge renders `model switch · ~$6.10` with the tooltip *"Switching `<synthetic>` → claude-opus-5 discarded 610k cached tokens"*.

## Repro

Synthetic reproduction (verified 2026-08-06):

```python
# turns: real turn @T+0 (read 600k), <synthetic> @T+179m, real turn @T+180m (read 0, write 610k)
history(path).events
# -> [('model-switch', prev_model='<synthetic>', model='claude-opus-5', gap=60)]
# truth: 180 min idle, same model both sides -> ttl-expiry, no switch
```

Real data (re-scan of `~/.claude/projects/` with the shipped module, 2026-08-06):

| event | classified | gap used | true gap to last real turn | true prev model |
|---|---|---:|---:|---|
| `184f4b38` +367,935 tok | `model-switch` | 52 s | 543,361 s (151 h) | `claude-opus-4-8` — **same model** |
| `184f4b38` +549,793 tok | `model-switch` | 1,257 s | 4,081 s (68 min) | `claude-opus-4-8` — **same model** |

Both are TTL expiries with no model change, filed as sub-hour model switches.

## Impact on the evidence

The fleet currently classifies **10** model switches. Two of them are these artefacts, so the true count is **8**, and the sub-hour bucket is **14**, not 16 — against the **11 of 17** quoted in [[ISS-0104]], FEAT-0081's table, both change notes and `SNAPSHOT.yaml`'s focus note. The qualitative conclusion survives (8 model switches still outnumber the 6 unexplained), but no quoted number does. See [[ISS-0111]].

## Expected

A `<synthetic>` entry is not a turn. Skip any entry whose `message.model` is `<synthetic>` (or, more robustly, any assistant entry whose entire `usage` is zero) before it reaches dedupe, so it can neither become `prev` nor be counted.

## Actual

It is a turn, it is `prev`, and it is the most-reported cause of cache invalidation in the retrospective.

## Next Actions

- [x] Filter `<synthetic>` / all-zero-usage assistant entries out of `_iter_turns`
- [x] Re-run the retrospective and correct the figures in ISS-0104, FEAT-0081 and both CHG notes
- [x] A test with a `<synthetic>` entry between two real turns of the same model, asserting `ttl-expiry` and no `model_switch`
