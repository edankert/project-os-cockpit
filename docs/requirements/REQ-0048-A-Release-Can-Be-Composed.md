---
type: "[[requirement]]"
id: REQ-0048
aliases: ["REQ-0048"]
title: "A preparing release can be composed from features and phases, and its gate reports what blocks it"
status: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: "release surface"
implements: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
acceptance:
  - "[ ] A preparing release can add and remove features and phases from the cockpit, written to `features:` on its own note."
  - "[ ] A phase contributes its features; the phase is not stored as a second encoding of the same set."
  - "[ ] When a release names contents, its gate is `blocking_for(those subjects)` rather than the whole suite."
  - "[ ] A release naming nothing behaves exactly as today — derived contents, whole-suite gate. The new path is opt-in."
  - "[ ] The write refuses on a frozen release, like every other release write."
covers: []
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"]
tags: [requirement]
---

# Composing a release

Criterion 4 is the safety property. Deriving contents is what every existing release relies on, and a picker that quietly changed the meaning of `features: []` would rewrite the gate for eleven historical releases. Named contents are **opt-in**, and absence keeps today's behaviour.

Criterion 3 is what makes the picker worth building rather than merely convenient: it is the difference between a release page reporting *the suite* and reporting *itself*. `blocking_for(subjects)` exists and has a production caller; this gives it the subject set a release actually has.

## Acceptance criteria

- [ ] Add and remove features and phases from the cockpit.
- [ ] A phase contributes features; no second encoding.
- [ ] Named contents scope the gate.
- [ ] Naming nothing keeps today's behaviour.
- [ ] Frozen releases refuse.
