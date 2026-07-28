---
type: "[[issue]]"
id: ISS-0057
aliases: ["ISS-0057"]
title: "Design review staleness follows the artifact only, so the note's prose can change under a reviewer"
status: triage
severity: low
phase: "[[PHASE-999-Unscheduled]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of TASK-0229 rounds 2–3, 2026-07-28"]
related: ["[[TASK-0229-Offer-A-Design-For-Review]]", "[[TASK-0216-Revisions-And-Compare]]", "[[TASK-0220-Revision-Capture]]", "[[TASK-0218-Design-Review-In-The-Desk]]"]
fixed_by: []
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
