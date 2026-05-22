---
type: "[[task]]"
id: TASK-0042
aliases: ["TASK-0042"]
title: "Cockpit: interactive markdown checkboxes (click to toggle, file write-back)"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: []
related: ["[[TASK-0043]]"]
tests: []
---

# TASK-0042 — Interactive markdown checkboxes

## Goal
Let the user (or an LLM) emit `- [ ] item` / `- [x] item` lines in `.md` notes and have the cockpit render those as real interactive checkboxes. Clicking writes the toggle back to the source file. The watcher → SSE pipeline already handles re-rendering on file change.

## Definition of Done
- [ ] Markdown renderer turns GitHub-flavored task-list items into `<input type="checkbox">` elements with a `data-file` + `data-line` attribute.
- [ ] Centre pane JS intercepts clicks on these checkboxes, calls a new server endpoint, prevents the link-navigation default.
- [ ] Server endpoint `POST /api/checkbox` accepts `{path, line, checked}` and atomically flips the `[ ]` ↔ `[x]` character on that line. Validates the path is under `docs_root` (no `..` escape).
- [ ] Watcher detects the file change and re-renders the centre pane (existing behaviour).
- [ ] No flicker between click and re-render (optimistic local toggle, then resync from server payload).
- [ ] Tests: server endpoint accepts a happy path; rejects path traversal; rejects out-of-range line; handles `[X]` (capital) and indented list items.

## Steps
- [ ] Add a markdown extension (custom inline processor or post-process step) that emits `<input type="checkbox" class="task-list-checkbox" data-file="…" data-line="…">`. Mark as `disabled` if we want read-only first; remove `disabled` once API is wired.
- [ ] CSS: align the checkbox with the list bullet, muted hover, accent when checked.
- [ ] JS: delegated click listener in `cockpit.js` that calls `POST /api/checkbox`. Update the local DOM optimistically; revert + log on server error.
- [ ] Server: implement `POST /api/checkbox`. Read file, validate line, replace one character (the space inside `[ ]` becomes `x` and vice versa), write atomically.
- [ ] Tests: `tests/test_checkbox_api.py` (new) — happy path, traversal rejection, malformed payload, missing line.

## Notes
- This is the lingua franca for LLM ↔ user interactions in markdown — every editor supports it.
- File-write happens on every click. Acceptable for v1 because the file watcher coalesces rapid changes; we can add request debouncing later if needed.
- Future: structured form notes (`type: review` frontmatter with `options:` list) for radio / multi-select interactions. Deferred until checkboxes prove too weak.
