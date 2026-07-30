---
type: "[[issue]]"
id: ISS-0057
aliases: ["ISS-0057"]
title: "Design review staleness follows the artifact only, so the note's prose can change under a reviewer"
status: fixed
severity: low
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of TASK-0229 rounds 2–3, 2026-07-28"]
related: ["[[TASK-0229-Offer-A-Design-For-Review]]", "[[TASK-0216-Revisions-And-Compare]]", "[[TASK-0220-Revision-Capture]]", "[[TASK-0218-Design-Review-In-The-Desk]]"]
fixed_by: []
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
---

# Half of a design is unversioned, for review purposes

`design_revisions_payload` runs `git log --follow` over the **artifact path**. So `at_revision`, `revision_moved` and `design_revision` all describe the artifact and nothing else.

A design is two things: the artifact says what it looks like, the note says why. The note's prose — rationale, constraints, the Review section — can be rewritten while a review is open, and **nothing says so**. A reviewer can be shown reasoning at the moment of asking, accept a revision, and have the accepted record point at an artifact sha that has no bearing on the prose they actually read.

## Why it is filed separately

The reviewer's reasoning, which I agree with: `design_revisions_payload` is artifact-scoped **by design** — [[TASK-0216]] and [[TASK-0220]] own that decision — and the gap hits the `proposed` status-intake path identically, so it is not [[TASK-0229]]'s to fix. Folding it in would reopen a scope that task deliberately held to the ledger.

## What a fix would have to decide

- **Whether a design's revision means the artifact or the pair.** Pinning to a commit that touched *either* path is the obvious move and changes what `design_revision` means on every existing verdict.
- **What to do about the note's own `## Review` section**, which a review *appends to* — so a naive "did the note change" check goes stale the instant a comment is filed.

Both are real questions, which is why this is a triage note and not a patch.

## Fixed 2026-07-30 — additive, which dissolves both questions

This note said it was "a triage note and not a patch" because two decisions were open. Both stop being decisions once the fix **adds a signal instead of redefining one**.

**"Whether a design's revision means the artifact or the pair."** Neither. `at_revision`, `head_revision` and `design_revision` keep meaning exactly what they meant — the artifact — so **no stored request and no recorded verdict changes meaning**. The note gets its own separate signal alongside them. The difficulty was entirely in redefining an existing field, and nothing here does that.

**"What to do about the note's own `## Review` section, which a review appends to."** Excluded from the digest, along with `## Revisions` and the `reviewed_by` / `review_date` / `review_verdict` / `design_revision` / `updated` frontmatter fields. So recording a review cannot invalidate itself — the objection that kept this in triage — while a rewrite of Problem, Approach, Regions or Tokens does.

**What landed:** `cockpit.design_note_digest(record)` — a 12-char sha256 over the note's substance. `ReviewStore.add` takes `at_note_digest` and the design-offer path supplies it, so both halves are pinned at the moment the reviewer is shown the design. The review detail returns `at_note_digest`, `note_digest` and `note_moved`, mirroring the three artifact fields exactly.

Verified in both directions, which is the only way this fix is correct: appending to `## Review` leaves the digest unchanged, stamping the verdict leaves it unchanged, and changing the Problem changes it. Guarded by `test_a_design_note_digest_ignores_what_recording_a_review_touches`, mutation-verified by removing the section exclusion.

**Not done:** the desk does not yet *render* `note_moved` — the payload carries it and no UI reads it, exactly as `revision_moved` was carried before [[TASK-0229]] surfaced it. Naming that rather than leaving it implied, because a signal nothing renders is the shape of defect [[ISS-0065]] was about.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

The additive framing is right and dissolves the two open questions as claimed. One of the two directions is nonetheless false as implemented.

**`status` is missing from `EXCLUDED_FIELDS`, and the accept path writes it.** `note_writes.stamp_design_verdict` sets `reviewed_by`, `review_date`, `review_verdict`, `design_revision`, `updated` — all five excluded — **and** `status`, via `DECIDE_TRANSITIONS["design"]`, whenever `accept` is passed. So accepting a design through the app's own endpoint changes its digest, and `note_moved` reads true the instant the verdict is recorded. Measured on the field set `stamp_design_verdict` actually writes:

```
digest before accept: 75f3c3b31b1b
digest after  accept: bf126afd62d7   (only difference: status draft -> accepted)
```

That is precisely "filing a review would invalidate itself the instant it was recorded" — the objection this note says the fix answers. `test_a_design_note_digest_ignores_what_recording_a_review_touches` tests the five excluded fields and omits the sixth field the same code path writes, so it is shaped to the incomplete fix rather than to the accept flow.

**The disclosed limit is real and load-bearing.** `note_moved` has no consumer anywhere — not `renderer.ts`, not `static/cockpit.js`. The note names this honestly, which is worth crediting; but `test_the_reviewer_is_told_when_the_artifact_moved` exists in `tests/test_design_bench.py` specifically because the artifact half shipped in that state once already, and the new work reproduces the shape without extending that guard. An `ISS-*` for the desk rendering, or leaving this note short of `fixed`, would both be more accurate than closing it.

**And the failure this issue describes occurred in this same commit range, on the design that specifies it.** `DES-0004`'s accepting verdict was recorded in `4daa6c1`; `0e8008a` then appended a Correction section retracting the "9 tests last verified 66–83 days ago" measurement that the *unproven* mark's justification rests on. `design_revision` still reads `55a743d`, `review_date` is unchanged, and `## Revisions` has no entry for it. Nothing flagged it, because the only mechanism that could have is the one this fix added and no surface reads.
