---
type: "[[task]]"
id: TASK-0447
aliases: ["TASK-0447"]
title: "An acceptance row whose subject is not in flight is quiet, not blocking — finishing the application of a decision already accepted"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "[[ADR-0028-Work-Has-Three-Phases]] decision 3"]
parent: "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"
effort: S
depends: []
blocks: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]"]
tests: []
---

# The in-flight rule reaches acceptance rows

## Why

[[ADR-0028]] decision 3 says an obligation asks only while its subject is in flight, and it was applied to requirements and manual tests. Acceptance rows were left out — and they are the population the ADR was written about.

The cost of leaving them out is exact: **20 of `../your-trainer`'s 60 blocking rows are §1.25 Trainer Compatibility, whose feature FEAT-0074 is `backlog`.** They describe a screen that does not exist. A gate that asks a person to walk them is the self-re-arming badge [[ADR-0027]] refuses.

The link that makes this possible already works — [[ISS-0173]] taught `heading_refs` to read the bare `(FEAT-0074)` form, and **60 of 60** blocking rows now name a subject.

## What

Resolve each blocking row's `Item.refs` through the index, read the subject's status, and apply the existing `IN_FLIGHT` / `RESTING_STATES` predicate. A row whose subject rests is **quiet**: excluded from the blocking count, rendered in an expandable group naming the subject and its status.

## The cases that need deciding rather than assuming

- **A row with several subjects** — `## 1.2 Hardware Connectivity (FEAT-0001, FEAT-0007)`. In flight if **any** subject is in flight. Resting requires all of them to rest, because one live subject is enough to make the check walkable.
- **A row with no subject.** Blocking. Absence of a link is not evidence of rest, and this is the direction that fails safe.
- **A subject that does not resolve** — the id is written but no note exists. Blocking, same reasoning.
- **A subject whose status is `done`** — 13 of the 60 are FEAT-0011, `done`. `done` is a resting state, so those go quiet too. That is a real consequence and it is intended: a shipped feature's unchecked acceptance rows are chronic debt, not release-day work, and [[TASK-0446]] already classifies them as chronic. State it in the group so it is not a surprise.

## Done when

- [x] a blocking row whose every subject rests is quiet and not counted
- [x] the quiet group expands, and every row names its subject, that subject's status, and links to it ([[ADR-0028]] decision 5)
- [x] no subject, or an unresolvable subject, is **blocking** — with a test for each
- [x] a multi-subject row is in flight if any one subject is
- [~] the badge count drops by exactly the quiet count — **wrong as written**: the gate contributes ONE obligation to the badge, never sixty (ADR-0027's re-arming rule, and FEAT-0102 built it that way deliberately). Quieting twenty rows cannot move a count that was always 1. What is asserted instead is the thing the criterion was reaching for: `new + chronic + regressed + quiet == blocking == 60`, so the split accounts for every row and loses none
- [x] measured against `../your-trainer`: 60 → 40 blocking, 20 quiet, and the figure recorded
