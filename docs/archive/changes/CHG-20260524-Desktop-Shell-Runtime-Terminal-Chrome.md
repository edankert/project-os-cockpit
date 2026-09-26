---
type: "[[change]]"
id: CHG-20260524-Desktop-Shell-Runtime-Terminal-Chrome
aliases: ["CHG-20260524-Desktop-Shell-Runtime-Terminal-Chrome"]
title: "Desktop shell: bundled Python runtime, native terminal pane, app chrome"
status: merged
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: ["[[TASK-0062]]", "[[TASK-0063]]", "[[TASK-0064]]"]
commit: ""
pr: ""
impacts:
  - "desktop/scripts/fetch-python.mjs (new)"
  - "desktop/python-runtime/ (new — gitignored)"
  - "desktop/scripts/copy-assets.mjs (vendored xterm)"
  - "desktop/src/ipc/sidecar.ts (bundled-python resolver + agent-focus hook-up)"
  - "desktop/src/ipc/terminal.ts (new — node-pty backend)"
  - "desktop/src/ipc/agent-focus.ts (new — SSE bridge)"
  - "desktop/src/window-state.ts (new — bounds persistence)"
  - "desktop/src/main.ts (menu, single-instance, deep links, window state)"
  - "desktop/src/preload.ts (terminal/menu/agent/deeplink surface)"
  - "desktop/src/renderer/index.html (terminal pane + xterm scripts)"
  - "desktop/src/renderer/renderer.css (terminal styles + footer)"
  - "desktop/src/renderer/renderer.ts (xterm mount, IPC wire-up, divider drag, menu listeners)"
  - "desktop/package.json (deps: node-pty, @xterm/*, @electron/rebuild; script: fetch-python)"
  - "desktop/.gitignore (python-runtime/, .npm-cache/)"
issues: []
features: ["[[FEAT-0007]]"]
related: ["[[CHG-20260524-Desktop-Shell-Scaffold]]", "[[ADR-0005-Electron-Plus-Python-Sidecar]]"]
---

# Desktop shell: bundled Python, native terminal, app chrome

## Summary

Three follow-on tasks land on top of the scaffold:

- **TASK-0062** ships a bundled python-build-standalone runtime
  (Python 3.13.1, ~15 MB compressed per arch). After `npm run
  fetch-python` the Electron sidecar lifecycle resolves the
  interpreter automatically — no system Python needed.
- **TASK-0063** adds a native terminal pane (node-pty backend +
  xterm.js frontend) with vertical drag-resize, Cmd+\` toggle, and
  workspace-aware cwd.
- **TASK-0064** layers on app chrome: macOS menu bar (File / Edit /
  View / Window / Help), single-instance lock, `cockpit://`
  protocol registration, window position/size persistence, and an
  agent-focus SSE bridge that brings the window forward when an
  external `cockpit focus <id>` call fires.

All three preserved usage modes still hold — none of these changes
touch the Flask-style per-project entry point or Obsidian Bases.

## TASK-0062 — Bundled Python

`desktop/scripts/fetch-python.mjs`:
- Pins `cpython-3.13.1+20250115` from astral-sh/python-build-standalone.
- Auto-detects platform/arch (`darwin-arm64`, `darwin-x64`,
  `linux-x64`, `win32-x64`).
- Downloads + extracts to `desktop/python-runtime/<platform-arch>/`.
- `pip install -e <repo-root>` into the bundled interpreter so dev
  changes to `src/` are picked up immediately.
- Verifies by importing `project_os_cockpit` from the bundled python.

`desktop/src/ipc/sidecar.ts` resolution order:
1. `COCKPIT_DESKTOP_PYTHON` env var (explicit override, e.g.
   `.venv/bin/python` during dev).
2. Bundled `python-runtime/<arch>/python/bin/python3` (or
   `python.exe` on Windows) under `app.getAppPath()` or
   `process.resourcesPath`.
3. System `python3` as last resort.

Smoke test: `python-runtime/darwin-arm64/python/bin/python3 -m
project_os_cockpit --help` prints the CLI usage cleanly.

## TASK-0063 — Native terminal

`desktop/src/ipc/terminal.ts` owns the PTY (one per BrowserWindow):
- `terminal:spawn` accepts `{cwd, cols, rows}`; defaults `cwd` to
  the active workspace's root, else `$HOME`.
