---
type: "[[task]]"
id: TASK-0609
aliases: ["TASK-0609"]
title: "An HTML page in the record can show an image that sits beside it, because the frame is served any file inside the workspace's `docs/`"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]", "[[ADR-0042-What-May-Be-Framed]]"]
parent: "[[FEAT-0147-Pictures-Beside-The-Note]]"
effort: S
depends: ["[[TASK-0608-Pin-Image-Resolution-To-The-Note]]"]
blocks: ["[[TASK-0612-Convert-The-Largest-Embedded-Artifact]]", "[[TASK-0613-A-Generic-HTML-Viewer]]"]
related: ["[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]", "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"]
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [task, render, security]
---

# An HTML page may show a file beside it

## Definition of Done

- [ ] The route that serves files to a frame accepts **any path that resolves inside the workspace's `docs/`** ([[ADR-0042-What-May-Be-Framed]]). The design register's `claimed` set is gone.
- [ ] `<img src="shot.png">` inside a framed page resolves when `shot.png` sits beside it, and so does `<img src="__attachments__/shot.png">` and a path two directories down. No depth limit.
- [ ] `..` traversal is rejected and the resolved path must lie inside `docs_root`. A test proves both, because these are now the *only* path rules left.
- [ ] GET-only, no cookies, `X-Content-Type-Options: nosniff` — unchanged and asserted by test.
- [ ] **The sandbox assertion from [[RISK-0008-The-Sandbox-Is-The-Only-Boundary]] lands in this task**: a test reads the frame's `sandbox` attribute and fails if `allow-same-origin` appears in it, plus one sentence at `desktop/src/renderer/renderer.ts:5708` saying that attribute is now the only boundary and naming ADR-0042.
- [ ] The `text/html` charset fix from [[ISS-0050]] survives — `guess_type` returns `text/html` with no charset and a page without its own `<meta charset>` rendered as mojibake once already.
- [ ] [[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]] is `fixed`.

## Steps

- [ ] Accept [[ADR-0042-What-May-Be-Framed]] first.
- [ ] Delete the `claimed` set in `_serve_design_asset` (`src/project_os_cockpit/server.py:3375`). The function's docstring argues for a rule that measurement showed does not hold — replace the reasoning, do not keep it.
- [ ] Ask whether this route should exist at all, or whether the frame should simply use `/docs/<rel>` with a different header set. That is [[TASK-0613-A-Generic-HTML-Viewer]]'s decision; note the answer here either way.
- [ ] Leave `/docs/<rel>` itself alone.

## Notes

This became a much smaller task on 2026-09-12. The first version implemented a reference-reachability rule — a derived set of files any note points at, rebuilt on index reload, with a one-level-deep limit for relative references. Edwin removed the rule: *"I don't think we need that rule, what is the issue if this isn't limited? yes cross repo is allowed."* The measurement behind his question is in [[ADR-0042-What-May-Be-Framed]]: `/docs/<rel>` already serves every file under `docs/` with no gate, on a socket bound to `0.0.0.0`, so the allowlist was protecting nothing.

What survives from the first version is the **negative test**, and it moved: it used to prove that an unreferenced file is 404, and now it proves that `allow-same-origin` is absent. That is where the boundary actually is.
