---
type: "[[issue]]"
id: ISS-0172
aliases: ["ISS-0172"]
title: "A manual test whose procedure has subsections parses to zero steps, so the Run button silently does not exist — 8 of the 15 tests your-trainer is asking a person to walk"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Edwin 2026-08-16: 'it is not really clear how I should execute [them]'", "Measured against ../your-trainer/docs on 2026-08-16"]
severity: high
component: cockpit-server
parent: ""
related: ["[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[ISS-0155]]"]
tests: []
---

# A manual test with subsections has no runnable steps

## Problem

`manual_test_steps` (`src/project_os_cockpit/cockpit.py:2648`) enters at a procedure heading and then breaks at the **first heading of any level**:

```python
if in_section and _ANY_HEADING_RE.match(line):   # ^#{1,6}\s
    break
```

A subheading *of the section it is reading* satisfies that. Demonstrated:

```
## Steps          →  parser enters
### Export        →  parser breaks       ⇒ 0 steps
1. Open Settings…    (never reached)
```

Flat `## Steps` with two items parses to 2. The same two items under a `### Export` subheading parse to 0.

Separately, the heading vocabulary — `steps|checklist|procedure|scenario|script` — does not accept `Cases`, which is what `TST-0018` uses.

## Where it bites

Measured across the 15 manual tests `../your-trainer` currently asks a person to run, **8 parse to zero steps**:

| test | shape | steps |
| --- | --- | --- |
| TST-0007, TST-0008 | `## Steps` + `### Export` / `### Wipe` | 0 |
| TST-0009 | `## Procedure` + `### Tier 1 — golden path` | 0 |
| TST-0011, TST-0012 | `## Tiers` + `### Tier B` / `### Tier A` | 0 |
| TST-0013 | sixteen `## N. Area` sections of checkboxes | 0 |
| TST-0014 | `## A — Input screens` + `### A.1` | 0 |
| TST-0018 | `## Cases` | 0 |

None of these notes is malformed. They are ordinary Markdown, and the two-level shape is the natural one for a procedure with parts.

## Why it matters

The consequence is **silent in all three places the affordance lives**:

- `renderer.ts:4213` — `if (test.manual && test.steps > 0)` → no `Run ▸` on the verification-panel row
- `renderer.ts:1715` — `if (steps === 0) return;` → no `Verify` row on the note page at all
- the runner page, if reached by URL, says *"This test has no parsable ## Steps section — add numbered steps to run it here"*

So a reader opening `TST-0018` — written 2026-08-15 for `FEAT-0104`, the focus feature — sees a manual test with no way to run it and nothing saying why. That is Edwin's report in one line: *"it is not really clear how I should execute."*

An affordance that vanishes silently is worse than one that explains itself, and worse still than one that is simply always present.

## Expected

1. The procedure section ends at a heading **at or above** its own level, so subsections are part of it. A `##` procedure heading is terminated by the next `##` or `#`, not by a `###` inside it.
2. The heading vocabulary accepts `cases` alongside the existing five.
3. When a test genuinely parses to zero steps, the row **says so** rather than omitting the button — the note is still one click away and the reader learns why the stepper is not offered.

## Notes

This is independent of everything else in [[PHASE-034]] and can land first. It is also the enabler: a publication campaign is walking tests, and today more than half of the ones `your-trainer` would walk cannot be started from the tool.

Point 3 is the part that outlives the parser. However good the vocabulary gets, some note will always fail to parse, and the surface should degrade to an explanation rather than to absence.

## Fixed 2026-08-16

**Three rules, not two.** The level fix and the `cases` vocabulary reach four of the eight (TST-0007, 0008, 0009, 0018). The other four — TST-0011, 0012, 0013, 0014 — have **no procedure heading at all**: their whole body is sections of checkboxes (`## A — Input screens`, sixteen `## N. Area` sections), so there was nothing for a vocabulary to match. They are covered by a third rule: *when no heading names a procedure, the checkboxes are the procedure.*

A checkbox specifically, not any list item — a checkbox is an explicit *this is a thing to do* mark where a bullet inside a Purpose paragraph is prose. Measured before choosing it: **6 of the 65 TST notes fleet-wide contain one**, so the fallback is narrow and leaves the other 59 untouched.

**Result: every manual test in the fleet now parses.** `your-trainer` goes from 8 of 15 unrunnable to 0; TST-0018 yields 8 steps, TST-0013 yields 107. Verified against a live sidecar, not only in-process.

### Two defects found by reading the parser's own output

1. **A bold lead-in was a step.** `_STEP_ITEM_RE` allowed `[-*]` with `\s*` after it, and a bold run opens with the same character as a `*` bullet — so `**Offline entitlement (ISS-0374)** — on a device holding PRO:` became step 1 of 11, with its closing `**` still attached. Markdown requires whitespace after a list marker; the parser did not. TST-0018 reads 8 clean steps rather than 11 with a wrong first.
2. **Every expectation was a step of its own.** The corpus writes `- **Expected:** …` beneath the step it belongs to; `_EXPECTED_RE` anchored on a bare `Expected:` at line start, so it matched none of them and `_STEP_ITEM_RE` took them all. A procedure of eleven steps rendered as twenty-two, alternating action and expectation. Both are pre-existing and neither was visible until the section they live in started parsing.

### The surface

`renderer.ts:4213` and `renderer.ts:1715` both **returned** on zero steps, so the affordance was absent with nothing said. Both now render the row and say why — *"no steps"* on the verification row, *"No runnable steps found — open the note to walk it by hand"* on the note page. That is the part that outlives the parser, and it is why it was written even though nothing in the fleet currently needs it.

Guards in `tests/test_review_desk.py`, including a **completeness** assertion (`test_every_manual_test_in_this_repo_is_runnable`) rather than a non-zero one — the ISS-0164 lesson, since "some test parses" would have called 7 of 15 fixed. Six mutations, each chosen to defeat a guard rather than to confirm it; two of the first six were silent no-ops from bad shell escaping and were re-run with an apply-check before being believed.
