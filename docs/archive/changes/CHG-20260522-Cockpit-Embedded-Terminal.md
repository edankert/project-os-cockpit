---
type: "[[change]]"
id: CHG-20260522-Cockpit-Embedded-Terminal
aliases: ["CHG-20260522-Cockpit-Embedded-Terminal"]
title: "Cockpit: embedded ttyd terminal in centre-column bottom panel"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0043]]", "[[TASK-0044]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/templates.py"
  - "src/project_os_cockpit/server.py"
  - "src/project_os_cockpit/terminal.py"
  - "src/project_os_cockpit/static/cockpit.css"
  - "src/project_os_cockpit/static/cockpit.js"
  - "tests/test_terminal.py"
issues: []
features: ["[[FEAT-0003]]"]
related: ["[[ADR-0002]]", "[[REQ-0005]]"]
---

# Cockpit: embedded ttyd terminal

## Summary
Implements the v1 path from ADR-0002 — an embedded terminal that lives inside the cockpit window. ttyd spawns as a child process bound to `127.0.0.1` only (REQ-0005), and a new bottom panel inside the centre column hosts the iframe. The left and right panes remain full-height; only the centre column splits vertically.

## Impact

### Layout (TASK-0043)
- `templates.py`: wrapped `<main id="cockpit-centre">` in a new `.cockpit-centre-column` (vertical flex). Added `.cockpit-bottom-resizer` (4px draggable splitter) and `.cockpit-bottom-panel` (header strip + body) as siblings of the centre.
- `cockpit.css`: vertical flex on the centre column; centre = `flex: 1 1 auto; overflow-y: auto;` so it still scrolls internally; bottom panel = `flex: 0 0 auto` with default height 280px and `is-collapsed` shrinks to 26px (header only).
- `cockpit.js`: `mountBottomPanel()` wires the header toggle, persists `BOTTOM_COLLAPSED_KEY` + `BOTTOM_HEIGHT_KEY`. Drag-resize on the top splitter clamps between 80–`window.innerHeight - 120`px. Collapsed by default (matches the task spec).
- Resizer hidden via `:has()` when the panel is collapsed.

### Terminal (TASK-0044)
- New `terminal.py` — `TerminalProcess` class: spawn `ttyd -p <free-port> -i 127.0.0.1 -W <cmd>` from the project root; `atexit` handler kills it on cockpit exit. Lazy start on first `/api/terminal` call.
- `server.py`: imports `TerminalProcess`, instantiates one per handler-factory (lazy spawn), adds `GET /api/terminal` returning `{enabled, url, command}` or `{enabled: false, reason: …}` when ttyd is missing.
- `cockpit.js` `mountTerminalIframe()`: fetched on first panel-expand; renders `<iframe src="…">` or an install hint with a `<code>brew install ttyd</code>` snippet.

### Security
- ttyd `-i 127.0.0.1` enforces REQ-0005 even when the cockpit render endpoint is on `0.0.0.0` (LAN access for tablets etc.).
- Default command is `$SHELL` (`/bin/zsh` on macOS); user manually launches Claude Code / Codex / Gemini CLI inside.

### Tests
- `tests/test_terminal.py` (7 cases): binary detection, free-port allocation, info() fallback when ttyd missing, default-command resolution, command override, stop() idempotency, disabled-payload shape.
- 63 cockpit/index/release tests passing / 1 skipped (was 56 / 1; +7).

### Verified live (your-trainer/docs)
- `curl /api/terminal` returns `{"enabled": true, "url": "http://127.0.0.1:58935", "command": ["/bin/zsh"]}`.
- ttyd responds 200 on the allocated port (`curl -I http://127.0.0.1:58935`).
- Subsequent `/api/terminal` calls reuse the same URL (idempotent start).

## Follow-ups
- [ ] **TASK-0046** (already scaffolded): browser tab indicator on file-watcher activity. Independent — ships next.
- [ ] **TASK-0045**: preview tab next to the terminal (config-driven iframe / log-tail). Same panel, sibling tab.
- [ ] SIGTERM signal handler in `server.py` so ttyd is killed if the cockpit is sent SIGTERM (currently only `atexit` covers normal exit / KeyboardInterrupt).
- [ ] Project config (in `SNAPSHOT.yaml`?) to override the default terminal command (`claude-code`, `codex`, `gemini-cli`).
- [ ] REQ-0013 amendment: the requirement today specifies a 3-pane cockpit; the bottom panel adds a 4th surface inside the centre column. Update REQ-0013 prose or add a sibling REQ to document the layout.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0003 → in-progress)
- requirements: pending amendment to REQ-0013 (follow-up)
- tasks: new ([[TASK-0043]], [[TASK-0044]])
- issues: not-applicable
- tests: new (`tests/test_terminal.py`)
- workflows: not-applicable
- decisions: not-applicable (ADR-0002 already chose ttyd)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (FEAT-0003 status, focus.task → TASK-0046, metrics tasks_done 35→37, items.changes addition)
