---
type: "[[issue]]"
id: ISS-0284
aliases: ["ISS-0284"]
title: "The tier chips on the checks filter bar select a value nothing matches — the facet carries the section key (`regression`) and the predicate compares the tier number (`2`), so clicking one changes nothing or empties the page"
status: fixed
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Found in the live harness against ../your-trainer while verifying ISS-0280, 2026-09-06"]
severity: medium
component: ui
parent: ""
related: ["[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]", "[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]", "[[ADR-0039-A-Section-Is-Derived-Not-Filed]]"]
tests: []
---

# The tier chips filter nothing

## Problem

On `~checks`, clicking a chip in the **tier** row does nothing visible. From a bare `~checks` it is worse: selecting only a tier chip renders "No check matches these filters", because the value it selects matches no row at all.

Observed in the live harness against `../your-trainer` on 2026-09-06: with `~checks/tier/1` open and `Regression tests · 99` clicked, the filter set became `["1", "regression"]` and the page still showed only Feature tests.

## Cause

Two vocabularies for one axis, and they never meet.

- `acceptance._facets` emits `tiers` from **the section key**: `feature`, `regression`, `automated`. Its own comment says so — *"the facet is the SECTION now, under the key `tiers` so a pinned client keeps working"*. [[ADR-0039]] derived the sections and left the payload key alone.
- `checkMatches` compares `f.tiers.has(String(tier))`, where `tier` is the numeric position the payload also carries — `1`, `2`, `3`.
- The `~checks/tier/<n>` route puts a **digit** in the same set, which is why the address form works and the chips do not.

Nothing raised. A set holding `"regression"` is a valid set, and a predicate that never matches renders an empty list rather than an error. This is the shape [[ISS-0211]] records — a vocabulary migrated on one side of a comparison — one axis further along.

## Why it is fixed here rather than filed for later

[[ISS-0280]] persists the filter set per workspace. A per-session bug a reader works around by clicking again becomes a stored state they come back to. A change that makes an existing defect durable carries the fix for it.

## Fix

`checkMatches` takes the tier rather than its number, and accepts either vocabulary: the section key the chips emit, or the position the address uses. One predicate, both forms, so neither the filter bar nor `~checks/tier/2` has to be the side that changes.

## Risk scan

No trigger applies: no new dependency, env var, path or contract. The payload is unchanged.

## Next Actions

- [x] `checkMatches` matches a row on its section key as well as its tier number.
- [x] Guard: a test asserting the predicate consults both, so neither vocabulary can be dropped again.
