---
type: "[[task]]"
id: TASK-0205
aliases: ["TASK-0205"]
title: "Governance — decide the approval-gate policy for planning artifacts (ADR-0007 proposed → accepted/amended/superseded)"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0207]]"]
related: ["[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
tests: []
---

# Approval-gate decision (ADR-0007)

## Definition of Done

- [x] Edwin has decided [[ADR-0007-Planning-Artifact-Approval-Gate]] — accepted as drafted (advisory-first), amended (e.g. gated-by-type from day one), or superseded — and the ADR status reflects it. ADR acceptance is a human decision (STATUSES.md); the agent's job here is to present, not to flip.
- [x] The chosen policy's mechanism implications are recorded where TASK-0207 will read them (what "Accept set" stamps, whether dispatch checks for an accepting `review_verdict`).
- [x] If advisory is confirmed: the measurement plan (per-set outcome recording, revisit trigger) is agreed so the desk can implement it in TASK-0206/0207.

## Steps

- [x] Present ADR-0007 (it is the first item in the ~review Decisions queue by design; until the desk exists, present it directly).
- [x] Record the decision + any amendments in the ADR; update `status`.

## Notes

Drafted at preflight 2026-07-26 with `status: proposed`. The mechanism question is already settled by owner decision (2026-07-26, recorded in the ADR's alternatives): no new states — FEAT/TASK sets queue as dispatch-ledger review requests, acceptance stamps the existing review fields, rejection uses `cancelled` — so no upstream STATUSES/TAXONOMY change exists to follow up; what remains open here is the policy (advisory vs gated) and the measurement plan. This task deliberately precedes TASK-0207 in the plan: policy before mechanism-wiring, so "Accept" means something decided rather than something implied by UI.

## Outcome (2026-07-26)

Edwin accepted [[ADR-0007-Planning-Artifact-Approval-Gate]] **as drafted — advisory-first** — and did it *through the review desk*, which is the first production use of the write-back this feature added: the note's diff is exactly what `stamp_decision` writes (`status: proposed → accepted`, plus `reviewed_by` and `review_date`).

**Implementing the decision took almost nothing, which is the point of choosing advisory.** There is no gate to build: dispatch blocks nothing, and the mechanism the ADR names — accept stamps the existing review fields, reject uses `cancelled`, ADR/REQ/TST queue on their own intake states — already shipped in TASK-0206/0207.

Two gaps the acceptance exposed, both now closed:

1. **The measurement was recorded and never read.** `ReviewStore.outcome_counts()` had been counting outcomes since TASK-0206 and nothing surfaced them, so the ADR's revisit trigger ("~20 sets, or PHASE-008 close-out, whichever is later") would have fired with no evidence to look at — the exact failure [[ADR-0006-Retire-Delivered-Band]] was written about. The queue payload now carries `outcomes`/`reviewed`, and the queue pane renders the tally with the line that actually matters: how many sets *changed* on review.
2. **Lone-note decisions wrote no verdict.** The ADR names the future gate predicate as "has an accepting `review_verdict`", not a status check; `stamp_decision` wrote `reviewed_by`/`review_date` only, so an accepted ADR or requirement would have been invisible to that gate if the advisory phase ever promotes. It now writes `plan-accepted`/`plan-rejected` — still not close-out's vocabulary, so the verification gate stays unsatisfiable from here.

The revisit is now a PHASE-008 close-out item with real data behind it.

