---
type: "[[task]]"
id: TASK-0251
aliases: ["TASK-0251"]
title: "Fleet roll-up — one place that answers whether anything is drifting anywhere"
status: backlog
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0028-Fleet-Health-Surface]]"]
parent: "[[FEAT-0028-Fleet-Health-Surface]]"
effort: S
depends: ["[[TASK-0248-Live-Workspace-Validation-Aggregate]]", "[[TASK-0249-Cold-Workspace-Validation]]"]
blocks: []
related: ["[[TASK-0112-Health-Badge-And-Drift-Panel]]", "[[FEAT-0032-Agents-Screen]]"]
tests: []
---

# TASK-0251 — The roll-up

## Definition of Done
- [ ] One surface lists every workspace that is drifting, with its error count and when it was checked
- [ ] Each row deep-links into that workspace's drift panel ([[TASK-0112]]), opening the workspace if it is not current
- [ ] Workspaces in an `unknown` state are listed separately from clean ones — not silently folded into "fine"
- [ ] The all-clear state says so, and says **how many** repos and when, rather than rendering empty
- [ ] It is the only place fleet-wide validation is listed — no second rendering of the same counts

## Steps
- [ ] Choose the home: the `~agents` screen already aggregates per-workspace state across the fleet and is the closest existing surface — prefer it over a new screen unless it genuinely does not fit
- [ ] Render from the same IPC state the badges use
- [ ] Test: three workspaces in three states produce three rows in the right groups; a row navigates

## Notes

**Do not add a second counts surface.** PHASE-010 and PHASE-012 both ended up deleting one — Library's duplicate groups, and the Waiting-on-you list that re-listed what the squares already drew. If the badges answer "which repo", this answers "is anything wrong anywhere", and it should not restate what a badge already says.

The empty state is the one to get right, and it is the common one. *"12 repos, all clean, checked 4 minutes ago"* is information; a blank panel is indistinguishable from a broken one.
