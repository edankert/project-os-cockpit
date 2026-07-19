---
type: "[[task]]"
id: TASK-0045
aliases: ["TASK-0045"]
title: "Cockpit: project preview tab (config-driven iframe or log-tail)"
status: backlog
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
parent: "[[FEAT-0003]]"
fixes: []
effort: M
due: ""
depends: ["[[TASK-0043]]"]
blocks: []
related: ["[[TASK-0044]]"]
tests: []
---

# TASK-0045 — Project preview tab

## Goal
Sibling tab to the Terminal in the bottom panel. Renders project-generated content per project type — iframe of the project's dev server (web apps), or live log tail of a configured command (native / API projects).

## Definition of Done
- [ ] Bottom panel has a "Preview" tab next to "Terminal".
- [ ] Config schema (e.g. `cockpit.preview` block in `SNAPSHOT.yaml` or sibling `cockpit.config.yaml`):
  ```yaml
  preview:
    mode: iframe        # iframe | log | off
    url: http://localhost:3000
    # OR
    mode: log
    command: ["tail", "-f", "build/log.txt"]
  ```
- [ ] When `mode: iframe`: render `<iframe src=…>` filling the tab body. Sandbox attribute optional; document trade-offs.
- [ ] When `mode: log`: spawn the command, stream its stdout into a scrolling `<pre>` (server-side via SSE; client appends + auto-scrolls).
- [ ] When `mode: off` (or missing config): tab is hidden.
- [ ] Process lifecycle: log-mode command starts when tab first activated; killed when cockpit exits. Restart button in the tab header.
- [ ] Tests: config parsing (each mode), log-mode command lifecycle, iframe URL validation (must be local — no remote URLs without explicit allow-list).

## Steps
- [ ] Define the config schema. Decide whether it lives in `SNAPSHOT.yaml` (under a `cockpit:` block) or a sibling `cockpit.config.yaml`. Lean towards SNAPSHOT to avoid yet another file.
- [ ] Server: `src/project_os_cockpit/preview.py` — config loader + log-mode subprocess manager. Expose `GET /api/preview/config` and `GET /api/preview/log` (SSE for live tail).
- [ ] JS: Preview tab content — branch on mode; iframe or log viewer.
- [ ] CSS: minimal — match the terminal tab styling.
- [ ] Tests: `tests/test_preview.py`.

## Notes
- The cockpit doesn't run the user's dev server — that's the user's responsibility. The Preview tab just embeds what's there. (Bun-/Vite-style projects already have `npm run dev` running externally.)
- For native (iOS / Android) projects, log-mode is the only useful preview. Configure to tail the build/simulator log.
- v2: project-type auto-detection (look for `package.json`, `Cargo.toml`, `Package.swift`, etc.) to suggest a sensible default config.
