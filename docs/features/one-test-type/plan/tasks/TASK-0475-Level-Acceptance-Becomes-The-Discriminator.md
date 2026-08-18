---
type: "[[task]]"
id: TASK-0475
aliases: ["TASK-0475"]
title: "`level: acceptance` becomes the discriminator across TAXONOMY, TESTING and QUALITY"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"]
parent: "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"
effort: S
depends: ["[[TASK-0474-The-Test-Schema-Absorbs-The-Check-Fields]]"]
blocks: []
related: []
tests: []
---

# `level: acceptance` becomes the discriminator

The field already exists — TAXONOMY.md has carried `level: acceptance` since the template was written, described as *"user-level acceptance checks that gate releases"*. Nothing new is invented; the axis that was always there starts carrying the distinction.

Three instruction files change:

- **TAXONOMY.md** — `mark` moves from the check type to tests at `level: acceptance`.
- **TESTING.md** — lines 126–127 rewritten. They currently say an acceptance check *"is **not** a `TST-*` note"* and that `level: acceptance` on a test is *"a third, different thing"*. Both sentences become one: an acceptance check is a test at that level, manual or automated.
- **QUALITY.md** — the review gate states what it keys on, which is where [[ISS-0196-The-Review-Gate-Is-Described-Two-Ways]] gets settled rather than carried forward.

Done when: no template-owned document describes the check as a separate type, and TESTING.md's Tier 2 → Tier 3 → retire path is written against the merged type.
