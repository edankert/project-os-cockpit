---
type: "[[phase]]"
id: PHASE-008
aliases: ["PHASE-008"]
title: "State & review surfaces"
status: active
order: 8
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
goal: "The cockpit's overview surfaces carry maximum project state above the fold (state before history), and the agent's asks — proposals, decisions, questions, manual test runs — get a first-class human surface (~review) instead of living in terminal scrollback."
features:
  - "[[FEAT-0040-Overview-Rework]]"
  - "[[FEAT-0041-Review-Desk]]"
requirements:
  - "[[REQ-0022-Overview-State-Above-History]]"
depends: ["[[PHASE-007-Agent-Instrumentation]]"]
related: ["[[ADR-0007-Planning-Artifact-Approval-Gate]]", "[[ADR-0006-Retire-Delivered-Band]]", "[[FEAT-0017-Overview-Dashboard]]", "[[FEAT-0023-Overview-Scopes]]"]
design: ["[[REF-0001-Overview-Redesign-Dossier]]"]
---

# Phase 8: State & review surfaces

## Goal

PHASE-007 made the cockpit agent-aware: hooks feed state in, dispatch sends work out. This phase makes the two human-facing halves of that loop first-class. The overview surfaces (FEAT-0017/FEAT-0023) are rebuilt around a single organizing rule — state above the fold, history below it — per the approved design dossier (https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be). And a new ~review virtual page gives the agent's asks (proposal sets, decisions, questions, manual test runs) a place where a human can act on them, with the overview only announcing the queue.

## Scope

- FEAT-0040 — Overview rework: sidecar payload additions (focus block, issue severity, commits endpoint), state-first project overview (focus band, mix-bar stat tiles, phase accordion + Completed band, Waiting-on-you, full-width activity + commits), phase-detail rework (health band, next-action feature rows, exit-criteria evidence, Remaining list), record column right pane, retirement of the Active/Recent nav-mode buttons, and the design-input reference convention + surfaces (TASK-0212 — in-repo dossiers wrapped by reference notes, `design:` links, attachment strip, Library Design group).
- FEAT-0041 — Review desk: governance ADR (approval-gate policy), ~review virtual page with grouped queue and Review mode badge, proposal-set review with review-field write-back, question/revise dispatch round-trip, manual test runner with note write-back, typed announce rows on the overview, and the durable per-scope verification panel (TASK-0211 — acceptance tests with run affordances on feature/phase/release renders, extending FEAT-0018).
- Queue-vs-record rule (Edwin, 2026-07-26): ~review stays the pure transient queue; the durable records live on the scope pages (verification) and in the library (design input) — acting on a queue row writes into a durable home.

## Out of Scope

- Any new status vocabulary, anywhere (owner decision 2026-07-26) — the Completed band is a pure UI grouping over `done` phases (ADR-0006's `test_delivered_band_is_retired` guard stays green), and review pending-ness is dispatch-ledger runtime state, not note state, so STATUSES.md / TAXONOMY.md stay untouched here and upstream.
- Server-side removal of `nav?mode=active` / `mode=recent` — the FEAT-0008 API stability rule keeps both endpoints serving; only the mode buttons retire.
- Enforcement of the approval gate (dispatch refusing unaccepted sets) — ADR-0007 recommends starting advisory; gating is a separate future decision after measurement, and its predicate would be an accepting `review_verdict`, not a status.

## Exit Criteria

- [ ] In a 900 px window, every ~overview section above the fold states current status; the activity sparkbar and commits panel are the only sections that scroll (REQ-0022).
- [ ] The Requirements stat tile renders — `hero.requirements` is no longer computed-but-unrendered.
- [ ] The phase drill-down answers "how far, what gates it, what's left, what's next" without opening a note: header fraction + gates chip, health band, per-feature fractions with a next-action line, and a Remaining list.
- [ ] ~review lists decisions, proposal sets, questions, and runnable manual tests from live index/ledger data; accepting a proposal set stamps the independent-review fields into its members through the guarded review write-back endpoint and clears the ledger request, and rejecting flips the set to `cancelled`.
- [ ] TST-0011 has been executed at least once through the manual test runner, with the run log recorded under its `## Runs` section.
- [ ] ADR-0007 is decided (accepted or superseded), and the mode strip carries Review in the slot Active/Recent vacated while `nav?mode=active|recent` still serve (FEAT-0008 rule).

## Notes

- Sequencing: FEAT-0040's TASK-0199 (sidecar payload additions) first — it is the data pipe the overview stage, phase detail, and record column consume. FEAT-0041 is independently shippable except TASK-0210 (announce rows), which needs FEAT-0040's Waiting-on-you list; ADR-0007 (TASK-0205) should be decided before TASK-0207 hard-wires an accept flow.
- Design source: the dossier artifact above (plates C/D/E, the states audit, and the data-source table) is the canonical design record for both features; both FEAT notes link it.
- The dossier's states audit is a design constraint, not decoration: Waiting-on-you and the review queue may only surface states the corpus actually writes (open issues, in-review stalls, ready-never-executed tests, parked items, open risks, done-but-unclosed phases) — never assumed live states.
