---
type: "[[task]]"
id: TASK-0203
aliases: ["TASK-0203"]
title: "Record column — right pane on both overview scopes becomes Decisions / Verification / Library cards, phase-scoped on drill-down"
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
related: ["[[FEAT-0023-Overview-Scopes]]", "[[FEAT-0018-Verification-Health-Surface]]", "[[REQ-0013-Cockpit-Layout]]"]
tests: []
---

# Record column

## Definition of Done

- [x] On the project overview scope, `renderOverviewRightPane` renders three cards — Decisions (ADRs with status, newest first, older behind a disclosure), Verification (tests n/m + mix-bar, non-passing tests listed, validator state; **waiver count deferred** — the count has no payload field today and inventing a second scan for it would duplicate FEAT-0018, which owns waiver badges: recorded as a follow-up on that feature rather than faked here, per independent review 2026-07-26), Library (references) — plus the ID-counters line; the pinned-only rendering retires.
- [x] On the phase drill-down scope, the cards scope to the phase: transient In-flight/Attention cards on top (often empty by design), the phase's acceptance tests with live statuses, ADRs whose `related:` links reach the phase (resolved server-side through the link graph by `scope_tests_payload`; an earlier cut matched ids inside ADR titles and would have missed ADR-0007 itself — fixed after independent review, 2026-07-26), and the raw Linked/Backlinks lists demoted to collapsed disclosures — not removed.
- [x] All card data comes from the indexed corpus (`notes_by_type("adr" / "test" / "reference")` + scoped payload); the validator field consumes the FEAT-0018 surface (`/api/cockpit/validation`). Waivers are **not** consumed — see the deferral above; FEAT-0018 owns waiver badges and no payload exposes a count today.

## Steps

- [x] Project-scope record column in `renderOverviewRightPane` (cards, disclosures, counters line).
- [x] Phase-scope variant: acceptance-test join (same TSTs the exit criteria cite), ADR `related:` reachability, linked/backlinks demotion.
- [x] Empty-state handling per card: the Verification card reads "Every recorded test is passing." with the validator line beneath it ("validator clean" / "validator: N errors"). The waiver half of the original example is not rendered, per the deferral above.

## Notes

This is dossier Option A, chosen over B (collapse-by-default) and C (commits in the pane). Always-populated by construction — every real project has ADRs, tests, references — which is what makes it honest where v1's "meanwhile" column was not. The linked/backlinks demotion (rather than deletion) is what keeps FEAT-0023's pane contract and REQ-0013's spirit intact.
