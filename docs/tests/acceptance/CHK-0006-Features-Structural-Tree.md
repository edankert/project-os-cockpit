---
type: "[[check]]"
id: CHK-0006
aliases: ["CHK-0006"]
title: "Features is the structural tree"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The navigator"
section: "1.3"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0010]]", "[[FEAT-0046]]", "[[FEAT-0058]]", "[[FEAT-0085]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.3.1 @ 7de1a86"
related: []
---

# Features is the structural tree

open Features. Expect: phase → feature → its requirements, then its plan, then its tasks; finished groups collapsed beneath the live ones. — 2026-08-11, **rendered**, live harness against a current sidecar: `OPEN · 3` (PHASE-028/029/999, expanded) above `COMPLETED · 86 FEATURES` (collapsed). FEAT-0083 expands to `REQ-0032` then `TASK-0361..0363`; FEAT-0079 to `PLAN` then `TASK-0338/0339` — requirements, then plan, then tasks, on two features that between them carry both. (user:edwin, 2026-08-11)
