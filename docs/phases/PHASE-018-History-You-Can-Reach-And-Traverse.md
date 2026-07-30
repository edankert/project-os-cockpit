---
type: "[[phase]]"
id: PHASE-018
aliases: ["PHASE-018"]
title: "History you can reach and traverse — a permanent way in, and a year of activity you can click into"
status: done
order: 18
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Make History reachable without hunting for a link at the bottom of a tile, and make the span of the project navigable — a contribution grid where a day is a destination rather than a decoration."
features:
  - "[[FEAT-0053-History-Navigation]]"
requirements: []
issues: []
depends: ["[[PHASE-017-History-As-Document-Events]]"]
related: ["[[FEAT-0052-History-Timeline]]", "[[FEAT-0032-Agents-Screen]]"]
tags: [overview, history, navigation]
---

# History you can reach and traverse

## Where this came from

Edwin, immediately after [[PHASE-017]] landed:

> *"is there a way to get to the history page without having to press that hidden button at the bottom of the page? … can we instead have a github style contribution panel for the last year and maybe have a way to move to specific dates … possibly scroll to previous years?"*

Both are the same complaint from different ends: the surface exists and there is no way in.

## The measurement that shaped it

A literal GitHub grid would look broken on this corpus, and the numbers say why:

```
span                       2026-05-07 → 2026-07-30   (12 weeks)
days with any activity     16
transitions per active day min 1 · median 34 · max 199
```

**365 cells, 16 lit.** And GitHub's intensity buckets top out at "10+", so at a median of 34 nearly every lit cell would be maximum darkness — a sea of grey with sixteen identical dark squares, saying "worked on 16 days" and nothing more.

The idea is right; GitHub's *constants* are wrong for this data. Three corrections keep the familiar shape and make it informative:

1. **Relative intensity** — quartiles of this repo's own active days, so a 199-day and a 6-day are visibly different.
2. **"Did not exist" is not "no activity"** — cells before the first commit render as absent rather than empty. GitHub conflates the two, which is why every young repo's graph looks like neglect.
3. **Year controls appear only when there is more than a year** — today there is nothing to scroll back to, so no controls. Same rule the fleet roll-up uses for its empty state.

## Scope

- **[[FEAT-0053]]** — the per-day activity payload, the grid, and a permanent entry point.
- The entry point is a **rail tool button**, beside Agents. The top bar is nav *modes* — each changes what the left pane lists — and History has no left-pane listing. `~agents` is the exact precedent: a page, not a mode, reached from the rail.

## Out of Scope

- **A History nav mode.** Bending the top bar's meaning to fit one page is how a surface's grammar erodes; [[PHASE-010]] spent itself undoing that class of drift.
- **Per-day drill-down as its own page.** Clicking a day scrolls History to that day. A third surface for one date would be the duplication this repo keeps deleting.

## Exit Criteria

- [x] History is reachable from the rail without visiting the overview — evidence: from `~overview`, `#history-toggle` lands on `~history` with 170 rows
- [x] The grid renders a year, pre-history visibly absent — evidence: 371 cells, **286 absent** vs **69 empty**
- [x] Intensity is relative to this repo — evidence: 16 active days spread **5 / 4 / 3 / 4**; buckets `[22, 36, 64]`
- [x] Clicking a day lands on that day — evidence: the 2026-05-07 cell lands on the 2026-05-07 divider, after the anchoring fix below
- [x] Year controls absent under a year of history — evidence: 0 rendered on this repo
- [x] The sparkline is gone — evidence: `ov-history-spark` absent from the build, guarded

## Notes

**The cost profile differs from [[FEAT-0052]]'s and so does the caching.** The grid needs a full-history pass (0.57 s, 3.3 MB of diff), but it only changes when HEAD does — so it caches cleanly on HEAD, unlike the timeline payload whose uncommitted band is precisely the part that must never be cached. Two payloads with opposite caching needs, which is the reason they are two payloads.


## Closed 2026-07-30

[[FEAT-0053]] done, three tasks, every criterion verified live.

**Both of Edwin's questions had the same answer.** "How do I get to History" and "can we have a contribution panel" are one problem — a surface with no way in — and the grid solves both, because a cell you click is an entrance you cannot miss.

### What the measurement changed

The request was for a GitHub-style panel. Measured first — 16 active days in 12 weeks, median 34 transitions — and a literal copy would have been **365 cells with 16 lit, all at maximum intensity**: a sea of grey with sixteen identical squares saying "worked on 16 days".

The idea was right and GitHub's *constants* were wrong for this data. Three corrections kept the familiar shape and made it informative, and all three are visible in the result: 286 absent vs 69 empty, four populated intensity steps, zero year controls.

Worth generalising: **copying a known design means copying its constants, and constants are fitted to the data the original had.** GitHub's are fitted to repos with daily commits from many people.

### The live pass earned its place again

[[TASK-0259]] wrote down "a cell that does not navigate is the sparkline again" before implementation, and the first cut navigated to the wrong day anyway — silently, landing on the oldest commit that happened to be loaded. No test would have caught it; nothing was thrown and a divider *was* highlighted.

That is the seventh finding this week from looking at a rendered surface rather than from a check. The difference this time is that it was **my own** surface and my own warning, found within minutes because the pass was run before the claim was written.
