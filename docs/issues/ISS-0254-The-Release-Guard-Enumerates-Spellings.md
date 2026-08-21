---
type: "[[issue]]"
id: ISS-0254
aliases: ["ISS-0254"]
title: "The ADR-0035 guard enumerates function names, so any new route to a check write reaches a release surface unreported — it was widened three times and evaded each time"
status: open
owner: user:edwin
created: 2026-08-21
updated: "2026-08-21"
source: ["independent review, fifth/sixth/seventh passes while closing PHASE-037, 2026-08-21"]
severity: medium
component: cockpit
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]", "[[TASK-0576-An-Exclusion-Says-Why-And-What-It-Cost]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]"]
tests: []
---

# A guard that names spellings is a guard you can spell around

## Problem

`test_no_write_path_to_a_check_appears_on_the_release_page` enforces [[ADR-0035]] — *a release page reports, it does not record* — by scanning the release surfaces for a **list of forbidden names**. It has been widened three times in three review rounds, and each widening was followed by a reviewer reaching a check write past it.

| round | what got past it | how |
|---|---|---|
| 5 | `buildCheckRow(item)` in `buildReleaseItemPage` | the list named `askForMark`/`walkOneCheck`; the row builder opens the same dialog **one call deeper** |
| 6 | `buildCheckRow(item, true)`, `(item, manual)`, `(c)` | the list then named the *spelling* `buildCheckRow(item)` |
| 7 | `checkMark(item)`, `markCheckRow(item)` | the list named `markGateRow(`, which is **deleted**, and omitted three live routes |

Every one typechecked and left the suite green.

**Widened again 2026-08-21** to name `checkMark(`, `markCheckRow(`, `paintCheckList(` and `/api/notes/retire-check`, and the argument rule on `buildCheckRow` is now scoped to the release region rather than matched over the whole file. **That closes the three known routes and not the class.**

## Why it is worth an issue rather than a fourth widening

**A rule that cannot fire is this phase's signature defect**, and an enumeration that has been evaded three times is one that fires only on what somebody already thought of. Every widening was correct and none of them made the guard *complete*, because completeness here is a property of the **call graph** — *no function reachable from a release surface performs a check write* — and the test asks a question about text.

The product is currently right. A transitive scan of all nine release surfaces finds exactly one route to a check write and it is disarmed. What is missing is a guard that stays right without somebody re-deriving the list after each change.

## Expected

One of:

1. **A reachability rule.** Parse `renderer.ts`, build the call graph from each release surface, and refuse if any reachable function contains a check write. Catches every spelling by construction, including one nobody has written yet.
2. **A type-level split.** A `ReadOnlyCheckRow` that structurally cannot mount a control, so a release surface holding a writable row does not compile. Strongest, and the largest change.
3. **A runtime assertion in the render path** — a release surface that mounts a `button` bound to a write endpoint throws in development.

## Actual

A list of ten strings, correct today, maintained by hand, and re-derived only when a reviewer breaks it.

## Repro

In `desktop/src/renderer/renderer.ts`, inside `buildReleaseItemPage`, add a line calling any function that reaches `postJson('/api/notes/mark-check', …)` under a name **not** in the `forbidden` list of `tests/test_release_held_back.py`. Typecheck and run the suite: both pass. The three names above were the ones available on 2026-08-21; the point is that there is always another.

## Why this is filed rather than fixed

Because it is a **new capability**, not a correction: option 1 is a call-graph analyser this repo does not have, and options 2 and 3 change how the renderer is written. [[PHASE-037]] closed on [[ADR-0035]] holding of the product, which it does — this is about the guard that keeps it holding, and it belongs to whoever opens the next phase rather than to a fourth round of the last one.
