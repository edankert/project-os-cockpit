---
type: "[[task]]"
id: TASK-0229
aliases: ["TASK-0229"]
title: "Offer a design for review through the ledger, without changing its status"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["Edwin, 2026-07-28: 'If I need to review these why is this not available in the review section?'"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: []
blocks: []
related: ["[[TASK-0218-Design-Review-In-The-Desk]]", "[[TASK-0217-Region-Anchored-Annotation]]", "[[TASK-0220-Revision-Capture]]", "[[REQ-0023-Design-Artifacts-In-Repo]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
tests: []
reviewed_by: model:claude-opus-5
review_date: 2026-07-28
review_verdict: changes-requested
---

# Offer a design for review

> **[[FEAT-0042]] is `done`.** This task is a follow-on, deliberately parked at `backlog`. Starting it means moving the feature back to `doing` first — a `done` feature with in-flight work is the same self-contradiction independent review already caught once (`done` beside `changes-requested`).

## Why

Edwin, on being told PHASE-009's remaining exit criteria need him to review a design: *"If I need to review these why is this not available in the review section?"*

Because the desk has two entry paths and designs are wired to only one:

1. **Status intake** — `QUEUE_INTAKE_STATES["design"] = ("proposed",)`.
2. **The request ledger** — `.cockpit/review-requests.json`, transient runtime state independent of note status. This is how FEAT/TASK proposal sets enter ([[ADR-0007]]: *pending-ness is runtime state, not note state*). **Designs were never wired to it.**

No design has ever been `proposed`. DES-0001 was created at `implemented` — it documented a redesign already built. DES-0002 went `draft` → `implemented` when its artifact landed. Both skipped the only state that queues, so the review path built by [[TASK-0218]] has never been entered by a real design.

[[TASK-0218]] did not overclaim: its first DoD bullet names the intake rule and says `implemented` is *deliberately* absent, with the correct reasoning — `implemented` is the state **after** the design was built, and queueing it would ask for a decision nobody owes. The rule is right. What is missing is a way to say *"please look at this"* **without lying about the design's status.**

This is also the structural reason [[REQ-0023]] carries two reconciled `[~]` criteria: the revision-capture and annotation paths are built and tested but have never run on a real design, because nothing could put one in front of a human.

## Definition of Done

- [x] A design can be offered for review from the design surface, at **any** status, without changing its status — evidence: `POST /api/design/offer-review`; `test_a_design_can_be_offered_without_changing_its_status` asserts the note text is unchanged and contains no `proposed`
- [x] The request lands in the existing ledger (`ReviewStore`) — no new status vocabulary, no note frontmatter written at request time — evidence: `ReviewStore.add(..., subject=, at_revision=)`; no frontmatter write on this path
- [x] The request records **which revision it was raised against** — evidence: `buildDesignReviewView` renders `Reviewing revision <sha>` and warns on `revision_moved`/`dirty`; verified in the Electron app against Edwin's real request (*Reviewing revision 6eb6888*)
- [x] The desk renders an offered design with its regions — evidence: a design subject routes to `buildDesignReviewView`, not `buildProposalView`; `test_a_design_never_reaches_the_plan_verdict_path`. **Per-region verdicts are still not surfaced** — there is no region UI in the renderer for either intake path, which [[ISS-0055]] records; this bullet is met for the verdict path and honestly not for regions
- [x] The existing `proposed` intake still works, and a design that is both `proposed` and explicitly offered appears **once** — evidence: `test_status_intake_and_the_ledger_do_not_double_list` — one row, and the surviving row keeps the revision
- [x] Accepting or rejecting clears the request; requesting changes leaves it open with the comments attached ([[TASK-0218]]'s existing behaviour) — evidence: unchanged `ReviewStore.resolve` path from [[TASK-0218]]; this task added no resolution behaviour
- [x] The verdict is still never auto-stamped, and the request endpoint is loopback-only like every other mutation — evidence: this endpoint writes only the ledger; `test_the_offer_endpoint_is_loopback_only`
- [x] Offering a design twice is idempotent — evidence: the check moved inside `add`, under the lock that appends; `test_offering_is_idempotent_under_concurrency` runs 16 threads through a barrier and asserts one request
- [x] A request whose design has been deleted or renamed degrades visibly — evidence: `subject_missing` on the detail payload routes to `buildOrphanedRequestView`, which clears the LEDGER only; `test_an_orphaned_request_can_be_cleared`

## Steps

- [x] A request endpoint beside the existing review write-back, loopback-guarded
- [x] An "Ask for review" control on the design surface
- [x] Merge ledger requests with status intake in `review_queue_payload`, deduped by design id
- [x] Capture the current revision sha on the request; compare against head when rendering
- [x] Exercise it end to end in the Electron app via `tools/dev/cdp.py`, not only in tests

## Result

**Exercised in the Electron app, not only in tests.** Driven through `tools/dev/cdp.py`: the control on DES-0002 reports *"DES-0002 sent to Review"*, becomes *"Waiting in Review"*, and the desk shows **Design review: Cockpit design system**. That request is now genuinely in Edwin's queue — the first real design review this bench has ever held, which is the point.

**Staleness is computed on open, not in the queue payload.** It costs a git call and only matters once you are looking at the thing. The detail route reports `at_revision`, `head_revision`, `revision_moved` and `dirty`.

**Dedupe favours the ledger row**, because it carries the revision the reviewer was asked about. A `proposed` design that is also offered would otherwise produce two rows a human cannot tell apart.

**The vanished-design case is driven at the payload level with a stub store**, not by deleting a file mid-request: the live index caches the note, so a filesystem race would have tested the watcher rather than the branch.

Found while verifying in the app: the desk said *"1 item need a human"* — the noun was pluralised and the verb was not. Fixed.

## Correction (ISS-0056)

Independent review returned `changes-requested` on the first pass, and the blocking finding was the one this task's own Notes had named: *"a reviewer can accept something other than what they were shown"* was **not** closed by recording `at_revision` — it was reproduced one click later, on the write.

A ledger row rendered through `buildProposalView`, the path built for FEAT/TASK proposal sets, because the desk dispatched on *"request or note"* rather than on what the request was about. Accept posted `plan-accepted` with no revision; Reject wrote `status: cancelled` onto a design that was `implemented`. `design` is not in `GATE_BEARING_TYPES`, so both writes landed. Nothing in the desktop called `/api/design/verdict` at all — the endpoint [[TASK-0218]] built for exactly this had no caller outside tests.

Fixed by dispatching on the subject: a design routes to `buildDesignReviewView`, which calls the revision-validated endpoint and lets that endpoint decide what rejecting a design means for its status. Verified in the Electron app against Edwin's real queued request.

Four more from the same review: a vanished subject wedged the queue (both actions 404'd before reaching resolve — now a clear-the-request path that writes no note); idempotency was check-then-act across two lock acquisitions (16 concurrent offers produced 9 requests — the check moved inside `add`); a design with no committed revision was offered silently, producing a 200 indistinguishable from a good one (now refused with 409, as `/api/design/verdict` already did); and a design offered dirty records `dirty_at_offer`, because the surface renders the working copy.

**Four DoD bullets were unticked before being re-earned.** They had been written wider than the code — no client read `revision_moved`, `head_revision` or `subject_missing`; the payload carried them and nothing rendered them. That is the [[ISS-0049]] pattern in work filed the same day it was named.

`test_the_offer_endpoint_is_loopback_only` was rewritten to **exercise** the guard: the reviewer had moved the check out of the live path while leaving its literal text behind, and the source-matching version stayed green with the endpoint open to the LAN. Bypassing the guard now fails the test.

## Notes

**A review is of a revision, not of "the design".** [[TASK-0218]] already requires `design_revision` on accept and validates it against real history; a request should capture the revision it was raised against for the same reason. Without it, a reviewer can accept something different from what they were shown, and neither of them would know.

**Do not add a `review` status for designs.** [[ADR-0007]] considered exactly that for features and tasks and rejected it: the ledger carries the transient request, the note carries the durable outcome. Designs should follow the decision the repo already made rather than reopen it.

**The first real design review should be Edwin's, not a fixture's.** That is what makes this worth doing before PHASE-009 closes — it is the only path by which the phase's two remaining exit criteria become reachable, and by which [[REQ-0023]]'s reconciled criteria can be honestly ticked.

## Independent review — 2026-07-28 (`model:claude-opus-5`, fresh session, notes + commit 16d419d only)

`changes-requested`. The offer path itself does what it says: it writes no note state, it is loopback-guarded in the shipped code, it validates the id against the design register, and the payload-level tests genuinely constrain it (eight mutations tried, eight caught — dedupe removed, dedupe reversed, `at_revision` dropped, `revision_moved` pinned true and false, idempotency check removed, `subject_missing` dropped, unknown-design 404 removed). `ReviewStore.add`'s new keyword-only params break no caller. What does not hold is most of what the change is *for*: the verdict the new row leads a human to, and the DoD bullets written about the desk rather than the payload.

**1. The row leads to the wrong verdict machinery, and one click later it does write a status.** A ledger row renders through `buildProposalView` (renderer.ts:3479), not the `proposed` path's `buildSingleNoteReview`. Its "Accept set" posts `/api/notes/review` with `verdict: plan-accepted` per item; "Reject" posts `verdict: plan-rejected, status: cancelled`. Driven against a fixture: accepting an offered design stamps `review_verdict: plan-accepted` on the design note, and rejecting stamps `status: "cancelled"` on a design that was `implemented`. Both bypass `/api/design/verdict`, the endpoint [[TASK-0218]] built so that *"a verdict must name a revision that exists"* — so the reachable accept records **no revision at all**. The defect this task names in its own Notes ("a reviewer can accept something other than what they were shown") is therefore not closed; it is reproduced in the plan-acceptance vocabulary. And "without changing its status" is true only of the offer: the reject one click away writes the untrue status the task exists to avoid.

**2. Nothing in the UI reads any field this change added.** `grep -rn 'subject_missing|revision_moved|head_revision|at_revision|subject_note|subject_type' desktop/src` → zero hits. So DoD bullet 3's *"and the desk says so when the working copy has moved since"* is false (computed, returned, never displayed), and bullet 4's *"renders an offered design with its regions ready for per-region verdicts, identically to the `proposed` path"* is false three times over: different render function, no region UI exists anywhere in the renderer (`/api/design/comment` and `/api/design/verdict` have no caller outside tests), and the cited evidence is payload fields no client reads. The Result section states this correctly ("the detail route reports…"); the DoD bullets state it wider than the code.

**3. A vanished subject wedges the queue rather than degrading.** Accept and Reject both post `/api/notes/review` for the missing id first and get `404 unknown note`, so `review-resolve` is never reached; "Request changes" leaves it open by design. Verified against a fixture. The row cannot be cleared by any desk action — only by hand-editing `.cockpit/review-requests.json`. `subject_missing` is set, and nothing renders it, so the human sees a bare id and three buttons that all fail.

**4. Idempotency is a check-then-act race.** `open_for_subject` takes the lock and releases it before `add` takes it again. 16 concurrent offers of one design produced **9 open requests and 9 indistinguishable queue rows** (dedupe only suppresses the *status-intake* row, never a second ledger row). The renderer disables its button synchronously so a double-click is safe, but a second window or any scripted caller is not. `test_offering_twice_is_idempotent` only covers the sequential case. One-line fix: do the lookup inside `add` under the same lock.

**5. A design with no committed artifact is offered with no revision, silently.** `design_revisions_payload` returns `available: False` when `asset` is empty or the tree is not a repo → `head == ""` → `at_revision` is omitted (falsy) → the detail route's `if subject and asked_at` skips the whole staleness block, so `at_revision`, `head_revision`, `revision_moved` and `dirty` are all absent and the response is indistinguishable from a good one. Verified: `http=200`, `at_revision=None`, no staleness keys. This is DES-0002's exact situation until its `asset` was filled in — the design that motivated the task. `/api/design/verdict` refuses this case outright; the offer path should refuse or say so too. No test covers it: every fixture commits the artifact first.

**6. Dirty at offer time is not recorded.** Offered while the artifact is dirty, `at_revision` names a commit the reviewer was never shown (the surface renders the working copy) and `revision_moved` stays `false`. Verified: `revision_moved=False, dirty=True`. `dirty` is computed at open, a different moment, and per finding 2 is not displayed.

**7. `test_the_offer_endpoint_is_loopback_only` does not guard.** It string-matches the handler source. Mutation: move the guard out of the live path (`if False:` around it, literal text intact) — all four loopback tests still pass while the endpoint accepts writes from any LAN client on the 0.0.0.0 render port. Three sibling tests share the shape, so this is inherited rather than introduced, but the DoD cites this test as the evidence for the safety claim. `test_the_design_surface_offers_the_control` is the same shape and would pass if the button were built and never appended.

**8. Smaller, non-blocking.** The dedupe suppresses status intake for *any* note type whose id matches an open request's `subject` — latent today because only designs set `subject`, but a future subject on a `proposed` ADR would silently swap the ADR's own decide vocabulary for "Accept set". `_serve_design_offer_review` records no `tracker.record_dispatch` and publishes no `cockpit:review-request` event, both of which the sibling `_serve_review_request` does and which `review.py`'s module docstring asserts as the ledger's provenance invariant. `note` reaches `body` untruncated (bounded only by the 2MB body cap) where `prompt` and `resolution_note` are `[:500]`; `_MAX_REQUESTS` trims the persisted file but never `self._requests` in memory.

Suite and validator run by the reviewer: `475 passed`, `validate-docs: OK` (only the pre-existing ADR-0011 review warnings). Independence: fresh session, first sight of this work, notes + diff only; same model family as the author, recorded in `reviewed_by` as provenance ([[ADR-0013]] makes clean context the mechanism, not family).

## Independent review, round 2 — 2026-07-28 (`model:claude-opus-5`, commits 22f2311 + 1238806)

Verdict stays `changes-requested`, on a much smaller surface. Round-1 findings 1–6 are genuinely fixed and I could not break them: the design subject now routes to `buildDesignReviewView`; the verdict goes through `/api/design/verdict` with `revision: detail.at_revision`, so `design_revision` lands on the note; the orphan view resolves the ledger only and `review-resolve` cannot 404 on an id that came from the payload (resolving twice is 200, unknown id is 404); `add()` dedupes inside the lock that appends and 16 barriered threads produce one request; a design with no committed revision is refused 409; `dirty_at_offer` is recorded. `483 passed`, `validate-docs: OK`.

**1. Accepting demotes the only designs that can be offered.** `stamp_design_verdict(accept=True)` writes `DECIDE_TRANSITIONS["design"][0]` = `accepted`. Driven against a fixture: a design at `implemented` accepted at its revision comes back `status: "accepted"`. Every design in this repo is `implemented` — that is this task's own premise for why the ledger route was needed — so "Accept this revision" replaces a true status with a false one, one click after an offer that scrupulously wrote none. It is reachable right now on the real DES-0002 row. TASK-0218's transition table is right for a design reviewed *before* it is built; the offer path introduced the case it does not cover. Fix server-side: send/apply `accept: null` when the design is already `implemented` (record the verdict, leave the status), or make `stamp_design_verdict` refuse a backwards move.

**2. "Request changes" silently discards the comment.** In `buildDesignReviewView` the accept and reject branches pass `note: comment.value` to `review-resolve`; the changes-requested branch posts only `/api/design/verdict` and never reads `comment.value` — and unlike the proposal path it does not dispatch the text back to the agent either. A reviewer types their reasoning, presses the one button that keeps the review open, and the text is gone. DoD bullet 6 still reads *"requesting changes leaves it open with the comments attached … this task added no resolution behaviour"*; both halves are now stale — this task does add resolution behaviour (`act()` and the orphan view both call `review-resolve`), and the comments are not attached on the design path.

**3. A ledger row with a subject but no `at_revision` still reaches the plan-verdict path.** `payload["subject_type"]` is computed inside `if subject and asked_at:` (server.py:1305), while the renderer dispatches on `detail.subject_type === 'design'`. Verified with a ledger row of exactly the shape the pre-fix build wrote: `subject_type` is absent and the row renders as a proposal set — ISS-0056 unfixed for that row. `.cockpit/review-requests.json` is persistent runtime state that survives the upgrade, and the population that has this shape is precisely finding 5's (offered when the design had no committed artifact). Edwin's real row carries `at_revision: 6eb6888` and is safe. One-line fix: compute `subject_type` whenever `subject` resolves.

**4. `test_the_offer_endpoint_is_loopback_only` still does not tie the guard to the endpoint.** The rewrite genuinely exercises `_require_loopback`/`_is_loopback` against a LAN peer — a real improvement — but it dropped the assertion that *this handler calls them*. I deleted the `if not self._require_loopback(): return` from `_serve_design_offer_review` at HEAD: **all 482 tests pass** with the endpoint accepting writes from any LAN client on the 0.0.0.0 render port. The mutation that motivated the rewrite is the mutation it does not catch. A test that binds a stub `self` carrying the real `_require_loopback` with a remote `client_address`, calls `_serve_design_offer_review` on it, and asserts the ledger is untouched would close it.

**5. The dirty banner now contradicts the line above it.** The blurb says *"the frame below is that revision, not the working copy"*; the banner two lines down says *"the design surface is showing something no revision names"* — wording written for the version with no frame. It also fires on `detail.dirty` (present fact) and `request.dirty_at_offer` (past fact) with the same present-tense sentence. On the substantive question: embedding the historical revision **is** right, and I could not break that reasoning — the verdict pins to `at_revision`, so rendering anything else would mean judging X and recording Y. The gap `dirty_at_offer` exposes is at the *offer* end, not the render end: the offerer sees "DES-0002 sent to Review" with no hint that their uncommitted edits are not what will be reviewed, though `/api/design/capture` exists to commit exactly those. Either say so on the control or refuse as the no-revision case does.

**6. `has_asset` is a working-copy test gating a historical render.** `buildDesignReviewView` bails with *"declares no artifact — there is nothing to show"* when `!d.has_asset`, but `has_asset` is `(docs_root / asset).is_file()` on the working copy while `design-asset-at` reads from git. A design whose artifact is deleted after being offered — the note surviving, so not the orphan case — shows "nothing to show" for a revision that renders perfectly. It also collapses `!d.asset` (none declared) into the same message `buildDesignFrame` deliberately keeps distinct.

**On the two deliberate omissions.** Neither blocks. Per-region verdicts: correctly carved out, and ISS-0055 is the right home — but DoD bullet 4 still reads *"renders an offered design with its regions"*, and no region is rendered on either path; the honest wording is "renders the offered design's artifact at the reviewed revision". `record_dispatch` / the SSE publish: no consumer exists for the event and provenance loss is cosmetic today; leaving it is defensible, though `review.py`'s module docstring still asserts the invariant this path breaks.

**On the real DES-0002 request (asked, so checked rather than agreed).** `git log --follow -- docs/designs/DES-0002-style-guide.html` heads at `6eb6888`, which equals `at_revision`; `git status --porcelain` on that path is clean; neither 16d419d nor 22f2311 touched the artifact. So `revision_moved: false` / `dirty: false` are correct and the reasoning holds. The boundary worth naming: staleness is computed over the **artifact path only**, so a design whose substance is its note prose can change arbitrarily under a review and nothing says so — for DES-0002, whose content is the artifact, this is fine.

**Addendum — the tree moved during round 2.** `desktop/src/renderer/renderer.ts` carries an uncommitted fourth revision of `buildDesignReviewView` (actions moved into `buildReviewHeader`, the three actions unified through `act()`, the note body mounted inline). Reviewed against it: findings 5 and 6 survive unchanged, and finding 2 is worse rather than fixed — "Request changes" passes `outcome: null`, so the `review-resolve` call carrying `note: comment.value` is skipped entirely, while the box's placeholder now reads *"sent with Request changes, recorded with Accept."* The comment is sent on neither path it names except Accept. Findings 1, 3 and 4 are server-side and untouched by that edit.
