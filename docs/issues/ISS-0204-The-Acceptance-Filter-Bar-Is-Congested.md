---
type: "[[issue]]"
id: ISS-0204
aliases: ["ISS-0204"]
title: "The acceptance page leads with five filter axes and 164 chips — the reader meets the filter bar before the checks"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: low
component: ui
phase: "[[PHASE-036-One-Human-Walk]]"
related: ["[[FEAT-0114-The-Suite-Is-A-View]]", "[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[TESTING-MODEL]]"]
---

# The filter bar is the first thing on the page, and the largest

Edwin, 2026-08-18: *"The acceptance test page top of the page is very congested (your-trainer less so on project-os-cockpit) with all these options to turn on/off visibility of tests … probably only need selection based on the mark/status?"*

Measured on `your-trainer`'s live payload:

| axis | values |
|---|---|
| marks | 2 |
| tiers | 3 |
| **areas** | **76** |
| **covers** | **80** |
| automation | 3 |

**164 chips above the first check.** The `areas` and `covers` axes are the congestion: both scale with the corpus, so the surface gets worse exactly as the suite it serves gets more useful. `project-os-cockpit` is milder only because it has 34 checks rather than 579 — the same design, a twentieth of the data.

The single-value suppression rule (*"a single value on an axis is not a filter, it is a fact"*) already exists and is correct; it just never fires on the two axes that need it.

## Why it was built this way

[[FEAT-0114-The-Suite-Is-A-View]] made every filter a **field** rather than a heading — deliberately, because the old document could only be filtered by what a heading happened to say, which is why `missing_issue_refs` once reported 158 of 158. That was the right change and this is its cost: having made five axes filterable, the page offered all five at once.

## Edwin's proposal, and one caveat

Leading with **mark** alone is right for the common question — *what is outstanding*. The caveat is that `area` is how a walker actually batches work (*"one walk's worth of related checks"* is the field's own definition), so it should stay reachable rather than be deleted — behind a control, not in front of the list.

## Done when

- [ ] The page leads with the checks. Mark is the primary filter; tier follows from the address ([[ISS-0203]]).
- [ ] `areas` and `covers` are reachable but not rendered as 156 chips — a picker, a search, or a grouping the list already has.

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context, measured against both live sidecars.**

**The counts are exact.** `your-trainer`: marks 2, tiers 3, areas 76, covers 80, automation 3 = **164 chips**, and `buildCheckFilters` renders every value with no cap and no collapse, above the list. The single-value suppression (`if (values.length < 2) continue`) is present and correct, and on `your-trainer` it fires on nothing.

**"`project-os-cockpit` less so" is true of the height and false of the ratio.** This repo renders **65 chips over 34 checks** — marks 2, tiers 2, areas 21, covers 40, with `automation` (1 value) correctly suppressed. That is **1.9 chips per check against `your-trainer`'s 0.28**. The small repo is the worse offender per row; what makes it feel milder is that 65 chips is two or three lines rather than eight. Worth correcting in the note, because it changes what the fix has to survive: the design fails at both ends of the corpus-size range, not only the large one.

**The caveat about `area` is right, and it has a number.** 76 areas over 579 checks is **7.6 checks per area** — one sitting's worth, which is what the field's definition claims for it, so it earns a control rather than deletion. `covers` has no comparable defence: 80 values over 579 rows, and the same question is answerable from a feature's own page through the reverse index ([[ADR-0032]]).

**Leading with mark is nearly free.** The mark axis is **2 chips on `your-trainer`** (`passed` 513, `unwalked` 66) and **2 here** (`passed` 33, `partial` 1) — because `-`, `!` and `?` are written nowhere in the fleet ([[ISS-0200-Marks-Versus-Statuses]]). So the proposed primary filter costs two chips today and can only reach six.

**Verdict: approved. Correct the "milder" sentence to the per-check ratio, and note that mark-only is a two-chip bar rather than a six.**
## Fixed 2026-08-18

`CHIP_CAP = 8`. A wider axis collapses to a `<details>` carrying its own value count **and its own selection count**, so a filter cannot hide inside a fold and quietly shorten the list. Measured after: 164 chips → 8 on `your-trainer`, 65 → 4 here.

The caveat in this note held: `area` stays reachable behind the fold at 7.6 checks each — one sitting's work, which is what the field means — while `covers` at 80 values is a query rather than a filter bar.
