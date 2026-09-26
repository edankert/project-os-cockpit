---
type: "[[task]]"
id: TASK-0174
aliases: ["TASK-0174"]
title: "Fix ISS-0001 — canonicalise watcher path-case in Index.invalidate so /api/render finds post-start files"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: ["[[ISS-0001]]"]
parent: "FEAT-0006"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[ISS-0001]]"]
tests: ["[[TST-0001]]"]
---

# TASK-0174 — index case canonicalisation (ISS-0001)

Confirmed still live on 2026-07-20: reproduced that `.resolve()` does not fold case on this filesystem, so after `Index.invalidate(mixed_case_path)` the record is re-keyed under the watcher's case and `Index.get((docs_root / rel).resolve())` misses it — the empty-frontmatter symptom on `/api/render` for any file created/modified after cockpit start when the shell cwd case differs from the docs-root case. The prior partial fix (case-insensitive removal) prevented dual-keys but not the `get()` miss.

Fix (ISS-0001 Option A, applied at the index): in `Index.invalidate`, after resolving the changed path, canonicalise its case to `self.docs_root` via `relative_to_ci` (`changed_path = self.docs_root / rel`) so records are always keyed under the walk's case regardless of the case fsevents reported for a parent component. Single point of fix; happy path unchanged.

Verification: a regression test builds an Index under a docs root, invalidates with a mixed-case abs path, and asserts `index.get(canonical_path)` returns the record (and it fails without the canonicalisation). Added to the TST-0001 index suite.
