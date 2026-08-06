---
type: "[[issue]]"
id: ISS-0111
aliases: ["ISS-0111"]
title: "The measurement the whole feature is shaped by cannot be re-run — no scan script was committed, and the shipped module returns different numbers than the notes quote"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: medium
component: "docs"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]", "[[ISS-0106-Synthetic-API-Error-Entries-Are-Counted-As-Turns-And-Reported-As-Model-Switches]]", "[[CHG-20260806-Session-Cache-Economics]]"]
tests: []
---

# The measured figures do not reproduce

## Problem

FEAT-0081 opens by saying the measurement changed what got built, and it is right to: "measured first" is the best decision in this change. But the measurement exists only as prose. No scan script was committed with either commit, so the numbers quoted in FEAT-0081's table, ISS-0104's Evidence section, both CHG notes and `SNAPSHOT.yaml`'s focus note cannot be re-derived by anyone — including their author, later.

Re-deriving them with the shipped module over `~/.claude/projects/` on 2026-08-06 (independent review):

| figure | quoted | re-derived | verdict |
|---|---:|---:|---|
| transcripts | 38 | 38 | matches |
| deduplicated assistant turns | 21,607 | 21,845 | grew — consistent |
| cache reads | ≈$5,287 | $5,328 | grew — consistent |
| cache writes | ≈$1,444 | $1,447 | grew — consistent |
| TTL expiry | 41 events, 19.0M, ≈$236 | 42, 19.4M, $240 | grew — consistent |
| **sub-hour re-writes** | **17** | **16** | **cannot grow smaller** |
| **of which model switches** | **11** | **10** | **cannot grow smaller** |

Counts of past events only rise as transcripts accumulate. Two of the seven figures fell, so the sub-hour figures were produced by logic that differs from the module that shipped, and there is no record of what that logic was.

Worse, [[ISS-0106]] shows **2 of the 10 remaining "model switches" are `<synthetic>` API-error artefacts**, and both are actually TTL expiries with no model change. The defensible numbers are therefore **8 model switches out of 14 sub-hour re-writes**, against the "11 of 17" that ISS-0104's headline, its Evidence section, its snapshot note and both change notes all state.

**The conclusion survives** — 8 model switches still outnumber the 6 with no discoverable cause, so "model switching is the single largest identified cause of non-TTL cache invalidation" holds. Every number supporting it is wrong.

## A second, smaller arithmetic problem

`CHG-20260806-Session-Cache-Economics` says:

> Of the writes, full-prefix re-writes cost ≈$336 — ≈$236 to TTL expiry after >60 min idle, ≈$100 to sub-hour invalidation. So staleness is real and it is **~3.5% of the input bill**

$336 / $6,731 = **5.0%**, not 3.5%. The 3.5% figure is $236/$6,731 — TTL expiry alone. The sentence defines staleness as the $336 total and then quotes the ratio for one of its two halves. The same "~3.5%" appears in FEAT-0081, in the snapshot focus note, in the `items.features` note and in the commit message headline.

## Expected

- The scan committed as a script (`tools/scripts/` or a test fixture), so the figures are a command anyone can run rather than a claim in prose.
- The `/api/cockpit/session-cache` endpoint already computes most of this. It is a per-workspace endpoint over the tracker's known transcripts, so it does not answer the cross-fleet question the notes ask — which is itself worth stating, since a reader may assume the endpoint *is* the measurement.
- Figures corrected after [[ISS-0106]] is fixed.

## Actual

Prose figures, unreproducible, two of them impossible, and the headline percentage inconsistent with its own inputs.

## Next Actions

- [ ] Commit the scan as a script
- [ ] Fix [[ISS-0106]], re-run, and correct every quoted figure in FEAT-0081, ISS-0104, both CHG notes and SNAPSHOT.yaml
- [ ] Decide whether "staleness" means TTL expiry or all avoidable re-writes, and use one definition everywhere
