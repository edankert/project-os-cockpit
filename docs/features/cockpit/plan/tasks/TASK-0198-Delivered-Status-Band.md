---
type: "[[task]]"
id: TASK-0198
aliases: ["TASK-0198"]
title: "Delivered status band — one canonical status vocabulary, applied across all six palette surfaces"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["[[ISS-0023-Implemented-Status-Band-Drift]]"]
parent: "[[FEAT-0006]]"
fixes: ["[[ISS-0023-Implemented-Status-Band-Drift]]"]
effort: M
due: ""
depends: []
blocks: []
related: ["[[REQ-0012-Visual-Style]]", "[[TASK-0016-Status-Palette-Overhaul]]"]
tests: ["[[TST-0019-Status-Vocabulary-Parity]]"]
---

# TASK-0198 — Delivered status band

Successor to [[TASK-0016-Status-Palette-Overhaul]], which established the 6-bucket palette but left `implemented` half-mapped. See [[ISS-0023-Implemented-Status-Band-Drift]] for the drift table.

## Definition of Done
- [x] `src/project_os_cockpit/statuses.py` is the single canonical vocabulary: every project-os status from `tools/instructions/STATUSES.md` assigned to exactly one band (`active`, `pending`, `delivered`, `done`, `archived`, `blocked`, `reference`), plus the terminal/completed subset used by Hide-completed — `src/project_os_cockpit/statuses.py`, exporting `BANDS`, `BAND_TOKEN`, `STATUS_BAND`, `VOCABULARY`, `COMPLETED_STATUSES`, `DELIVERED_STATUSES`, `band_of()`, `is_completed()`.
- [x] `cockpit.py` `TASK_STATUS_ORDER` and `templates.py` `STATUS_RANK` / `COLLAPSED_BY_DEFAULT` derive from `statuses.py` instead of restating it — `COLLAPSED_BY_DEFAULT` is now literally `COMPLETED_STATUSES`; the two ordering tables stay explicit (they encode *priority*, not membership, which is a different question) and are held to the vocabulary by the parity test.
- [x] `implemented` and `staged` occupy the new **Delivered** band: ranked after the pending band and before the done band, **not** collapsed by default, and **not** members of the completed set — `statuses.py` `BANDS["delivered"]`; ranks 50/51/52 against pending ≤35 and done ≥60 (`templates.py:STATUS_RANK`); asserted by `test_delivered_ranks_between_pending_and_done` and `test_delivered_is_not_completed`.
- [x] `base.css` defines `--status-delivered` for light and dark themes at ≤60% saturation, per the [[REQ-0012-Visual-Style]] amendment; `cockpit.css` group-icon rules cover every band member — `hsl(42 46% 34%)` light / `hsl(42 46% 60%)` dark; asserted by `test_every_band_token_is_defined_in_both_themes` and `test_status_tokens_stay_muted`.
- [x] Statuses observed in real corpora but previously unmapped are covered: `released`, `staged`, `rolled-back`, `mitigating`, `monitoring`, `deprecated`, `resolved` — all seven now carry a chip rule, a group-icon rule, and both ranks.
- [x] [[TST-0019-Status-Vocabulary-Parity]] fails if any of the six surfaces drifts from `statuses.py` — confirmed against the real pre-fix tree: reverting `cockpit.js`, `cockpit.css`, and `cockpit.py` to HEAD produces 3 failures, one per drifted surface (evidence in the TST note).
- [x] Full pytest suite green; released to `project-os` via `tools/scripts/release-to-project-os.sh` and synced downstream.

## Verification

`.venv/bin/pytest -q` → **245 passed, 1 skipped** (was 244 + 1 skipped + 1 failure mid-change: `tests/test_index.py::test_implemented_status_sorts_and_collapses_with_the_done_family` asserted the contract this task reverses, and was rewritten as `test_implemented_status_sorts_after_backlog_but_stays_expanded`).

`.venv/bin/ruff check src/ tests/` → 15 errors, unchanged from the pre-change baseline; the two new files are clean.

Guarding test: [[TST-0019-Status-Vocabulary-Parity]] (`tests/test_status_vocabulary.py`, 13 tests, `passing`).

Spec change: [[REQ-0012-Visual-Style]] clause 6 amended (6 → 7 buckets) and clause 7 added; see its `## Amendments` section for the argument and the corpus evidence.

Not covered by automation: a browser visual pass on the new amber hue in light and dark themes.
