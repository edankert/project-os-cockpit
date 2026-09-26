---
type: "[[task]]"
id: TASK-0080
aliases: ["TASK-0080"]
title: "Activity-bar layout shell — rail + in-workspace nav + stage (+ right pane column)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0010"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0082]]", "[[TASK-0083]]", "[[TASK-0085]]"]
related: []
tests: []
---

# Activity-bar layout shell

## Definition of Done
- [ ] `.app` grid is `52px 240px 1fr` (right pane column landed in
      TASK-0085 — placeholder `0` here so adding it later is one CSS
      tweak, not a layout rebuild).
- [ ] HTML restructure:
      - `<aside id="rail">` replaces the workspace-list section of
        the old `.switcher`.
      - `<aside id="ws-nav">` exists between rail and `.stage`.
      - Old `.switcher` element is removed; the terminal toggle that
        lived in its footer moves to the rail's footer (small icon).
      - Old workspace-count label is dropped (the rail is visually
        the count).
- [ ] `.rail` and `.ws-nav` styled to look correct empty (background,
      border, padding); placeholder content in `#ws-nav` reads
      "Workspace nav — landing in TASK-0083".
- [ ] All `min-height: 0` + `overflow: hidden` flex/grid rules
      preserved from the prior switcher fix.
- [ ] Existing scrolling, terminal toggle, ⌘\` shortcut all still
      work end-to-end.

## Steps
- [ ] Patch `desktop/src/renderer/index.html` — restructure the
      sidebar markup.
- [ ] Patch `desktop/src/renderer/renderer.css` — new grid;
      `.rail` styles (52px wide, vertical stack of icon pills);
      `.ws-nav` styles (240px wide, scrollable container).
- [ ] Patch `desktop/src/renderer/renderer.ts` — update DOM lookups
      (`$<HTMLUListElement>('#workspace-list')` likely now lives
      inside `#rail`; rename internally as needed).
- [ ] Move the terminal toggle into the rail footer.

## Notes
Layout-only task. No behaviour changes beyond placement. Confirm
the scrollbar / chrome on the new columns matches the muted-greyscale
palette already in use. The icon pills in `#rail` are just empty
placeholders in this task — TASK-0082 fills them with letters + dots.
