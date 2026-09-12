---
type: "[[feature]]"
id: FEAT-0148
aliases: ["FEAT-0148"]
title: "One HTML viewer replaces the design bench — any note's page opens in it, and nothing about showing a page is specific to designs"
status: done
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'html viewer vs bench, I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer'"]
goal: "Replace the design bench with one viewer that frames any HTML page a note references, so an agent can show Edwin a page without the page having to be a design."
requirements:
  - "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"
tasks:
  - "[[TASK-0613-A-Generic-HTML-Viewer]]"
  - "[[TASK-0614-Links-Stop-Asking-For-The-Bench]]"
  - "[[TASK-0615-Remove-The-Bench]]"
  - "[[TASK-0616-Intent-After-The-Bench]]"
  - "[[TASK-0617-Register-And-Deck]]"
release: ""
issues:
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
  - "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]"
  - "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[FEAT-0042-Design-Bench]]"
  - "[[FEAT-0147-Pictures-Beside-The-Note]]"
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"
  - "[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
  - "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]"
  - "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"
reviewed_by: model:claude-opus-5
review_date: 2026-09-12
review_verdict: changes-requested
tags: [feature, render, design, removal]
---

# One HTML viewer

## Goal

Edwin, 2026-09-12: *"I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer."*

A page the cockpit can show should not have to be a design. Replace the bench with a viewer that frames any HTML file a note references, and remove the bench, its endpoints and the machinery around it.

## Scope

### In scope

- A viewer that frames an HTML page referenced by any note, whatever the note's type.
- Removal of the `~design` view, the four `/api/design/*` write endpoints, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/design-asset/` and `/design-asset-at/`.
- Unbinding design verdicts from the bench's endpoint so the **buttons stay on the note**: `VERDICT_ENDPOINTS` loses its `design` entry, `DESIGN_REVIEW_FIELDS` and `design_revision` writing go, and the refusal message naming the old endpoint goes with them.
- Removal of the variant strip, `chosen_variant:` and the Choose-a-variant ADR offer.
- Deciding where the design-ID link rule goes, and superseding [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] and [[FEAT-0042-Design-Bench]].
- What the Intent landing shows for designs afterwards.
- The capability register, and telling Deck.
- Removal of the tests that covered the removed feature: `tests/test_design_bench.py` (170 tests, 3,174 lines), and the design-specific parts of `test_design_gate.py` (7), `test_design_variants.py` (11), `test_design_tokens.py` (10).

### Out of scope

- **Side-by-side comparison of two versions.** Deferred by Edwin, and when it is built it must serve `.md` notes too. See the phase note.
- A replacement for region-anchored commenting. Nothing is built to replace it in this feature; the argument is in the table below.
- Images and the attachment convention — [[FEAT-0147-Pictures-Beside-The-Note]].

## What the bench carried, and where each part goes

Measured across 23 design notes in 12 fleet repos on 2026-09-12.

| Capability | Measured use | Where it goes |
| --- | --- | --- |
| Frame an HTML artifact at a declared viewport | 21 of 23 notes declare an `asset:` | **Kept**, as the generic viewer. This is the feature. |
| `## Revisions` log | 6 notes carry real entries (deck DES-0002: 10, your-health DES-0002: 9, this repo's DES-0004: 4) | **Survives for free.** It is Markdown in the note; the note renderer already shows it. Nothing to build. |
| Revision capture (`/api/design/capture`) and side-by-side compare of two shas | The log has 6 users; the capture button wrote some of them | **Retired.** A revision is a commit against the page (`TRACEABILITY.md`, `[[design]]` links) and the reason belongs in the commit message. Writing the log line by hand is one line of Markdown. Compare is the deferred work. |
| Region-anchored comments (`data-design-region`, `/api/design/comment`) | **Used, once, seriously.** 7 artifacts declare regions. 12 region-anchored comments exist fleet-wide, all on `project-os-deck` DES-0002, all written by one reviewer in one pass on 2026-09-05; 4 more comments are document-level. | **Retired, and this one gives something up.** The 16 comments already in notes stay — they are Markdown under `## Review` and the note renderer shows them. What is lost is the anchoring: a new comment can no longer say *which part* it is about except in its own words. One reviewer has ever wanted that, and could have written the same list into the note. If it should come back it is a separate feature with that reviewer's case behind it. |
| Choose-a-variant and the ADR it offers | 1 note uses `## Variant`; `chosen_variant:` set on **0** | **Retired.** Never exercised on a real design. |
| **Accept / Decline on a design** | 7 designs carry a verdict; 3 of those also carry a `design_revision` | **Kept, and it was never the bench's.** The buttons sit on the **note**, from the same actuator table every other type uses. `note_writes.py:239` says so: *"The actuator row still offers the buttons — the vocabulary stays in this table — but they carry the endpoint that has to serve them."* After this, they carry the generic `/api/notes/transition` like a task or an issue. |
| The verdict's binding to a revision (`/api/design/verdict`, `design_revision`) | 3 designs carry a `design_revision`: this repo's DES-0002 and DES-0004, and DES-0009 | **Retired, knowingly, and it re-opens a hazard.** The endpoint's job was to make a verdict name the artifact commit it judged. Dropping it means an approval given to revision 3 silently covers revision 6. Edwin accepted that on 2026-09-12 — *"Drop the binding for now!"* — and **"for now"** is why it is [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]] rather than a closed decision. Existing `design_revision:` values stay in their notes. |
| Ask for review (`/api/design/offer-review`) | The bench header button at `renderer.ts:6637` — the one genuinely bench-hosted write | **Retired as an endpoint.** Putting a design on the review desk is the generic path, the same as any other note. |
| The design rows on the Intent landing | The only way to browse designs | **Kept, re-pointed.** [[TASK-0616-Intent-After-The-Bench]]. |
| The note banner button and the bench header's ID chip | Navigation between note and bench | **Re-pointed.** The note gains a link to its page when it has one; the chip goes with the bench. |

