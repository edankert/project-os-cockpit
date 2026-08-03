---
type: "[[adr]]"
id: ADR-0009
aliases: ["ADR-0009"]
title: "The principal is a role, not a person — autonomy is delegation of that role, never the weakening of its gates"
status: "accepted"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-03"
source: ["Edwin 2026-08-03: 'I am contemplating allowing an LLM to do full maintenance and work on a project independently of a human, make sure the current solution we are implementing does not stop us from enabling this'"]
related: ["[[PHASE-023-Levers-For-The-Human]]", "[[PHASE-024-Acceptance-Witnessed]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[REQ-0028-Evidence-Names-Its-Witness]]", "[[DES-0005-The-Actuator-Grammar]]"]
reviewed_by: "user:edwin"
review_date: "2026-08-03"
review_verdict: "plan-accepted"
---

# The principal is a role

## Context

PHASE-023/024 are written in the language of "the human": human-owned transitions, a human witness, an acceptance gate only the asker can satisfy. Edwin is now contemplating **fully autonomous operation** — an LLM maintaining a project with no human in the daily loop. Do the phases as planned foreclose that?

Audited against every gate in the plan, the answer is no — *provided one word is fixed now, before implementation hard-codes it.* The ownership table's "user" column, REQ-0026's "human-owned", REQ-0028's witness: in every case the load-bearing property is not humanity. It is **being the party that holds the intent** — the asker, whose judgment questions like "is this what I asked for?" are addressed to. STATUSES.md's split is really *worker* vs *principal*; ADR-0013 already established the analogous point for review (independence is clean context, not model family).

## Decision

1. **"User" in the ownership table, "human" in PHASE-023/024, and every witness field mean the principal** — the party holding the project's intent. Today, and until a further decision, the principal of every fleet repo is `user:edwin`.
2. **Autonomy is achieved by delegating the principal role** — to an agent session that is (a) distinct from the worker whose output it judges, (b) clean-context per ADR-0013's standard, and (c) bound to a durable intent artifact it judges against (the DES-0003 intent page is the natural charter). It is **never** achieved by skipping gates, softening witness requirements, or letting a worker stamp its own acceptance.
3. **Implementation consequences, binding on PHASE-023/024**: witness and `accepted_by` values are principal identifiers (`user:…` or, later, `agent:…` under a recorded delegation); the actuator endpoints check *role policy*, not species; nothing may compare against the literal `user:edwin` or assume a keyboard.
4. **The delegation itself, when it comes, is a per-repo recorded fact** — a policy note naming what is delegated (triage to severity ≤ medium, REQ approval, acceptance) and what escalates. Writing that policy mechanism is future work, deliberately not smuggled into these phases.

## Consequences

- The four planned phases build the *supervision surface* autonomy needs — the digest, the debt card, the desk queue — which serve a human principal as gates today and an auditing human as instruments under delegation tomorrow. Nothing gets thrown away in the transition.
- The one hard human step remaining in daily operation is **pushing** (FEAT-0055: a person clicks, deploy remotes refused). Under full autonomy that either stays (a human publishes on their own cadence) or is revisited as its own decision under this frame — it is named here so it cannot be relaxed as a side effect.
- REQ-0026 and REQ-0028 are read under this ADR without amendment: "human-owned" = principal-owned; "an agent cannot be a witness" = *the worker* cannot witness its own work, and no agent can without a recorded delegation.
