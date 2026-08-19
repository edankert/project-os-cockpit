---
type: "[[test]]"
id: TST-0054
aliases: ["TST-0054", "CHK-0011"]
title: "Every stat tile lands somewhere true"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The overview"
section: "1.5"
ordinal: 10
covers: ["[[FEAT-0017]]", "[[FEAT-0023]]", "[[FEAT-0040]]", "[[FEAT-0048]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.5.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0011 @ 4c02731"
---

# Every stat tile lands somewhere true

click each of Features, Tasks, Tests, Issues, Risks. Expect: each opens a view that contains that type. (Reqs is inert by decision.) — 2026-08-10, **rendered**: all five are `<button>`, Reqs is a `<div>` — the inertness is by construction, not by a missing handler. Destinations are asserted against the live corpus by `test_every_stat_tile_lands_where_its_type_lives`, and Risks was confirmed in the constraints view by eye (`Risks · 6 · open`).
