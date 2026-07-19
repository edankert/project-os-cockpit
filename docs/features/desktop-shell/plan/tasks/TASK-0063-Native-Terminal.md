---
type: "[[task]]"
id: TASK-0063
aliases: ["TASK-0063"]
title: "Native terminal pane (node-pty + xterm.js) for desktop mode"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: ["[[TASK-0061]]"]
blocks: []
related: ["[[FEAT-0003-Embedded-Terminal]]"]
tests: []
---

# Native terminal pane

## Definition of Done
- [ ] Terminal pane in the desktop shell uses node-pty (main) + xterm.js
      (renderer), not ttyd.
- [ ] Spawned shell's `cwd` is the workspace root.
- [ ] Resize, copy/paste, scrollback all work.
- [ ] Running `claude` / `codex` inside the terminal works identically to
      the ttyd path in mode 1.
- [ ] Mode 1 (browser) unaffected — still uses ttyd because the sidecar in
      browser mode does not see `COCKPIT_DESKTOP=1`.

## Steps
- [ ] Add `node-pty` + `xterm` deps to `desktop/package.json`.
- [ ] `electron/ipc/terminal.ts` — spawn / write / resize / dispose; binary
      IPC framing for the PTY stream.
- [ ] `renderer/terminal.ts` — xterm.js mount; wire to the IPC channel.
- [ ] Inject a `data-cockpit-mode="desktop"` attribute on `<html>` from
      `preload.ts` so the cockpit UI can render a native mount-point in the
      bottom-panel slot instead of the iframe.
- [ ] Update the cockpit UI to honour the attribute (a small change to
      `src/project_os_cockpit/static/cockpit.js` — additive, gated on
      desktop mode).

## Notes
The cockpit's bottom-panel slot is already in place (FEAT-0003 / TASK-0043).
This task replaces only the iframe with a mount-point when running under
the desktop shell. Browser users see no change.
