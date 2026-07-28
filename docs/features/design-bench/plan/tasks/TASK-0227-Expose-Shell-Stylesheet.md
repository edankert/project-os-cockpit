---
type: "[[task]]"
id: TASK-0227
aliases: ["TASK-0227"]
title: "Expose the shell stylesheet to design artifacts"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[DES-0002-Cockpit-Design-System]]", "user decision 2026-07-28"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "S"
depends: []
blocks: ["[[TASK-0228-Living-Style-Guide]]"]
related: ["[[ISS-0023-Status-Vocabulary-Drift]]"]
tests: []
---

# Expose the shell stylesheet to design artifacts

## Why

A design artifact is served from the **sidecar** origin (`/design-asset/...`), so a `<link>` inside it resolves against the sidecar. The sidecar serves `/_static/base.css` and `/_static/cockpit.css` from the Python package — but `renderer.css`, which styles every widget in the desktop shell, lives in `desktop/dist/renderer/` and the sidecar has never heard of it.

Without it, [[TASK-0228]] can show the palette, typography and spacing (all in `base.css`/`cockpit.css`) but every widget example would be unstyled markup. The Widgets table is the most valuable thing in [[DES-0002]] — five components whose stated property is "distinguishable **without colour**" — and that claim is only testable when the widgets are actually styled.

## The constraint that shapes it

**The sidecar runs without the desktop app.** Mode-1 is a browser cockpit with no Electron and no `desktop/dist/`. So this cannot be a hard dependency, and copying `renderer.css` into the package's static dir would create a second copy of a stylesheet — the [[ISS-0023]] failure, in a new place.

## Definition of Done

- [x] The sidecar takes an optional path to the shell's built renderer assets and serves the stylesheet from it — evidence: `--shell-assets`; `DocsServer(shell_assets=…)`; route `/_shell/<file>`; `test_the_shell_stylesheet_is_served_when_the_path_is_given`
- [x] The desktop passes that path when it spawns the sidecar; nothing else changes for mode-1 — evidence: `shellAssetsPath()` in `sidecar.ts`, derived from `__dirname` — the same base `main.ts` loads the window from; `test_the_desktop_passes_the_path_and_derives_it_once`
- [x] When the path is absent or the file is missing, the route 404s cleanly rather than erroring — evidence: `test_mode_1_degrades_to_404_rather_than_erroring`, which also asserts the rest of the server is unaffected
- [x] A page that depends on it **says so** when it is unavailable, rather than silently rendering unstyled widgets that look like a design regression — evidence: carried into [[TASK-0228]]'s DoD, where the page that depends on it lives
- [x] Traversal and escape are refused, matching `_serve_static`'s existing guards, and a test asserts it over HTTP — evidence: `test_traversal_and_escape_are_refused` over real HTTP, including `..`, encoded `..`, empty and nested paths
- [x] No copy of `renderer.css` is created anywhere — the file is served from where the build already puts it — evidence: `test_no_copy_of_the_stylesheet_is_made` asserts the package static dir stays clean

## Steps

- [x] CLI flag + a route beside `_serve_static`, reusing its traversal guards rather than writing new ones
- [x] Pass the flag from `desktop/src/ipc/sidecar.ts`
- [x] Test the absent case, the present case, and traversal, over real HTTP

## Result

**An allow-list, not a directory share.** The DoD asked only that the stylesheet be served; serving the directory would have satisfied it while also exposing `renderer.js` and its source maps. `SHELL_ASSET_FILES` is a frozenset of exactly one name, and a test asserts the bundle and its map are refused. The design surface needs a stylesheet, and nothing about that is a reason to publish the build.

The traversal guards are `_serve_static`'s, reused rather than re-derived — this route must not become the one place the check was written slightly differently. Verified over real HTTP against `..`, percent-encoded `..`, an empty path and a nested one.

A bad `--shell-assets` path warns and continues rather than refusing to start: the capability is optional by design, and a tool that will not open because an optional extra is missing is worse than one that quietly does less.

## Notes

Serve, never copy. The whole reason this task exists rather than a two-line `cp` in the build is that a second copy of a stylesheet is exactly the drift this project was founded on ([[ISS-0023]]), and the design system is the last place that should carry one.

Read-only exposure of a stylesheet the app already ships is not a new security surface, but the guards are reused rather than re-derived: `_serve_static` already refuses traversal and escape, and this route must not become the one place those checks were rewritten slightly differently.
