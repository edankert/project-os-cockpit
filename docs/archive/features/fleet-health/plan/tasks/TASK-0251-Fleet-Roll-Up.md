---
type: "[[task]]"
id: TASK-0251
aliases: ["TASK-0251"]
title: "Fleet roll-up — one place that answers whether anything is drifting anywhere"
status: done
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
- [x] One surface lists every workspace that is drifting, with its error count and when it was checked
- [x] Each row deep-links into that workspace's drift panel ([[TASK-0112]]), opening the workspace if it is not current
- [x] Workspaces in an `unknown` state are listed separately from clean ones — not silently folded into "fine"
- [x] The all-clear state says so, and says **how many** repos and when, rather than rendering empty
- [x] It is the only place fleet-wide validation is listed — no second rendering of the same counts

## Steps
- [x] Choose the home: the `~agents` screen already aggregates per-workspace state across the fleet and is the closest existing surface — prefer it over a new screen unless it genuinely does not fit
- [x] Render from the same IPC state the badges use
- [~] Test: three workspaces in three states produce three rows in the right groups; a row navigates

## Notes

**Do not add a second counts surface.** PHASE-010 and PHASE-012 both ended up deleting one — Library's duplicate groups, and the Waiting-on-you list that re-listed what the squares already drew. If the badges answer "which repo", this answers "is anything wrong anywhere", and it should not restate what a badge already says.

The empty state is the one to get right, and it is the common one. *"12 repos, all clean, checked 4 minutes ago"* is information; a blank panel is indistinguishable from a broken one.

## Done 2026-07-30

`buildFleetHealthSection()` on the `~agents` screen, between the fleet list and the session history. That screen already aggregates per-workspace state across the fleet; a second fleet screen would split the answer in two.

- Drifting repos listed by error count, descending. Clicking a row opens that workspace, where [[TASK-0112]]'s drift panel holds the actual violations — this row carries a number and a door, not a second rendering of the errors.
- **Unknown listed separately**, never folded into "fine", with each repo's reason in the tooltip.
- **The all-clear states the count and the age** — *"11 of 12 repos clean, newest check 4m ago"* — because a blank panel is indistinguishable from a broken one, and this is the state the fleet is in most of the time.
- A **Re-check** button, the only user-facing way to force the cold pass. Opening the screen deliberately does not: a surface opening must not fork ten subprocesses.

**No second counts surface.** [[PHASE-010]] and [[PHASE-012]] each ended by deleting one — Library's duplicate groups, and the Waiting-on-you list that re-listed what the phase squares already drew. The badges answer "which repo"; this answers "is anything wrong anywhere". Where they would overlap (a per-repo count), only the badge shows it and the roll-up's row is the deep link.


### The test box is `[~]`, and why

`buildFleetHealthSection` is DOM code in `renderer.ts`, which cannot be imported outside a browser — the same reason every other renderer guard in this repo is structural. It is covered by the **live pass** below rather than by an automated case, which is the bar [[FEAT-0018]] closed on for its badge and drift panel. Stated as a gap rather than ticked: a live pass is evidence, but it does not run again tomorrow.

## Live pass 2026-07-30

With one repo drifting:

```
Docs health                                    [Re-check]
1    project-os-cockpit                        just now
```

With the drift cleared:

```
Docs health                                    [Re-check]
10 of 10 repos clean, newest check just now.
```

Both states are informative — the all-clear names the count and the age rather than rendering an empty panel, which is the requirement that mattered because it is the state the fleet is in almost always. No `unknown` group appeared, correctly: every workspace had been checked by then.
