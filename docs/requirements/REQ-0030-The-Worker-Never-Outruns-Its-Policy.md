---
type: "[[requirement]]"
id: REQ-0030
aliases: ["REQ-0030"]
title: "The worker never outruns its policy"
status: "approved"
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
