---
type: "[[requirement]]"
id: REQ-0044
aliases: ["REQ-0044"]
title: "A page whose subject is a release reports the gate and records nothing"
status: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "release surface"
implements: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
acceptance:
  - "[ ] No control on a release page can change a check's mark. Guarded, not merely removed."
  - "[ ] The gate is reported as a verdict plus a breakdown, not as one row per blocking check."
  - "[ ] Every gate row remains a link to the check's own surface, so the walk is one click away."
  - "[ ] The release page shows the open tests for the features it contains."
covers: []
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]"]
tags: [requirement]
---

# A release page records nothing

The rule is [[ADR-0035]]'s: a release is not the subject of an acceptance check, and a page that shows a check's *name* but not its *steps* must not offer the control that attests to the steps.

**Guarded rather than removed** is the operative half of criterion 1. Removing the control fixes today; the guard is what stops the next person adding a convenient tick to the page where clearing the gate is the goal. The same control has now been removed twice from two surfaces ([[ISS-0192]], then this) and neither removal left a test behind.

## Acceptance criteria

- [ ] No control on a release page can change a check's mark.
- [ ] The gate is a verdict plus a breakdown.
- [ ] Gate rows link to the check.
- [ ] Open tests for the release's contents are shown.
