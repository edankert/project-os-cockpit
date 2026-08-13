---
type: "[[task]]"
id: TASK-0415
aliases: ["TASK-0415"]
title: "Git state for every workspace, including the one you have open"
status: backlog
owner: unassigned
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

- [ ] A workspace with a live sidecar reports `ahead` and `remoteKind` like any other, and the values survive a live validator report.
- [ ] The row merge stops replacing wholesale: a validator report updates validator fields and leaves git fields alone, or refreshes them deliberately.
- [ ] The three existing surfaces (overview band, Agents group, rail tooltip) come back to life for the open workspace with no changes of their own — evidence that the defect was the data, not them.
- [ ] A test asserts the property directly: a workspace with a live subscription still yields a git count. The current bug passes every existing test.
- [ ] The no-remote case is equally live: `remoteKind === 'none'` reaches the surfaces for an open workspace, so *nothing here is backed up* can be said about the repo you are in.

## Steps

- [ ] Choose among [[ISS-0156]]'s three candidates — probe git in the shell for live workspaces (cheapest, and puts the count in the process that owns the push), split the cold pass so git ignores the live-sidecar skip, or teach the sidecar's validation payload to carry git state.
- [ ] Implement, with the merge fix.
- [ ] Add the regression test, and check it fails before the fix.
