---
type: "[[issue]]"
id: ISS-0056
aliases: ["ISS-0056"]
title: "An offered design routes to the plan verdict path, which stamps it without a revision and can cancel it"
status: open
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of TASK-0229, 2026-07-28"]
related: ["[[TASK-0229-Offer-A-Design-For-Review]]", "[[TASK-0218-Design-Review-In-The-Desk]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]", "[[FEAT-0042-Design-Bench]]"]
fixed_by: []
---

# The offer works; the verdict on the other side does not

## Live hazard first

**There is an open request for DES-0002 in Edwin's queue, filed while verifying [[TASK-0229]].** Actioning it is currently unsafe:

- **Accept** → `POST /api/notes/review {verdict: "plan-accepted"}` stamps `review_verdict: plan-accepted` on the design note **with no revision recorded**.
- **Reject** → `{verdict: "plan-rejected", status: "cancelled"}` writes `status: cancelled` onto a design that is `implemented`.

`GATE_BEARING_TYPES` is `{test, change}`, so a `design` note is **not** refused by that endpoint and the write lands. Do not action that row until this is fixed; **Request changes** is safe (it leaves the request open and writes nothing).

## Cause

A ledger row renders through `buildProposalView` (renderer.ts:3479) — the path built for FEAT/TASK proposal sets — because the desk dispatches on *"is this a request or a note"*, not on what the request is about. The `proposed` intake path renders through `buildSingleNoteReview` instead, so **the two entry paths reach different verdict machinery**.

Nothing in the desktop calls `/api/design/verdict` at all — the endpoint [[TASK-0218]] built precisely so *"a verdict must name a revision that exists"* has no caller outside tests.

So the defect [[TASK-0229]] names in its own Notes — *"a reviewer can accept something other than what they were shown"* — is not closed by recording `at_revision` on the request. It is reproduced one click later, in plan vocabulary, on the write.

## The other blocking findings

**A vanished subject wedges the queue.** Accept and Reject both post `/api/notes/review` for the missing id, get `404 unknown note`, and never reach `review-resolve`. The row is unclearable except by hand-editing `.cockpit/review-requests.json` — and since nothing renders `subject_missing`, the human sees a bare id and three buttons that all fail. [[TASK-0229]]'s DoD bullet 9 claims the opposite.

**Idempotency is a check-then-act race.** `open_for_subject` releases the lock before `add` re-takes it. Measured: 16 concurrent offers produced **9 open requests**. Not reachable by double-click (the button disables synchronously) but reachable from a second window or any scripted caller. The fix is to do the lookup inside `add`, under the same lock.

**A design with no committed artifact is offered with no revision, silently.** Empty `asset`, or no git, gives `head == ""`, `at_revision` is omitted, and the detail route's `if subject and asked_at` then skips staleness entirely — a 200 indistinguishable from a good one. That was DES-0002's own situation until its `asset` was filled. `/api/design/verdict` refuses this case; the offer path should too.

**Offered dirty, the revision is a commit the reviewer was never shown.** The surface renders the working copy; `at_revision` names HEAD; `revision_moved` stays false.

## Two DoD bullets were written wider than the code

Recorded because this is the pattern [[ISS-0049]] was filed about:

- *"the desk says so when the working copy has moved"* — **no client reads `revision_moved`, `head_revision`, `at_revision`, `subject_missing`, `subject_note` or `subject_type`.** Zero hits in `desktop/src`. The payload carries them; nothing renders them.
- *"renders an offered design with its regions ready for per-region verdicts, identically to the `proposed` path"* — there is no region UI in the renderer at all, and the two paths demonstrably do not render identically.

The task's Result section describes what was built accurately. The DoD bullets above it do not, and I ticked them.

## And the test cited as safety evidence does not guard

`test_the_offer_endpoint_is_loopback_only` string-matches handler source. The reviewer moved the guard out of the live path while leaving the literal text in the function; **all four loopback tests stayed green** with the endpoint accepting writes from any LAN client on the `0.0.0.0` render port. The guard is correct in the shipped code — what is broken is the evidence that it stays correct. Three sibling tests share the shape, and [[ISS-0055]] already records that this file needs a pass converting string-shaped guards into behavioural ones.
