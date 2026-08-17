---
type: "[[check]]"
id: CHK-0032
aliases: ["CHK-0032"]
title: "`changes-requested` on finished work reads settled"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "A settled verdict is not owed"
section: "2.5"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[ISS-0121]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.5.1 @ 7de1a86"
related: []
---

# `changes-requested` on finished work reads settled

expect a note carrying `review_verdict: changes-requested` whose status is terminal to appear as settled, not as owed. (All ten rows the desk headed *Changes requested* were terminal; the real count was zero.) — 2026-08-10, `GET /api/cockpit/reviewed`: **104 verdicts, 0 owed**.
