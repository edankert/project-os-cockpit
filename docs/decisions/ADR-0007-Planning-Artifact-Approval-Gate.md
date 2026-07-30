---
type: "[[adr]]"
id: ADR-0007
aliases: ["ADR-0007"]
title: "Approval gate for planning artifacts — advisory first, measured before gating"
status: "accepted"
owner: user:edwin
created: 2026-07-26
updated: "2026-07-29"
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
decision: "Adopt an advisory review flow first: every planning artifact set the agent produces is reviewable in ~review, nothing is blocked on acceptance, and the desk records how often review actually changes a plan. The mechanism introduces no new states: FEAT/TASK proposal sets enter the queue as dispatch-ledger review requests while their notes stay at plain `backlog`; accepting a set stamps the existing independent-review frontmatter (`reviewed_by`, `review_date`, `review_verdict`) into each note and clears the ledger request; rejecting flips the set to the existing `cancelled` status; ADR/REQ/TST queue groups use their existing intake states (`proposed`/`draft`/`ready`). Only after measurement decide whether to promote the gate to gated-by-type — and if so, the gate predicate is 'has an accepting review_verdict', not a status check."
context: "Today LIFECYCLE lets preflight create planning artifacts and proceed straight to implementation; the review desk (FEAT-0041) introduces a surface where a human can accept, amend, or reject a proposal set before work starts. Making review a hard gate — dispatch refusing a set that has not been accepted — would be a lifecycle change, and the fleet's own history (ADR-0006: a band nobody ever wrote; upstream ADR-0008: statuses measured before deletion) argues for measuring before legislating. The queue/record split follows ADR-0009 and the REQ-0018 attention model: pending-ness is transient runtime state (the dispatch ledger), the durable outcome lives in the note (review fields, or a real status transition)"
alternatives:
  - "Introduce `proposed` for feature/task vocabularies (the dossier's original sketch) — rejected 2026-07-26, owner preference: no new states; the dispatch ledger + existing review fields cover both the queue (transient pending-ness) and the record (durable outcome) without touching STATUSES/TAXONOMY or the upstream template"
  - "Gated by type from day one — FEAT / REQ / ADR require acceptance before dispatch; TASK breakdowns under an accepted FEAT auto-accept. Rejected for now: adds a human bottleneck to every feature before any evidence that review changes outcomes; revisit with the advisory-phase measurements in hand"
  - "Fully gated — every planning artifact requires acceptance. Rejected: turns the docs system's strength (agents keep documentation current without friction) into a queue, and contradicts the bursty session pattern the states audit documents"
  - "No review surface at all (status quo) — rejected: the asks already exist (proposal sets, questions, never-executed manual tests like TST-0011) and currently live in terminal scrollback where they decay"
consequences:
  - "No LIFECYCLE change is needed for the advisory phase, and no vocabulary change anywhere: notes stay on their existing statuses, so STATUSES.md/TAXONOMY.md and the upstream template are untouched"
  - "The split is ADR-0009-clean: the ledger carries the transient review request (runtime state, like REQ-0018 attention items), the note carries the durable outcome — stamped review fields on accept, a statuses.py-guarded flip to `cancelled` on reject; snapshot sync at pre-commit is unchanged"
  - "The write mechanism is a review write-back endpoint (TASK-0207) — a deliberate, narrow relaxation of the 'cockpit is a viewer' constraint (PHASE-007 out-of-scope list), extending the TASK-0074 checkbox precedent: it writes only the three review fields and guarded status transitions, nothing else"
  - "If gating is later adopted, dispatch's gate predicate is 'set has an accepting review_verdict' — a frontmatter check, not a status check, so gating still introduces no vocabulary"
  - "The review fields do double duty: today they record close-out independent review (e.g. FEAT-0023), now also plan acceptance. The desk must not let a plan-acceptance stamp satisfy the close-out review gate — distinguish by verdict value (decide the exact value in TASK-0207)"
  - "The advisory phase must actually measure: the desk records per-set outcomes (accepted unchanged / accepted amended / changes requested / rejected) so the gating decision is evidence-based, the same lesson ADR-0006 codified"
  - "SETTLED 2026-07-29 — stay advisory, permanently. Not because review rubber-stamps but because the flow the gate would govern does not occur: 1 desk interaction against 62 notes carrying a review_verdict, because review here happens at close-out (QUALITY.md), not before implementation. The measurement obligation is discharged and the tally surface removed (TASK-0247); the store keeps recording outcomes. See the Gating decision section"
