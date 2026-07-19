---
type: "[[change]]"
id: CHG-20260524-Desktop-Shell-Scaffold
aliases: ["CHG-20260524-Desktop-Shell-Scaffold"]
title: "Desktop shell scaffold — Electron + Python sidecar, multi-project workspace switcher"
status: merged
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: ["[[TASK-0058]]", "[[TASK-0059]]", "[[TASK-0060]]", "[[TASK-0061]]"]
commit: ""
pr: ""
impacts:
  - "desktop/ (new top-level directory — Electron + TypeScript)"
  - "src/project_os_cockpit/__main__.py"
  - "src/project_os_cockpit/server.py"
  - "src/project_os_cockpit/terminal.py"
  - "tests/test_sidecar_contract.py (new)"
  - "docs/features/desktop-shell/plan/tests/TST-0004-Sidecar-Contract.md (new)"
issues: []
features: ["[[FEAT-0007]]"]
related: ["[[ADR-0005-Electron-Plus-Python-Sidecar]]", "[[PHASE-005-Desktop-Shell]]"]
---

# Desktop shell scaffold

## Summary

Lands the first four tasks of PHASE-005 / FEAT-0007 — the architectural
backbone of the Electron desktop shell modeled after Claude Cowork /
OpenAI Codex Desktop / Google Antigravity. **Smoke-tested live by the
user 2026-05-24:** the end-to-end milestone (pick a workspace →
cockpit renders inside an Electron window) works. 9 project-os repos
under `~/Dev/repos/` were discovered automatically; clicking a row
spawns the Python sidecar and renders the existing 3-pane cockpit in
the Electron window. The remaining four tasks (bundled Python, native
terminal, app chrome, signed distribution) are unscaffolded.

The three preserved usage modes are intact:

1. **Per-project Flask-style direct** (`python -m project_os_cockpit ./docs`) —
   defaults unchanged; the new contract additions only activate when the
   `COCKPIT_DESKTOP=1` env var is set.
2. **Obsidian Bases** (`docs/__bases__/`) — untouched.
3. **Electron desktop** (new) — separate `desktop/` package, not synced
   to downstream projects.

## What landed

### TASK-0058 — Electron shell scaffold (`desktop/`)
- `desktop/package.json`, `desktop/tsconfig.json`, `desktop/.gitignore`,
  `desktop/README.md`.
- `desktop/scripts/copy-assets.mjs` — copies HTML + CSS to `dist/` after
  tsc emits `.js`.
- `desktop/src/main.ts` — Electron main: single `BrowserWindow`, preload
  wiring, sidecar shutdown on quit.
- `desktop/src/preload.ts` — `contextBridge.exposeInMainWorld('cockpit', …)`
  surface: `workspaces.{list, rescan, open}`, `sidecar.onEvent`.
- `desktop/src/types.ts` — shared `Workspace` / `Sidecar*Payload` types.
- `desktop/src/renderer/{index.html,renderer.css,renderer.ts}` — workspace
  switcher chrome + iframe mount-point for the sidecar URL.

### TASK-0059 — Python sidecar contract (additive, mode-1 untouched)
- `__main__.py` — new `--no-open` flag (no-op today; reserved for forward
  compat with any future browser auto-launch).
- `server.py`:
  - new `_desktop_mode()` helper reading `COCKPIT_DESKTOP`;
  - new `GET /healthz` route returning
    `{ok, service, schema, docs_root, desktop_mode}` — used by the
    Electron sidecar lifecycle to confirm "this is our sidecar" before
    loading its URL into the window;
  - `_write_discovery_file()` skipped in desktop mode (the Electron
    shell drives focus via IPC, not the `.cockpit/url` hint).
- `terminal.py`:
  - `is_available()` returns False in desktop mode even if ttyd is on
    PATH;
  - `info()` returns a specific "desktop mode" reason rather than the
    misleading `brew install ttyd` install hint.
- `tests/test_sidecar_contract.py` — 10 tests, all passing
  (TST-0004 documents intent).
- Full suite: 87 passed + 1 skipped (was 77 + 1).

### TASK-0060 — Workspace discovery + switcher UI
- `desktop/src/ipc/workspaces.ts`:
  - Scans default roots (`~/Dev/repos/`) depth-2 for `SNAPSHOT.yaml`;
    skips `node_modules`, `.git`, `__pycache__`, `.venv`, etc.
  - Persists to `app.getPath('userData')/workspaces.json`.
  - IPC: `workspaces:list` (lazy load), `workspaces:rescan`.
  - Workspace ID = SHA-1 prefix of absolute repo path; carries
    `lastOpened` and `pinned` across rescans.
