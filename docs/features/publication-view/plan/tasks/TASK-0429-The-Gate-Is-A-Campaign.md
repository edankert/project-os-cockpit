---
type: "[[task]]"
id: TASK-0429
aliases: ["TASK-0429"]
title: "The gate is a campaign — the acceptance suite attached to the release rung, grouped by what you need at hand, counted as one obligation and never as sixty"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16, refusing the first proposal: 'I am also afraid that this could overwhelm my attention'", "[[ADR-0028]] decision 3 and its consequences"]
parent: "[[FEAT-0102-Publication-Becomes-A-View]]"
effort: M
depends: ["[[TASK-0428-The-Release-Rung]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]"]
blocks: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0141]]", "[[ISS-0143]]"]
tests: ["[[TST-0028-The-Release-Gate-Names-Its-Number]]"]
---

# The gate is a campaign

## What

`acceptance.gate_payload` already computes the release gate correctly and completely. Nothing consumes it except a band that mounts only when you open a release note — and in `your-trainer` the newest release is already `released`, so **no page in the app currently states the number 60**.

This attaches the gate to the release rung, where its subject lives, and shapes it as a campaign rather than a list.

## One obligation, not sixty

The first proposal was to admit all 60 rows to the registry. Edwin refused it and the registry's own charter agrees: [[ADR-0027]] excludes staleness because *"counting it is a badge that re-arms itself forever"*, and acceptance rows re-arm **in bulk, by the suite's own rule 3**.

So the gate contributes **one** obligation while a release is `draft`, and **zero** otherwise. Sixty is a number the campaign *states*; it is never a number a badge sums.

## The unit is the sitting

`your-trainer`'s 60 blocking rows cluster into 17 sections, and two carry 33 — Trainer Compatibility (20) and Monetization & Licensing (13). Top five carry 45 of 60. That is about two sittings, most of it with a trainer plugged in.

The suite already says what each needs at hand, in its own *Manual Test Environment Breakdown*: trainer hardware ~24, HRM ~9, Strava ~6, Play Billing ~2, Android OS ~7, visual ~50. Nothing reads it. Grouping by environment makes the unit the sitting rather than the checkbox — which is the whole difference between a campaign and a wall.

## Definition of done

- [ ] The gate is attached to the release rung and **states its number** — `your-trainer` reads 60, not `306/347` requiring the reader to subtract
- [ ] It contributes exactly **one** obligation while a release is `draft`, and **zero** when none is. Asserted both ways
- [ ] Rows group by environment, read from the suite's own table rather than from a list in the code; a suite with no such table groups by section and says so
- [ ] Tier 3 is shown and does not gate — `TESTING.md` is explicit, and [[ISS-0143]] already retired its checks here
- [ ] A `- [~]` reconciled row is counted and named, never folded into `checked` ([[ISS-0141]]'s rule, which the parser already honours and the surface must not undo)
- [ ] Opening a row reaches the suite at that section
- [ ] With no suite at all the rung says *never instantiated*, not *nothing blocking* — `gate_payload` reports `exists` for exactly this reason and a surface that conflated them would restore the state that made the gate look like it worked
- [ ] The gate's own sentence stays the contract's words, shipped from the server, including the local reconciliation clause beside it
