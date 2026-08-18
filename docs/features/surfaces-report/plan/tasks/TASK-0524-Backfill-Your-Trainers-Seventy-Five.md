---
type: "[[task]]"
id: TASK-0524
aliases: ["TASK-0524"]
title: "Backfill or except the 75 your-trainer features with no acceptance check"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Backfill or except the 75 your-trainer features with no acceptance check

Measured 2026-08-18: 102 features, 75 with nothing in any check's `covers:`. That is what eighteen months of a manual ask produced — 27% coverage — and it is the evidence for REQ-0051.

Do it AFTER the surfaces exist (FEAT-0130): a backfilled check needs a surface to sit on, and minting 75 more free-text areas is the problem this phase is fixing.
