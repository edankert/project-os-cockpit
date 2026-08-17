---
type: "[[check]]"
id: CHK-0013
aliases: ["CHK-0013"]
title: "The brief opens first"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Design and the constraints view"
section: "1.6"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0042]]", "[[FEAT-0043]]", "[[FEAT-0044]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.6.1 @ 7de1a86"
related: []
---

# The brief opens first

open Intent (`~design`, the view Design was renamed to). Expect: the project's own brief, not a file list. — 2026-08-11, **rendered**: the pane opens on `project-os-cockpit` and its four questions — *where is this project now / what is an agent doing / what needs my decision / what should this look like* — with `Read the full brief` beneath, and the design register only after it. Nav carries `WHAT THIS PROJECT IS · 8`, `DESIGNS 10 · 3 DONE`, `DECISIONS 13`. Clicking `README` in the standing set opens `docs/README.md` — [[ISS-0135]]'s fix confirmed by hand, the row that used to go nowhere. (user:edwin, 2026-08-11)
