---
type: "[[requirement]]"
id: REQ-0028
aliases: ["REQ-0028"]
title: "Acceptance evidence names its witness"
status: draft
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0006-The-Acceptance-Desk]]"]
priority: high
scope: "Everything the acceptance runner writes; the property that makes an acceptance record worth having"
specifies: ["[[FEAT-0063-The-Acceptance-Runner]]"]
acceptance:
  - "Every tick the runner writes carries who and when, machine-composed — never typed, never omitted"
  - "A run's log line in the feature note names the same witness and totals (passed / failed→issues / skipped)"
  - "accepted_by is only ever written by a completed run — no path stamps it directly"
  - "An agent cannot be a witness: the runner's writes are actuator-row actions, loopback-only, human-initiated by REQ-0026's terms"
---

# Evidence names its witness

The difference between acceptance and a checkbox: `- [x]` says something was ticked; *accepted in cockpit run, user:edwin, 2026-08-03* says who stood behind it. PHASE-022 ran twelve acceptance rounds whose only witness record is a chat transcript — this requirement is why that cannot recur.
