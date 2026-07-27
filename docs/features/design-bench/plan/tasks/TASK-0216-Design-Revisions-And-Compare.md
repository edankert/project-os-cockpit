---
type: "[[task]]"
id: TASK-0216
aliases: ["TASK-0216"]
title: "Revisions from git, side by side, with the reason for each"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[REF-0001-Overview-Redesign-Dossier]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0214]]"]
blocks: []
related: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tests: []
---

# Revisions and compare

## Definition of Done

- [ ] The surface lists an artifact's revisions from git history, newest first, each with date, commit and subject
- [ ] Any two revisions render **side by side** at the same viewport
- [ ] The reason for a revision is visible next to it — sourced from the commit subject/body, so the record exists whether or not the cockpit is running
- [ ] Selecting a revision renders that revision, not the working copy
- [ ] An artifact with a single revision shows the list without offering a meaningless comparison
- [ ] Reading a historical revision never mutates the working tree

## Steps

- [ ] Add a revisions endpoint (`git log --follow` over the asset path, argv-fixed, clamped)
- [ ] Serve an artifact at a given commit (`git show <sha>:<path>`) without checking anything out
- [ ] Build the side-by-side view reusing the viewport switcher from [[TASK-0215]]
- [ ] Verify against a real multi-revision artifact — create one by committing a genuine revision of REF-0001's dossier

## Notes

This is the task that addresses the actual loss. The overview dossier went through six revisions in one session; the sixth is committed and the reasoning for the other five is in a transcript. Going forward the commit *is* the record, which is why the reason comes from the commit message rather than a field the cockpit owns — it survives the tool.

`git show <sha>:<path>` rather than a checkout is deliberate: reading history must never touch the working tree. The commits endpoint added in [[TASK-0199]] is the model for the subprocess handling (fixed argv, timeout, clamped limit).
