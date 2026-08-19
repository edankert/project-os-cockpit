---
type: "[[test]]"
id: TST-0077
aliases: ["TST-0077"]
title: "Decisions survive a nav-mode change"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "The record column has its own source"
covers: ["[[ISS-0065]]"]
related: []
level: acceptance
---

# Decisions survive a nav-mode change

expect the overview's Decisions card to list every ADR, sourced from its own endpoint rather than harvested from a navigator that a later change can empty. — 2026-08-10, **rendered** after switching modes four times: the record column shows `Decisions 10/11 accepted`, `Verification 23/23` and `Reviewed 104` — the last being [[TASK-0377]]'s re-homed register in its new place.
