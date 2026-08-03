---
type: "[[feature]]"
id: FEAT-0066
aliases: ["FEAT-0066"]
title: "Visual evidence — the shell captures a surface into the repo and the note renders it, so evidence a non-code reader can trust"
status: planned
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Review 2026-08-03: 'evidence: 13 passed in 0.06s' is programmer evidence; for this persona, evidence of UI work is a screenshot"]
goal: "One capture path: the desktop shell snapshots a chosen surface to docs/attachments/, returns the relative path, and runner verdicts, TST evidence and CHG notes reference it as an image the cockpit renders."
requirements: []
tasks:
  - "[[TASK-0297-Capture-To-Attachments]]"
  - "[[TASK-0298-Attach-At-The-Verdict]]"
  - "[[TASK-0299-The-Agent-Side]]"
release: ""
related: ["[[FEAT-0063-The-Acceptance-Runner]]"]
tests: []
---

# Visual evidence

## Goal

The preload already exposes `captureScreenshot`; this feature gives it a home and a contract: captures land in `docs/attachments/<note-id>/<date>-<n>.png` (committed — evidence is record), the sidecar serves them, markdown image links render in the note view, and the runner/desk offer capture at the moment of verdict.

## Integration points (investigated)

- Electron `webContents.capturePage` on the workspace view; the existing preload seam.
- Write path through a new note_writes attach helper (allow-listed like everything else) so evidence lines carry their image reference in one write.
- The agent side gets the same endpoint, so a CHG can carry before/after without me describing pixels in prose.

## Out of Scope

- Screenshot *diffing* — DES-0007 rejects pixels as a comparator; images are evidence, the measure view is the comparator.
- Any capture leaving the repo. Attachments are files beside the notes they evidence.
