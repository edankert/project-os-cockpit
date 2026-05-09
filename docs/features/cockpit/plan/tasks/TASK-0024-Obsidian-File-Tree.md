---
type: "[[task]]"
id: TASK-0024
aliases: ["TASK-0024"]
title: "Cockpit: Obsidian-style file tree styling for compact trees"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0012]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0021]]"]
blocks: []
related: ["[[TASK-0023]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0024 — Obsidian-style file tree for compact trees

## Definition of Done
- [x] All `nav-group-compact` groups in Project mode render as a tight file/folder tree.
- [x] Folder rows: folder icon + chevron + label, full-width hover band.
- [x] File rows: file icon + filename, mono font, tighter rows.
- [x] Indent guides: muted vertical line at each nesting level (driven by `--tree-indent` + `data-depth` mirrored on the `<details>`).
- [x] Hover band spans the full row for both folders and files.
- [x] Visual quiet — no card borders between rows in compact trees.
- [x] Card-layout groups (Features/Tasks/Issues lists) are unaffected.

## Steps
- [x] Kept existing rotated-square chevron (consistent with other section headers); rest of the styling is the visible change.
- [x] Folder icon via CSS `mask-image` (inline SVG data URL) before subgroup labels.
- [x] File icon via `mask-image` on `.nav-item-compact::before`.
- [x] Indent-guide via `::before` pseudo on nested `.nav-subgroup[data-depth]:not([data-depth="0"])`; depth + `--tree-indent` mirrored from JS onto the `<details>`.
- [x] Tightened padding, removed `border-bottom` on compact rows, added full-width hover band.
- [ ] Visual verification in a browser is still pending — server-side payload was checked but final pixel-level output (icon weights at light/dark themes, spacing) was not opened in a browser by the implementing agent.

## Notes
CSS-only change. Server payload unchanged.
