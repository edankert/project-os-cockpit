---
type: "[[task]]"
id: TASK-0415
aliases: ["TASK-0415"]
title: "Git state for every workspace, including the one you have open"
status: done
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: S
depends: []
blocks: ["[[TASK-0417-Publication-Enters-The-Registry]]"]
related: ["[[FEAT-0098]]", "[[FEAT-0055]]"]
tests: []
---

# Git state for every workspace

Closes [[ISS-0156]]. `ahead` and `remoteKind` are assigned only in `refreshColdWorkspaces()`, which skips every workspace with a live sidecar — so the repo you are working in, the one accumulating commits, is the one with no count. The live path replaces the whole row, so a count learned while the workspace was cold is erased rather than merely stale.

**First, and not a footnote.** Absent-at-zero ([[ADR-0027]] admission test 4) means an unknown count renders exactly like nothing-owed. Every surface built on top of this would be silent in precisely the case it exists for, and would look correct.

## Definition of Done

- [x] A workspace with a live sidecar reports `ahead` and `remoteKind` like any other, and the values survive a live validator report.
- [x] The row merge stops replacing wholesale — **stronger than asked**: git state moved out of the validator row into its own map, composed at read time in `fleetHealth()`, so no validator code path *can* clobber it. The class of bug is gone, not the instance.
- [x] The three existing surfaces come back to life for the open workspace with no changes of their own — the defect was the data.
- [x] A test asserts the property directly (`desktop/tests/git-state.test.mjs`, real git repos): a live-subscribed workspace still yields its count, and a live validator report does not erase it.
- [x] The no-remote case is equally live: `null` and `'none'`, never `0`.

## How it was done

**[[ISS-0156]]'s first candidate**, and one step further. Rather than probing git for live workspaces *as well*, the shell now probes it for **every** workspace on one clock (`refreshGitState`, 60s) and the cold pass no longer reports git at all. The live/cold split belongs to the validator — a repo with its own sidecar genuinely has a better answer about its notes — and never belonged to git, where the sidecar knows nothing the shell cannot ask `git` directly. Applying it to both is what the defect *was*, so removing the split removes it.

`fleet_validate.py` still emits `ahead`/`remote_kind` for anyone running it standalone; the shell simply stops reading them.

## Adequacy

Reverting the composition in `fleetHealth()` fails four of the five cases and leaves the pure-function one passing — checked by mutation, not assumed. The existing suite passed against the defect, which is why the test is new rather than adjusted.

## Steps

- [x] Choose among [[ISS-0156]]'s three candidates.
- [x] Implement, with the merge fix.
- [x] Add the regression test, and check it fails before the fix.
