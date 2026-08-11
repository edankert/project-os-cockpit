---
type: "[[phase]]"
id: PHASE-027
aliases: ["PHASE-027"]
title: "The standing worker — a project runs without its human in the daily loop: work selected and closed by a worker, judgments delegated under recorded policy, exceptions that escalate instead of stall"
status: planned
order: 27
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
goal: "Make ADR-0009 operational: a driver that selects, works and closes; a delegation policy the actuator endpoints consult; escalation defaults so no unanswered question stalls the loop; and an intent charter the delegated principal judges against."
features:
  - "[[FEAT-0074-The-Standing-Worker]]"
  - "[[FEAT-0075-The-Delegation-Policy]]"
  - "[[FEAT-0076-Escalation-With-Defaults]]"
  - "[[FEAT-0077-The-Intent-Charter]]"
requirements:
  - "[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]"
  - "[[REQ-0030-The-Worker-Never-Outruns-Its-Policy]]"
  - "[[REQ-0031-The-Loop-Always-Halts]]"
issues: []
depends: ["[[PHASE-023-Levers-For-The-Human]]", "[[PHASE-024-Acceptance-Witnessed]]"]
related: ["[[ADR-0009-The-Principal-Is-A-Role]]", "[[DES-0009-The-Standing-Worker]]", "[[RISK-0006-The-Unattended-Worker]]"]
tags: [autonomy, agents, governance]
---

# The standing worker

## Where this came from

Edwin, 2026-08-03: *"I am contemplating allowing an LLM to do full maintenance and work on a project independently of a human."* [[ADR-0009]] (accepted same day) settled the frame — the principal is a role, autonomy is delegation of that role under recorded policy, never the weakening of gates. This phase builds the four things the audit found missing between that frame and a project that actually runs unattended.

## What the docs contract already provides

LIFECYCLE step 2 already instructs an unassigned agent to *select work based on focus and item statuses* — self-selection is contractual, not novel. The shell already spawns, instruments and tracks sessions. The desk queue already is the exception channel. PHASE-023 gives judgments their endpoints; PHASE-024 gives acceptance its runner. This phase is the loop around all of it, plus the two genuinely new artifacts: the **delegation policy** and the **intent charter**.

## Scope

[[FEAT-0074]] — the driver: pick, work, close, next; the focus lease; stop conditions. [[FEAT-0075]] — the policy note the role checks consult, and the push decision taken as an ADR rather than eroded. [[FEAT-0076]] — per-kind escalation timeouts and proceed-on-recorded-assumption, so the loop degrades gracefully instead of stalling silently. [[FEAT-0077]] — the charter: DES-0003's intent page graduated into the oracle a delegated acceptance judges against.

Design: [[DES-0009]].

## Out of Scope

- **Weakening any gate.** ADR-0009 §2 is the boundary condition of the whole phase; a shortcut here invalidates it.
- **Autonomous pushing.** The push decision is *authored* here ([[TASK-0328]]) and takes effect only as that ADR decides.
- **Multi-repo orchestration.** One repo, one worker first; the fleet loop is its own phase once one repo has run clean for weeks.
- **Model-quality problems.** The phase makes bad judgment *visible and bounded*; making judgment good is not a feature.

## Exit Criteria

- [ ] A repo runs a week of maintenance with the human touching only the digest and the desk — evidence: <the week's ledger, and what the digest showed>
- [~] Every autonomous transition traces to a delegation entry — **reconciled: enforced by construction, unauditable by data.** No autonomous transition has occurred, so the audit query returns zero orphans **vacuously**, and ticking on a vacuous pass is the kind of green this release exists to refuse. What *is* proven: a delegate write that cannot name its charter and delegation is **refused at the write path** ([[REQ-0029]], `test_a_bare_agent_witness_is_refused`), so an untraceable autonomous transition cannot be recorded in the first place. The query becomes meaningful during [[RISK-0006]]'s supervised week (user:edwin, 2026-08-11)
- [x] An unanswered question cannot stall the loop silently: it proceeds on a recorded assumption or alarms — evidence: both paths exercised in `tests/test_escalation.py` (13). A kind with a `default` **lapses carrying its assumption**; a kind with none, or an unknown kind, **alarms** — and `test_the_drill_no_entry_waits_silently` enumerates every silent-wait shape rather than sampling. `permission` was added to the clock by [[ISS-0094]], closing the one way an unattended worker most likely stops (user:edwin, 2026-08-11)
- [x] The worker halts on each stop condition in a drill, not just in theory — evidence: six halt paths, each with its own drill in `tests/test_worker.py` (32) — stop-switch, no-delegation, validator-red, parked-items, session-budget, wall-clock. Written **before** the loop that needs them, which is [[REQ-0031]]'s own order: *brakes are tested before the hill*. `test_every_halt_carries_a_reason` sweeps them, because a halt with no reason is indistinguishable from a worker that went quiet (user:edwin, 2026-08-11)
- [x] Publishing under autonomy has a decision, not a habit — evidence: [[ADR-0022]], `proposed`. It weighs all three options and proposes keeping the status quo, on the ground that no delegate has yet made a single autonomous judgment here. **Until it is accepted the worker's relationship to `git push` is: never** — which is the operative rule, not a placeholder (user:edwin, 2026-08-11)

## Why this phase is `planned` and not `done` — 2026-08-11

Every feature is `done`, every task is resolved, all three requirements are `implemented`, and four of five exit criteria are settled. **One criterion is left standing, deliberately, and it is not an oversight:**

> A repo runs a week of maintenance with the human touching only the digest and the desk

It has not happened. No worker has executed a single turn — `run_once` refuses without an approved `DELEGATION.md` and this repo has none.

**It is left `[ ]` rather than reconciled**, and the distinction is the point. `STATUSES.md` offers `- [~]` for a criterion that was **cut** — departed from, with the reason. This one was not cut; it is *not yet done*. Marking it reconciled would record a decision nobody made, and the difference between *"we chose not to"* and *"we haven't"* is exactly the kind of thing a record exists to keep straight.

The same reasoning holds [[RISK-0006]] open. Its own text: *"closes when a repo has run a supervised week — worker on, human watching daily — with the drill log green and the audit query returning zero orphans. **Unattended operation before that standard is the risk realised, not accepted.**"* Closing it now would put a false statement in the record about whether a machine making judgments unattended is safe — assessed by a machine, unattended.

[[DES-0009]] is `proposed` with its artifact and waits on an Accept, which `HUMAN_TRANSITIONS` reserves for the principal and the server refuses to an agent.

**What the phase delivered**, so the remaining gap is not mistaken for a hole in the work: the delegation policy defaulting closed, the escalation clock with nothing waiting silently, permission prompts brought under it, turn checkpoints with a principal-owned restore, a picker that records what it passed over, six drilled halt paths, and a session loop that spawns nothing of its own. Every mechanism the supervised week needs exists and is tested. What is missing is the week.
