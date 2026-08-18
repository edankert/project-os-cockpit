---
type: "[[test]]"
id: TST-0077
aliases: ["TST-0077", "CHK-0034"]
title: "Decisions survive a nav-mode change"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "The record column has its own source"
section: "2.7"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[ISS-0065]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.7.1 @ 7de1a86"
related: []
level: acceptance
kind: manual
merged_from: "CHK-0034 @ 4c02731"
---

# Decisions survive a nav-mode change

expect the overview's Decisions card to list every ADR, sourced from its own endpoint rather than harvested from a navigator that a later change can empty. — 2026-08-10, **rendered** after switching modes four times: the record column shows `Decisions 10/11 accepted`, `Verification 23/23` and `Reviewed 104` — the last being [[TASK-0377]]'s re-homed register in its new place.
