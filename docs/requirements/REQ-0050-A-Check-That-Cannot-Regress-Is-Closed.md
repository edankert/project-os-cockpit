---
type: "[[requirement]]"
id: REQ-0050
aliases: ["REQ-0050"]
title: "A check that cannot regress is retired with its reason, and the gate delta is stated before it lands"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
priority: medium
scope: "acceptance suite"
implements: "[[FEAT-0131-The-Suite-Is-Refined]]"
acceptance:
  - "[ ] Every retired check names WHY — the automated test that covers it, or the one-time fix that cannot recur. A retirement with no reason is indistinguishable from a deletion."
  - "[ ] No check is deleted. `status: retired`, per ADR-0008."
  - "[ ] The blocking count before and after is measured and stated per repo, BEFORE the change lands."
  - "[ ] Tier 2 closures are individually justified; a blanket rule over Tier 2 is refused, because TESTING.md's default for it is `never removed`."
covers: []
related: ["[[FEAT-0131-The-Suite-Is-Refined]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [requirement]
---

# Retiring a check is a claim, and it needs its evidence

Criterion 3 exists because **this moves a release gate quieter**, and quieter is the direction a gate must never move without somebody deciding it. That sentence has already been earned once this month, on the tier-rule question ([[ISS-0208]]): the change was measured at 60 → 66, and reverted because it contradicted a written rule.

Here the movement is the other way and the same discipline applies — state the number first.

Criterion 4 is the guard against doing the easy thing. Tier 3's holding pen can be handled by rule because its area name records why each check is in it. Tier 2 cannot: its default is permanence, and 158 blanket retirements would be indistinguishable from losing the suite.

## Acceptance criteria

- [x] Every retirement names its reason — **vacuously: nothing was retired.** [[TASK-0518]] decided *no retirements* (Edwin, 2026-08-20) after [[TASK-0525]] read all 73 Tier 2 checks individually, and [[TASK-0517]] **kept** all 60 parking-bay checks with their recovered areas rather than retiring any. Marked as satisfied-because-empty, not as exercised.
- [x] Nothing deleted; `retired` — no check note was deleted anywhere in this phase, and none was set to `retired` either. The mechanism that made deletion unnecessary is [[TASK-0526]]'s **resting**: a regression guard whose issue is closed is kept, counted, listed, not asked about, and wakes on its own if the issue reopens.
- [x] Gate delta measured and stated first — [[TASK-0517]] states it **before** landing, as its own header instructs: `your-trainer` 581 items / 59 blocking, unchanged, with an **indexed** loader that can detect a change and reports none. The instrument matters: [[ISS-0213]] was simulated with an index-less loader where the numbers could not move, and that non-result was reported as proof.
- [x] Tier 2 justified per check — [[TASK-0525]]'s individual read of all 73: **35** name a `FEAT-*`, 15 name only a `TASK-*`, 17 name something else, **6 name nothing**. All 73 derive to `feature`; the 91 that do name an issue derive to `regression` (86) and `automated` (5) by the same rule. The 6 subject-less ones were given the feature they verify on Edwin's approval.
