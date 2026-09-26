---
type: "[[issue]]"
id: ISS-0119
aliases: ["ISS-0119"]
title: "Four counts in the round-two record do not match the artefacts they count — fifteen tasks against thirteen, `39 → 45` tests against `32 → 37`, and a ~0.1% move that measures 0.03%"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-3"]
severity: low
component: "docs"
related: ["[[CHG-20260806-Round-Two-Findings-Fixed]]", "[[ISS-0116-Ticked-Boxes-That-Do-Not-Match-The-Work]]", "[[TASK-0355-The-Record-Stops-Overclaiming]]"]
tests: []
---

# The round-two record miscounts what it counts

## Problem

Every figure quoted from `scan-cache-economics.py` reproduces — that half of [[ISS-0111]] is genuinely closed, and this issue is not about those. It is about four counts of the *work itself*, none of which needs a script to check.

### 1. "fifteen tasks" — there are thirteen

[[CHG-20260806-Round-Two-Findings-Fixed]] says it twice:

> Run over every ticked box in this feature's **fifteen tasks**, it now passes

> features: updated — FEAT-0081 lists **fifteen tasks** and thirteen fixed issues

FEAT-0081's frontmatter lists TASK-0343 … TASK-0355 — thirteen — and `ls docs/features/session-economics/plan/tasks | wc -l` is 13. "Thirteen fixed issues" in the same sentence is right (ISS-0104 … ISS-0116).

This matters more than the other three because it is attached to the round's central claim. A check run over fifteen tasks that do not exist was not run over the thirteen that do, and [[ISS-0117]] and [[ISS-0118]] are five boxes it should have caught.

### 2. "`tests/test_session_cache.py` 39 → 45"

Collected with `pytest --collect-only`:

| | at `4de65a3` | at `907fe14` |
|---|---:|---:|
| `tests/test_session_cache.py` | 32 | **37** |
| `+ tests/test_session_cache_surface.py` | 39 | **44** |

The commit adds five tests to that file. So `39` is the two-file total wearing one file's name — the exact conflation [[ISS-0116]] flagged as "Related, minor" about the previous note's `19 → 39` — and `45` is neither figure.

### 3. TASK-0355's "all eleven tasks"

[[TASK-0355-The-Record-Stops-Overclaiming]] DoD: `- [x] items.features.FEAT-0081.tasks lists all eleven tasks …`. Thirteen, by the time TASK-0355 existed to say it. (That the list is still five is [[ISS-0117]]; this is only the denominator.)

### 4. "moving the fleet totals by ~0.1%"

Measured, by reverting `_effective_usage` to the identity function and re-running `tools/scripts/scan-cache-economics.py` over the same corpus in the same minute:

| | with the fix | reverted | delta |
|---|---:|---:|---:|
| turns | 21,938 | 21,933 | +5 |
| read tokens | 10,165,695,077 | 10,161,245,527 | +0.044% |
| input-side total | $6,813.62 | $6,811.32 | **+0.034%** |
| every re-write bucket | 8 / 6 / 44 | 8 / 6 / 44 | unchanged |
| staleness %, avoidable % | 3.7 / 4.9 | 3.7 / 4.9 | unchanged |

The substantive claim beside it — that no bucket, ratio or quoted figure moves — is **confirmed**. Only the magnitude is overstated, by about 3x, and in the direction of claiming more effect than the change has.

## Expected

Four numbers corrected. None of them requires re-deriving anything.

## Actual

A note whose subject is a record that overclaims, miscounting its own tasks, its own tests and its own effect size.

## Next Actions
- [x] `fifteen tasks` → thirteen, in both places, and re-run the ticked-box check over the thirteen that exist
- [x] `39 → 45` → `32 → 37` for that file, or name both files if the two-file total is what is meant
- [x] `all eleven tasks` → thirteen in [[TASK-0355]]
- [x] `~0.1%` → the measured 0.03%, or drop the magnitude and keep the claim that nothing quoted moves
