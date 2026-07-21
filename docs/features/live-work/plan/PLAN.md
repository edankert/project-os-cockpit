# Plan — FEAT-0036 Live work views

Order: 0162 → 0163 → 0164 → 0165 (the diff layer is the shared foundation; session scope first — it's where the user watches; the board is a rendering of 0164's data).

1. **TASK-0162.** Status-diff layer: frontmatter differ in the watcher path, `cockpit:status-change` SSE + recent-transitions log, pytest coverage.
2. **TASK-0163.** Session rail "work" tab (boxes + expandable chip list), driven by tracker `docs_notes` × status-change events.
3. **TASK-0164.** Active nav mode (left pane), default for phase-less projects.
4. **TASK-0165.** Overview Now board for phase-less projects.
