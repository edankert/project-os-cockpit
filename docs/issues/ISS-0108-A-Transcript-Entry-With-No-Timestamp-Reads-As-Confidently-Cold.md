---
type: "[[issue]]"
id: ISS-0108
aliases: ["ISS-0108"]
title: "An entry with no timestamp yields `state: cold` with a 56-year age — the Python reader has no `unknown`, which is the exact asymmetry its TypeScript half was written to avoid"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: medium
component: "session-cache"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Session-Cache-Economics]]"]
tests: []
---

# A transcript entry with no timestamp reads as confidently cold

## Problem

`_turn_from_entry` deliberately tolerates a missing timestamp (`ts = ts if isinstance(ts, str) else ""`), and `_parse_iso("")` returns `0.0`. `_with_age` then computes `age = now - 0.0` and takes the `age >= ttl_seconds` branch:

```
state: "cold"   age_seconds: 1786017720   # 56 years
```

That value is served on `/api/cockpit/state` and the strip renders `cold · ~$6.10` with the tooltip "Cache older than its 60min TTL", for a session whose age was never measured.

The same feature's TypeScript half gets this exactly right and says why:

> `unknown` is not `cold`: a square with no timestamp has told us nothing, and painting it grey would assert an age we never measured. … the ISS-0065 lesson that absence must not render as a confident state.

`LiveCacheState.state` has no `unknown` member. The principle is stated in one file of the change and violated in the other, and no note records the asymmetry.

## Repro

```python
# last assistant entry carries usage but no "timestamp" key
live_state(path, now=…)
# -> LiveCacheState(state='cold', age_seconds=1786017720.0, …)
```

## Expected

Either `live_state` returns `None` when the last turn has no usable timestamp (matching the module's own "every failure is an absent badge" contract), or `LiveCacheState.state` gains `unknown` and the strip renders the weight without a temperature.

## Actual

The most alarming state the badge has, asserted from the absence of data. There is also no test covering a timestamp-less entry, so nothing would notice a change here.

## Notes

Severity is medium rather than high because Claude Code does write `timestamp` on every entry observed in this fleet, so it is not currently firing. It is the module's *stated* tolerance of the case that makes it a defect: the code goes out of its way to accept the input and then draws a confident conclusion from it.

## Next Actions

- [ ] Return `None` (or `unknown`) when `_parse_iso(last_turn_at)` is `0.0`
- [ ] Test: last entry without `timestamp` yields no badge
