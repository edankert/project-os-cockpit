---
type: "[[task]]"
id: TASK-0613
aliases: ["TASK-0613"]
title: "A viewer frames any HTML page a note references, with no design vocabulary in the route, the mode or the frame"
status: backlog
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

- [ ] A route serves an HTML page to a frame, accepting any path inside the workspace's `docs/` ([[ADR-0042-What-May-Be-Framed]]), named for what it does and not for designs. Decide here whether it is a new route at all or `/docs/<rel>` with the artifact header set, and record which.
- [ ] A view frames it, with a way back to the note that references it and the note's ID visible.
- [ ] It works for a note of **any** type, proven with a non-design note in the walk.
- [ ] It frames a page in **another workspace** the shell has open, by addressing that workspace's sidecar. Cross-repo is allowed (Edwin, 2026-09-12) and each sidecar still bounds its own `docs/`.
- [ ] The frame keeps every property the bench's frame had: `sandbox` without `allow-same-origin`, `referrerpolicy=no-referrer`, theme passed in the URL because the frame has an opaque origin and cannot read the app.
- [ ] The stylesheet injection that makes one style-guide page work in every repo is kept, or its removal is recorded as a decision — it is the reason six repos share one artifact rather than six that drift.
- [ ] The bench still works. This task adds; it removes nothing.

## Steps

- [ ] Read `buildDesignStage` and its callers in `desktop/src/renderer/renderer.ts` (around line 5650) before writing anything. Several comments there record defects that were expensive to find — the `is-empty` class and the stretched-child slab, the `has_asset` / historical-render interaction, the charset bug from [[ISS-0050]]. Carry those forward rather than rediscovering them.
- [ ] Build beside the bench, not in place of it.
- [ ] A 404 means the file is not there, or the path escaped `docs_root`. There is no "nobody linked this" case any more — the reachability rule was dropped on 2026-09-12.

## Notes

**Amended 2026-09-12.** The first version of this task inherited a reference-reachability rule from [[ADR-0042-What-May-Be-Framed]]'s first version, and a 404 that had to explain that nobody had linked the file. Edwin removed the rule; the ADR's amendment note carries the measurement that justified it. Cross-repo framing was also an open question in the first version and is now decided: allowed.

Keeping both surfaces alive for one commit is the point. The bench's 198 tests still pass while the viewer is checked on its own, and only then does [[TASK-0615-Remove-The-Bench]] delete both the surface and its tests.
