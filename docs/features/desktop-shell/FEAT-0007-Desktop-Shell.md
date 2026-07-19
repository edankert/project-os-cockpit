---
type: "[[feature]]"
id: FEAT-0007
aliases: ["FEAT-0007"]
title: "Electron desktop shell (multi-project, Python sidecar)"
status: in-progress
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
goal: "Wrap the existing Python cockpit in an Electron app that can be pointed at all project-os repos on a system — without breaking the per-project Flask-style install or the Obsidian Bases workflow."
related: ["[[FEAT-0003-Embedded-Terminal]]", "[[FEAT-0006-Cockpit-Layout]]", "[[ADR-0005-Electron-Plus-Python-Sidecar]]"]
requirements: []
tasks: ["[[TASK-0058]]", "[[TASK-0059]]", "[[TASK-0060]]", "[[TASK-0061]]", "[[TASK-0062]]", "[[TASK-0063]]", "[[TASK-0064]]", "[[TASK-0065]]"]
release: ""
tests: []
---

# Electron desktop shell

## Goal
A standalone macOS/Windows/Linux desktop application — installed once
system-wide — that can be pointed at any project-os repo on the user's machine
and renders the existing 3-pane cockpit inside a native window. Built on
Electron with a Python sidecar (the existing `project_os_cockpit` package),
matching the shape of Claude Cowork, OpenAI Codex Desktop, and Google
Antigravity.

## Scope

### In scope
- Electron shell — main process, preload, renderer, IPC.
- Python sidecar lifecycle — spawn one `project_os_cockpit` process per active
  workspace; manage port allocation, health, and shutdown.
- Workspace discovery — scan configurable roots (default `~/Dev/repos/`) for
  `SNAPSHOT.yaml`; persist the list per user.
- Workspace switcher — left rail or top picker; switching tears down the
  current sidecar and starts a new one (or keeps N alive for fast switch).
- Renderer loads `http://localhost:<sidecar-port>` directly — reuses 100% of
  the existing cockpit UI; no UI re-implementation.
- Native terminal pane — `node-pty` replaces `ttyd` inside the desktop shell
  (the `ttyd` path remains for the per-project browser mode).
- Bundled Python runtime — `python-build-standalone` so the app installs on
  machines without Python.
- Native menus, single-instance lock, deep links (`cockpit://<workspace>/<target>`),
  notifications, auto-updater (`electron-updater`).
- Code signing + notarization for macOS distribution.

### Out of scope (v1)
- An in-shell agent-conversation pane (Cowork-style). The user keeps running
  `claude` / `codex` in the terminal pane.
- VM-based sandbox (Cowork-style). Not needed until a use case requires it.
- Editing notes from the renderer. The cockpit remains a viewer; editing
  happens in the user's editor (Obsidian, VS Code, Cursor).
- Replacing the Flask-style entry point. The Python tool keeps its CLI
  exactly as is; the desktop shell consumes it as a child process.
- Replacing the Obsidian Bases workflow.

## Acceptance
- Install the `.app`, launch, see a workspace picker populated by scanning
  `~/Dev/repos/` for `SNAPSHOT.yaml` files.
- Pick a workspace; the existing cockpit UI renders inside the Electron
  window, indistinguishable from the browser version.
- Open another workspace in a new window (⌘N) — both run independent sidecars
  on different ports without interfering.
- Run `python -m project_os_cockpit ./docs` from a terminal in the same repo —
  works unchanged.
- Open the repo in Obsidian — `.base` views render unchanged.
- Run `cockpit focus FEAT-0006` from any terminal — the focused desktop
  window navigates.
- App passes macOS Gatekeeper (signed + notarized).

## Links
- Framework choice + tradeoffs: [[ADR-0005-Electron-Plus-Python-Sidecar]]
- Sidecar this wraps: [[FEAT-0006-Cockpit-Layout]]
- Existing browser-terminal it replaces in desktop mode: [[FEAT-0003-Embedded-Terminal]]
- Implementation plan: see `plan/PLAN.md`
