---
type: "[[task]]"
id: TASK-0321
aliases: ["TASK-0321"]
title: "Mode 1 decided once, with the drift record as evidence"
status: backlog
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0073-One-Voice]]"]
parent: "[[FEAT-0073-One-Voice]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Mode 1 decided once, with the drift record as evidence

## Definition of Done

- An ADR weighs mode 1's audience (the tablet read case) against its cost (three twin-drifts in two days, every UI change doubled); it retires, funds, scopes, or **shares the contract** — and the decision arrives `proposed` for the actuator row.
- **The fourth option is new, and it is evidence rather than opinion** (t3.codes comparison, 2026-08-05): T3 serves **three** client surfaces — web, Electron desktop, React Native mobile — from one shared typed schema package, and does not suffer vocabulary drift. The cockpit has **two** surfaces, no shared schema, and drifted three times in two days. The ADR must address this directly: the drift is not evidence that two surfaces are unaffordable, it is evidence that two *hand-written* surfaces are.
