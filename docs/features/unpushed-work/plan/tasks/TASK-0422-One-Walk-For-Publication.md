---
type: "[[task]]"
id: TASK-0422
aliases: ["TASK-0422"]
title: "One walk for publication — three implementations of 'what is unpublished' become one, and the guard can see the surface written in the other language"
status: done
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["[[ISS-0165]], filed by independent review of [[FEAT-0100]] 2026-08-14, finding 4"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: []
blocks: []
related: ["[[ISS-0165-The-Attention-Card-Reads-A-Second-Git-Walk]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]", "[[TASK-0415-Git-State-For-Every-Workspace]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tests: []
---

# One walk for publication

## The count exists three times, not twice

[[ISS-0165]] names two. There are three:

| where | what it walks | who reads it |
|---|---|---|
| `git_state.read()` | `rev-list @{u}..HEAD`, plus the commits themselves | the badge (`obligations._publication_rows`) and History |
| `probeGitState` (`desktop/src/ipc/git.ts`) | the same `rev-list`, in TypeScript, on a 60s clock | the rail's attention card and the fleet roll-up |
| `fleet_validate.git_standing` | the same `rev-list` again, in Python | **nobody** — the shell computes it and deliberately discards it ([[ISS-0156]]) |

The third is the tell. A rule that exists three times has already stopped being a rule.

## Why the issue's own resolution cannot be taken as written

It says: *have `fleetHealth` read the sidecar's publication payload*. A sidecar exists only for a workspace someone has **opened**. The card is cross-workspace and the roll-up covers the whole fleet, so reading the sidecar answers for one repo and leaves eleven blank — which is [[ISS-0156]] inverted, and `refreshGitState` exists precisely because the live/cold split does not belong to git. The property to preserve is *one clock for the whole fleet*, and the property to gain is *one implementation*. The sidecar route trades the first for the second.

## What it does instead

**The one implementation is the Python one, and the shell calls it for every workspace on the clock it already has.**

- A new `project_os_cockpit.fleet_git` module: `python -m project_os_cockpit.fleet_git <root>…` emits one JSON line per repo — `{root, ahead, remote, remote_kind, dirty}` — from `git_state.read()`. Small, and it imports `git_state` alone rather than the cockpit, because it runs every 60 seconds in a subprocess.
- `refreshGitState()` calls it for **all** workspaces, live and cold, replacing the per-repo `probeGitState` fan-out. One clock, unchanged.
- `probeGitState` loses its counting. `git.ts` keeps `remoteKind`, which is deliberate and asserted against the same URL table in both suites: it is the classification that decides whether `git push` may run, and the process that runs the push does not take that answer over IPC.
- `fleet_validate.git_standing` delegates to `git_state.read()` rather than repeating it. Its output is unchanged for anyone running the module standalone.
- **`dirty` comes along**, because it is the same defect one number to the left: `_uncommitted_notes` (History's band) and `probeGitState` both walk `git status --porcelain -- docs/ SNAPSHOT.yaml`. `git_state` gains that walk, History decorates its rows from it, and `GitState.dirty` is what the shell reads. Leaving it behind would mean deleting one git walk from `git.ts` and keeping the other, on the same row of the same card.

## Definition of Done

- [x] `desktop/src/ipc/git.ts` contains no commit count and no `status --porcelain`; a guard asserts it, so the third surface is no longer invisible to the check that exists to stop it disagreeing.
- [x] Every workspace — live and cold — still gets an `ahead`, from one Python implementation, on the existing 60s clock. [[ISS-0156]]'s node test still passes unchanged.
- [x] `fleet_validate.git_standing` and `_uncommitted_notes` both read `git_state`; no module walks git for publication state on its own.
- [x] A test asserts the shell's numbers and the badge's numbers come from the same call, rather than asserting that two numbers happen to match.
- [x] An unreadable or missing repo keeps its last answer and never renders as "pushed" (the existing behaviour, preserved through the new path).
