---
type: "[[task]]"
id: TASK-0615
aliases: ["TASK-0615"]
title: "Remove the design bench: the view, eight endpoints, the variant strip, and the ~198 tests that covered them"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'I would remove it'"]
parent: "[[FEAT-0148-One-HTML-Viewer]]"
effort: L
depends: ["[[TASK-0613-A-Generic-HTML-Viewer]]", "[[TASK-0614-Links-Stop-Asking-For-The-Bench]]", "[[TASK-0616-Intent-After-The-Bench]]", "[[TASK-0611-Upstream-The-Markdown-First-Contract]]"]
blocks: []
related: ["[[FEAT-0042-Design-Bench]]", "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]", "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]", "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"]
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [task, removal]
---

# Remove the bench

## Definition of Done

- [ ] Gone from `src/project_os_cockpit/server.py`: `/api/design/capture`, `/api/design/comment`, `/api/design/offer-review`, `/api/design/verdict`, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/design-asset/`, `/design-asset-at/`.
- [ ] Gone from `desktop/src/renderer/renderer.ts`: the `~design` view and its stage, the empty state at line 5669, the bench header and ID chip, the variant strip (`buildVariantStrip`), the Choose button and `offerVariantAdr`.
- [ ] Gone from `src/project_os_cockpit/note_writes.py`: `read_design_comments`, `append_design_comment`, `stamp_design_verdict` and `_COMMENT_RE` — unless the review comments in existing notes need them to keep rendering, in which case the **reader** stays and the **writers** go.
- [ ] **The design verdict is unbound from its endpoint, and the buttons stay on the note** ([[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]). `VERDICT_ENDPOINTS` (`note_writes.py:247`) loses its `design` entry so `/api/notes/transition` stops refusing the type; `DESIGN_REVIEW_FIELDS` and the writing of `design_revision` go; the refusal message at `note_writes.py:553` that names `/api/design/verdict` goes with them. `VERDICT_SEMANTICS`' two design rows go too.
- [ ] **The three existing `design_revision:` values are left alone** — this repo's DES-0002 and DES-0004, and DES-0009. A note is never rewritten to erase what was true.
- [ ] Accept and Decline are walked on a real design note after the change, in the window. They are the thing Edwin said must not be lost, and a removal task is exactly where they would be lost by accident.
- [ ] `Ask for review` goes from the bench header (`renderer.ts:6637`) with the header; putting a design on the review desk is the generic path.
- [ ] Gone: `tests/test_design_bench.py` (170 tests), and the design-bench parts of `test_design_gate.py`, `test_design_variants.py`, `test_design_tokens.py`. Removing a feature means removing its tests.
- [ ] `chosen_variant:` and the `## Variant` convention removed from documentation (the upstream half is [[TASK-0611-Upstream-The-Markdown-First-Contract]]).
- [ ] [[FEAT-0042-Design-Bench]] set to `superseded`, `superseded_by: "[[FEAT-0148-One-HTML-Viewer]]"`. Its tasks TASK-0214..0229 keep their statuses; a superseded feature's finished tasks stay done.
- [ ] **[[REQ-0023-Design-Is-A-Project-Record]] is left at `implemented` and untouched.** Check each of its four criteria against the new state before closing this task — all four still hold, and two hold better. Do not supersede it.
- [ ] [[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]] closed as `fixed`, after **checking** that a markdown-only design now opens its note with no apology — not assumed from the deletion.
- [ ] A `CHG-*` note recording the removal, the eight endpoints, and what a reader does instead.
- [ ] `bash tools/scripts/validate-docs.sh` green; full suite run in the **foreground** with a visible `N passed`.

## Steps

- [ ] Do not start until [[TASK-0611-Upstream-The-Markdown-First-Contract]] has landed upstream and synced. Otherwise the authoring skill still tells every agent in every repo to write for this surface.
- [ ] Endpoints first, then the renderer, then the tests, then the notes. Each is its own commit so a bisect can find which half broke something.
- [ ] Grep for `design` across `server.py`, `cockpit.py`, `renderer.ts` and `note_writes.py` afterwards. What is left should be note-type vocabulary only — no route, no mode, no display decision.

## Notes

The scale, measured 2026-09-12: `tests/test_design_bench.py` is 3,174 lines and 170 tests; the three other design test files add 28. That is the cost of the surface, and it is the strongest single argument for Edwin's judgement that the bench does not provide much.

**Amended 2026-09-12.** The first version of this task treated the design verdict as part of the surface being removed. It is not: Accept and Decline live on the note, from the actuator table every type shares, and only the endpoint behind them was design-specific. What is actually retired is the binding of a verdict to an artifact commit, which Edwin accepted knowingly — *"Drop the binding for now!"* — and which re-opens the hazard [[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]] and [[TASK-0375-Decide-And-Accept-On-The-Constraints-View]] exist for. [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]] carries it.

Nothing in this task deletes a note. `docs/designs/` keeps every design, every `## Revisions` log and every `## Review` comment — they are Markdown and the note renderer shows them.
