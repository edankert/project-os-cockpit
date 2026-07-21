---
type: "[[phase]]"
id: PHASE-005
aliases: ["PHASE-005"]
title: "Desktop shell (Electron + Python sidecar)"
status: done
order: 5
owner: user:edwin
created: 2026-05-24
updated: 2026-07-20
features:
  - "[[FEAT-0007-Desktop-Shell]]"
depends: ["[[PHASE-002-Project-OS-Adapter]]"]
---

# Phase 5: Desktop shell (Electron + Python sidecar)

## Goal
Ship a separately-installed desktop application that surfaces project-os-cockpit
across **all** project-os repos on a user's machine — modeled after Claude Cowork,
OpenAI Codex Desktop, and Google Antigravity (all Electron). The shell embeds the
existing Python cockpit as a sidecar process, so all rendering, indexing, SSE, and
project-os-adapter logic stays in one place and is not re-implemented.

## Scope

### In scope
- A new top-level `desktop/` directory in this repo — a separate npm package,
  **not** synced into downstream projects via `tools/scripts/sync-project-os.sh`.
- Electron main + preload + renderer; the existing `project_os_cockpit` Python
  package runs as a child process per active workspace.
- Multi-workspace discovery: scan one or more user-configured roots
  (default `~/Dev/repos/`) for `SNAPSHOT.yaml`; each match becomes a workspace.
- Native terminal pane via `node-pty` (replaces `ttyd` **inside the desktop shell
  only** — `ttyd` remains the terminal backend for the per-project browser mode).
- macOS distribution first (signed DMG + notarized), Windows + Linux follow.
- Bundled Python runtime via `python-build-standalone` so the app installs on
  machines with no Python toolchain.

### Out of scope
- Replacing the per-project Flask-style install. `python -m project_os_cockpit <docs>`
  stays as the lightweight embeddable per-project tool.
- Replacing Obsidian Bases. `.base` files under `docs/__bases__/` remain the source
  of truth for Obsidian's frontmatter-driven views.
- Owning an agent runtime in v1. The shell exposes a native terminal; the user
  runs `claude` / `codex` inside it the same way they do today. A future phase may
  add an in-shell agent pane (Cowork-style) — this scaffold leaves room for it.
- VM-based sandboxing (Cowork's model). The desktop shell runs the sidecar and
  terminal as ordinary user processes; the threat model matches today's browser mode.

## Exit criteria
- A `.app` installs on a clean macOS machine with no Python installed and
  immediately discovers project-os repos under `~/Dev/repos/`.
- Picking a workspace spawns the Python sidecar and renders the existing 3-pane
  cockpit UI inside the Electron window — visually identical to the browser mode.
- The existing `python -m project_os_cockpit ./docs` workflow still works for any
  single repo, unmodified (mode 1 preserved).
- The existing Obsidian Bases (`docs/__bases__/`) still render correctly in
  Obsidian, unmodified (mode 2 preserved).
- An agent running `cockpit focus <id>` from any terminal — including the desktop
  app's own terminal — drives the desktop app's view.

## Dependencies
- PHASE-002 (project-os adapter / cockpit layout) — the sidecar is what PHASE-002
  produced; the shell is a wrapper around it.
- Small additive changes to the Python tool (`--no-open` flag, `/healthz`
  endpoint, `COCKPIT_DESKTOP=1` env var) tracked as TASK-0059. These do not alter
  the Flask-style entry point's defaults.

## Notes
- **Why a new phase, not a feature of an existing one.** The desktop shell is a
  separate install target with its own runtime (Node + Electron + bundled Python),
  its own distribution pipeline (signing, notarization, auto-update), and a
  workspace model that is system-wide rather than per-repo. Milestone-level scope.
- **Three preserved usage modes** (non-negotiable):
  1. Per-project Flask-style direct use (`python -m project_os_cockpit`).
  2. Obsidian Bases via `.base` files.
  3. System-wide Electron desktop (new — this phase).
- **Inspirations and shape.** Claude Cowork is Electron + a local Linux VM that
  hosts Claude Code. OpenAI Codex Desktop is Electron with a non-JS sidecar over
  IPC. Google Antigravity is a VS Code fork (Electron). project-os-cockpit picks
  the **Codex Desktop shape** — Electron + language-foreign sidecar — because the
  existing ~1.6 kloc of Python (renderer, index, SSE, wikilink, project-os
  adapter) is load-bearing and a JS rewrite buys nothing.

## Close-out (2026-07-20)

The Electron desktop shell is complete and closed (FEAT-0007): per-workspace Python sidecar lifecycle, multi-workspace discovery/persistence, native window/menus/deep-links, tmux survivability + quit guard. Distribution (signing/notarization, TASK-0065) is deferred until external sharing matters. No open items remain.
