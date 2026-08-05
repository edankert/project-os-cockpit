---
type: "[[phase]]"
id: PHASE-028
aliases: ["PHASE-028"]
title: "Borrowed capability — the cockpit takes what adjacent agent harnesses have already proven, and keeps looking"
status: active
order: 28
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
goal: "Adopt proven capability from adjacent tools rather than inventing it, and keep a standing survey of what else is worth taking — so the cockpit's effort goes into the governance thesis nobody else is building."
features:
  - "[[FEAT-0079-Supervision-From-A-Phone]]"
  - "[[FEAT-0080-The-Harness-Survey]]"
requirements: []
issues: []
depends: ["[[PHASE-023-Levers-For-The-Human]]", "[[PHASE-026-The-Returning-Human]]"]
related: ["[[PHASE-027-The-Standing-Worker]]", "[[RISK-0005-The-Write-Surface]]"]
tags: [external, remote, survey]
---

# Borrowed capability

## Where this came from

The 2026-08-05 comparison against [t3.codes](https://github.com/pingdotgg/t3code) — 1,100 source files, 2,259 test files, five coding agents behind one driver interface, three client surfaces. It has **no** requirements, acceptance criteria, phases or validator: its own `AGENTS.md` describes an *"agent harness control surface"*, and it holds no opinion about what should be built or whether it was right.

That is the whole finding. The two tools are orthogonal, so the comparison is worth having **not** as a feature list to chase but as a map of what is already solved elsewhere. Every hour spent reinventing a harness is an hour not spent on the governance layer nobody else is building.

## Why this is a standing phase

A survey has no natural exit, so it fails the phase test in `CLAUDE.md` — its criteria would be "the tasks are done". But each round produces adoptions that need a home, and minting a phase per round is exactly what [[ISS-0077]] forbade. So this is a **standing phase**: `done` when idle, reopened when a survey round or an adoption arrives.

## Scope

[[FEAT-0079]] — the first adoption: supervision from a phone, which autonomy makes valuable and which [[RISK-0005]] makes delicate. [[FEAT-0080]] — the survey itself: a repeatable pass over adjacent tools whose output is filed issues, not prose.

## Out of Scope

- **Becoming a harness.** Multi-forge source control, an editor, a conversation UI: T3 does these well and the cockpit should not.
- **Adopting architecture.** T3's Effect-TS event-sourced orchestration suits 1,100 files; importing it into a 16k-line Python tool is the *"machinery because it looks architecturally impressive"* its own AGENTS.md warns against.
- **Anything already filed elsewhere.** The survey's other findings live where they belong — [[ISS-0094]], [[ISS-0095]], [[ISS-0096]], [[FEAT-0078]] — not here.

## Exit Criteria

- [ ] The cockpit can be supervised from a phone without widening what [[RISK-0005]] forbids — evidence: <the authenticated path, and the risk's re-scan>
- [ ] A survey round produces filed issues with a recorded verdict each, including the explicit declines — evidence: <the round's note>
- [ ] Declining to adopt is as recorded as adopting — evidence: <the not-taken list>
