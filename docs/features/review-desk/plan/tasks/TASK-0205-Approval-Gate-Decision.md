---
type: "[[task]]"
id: TASK-0205
aliases: ["TASK-0205"]
title: "Governance — decide the approval-gate policy for planning artifacts (ADR-0007 proposed → accepted/amended/superseded)"
status: backlog
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

- [ ] Edwin has decided [[ADR-0007-Planning-Artifact-Approval-Gate]] — accepted as drafted (advisory-first), amended (e.g. gated-by-type from day one), or superseded — and the ADR status reflects it. ADR acceptance is a human decision (STATUSES.md); the agent's job here is to present, not to flip.
- [ ] The chosen policy's mechanism implications are recorded where TASK-0207 will read them (what "Accept set" stamps, whether dispatch checks for an accepting `review_verdict`).
- [ ] If advisory is confirmed: the measurement plan (per-set outcome recording, revisit trigger) is agreed so the desk can implement it in TASK-0206/0207.

## Steps

- [ ] Present ADR-0007 (it is the first item in the ~review Decisions queue by design; until the desk exists, present it directly).
- [ ] Record the decision + any amendments in the ADR; update `status`.

## Notes

Drafted at preflight 2026-07-26 with `status: proposed`. The mechanism question is already settled by owner decision (2026-07-26, recorded in the ADR's alternatives): no new states — FEAT/TASK sets queue as dispatch-ledger review requests, acceptance stamps the existing review fields, rejection uses `cancelled` — so no upstream STATUSES/TAXONOMY change exists to follow up; what remains open here is the policy (advisory vs gated) and the measurement plan. This task deliberately precedes TASK-0207 in the plan: policy before mechanism-wiring, so "Accept" means something decided rather than something implied by UI.
