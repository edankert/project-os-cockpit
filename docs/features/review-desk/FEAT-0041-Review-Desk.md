---
type: "[[feature]]"
id: FEAT-0041
aliases: ["FEAT-0041"]
title: "Review desk (~review) — agent proposals, questions, and manual test runs"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
goal: "A new virtual page (~review, same family as ~overview/~agents/~session) where the agent's asks meet a human: a queue grouped Decisions / Proposals / Questions / Test runs; proposal-set review with Accept set / Request changes / Reject — accept stamps the existing independent-review fields via a guarded review write-back endpoint, reject flips to `cancelled`, no new states anywhere; question/revise round-trips over the dispatch runtime; and a manual test runner that executes TST notes step-by-step and writes results back — announced on the overview by typed Waiting-on-you rows and a queue-count badge on the Review mode button."
requirements: []
tests: ["[[TST-0021-Review-Desk]]"]
tasks: ["[[TASK-0205]]", "[[TASK-0206]]", "[[TASK-0207]]", "[[TASK-0208]]", "[[TASK-0209]]", "[[TASK-0210]]", "[[TASK-0211]]"]
related: ["[[FEAT-0021-Task-Dispatch]]", "[[FEAT-0024-Agent-Verbs]]", "[[FEAT-0025-Dispatch-Runtime]]", "[[FEAT-0030-Agent-Inbox]]", "[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0040-Overview-Rework]]", "[[FEAT-0018-Verification-Health-Surface]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
design: ["[[DES-0001-Overview-Redesign]]"]
---

# Review desk (~review)

## Why

Design review 2026-07-26 (approved dossier: https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be, plate E). Reviewing a proposal set or stepping through a manual test is a *session* — it needs the whole stage, context, and actions — while the project screen's job is to stay glanceable. So the overview **announces** (typed decide/review/answer/run rows in Waiting-on-you, a count badge on the Review mode button that takes Active/Recent's vacated slot) and ~review **acts**. Everything runs on rails that already exist: ADR/REQ/TST intake states (`proposed`/`draft`/`ready`) are in the vocabulary, the dispatch queue and ledger (FEAT-0025) carry round-trips and the FEAT/TASK review requests, session provenance comes from the hooks (FEAT-0019), note write-back has a precedent in the interactive checkboxes (TASK-0074), and acceptance reuses the independent-review frontmatter convention — per Edwin's decision (2026-07-26, ADR-0007): no new states, anywhere. The concrete backlog it drains on day one: TST-0011 has sat at `ready` — defined, never executed — since June.

Structural rule (Edwin, 2026-07-26 — queue vs record): the desk's queue is transient by design — proposals, questions, and pending runs empty as you act — but the desk's two founding asks are record-shaped: validating a feature/phase/release via acceptance tests, and keeping design input visible so it isn't lost. So ~review stays the pure queue, and each founding ask gets a durable home: **the queue is the doorbell; the records live on the scope pages (verification — TASK-0211) and in the library (design input — FEAT-0040's TASK-0212); acting on a queue row writes into a durable home** — review stamps into the note, runs into `## Runs`, decisions into the ADR.

## Scope

