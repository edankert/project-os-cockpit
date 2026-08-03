---
type: "[[task]]"
id: TASK-0312
aliases: ["TASK-0312"]
title: "The watermark, and the Caught-up that moves it"
status: backlog
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0071-Since-You-Looked]]"]
parent: "[[FEAT-0071-Since-You-Looked]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The watermark, and the Caught-up that moves it

## Definition of Done

- `.cockpit/last-seen.json` per workspace; GET/POST endpoints; only the explicit `Caught up` action moves it — opening the app never does.
- Missing watermark reads as epoch: the first digest shows everything, honestly.
