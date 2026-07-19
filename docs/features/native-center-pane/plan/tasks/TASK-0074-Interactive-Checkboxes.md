---
type: "[[task]]"
id: TASK-0074
aliases: ["TASK-0074"]
title: "Interactive checkboxes — POST /api/notes/check-toggle + renderer click handler"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0042]]"]
parent: "FEAT-0011"
effort: ""
due: ""
depends: ["[[TASK-0070]]"]
blocks: []
related: []
tests: []
---

# Interactive checkboxes

## Definition of Done
- [ ] New endpoint `POST /api/notes/check-toggle` accepts
      `{path, line, checked}` — locates the `- [ ]` / `- [x]`
      token on the given 1-based line and rewrites it.
- [ ] Path traversal guarded; only `.md` files under the docs root
      mutated.
- [ ] Per-file write lock so concurrent toggles don't race.
- [ ] Renderer click handler on `input[type=checkbox][data-task-list]`
      reads `data-line` (emitted by the markdown renderer) and POSTs.
- [ ] Optimistic UI update; SSE `file-changed` confirms.
- [ ] HTTP-level test covering: happy toggle on/off, 400 on
      missing field, 403 on path traversal, 404 on missing line.
- [ ] TST-* note documenting the test.
- [ ] `docs/references/COCKPIT-API.md` updated with the new
      endpoint.

## Steps
- [ ] Python: implement `_serve_check_toggle` in `server.py`;
      module-level `_FILE_LOCKS` dict; reuse `_jsonable` /
      response helpers.
- [ ] Python: extend `renderer.py` so the tasklist markdown
      extension emits `data-line="<N>"` on each rendered checkbox
      (so the client can identify which line to toggle).
- [ ] Renderer: click handler on `#doc-view` matching
      `input[type=checkbox]`; POST; on success, update the
      checkbox's `checked` attribute (mounted HTML is replaced
      anyway when SSE refresh fires).

## Notes
Original TASK-0042 (browser cockpit, status `backlog`) had the
same goal in mode 1. This task supersedes it for mode 3; closing
out 0074 in mode 3 doesn't automatically close 0042 (the browser
cockpit would still need its own renderer-side wiring), but the
Python endpoint is shared and could be reused later.

The `data-line` injection in the markdown renderer is the
shared work that benefits both modes.
