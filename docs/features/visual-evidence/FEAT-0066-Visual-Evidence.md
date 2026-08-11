---
type: "[[feature]]"
id: FEAT-0066
aliases: ["FEAT-0066"]
title: "Visual evidence — the shell captures a surface into the repo and the note renders it, so evidence a non-code reader can trust"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["Review 2026-08-03: 'evidence: 13 passed in 0.06s' is programmer evidence; for this persona, evidence of UI work is a screenshot"]
goal: "One capture path: the desktop shell snapshots a chosen surface to docs/attachments/, returns the relative path, and runner verdicts, TST evidence and CHG notes reference it as an image the cockpit renders."
requirements: []
tasks:
  - "[[TASK-0297-Capture-To-Attachments]]"
  - "[[TASK-0298-Attach-At-The-Verdict]]"
  - "[[TASK-0299-The-Agent-Side]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
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

## Acceptance

- [x] Captures land in the repo at `docs/attachments/<NOTE-ID>/<date>-<n>.png` and are committed — evidence is record, not staging ([[TASK-0297]])
- [x] The sidecar serves them and Markdown image links render — **no new read path was needed**: `/docs/<path>` already serves the tree and `ImageSourceTreeprocessor` already rewrites image sources
- [x] The runner offers capture at the moment of verdict, and the capture is spent **on** that verdict rather than written loose ([[TASK-0298]])
- [x] Agents cite pictures through the same guarded endpoint, with no agent-specific path ([[TASK-0299]])
- [x] Five refusals with tests: unknown note, non-PNG, malformed base64, oversized blob (git cannot forget one), and a traversing id
- [x] A staged capture leaves `inbox/` when it is filed — staging's success condition is being empty

## Verification

`tests/test_attachments.py` — 11 tests, two of them over a live server for the staging round-trip and its traversal refusal.

The traversal test asserts **both** that the request is refused and that the file outside `inbox/` still exists: a guard that refuses after consuming the file would pass a weaker assertion.
