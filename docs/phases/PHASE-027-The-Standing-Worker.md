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
- [ ] Every autonomous transition traces to a delegation entry — evidence: <the audit query returning zero orphans>
- [ ] An unanswered question cannot stall the loop silently: it proceeds on a recorded assumption or alarms — evidence: <both paths exercised>
- [ ] The worker halts on each stop condition in a drill, not just in theory — evidence: <the drill log>
- [ ] Publishing under autonomy has a decision, not a habit — evidence: <the push ADR's id and status>