- `desktop/src/renderer/renderer.ts` — switcher list, active-row
  highlight, rescan button, empty state.

### TASK-0061 — Sidecar lifecycle
- `desktop/src/ipc/sidecar.ts`:
  - `portfinder.getPortPromise({port:8765, stopPort:8865})`.
  - `spawn(python, ['-m','project_os_cockpit', '<docs>',
    '--port','--bind 127.0.0.1','--no-open'],
    env: {COCKPIT_DESKTOP:'1', PYTHONUNBUFFERED:'1'})`.
  - 10-second `/healthz` poll (200 ms interval); failure surfaces stderr
    tail to the renderer as a `sidecar:event` 'failed' message.
  - One sidecar per window; switching workspace kills the previous child
    cleanly (SIGTERM → 3 s → SIGKILL).
  - `shutdownAllSidecars()` runs on `before-quit`.
- Python interpreter resolved via `COCKPIT_DESKTOP_PYTHON` env var
  (development override, e.g. `.venv/bin/python`) → fallback `python3`.
  TASK-0062 will bundle the runtime.

## Out of scope (intentional)
- TASK-0062 — bundled python-build-standalone runtime.
- TASK-0063 — native node-pty terminal pane (the cockpit's bottom-panel
  slot is currently empty in desktop mode; the sidecar's `/api/terminal`
  reports `enabled: false` with reason "desktop mode").
- TASK-0064 — menu bar, single-instance lock, `cockpit://` deep links,
  agent-focus SSE bridge, window-state persistence.
- TASK-0065 — electron-forge makers, code signing, notarization,
  auto-update.

## Smoke test — verified 2026-05-24

Run:
```sh
# repo root — install Python deps if not already
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# desktop/
cd desktop
npm install --cache "$(pwd)/.npm-cache"   # local cache works around any ~/.npm perm issues
COCKPIT_DESKTOP_PYTHON="$(pwd)/../.venv/bin/python" npm start
```

Observed: Electron window opens; left-rail switcher lists 9
workspaces discovered under `~/Dev/repos/`; clicking a row spawns a
Python sidecar and renders the existing 3-pane cockpit in the
iframe.

## Smoke-test bug fixed mid-session

First launch landed an empty workspace switcher. Root cause: tsc
compiled `renderer.ts` with CommonJS module wrappers (`exports.x =
...`) because the file had `import` / `export` statements; loaded as
a plain `<script>` in the renderer, the first line threw
`ReferenceError: exports is not defined` and the script never ran.

Fix: removed all `import` / `export` statements from `renderer.ts`
and inlined the shared types. The renderer compiles to a plain top-
level script with no module wrapper. A proper fix (separate
tsconfig.renderer.json with `module: ESNext` + `<script
type="module">`) is deferred to TASK-0063 / TASK-0064.

Also added during the debug pass:
- Main-process console mirroring for renderer messages
  (`webContents.on('console-message')`).
- Auto-open of DevTools (`mode: 'detach'`) during scaffold review.
  Drop in TASK-0064 when the proper app menu lands.
- Diagnostic logging in `workspaces.ts` (`[workspaces] scanning
  root…`, `[workspaces] returning N workspace(s)`). Useful for
  TASK-0060 dev-loop; keep until that task is closed.

## Documentation Coverage
- features: covered (FEAT-0007 status → `in-progress`)
- requirements: not-applicable (none added; existing REQs unaffected)
- tasks: TASK-0058..0061 status → `done` (smoke-tested live by user)
- issues: not-applicable
- tests: TST-0004 added (status `passing`)
- workflows: not-applicable
- decisions: ADR-0005 already accepted in prior turn
- risks: not-applicable (no new RISK — the sidecar runs as the user,
  matching today's threat model; bundled Python licensing audit lives
  in TASK-0062)
- changes: new (this note)
- snapshot: updated (FEAT-0007 → `in-review`, PHASE-005 → `active`,
  TASK-0058..0061 → `doing`, TST counter 3 → 4, TST-0004 added to
  items.tests, metrics bumped, focus moved to TASK-0061 / FEAT-0007 /
  PHASE-005)
