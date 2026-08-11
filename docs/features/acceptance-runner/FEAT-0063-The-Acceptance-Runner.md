---
type: "[[feature]]"
id: FEAT-0063
aliases: ["FEAT-0063"]
title: "The acceptance runner — a feature's criteria walked one at a time; pass ticks with a witness, fail files the issue, the run leaves a log"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0006-The-Acceptance-Desk]]"]
goal: "Generalise the desk's manual-test runner to acceptance: criteria from the feature's requirements presented singly; pass ticks via the tick path with the human as evidence; fail creates a pre-linked issue inline; the run appends its log to the feature note in stamp_test_run's grammar."
requirements: ["[[REQ-0028-Evidence-Names-Its-Witness]]"]
tasks:
  - "[[TASK-0287-The-Criteria-Payload]]"
  - "[[TASK-0288-The-Runner-Surface]]"
  - "[[TASK-0289-Stamp-Acceptance]]"
  - "[[TASK-0290-The-Queue-Entry-And-Resolution]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
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

## Acceptance

- [x] A feature's criteria can be walked one at a time from the cockpit — `~accept/<FEAT-id>`, criterion text large, `Pass / Fail… / Skip-reconcile…`, progress `N of M` ([[TASK-0288]], [[DES-0006]])
- [x] The runner walks exactly what REQ-BOXES counts — proven requirement-by-requirement over the whole corpus against the real `validate-docs.py`, not against fixtures ([[TASK-0287]])
- [x] Pass ticks with a **machine-composed** witness; the walked copy's boxes pass the validator with 0 REQ-BOXES errors ([[REQ-0028]])
- [x] A fail files a pre-linked issue and **the run continues** — a fail is a datum, not an abort
- [x] Reconcile writes the `[~]` form with its reason, so the honest third answer exists
- [x] A completed run appends `### <date> — <witness> — N passed · M failed → ISS-… · K skipped` under `## Acceptance runs`, and stamps `accepted_by`/`accepted_date` **only** when the feature had requested acceptance ([[TASK-0289]])
- [x] An abandoned run keeps the work already done and stays resumable — every verdict writes immediately, so the record is the ledger rather than the in-memory run
- [~] The desk queue entry resolves through `review-resolve` — **reconciled**: [[ADR-0020]] retired the desk and [[FEAT-0090]] removed it. The entry point re-homed to the feature's actuator row, where the obligation lives ([[TASK-0290]])

## Verification

`tests/test_criteria.py` (8) and `tests/test_acceptance_run.py` (8). Both halves of the write path were also **walked end to end** against a throwaway copy: four criteria on REQ-0028 — three passed, one reconciled — then the run recorded, with the validator reporting 0 REQ-BOXES errors on the result.

Two defects a real walk found that no unit test would have: `stamp_tick` could not tick a requirement whose criteria are declared in frontmatter with no boxes (REQ-0028's exact state — the runner's first target was a note it could not write to), and the run stamp refused features that had not opted in, which would have made a walk impossible on most features. Both fixed, both now tested.
