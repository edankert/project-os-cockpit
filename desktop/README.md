# project-os-cockpit-desktop

Electron shell for [project-os-cockpit](../). Wraps the existing Python
cockpit as a sidecar and surfaces every project-os repo on the system
through one native window. See `../docs/features/desktop-shell/` for the
plan, tasks, and ADR.

## Status

Scaffold milestone (TASK-0058 → TASK-0061). Pre-review.

| Task | Status | What lands |
|------|--------|-----------|
| TASK-0058 | shipped | `desktop/` package, Electron main + preload + renderer |
| TASK-0059 | shipped | Python contract (`--no-open`, `/healthz`, `COCKPIT_DESKTOP=1`) |
| TASK-0060 | shipped | Workspace discovery + switcher UI |
| TASK-0061 | shipped | Python sidecar lifecycle |
| TASK-0062..0065 | not started | bundled Python, native terminal, app chrome, signed distribution |

## Develop

Requires Node 20+ and Python 3.11+. The Python tool (the sidecar) must
be installed in a venv reachable from `python3` for now — TASK-0062
bundles its own runtime.

```sh
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# from desktop/
cd desktop
npm install
npm start            # build (tsc + asset copy) + launch Electron
```

## Layout

```
desktop/
  package.json
  tsconfig.json
  scripts/
    copy-assets.mjs              # tsc only emits .js; we copy HTML + CSS
  src/
    main.ts                      # Electron main process
    preload.ts                   # contextBridge → window.cockpit
    ipc/
      workspaces.ts              # workspace discovery + persistence
      sidecar.ts                 # spawn / healthz-poll / kill the Python sidecar
    renderer/
      index.html
      renderer.ts                # switcher + sidecar mount
      renderer.css
  dist/                          # tsc output + copied assets (gitignored)
```

## What's deliberately not here

- No bundler (Vite / webpack). Electron loads `dist/main.js` directly;
  the renderer uses a plain `<script src="renderer.js">`.
- No bundled Python (TASK-0062).
- No native terminal pane (TASK-0063).
- No menu / single-instance / deep links / window memory (TASK-0064).
- No build / sign / notarize / auto-update (TASK-0065).
