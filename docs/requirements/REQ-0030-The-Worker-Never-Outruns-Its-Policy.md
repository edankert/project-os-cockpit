---
type: "[[requirement]]"
id: REQ-0030
aliases: ["REQ-0030"]
title: "The worker never outruns its policy"
status: "implemented"
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-11"
source: ["[[ADR-0009-The-Principal-Is-A-Role]]"]
priority: high
scope: "The driver, the actuator endpoints under a delegate identity, and every escalation default"
specifies: ["[[FEAT-0074-The-Standing-Worker]]", "[[FEAT-0075-The-Delegation-Policy]]"]
acceptance:
  - "No approved DELEGATION.md → no worker, no delegate actions, no defaults — the unconfigured repo is exactly as manual as today"
  - "An action outside the approved policy is refused server-side with the policy line named, regardless of what any caller requests"
  - "Everything a lapsed timeout authorises traces to an escalate: line; kinds without one wait and alarm"
  - "The refusals are exercised by the hardening suite — no policy, draft policy, outside-threshold, reserved-kind — each by attempting the forbidden thing"
---

# The worker never outruns its policy

REQ-0026 for the autonomous case: the gate is the server's, the policy is the principal's, and the worker's ambition is bounded by what was actually signed.

## Acceptance Criteria

- [x] No approved DELEGATION.md → no worker, no delegate actions, no defaults — the unconfigured repo is exactly as manual as today — evidence: `delegation.load` returns `approved: False` for absent, unreadable **and** draft policies; `worker.can_start` halts with `no-delegation`; `legal_actions` offers a delegate nothing. Three tests, one for each surface (user:edwin, 2026-08-11)
- [x] An action outside the approved policy is refused server-side with the policy line named, regardless of what any caller requests — evidence: `permits()` returns False unless a delegation names the judgment *and* the actor; there is no wildcard, no prefix match and no branch that grants on absence (user:edwin, 2026-08-11)
- [x] Everything a lapsed timeout authorises traces to an escalate: line; kinds without one wait and alarm — evidence: `escalation.assess` lapses only where `DEFAULT_POLICY` supplies a `default`; an unknown kind **alarms** (`test_a_kind_with_no_policy_alarms_rather_than_passing`), and `permission` deliberately has no default at all (user:edwin, 2026-08-11)
- [x] The refusals are exercised by the hardening suite — no policy, draft policy, outside-threshold, reserved-kind — each by attempting the forbidden thing — evidence: `tests/test_delegation.py` (14) attempts each refusal rather than asserting a flag; the template case **failed on its first run**, catching a parser that would have delegated everything on install (user:edwin, 2026-08-11)
