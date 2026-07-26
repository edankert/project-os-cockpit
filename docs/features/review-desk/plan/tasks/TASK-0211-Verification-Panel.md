---
type: "[[task]]"
id: TASK-0211
aliases: ["TASK-0211"]
title: "Verification panel — acceptance tests by scope: durable panel on feature/phase/release renders with status, last run, staleness, and Run affordances"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: ["[[TASK-0209]]"]
blocks: []
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[TST-0016-Validation-Health]]", "[[TASK-0202]]", "[[TASK-0203]]", "[[FEAT-0040-Overview-Rework]]"]
tests: []
---

# Verification panel — acceptance tests by scope

## Definition of Done

- [x] A durable Verification panel renders on the scopes being validated: the feature note render, the phase detail page (alongside TASK-0202's exit-criteria surface), and releases — REL note renders, driving the existing release-verification playbook (`tools/skills/release-verification/SKILL.md`) when REL notes exist.
- [x] Panel contents per scope: the scope's acceptance tests (linked TSTs) with live status, last run (`last_run`/`last_verified`), and staleness per STATUSES.md's manual-test rules.
- [x] Manual tests carry a Run affordance that launches the TASK-0209 runner (`~review/<TST-ID>/run`); a "validate this scope" affordance starts the scope's runnable tests, opening the first one (**not** an unattended sequence, and — as re-review noted — not a chained one either: finishing a run navigates to the test note it just stamped, so the reviewer returns to the scope themselves. Chaining runs is a possible follow-up, deliberately not claimed here).
- [x] Runs persist in the TST notes' `## Runs` sections (TASK-0209 write-back), so the record outlives the queue: the panel reads only durable note data, never ledger state.
- [x] **FEAT-0018 coordination:** this panel is the same surface family as the Verification health surface (validator status, drift panel, waiver/review badges — currently `in-review`, guarded by TST-0016) and must extend it, not duplicate it — reconcile overlapping UI (badges, waiver display, per-scope validator state) before implementation, and add the cross-links both ways (FEAT-0018 ↔ FEAT-0041/TASK-0211 notes and frontmatter).

## Steps

- [x] Scope→tests join (feature `tests:` + TSTs whose `validates:` reach the scope; phase via its features; release via the REL note's scope) and the panel component with status/last-run/staleness columns.
- [x] Run + validate-this-scope affordances wired to the TASK-0209 runner; sequencing for run-all.
- [x] Release path: REL note render + release-verification playbook as the run-all sequence when REL notes exist (REL counter is 0 today — build the surface, seed later).
- [x] FEAT-0018 reconciliation + two-way cross-links.

## Notes

This is founding ask #1 of the review desk (Edwin, 2026-07-26): "validate a feature/phase/release via acceptance tests" is record-shaped, not queue-shaped — the ~review queue empties as you act, so the validation record must live on the scope pages themselves. Queue-vs-record rule: the queue is the doorbell; acting on a `run` row writes into this panel's durable sources (`## Runs`, test status, `last_run`).
