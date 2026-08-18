---
type: "[[feature]]"
id: FEAT-0075
aliases: ["FEAT-0075"]
title: "The delegation policy — a principal-approved note the actuators consult, delegate writes that carry their authority, and the push decision taken as an ADR"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0009-The-Standing-Worker]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
goal: "DELEGATION.md as the per-repo record of what is delegated and what escalates, approved through the actuator row it configures; the actions endpoint answering per caller identity; every delegate write stamped with its authority; and publishing under autonomy decided, not eroded."
requirements: ["[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]", "[[REQ-0030-The-Worker-Never-Outruns-Its-Policy]]"]
tasks:
  - "[[TASK-0326-The-Policy-Note]]"
  - "[[TASK-0327-Role-Checks-Consult-Policy]]"
  - "[[TASK-0328-The-Push-Decision]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: []

---

# The delegation policy

## Goal

ADR-0009 §4 made the delegation "a per-repo recorded fact"; this feature is that fact's format and its enforcement. The policy passes through the gate it configures — the principal approves DELEGATION.md via the actuator row — and its absence means what it should: **no delegation, no worker.**

## Out of Scope

- Fleet-default policies. Each repo's principal signs each repo's policy; inheritance is a later convenience with its own risks.
- Any delegation of publishing — that is TASK-0328's ADR to decide, explicitly.

## Acceptance

- [x] The policy has a format, and a template that ships delegating **nothing** ([[TASK-0326]])
- [x] **No policy → no delegation → no worker** — every path returns False unless something explicitly says yes
- [x] A **draft** policy is no policy; an unreadable status is treated as unapproved, because guessing permissively is the one affordable-nowhere mistake
- [x] An HTML-commented example is not a grant — the template would otherwise have delegated everything **on install**
- [x] [[REQ-0030]]'s first layer: a delegate is offered only what the policy names ([[TASK-0327]])
- [x] Delegate writes carry `(agent:principal, delegation: DELEGATION.md@<sha>)` — who, under what authority, as the policy stood when
- [~] The push ADR — **reconciled to [[TASK-0328]]**, which is its own deliverable: [[ADR-0009]] named pushing so it could not relax as a side effect, and that ADR is where it may relax *as a decision*

## Verification

`tests/test_delegation.py` — 14 tests, most of them spent on the paths where a permissive default would hide.

The template test **failed on its first run**, which is the best evidence the module is shaped correctly: the parser skipped code fences but not HTML comments, so the shipped default would have delegated `everything → any-delegate` through the one file every repo copies.
