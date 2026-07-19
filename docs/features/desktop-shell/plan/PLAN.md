---
type: "[[plan]]"
id: PLAN-FEAT-0007
aliases: ["PLAN-FEAT-0007"]
title: "Plan: Electron desktop shell with Python sidecar"
status: draft
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
implements: ["[[FEAT-0007-Desktop-Shell]]"]
related: ["[[ADR-0005-Electron-Plus-Python-Sidecar]]", "[[PHASE-005-Desktop-Shell]]"]
---

# Plan — FEAT-0007 Desktop shell scaffold

## Three preserved usage modes (non-negotiable)

The shell is **additive**, not a replacement. All three modes must keep working
independently and in parallel:

| # | Mode | Install scope | Entry point | Owner of UI |
|---|------|---------------|-------------|-------------|
| 1 | Flask-style direct | Per-project (synced via `tools/scripts/sync-project-os.sh`) | `python -m project_os_cockpit docs/` | Browser |
| 2 | Obsidian Bases | Per-project (`.base` files in `docs/__bases__/`) | Obsidian opens the vault | Obsidian |
| 3 | Electron desktop (new) | System-wide (one `.app`) | Launch app, pick workspace | Electron window |

Modes 1 and 2 must not change. Mode 3 **consumes** mode 1's server as a child
process but is **not** installed per-project. The desktop shell's bundled
Python runtime is separate from any system or per-project Python install.

## Architectural shape

```
┌──────────────────────────────────────────────────────────────────┐
│ Electron app  (project-os-cockpit-desktop)                       │
│                                                                  │
│  ┌──────────────────────────────┐                                │
│  │ Main process (Node)          │   spawns / monitors            │
│  │  - workspace discovery       │ ─────────────────────┐         │
│  │  - sidecar lifecycle         │                      │         │
│  │  - native menu, deep links   │                      │         │
│  │  - auto-update               │                      │         │
│  └──────────────┬───────────────┘                      │         │
│                 │ IPC (contextBridge)                  │         │
│  ┌──────────────▼───────────────┐                      │         │
│  │ Renderer (Chromium)          │                      │         │
│  │  - workspace switcher chrome │                      │         │
│  │  - cockpit UI ──── loadURL ──┼──────────────────────┤         │
│  │  - node-pty terminal pane    │   HTTP / SSE         │         │
│  └──────────────────────────────┘   (loopback)         │         │
└────────────────────────────────────────────────────────┼─────────┘
                                                         │
                                       ┌─────────────────▼──────────┐
                                       │ Python sidecar             │
                                       │ (project_os_cockpit)       │
                                       │  one process per workspace │
                                       │  bundled Python runtime    │
                                       └────────────────────────────┘
```

## Module layout

```
project-os-cockpit/                   ← this repo
  src/project_os_cockpit/             ← UNCHANGED — mode 1 lives here
  docs/__bases__/                     ← UNCHANGED — mode 2 lives here
  desktop/                            ← NEW top-level (mode 3)
    package.json
    tsconfig.json
    forge.config.ts                   ← electron-forge config
    electron/
      main.ts                         ← app lifecycle, window mgmt
      preload.ts                      ← contextBridge surface
      ipc/
        workspaces.ts                 ← discovery + persistence
        sidecar.ts                    ← spawn/health/kill
        terminal.ts                   ← node-pty bridge
        agent-focus.ts                ← receives focus events from sidecar SSE
      sidecar/
        python-runtime.ts             ← resolves bundled python path
        process-pool.ts               ← per-workspace processes, port pool
      windows/
        workspace-window.ts           ← one BrowserWindow per workspace
        chooser-window.ts             ← startup picker (first launch)
      menu/
        app-menu.ts                   ← macOS menu bar
      deeplinks/
        protocol.ts                   ← cockpit:// handler
      updater/
        electron-updater.ts
    renderer/
      index.html                      ← shell chrome (workspace switcher)
      shell.ts                        ← mounts cockpit UI + terminal pane
      switcher.ts                     ← workspace switcher UI
      terminal.ts                     ← xterm.js wire-up
    python-runtime/                   ← python-build-standalone tarball,
                                        unpacked at build time, signed
    build/
      mac/                            ← entitlements.plist
      win/
      linux/
```

The `desktop/` directory is **not** synced to downstream repos.
`tools/scripts/sync-project-os.sh` already operates on an allowlist
(`tools/instructions/`, `tools/skills/`, `docs/__templates__/`,
`docs/__bases__/`) and so excludes `desktop/` by default.

## Workspace discovery model

A "workspace" is any directory containing a `SNAPSHOT.yaml` at its root.

- **Default scan roots**: `~/Dev/repos/`, `~/code/`, `~/work/` — user-editable
  in Preferences.
