---
type: "[[plan]]"
title: "Review desk — delivery plan"
status: done
owner: user:edwin
created: 2026-07-26
updated: 2026-07-28
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
implements: ["[[FEAT-0041-Review-Desk]]"]
related: ["[[FEAT-0040-Overview-Rework]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
---

# Review desk — delivery plan

## Delivery sequence

1. **TASK-0205** — decide ADR-0007 (approval-gate policy; drafted at preflight, awaiting Edwin). The mechanism is already fixed by owner decision (no new states — ledger review requests + existing review fields); the policy (advisory vs gated) and the measurement plan are what this decides before TASK-0207 hard-wires the actions.
2. **TASK-0206** — ~review virtual page: queue pane (Decisions / Proposals / Questions / Test runs — FEAT/TASK groups from ledger review requests, the rest from existing intake states), routing, Review mode button + count badge.
3. **TASK-0207** — proposal-set review: set rendering with ticks; Accept stamps `reviewed_by`/`review_date`/`review_verdict` via `POST /api/notes/review` and clears the ledger request; Reject flips to `cancelled` (`statuses.py`-guarded); impact/provenance/attachments panels.
4. **TASK-0208** — question/revise round-trip over the FEAT-0025 dispatch queue (new verbs; ledger entries; replies dispatch back as prompts).
5. **TASK-0209** — manual test runner: Steps parser, stepper UI, Pass/Fail/Skip + evidence, `status`/`last_run` stamping, `## Runs` log, fail→ISS draft. First target: TST-0011.
6. **TASK-0210** — overview announce rows (typed decide/review/answer/run rows in Waiting-on-you, deep-linking into ~review). Needs FEAT-0040's TASK-0200 for the Waiting-on-you list.
7. **TASK-0211** — verification panel: acceptance tests by scope on the feature/phase/release renders (status, last run, staleness, Run + validate-this-scope affordances), extending FEAT-0018's surface. Queue-vs-record: this is the verification half of the durable record (the ~review queue is the doorbell; FEAT-0040's TASK-0212 owns the library half for design input).

## Dependencies

- **Hard:** TASK-0207/0208/0209 need TASK-0206's page shell + routing. TASK-0210 needs FEAT-0040 TASK-0200; TASK-0211 needs TASK-0209's runner for its Run affordances. No vocabulary dependency remains — the ledger mechanism removed it (owner decision 2026-07-26).
- **Soft:** TASK-0205 before TASK-0207 (policy before mechanism-wiring). TASK-0208's verbs before TASK-0207's Request-changes wiring, or land the two together. TASK-0211 must reconcile with FEAT-0018 (in-review) before its UI lands — same surface family, extend not duplicate.

## Open questions

- Advisory vs gated-by-type — deliberately open in ADR-0007; the recommendation (start advisory, measure, decide) is in the ADR for Edwin to accept or amend.
- The plan-acceptance `review_verdict` value — must be distinguishable from close-out review's `approved` so a plan stamp never satisfies the close-out gate (ADR-0007 consequence; decide in TASK-0207).
- Queue source for Questions: dispatch-ledger entries only, or also unanswered `answer` requests persisted across sidecar restarts? Decide in TASK-0206/0208.
- Badge count semantics when an item is open in ~review but unhandled (count it until a decision is recorded, per REQ-0018's no-decay principle?).
