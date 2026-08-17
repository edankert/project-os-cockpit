---
type: "[[check]]"
id: CHK-0012
aliases: ["CHK-0012"]
title: "Changes read on the overview"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The overview"
section: "1.5"
ordinal: 20
mark: "/"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0017]]", "[[FEAT-0023]]", "[[FEAT-0040]]", "[[FEAT-0048]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.5.2 @ 7de1a86"
related: []
---

# Changes read on the overview

recent change notes in the history band, older ones collapsed by month and still openable — **cut: the surface it describes was retired by decision before this suite was written.** [[FEAT-0052]] (`2eec1a4`, 2026-07-30) replaced the Activity, Changes and Commits tiles with one History band, on the stated ground that *"the overview had three history tiles answering one question three ways."* This check was authored on 2026-08-10 — **eleven days later** — describing a tile that had already gone, which is what happens when a checklist is written from the record rather than from the screen. What the History band does render is verified under 1.12.1. The orphaned `fillChanges` and its still-served `/api/cockpit/changes` are filed as [[ISS-0139]]; the archive coming back would be a new check, not this one. (user:edwin, 2026-08-11)
