---
type: "[[test]]"
id: TST-0075
aliases: ["TST-0075", "CHK-0032"]
title: "`changes-requested` on finished work reads settled"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "A settled verdict is not owed"
section: "2.5"
ordinal: 10
covers: ["[[ISS-0121]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.5.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0032 @ 4c02731"
---

# `changes-requested` on finished work reads settled

expect a note carrying `review_verdict: changes-requested` whose status is terminal to appear as settled, not as owed. (All ten rows the desk headed *Changes requested* were terminal; the real count was zero.) — 2026-08-10, `GET /api/cockpit/reviewed`: **104 verdicts, 0 owed**.