- **Scan depth**: 2 levels under each root. Skips `node_modules`, `.git`,
  `target`, `dist`, `__pycache__`.
- **Persistence**: `app.getPath('userData')/workspaces.json`, storing
  `{id, root, name, last_opened, pinned}`.
- **Refresh**: re-scan on app launch + on user-triggered "Rescan" menu item.
  No background polling.
- **Manual add**: file picker → validate `SNAPSHOT.yaml` exists at root.
- **Workspace identity**: SHA-1 of the absolute repo path. Stable across
  rescans; survives renames if the user re-points it.

## Sidecar lifecycle contract

Per workspace window:

1. **Allocate port** — `portfinder.getPortPromise()`, range 8765–8865.
2. **Spawn** —
   ```
   spawn(bundledPython,
         ['-m', 'project_os_cockpit', `${workspaceRoot}/docs`,
          '--port', String(port), '--no-open'],
         { cwd: workspaceRoot,
           env: { ...process.env, COCKPIT_DESKTOP: '1' } })
   ```
3. **Wait for ready** — poll `GET http://127.0.0.1:<port>/healthz` (200 = ready),
   timeout 10s. (New endpoint — TASK-0059.)
4. **Load** — `BrowserWindow.loadURL('http://127.0.0.1:<port>')`.
5. **Watch** — capture stderr to a per-workspace log; surface fatal exits as a
   renderer toast.
6. **Shutdown** — on window close or workspace switch, `SIGTERM`, wait 3s,
   `SIGKILL` if still alive.

### Required additions to the Python tool (small, additive)
- `--no-open` — suppress any browser auto-launch.
- `/healthz` — returns 200 once the index is built; 503 before.
- Honour `COCKPIT_DESKTOP=1` — skip `ttyd` spawn and `.cockpit/url` write.
  (The desktop shell drives the terminal natively and routes focus via IPC.)

All three additions land via TASK-0059. None change behaviour for users of
mode 1 — defaults are unchanged.

## IPC surface (renderer ↔ main)

Exposed on `window.cockpit` via `contextBridge`:

```ts
interface CockpitDesktopAPI {
  workspaces: {
    list(): Promise<Workspace[]>
    open(id: string, opts?: { newWindow?: boolean }): Promise<void>
    add(root: string): Promise<Workspace>
    remove(id: string): Promise<void>
    rescan(): Promise<Workspace[]>
  }
  terminal: {
    spawn(opts: { cwd: string; cols: number; rows: number }): Promise<{ id: string }>
    write(id: string, data: string): void
    resize(id: string, cols: number, rows: number): void
    dispose(id: string): void
    onData(id: string, cb: (data: Uint8Array) => void): () => void
    onExit(id: string, cb: (code: number) => void): () => void
  }
  agent: {
    onFocus(cb: (target: string) => void): () => void  // mirrors `cockpit focus`
  }
  app: {
    openExternal(url: string): void
    relaunch(): void
  }
  updater: {
    onAvailable(cb: () => void): () => void
    onDownloaded(cb: () => void): () => void
    quitAndInstall(): void
  }
}
```

The cockpit-focus protocol from FEAT-0006 keeps HTTP/SSE as its substrate.
The main process subscribes to each sidecar's `/_events`, filters
`agent_focus` events, and forwards them to the renderer via `agent.onFocus`.
This means an external `cockpit focus FEAT-0006` invocation still works —
it hits the sidecar's HTTP API, the main process sees the SSE, the renderer
navigates.

## Bundled Python

