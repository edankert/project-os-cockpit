---
type: "[[task]]"
id: TASK-0058
aliases: ["TASK-0058"]
title: "Electron shell scaffold (desktop/ package, BrowserWindow + preload)"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0060]]", "[[TASK-0061]]"]
related: ["[[ADR-0005-Electron-Plus-Python-Sidecar]]"]
tests: []
---

# Electron shell scaffold

## Definition of Done
- [ ] `desktop/` directory exists with an electron-forge TypeScript project.
- [ ] `npm run start` from `desktop/` opens an Electron window on macOS.
- [ ] Window can `BrowserWindow.loadURL(<arbitrary-url>)`.
- [ ] `preload.ts` exposes an empty `window.cockpit` placeholder via `contextBridge`.
- [ ] `desktop/` is excluded from `tools/scripts/sync-project-os.sh` (verify the
      allowlist does not pick it up).

## Steps
- [ ] `cd desktop && npx create-electron-app@latest . --template=typescript`.
- [ ] Strip the scaffold's renderer to a minimal `index.html` + `shell.ts`.
- [ ] Add `electron/main.ts` that creates a single `BrowserWindow` and loads a
      placeholder URL (`about:blank` is fine).
- [ ] Add `preload.ts` with an empty `contextBridge.exposeInMainWorld('cockpit', {})`.
- [ ] Confirm by inspection that `tools/scripts/sync-project-os.sh` does not
      include `desktop/` in its sync paths.

## Notes
This is the bare floor. Subsequent tasks add workspace discovery, sidecar
spawning, terminal, chrome, and distribution. No chrome customisation here.
Pick the recommended option from the plan: load the workspace URL into the
whole `BrowserWindow` and inject switcher chrome via preload — not `<webview>`.
