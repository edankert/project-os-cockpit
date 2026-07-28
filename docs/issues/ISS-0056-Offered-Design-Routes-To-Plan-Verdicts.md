---
type: "[[issue]]"
id: ISS-0056
aliases: ["ISS-0056"]
title: "An offered design routes to the plan verdict path, which stamps it without a revision and can cancel it"
status: fixed
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

## Resolved 2026-07-28

All five findings fixed and verified; the DES-0002 request in Edwin's queue is now safe to action and renders *Accept this revision / Request changes / Reject* against revision `6eb6888`.

## The hazard, as it was

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


## Round 2 (2026-07-28)

Six more, all smaller, all fixed. The two that mattered:

**Accepting demoted the only designs that can be offered.** `stamp_design_verdict(accept=True)` wrote `DECIDE_TRANSITIONS["design"][0]` = `accepted` unconditionally. `accepted` means *agreed, not yet built*; `implemented` means the code shipped. So accepting a design at `implemented` replaced a true status with a false one — **one click after an offer that scrupulously wrote none** — and every design that can be offered today is `implemented`, which is this feature's own premise. It was live on Edwin's real DES-0002 row. A backwards move is now declined while the verdict is still recorded, because the verdict is the honest part.

**The loopback test still did not tie the guard to the endpoint.** Round 1's rewrite exercised `_require_loopback` properly and dropped the assertion that this handler *calls* it: deleting `if not self._require_loopback(): return` from the endpoint left all 482 tests passing, with the endpoint open to the LAN. Third version drives a real request with `_is_loopback` forced false — the only shape that ties a guard to its use. Verified by deleting the call again: it now fails.

That is two consecutive test rewrites that missed the mutation motivating them. Worth stating as a rule: **a guard test must fail when the guard is removed from the thing it guards**, not merely when the guard itself is broken.

The rest: `subject_type` was computed inside `if subject and asked_at`, so a row with a subject and no revision — the shape every pre-fix offer wrote — still reached the plan-verdict path; "Request changes" discarded the reviewer's comment while the placeholder promised it was sent; the dirty banner fired the same present-tense sentence for two different facts and contradicted the line above it; and `has_asset`, an `is_file()` on the working copy, gated a historical render so a deleted artifact hid a revision that renders fine.


## Round 3 (2026-07-28)

**Reject still cancelled a design that shipped** — the mirror of the bug round 2 fixed. The round-2 guard was accept-only, and rank could not have caught it in principle: `cancelled` and `superseded` rank *above* `implemented`, so cancelling a shipped design reads as a **forward** move. Worse, `buildDesignReviewView`'s own docstring said *"rejecting goes through the design endpoint so a built design is not cancelled by a status posted from the client"* — true about the mechanism, false about the consequence, and that sentence is what carried the reject branch through round 2 unexamined.

Fixed with `_DESIGN_SETTLED`: a verdict never moves a design out of `implemented`, `superseded` or `cancelled`, for **either** verdict. A design that shipped cannot be un-shipped by a review; deciding to replace it is a new design or an issue.

**The rank table failed open.** An unranked status returned 0, never compared as backwards, and was silently demoted — quietly reopening the very bug the table exists to prevent. Now fails closed, and a test asserts the table covers exactly `ALLOWED_STATUS["design"]`. The reviewer's verdict on the ISS-0042 worry I raised: it does not apply, because `statuses.py` owns a vocabulary and a band *categorisation*, not a lifecycle order — there was no existing ordering to duplicate.

**The loopback test was one clause short.** Deleting the guard from the endpoint failed it, as intended — but *moving* the guard to sit after `review_store.add(...)` passed: 403 returned, ledger row written. The rule needs both halves: **a guard test must fail when the guard is removed from the thing it guards, and assert the guarded side effect did not happen.** Three versions of this test, three different holes.

**`has_asset` still gated the historical render**, one layer below the round-2 fix: `buildDesignFrame` kept its own unconditional return, so only the message changed. The test greped the outer substring and could not see the inner return.
