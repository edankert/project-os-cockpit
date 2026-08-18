---
type: "[[requirement]]"
id: REQ-0050
aliases: ["REQ-0050"]
title: "A check that cannot regress is retired with its reason, and the gate delta is stated before it lands"
status: draft
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
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

- [ ] Every retirement names its reason.
- [ ] Nothing deleted; `retired`.
- [ ] Gate delta measured and stated first.
- [ ] Tier 2 justified per check.
