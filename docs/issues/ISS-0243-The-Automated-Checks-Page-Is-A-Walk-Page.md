---
type: "[[issue]]"
id: ISS-0243
aliases: ["ISS-0243"]
title: "The generated page for an automated section is the walk page with the walking removed — it shows 90% complete over checks with no recorded result, and puts the command in a 22-character cell where all 89 render identically"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
source: ["user:edwin"]
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0223-The-Bar-Is-The-Wrong-Instrument-In-The-Editor]]", "[[ISS-0234-The-Generated-Page-Repeats-Itself]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tests: []
---

# The page an automated section gets was built for walking

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

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
| **all areas** | **89** | **90%** |

*(**The area count in this table was 15 when it was written and is 45 now.** Not a correction — a consequence: [[TASK-0517]] ran later the same day and replaced the single `Moved from Tier 1 / Tier 2` parking bay with 47 recovered areas, so the same 89 checks are spread across 45 distinct names in 61 blocks. The **90% is exact and unchanged** — 80 of 89 at `mark: done`. Caught by independent review, and worth keeping visible: a figure of mine was invalidated by a later change of mine, inside one session.)*

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

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

Both fixes are correctly guarded — mutants un-guarding `checkPercent` and returning the command to the row's leading slot were executed and each fails its named test.

**The `90%` reproduces exactly; the `15 areas` does not.** `checkPercent` classifies through `MARK_CLASS`, and 80 of 89 are `mark: done` → 90%. But the automated section of the checks page renders **61 area blocks over 45 distinct area names**, not 15 — `view_payload` opens a new block on every *run* of equal `item.area`, so repeats split. The figure is repeated in six places (this note twice, `PHASE-037`, `renderer.ts`, `test_an_automated_area_shows_no_completion_percentage`'s docstring, `SNAPSHOT.yaml`) and I can reproduce it at no basis — at HEAD there is no automated section at all. If anything, it understates the defect by a factor of four.

The command claim is exact: 89 commands, **69 distinct**, and all 89 share the identical 22-character prefix `cd android && ./gradle` — so one distinct value across the page as rendered is precisely right.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

**I withdraw my own finding: the `15 areas` was correct when written, and I measured a later corpus.** Re-measured with `area:` reverted to the parking bay on all 66 notes — a single-variable copy of the same working tree:

| | automated area blocks | distinct names |
|---|---|---|
| before `TASK-0517` | **15** | 15 |
| after `TASK-0517` | 61 | 45 |

So the figure reproduces exactly at the basis it was taken on. My first pass measured after `TASK-0517`'s excavation had landed in the working tree and reported the difference as an unreproducible number — the same basis error I was raising, made while raising it. The note's framing of it as a consequence rather than a correction is right.

One residue: the parenthetical says *"is 45 now"*, which is the distinct-name count; the page renders **61** area blocks. Same conflation as `TASK-0517`'s *"15 area rows to 47"*.