related: ["[[FEAT-0041-Review-Desk]]", "[[TASK-0205]]", "[[FEAT-0025-Dispatch-Runtime]]", "[[ADR-0006-Retire-Delivered-Band]]", "[[TASK-0247-Drop-The-Advisory-Tally]]", "[[ISS-0064-Two-Reviewed-Sections]]"]
reviewed_by: "user:edwin"
review_date: "2026-07-26"
---

# Approval gate for planning artifacts

## Context

The project-os lifecycle currently has no human checkpoint between planning and implementation: preflight classifies, allocates IDs, writes the notes, and the agent proceeds. That is by design — the system's value is that documentation keeps up with the work — but it means the moments where a human *should* weigh in (a new feature's shape, a requirement's acceptance criteria, a decision like this one) have no surface. FEAT-0041 builds that surface (~review). What it must not do silently is change the lifecycle's default: whether an unaccepted proposal set may be implemented at all.

Two defensible shapes exist for the policy. **Advisory:** everything is reviewable, nothing is blocked — the desk is a lens, and acceptance is a recorded opinion. **Gated by type:** FEAT / REQ / ADR require acceptance before dispatch; TASK breakdowns under an already-accepted FEAT auto-accept, so day-to-day flow keeps its speed.

Orthogonal to the policy is the mechanism, and there the owner's constraint is fixed (2026-07-26): **no new states, anywhere.** Pending-ness is not note state — the same philosophy as REQ-0018's attention items, which live in the runtime, not in frontmatter.

## Decision

Start advisory, with a stateless-queue mechanism:

- **Queue:** FEAT/TASK proposal sets enter ~review as **dispatch-ledger review requests** (FEAT-0025 runtime); the notes themselves stay at plain `backlog`. ADR, REQ, and TST queue groups are driven by their existing intake states (`proposed`, `draft`, `ready`).
- **Accept:** stamps the existing independent-review convention — `reviewed_by`, `review_date`, `review_verdict` — into each note in the set and clears the ledger request. Durable outcome in the note, transient queue in the runtime (ADR-0009-clean).
- **Reject:** flips the set to the existing `cancelled` status through a statuses.py-guarded transition.
- **Request changes:** a dispatch round-trip back to the originating session (comment + unticked rows), leaving the ledger request open.

Nothing refuses to run for lack of acceptance. The desk records review outcomes per set. After a measurement period (suggested: revisit when ~20 sets have passed through the desk, or at the PHASE-008 close-out — whichever is later), decide gating with data: if review regularly changes plans before implementation, promote to gated-by-type — where the gate predicate is "set has an accepting `review_verdict`", a frontmatter check, never a status check. If it rubber-stamps, stay advisory and say so here.

This mirrors the fleet's best recent lesson (ADR-0006 / upstream ADR-0008): vocabulary and process should follow what the corpus actually does, measured, not what a design wishes it did.

## Alternatives

See frontmatter — introducing `proposed` for features/tasks (rejected: owner preference, no new states; ledger + existing review fields cover both queue and record), gated-by-type from day one, fully gated, and status quo, with rejection reasons.

## Verdict values (recorded from TASK-0207, 2026-07-26)

The desk writes **`plan-accepted`** on acceptance and **`plan-rejected`** on rejection. Neither is close-out's vocabulary (`approved` / `changes-requested`, QUALITY.md), and the write-back endpoint refuses those strings outright, so a plan approval can never read as a verification sign-off.

Refusing the string turned out to be only half the guard. Independent review (2026-07-26) observed that the mechanical close-out check accepts *any* verdict other than `changes-requested`, so a `plan-accepted` stamp landing on a TST or CHG note would silence a gate it never satisfied — and review requests accept arbitrary ids. The endpoint therefore also refuses to stamp **gate-bearing note types** (`test`, `change`) at all: those are reviewed through close-out, not through the desk. Both guards are asserted in [[TST-0021-Review-Desk]].

## Consequences

