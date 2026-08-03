---
type: "[[feature]]"
id: FEAT-0063
aliases: ["FEAT-0063"]
title: "The acceptance runner — a feature's criteria walked one at a time; pass ticks with a witness, fail files the issue, the run leaves a log"
status: planned
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0006-The-Acceptance-Desk]]"]
goal: "Generalise the desk's manual-test runner to acceptance: criteria from the feature's requirements presented singly; pass ticks via the tick path with the human as evidence; fail creates a pre-linked issue inline; the run appends its log to the feature note in stamp_test_run's grammar."
requirements: ["[[REQ-0028-Evidence-Names-Its-Witness]]"]
tasks: []
release: ""
related: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[FEAT-0061-Quick-Capture-And-Triage]]", "[[FEAT-0066-Visual-Evidence]]"]
tests: []
---

# The acceptance runner

## Goal

See [[DES-0006]] — the flow, the screens, and what a run leaves behind are specified there. The mechanism is three existing pieces joined: the desk's step-runner shape, PHASE-023's tick and create paths, and `stamp_test_run`'s log grammar aimed at `## Acceptance runs` on the feature.

## Integration points (investigated)

- Criteria source: `acceptance:` lists in REQ frontmatter plus criteria sections in body — the same parse REQ-BOXES uses, exposed via a payload endpoint.
- Ticks and issues: FEAT-0059's verbs; nothing new is written here beyond the run log.
- Capture attach: FEAT-0066's endpoint, referenced per criterion verdict.

## Out of Scope

- Any automation of the judgment. The runner sequences and records; the human decides.
- Running against features with no criteria — the runner refuses with "nothing to accept", which is itself the acceptance-debt signal (FEAT-0065).