**Two corrections to this table, 2026-09-12, both worth seeing rather than silently absorbed.**

The first version said region comments had **never been used**. They have: 12 region-anchored comments exist, and the retirement row now states what is given up instead of implying nothing is.

The first version also retired *"offer-for-review and the design verdict"* as one row, on the reasoning that verdicts are frontmatter and get written directly. Edwin challenged it — *"The only thing about design verdict buttons, why can we not have these, we currently allow for the other items to be triaged and providing review info?"* — and he was right. Accept and Decline for a design were never bench-hosted; they sit on the note, from the actuator table every type shares, and only their **endpoint** was design-specific. The row was describing a removal that was not on the table. It is now three rows: the buttons are kept, the revision binding is retired with its hazard recorded, and `Ask for review` — the one write that really did live in the bench header — is retired.

Removing a feature means removing its tests. It does **not** mean removing its notes: [[FEAT-0042-Design-Bench]], [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] and their tasks stay at `superseded`, as the record of what was built and why.

**[[REQ-0023-Design-Is-A-Project-Record]] is not superseded and must not be.** It requires that a design, its revisions and its verdicts live in the repo and remain readable without the tool that renders them. Every one of its four acceptance criteria is still satisfied after this work, and two are satisfied better: annotations and verdicts stay plain Markdown in the note, and no design state was ever held in the cockpit's runtime. Superseding it because its feature is being superseded would discard the one clause that makes this removal safe.

## Upstreaming

Everything in this feature stays local — the viewer, the routes, `renderer.ts`, the capability register, and [[ADR-0042-What-May-Be-Framed]], which is a decision about this application's render surface. The upstream half of the phase is in [[FEAT-0147-Pictures-Beside-The-Note]], and the skill flip there must land **before** [[TASK-0615-Remove-The-Bench]].

Deck consumes this sidecar and is affected without being downstream: `docs/reference/cockpit-capability-register.md` rows `shell.reader.design`, `api.write.design`, `shell.reader.render`, `shell.windows` and `api.infra` all change, and Deck's adoption table at `~/Dev/repos/project-os-deck/docs/reference/cockpit-adoption.md` tracks them. [[TASK-0617-Register-And-Deck]].

## Acceptance

- An HTML page any note references opens in the viewer.
- Nothing in the sidecar or the renderer decides display by the word `design`.
- The eight endpoints are gone; each is re-homed or retired with the reason recorded above.
- A design's Accept and Decline still work, from the note, through `/api/notes/transition` — and no longer write `design_revision`.
- A design's `## Revisions` and `## Review` sections still read in the note.
- The Intent landing still reaches every design.
- The capability register names no removed route.

## Links