- `terminal:input` / `terminal:resize` are fire-and-forget `on`
  channels (renderer doesn't need replies on keystroke).
- `terminal:data` / `terminal:exit` push from main → renderer.
- `shutdownAllTerminals()` runs on `before-quit`.

Renderer:
- Lazy-instantiates `Terminal` + `FitAddon` on first toggle.
- `xterm.js` + `xterm.css` + `addon-fit.js` are copied into
  `dist/renderer/` as UMD by `copy-assets.mjs` and loaded via
  `<script>` tags. (The renderer is a non-module script — see the
  scaffold change-note for why.)
- Divider drag updates `terminalPane.style.height` between 80 px and
  `innerHeight - 120`; `fitAddon.fit()` runs on mouseup + on
  window resize.
- Theme matches the existing browser-mode ttyd theme (muted greyscale
  on dark, semantic ANSI colours).

Cmd+\` toggles via both the View → Toggle Terminal menu accelerator
(TASK-0064) and a renderer-side `keydown` listener (fallback).

## TASK-0064 — App chrome

`desktop/src/main.ts`:
- `app.requestSingleInstanceLock()`: second launches focus the
  existing window and forward `cockpit://…` argv via the
  `second-instance` event.
- `app.setAsDefaultProtocolClient('cockpit')` + `open-url` (macOS)
  + `second-instance` argv parsing (Windows/Linux) routes through
  `handleDeepLink(url)`. Sends `deeplink` to the renderer; the
  renderer parses `cockpit://<workspace-id>/<target>` and opens the
  workspace.
- `setWindowOpenHandler` deflects non-loopback links to
  `shell.openExternal` (keeps the iframe's in-cockpit nav intact;
  external links open in the user's browser).
- Native menu: File / Edit / View / Window / Help with standard
  roles + Toggle Terminal (Cmd+\`) and Rescan Workspaces
  (Cmd+Shift+R) → IPC to the renderer.

`desktop/src/window-state.ts`:
- `loadWindowState()` reads `userData/window-state.json` for
  `{x, y, width, height}`, falling back to 1400 × 900.
- `attachWindowStatePersistence()` debounces resize+move writes
  (250 ms) and saves on close.

`desktop/src/ipc/agent-focus.ts`:
- After `sidecar:ready`, `subscribeAgentFocus(window, url)` opens an
  `http.get` against `<sidecar>/_events` and parses the SSE stream
  by hand (Node has no native EventSource).
- On `event: cockpit:focus`, the main process brings the window
  forward (`restore` + `show` + `focus`) and forwards the event
  payload to the renderer as `agent:focus`.
- `unsubscribeAgentFocus(window)` runs on workspace switch / window
  close — torn down by `killSidecarFor` in `sidecar.ts`.

## Smoke-test — partial

Run:
```sh
cd desktop
npm install --cache "$(pwd)/.npm-cache"
npm run fetch-python      # one-time per machine; ~1.5 s download
npm start                 # no env var needed — bundled python kicks in
```

**Verified by Claude:**
- `npm run build` passes cleanly.
- `python-runtime/darwin-arm64/python/bin/python3 -m
  project_os_cockpit --help` works.
- Electron launches without errors; renderer logs `got 9 workspaces`.

**TASK-0063 verified by user 2026-05-24** — terminal opens, accepts
input, drag-resizes.

**TASK-0064 still needs your eyes (status `doing` until confirmed):**
native menu bar shows (File / Edit / View / Window / Help);
Cmd+Shift+R triggers Rescan; Cmd+\` from the menu toggles the
terminal; window position remembers across launches; opening
`cockpit://<id>/whatever` from another terminal brings the window
forward.

## Terminal bug fixed mid-session

First click on the Terminal button opened an empty pane that
swallowed all keystrokes. Root cause: the `@xterm/addon-fit` UMD
build assigns its module object to `window.FitAddon`, so the actual
class lives at `window.FitAddon.FitAddon` — but `@xterm/xterm`'s UMD
assigns each named export *directly* to `window`, so `Terminal` is
already a class. Asymmetric shapes; `new FitAddon()` threw
`TypeError: FitAddon is not a constructor`, the error rejected
the `ensureTerminal()` promise, and `term.onData` never got wired
up.

Fix: changed `new FitAddon()` → `new FitAddon.FitAddon()` and
updated the ambient TypeScript declaration to reflect the namespace
shape.

## Documentation Coverage
- features: covered (FEAT-0007 stays `in-progress` — TASK-0065 still
  open)
- requirements: not-applicable
- tasks: TASK-0062 → `done`; TASK-0063, TASK-0064 → `doing`
- issues: not-applicable
- tests: not-applicable (no automated tests yet for the desktop side
  — TASK-0065 may add one; the Python contract retains TST-0004)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable (bundled-Python license audit deferred to
  TASK-0065's signing/distribution pass)
- changes: new (this note)
- snapshot: updated (counters unchanged, statuses + focus shifted to
  TASK-0064, tasks_done 58 → 59)
