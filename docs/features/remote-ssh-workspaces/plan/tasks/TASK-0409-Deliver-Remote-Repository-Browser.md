---
type: "[[task]]"
id: TASK-0409
title: "Deliver the remote repository browser"
status: backlog
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
source: []
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: M
depends: ["[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]"]
blocks: []
related: ["[[REQ-0036-Remote-Development-Workflow]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Deliver the remote repository browser

## Definition of Done

- [ ] The cockpit displays a lazy, bounded directory tree, text preview, and remote git status for the selected remote root.
- [ ] Paths outside the selected root are rejected after canonical-path resolution; symlink presentation makes an escape visible rather than silently following it.
- [ ] Selecting an item can open its project-os note/context or create a terminal at its containing directory without adding file mutation in v1.

## Steps

- [ ] Specify the remote filesystem API, paging limits, ignore rules, and binary/large-file behaviour.
- [ ] Implement the renderer tree and preview with workspace-qualified paths.
- [ ] Add git status and context actions with a safe path-resolution test matrix.
