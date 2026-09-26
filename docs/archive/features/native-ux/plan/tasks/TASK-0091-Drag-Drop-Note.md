---
type: "[[task]]"
id: TASK-0091
aliases: ["TASK-0091"]
title: "Drag-and-drop `.md` file → navigate (or offer to add workspace)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0012"
effort: ""
due: ""
depends: ["[[TASK-0070]]"]
blocks: []
related: []
tests: []
---

# Drag-and-drop file

## Definition of Done
- [ ] Drop a `.md` file from Finder onto the cockpit window.
- [ ] If the file path is inside an existing workspace's docs root
      → switch workspace (if needed) + navigate to the file.
- [ ] If outside any known workspace but inside a directory with
      `SNAPSHOT.yaml` → toast: "Add this repo as a workspace?" with
      a button that adds + opens.
- [ ] If neither → ignored toast: "Not a project-os note."
- [ ] Drag-over visual cue (overlay border on the window).

## Steps
- [ ] Renderer-side `dragenter` / `dragover` / `drop` listeners on
      the document. Show the overlay on dragenter; hide on
      dragleave / drop.
- [ ] On drop: read `dataTransfer.files[0]` (Electron's File has
      `.path` even in the renderer); IPC to main for workspace
      discovery + decision.
