---
type: "[[task]]"
id: TASK-0065
aliases: ["TASK-0065"]
title: "Build pipeline — electron-forge makers, code signing, notarization, auto-update"
status: blocked
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: ["[[TASK-0062]]", "[[TASK-0064]]"]
blocks: []
related: []
tests: []
---

# Build, sign, notarize, distribute

> **Parked 2026-05-25.** Deferred until the desktop app needs to be
> handed to someone other than the developer. The current dev loop
> (`cd desktop && npm start`) covers in-place use. Unblock by:
> setting Apple Developer ID + notarization secrets, then resuming
> with `forge.config.ts` + GitHub Actions workflow.

## Definition of Done
- [ ] `npm run make` produces a signed + notarized macOS DMG.
- [ ] DMG passes Gatekeeper on a clean macOS install.
- [ ] `electron-updater` wired against GitHub Releases (v1).
- [ ] Windows installer (Squirrel.Windows or NSIS) produced — unsigned
      for v1 is acceptable, with a follow-up issue tracking Authenticode.
- [ ] Linux: AppImage or `.deb` (best-effort; does not block macOS ship).
- [ ] `desktop/BUILD.md` documents required secrets (Apple Developer ID,
      notarization API key, GitHub release token).

## Steps
- [ ] `forge.config.ts` — makers per platform.
- [ ] macOS signing: hardened runtime + entitlements;
      `@electron/osx-sign` + `@electron/notarize`.
- [ ] Auto-update config (`electron-updater` + GitHub Releases).
- [ ] End-to-end build on CI (GitHub Actions macos-latest); upload DMG
      artefact for manual smoke test.

## Notes
Signing keys live outside the repo; CI secrets handle them. `BUILD.md`
captures the secrets-required list so future contributors know what's
needed to cut a release.