1. **TASK-0205 — Governance decision.** [[ADR-0007-Planning-Artifact-Approval-Gate]] (authored at preflight, `status: proposed`) decides the approval-gate policy for planning artifacts: advisory-first vs gated-by-type — the dossier recommends starting advisory, measuring, then deciding. The mechanism is already fixed by owner decision (no new states — see ADR-0007's alternatives); what this task decides is the policy and the measurement plan.
2. **TASK-0206 — ~review virtual page.** Queue pane grouped Decisions / Proposals / Questions / Test runs — ADR/REQ/TST groups driven by their existing intake states (`proposed`/`draft`/`ready`) over the index, the FEAT/TASK Proposals group and Questions driven by dispatch-ledger entries (pending-ness is runtime queue state, not note state) — plus routing (`~review`, `~review/<ID>`, `~review/<TST-ID>/run`) and the Review mode button with its count badge.
3. **TASK-0207 — Proposal-set review.** A FEAT renders with its REQ/TASK children as one reviewable set (identified by its ledger review request; the notes stay at `backlog`): per-item accept ticks; Accept set / Request changes / Reject. Accept stamps the existing independent-review frontmatter (`reviewed_by`, `review_date`, `review_verdict`) into each note via a new `POST /api/notes/review` and clears the ledger request; Reject flips the set to the existing `cancelled` status through a `statuses.py`-guarded transition (write-back precedent: TASK-0074). The proposal view includes impact-analysis output, provenance (origin session via FEAT-0019 hooks, dispatch-ledger entry), and attachments (design artifacts).
4. **TASK-0208 — Question/revise round-trip.** Dispatch-queue verbs (FEAT-0025 runtime): the agent files an answer request; the human's reply — and Request-changes comments + unticked rows — dispatches back to the session as a prompt.
5. **TASK-0209 — Manual test runner.** Parse the TST note's Steps section (exit-criteria parser pattern) into a stepper with expected results and Pass/Fail/Skip + evidence per step; completion stamps `status` + `last_run` and appends a run log under `## Runs`; a failing step drafts an ISS via issue intake.
6. **TASK-0210 — Overview announce rows.** Typed decide/review/answer/run rows in Waiting-on-you deep-linking into ~review — the announce coupling to FEAT-0040.
7. **TASK-0211 — Verification panel (the durable record).** Acceptance tests by scope, rendered on the scopes being validated — the feature note render, the phase detail page, and REL notes (driving the existing release-verification playbook when they exist) — with status, last run, staleness, Run affordances launching the TASK-0209 runner, and a "validate this scope" run-all. Same surface family as FEAT-0018's Verification health surface: extends it, never duplicates it.

## Out of scope

- Enforcing the gate (dispatch refusing unaccepted sets) — that is the future, post-measurement half of ADR-0007; this feature ships the advisory surface. If gating is adopted later, the predicate is "has an accepting review_verdict", a frontmatter check, not a status check.
- Any new status vocabulary — per Edwin's 2026-07-26 decision there are no new states anywhere: FEAT/TASK pending-ness lives in the dispatch ledger, and STATUSES.md / TAXONOMY.md (here and upstream) are untouched.
- General note editing from the cockpit — write-back stays narrow: the three review fields + guarded status transitions through `POST /api/notes/review`, test-run stamping/logs, and checkbox toggles (TASK-0074). The "cockpit is a viewer" constraint (PHASE-007 out-of-scope list) is deliberately relaxed only this far; ADR-0007 records the relaxation.
- Cross-workspace review aggregation (that is ~agents territory; ~review is per-workspace in v1).

## Acceptance

- ~review renders a grouped queue from live data (proposed ADRs, draft requirements/plans, ledger review requests for FEAT/TASK sets, ledger questions, `ready` manual tests) with ages; the Review mode button shows the queue count and the badge clears as items are handled.
- A proposal set can be accepted (each ticked member gets `reviewed_by`/`review_date`/`review_verdict` stamped via `POST /api/notes/review` and the ledger request clears), rejected (the set flips to `cancelled` through a `statuses.py`-validated transition; invalid transitions 4xx and change nothing), or sent back — Request-changes dispatches the comment + unticked rows to the originating session as a prompt through the FEAT-0025 queue with a ledger entry.
- An agent-filed question surfaces as an answer row; replying dispatches the answer back to the session; the exchange is visible in the ledger.
- Running a manual TST steps through its parsed Steps with Pass/Fail/Skip + evidence; completion stamps `status` + `last_run` and appends the run under `## Runs`; a failing step opens a pre-filled ISS draft (issue-intake shape); TST-0011 is executable end-to-end.
- Feature, phase, and release renders carry the durable Verification panel: the scope's acceptance tests with status, last run, and staleness, Run affordances on manual tests, and a "validate this scope" run-all — reading only durable note data, and extending FEAT-0018's verification surface rather than duplicating it (cross-links both ways).
- The proposal view shows provenance (session, prompt, ledger entry), touches (impacted items), and attachments (e.g. this feature's design dossier link).

## Impact analysis (2026-07-26, preflight)

- **FEAT-0025 (dispatch runtime) / FEAT-0024 (agent verbs):** additive — new `question`/`revise` verbs join the registry and travel the existing queue/ledger; TST-0013 (verb registry) and TST-0014 (dispatch ledger) will need extension, not change. No conflict.
- **FEAT-0021 (task dispatch):** unchanged in advisory mode; if ADR-0007 later lands gated-by-type, dispatch gains an acceptance check — that dependency is the gate decision's consequence, recorded there, and is why TASK-0205 precedes TASK-0207 in sequence.
- **FEAT-0030 / REQ-0018 (attention completeness):** the review queue is a new "needs the user" surface; REQ-0018's no-decay rule applies to it (queue rows persist until acted on or dismissed) — supporting, not conflicting. The ledger-not-status mechanism follows the same philosophy: pending-ness is runtime state, like attention items.
- **FEAT-0031 (one agent-status surface per scope):** the Review badge counts human-blocking queue items, not agent state — distinct semantics from the consolidation rule, so no new competing agent-status surface. Noted to keep the boundary deliberate.
- **PHASE-007 "viewer" constraint:** `POST /api/notes/review` extends write-back beyond TASK-0074's checkboxes — a real, deliberate constraint relaxation, recorded in ADR-0007 rather than silently drifted past; the write scope is strictly the three review fields plus guarded status transitions.
- **Status vocabulary (resolved by design, 2026-07-26):** the preflight draft flagged that feature/task vocabularies do not admit `proposed` and sketched an upstream STATUSES/TAXONOMY change; Edwin declined it — no new states anywhere. FEAT/TASK sets queue as dispatch-ledger review requests while the notes stay at `backlog`; acceptance stamps the existing independent-review fields; rejection uses the existing `cancelled` status. No upstream change is needed and the former sequencing dependency is gone. One residual to track (ADR-0007 consequence): the review fields now do double duty (plan acceptance vs close-out review), distinguished by verdict value — decided in TASK-0207.
- **LIFECYCLE preflight:** advisory-first changes no lifecycle step; a later gated policy would amend LIFECYCLE upstream — governed by ADR-0007, with the gate predicate being an accepting `review_verdict`, not a status.

## Risk scan (2026-07-26, preflight; resolution folded into DoDs per Edwin's decision)

`POST /api/notes/review` is a new file-mutating endpoint on the sidecar — larger blast radius than checkbox toggles (review stamps and status flips drive gates). Per Edwin's 2026-07-26 decision no separate RISK note is filed; the hardening is part of TASK-0207's DoD: mutation endpoints follow the terminal-endpoint precedent and bind loopback-only (127.0.0.1 — RISK-0001's pattern), transitions are `statuses.py`-guarded, target paths are canonicalized against the indexed docs tree (TASK-0174 precedent), and no arbitrary frontmatter writes are possible (three review fields + guarded status, enforced by an allow-list with tests). The runner's note write-back (TASK-0209) appends under `## Runs` and stamps only the test-status fields. No new dependency, env var, or path change otherwise — negative result recorded.

## Upstream follow-up (recorded, not executed here)

`tools/scripts/validate-docs.py`'s close-out review check accepts **any** `review_verdict` other than `changes-requested` as evidence of independent review. The desk cannot exploit that — it refuses to stamp gate-bearing note types at all — but the laxity predates this feature and applies to any writer, including a direct edit. The validator is template-owned, so the fix belongs upstream in `~/Dev/repos/project-os/`: the gate should require the close-out vocabulary (`approved`) explicitly rather than treating "not changes-requested" as approval. Raised by independent review, 2026-07-26; nothing template-owned was edited in this repo.

