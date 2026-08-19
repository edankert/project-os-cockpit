---
type: "[[test]]"
id: TST-0067
aliases: ["TST-0067", "CHK-0024"]
title: "Fleet roll-up"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Verification health and the fleet"
section: "1.11"
ordinal: 20
covers: ["[[FEAT-0018]]", "[[FEAT-0028]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.11.2 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0024 @ 4c02731"
---

# Fleet roll-up

expect a validator badge per discovered repo, and a push action that refuses a deploy remote. — 2026-08-10: 10 of 10 rail entries carry a validator verdict; `your-applications.com` is labelled `remote is a deploy target`. *The refusal itself was read from the label, not exercised — pushing is deliberately a person's action.*
