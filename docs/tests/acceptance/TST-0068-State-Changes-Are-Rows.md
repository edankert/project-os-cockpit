---
type: "[[test]]"
id: TST-0068
aliases: ["TST-0068", "CHK-0025"]
title: "State changes are the rows"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "History"
section: "1.12"
ordinal: 10
mark: done
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0052]]", "[[FEAT-0053]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.12.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0025 @ 4c02731"
---

# State changes are the rows

open History. Expect: status transitions as rows with commits as dividers, and the contribution grid clicking through to a day. — 2026-08-11, **rendered**: `History — what changed state, and which commit carried it`, with `08-11 94bf4ee` as a divider over `DES-0009 proposed → "accepted"` and `PHASE-027 planned → done` — this session's own commit, read back off the surface. Clicking the grid's 2026-08-09 cell (`24 state changes, 3 commits`) routes to `~history/2026-08-09` and the header becomes *what changed state on or before 2026-08-09*. (user:edwin, 2026-08-11)
