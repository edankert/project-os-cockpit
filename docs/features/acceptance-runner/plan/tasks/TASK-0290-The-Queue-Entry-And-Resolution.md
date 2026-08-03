---
type: "[[task]]"
id: TASK-0290
aliases: ["TASK-0290"]
title: "The awaiting-acceptance queue entry resolves through the run"
status: backlog
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: S
depends: ["[[TASK-0289]]"]
blocks: []
related: []
tests: []
---

# The awaiting-acceptance queue entry resolves through the run

## Definition of Done

- `Awaiting your acceptance` rows open the runner; a completed run resolves the entry via review-resolve with the run summary as outcome.
- An abandoned run leaves the entry open and the partial run resumable — never silently resolved.
