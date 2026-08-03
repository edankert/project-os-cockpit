---
type: "[[task]]"
id: TASK-0328
aliases: ["TASK-0328"]
title: "The push decision — publishing under autonomy taken as an ADR, not eroded by convenience"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0075-The-Delegation-Policy]]"]
parent: "[[FEAT-0075-The-Delegation-Policy]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The push decision

## Definition of Done

- An ADR weighs: the human publishes on cadence (status quo, FEAT-0055's line) / a scoped delegation for non-deploy remotes only / full delegation with the deploy-refusal untouchable. It arrives `proposed` for the principal.
- ADR-0009 named pushing so it could not relax as a side effect; this ADR is where it may relax **as a decision** — the distinction is the deliverable.
- Until accepted, the worker's relationship to `git push` is: never.
