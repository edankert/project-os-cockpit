---
type: "[[task]]"
id: TASK-0613
aliases: ["TASK-0613"]
title: "A viewer frames any HTML page a note references, with no design vocabulary in the route, the mode or the frame"
status: done
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"]
parent: "[[FEAT-0148-One-HTML-Viewer]]"
effort: L
depends: ["[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]"]
blocks: ["[[TASK-0614-Links-Stop-Asking-For-The-Bench]]", "[[TASK-0615-Remove-The-Bench]]"]
related: ["[[ADR-0042-What-May-Be-Framed]]", "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"]
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [task, render]
---

# A generic HTML viewer

## Definition of Done

- [x] A route serves an HTML page to a frame, accepting any path inside the workspace's `docs/` ([[ADR-0042-What-May-Be-Framed]]), named for what it does and not for designs. Decide here whether it is a new route at all or `/docs/<rel>` with the artifact header set, and record which.
- [x] A view frames it, with a way back to the note that references it and the note's ID visible.
- [x] It works for a note of **any** type, proven with a non-design note in the walk.
- [x] It frames a page in **another workspace** the shell has open, by addressing that workspace's sidecar. Cross-repo is allowed (Edwin, 2026-09-12) and each sidecar still bounds its own `docs/`.
- [x] The frame keeps every property the bench's frame had: `sandbox` without `allow-same-origin`, `referrerpolicy=no-referrer`, theme passed in the URL because the frame has an opaque origin and cannot read the app.
- [x] The stylesheet injection that makes one style-guide page work in every repo is kept, or its removal is recorded as a decision — it is the reason six repos share one artifact rather than six that drift.
- [x] The bench still works. This task adds; it removes nothing.

## Steps

- [x] Read `buildDesignStage` and its callers in `desktop/src/renderer/renderer.ts` (around line 5650) before writing anything. Several comments there record defects that were expensive to find — the `is-empty` class and the stretched-child slab, the `has_asset` / historical-render interaction, the charset bug from [[ISS-0050]]. Carry those forward rather than rediscovering them.
- [x] Build beside the bench, not in place of it.
- [x] A 404 means the file is not there, or the path escaped `docs_root`. There is no "nobody linked this" case any more — the reachability rule was dropped on 2026-09-12.

## Notes

**Amended 2026-09-12.** The first version of this task inherited a reference-reachability rule from [[ADR-0042-What-May-Be-Framed]]'s first version, and a 404 that had to explain that nobody had linked the file. Edwin removed the rule; the ADR's amendment note carries the measurement that justified it. Cross-repo framing was also an open question in the first version and is now decided: allowed.

Keeping both surfaces alive for one commit is the point. The bench's 198 tests still pass while the viewer is checked on its own, and only then does [[TASK-0615-Remove-The-Bench]] delete both the surface and its tests.

## Outcome (2026-09-12)

**The route is `/framed/<rel>`**, and `/design-asset/<rel>` still reaches the same handler until [[TASK-0615-Remove-The-Bench]] takes it away. One handler, two names, so they cannot drift while both exist. The task asked me to decide whether a separate route should exist at all rather than `/docs/<rel>` with different headers: it should, and narrowly — `nosniff`, `no-store` and the utf-8 repair from [[ISS-0050]] belong on a file served for framing and not on the browsing route, and a second name is what lets the bench's name retire without a flag day.

**The page is `~view/<rel>`**, and `~view/@<project>/<rel>` frames a file in another workspace through that workspace's own sidecar — cross-repo, as Edwin allowed, with each sidecar still bounding its own `docs/`. A project the window does not have open says so instead of showing a blank pane.

**The frame keeps every property the bench's had**: sandboxed without the same-origin flag, `referrerpolicy=no-referrer`, and the theme passed in the URL — which is what makes one style-guide page follow six projects rather than drifting into six copies.

**The way back is recorded on the way in.** By the time the viewer renders, `currentRel` is the viewer, so `navigateTo` captures the note before navigating. A viewer opened cold shows no back button rather than one that goes nowhere.

Checked in the renderer harness: a design note's page framed from its note, the back button returning to that note, project-os-deck's DES-0001 framed while project-os-cockpit was on screen, and an unknown project reporting itself. Five source guards in `tests/test_framing.py`, including one that fails if the viewer ever consults the design register — which would re-impose the bench's limit that a file must be claimed to be shown.

**The bench still works.** This task removed nothing; `test_design_bench.py`'s 170 tests still pass.

## One thing worth knowing for the next task

`conftest.js_function_body` cannot find the body of a function whose return type contains braces — it takes the first `{` after the parameter list. `viewerTarget` returned `{ base, path, project } | null` and the guard read the signature as the whole body. Naming the type (`ViewerTarget`) fixes it, and this is the second time in this phase: `designsForLink` hit the same trap on 2026-09-11.
