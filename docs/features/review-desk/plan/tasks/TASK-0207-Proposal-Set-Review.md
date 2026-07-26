---
type: "[[task]]"
id: TASK-0207
aliases: ["TASK-0207"]
title: "Proposal-set review — FEAT + children as one set; per-item ticks; Accept stamps review fields, Reject flips to cancelled via guarded POST /api/notes/review"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: ["[[TASK-0205]]", "[[TASK-0206]]"]
blocks: []
related: ["[[TASK-0074]]", "[[TASK-0174]]", "[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0025-Dispatch-Runtime]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]", "[[RISK-0001-Terminal-Exposure]]"]
tests: []
---

# Proposal-set review

## Definition of Done

- [x] A proposal renders as one set: the FEAT with its REQ/TASK children, each row with an accept tick, title, and status chip; a summary blurb and the set's attachments (design artifacts linked in frontmatter `source:`) render above. The set is identified by its dispatch-ledger review request (ADR-0007 mechanism) — the notes themselves stay at plain `backlog`.
- [x] The proposal view includes impact-analysis output (from the set's notes) and provenance: origin session (FEAT-0019 hook data), prompt, and dispatch-ledger entry.
- [x] **Accept set** stamps the existing independent-review frontmatter — `reviewed_by`, `review_date`, `review_verdict` — into each ticked note via a new review write-back endpoint (`POST /api/notes/review`) and clears the ledger review request. The plan-acceptance verdict value is distinguishable from close-out review's `approved` so it can never satisfy the close-out gate (exact value decided here, recorded back into ADR-0007).
- [x] **Reject** flips the set to the existing `cancelled` status through a statuses.py-guarded transition on the same endpoint; **Request changes** hands off to TASK-0208's dispatch (comment + unticked rows back to the session), leaving the ledger request open.
- [x] Endpoint hardening (the preflight risk-scan finding folded into this DoD per Edwin's 2026-07-26 decision — no separate RISK note): mutation endpoints refuse non-loopback callers via a per-request peer-address check on the shared 0.0.0.0 socket (**not** a separate bind — the wording was corrected after independent review; the terminal endpoint gets a real second bind, these get a guard), asserted by `test_mutation_endpoints_reject_non_loopback_callers`; status transitions are validated against `statuses.py` (invalid → 4xx, nothing written); target paths are canonicalized against the indexed docs tree (TASK-0174 precedent); no arbitrary frontmatter writes — the endpoint can touch only the three review fields and the guarded status transition, nothing else.
- [x] Per-set outcomes (accepted unchanged / accepted amended / changes requested / rejected) are recorded for ADR-0007's advisory-phase measurement.
- [x] Endpoint tests: field allow-list (a payload naming any other frontmatter key is rejected), transition guard, unknown ID, path traversal, the non-loopback refusal (peer-address check, not a bind), concurrent-edit safety (mtime/etag check), snapshot untouched (ADR-0009 — sync happens at pre-commit, not from the endpoint).

## Steps

- [x] Sidecar: `POST /api/notes/review` (review-field stamping + guarded reject transition) on the loopback-only side of the server, with the allow-list and canonicalization guards + tests.
- [x] Renderer: set assembly from the ledger request + the FEAT's `requirements`/`tasks` links; ticks; action row; impact/provenance/attachment panels.
- [x] Ledger: clear-on-accept / keep-open-on-request-changes wiring; outcome recording for the measurement.

## Notes

Write-back precedent: TASK-0074's check-toggle. Mechanism per ADR-0007 (Edwin, 2026-07-26): no new states — pending-ness lives in the dispatch ledger, the durable outcome lands in the note as review fields (accept) or an existing-status flip (reject → `cancelled`). If ADR-0007 later chooses gating over advisory, the gate predicate becomes "has an accepting review_verdict", not a status check — build the desk so that check is cheap.
