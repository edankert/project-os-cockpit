---
type: "[[test]]"
id: TST-0070
aliases: ["TST-0070", "CHK-0027"]
title: "The badges cover everything owed"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Obligations"
section: "1.14"
ordinal: 10
covers: ["[[FEAT-0089]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.14.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0027 @ 4c02731"
---

# The badges cover everything owed

expect a count on each view button, the sum equal to the registry's total, and no badge at all where nothing is owed. — 2026-08-10, **rendered**: the buttons carry `overview 81 · design 3 · features 4 · issues 7` — sum **95**, the registry's total — and the Tests button, owed nothing, carries no badge at all.
