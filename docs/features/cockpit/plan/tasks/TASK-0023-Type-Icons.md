---
type: "[[task]]"
id: TASK-0023
aliases: ["TASK-0023"]
title: "Cockpit: inline SVG type icons across panes"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: []
blocks: ["[[TASK-0025]]", "[[TASK-0028]]"]
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0023 — Inline SVG type icons across cockpit

## Definition of Done
- [x] Each cockpit item shape (left + right pane) carries the note `type` so the JS can render an icon for it.
- [x] A `typeIcon(type, size)` helper in `cockpit.js` returns a Lucide-style monochrome stroke SVG (14px default, 13px for group headers) per known type.
- [x] Icons appear: left-pane `navItem` and `navItemStacked`, right-pane `ctxItem` and `ctx-type-label` group header.
- [x] Icon color uses the existing `--type-<name>` tokens (CSS `.type-icon[data-type=...]`).
- [x] Unknown / empty types fall back to the file-text icon.
- [x] Tests pass; new tests assert `type` is present on every item across modes and on context items.

## Type → icon mapping
- feature → flag
- task → check-square
- issue → alert-octagon
- requirement → clipboard-list
- phase → milestone
- change → git-commit
- adr → scale
- risk → shield-alert
- test → flask-conical
- workflow → workflow
- release → package
- reference → book-open
- plan → map
- (default) → file-text

## Steps
- [ ] Extend item shapes in `cockpit.py` to emit `"type": record.note_type or ""`.
- [ ] Add `typeIcon(type)` + SVG path table to `cockpit.js`.
- [ ] Mount in `navItem`, `navItemStacked`, `ctxItem`. Update `ctx-type-label` group header to include the same icon.
- [ ] CSS tweaks: `.type-icon { color: var(--type-default) } .type-icon[data-type="…"] { color: var(--type-…) }`.
- [ ] Tests: assert `type` field is emitted.

## Notes
Stays inline (no font/icon library) so there's still no build step.
