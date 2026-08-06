---
type: "[[change]]"
id: CHG-20260806-Round-Two-Findings-Fixed
aliases: ["CHG-20260806-Round-Two-Findings-Fixed"]
title: "Round two: the usage totals are read where they actually live, and the record stops claiming more than the code does"
status: merged
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/session_cache.py", "desktop/src/renderer/renderer.ts", "SNAPSHOT.yaml"]
issues: ["ISS-0113", "ISS-0114", "ISS-0115", "ISS-0116"]
features: ["FEAT-0081"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Review-Findings-Fixed]]"]
---

# Round two: usage read where it lives, and a record that stops overclaiming

## Summary

The re-review returned `changes-requested` with a different shape of verdict: **the code was fixed; the notes claimed more than it did.** Four findings, all four fixed.

**ISS-0114 — a fix that overreached.** The ISS-0106 placeholder filter was widened to key on "consumed no tokens" so a future placeholder under another name could not slip through. It caught five real turns: entries whose top-level `usage` counters are all zero while the real accounting sits in `usage.iterations` — one a `stop_reason: tool_use` turn that read 461,787 cached tokens. Both dropping them and the previous behaviour of counting them as zero are wrong, so `_effective_usage` now takes the totals from wherever they are. The placeholder test became "no tokens **anywhere**", which still rejects every `<synthetic>` entry.

The serving attempt is used, not the sum: `prefix_tokens` answers *what will the next turn read*, and summing would double-count a prefix that existed once. Every entry in this corpus has a single iteration, so the distinction only bites on a server-side fallback — and there, last-attempt is right for weight even though sum is right for billing. That choice is now pinned by a test, because the mutation that took the first iteration instead survived until one was written.

**ISS-0115 — one decision, two implementations, and a false claim.** `tickTemperatures` still restated `railKey`'s rule inline, so the cold decision existed twice and only one copy was tested; it now calls `railKey`. And `CHG-Review-Findings-Fixed` said deleting ISS-0105's behaviour "turns the suite red". Re-verified: it does not — the suite stays fully green. The guarded surface grew; it did not become total. Corrected to what the suite actually does.

**ISS-0113 / ISS-0116 — the record.** `SNAPSHOT.yaml` still carried the entire retracted figure set — `11 of 17`, `~3.5%`, 38 transcripts — in the two places ISS-0111 named by hand, while TASK-0352 ticked "every quoted figure in SNAPSHOT.yaml is corrected". That is the surface every session reads first, and it went a whole fix round still asserting a number the review had proved impossible. Corrected, along with `items.features.FEAT-0081.tasks` (5 of 11 listed — ISS-0112's drift with the sides swapped), `6 of the 17` in two more files, and duplicated follow-up lines in an earlier note.

## The pattern, named

Three of round two's four findings were the same defect as round one's core finding — **a claim written wider than the code** — committed *while fixing it*. Twice is a pattern, not an accident: the close-out step that ticks a box and the step that verifies the box are the same step, done by the same session, in the same minute.

The mechanical corrective now applied: **before ticking a box that names a file, confirm the file is in the diff.** Run over every ticked box in this feature's fifteen tasks, it now passes — and it would have caught ISS-0113 and ISS-0116 at the time.

The structural corrective is `PARENT-BACKLINK`, which proved itself during this very round: adding TASK-0354 and TASK-0355 with `parent: FEAT-0081` failed the validator until the feature named them back. A third repetition of the ISS-0112 drift, caught by the gate written for the first.

## Impact

- **Changed:** `session_cache.py` — `_effective_usage`, `TOKEN_FIELDS`, and a docstring whose premise no longer contradicts the corpus.
- **Changed:** `renderer.ts` — `tickTemperatures` asks `railKey` rather than restating it.
- **Changed:** `SNAPSHOT.yaml` — corrected figures in both prose notes, complete task and issue membership.
- **No behavioural change to any surface.** The badge, the rail and the panel render exactly as before; five previously-invisible turns now count, moving the fleet totals by ~0.1%.

## Documentation Coverage (All Types Considered)

- features: updated — FEAT-0081 lists fifteen tasks and thirteen fixed issues, plus an acceptance clause for the iterations case
- requirements: not-applicable
- tasks: new — TASK-0354, TASK-0355
- issues: [[ISS-0113]] … [[ISS-0116]] all `fixed`
- tests: `tests/test_session_cache.py` 39 → 45, each new guard verified by re-running its mutation
- workflows / decisions / risks: not-applicable
- changes: this note; corrections applied to [[CHG-20260806-Review-Findings-Fixed]]
- snapshot: updated

## What is still not fixed

- **The DOM adapters remain unguarded.** Deleting the three call sites in `renderer.ts` leaves the suite green. The decisions they call are guarded; the calls are not, and closing that needs a DOM the node suite declines to bring in.
- **69 grandfathered `PARENT-BACKLINK` violations** remain as warnings.
- **`PARENT-BACKLINK` checks `parent:` only**, not the `fixes:` direction — so the snapshot-side drift ISS-0116 found is still structurally invisible.
- `CACHE_TTL_MS` still duplicates `TTL_1H` with nothing detecting drift.

## Follow-ups

- [ ] A third review, then close FEAT-0081 and PHASE-007 on the verdict.
- [ ] Extend `PARENT-BACKLINK` to the snapshot side, or accept that membership there is unguarded and say so.
- [ ] Work down the grandfathered ledger.
