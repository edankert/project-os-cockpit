---
type: "[[check]]"
id: CHK-0028
aliases: ["CHK-0028"]
title: "Every plan on disk is reachable"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "Plans are visible"
section: "2.1"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[ISS-0062]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.1.1 @ 7de1a86"
related: []
---

# Every plan on disk is reachable

count `docs/features/*/plan/PLAN.md` on disk and find each one in the Features tree, including the three with no frontmatter. Expect: equal counts. (19 of 33 were invisible when this was filed, because the lookup used the note *type* and most plans do not declare one.) — 2026-08-10: **71 on disk, 71 reachable** in the `features` payload.
