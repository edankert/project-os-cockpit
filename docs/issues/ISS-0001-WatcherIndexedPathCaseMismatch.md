---
type: "[[issue]]"
id: ISS-0001
title: "Watcher-indexed paths poison the in-memory _records under a different case than the initial walk on case-insensitive filesystems, so /api/render returns empty frontmatter for any file created or modified after cockpit start"
status: closed
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-06-01
updated: 2026-07-20
source: [diagnosis_session_2026-06-01]
severity: high
component: index/watcher
parent: ""
related: ["[[TASK-0174]]", "[[CHG-20260720-Index-Case-Canonicalisation]]"]
tests: []
---

# Watcher-indexed paths poison `_records` under a mismatched case

## Problem

On macOS (case-insensitive but case-preserving HFS+/APFS), the
in-memory `Index._records` dict can end up with two different keys for
the same physical file:

- Files present at cockpit start get indexed under the **case the
  walker uses** — usually the case of `docs_root` as passed on the CLI
  (e.g. lowercase `/Users/edwin/...`).
- Files created or modified after start get indexed by the watcher
  under **the case fsevents reports**, which may differ (e.g.
  capital-E `/Users/Edwin/...` if the user's shell cwd uses that case).

`Index.get(path)` performs an exact lookup (`_records.get(path.resolve())`)
and is case-sensitive at the dict level. So any API handler that
computes `target = (docs_root / rel_path).resolve()` and calls
`index.get(target)` will miss watcher-indexed records.

The visible symptom: `/api/render` returns `metadata_html: ""` and
`frontmatter: {}` for any file created or modified after cockpit
start. The Electron centre pane mounts the body but not the
frontmatter strip. Files present at cockpit start render normally.

`index.by_id(note_id)` still works because `_by_id` stores the same
(wrong-case) path the watcher used, so resolution via ID
short-circuits past `Index.get`. That's why `?this=FEAT-0090` returns
the active block but `/api/render?path=features/FEAT-0090...md`
returns empty.

## Repro

1. Launch cockpit with lowercase docs root:
   `python -m project_os_cockpit /Users/edwin/Dev/repos/your-trainer/docs --port 8766`
2. From a shell whose cwd uses the capital-E case (`/Users/Edwin/...`),
   create a new markdown file under `docs/features/` with valid
   frontmatter. (Or modify an existing one — same effect.)
3. `curl -s "http://127.0.0.1:8766/api/render?path=features/<new-file>.md" | jq '.metadata_html, .frontmatter'`
4. Observe: `metadata_html` is `""`, `frontmatter` is `{}`, `title`
   falls back to `target.stem`.
5. Compare: `curl -s "http://127.0.0.1:8766/api/cockpit/context?this=<NOTE-ID>" | jq '.active'`
   → returns a populated active block with the real title from
   frontmatter. Proves the record IS in the index, just under a
   different path key.
6. `touch` cannot recover the file — watchdog re-fires the same
   capital-E path; `_records[capital-E]` is overwritten but
   `_records[lowercase-e]` stays absent.

Encountered against `your-trainer/docs/` during the 2026-06-01
v2.1.0 session — affected FEAT-0020, FEAT-0079, FEAT-0089,
FEAT-0090, FEAT-0091, FEAT-0092 (every file created or modified
after the cockpit launch on 2026-05-26 18:13).

## Expected

`Index.get((docs_root / rel).resolve())` resolves any file under
`docs_root` regardless of which path-case the watcher used. The
metadata strip renders identically for files present at startup and
files created later in the same session.

## Actual

The render endpoint returns `metadata_html: ""` and the centre pane
shows body content with no frontmatter widget for any file the
watcher (not the initial walk) is responsible for indexing — i.e.
every file touched after cockpit start when the shell case differs
from the docs-root case.

## Evidence

- Diagnostic walkthrough in chat 2026-06-01.
- Direct file URL (`/docs/features/X.md`) renders the metadata strip
  fine — that path reads frontmatter from disk via
  `renderer.render_markdown_file`, not from the index.
- `/api/render` and `/api/cockpit/context?this=<path>` both return
  empty `active` because both hit `Index.get(path)`.
- `/api/cockpit/context?this=<ID>` returns full `active` because
  `_by_id` resolution sidesteps `Index.get`.

## Fix options

**Option A (preferred)** — Canonicalise the watcher's path-case to
match `docs_root` before indexing. In `watcher._Handler._emit`, after
the `relative_to_ci` call, recompute `abs_path = self._root / rel`
so events publish with the docs-root case. Single point of fix; no
behaviour change for the happy path; downstream code is unchanged.

**Option B** — Make `Index.get` case-insensitive by storing
`_records` under `str(path).lower()` keys (or maintaining a parallel
lowercase lookup). Larger blast radius — every dict access changes.
Defensible if other path-keyed maps (`_outbound`, `_inbound`,
`_by_filename`) have the same latent bug. Worth auditing before
choosing.

**Option C** — Defensive fallback in `_serve_render`: if
`index.get(target)` returns None, do a case-insensitive scan of
`_records.keys()` for a match. Cheap but hides the bug at the API
boundary rather than fixing the underlying invariant.

Recommendation: **A**, with a small unit test that fakes a watcher
event using a different case and asserts `index.get(canonical_path)`
finds the record.

## Next Actions

- [x] Decide Option A vs B (A recommended).
- [x] Implement + unit test the canonicalisation.
- [x] Add a regression test that constructs an Index with a
      lowercase docs_root, invokes `invalidate` with a mixed-case
      abs_path, and asserts `index.get(lowercase_path)` returns the
      record.
- [x] Note in CHANGELOG / CHG once shipped: "Watcher-indexed files
      now resolve under both case variants on macOS — fixes empty
      metadata strip on `/api/render` for files created after
      cockpit start (ISS-0001)."

## Resolution (2026-07-20)

Fixed via Option A applied in `Index.invalidate` (TASK-0174): after `.resolve()`, the changed path is re-rooted under `docs_root` via `relative_to_ci`, so records are always keyed under the walk's case regardless of the case fsevents reports for a parent component. Confirmed still live before the fix (reproduced: `mixed.resolve() != canonical`, `get(canonical)` MISS after a mixed-case invalidate) and verified fixed by regression test `test_invalidate_folds_path_case_to_docs_root` (passes with the fix, fails without it). See [[CHG-20260720-Index-Case-Canonicalisation]].
