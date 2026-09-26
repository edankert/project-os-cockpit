---
type: "[[task]]"
id: TASK-0062
aliases: ["TASK-0062"]
title: "Bundled Python runtime (python-build-standalone)"
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
blocks: ["[[TASK-0065]]"]
related: []
tests: []
---

# Bundled Python runtime

## Definition of Done
- [ ] python-build-standalone tarball downloaded + checksum-verified for each
      target arch (macOS arm64, macOS x86_64, Windows x64, Linux x64).
- [ ] Build script unpacks the tarball into `desktop/python-runtime/<arch>/`
      and installs `project_os_cockpit` (and deps) into a venv inside it.
- [ ] Spawned sidecar uses the bundled interpreter — no PATH lookup.
- [ ] App launches on a clean macOS VM with no Python installed and
      discovers + opens workspaces.
- [ ] License audit recorded — confirm aggregate (PSF + bundled libs) is
      compatible with distribution.

## Steps
- [ ] Pin a python-build-standalone release tag.
- [ ] Build hook downloads + unpacks per-arch into `desktop/python-runtime/`.
- [ ] `pip install -e ../src/project_os_cockpit` into the bundled venv at
      build time.
- [ ] `electron/sidecar/python-runtime.ts` resolves the bundled interpreter
      path relative to `app.getAppPath()`.
- [ ] All bundled binaries (libffi, openssl, etc.) get signed in the
      codesign step (the codesign work lands in TASK-0065).

## Notes
Heaviest task in the phase. The clean-machine acceptance criterion is the
proof. PyInstaller is **not** the right tool here — we want a reusable
interpreter that runs an arbitrary command line, not a single bundled script.
