---
type: "[[issue]]"
id: ISS-0250
aliases: ["ISS-0250"]
title: "A check names its surface by copying its title, so renaming a surface silently orphans every check on it — and an orphaned surface is indistinguishable from an uncovered one"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["measured while closing FEAT-0130, 2026-08-20"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[TASK-0515-Consolidate-Your-Trainer-Surfaces]]", "[[TASK-0516-Surfaces-On-The-Design-View]]", "[[REQ-0049-A-Surface-Exists-Whether-Or-Not-A-Test-Names-It]]"]
tests: []
---

# The join is a string comparison, and its failure mode is silence

## Problem

`surface_coverage()` (`src/project_os_cockpit/cockpit.py`) joins a surface to its checks on the **lower-cased title**:

```python
key   = str(item.area or "").strip().lower()     # the check
title = str(record.title or "").strip().lower()  # the surface
counts[record.note_id or ""] = areas.get(title, 0)
```

There is no link, no id, and no reverse check. So editing a surface's `title:` moves its count to **zero** and moves nothing else.

**Measured rather than assumed, and the first version of this note got it wrong.** The join lower-cases and strips both sides, so it *survives* the two edits I first named — `Riding — routes` -> `Riding — Routes` and surrounding whitespace both stay at 3 of 3. What breaks it is any other character: `Riding — routes` -> `Riding - routes`, **an em dash typed as a hyphen**, drops 3 to 0. That is the worst possible case to have got backwards, because **8 of `your-trainer`'s 15** surface titles contain an em dash — `Data — backup/export`, `Integrations — AI`, `Integrations — Strava`, the three `Riding —` and the two `Workouts —` — and every one of them is otherwise ordinary words a person would retype. Constructed and executed, three checks against one surface:

| surface `title:` | coverage | design view head |
|---|---|---|
| `Riding — routes` | 3 | `Surfaces` |
| `Riding — Routes` | 3 | `Surfaces` |
| `&nbsp;Riding — routes&nbsp;` | 3 | `Surfaces` |
| `Riding - routes` | **0** | `Surfaces · 1 with no checks` |
| `Riding — routes & free ride` | **0** | `Surfaces · 1 with no checks` |

The design view then shows the surface under `Surfaces · N with no checks`, which is **the exact row [[FEAT-0130]] built the type to produce**: a place in the product nobody has tested.

**The two states render identically.** A surface with genuinely no checks and a surface whose 91 checks were orphaned by a rename both read *"no checks"*. The renamed one is the more urgent of the two and is the one the surface tells you least about.

`area:` values naming no surface are equally invisible from the other end: nothing walks them, so a check can sit on a name no surface has and never be reported.

## Repro

In `your-trainer` (working tree, 2026-08-20), change `docs/surfaces/SUR-0011-Riding-routes.md` `title:` from `Riding — routes` to `Riding - routes` — one em dash retyped as a hyphen. `surface_coverage` drops that surface from **91 to 0**. No validator error, no test failure; the design view head count rises by one and says the surface has no checks.

## Expected

A rename is either impossible to get wrong (the check names the surface by **id**) or it is **reported** (a validator rule names any `area:` value that matches no surface, in a repo that has surfaces).

## Actual

Silent. The only signal is a number changing on a screen nobody is looking at for that reason.

## Evidence

- The join, quoted above, and its own docstring: *"a surface whose title matches no `area:` reads as zero, which is correct rather than a gap in the join."* True at the moment it was written and it is precisely the ambiguity above.
- [[TASK-0515]] recorded this as the thing it left: *"the join is by name — so renaming a surface silently orphans 91 checks. Closing that is a schema change on the check (`area:` becomes a link), which is [[FEAT-0130]]'s endpoint rather than this task's."*
- **The corpus is clean right now**, which is what makes a day-one error affordable. Measured in `your-trainer` 2026-08-20: **15** surface titles, **15** distinct non-empty `area:` values, and `comm -23` over the two sorted sets returns **nothing** — no area names a surface that does not exist. The two `level: acceptance` notes outside the directory (`TST-0015`, `TST-0018`) carry `area: ""` and are the empty case a rule must skip rather than report.
- No other fleet repo holds a `SUR-*` note, so a rule guarded on *"this repo has surfaces"* is silent in eleven of twelve.

## Next Actions

- [ ] Decide the shape: a validator rule (`SURFACE-ORPHAN`) reporting an `area:` that names no surface, or the schema change that makes `area:` a `[[SUR-####]]` link. The rule is cheap and catches the same defect from the side where the population lives; the link is the real fix and touches 579 notes in another repo.
- [ ] Whichever is chosen, construct the rename and **watch the check fire** — an orphan reading as an honest zero is the failure this phase has met eight times.
