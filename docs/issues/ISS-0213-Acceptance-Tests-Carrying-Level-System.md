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

## The judgement, made 2026-08-20

Two of the five had already been resolved before this was picked up: **TST-0015** and **TST-0018** now carry `level: acceptance` and `status: active`, and both render under their tier. The issue's table above is that far out of date.

The remaining three, each read rather than pattern-matched on its name:

| id | judgement | why |
|---|---|---|
| **TST-0011** Android BLE hardening | `acceptance` | *"Validate, on a real smart trainer… This is the gate (with TST-0012 for iOS) that closes TASK-0592/0593/0766, ISS-0256/0329, FEAT-0085, REQ-0185 and RISK-0008. Until every Tier-A row here passes, the branch stays unmerged."* A note that holds a branch shut is an acceptance gate by any reading. |
| **TST-0012** iOS BLE hardening | `acceptance` | The iOS half of the same gate, in the same words. |
| **TST-0013** iOS parity acceptance | `acceptance`, **with a caveat below** | *"Manual acceptance coverage for everything the iOS parity push implemented… so Edwin can verify each new rider-facing surface before the iOS release."* Gates a release. |

**The caveat on TST-0013 is worth more than the level.** It carries **107 checkbox rows** in one note (TST-0011 has 18, TST-0012 has 15). Under [[ADR-0030]] one note is one check, so calling it `level: acceptance` labels a 107-check document as a single acceptance check. The level is still right — the alternative is worse, since `system` routes it to a flat group that contradicts its own title — but the shape is the document-suite [[PHASE-035]] migrated away from, and it should eventually become notes. Noted rather than fixed here: that is a migration, not a field edit.

## Measured before recommending it

Relevelling all three was simulated on a **throwaway copy** of `your-trainer/docs` rather than reasoned about:

```
BEFORE: items=579 blocking=57
AFTER : items=579 blocking=57
newly blocking: []
```

**Zero gate impact.** `acceptance.load` reads the acceptance *directory*, and all three live in `docs/tests/`, so the change moves them in the navigator — out of the flat `Needs you` group and under their tier — and touches nothing the release gate counts. That is exactly the second criterion below and nothing else.

## Not yet applied — the data change needs a hand

The edit is three lines, `level: system` → `level: acceptance`, in:

- `your-trainer/docs/tests/TST-0011-AndroidBleHardeningAcceptance.md`
- `your-trainer/docs/tests/TST-0012-IosBleHardeningAcceptance.md`
- `your-trainer/docs/tests/TST-0013-IosParityAcceptance.md`

It was attempted and **refused by the sandbox** — writes into a second repository are blocked from this one, which is the right default: a change to `your-trainer`'s record should not arrive as a side effect of work in the cockpit.

## Done when

- [x] Each of the five is assigned a `level:` deliberately, with the reasoning recorded — **done above**; two were already applied, three are decided and pending.
- [ ] The three edits land in `your-trainer`.
- [ ] Whatever the outcome, no test's *group* contradicts its own name. Verified for TST-0015/0018 (tier children); pending for the three.
