---
type: "[[change]]"
id: CHG-20260720-Index-Case-Canonicalisation
aliases: ["CHG-20260720-Index-Case-Canonicalisation"]
title: "Index re-roots watcher paths to docs_root case — /api/render finds files created/modified after cockpit start (ISS-0001)"
status: merged
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
impacts: ["Index.invalidate path-case canonicalisation", "/api/render frontmatter for post-start files"]
issues: ["[[ISS-0001]]"]
features: ["[[FEAT-0006-Cockpit-Layout]]"]
related: ["[[TASK-0174]]", "[[TST-0001]]"]
---

# Index case canonicalisation (ISS-0001)

## Summary

On case-insensitive macOS volumes `Path.resolve()` does not fold case, so fsevents could report a changed file under a different parent-component case (`/Users/Edwin/…`) than the initial walk used (`/Users/edwin/…`). `Index.invalidate` then re-keyed the record under the reported case, and `Index.get((docs_root / rel).resolve())` — the exact-case lookup behind `/api/render` and `/api/cockpit/context?this=<path>` — missed it. Symptom: empty `metadata_html`/`frontmatter` (no frontmatter strip in the centre pane) for any note created or modified after cockpit start when the shell cwd case differed from the docs-root case.

Fix (ISS-0001 Option A, at the index): `Index.invalidate` now re-roots the resolved changed path under `self.docs_root` via `relative_to_ci` before indexing, so every record is keyed under the walk's case. Single point of change; happy path unchanged. The prior case-insensitive stale-entry removal stays as belt-and-suspenders.

## Verification

Reproduced the live bug first (`mixed.resolve() != canonical`; `get(canonical)` MISS after a mixed-case `invalidate`). Added regression test `test_invalidate_folds_path_case_to_docs_root` (tests/test_index.py) — passes with the fix, fails without it (adequacy checked by disabling the re-root). Full suite: 218 passed, 1 skipped.

Files: `src/project_os_cockpit/index.py`, `tests/test_index.py`.
