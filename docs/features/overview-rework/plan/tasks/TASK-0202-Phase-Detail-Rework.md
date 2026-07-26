---
type: "[[task]]"
id: TASK-0202
aliases: ["TASK-0202"]
title: "Phase-detail rework — header fraction/gates chip, one-line health band, next-action feature rows, exit-criteria summary + evidence chips, Remaining list, scoped activity IDs"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0040-Overview-Rework]]"
effort: ""
due: ""
depends: ["[[TASK-0199]]"]
blocks: []
related: ["[[FEAT-0023-Overview-Scopes]]", "[[TST-0012-Scoped-Stats]]"]
tests: []
---

# Phase-detail (scoped) rework

## Definition of Done

- [x] The scoped header gains fraction + percentage and a gates chip (n/m exit criteria, anchoring to the criteria section) alongside the existing crumb, chip, and open-note link — no extra row.
- [x] A one-line health band (scoped counts with inline mix-bars: features, tasks, tests, open issues, in-flight/attention flags) replaces the repeated six-tile hero.
- [x] Feature rows carry fractions; rows with live or pending work gain a next-action second line (doing/next child by ID + title) and an open-issue flag; done rows collapse to one line with long-done ones behind a disclosure.
- [x] Exit criteria render with an n/m summary bar, and criteria whose text names a TST/TASK ID sprout an evidence chip showing that item's live status (client-side ID regex over the criterion text; sidecar parse in `_exit_criteria_from_body` is the durable follow-up).
- [x] A Remaining-work list spells out every not-done item in scope, sorted doing → triage → draft → backlog.
- [x] Scoped activity rows regain their ID column (dropped in TASK-0173's 3-column template) at a tighter row height.

## Steps

- [x] Rework `renderScopedOverview`: header stat-inline + gates chip; health band from the scoped payload.
- [x] Two-line feature rows with next-action derivation from `phases[].features[].children[]` (doing first, else first backlog child; flag open issues in scope).
- [x] Exit-criteria head (fraction + bar) and evidence-chip regex join.
- [x] Remaining list derivation + sort; restore the ID column in the scoped feed template.

## Notes

All client-derivable from the existing scoped `stats_payload` (TST-0012's surface) — the only sidecar dependency is TASK-0199's severity field for attention ordering. Preserves FEAT-0023's select→detail→context contract; only the centre composition changes.