See frontmatter. The two that need active tracking: the review-field double duty (plan acceptance vs close-out independent review share `reviewed_by`/`review_date`/`review_verdict` — the desk must distinguish by verdict value so a plan-acceptance stamp never satisfies the close-out gate; exact value decided in TASK-0207), and the measurement obligation (the advisory phase is an experiment, not a resting place; TASK-0205 carries the decision, and the revisit is part of PHASE-008's close-out).

## Advisory-phase revisit (PHASE-008 close-out, 2026-07-26)

The ADR set two triggers for revisiting the gate: ~20 proposal sets through the desk, or PHASE-008's close-out, whichever is later. Close-out has arrived first, and the honest reading is that **there is nothing yet to decide with.**

The desk shipped and was accepted on the same day. Its measurable history is one review request — filed by the implementing session to exercise the flow end to end — which was cleared as test residue rather than resolved, because resolving it would have injected a fabricated data point into the exact tally this phase exists to collect. The advisory-phase count is therefore zero, honestly.

That is not a failure of the measurement; it is the measurement working. The trigger stands at ~20 sets and the gating question stays open. What changed at close-out is that the tally is now *visible* — the queue pane renders it, including how many sets changed on review — so the revisit will have evidence when it happens rather than a recollection.

One observation worth keeping for that revisit: the first real use of the desk was a human accepting an ADR through it, which is the *lightest* case (one note, no set, no amendment). The interesting evidence will come from proposal sets that get amended or sent back, and none has occurred yet.


## Gating decision — settled (2026-07-29): stay advisory

**Decided by Edwin, 2026-07-29. The gate is not promoted. Review stays advisory, and this ADR stops carrying a measurement obligation.**

The ADR offered two exits: promote to gated-by-type if review regularly changes plans, or "stay advisory and say so here" if it rubber-stamps. The evidence supports the second exit **for a reason the ADR did not anticipate**, and the distinction is the whole value of writing this down.

It is not that review rubber-stamps. It is that **the flow the gate would govern does not occur.** Three days after the 2026-07-26 revisit the desk's tally stands at one — the [[DES-0002]] design acceptance on 2026-07-28, still the lightest possible case: one note, no set, no amendment. Meanwhile the corpus holds **62 notes carrying a non-empty `review_verdict`** (surfaced by [[TASK-0242]]'s register). Review is not rare here; it is pervasive. It simply happens at a different point in the lifecycle than this gate sits.

- The gate this ADR designed sits **before implementation**, on agent-produced proposal sets entering the queue.
- Review as actually practised happens at **close-out**, per `QUALITY.md`, stamping `reviewed_by`/`review_date`/`review_verdict` into the note once the work exists.

A gate on the first would have governed **1 of 62** review events — the two populations overlap by exactly one, because the single desk interaction is the [[DES-0002]] acceptance and that note carries `review_verdict: "accepted"`, putting it inside the register. (Corrected 2026-07-30; it read "1 of 63" as though the sets were disjoint.) Promoting the gate would not have made planning more reviewed; it would have added a bottleneck to a path nobody walks, while the other 61 reviews continued past it untouched.

Two further caveats, both narrowing the ratio and neither reaching the conclusion. Ten of those verdicts read `CLOSE`, which is not a QUALITY.md value, so the count of *conforming* reviews is nearer 51 than 62. And the windows differ — the verdicts span 11 days, the desk 3 — so the honest rate comparison is roughly 17:1 rather than 62:1. A gate that governs one event in seventeen is still governing a path nobody walks.

That the two mechanisms share the `review_verdict` field is what made this measurable at all — and also what made it invisible for three days. The tally counted desk interactions; the field counted everything. Only rendering both next to each other exposed the gap, which happened by accident: [[ISS-0064]] was filed because `Reviewed · 1` and `Reviewed · 62` appeared a few rows apart and looked like a bug.

### What changes

- **No lifecycle change.** Same outcome as the advisory phase, now by decision rather than by default. Nothing gates on acceptance; `LIFECYCLE.md`, `STATUSES.md` and the upstream template stay untouched, exactly as the advisory phase promised.
- **The tally surface is removed** ([[TASK-0247]]). It was built to inform this decision; the decision is made. It was also the only non-interactive block in a nav pane of clickable rows, which is how Edwin came to ask what it was for.
- **The recording continues.** `ReviewStore.resolve()` still stamps outcomes and `review_queue_payload` still exposes `outcomes`/`reviewed` — that is the ledger's own record of what the desk did, it costs nothing, and it is what a future revisit would read. What is retired is the *obligation to watch it*, not the data.
- **The desk keeps its queue.** Nothing here argues against the surface — proposals, questions and manual test runs all still meet a human there. Only the gate question is closed.

