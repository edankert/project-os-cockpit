---
type: "[[issue]]"
id: ISS-0204
aliases: ["ISS-0204"]
title: "The acceptance page leads with five filter axes and 164 chips — the reader meets the filter bar before the checks"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: low
component: ui
phase: "[[PHASE-999-Future]]"
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
