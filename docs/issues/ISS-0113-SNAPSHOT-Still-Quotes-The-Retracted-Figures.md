---
type: "[[issue]]"
id: ISS-0113
aliases: ["ISS-0113"]
title: "SNAPSHOT.yaml still carries the whole retracted figure set — `11 of 17`, `~3.5%`, `38 transcripts`, `$236`/`$100` — in the two places [[ISS-0111]] named, while the task that fixed it ticks `SNAPSHOT.yaml` as corrected"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-2"]
severity: medium
component: "docs"
related: ["[[ISS-0111-The-Measured-Figures-Do-Not-Reproduce-And-No-Scan-Script-Was-Committed]]", "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Review-Findings-Fixed]]"]
tests: []
---

# SNAPSHOT.yaml still quotes the retracted figures

## Problem

[[ISS-0111]] listed exactly where the disproven numbers appear, and named the snapshot twice:

> The same "~3.5%" appears in FEAT-0081, in the snapshot focus note, in the `items.features` note and in the commit message headline.

[[TASK-0352-The-Scan-Committed-And-The-Figures-Corrected]]'s Definition of Done ticks:

> - [x] Every quoted figure in FEAT-0081, [[ISS-0104]], both change notes and `SNAPSHOT.yaml` is re-derived after [[TASK-0348]] and corrected, with the correction visible rather than silent.

and [[CHG-20260806-Review-Findings-Fixed]] says "Corrected everywhere". The notes were corrected. `SNAPSHOT.yaml` was not — commit `4de65a3` touches the file (counters, `fixes:`, six new task entries, seven status flips) and leaves both prose notes byte-identical.

`SNAPSHOT.yaml:52` (`focus.note`) still reads:

> across 38 transcripts / 21,607 deduped assistant turns, cache READS are $5,287 of the $6,731 input-side spend; TTL expiry is $236 and sub-hour invalidation $100. Staleness is real and it is ~3.5% … ISS-0104 (**11 of 17** sub-hour re-writes were MODEL SWITCHES …)

`SNAPSHOT.yaml:63` (`items.features.FEAT-0081.note`) still reads:

> cache staleness is ~3.5% of the input bill (TTL expiry $236, sub-hour invalidation $100) against $5,287 for cache READS

Every figure in both is superseded. `11 of 17` is the one the review proved impossible.

## Why this is the worst remaining place for it

`CLAUDE.md` and `LIFECYCLE.md` both make this file **the** thing a session reads first: "the canonical, machine-readable active context for agents/LLMs". A wrong number in a note is read by whoever opens the note; a wrong number in `focus.note` is read by every session that starts in this repo, before it reads anything else. The correction landed everywhere except the surface with the widest readership.

## Repro

```
python3 tools/scripts/scan-cache-economics.py     # 42 transcripts, 8 of 14, 3.7% / 4.9%
grep -n "3.5%\|11 of 17\|21,607\|6,731" SNAPSHOT.yaml
```

## Expected

Both notes re-derived from the committed scan, with the correction visible rather than silent — the same treatment [[ISS-0104]]'s Evidence section got.

## Actual

Corrected in five notes, uncorrected in the file the process calls canonical, and ticked as done.

## Notes

Also stale, lower stakes: `focus.task: TASK-0343` and `focus.issue: ISS-0104` both point at terminal items while TASK-0348…TASK-0353 are the work actually in hand.

## Next Actions
- [x] Re-derive `focus.note` and `items.features.FEAT-0081.note` from `scan-cache-economics.py`
- [x] Move `focus` onto the work actually in flight
- [x] Consider whether a figure quoted in more than two places should live in one place and be referenced
