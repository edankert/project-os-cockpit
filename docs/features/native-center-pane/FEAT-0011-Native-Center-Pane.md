---
type: "[[feature]]"
id: FEAT-0011
aliases: ["FEAT-0011"]
title: "Native centre pane + routing (rendered Markdown, history, anchors, interactive checkboxes)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Replace the iframe with a native renderer pane that fetches the rendered Markdown HTML fragment (FEAT-0008) and owns navigation, history, scroll preservation, hash anchors, and interactive checkboxes."
related: ["[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0009-Native-Shell-Layout]]", "[[FEAT-0010-Native-Nav-Right-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: []
release: ""
tests: []
---

# Native centre pane + routing

## Goal
The centre column — currently an iframe showing the Python tool's
full HTML page — becomes a TypeScript component that fetches the
rendered Markdown HTML fragment from `GET /api/render/<rel-path>`
and mounts it in-place. The renderer owns navigation (intercepts
internal `<a>` clicks), history (back/forward), scroll preservation
per note, hash anchors, and interactive checkboxes.

After this lands, there is no iframe anywhere in the desktop app.

## Scope

### In scope

**Render flow:**
- On nav request: `fetch('/api/render/<rel-path>')` → set
  `centre.innerHTML = response.html` → run a "post-mount" pass that:
  - rewrites `[[wikilink]]` anchors' click handlers to soft-nav,
  - rewrites `<a href="docs/...">` to soft-nav,
  - rewrites `<a href="https://…">` to `shell.openExternal` via IPC,
  - re-runs syntax highlight if needed (probably Python already did),
  - wires `<input type="checkbox" data-task-list>` for interactive
    edits (writes back via a new `POST /api/notes/check-toggle` or
    similar — TASK-0042 design, but now native).

**Routing:**
- In-memory history stack. Back / forward via mouse buttons +
  Cmd+[, Cmd+], menu items.
- Hash anchors: support `#some-heading`; scrolls within mounted
  HTML; preserved in history.
- Per-note scroll restore: remember scroll position keyed by
  `rel_path`; restore on history back.
- Deep links from FEAT-0007's `cockpit://` handler navigate the
  centre pane (today they only switch workspace).

**Cockpit focus events:**
- Receiving `cockpit:focus` SSE event (from
  `subscribeAgentFocus` in `desktop/src/ipc/agent-focus.ts`) drives
  centre-pane navigation, matching the iframe's current behaviour.

**Interactive checkboxes** (TASK-0042 lift):
- Native version of the checkbox toggle. Optimistic update +
  write-back to the Python sidecar (new endpoint:
  `POST /api/notes/check-toggle {path, line, checked}`).

### Out of scope
- Markdown rendering itself — stays in Python (`renderer.py`).
- Find in document — that's FEAT-0012.
- Side-by-side / two-pane comparison view — FEAT-0012.
- Inline note editing — out of scope for the cockpit (always).
- Plugin / extension hooks for custom render passes.

## Acceptance
- Picking any note in the left nav renders inside the centre pane
  with no iframe. Visual parity with mode 1.
- `[[wikilinks]]` and project-os ID links navigate softly (no full
  reload). External links open in the system browser via
  `shell.openExternal`.
- Browser-style back / forward (mouse buttons + menu items) walks
  the history.
- Switching notes back and forth restores the scroll position of
  the previous note.
- A `#heading` link scrolls to that heading; back recovers the
  previous scroll.
- Clicking a task-list checkbox toggles it in the underlying `.md`
  file (verified by `git diff`); SSE confirms the file change.
- `cockpit focus <id>` from any terminal lands the user at the
  expected note.

## Open questions
- **HTML or AST from Python.** v1 = HTML fragment (simpler).
  Re-evaluate if styling drift becomes painful — a structured
  payload would let the TS layer style frontmatter cards and
  wikilinks consistently with the rest of the renderer.
- **Diff-friendly checkbox toggles.** Implementation reuses
  TASK-0042's mode-1 design if any of it was written.

## Links
- API endpoint contract: [[FEAT-0008-Cockpit-API-Hardening]].
- Sibling panes: [[FEAT-0010-Native-Nav-Right-Pane]],
  [[FEAT-0009-Native-Shell-Layout]].
- Replaces the iframe in [[FEAT-0007-Desktop-Shell]].
- Phase: [[PHASE-006-Native-Cockpit-UI]].
