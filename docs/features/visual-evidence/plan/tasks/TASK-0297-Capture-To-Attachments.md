---
type: "[[task]]"
id: TASK-0297
aliases: ["TASK-0297"]
title: "Capture lands in the repo and serves back"
status: backlog
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0066-Visual-Evidence]]"]
parent: "[[FEAT-0066-Visual-Evidence]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Capture lands in the repo and serves back

## Definition of Done

- Shell IPC captures the chosen surface to `docs/attachments/<note-id>/<date>-<n>.png`; sidecar serves attachments; markdown image links render in the note view.
- Captures are committed files — evidence is record; the attachments dir joins the docs contract, not gitignore.
