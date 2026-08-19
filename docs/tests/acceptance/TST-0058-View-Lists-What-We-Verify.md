---
type: "[[test]]"
id: TST-0058
aliases: ["TST-0058", "CHK-0015"]
title: "The view lists what we verify"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Tests"
section: "1.7"
ordinal: 10
covers: ["[[FEAT-0086]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.7.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0015 @ 4c02731"
---

# The view lists what we verify

open Tests. Expect: every `TST-*` in the corpus, grouped by state, each row naming the feature it verifies; both `docs/tests/` and `plan/tests/` present with no sign of the split. — 2026-08-10, **rendered**, via `desktop/harness/live-harness.html` against a current sidecar: four groups — `Tier 1 · 8/27`, `Tier 2 · 3/7`, `Tier 3 · 0/2`, `Verified · 23`. The tier groups sort above `Verified` because they hold unchecked items and it does not, which is the settled-group rule working.