- **Toolchain**: [python-build-standalone](https://github.com/astral-sh/python-build-standalone).
- **Layout**: one tarball per arch unpacked into `desktop/python-runtime/<arch>/`
  at build time, then bundled inside the `.app` Resources.
- **Why not PyInstaller**: PyInstaller is per-script bundling; we want a
  reusable interpreter that runs an arbitrary command line
  (`-m project_os_cockpit`).
- **Why not system Python**: forks the install story (which version is
  installed? is it on PATH? does it have `venv` support?) and breaks for
  users who don't write Python.
- **Size**: ~30 MB compressed per arch. Acceptable.
- **Signing**: every binary in the runtime must be signed during
  notarization. The build script handles this.

## Native terminal pane

- Renderer uses **xterm.js** for display.
- Main spawns **node-pty** for the PTY.
- Stream binary chunks renderer ↔ main over IPC; never serialise the whole
  stream.
- `ttyd` stays as the terminal backend for **mode 1** (browser). Mode 3 uses
  `node-pty` instead, gated by `COCKPIT_DESKTOP=1` in the sidecar (which
  suppresses the `ttyd` spawn).
- The existing cockpit UI reserves space for a bottom-panel terminal; the
  desktop shell mounts the native pane into the same slot. A small DOM hook
  (e.g. `<html data-cockpit-mode="desktop">` injected by preload) lets the
  cockpit UI know to skip the iframe and surface a mount point.

## OS chrome the category expects

| Concern | Approach |
|---------|----------|
| Menu bar (macOS) | Native via `Menu.setApplicationMenu`. File / View / Window / Help. |
| Single-instance | `app.requestSingleInstanceLock()`. Second launch focuses an existing window or opens the workspace from argv. |
| Deep links | `cockpit://<workspace-id>/<target>` registered via `app.setAsDefaultProtocolClient`. Routes through the agent-focus channel. |
| Notifications | `new Notification(...)` placeholder for agent-turn-end events; wired but unused in v1. |
| Auto-update | `electron-updater` against GitHub Releases for v1. |
| Code signing | Apple Developer ID Application cert + hardened runtime + notarization on macOS; Authenticode on Windows. |
| Window memory | Persist `{x, y, w, h, workspace}` per window in `userData`. |

## Delivery sequence

1. **[[TASK-0058]] — Electron shell scaffold.** `desktop/` directory,
   electron-forge, a `BrowserWindow` that loads `about:blank`. Smoke test:
   `npm run start` opens a window on macOS.
2. **[[TASK-0059]] — Python tool contract additions.** `--no-open`,
   `/healthz`, `COCKPIT_DESKTOP=1` handling. Mode 1 unaffected — proven by
   an explicit TST-* note.
3. **[[TASK-0060]] — Workspace discovery + switcher.** Scan, persist, render
   switcher UI. Picking a workspace dispatches an event; no sidecar yet.
4. **[[TASK-0061]] — Sidecar lifecycle.** Spawn / health-poll / loadURL /
   shutdown. End-to-end milestone: pick a workspace, cockpit renders.
5. **[[TASK-0062]] — Bundled Python runtime.** python-build-standalone,
   build-time unpack, signing inputs.
6. **[[TASK-0063]] — Native terminal pane.** node-pty + xterm.js;
   `COCKPIT_DESKTOP=1` suppresses `ttyd` in the sidecar.
7. **[[TASK-0064]] — App chrome.** Menu, single-instance, deep links,
   window memory, agent-focus SSE bridge to renderer.
8. **[[TASK-0065]] — Build, sign, notarize, distribute.** electron-forge
   makers; macOS DMG (signed + notarized) + Windows + Linux; auto-update
   channel.

## Dependencies

- **Hard:** FEAT-0006 (the sidecar this wraps).
- **Soft:** FEAT-0003 (ttyd) — desktop mode uses node-pty instead; ttyd
  remains for the browser mode.
- **None on PHASE-003 (downstream pilot).** The desktop shell works against
  any repo with a `SNAPSHOT.yaml`, including the pilot, but does not
  require it to be live.

## Open questions to pin during implementation

- **Workspace concurrency.** Keep N sidecars alive (one per recently-opened
  workspace) for instant switching, vs. one at a time. Memory cost is
  ~80 MB per Python process. Likely answer: "one per visible window" + GC
  after idle 10 min. Decided in TASK-0061.
- **Renderer choice for sidecar UI.** A `<webview>` tag is the simplest
  ("load URL, done"), but Electron's `<webview>` has stability caveats.
  Alternative: `BrowserWindow.loadURL` for the whole window and inject the
  switcher chrome via a preload script. Recommend the second — simpler
  IPC, no webview tag. Decided in TASK-0058.
- **Renderer ↔ pty IPC framing.** xterm.js wants UTF-8 strings; node-pty
  emits Buffers. Pick binary IPC channel and decode in renderer, or
  decode in main. Decided in TASK-0063.
- **Distribution channel.** GitHub Releases (free, public) vs private S3
  (private, paid). v1 = GitHub Releases. Revisit if a private build is
  ever needed.
- **Bundled-Python licensing.** python-build-standalone is PSF-licensed
  but bundles OpenSSL, libffi, etc. Confirm aggregate licence is
  compatible with the project's distribution stance. Likely trivial;
  worth a checkbox in TASK-0062.

## Explicit non-goals

- **No agent runtime in the shell (v1).** The user keeps running their
  agent in the terminal pane. A future phase could add an in-shell agent
  pane mirroring Cowork; this scaffold leaves the IPC hooks for it but
  does not build the pane.
- **No sandboxing of the sidecar.** It runs as the user. Filesystem read
  access to `docs/` and the controlled HTTP surface match today's browser
  threat model.
- **No Linux GUI as v1 ship target.** The build pipeline supports Linux;
  QA priority is macOS first, Windows second.