### If this is ever reopened

The trigger would not be "~20 sets" again — that trigger already failed twice by never firing. It would be evidence that pre-implementation proposal review is **being used**: a non-trivial count of sets amended or sent back through the desk. Until that happens, gating a path with no traffic is legislating for a hypothetical, which is the failure [[ADR-0006]] and upstream ADR-0008 were both written about.

### Independent review of the settlement section — 2026-07-30

Reviewed by `model:claude-opus-5` in a fresh session, from the notes and the diff for `bed48ea` alone. **Scope note:** this covers only the `## Gating decision — settled` section added in `bed48ea`, not the original decision. The frontmatter `reviewed_by: "user:edwin"` / `review_date: "2026-07-26"` is deliberately left untouched — it is Edwin's own review of the original decision, it is the stronger provenance, and overwriting it would claim a coverage I do not have. That does mean the ADR's most consequential section postdates its review stamp by three days, and the note should say which review covers which part.

**The decision is upheld. Three figures in it are wrong and are cheap to fix.**

1. **"A gate on the first would have governed 1 of 63 review events" — it is 1 of 62.** The single desk interaction is the [[DES-0002]] acceptance, and `docs/designs/DES-0002-*.md` carries `review_verdict: "accepted"`, so it is *inside* the register's 62 (it is the only `accepted` verdict there; the rest are 51 `approved` and 10 `CLOSE`). The two populations overlap by exactly one. This strengthens the conclusion. "The 62 real reviews continued past it untouched" is likewise wrong by one.
2. **"62 notes carrying a non-empty `review_verdict`" is true, but 10 of them read `review_verdict: CLOSE`**, which is not a value in QUALITY.md's vocabulary (`approved` | `changes-requested`). Pre-existing corpus hygiene rather than anything this change introduced — but by the documented vocabulary the count of real close-out reviews is 52, not 62.
3. **The windows are not comparable and the section presents them as if they were.** All 62 `review_date` values fall in 2026-07-18..2026-07-28 (11 days); [[FEAT-0041]] shipped 2026-07-26, so the desk's window is 3 days. Rate-normalised the gap is roughly 17:1, not 62:1. The conclusion survives with room to spare — the point is that the section's own better sentence ("they count different populations") should carry the argument rather than a raw ratio.

**One durability problem for a settlement described as permanent.** The load-bearing "1" lives in `.cockpit/review-requests.json`, which `.gitignore:32` excludes. I confirmed it locally — one request, `subject: DES-0002`, `status: resolved`, `outcome: accepted`, `resolved_at: 2026-07-28T15:31:03+00:00` — but a future reader weighing whether to reopen this cannot. Transcribe that record into this note so the evidence outlives the untracked file.

**What survived refutation.** The reasoning that neither of the ADR's two exits applied, and that the gate would govern a path with no traffic, is sound and is the right conclusion on this evidence. The code change is clean and guarded in both directions: the surface's absence is asserted in renderer *and* stylesheet (re-adding `.review-tally` rules fails a test), and `test_queue_reports_the_advisory_phase_tally` does still assert the payload, so "the recording survives" is verified rather than aspirational. No `SCHEMA_VERSION` change was needed and none was made.

### The evidence, transcribed (2026-07-30)

The "1" this settlement rests on lives in `.cockpit/review-requests.json`, which `.gitignore` excludes. A permanent decision whose reopen trigger is *a delta from a baseline* cannot rest on a datum a future reader has no way to see — so the baseline is written down here.

The store's entire population as of 2026-07-30:

| field | value |
|---|---|
| `subject` | `DES-0002` |
| `kind` | `review` |
| `status` | `resolved` |
| `outcome` | `accepted` |
| `resolved_at` | `2026-07-28T15:31:03+00:00` |

One request, resolved, accepted. That is the whole desk history at the time of this decision.

Independent review supplied the argument for transcribing it, and it is this ADR's own reasoning turned around: [[TASK-0242]] deliberately sourced the Reviewed register from note frontmatter rather than from this store **because** `_MAX_REQUESTS = 200` trims oldest-first and "a store-sourced register would silently lose its tail". The same store, designed to forget, was left holding the only copy of the number a permanent settlement turns on. Anyone reopening the gate question compares their count against the table above, not against a file that may no longer contain it.
