---
type: "[[change]]"
id: CHG-20260727-Design-Surfaces
title: "PHASE-009: design becomes a project record — render, capture, compare, annotate, review, check"
status: merged
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[PHASE-009-Design-Surfaces]]", "review:model:claude-fable-5 2026-07-27"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/server.py", "src/project_os_cockpit/note_writes.py", "src/project_os_cockpit/design_tokens.py", "desktop/src/renderer/renderer.ts", "docs/designs/"]
issues: []
features: ["[[FEAT-0042-Design-Bench]]"]
design: ["[[DES-0001-Overview-Redesign]]", "[[DES-0002-Cockpit-Design-System]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REQ-0023-Design-Is-A-Project-Record]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
---

# Design surfaces

## Summary

All eight tasks of [[PHASE-009]] are `done`. The cockpit now renders design artifacts at the viewport the app runs at, captures revisions with their reasons, compares two revisions side by side from git, carries region-anchored comments as Markdown, reviews designs through the existing desk pinned to the revision judged, and checks a design's status palette against the implementation.

Five of seven phase exit criteria are met or reconciled. **Two remain open and both need Edwin** — they are recorded as outstanding rather than reworded to match what shipped.

## What the review changed

Fable reviewed the plan cold before any code was written and found the hole it was built around: **[[TASK-0216]] rendered git history and nothing deposited it.** An agent iterating against the live surface edits the working copy six times and commits once — exactly what happened to [[DES-0001]], the loss this phase exists to prevent. Every exit criterion could have gone green while the next design session lost five revisions again.

The tell was in the plan already: TASK-0216's step 4 *manufactured* its own multi-revision fixture. A task that has to fabricate its own subject is admitting the organic thing is not expected to exist.

That produced [[TASK-0220]] (capture, sequenced *before* compare) and [[TASK-0221]] (the authoring contract, because the bench shipped detectors that the only real artifact could not satisfy). It also demoted the token-parity claim from "the reason to build this" to a real but narrow check.

## Decisions worth keeping

- **Anchors are region ids, never coordinates.** A comment survives its region *moving*; it orphans when the region is *renamed* — and is flagged, never dropped, because a vanished comment takes the objection with it.
- **The revision log carries no sha.** A commit cannot contain its own hash: write it, commit, and it is already stale; amend to fix it and the amend changes it again. The note records the *reason*, git records the *revision*, and they pair by order and date — which also survives a rebase.
- **A verdict names the revision it judged**, validated against real history. Without it an approval given to v3 silently launders v6.
- **`viewport` absence is meaningful** — the artifact is a document *about* a surface, not the surface. Device widths are disabled for one, because framing a scrolling dossier at 420px proves nothing.
- **The asset endpoint gates on the register, not the directory.** Serving any file under `docs/` by path would turn a render surface into a file browser.

## Still open

- Edwin has not reviewed a real design through the surface. The machinery is complete; the verdict is not something an agent may supply.
- No design has yet been *produced* through this workflow, so the behaviour change — two committed revisions with reasons, unrescued — is unproven by construction.
- Live reload on artifact edit did not land; the dirty indicator says the pane is stale instead.

## Verification

382 passed / 1 skipped. `tests/test_design_bench.py` (42) and `tests/test_design_tokens.py` (10) are new. `tsc` clean, bundle rebuilt, validator clean.
