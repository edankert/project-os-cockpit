---
type: "[[change]]"
id: CHG-20260803-One-Handle-One-Column
title: "One expand handle across the whole tree, and a group head's id no longer gives up its space to a long title"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-03
review_verdict: approved
date: 2026-08-03
owner: user:edwin
component: [static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[ISS-0091-Two-Handles-And-A-Shrinking-Id]]"]
---

# One handle, one column

## What changed

**Phase ids are fully visible.** Three of eighteen were clipped — `PHASE-007` showed 7px of the 62 it needs — because `flex: none` on the id was scoped to rows and not to group heads, so a long phase title took the space. The ellipsis now sits on the name, which is the part that should shorten.

**One expand handle.** Group heads drew an 8px caret from two rotated borders; feature rows drew a 4px solid triangle; the right pane and the overview drew the same triangle. All four now use the triangle — the smaller one, as asked.

## Paths

- `src/project_os_cockpit/static/cockpit.css` — `.group-chevron` becomes `.ov-chev`'s triangle
- both stylesheets — `.nav-group-header .nav-id { flex: none }`, the ellipsis moved to `.group-header-name`
- `desktop/src/renderer/renderer.css` — `.group-header-inner` stops clipping

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
