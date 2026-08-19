---
type: "[[test]]"
id: TST-0075
aliases: ["TST-0075"]
title: "`changes-requested` on finished work reads settled"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "A settled verdict is not owed"
covers: ["[[ISS-0121]]"]
related: []
level: acceptance
---

# `changes-requested` on finished work reads settled

expect a note carrying `review_verdict: changes-requested` whose status is terminal to appear as settled, not as owed. (All ten rows the desk headed *Changes requested* were terminal; the real count was zero.) — 2026-08-10, `GET /api/cockpit/reviewed`: **104 verdicts, 0 owed**.
