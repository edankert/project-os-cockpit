---
type: "[[task]]"
id: TASK-0384
aliases: ["TASK-0384"]
title: "Propose the manifest, the status removal and the freshness check upstream — 82 of the 90 documents are in other repos"
status: done
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
- [x] The manifest shape, the status removal and the three checks are proposed to `~/Dev/repos/project-os/`
- [x] The proposal carries the fleet measurement, not just the design
- [x] The two-layer split (template base, project extension) is stated as a requirement of the sync, not a preference
- [x] `yourtrainer-mcp`'s five missing documents are named as the case the presence check is for

## Steps
- [x] Write it against upstream's own conventions; the base set and the validator logic are both template-owned
- [x] Include the before number so the after is measurable
- [x] Flag the `sync-project-os.sh` interaction explicitly

## Notes
This repo holds **8 of 90** standing documents in the fleet. Fixing only these leaves 82 stale in eleven other repos, and the validator logic that would report them is template-owned — so a local-only fix is both the smaller win and the one that drifts at the next sync.

The measurement is the argument: 90 present, 85 stale or undated, 12 still template stubs. Upstream retires and adopts on measured evidence ([[ADR-0006]], upstream ADR-0008), so the proposal should lead with the count.

## Done 2026-08-10

Filed as **`project-os-dev` ISS-0040** (`a4e6555`), which is where upstream proposals go — the same route ISS-0027, ISS-0038 and ISS-0039 took, not `project-os/docs/issues/`, which holds only a README.

It carries the **measurement, not only the design**: 90 of 96 present, 85 of those stale or undated, 12 still template stubs, and `yourtrainer-mcp` missing five of the eight — named as the case the presence check exists for.

**The two-layer split is stated as a requirement of the sync rather than a preference**, which is the part most likely to be lost in translation: `sync-project-os.sh` copies `tools/` wholesale, so a project-specific entry there dies at the next sync. That is why extensions must live in `SNAPSHOT.yaml`, and why the base cannot.

It points at the working implementation here rather than describing one, and it ends with the before-number so adoption is measurable: *"85 of 90 stale or undated is the before. The proposal is only worth adopting if that number moves."*

`project-os-dev`'s own metrics needed a `--fix-metrics` pass before its validator was clean; that is committed with the issue.
