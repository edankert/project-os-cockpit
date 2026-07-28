---
type: "[[issue]]"
id: ISS-0050
aliases: ["ISS-0050"]
title: "The live design-asset route sent no charset, so revision-compare compared two encodings"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of FEAT-0042, 2026-07-28"]
related: ["[[TASK-0215-Design-Render-Surface]]", "[[TASK-0216-Revisions-And-Compare]]", "[[FEAT-0042-Design-Bench]]"]
fixed_by: []
---

# The same bytes, two encodings

`_serve_design_asset` derived its type from `mimetypes.guess_type()`, which returns `text/html` with **no charset**. `_serve_design_asset_at` — the *historical* route — hard-codes `text/html; charset=utf-8`.

DES-0001 carries no `<meta charset>`, so the identical bytes decoded as utf-8 from history and as latin-1 live: `project-os-cockpit Â· design review` in the working copy, `project-os-cockpit · design review` at `4ebe62d`.

Two of FEAT-0042's acceptance bullets depended on this. *"The existing DES-0001 dossier renders correctly — the real artifact, not a fixture"* was unmet. *"Two git revisions render side by side"* was worse than unmet: **compare was showing an encoding difference as though it were a design difference**, which is precisely the thing the compare view exists to rule out.

## Fix

Text types get `; charset=utf-8` on the live route, matching the historical one. Binary assets are untouched. Verified over HTTP: both routes now return `text/html; charset=utf-8`.

## Why the guard missed it

`test_the_asset_route_sets_no_store_and_nosniff` `inspect.getsource`s the handler and greps for the two headers it cares about. It never makes a request, so it could not see a header that was absent — and greps cannot notice absence they were not told to look for. The new test asks the server.
