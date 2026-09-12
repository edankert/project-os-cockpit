---
type: "[[task]]"
id: TASK-0615
aliases: ["TASK-0615"]
title: "Remove the design bench: the view, eight endpoints, the variant strip, and the ~198 tests that covered them"
status: done
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

- [x] Gone from `src/project_os_cockpit/server.py`: `/api/design/capture`, `/api/design/comment`, `/api/design/offer-review`, `/api/design/verdict`, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/design-asset/`, `/design-asset-at/`.
- [x] Gone from `desktop/src/renderer/renderer.ts`: the `~design` view and its stage, the empty state at line 5669, the bench header and ID chip, the variant strip (`buildVariantStrip`), the Choose button and `offerVariantAdr`.
- [x] Gone from `src/project_os_cockpit/note_writes.py`: `read_design_comments`, `append_design_comment`, `stamp_design_verdict` and `_COMMENT_RE` — unless the review comments in existing notes need them to keep rendering, in which case the **reader** stays and the **writers** go.
- [x] **The design verdict is unbound from its endpoint, and the buttons stay on the note** ([[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]). `VERDICT_ENDPOINTS` (`note_writes.py:247`) loses its `design` entry so `/api/notes/transition` stops refusing the type; `DESIGN_REVIEW_FIELDS` and the writing of `design_revision` go; the refusal message at `note_writes.py:553` that names `/api/design/verdict` goes with them. `VERDICT_SEMANTICS`' two design rows go too.
- [x] **The three existing `design_revision:` values are left alone** — this repo's DES-0002 and DES-0004, and DES-0009. A note is never rewritten to erase what was true.
- [x] Accept and Decline are walked on a real design note after the change, in the window. They are the thing Edwin said must not be lost, and a removal task is exactly where they would be lost by accident.
- [x] `Ask for review` goes from the bench header (`renderer.ts:6637`) with the header; putting a design on the review desk is the generic path.
- [x] Gone: `tests/test_design_bench.py` (170 tests), and the design-bench parts of `test_design_gate.py`, `test_design_variants.py`, `test_design_tokens.py`. Removing a feature means removing its tests.
- [x] `chosen_variant:` and the `## Variant` convention removed from documentation (the upstream half is [[TASK-0611-Upstream-The-Markdown-First-Contract]]).
- [x] [[FEAT-0042-Design-Bench]] set to `superseded`, `superseded_by: "[[FEAT-0148-One-HTML-Viewer]]"`. Its tasks TASK-0214..0229 keep their statuses; a superseded feature's finished tasks stay done.
- [x] **[[REQ-0023-Design-Is-A-Project-Record]] is left at `implemented` and untouched.** Check each of its four criteria against the new state before closing this task — all four still hold, and two hold better. Do not supersede it.
- [x] [[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]] closed as `fixed`, after **checking** that a markdown-only design now opens its note with no apology — not assumed from the deletion.
- [x] A `CHG-*` note recording the removal, the eight endpoints, and what a reader does instead.
- [x] `bash tools/scripts/validate-docs.sh` green; full suite run in the **foreground** with a visible `N passed`.

## Steps

- [x] Do not start until [[TASK-0611-Upstream-The-Markdown-First-Contract]] has landed upstream and synced. Otherwise the authoring skill still tells every agent in every repo to write for this surface.
- [x] Endpoints first, then the renderer, then the tests, then the notes. Each is its own commit so a bisect can find which half broke something.
- [x] Grep for `design` across `server.py`, `cockpit.py`, `renderer.ts` and `note_writes.py` afterwards. What is left should be note-type vocabulary only — no route, no mode, no display decision.

## Notes

The scale, measured 2026-09-12: `tests/test_design_bench.py` is 3,174 lines and 170 tests; the three other design test files add 28. That is the cost of the surface, and it is the strongest single argument for Edwin's judgement that the bench does not provide much.

**Amended 2026-09-12.** The first version of this task treated the design verdict as part of the surface being removed. It is not: Accept and Decline live on the note, from the actuator table every type shares, and only the endpoint behind them was design-specific. What is actually retired is the binding of a verdict to an artifact commit, which Edwin accepted knowingly — *"Drop the binding for now!"* — and which re-opens the hazard [[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]] and [[TASK-0375-Decide-And-Accept-On-The-Constraints-View]] exist for. [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]] carries it.

Nothing in this task deletes a note. `docs/designs/` keeps every design, every `## Revisions` log and every `## Review` comment — they are Markdown and the note renderer shows them.

## Outcome (2026-09-12)

Eight endpoints gone, plus `/api/notes/choose-variant` which the removal made unreachable: that is **five guarded write paths**, recorded deliberately in `tests/test_remote_peer_refusal.py`, which exists to make exactly this kind of change a decision rather than a drift. `/design-asset/` is now only `/framed/`.

The modules behind them went too — `design_comments_payload`, `design_note_digest`, `design_revisions_payload`, `append_design_comment`, `read_design_comments`, `stamp_design_verdict`, `stamp_chosen_variant`, `resolve_anchor`, and all of `design_tokens.py`. In the shell: the `~design/<ID>` page, the header and chip, the revision rail and compare, the variant strip with Choose and its ADR offer, `Ask for review`, the viewports and the sidebar. `[[CHG-20260912-The-Design-Bench-Becomes-One-Viewer]]` lists it for a reader.

**Accept and Decline were kept, and this is where they would have been lost.** The desk's design branch was rewritten rather than deleted: it still keeps a design off the proposal path — which stamps `plan-accepted` and rejects by writing `cancelled` onto a design that may be `implemented` ([[ISS-0056]]) — and now posts to `/api/notes/decide`, whose `DECIDE_TRANSITIONS` already spoke a design's vocabulary. `VERDICT_ENDPOINTS` and `VERDICT_SEMANTICS` are empty rather than deleted, with the way back written beside them.

**ISS-0300 was checked, not assumed.** In the harness on the built renderer: DES-0003 (no asset) renders with no banner at all, `your-health`'s DES-0002 shows "This design has a page as well as this note" and its button opens `~view/…`, and `~design/DES-0002` lands on the note.

**REQ-0023 was checked criterion by criterion and left at `implemented`**, with the check written into the note. All four hold; two hold better, because there is less runtime to hide design state in than when it was written.

## Four things the removal broke that were not the bench

Each was a test or a constant that lived beside bench code and belonged to something else. Worth naming, because "delete the feature's code" found them only by running the suite:

- `review.py`'s `normalise_anchor` is still called by `ReviewStore.add`; only its sibling `resolve_anchor` belonged to the bench. Removing both took `OUTCOMES`, `_ID_RE` and `_MAX_REQUESTS` with them, which broke the review desk in five tests.
- `test_remote_peer_refusal.py` asserts an exact guarded/open endpoint split, so five removals had to be recorded there as a deliberate edit. That is the guard working.
- `test_tests_view.py` had two tests asserting a design verdict **must not** go through the transition path. They now assert the opposite, with RISK-0009 named — the ISS-0056 half that survives is the vocabulary, not the routing.
- `test_surface_ownership.py`'s digest test lost its subject; a comment records what it checked and where it goes if the binding returns.

## What is left for TASK-0617

The sidecar still parses `## Variant` sections and emits `variants` in the design register, and nothing renders them. It is harmless and Deck may read the register, so it is a decision for the register task rather than a silent deletion here.
