---
type: "[[task]]"
id: TASK-0384
aliases: ["TASK-0384"]
title: "Propose the manifest, the status removal and the freshness check upstream — 82 of the 90 documents are in other repos"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]"]
parent: "[[FEAT-0091-The-Standing-Documents]]"
effort: S
due: ""
depends: ["[[TASK-0381-Statuses-Out-Checks-In]]"]
blocks: []
related: []
tests: []
---

# Propose the manifest upstream

## Definition of Done
- [ ] The manifest shape, the status removal and the three checks are proposed to `~/Dev/repos/project-os/`
- [ ] The proposal carries the fleet measurement, not just the design
- [ ] The two-layer split (template base, project extension) is stated as a requirement of the sync, not a preference
- [ ] `yourtrainer-mcp`'s five missing documents are named as the case the presence check is for

## Steps
- [ ] Write it against upstream's own conventions; the base set and the validator logic are both template-owned
- [ ] Include the before number so the after is measurable
- [ ] Flag the `sync-project-os.sh` interaction explicitly

## Notes
This repo holds **8 of 90** standing documents in the fleet. Fixing only these leaves 82 stale in eleven other repos, and the validator logic that would report them is template-owned — so a local-only fix is both the smaller win and the one that drifts at the next sync.

The measurement is the argument: 90 present, 85 stale or undated, 12 still template stubs. Upstream retires and adopts on measured evidence ([[ADR-0006]], upstream ADR-0008), so the proposal should lead with the count.
