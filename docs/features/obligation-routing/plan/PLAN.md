---
type: "[[plan]]"
title: "Plan — FEAT-0101 Obligations route by the state of their subject"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: []
implements: ["[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
---

# Plan — FEAT-0101 Obligations route by the state of their subject

## Delivery sequence

1. **[[TASK-0423]] — the shape.** Make an obligation's view derivable per item, and make an unrouted kind fail a test. **First, and alone:** this is a refactor with no behaviour change — every item routes exactly where it routes today — so it can be proven by the existing suite staying green at its current count. Landing it together with the predicate would mean a structural change and a behavioural one arriving in the same diff, with only the second one visible.
2. **[[TASK-0424]] — the predicate.** The in-flight rule for requirements and tests, with `deferred` as the override and the subject-less case chosen deliberately. This is where the number moves, and it moves on one commit that can be measured before and after.
3. **[[TASK-0425]] — the surface.** The collapsed line that makes the quiet inspectable.

2 needs 1. 3 needs 2 — there is nothing to collapse until something is quiet — but 3 must land in the same session as 2, because between them the tool has silently dropped 33 rows from `your-trainer`, which is the failure this feature exists to prevent.

## Dependencies

[[ADR-0028]] must be `accepted`. Per-item routing breaks a stated invariant; doing that on an undecided ADR would make the decision after the fact.

Independent of [[ISS-0172]] and [[ISS-0173]], and of [[FEAT-0102]] — although a test's subject gains a second kind (a release) once [[FEAT-0102]] lands, which is why [[TASK-0424]]'s predicate is written to take a *subject*, not a feature.

## How this is verified

[[TST-0025]] is the automated guard — routing completeness, and the rule's behaviour on constructed fixtures. [[TST-0026]] is the fleet measurement: the before/after numbers in the acceptance criteria are claims about twelve real repos and are checked against them, not against fixtures.

Both exist before this feature can reach `done`. [[FEAT-0100]] closed with `tests: []` and both of its blocking independent-review findings were the class a linked test would have caught; [[PHASE-034]] carries that as an exit criterion.
