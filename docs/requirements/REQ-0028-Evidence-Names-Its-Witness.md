---
type: "[[requirement]]"
id: REQ-0028
aliases: ["REQ-0028"]
title: "Acceptance evidence names its witness"
status: "implemented"
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-11"
source: ["[[DES-0006-The-Acceptance-Desk]]"]
priority: high
scope: "Everything the acceptance runner writes; the property that makes an acceptance record worth having"
specifies: ["[[FEAT-0063-The-Acceptance-Runner]]"]
acceptance:
  - "Every tick the runner writes carries who and when, machine-composed — never typed, never omitted"
  - "A run's log line in the feature note names the same witness and totals (passed / failed→issues / skipped)"
  - "accepted_by is only ever written by a completed run — no path stamps it directly"
  - "An agent cannot be a witness: the runner's writes are actuator-row actions, loopback-only, human-initiated by REQ-0026's terms"
reviewed_by: "user:edwin"
review_date: "2026-08-03"
review_verdict: "plan-accepted"
---

# Evidence names its witness

The difference between acceptance and a checkbox: `- [x]` says something was ticked; *accepted in cockpit run, user:edwin, 2026-08-03* says who stood behind it. PHASE-022 ran twelve acceptance rounds whose only witness record is a chat transcript — this requirement is why that cannot recur.

## Acceptance Criteria

- [x] Every tick the runner writes carries who and when, machine-composed — never typed, never omitted — evidence: `acceptanceEvidence()` composes `accepted in cockpit run, <actor>, <date>` in the renderer and `TICK_TEMPLATE` stamps `({actor}, {date})`; neither is free text on this path, and `test_a_completed_run_names_its_witness_and_totals` asserts it (user:edwin, 2026-08-11)
- [x] A run's log line in the feature note names the same witness and totals (passed / failed→issues / skipped) — evidence: one composed string in `stamp_acceptance_run`, so the log and the frontmatter cannot disagree; walked live to `### 2026-08-11 — user:edwin — 3 passed · 0 failed · 1 skipped` (user:edwin, 2026-08-11)
- [x] accepted_by is only ever written by a completed run — no path stamps it directly — evidence: `stamps = complete and requested == "requested"` is the only writer of `accepted_by`; `test_an_incomplete_run_logs_but_stamps_nothing` and `test_a_feature_that_never_asked_is_logged_but_not_stamped` cover both refusals (user:edwin, 2026-08-11)
- [x] An agent cannot be a witness: the runner's writes are actuator-row actions, loopback-only, human-initiated by REQ-0026's terms — evidence: `_serve_acceptance_run` calls `_require_loopback` before reading the body, and `test_every_note_mutating_endpoint_requires_loopback` found the new route by parsing the POST table — 21 routes, guard required in each (user:edwin, 2026-08-11)

**One criterion was harder to satisfy than to write.** The runner's first target was this very note, which declared four criteria and carried **no checkboxes** — REQ-BOXES' "no verification record". `stamp_tick` rewrites an existing box and could not create one, so the acceptance runner could not record a verdict on the requirement that specifies it. Fixed in [[TASK-0288]]: a first tick may create the box, guarded so the criterion must appear verbatim in this note's own `acceptance:` list.
