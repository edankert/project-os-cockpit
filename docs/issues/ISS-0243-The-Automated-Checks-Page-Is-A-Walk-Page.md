---
type: "[[issue]]"
id: ISS-0243
aliases: ["ISS-0243"]
title: "The generated page for an automated section is the walk page with the walking removed — it shows 90% complete over checks with no recorded result, and puts the command in a 22-character cell where all 89 render identically"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["user:edwin"]
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0223-The-Bar-Is-The-Wrong-Instrument-In-The-Editor]]", "[[ISS-0234-The-Generated-Page-Repeats-Itself]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tests: []
---

# The page an automated section gets was built for walking

## Problem

Edwin, 2026-08-20: *"why do we have a automated tests generated details page? (note: this details page shows the command as one of the first list items, this doesn't have enough space there; if we show the command then it should be underneath the description instead."*

Nothing decided an automated section should have this page. It has one because `renderChecks` iterates **every** derived section, and the section head links to it — so the automated section inherited the surface built for the manual walk, and inherited its furniture with it.

### 1. A completion percentage over checks nobody completes

`checkPercent` runs per area regardless of `manual`. On `your-trainer` that page reads **90% complete across 15 areas**:

| area | checks | shown |
|---|---|---|
| Simulation Mode | 7 | 71% |
| Monetization & Licensing | 2 | 0% |
| Route Workouts | 3 | 100% |
| Workout Loop/Repeat, Per-Rider Data Export, Data Backup & Restore, Ghost Riders, Runtime Translate-on-Demand | 1 each | 100% |
| **all 15 areas** | **89** | **90%** |

Those 89 checks carry `evidence: []` and an empty `verdict_date` — **no recorded result for any of them** — and nine sit at `mark: todo`. The percentage is computed from `mark:`, which for an automated check is a person's tick on something no person executes. It is [[ISS-0241]]'s false assurance again, one surface down, and this time it is a number rather than a phrase.

### 2. The command occupies the checkbox slot, and says nothing there

`buildCheckRow` puts the command **first** on the row, in the slot a manual check gives its check mark, under `.checks-row-command { max-width: 22ch; white-space: nowrap; text-overflow: ellipsis }`.

Every one of `your-trainer`'s 89 commands begins `cd android && ./gradlew`. Truncated to 22 characters that is:

```
89 rows → cd android && ./gradle
        → 1 distinct value
```

**The column is not merely cramped — it distinguishes nothing at all.** The discriminating part of the string is its tail (`--tests com.yourtrainer.ui.components.LapTimesStripTrophyTest`), which is exactly what the ellipsis eats. It costs leading width on every row of the page and carries zero information.

## Expected

- **The command moves into `.checks-row-body`, below `.checks-row-text`** — Edwin's instruction, and it is also where the width is. Full-width, wrapping or tail-biased, so the class name is visible.
- **No completion percentage on an automated area.** Either drop it or replace it with something the section can honestly say. Whatever replaces it must not be a progress figure, per [[ADR-0039]] and the reasoning already written into [[ISS-0241]].
- **Decide whether the page should keep area blocks at all.** Areas exist so a walker can pick a surface to work through. Nobody works through this one. A flat list ordered by class may be the whole of what an automated section needs — but that is a design question, not a defect, and it is called out here rather than assumed.

## Where

- `desktop/src/renderer/renderer.ts` — `buildCheckRow` (the command slot), `renderChecks` (the area loop and `checkPercent`).
- `desktop/src/renderer/renderer.css` — `.checks-row.is-automated .checks-row-command`.

## Fixed

- **The command moved out of the checkbox slot** into `.checks-row-command` inside the row body, under the description. The CSS lost `max-width: 22ch` and the ellipsis with it — the identifying part of a gradle invocation is its tail, and the old rule kept only the head that all 89 shared.
- **`checkPercent` is guarded on `manual`.** An automated area shows how many checks it holds; it no longer reports a completion figure over checks with no recorded result.
- Guards on both, and on the CSS rule, so a later tidy cannot restore the 22-character cell.

## Next Actions

- [x] Move the command under the description.
- [x] Remove or replace the percentage on automated areas.
- [ ] **Decide on area blocks for an automated section.** Deliberately left open: areas exist so a walker can pick a surface, and nobody walks this one — but that is a design question rather than a defect, and [[FEAT-0138]] may change what an automated section should show at all.
- [x] A guard that fails if an automated surface renders a completion figure.
