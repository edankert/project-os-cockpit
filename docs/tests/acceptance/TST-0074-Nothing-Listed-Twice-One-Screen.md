---
type: "[[test]]"
id: TST-0074
aliases: ["TST-0074", "CHK-0031"]
title: "Nothing is listed twice on one screen"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "One home per obligation"
section: "2.4"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[ISS-0068]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.4.1 @ 7de1a86"
related: []
level: acceptance
kind: manual
merged_from: "CHK-0031 @ 4c02731"
---

# Nothing is listed twice on one screen

expect no item to appear both in a triage tray and a severity card, both in a badge count and a second list, or both in a group and a roll-up of the same group. — 2026-08-11, **rendered**, Issues view with **every group expanded and every fold opened first**, so nothing was hidden rather than absent: **20 rows, 20 distinct issues, no ID twice.** The two populations are disjoint by construction — `Needs triage · 9 · triage` holds the triage items and the severity cards (`Critical 1 · fixed`, `High 23`, `Medium 80 + 1 open`, `Low 24`) hold only `open`/`fixed`. The Issues badge reads **9**, the same 9 the tray lists, and there is no second list of them. *One apparent duplicate was checked and is not one: `ADR-0013` appears in two rows because [[ISS-0123]] and [[ISS-0053]] both name it in their titles — two issues, not one issue twice.* (user:edwin, 2026-08-11)
