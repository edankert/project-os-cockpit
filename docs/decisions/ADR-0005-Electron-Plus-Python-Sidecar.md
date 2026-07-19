---
type: "[[adr]]"
id: ADR-0005
aliases: ["ADR-0005"]
title: "Desktop shell: Electron + Python sidecar (additive, multi-project)"
status: accepted
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
decision: "Build the desktop shell as an Electron app that spawns the existing Python cockpit as a sidecar. Install once system-wide; discover all project-os repos via SNAPSHOT.yaml. Do not replace the Flask-style or Obsidian Bases entry points."
context: "The per-project browser cockpit works well, but the user wants a desktop-app experience comparable to Claude Cowork, OpenAI Codex Desktop, and Google Antigravity. All three are Electron; Codex Desktop in particular pairs Electron with a non-JS sidecar over IPC — the same shape this codebase is best positioned for."
alternatives: ["Tauri + Python sidecar", "Native shell (Swift on macOS) + Python sidecar", "Rewrite the cockpit in TypeScript and ship as pure Electron", "PyWebView wrapping the existing Flask server"]
consequences: ["Adds Node + Electron toolchain to the repo, in `desktop/` only — not synced downstream", "Bundled Python runtime (~30 MB per arch) ships inside the .app", "Distribution requires Apple Developer ID + notarization on macOS", "The Python tool gains a small additive contract (`--no-open`, `/healthz`, `COCKPIT_DESKTOP` env var) — no breaking changes to mode 1", "Per-project install (mode 1) and Obsidian Bases (mode 2) remain authoritative and untouched"]
related: ["[[FEAT-0007-Desktop-Shell]]", "[[PHASE-005-Desktop-Shell]]"]
---

# Desktop shell: Electron + Python sidecar (additive, multi-project)

## Context

The project ships a working Flask-style cockpit that renders project-os docs
in a browser, plus an Obsidian Bases workflow for frontmatter-driven views.
Comparable desktop tools — Claude Cowork, OpenAI Codex Desktop, Google
Antigravity — give users a native window experience the browser cannot
match, and they have set user expectations for what an "agent IDE" looks
like.

All three are Electron. Cowork wraps Claude Code inside a local Linux VM;
Codex Desktop wraps the agent in a separate sidecar process over IPC;
Antigravity is a VS Code fork. The closest fit for project-os-cockpit is
the **Codex Desktop shape** — Electron + language-foreign sidecar — because
the existing renderer / index / SSE / wikilink / project-os-adapter logic
is ~1.6 kloc of Python we do not want to reimplement.

## Decision

1. **Electron** for the shell. Matches the category, gives Chromium as a
   stable rendering substrate, and lets us reuse 100% of the existing web
   UI by loading the sidecar URL directly into a `BrowserWindow`.
2. **Python sidecar** — the existing `project_os_cockpit` package — spawned
   as a child process per active workspace. No JS rewrite of the renderer.
3. **System-wide install, multi-project model.** The desktop app is
   installed once and discovers all project-os repos (any directory with a
   `SNAPSHOT.yaml`) under user-configured roots. It does **not** ride
   along with the per-project `tools/scripts/sync-project-os.sh` pipeline.
4. **Three preserved usage modes** — Flask-style direct (mode 1), Obsidian
   Bases (mode 2), Electron desktop (mode 3) — must all work independently.
   The shell consumes the sidecar via HTTP; it does not depend on or alter
   Bases or the per-project install.
5. **Bundled Python runtime** via python-build-standalone. The user does
   not need any Python toolchain to run the desktop app.

## Alternatives

- **Tauri + Python sidecar.** Smaller binary, modern Rust toolchain.
  *Rejected:* the category standard is Electron — verisimilitude with
  Cowork / Codex / Antigravity is an explicit product goal — and Tauri's
  Rust shell adds a build dependency the team does not use elsewhere.
- **Native shell (Swift / SwiftUI) + Python sidecar.** Best macOS feel.
  *Rejected:* triples the platform surface (one UI codebase per OS) and
  abandons reuse of the existing web UI.
- **Rewrite the cockpit in TypeScript, pure Electron, no Python.**
  Cleanest single-language app. *Rejected:* the existing Python logic is
  load-bearing and a JS rewrite buys no product gain, only risk.
- **PyWebView wrapping the existing Flask server.** Lightest option, no
  Node toolchain. *Rejected:* the OS chrome the category demands (menu
  bar, deep links, auto-update, signed distribution, native terminal) is
  friction-heavy in PyWebView and first-class in Electron.

## Consequences

- New top-level `desktop/` directory; Node + Electron toolchain in-repo.
  Not synced to downstream projects (the sync script's allowlist already
  excludes it).
- Bundled Python runtime adds ~30 MB per arch to the installer.
- macOS distribution requires Apple Developer ID + notarization workflow.
  Windows requires Authenticode (deferred to a follow-up if needed).
- The Python tool gains three additive surface points (`--no-open` flag,
  `/healthz` endpoint, `COCKPIT_DESKTOP` env var). The Flask-style entry
  point keeps its current default behaviour without any of them.
- The cockpit-focus protocol (FEAT-0006) keeps HTTP / SSE as its
  substrate. The Electron main process subscribes to the sidecar's SSE
  and forwards `agent_focus` events to the renderer — so an external
  `cockpit focus FEAT-0006` invocation still drives the desktop window.
- Leaves the door open for a future in-shell agent-conversation pane
  (Cowork-style) without re-architecting the shell.