- Requirement: [[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]
- Tasks: [[TASK-0613-A-Generic-HTML-Viewer]], [[TASK-0614-Links-Stop-Asking-For-The-Bench]], [[TASK-0615-Remove-The-Bench]], [[TASK-0616-Intent-After-The-Bench]], [[TASK-0617-Register-And-Deck]]
- Check: [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]


## Independent review — changes-requested (2026-09-12, model:claude-opus-5)

Fresh context, separate session: the notes and the committed diff, no author transcript. Same model family as the author, recorded in `reviewed_by`. A sidecar of my own on port 8841 (started and stopped by pid); the user's Electron app was not touched.

What held up. All nine removed routes 404 against a freshly started sidecar, and `/framed/` and `/api/cockpit/designs` answer 200. `..` is refused (404 raw, 403 percent-encoded). `tests/test_framing.py`'s two sandbox guards both fail when `allow-same-origin` is added to the frame — I ran that mutation and restored the file. The four deleted test-file counts are exact: 170 tests / 3,174 lines, 11, 10, 12. Deck was told (`project-os-deck` `f9f445f`). `~view/<rel>` resolves correctly because `designs_payload` already returns a docs-root-relative `asset`.

### 1. The bench's removal re-opened the half of ISS-0056 that is not about revisions, and nothing records it

The desk's design branch was re-pointed from `/api/design/verdict` to `/api/notes/decide`. `note_writes.stamp_decision` (`src/project_os_cockpit/note_writes.py:837`) reads `DECIDE_TRANSITIONS` and writes the target status **without looking at the note's current status**. The guard that did look — `_DESIGN_SETTLED` — lived only in `stamp_design_verdict`, which was deleted; the constant survives at `note_writes.py:155` with no caller.

Reproduced. Against a temporary docs tree holding one design at `status: implemented`:

    stamp_decision(index, "DES-0001", reviewer="user:edwin", accept=False)
    -> {'status': 'cancelled', 'review_verdict': 'plan-rejected'}

and with `accept=True` it writes `status: "accepted"` over `implemented`. Two designs in this repo sit at `implemented` (DES-0001, DES-0002) and one at `superseded` (DES-0010). The branch is reachable: any loopback caller may file `POST /api/cockpit/review-request` with `subject: DES-xxxx`, and `review_queue_payload` sets `subject_type` from the index, which is what selects `buildDesignReviewView`.

This contradicts three statements in the record that were written to justify keeping the branch. `TASK-0615`'s outcome says the branch "still keeps a design off the proposal path — which stamps `plan-accepted` and rejects by writing `cancelled` onto a design that may be `implemented`". `renderer.ts:6912` says the same. The change note says it. All three name the two properties — no `plan-accepted`, no `cancelled` over `implemented` — and `/api/notes/decide` has neither: it writes `review_verdict: plan-accepted` / `plan-rejected` (`note_writes.py:893`) and `cancelled` at any status. The endpoint changed; the hazard did not.

`RISK-0009` records only the revision binding. This half is unrecorded, and `ISS-0056` is still `fixed`.

The new guards do not catch it: `test_tests_view.py::test_a_design_verdict_goes_through_the_generic_path_now` asserts a `proposed` design accepts and that `DECIDE_TRANSITIONS["design"] == ("accepted", "cancelled")`. Both pass while the behaviour above is live.

### 2. Accept on a design note writes no verdict at all

`TST-0087` step 5b asks for "the verdict is written and `design_revision` is not". `RISK-0009` says the change "keeps the buttons and drops the second field". Through the note actuator that is not what happens: `performNoteAction` posts to `/api/notes/transition`, and `stamp_transition` writes `status`, `updated` and a decision-record callout — no `reviewed_by`, no `review_date`, no `review_verdict`. Reproduced on a `proposed` design: the resulting frontmatter carries `status: "accepted"` and nothing else new. The walk's evidence line reports only the status, so the step reads as passed against an expectation it did not meet. (The desk path does write the verdict, via `stamp_decision` — the two paths now disagree about what an Accept records.)

### 3. The measurement the retirements rest on does not reproduce

*(This finding's own quotations were briefly mangled when the corrected figures were substituted across these notes; restored, because a finding that misquotes what it corrected is worse than the error it found.)*

The notes claimed **47 design notes across thirteen repos, 33 declaring an artifact, and 24 artifacts declaring regions**. None of the three reproduces. The 48 files matching the design type include 26 `__templates__` copies, and 24 is the number of region markers inside one artifact — `project-os-deck` DES-0002 — not a count of artifacts.

Measured again after the finding, by the `type:` field and excluding templates: **23 design notes across 8 repos, 21 declaring a non-empty `asset:`, and 7 HTML artifacts containing `data-design-region`**. The reviewer's own count was 22 notes; the one-note difference is a predicate detail and changes nothing.

What reproduces exactly: 12 region-anchored comments plus 4 document-level, all on deck DES-0002; 1 note with `## Variant`; `chosen_variant` set on 0; 3 notes carrying `design_revision`.

**The conclusion survives and is slightly stronger.** 21 of 23 designs were an HTML file, which is what the frame was for; the review machinery around the frame stayed at one note's worth of comments and a variant convention nobody used.

### 4. The capability register still names a removed route, against a ticked criterion

`REQ-0064` ticks "`docs/reference/cockpit-capability-register.md` has no row naming a removed route". Line 108 (`api.write.notes`) still lists `choose-variant`; line 109 says `/api/notes/choose-variant` is gone. Adjacent rows contradict each other. Line 92 (`shell.state.local`) still lists "design side" as persisted state; `designSide` no longer exists in `renderer.ts`. Line 109 also says "through `api.write.note`" for a row named `api.write.notes`.

### 5. Two ticked DoD lines in TASK-0615 do not describe what happened

- "Accept and Decline are walked on a real design note after the change, **in the window**" — `TST-0087` records step 5b in the renderer harness, on a temporary design (`WALK-0001`), not a real one.
- "Gone: ... the design-bench parts of `test_design_gate.py` (7)" — `tests/test_design_gate.py` is untouched by this change (13 tests, all passing) and should be: it covers the DESIGN-GATE validator check, which still exists. What actually went was `tests/test_annotations.py` (12), which appears in neither the DoD nor this feature's scope list.

### 6. Dead code the removal left behind

No caller anywhere in `src/`, `desktop/src/` or `tests/`: `cockpit.design_regions` (`cockpit.py:1871`), `cockpit.design_asset_at` (`cockpit.py:1893`), `note_writes._DESIGN_SETTLED` (`:155`) and `_DESIGN_KNOWN_STATUSES` (`:146`). The last two carry comments claiming they guard something, which is the failure mode `note_writes.py:141` itself describes. `design_variants` and the register's `variants` field are acknowledged in `TASK-0617`; these four are not mentioned anywhere.

`ISS-0057` is still `fixed` and the mechanism that fixed it — `cockpit.design_note_digest` — was deleted. Only a comment in `tests/test_surface_ownership.py:1047` records that.

### 7. The security argument is right; its conclusion is narrower than the notes claim

ADR-0042's premise checks out. `GET /docs/designs/DES-0002-style-guide.html` and `GET /framed/designs/DES-0002-style-guide.html` both return 200 with identical bodies on an unauthenticated socket, so framing widened no read access. Two things the notes do not say:

- **The `/docs/` copy is the weaker one.** `/framed/` sets `X-Content-Type-Options: nosniff` and is loaded into a frame with an opaque origin; `/docs/` sets neither and serves the same HTML as a top-level **same-origin** document. RISK-0008's "one attribute is the entire security model" describes the hardened path only.
- **The sandbox denies reads, not writes.** `_read_json_body` ignores `Content-Type`, so a CORS "simple request" is executed: `curl -X POST -H 'Content-Type: text/plain' -d '{"kind":"bogus"}' .../api/cockpit/review-request` returns `unknown kind: bogus`, i.e. the body was parsed. A framed page runs with `allow-scripts`, knows its own sidecar URL from `location`, and originates on the machine, so `_require_loopback` passes. It cannot read the reply and does not need to for a write. RISK-0008 calls the residual exposure "presentational"; it is not only that, and ADR-0042 widened the set of files that can be framed from "a design's own artifact" to "any HTML under `docs/`".

Neither is a regression this change introduced. Both belong in the risk note that was closed on the claim that the sandbox is the whole story.

### 8. Smaller things

- `tests/test_framing.py::test_the_viewer_page_is_routed_before_the_bench` compares the index of a `startsWith('~view/')` test against an **equality** test on `'~design'`. Ordering cannot matter between those two, so the assertion is now vacuous; its docstring still describes a bench that is gone.
- The generic viewer is styled entirely with `design-*` classes (`design-view`, `design-head`, `design-frame`, `design-chip`, `design-body`, `design-empty` in `renderViewerPage`), and `PHASE-042`'s reconciliation of the "no display decision named `design`" criterion says the grep returns four hits. It misses `navigateTo('~design')` as the Intent landing (`renderer.ts:12616`), `it.type === 'design'` for the owed set (`:6252`) and `'design'` in `RETIRED_NAV_MODES` (`:4371`).
- `RISK-0008`'s `source:` points at `renderer.ts:5708`, which is now the "Open the page" button; the sandbox line is `:6182`.
- `server.py:2988`'s docstring still refers to `_serve_design_asset_at`, which no longer exists.
- "eight endpoints" and "nine routes" are used interchangeably across `REQ-0064`, `TST-0087` and the change note for the same removal.

## Corrected measurement

**Corrected 2026-09-12 by independent review.** The counts first written here — 47 design notes, 33 declaring an artifact, 24 artifacts declaring regions, across thirteen repos — were wrong: they counted `__templates__` copies as designs and region *markers* inside one artifact as artifacts. Measured again by the `type:` field, excluding templates: **23 design notes across 8 repos, 21 declaring an artifact, and 7 HTML artifacts declaring regions**. The conclusion is unchanged and slightly stronger — 21 of 23 designs were an HTML file, which is what the frame was for, while the review machinery around it stayed at 12 comments on one note, one `## Variant`, and `chosen_variant` set nowhere.
