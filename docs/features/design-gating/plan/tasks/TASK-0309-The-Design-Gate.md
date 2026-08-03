---
type: "[[task]]"
id: TASK-0309
aliases: ["TASK-0309"]
title: "design: on features, and the DESIGN-GATE warning"
status: backlog
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0070-Design-Gating-And-Scaffolding]]"]
parent: "[[FEAT-0070-Design-Gating-And-Scaffolding]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# design: on features, and the DESIGN-GATE warning

## Definition of Done

- Optional `design:` frontmatter on features; local validator warning while the named design is unaccepted and the feature leaves the pending band.
- Warning first per ADR-0011's path; the escalation decision is deferred until lived with.
