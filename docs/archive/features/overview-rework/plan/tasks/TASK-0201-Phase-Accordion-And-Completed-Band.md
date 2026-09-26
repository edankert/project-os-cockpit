---
type: "[[task]]"
id: TASK-0201
aliases: ["TASK-0201"]
title: "Phase section rework — liveness-sorted accordion with expandable square strips; active-phase meta; finished phases collapse into a Completed band"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0040-Overview-Rework]]"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[ADR-0006-Retire-Delivered-Band]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
tests: []
---

# Phase accordion and Completed band

## Definition of Done

- [x] Phase rows are sorted by liveness (in-flight phases first), and any row expands/collapses its square strip with an explicit chevron; expand state is pure renderer state over the existing `phases[]` payload.
- [x] The active phase row carries fraction, percentage, and in-flight/attention meta (including the done-but-unclosed case: "awaiting close-out" when items are 100% done but the phase note is not closed / gates unmet).
- [x] Finished phases collapse into a band named **Completed** (one line each: name, item count, finish month), expandable like any row; the left scope pane mirrors the same in-flight/Completed ordering.
- [x] The band is a pure UI grouping over `done` phases — no new status, token, or vocabulary; `test_delivered_band_is_retired` and TST-0019 stay green.

## Steps

- [x] Liveness sort + accordion state in `buildPhaseSection` (client-side derive over `phases[].features[].children[]`).
- [x] Active-row meta derivation (in-flight count, attention count, gates fraction from `exit_criteria` when scoped data is present).
- [x] Completed band grouping + one-line collapsed rows; mirror ordering in the scope pane.

## Notes

The name "Completed" is deliberate: ADR-0006 retired the "Delivered" vocabulary the day after v1 of the dossier cited it, and the guard test would rightly fail a reintroduction. Do not introduce a status — this is a view over statuses.
