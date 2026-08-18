---
type: "[[issue]]"
id: ISS-0213
aliases: ["ISS-0213"]
title: "Five acceptance tests in your-trainer carry `level: system`, so they route to a flat group instead of under their tier"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: docs
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]"]
---

# Edwin: *"are these really manual tests?"*

Yes — and that is not the interesting half of the answer.

## Measured

The five rows in `your-trainer`'s **Needs a walk**:

| id | `level:` | `command:` | file |
| --- | --- | --- | --- |
| TST-0011 | `system` | none | `tests/TST-0011-AndroidBleHardeningAcceptance.md` |
| TST-0012 | `system` | none | `tests/TST-0012-IosBleHardeningAcceptance.md` |
| TST-0013 | `system` | none | `tests/TST-0013-IosParityAcceptance.md` |
| TST-0015 | `system` | none | `tests/TST-0015-ProSeatSelectionAndHiddenRiders.md` |
| TST-0018 | `system` | none | `tests/TST-0018-EntitlementResolution.md` |

All five are `status: ready` with no `command:`, so under [[ADR-0034]] they are manual: a person runs them. That part of the surface is correct.

**Three of them are named `…Acceptance`.** They are acceptance tests that never got `level: acceptance`, because they predate the migration and live in `docs/tests/` rather than `docs/tests/acceptance/`. `_tests_groups` excludes `level: acceptance` and routes the rest into flat buckets — so the level, not the content, is what decides where a test appears.

## Why this is the phase's shape

The reader sees five acceptance tests in a flat list and 579 in tier sections, with nothing on screen explaining the difference. The answer is a frontmatter field neither list mentions.

**The fix is data, not code** — and that makes it the one item here that needs a judgement per note rather than a rule. `EntitlementResolution` and `ProSeatSelectionAndHiddenRiders` are not obviously acceptance tests just because they are manual and system-level.

## Done when

- [ ] Each of the five is assigned a `level:` deliberately, with the reasoning recorded.
- [ ] Whatever the outcome, no test's *group* contradicts its own name.
