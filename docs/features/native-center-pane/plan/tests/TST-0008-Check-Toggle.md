---
type: "[[test]]"
id: TST-0008
aliases: ["TST-0008"]
title: "POST /api/notes/check-toggle — write-back, error shapes, nested tasks"
status: passing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0074]]"]
verifies: ["[[TASK-0074]]", "[[FEAT-0011-Native-Center-Pane]]"]
path: "tests/test_check_toggle.py"
---

# TST-0008 — checkbox toggle endpoint

## Intent
Locks the wire shape + on-disk mutation contract of `POST
/api/notes/check-toggle`. The renderer fires this on every
checkbox click; getting it wrong corrupts the user's note files.

## Coverage

**Happy paths (3)**
- Toggle on (`[ ]` → `[x]`); other lines untouched.
- Toggle off (`[x]` → `[ ]`).
- `docs/...` leading-segment tolerated (matches `/api/render`'s
  normalisation rule).

**Error shapes (5)**
- 400 on missing `path` / `index` / `checked`.
- 403 on path traversal (`..`).
- 404 on missing file.
- 404 on `index` out of range (and the error message names the
  count it found).

**Nested-list ordinals (1)**
- Indented `  - [ ] inner-x` items count toward the global index —
  match the rendered DOM order, where indent doesn't reset the
  ordinal.

## Location
`tests/test_check_toggle.py` — 10 tests, all passing as of
2026-05-25.

## Status
`passing` — 10/10.
