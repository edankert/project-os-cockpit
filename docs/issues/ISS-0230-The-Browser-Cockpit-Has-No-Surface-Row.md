---
type: "[[issue]]"
id: ISS-0230
aliases: ["ISS-0230"]
title: "The desktop shell draws a surface like a phase and the browser cockpit does not — the two front doors diverged in the left pane, which is PHASE-029's whole subject"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: cockpit-server
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
related: ["[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[ISS-0227-Every-Surface-Links-To-The-Same-Place]]", "[[REQ-0032]]"]
---

# One tool, and now two answers

`navItemSurface` — a surface drawn as a phase, with a chevron, an issue id, a completion bar and its checks beneath — was added to `desktop/src/renderer/renderer.ts`. The browser cockpit's `cockpit.js` has its own `pickItemRenderer` and did not get one, so it falls back to the plain row: **no bar, no handle, no children, and no issue link.**

Found by `test_the_picker_routes_only_to_known_renderers`, which checks **both** files — a guard written for renderer proliferation catching a front-door divergence instead.

[[PHASE-029]] states the rule this breaks: *"the browser cockpit and the desktop shell answer the same questions, and differ only where a difference was decided."* Nobody decided this one.

## Suggested fix

Port `navItemSurface` and the `.ov-phase*` styles it borrows. It is a copy rather than a shared module because the two renderers are separate bundles by design — which is the standing cost [[PHASE-029]] exists to pay down, and worth saying again here.

**Until then the guard is per-file**, so it keeps its teeth on both and names the difference rather than widening to accept anything.

## Done when

- [ ] A surface renders the same in both front doors, or a decision records why it does not.
