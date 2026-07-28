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
- [x] The request records **which revision it was raised against**, and the desk says so when the working copy has moved since — evidence: `test_the_request_records_the_revision_it_was_raised_against` commits a second revision and asserts `revision_moved` flips false → true
- [x] The desk renders an offered design with its regions ready for per-region verdicts, identically to the `proposed` path — evidence: the entry carries `subject`/`subject_note`/`subject_type`, and the detail route returns the request with its items, as for any proposal set
- [x] The existing `proposed` intake still works, and a design that is both `proposed` and explicitly offered appears **once** — evidence: `test_status_intake_and_the_ledger_do_not_double_list` — one row, and the surviving row keeps the revision
- [x] Accepting or rejecting clears the request; requesting changes leaves it open with the comments attached ([[TASK-0218]]'s existing behaviour) — evidence: unchanged `ReviewStore.resolve` path from [[TASK-0218]]; this task added no resolution behaviour
- [x] The verdict is still never auto-stamped, and the request endpoint is loopback-only like every other mutation — evidence: this endpoint writes only the ledger; `test_the_offer_endpoint_is_loopback_only`
- [x] Offering a design twice is idempotent rather than queueing it twice — evidence: `open_for_subject`; `test_offering_twice_is_idempotent` asserts the same `request_id` and one queue row
- [x] A request whose design has been deleted or renamed degrades visibly rather than wedging the queue — evidence: `subject_missing`; `test_a_request_whose_design_vanished_explains_itself`

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

## Notes

**A review is of a revision, not of "the design".** [[TASK-0218]] already requires `design_revision` on accept and validates it against real history; a request should capture the revision it was raised against for the same reason. Without it, a reviewer can accept something different from what they were shown, and neither of them would know.

**Do not add a `review` status for designs.** [[ADR-0007]] considered exactly that for features and tasks and rejected it: the ledger carries the transient request, the note carries the durable outcome. Designs should follow the decision the repo already made rather than reopen it.

**The first real design review should be Edwin's, not a fixture's.** That is what makes this worth doing before PHASE-009 closes — it is the only path by which the phase's two remaining exit criteria become reachable, and by which [[REQ-0023]]'s reconciled criteria can be honestly ticked.
