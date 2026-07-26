---
type: "[[requirement]]"
id: REQ-0022
aliases: ["REQ-0022"]
title: "The overview surfaces project state above history — every fact above the fold is current-state; history (activity, commits) is the only thing scrolled"
status: implemented
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
priority: high
scope: "FEAT-0040"
acceptance:
  - "state-only above the fold at 900px"
  - "requirements tile rendered"
  - "quiet state fully designed"
  - "history never outranks state on any overview scope"
implements: "[[FEAT-0040-Overview-Rework]]"
verifies: []
related: ["[[REQ-0013-Cockpit-Layout]]", "[[REQ-0012-Visual-Style]]", "[[ADR-0006-Retire-Delivered-Band]]"]
tests: []
---

# REQ-0022 — Overview state above history

## Statement

The overview surfaces (~overview and ~overview/PHASE-####) SHALL prioritise current project state over historical record: every section rendered above the fold in a 900 px window states what *is* (focus, status mixes, phase liveness, items waiting on the user), and historical sections (activity chart, commits/changes feeds) are the only content the user must scroll for. State surfaces must be honest about quiet: when nothing is in flight, the screens show the audited resting state (last-completed focus with note age, durable attention items, "All clear" when empty) rather than empty live-state placeholders.

## Acceptance Criteria

- [x] In a 900 px window on this repo's corpus, every ~overview section above the fold (focus band, stat tiles, phase rows, Waiting-on-you) presents current-state facts; the activity sparkbar and commits panel are the only sections that may begin below the fold. — evidence: measured 2026-07-26 in `desktop/harness/overview-harness.html` against the built bundle (stage offsets, phase accordion expanded, 8 Waiting-on-you rows): focus band 20–67 px, stat tiles 85–173, phases 191–556, Waiting-on-you 574–721 — the four state sections close at 721 px, inside a 900 px stage. Activity begins at 739 and Commits at 867, so the two history sections are the only ones that can reach the fold, and neither precedes any state section. Note the honest nuance: with a very long phase list Activity can still appear above the fold — what is guaranteed is the ordering (criterion 4), not that history always falls below it.
- [x] The Requirements stat tile renders from `hero.requirements` (computed by `stats_payload` today but never rendered by `buildHero`). — evidence: `desktop/src/renderer/renderer.ts` `buildStatTiles()` emits the Reqs tile from `hero.requirements`; visible as "REQS 21/22" in the harness capture.
- [x] The quiet (no live session) state is fully designed: the focus band reads as "last completed" with the focus note's age; Waiting-on-you lists only durable states the corpus actually holds (open issues, in-review stalls, ready-never-executed tests, parked tasks, open risks, done-but-unclosed phases) and renders "All clear" when empty. — evidence: `buildFocusBand()` adds the pulse/NOW label only when a slot is genuinely active and always renders the note's age (`daysSince`); the empty case renders "All clear — nothing is blocked on a human." **Corrected after independent review (2026-07-26):** the first implementation put all six states in `collectAttention()`, but the phases payload carries no test items (`child_records` is tasks/requirements/issues), so the failing-test and ready-test branches were unreachable — two of the six states could never appear. Tests are now sourced separately in `appendTestAttentionRows()` and the dead branches were removed; the other four states come from `collectAttention()` as before.
- [x] On both overview scopes, no history surface (activity, commits, recent feeds) renders above a state surface. — evidence: `renderProjectOverview()` composes focus → tiles → phases → Waiting-on-you → activity → commits, and `renderScopedOverview()` composes header → health band → features → exit criteria/Remaining → activity; the note feed and donut section were removed rather than relocated.

## Traceability

- Implements: [[FEAT-0040-Overview-Rework]]
- Verified by: to be defined at implementation (TST-* per test-authoring; the fold criterion is a manual/CDP check, the tile and ordering criteria are unit-checkable).
