---
type: "[[requirement]]"
id: REQ-0051
aliases: ["REQ-0051"]
title: "Acceptance coverage is produced by a rule at creation and gated at close-out, never by asking a person to remember"
status: draft
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "lifecycle"
implements: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
acceptance:
  - "[ ] The feature scaffold emits an acceptance test note. A feature created through the documented path is never uncovered."
  - "[ ] The validator reports a feature at a terminal status with no test naming it in `covers:` — one error, on the feature, at close-out."
  - "[ ] No per-check obligation is created and no badge counts checks (ADR-0027, ADR-0030)."
  - "[ ] A feature that legitimately needs no acceptance test can say so once, in a field, and be quiet permanently."
  - "[ ] The rule lands upstream in project-os, not only here — it is a lifecycle rule for every repo."
covers: []
related: ["[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[ADR-0027]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
tags: [requirement]
---

# A rule, measured against the thing it replaces

**Criterion 4 is the lesson the sweep already taught**, and it is why this is not simply the sweep with a different trigger. The sweep's three-state `acceptance_impact:` existed precisely so *"nothing to do"* could be said once — and it was still withdrawn, because being asked at all was the cost. So the exception here must be a **field on the feature**, not a prompt: a value the scaffold can leave empty and a person fills once.

**Criterion 2 puts the gate at close-out rather than during the work.** A feature under construction legitimately has no test yet. The moment the claim changes from *"I am building this"* to *"this is done"* is the moment coverage becomes a statement about truth.

**Criterion 5 is where the sweep went wrong structurally.** It was built in `project-os-cockpit` and nowhere else, so it governed one repo's features and the other eleven carried on uncovered. `your-trainer` reached **75 of 102 features with no acceptance check** while the mechanism existed.

## Acceptance criteria

- [ ] The scaffold emits a test.
- [ ] The validator gates terminal features.
- [ ] No per-check obligation, no check-counting badge.
- [ ] A permanent, once-only exception field.
- [ ] Upstream, for every repo.
