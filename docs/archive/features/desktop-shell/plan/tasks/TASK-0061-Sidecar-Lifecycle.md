---
type: "[[task]]"
id: TASK-0061
aliases: ["TASK-0061"]
title: "Python sidecar lifecycle (spawn, health-poll, loadURL, shutdown)"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: ["[[TASK-0058]]", "[[TASK-0059]]", "[[TASK-0060]]"]
blocks: ["[[TASK-0063]]", "[[TASK-0064]]"]
related: []
tests: []
---

# Sidecar lifecycle

## Definition of Done
- [ ] Picking a workspace allocates a free port (range 8765–8865 via
      `portfinder`) and spawns a Python sidecar bound to it.
- [ ] Spawn passes `cwd = workspaceRoot` and `env.COCKPIT_DESKTOP = '1'`.
- [ ] Main polls `/healthz` until 200 or 10s timeout; failures surface as a
      renderer toast with the captured stderr tail.
- [ ] On ready, `BrowserWindow.loadURL('http://127.0.0.1:<port>')`.
- [ ] Existing cockpit UI renders inside the Electron window —
      indistinguishable from the browser version.
- [ ] On window close or workspace switch: SIGTERM the sidecar, wait 3s,
      SIGKILL if still alive.
- [ ] Stderr captured to per-workspace log under `userData/logs/`.
- [ ] Decide concurrency policy (one per visible window vs one global)
      and document in this task's Notes.

## Steps
- [ ] `electron/ipc/sidecar.ts` — `spawn(workspace) → { port, kill }`.
- [ ] `electron/sidecar/process-pool.ts` — map window → child process; cleanup.
- [ ] Use `portfinder` for port allocation.
- [ ] Healthz poll util (axios or built-in fetch, 200ms interval, 10s total).
- [ ] Smoke test: pick this repo as a workspace, confirm the cockpit
      renders end-to-end.

## Notes
This is the first end-to-end milestone. After it lands, the shell is a viable
workflow against any one workspace. Until TASK-0062 lands, the spawn uses a
system Python path — fine for development.
