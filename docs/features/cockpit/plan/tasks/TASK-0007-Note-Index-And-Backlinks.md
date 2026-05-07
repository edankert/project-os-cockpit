---
type: "[[task]]"
id: TASK-0007
aliases: ["TASK-0007"]
title: "Note index + backlink graph (shared infrastructure)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: M
due: ""
depends: []
blocks: [TASK-0008, TASK-0009]
related: ["[[FEAT-0004]]"]
tests: ["[[TST-0001]]"]
---

# Note index + backlink graph

## Definition of Done
- [x] `docs_server.index.Index` exposes `paths()`, `get(path)`, `by_id(alias_or_id)`, `links_from(path)`, `links_to(path)`. Plus the existing `resolve()` / `url_for()` / `notes_by_type()` / `type_counts()` / `subscribe_to(bus)` from earlier tasks.
- [x] `Index.build(docs_root)` walks the docs tree and populates: `path → NoteRecord` (with frontmatter, body, title, id, aliases, type, status), `id → path`, `alias → path`, `filename → path`, `title → path`, plus `path → frozenset[path]` outbound and `path → set[path]` inbound graphs.
- [x] Outbound link extraction handles `[[Target]]` and `[[Target|Display]]` in BODY, and walks frontmatter values recursively (scalar / list / dict) so `parent: "[[FEAT-0001]]"` and `implements: ["[[FEAT-0006]]"]` both contribute.
- [x] Unresolvable wikilinks log at DEBUG (one entry per `(file, target)` pair), never raise. Lowered from WARNING because most unresolved hits in the actual docs tree are intentional placeholders in templates / SCHEMAS.md / illustrative `[[Foo]]` examples.
- [x] `Index.invalidate(path)` re-parses just that path and patches both lookup tables and graph. Called by the watcher subscriber on every `.md` event. Earlier callers using the legacy name `Index.update_path` still work (kept as alias).
- [x] Unit tests in `tests/test_index.py` ([[TST-0001]]) — 12 cases against a fixture docs tree under `tests/fixtures/index_basic/`. All passing in 0.06s.

## Steps
- [x] Extended `NoteRecord` with `body` field — needed for the body-side wikilink scan.
- [x] Two-pass build: first pass populates lookup tables for every note; second pass walks each note's frontmatter+body and resolves wikilinks. Single-pass would miss forward references during the walk.
- [x] `_wikilinks_in_body` / `_wikilinks_in_frontmatter` helpers — regex from `wikilinks.WIKILINK_RE`; frontmatter walker recursively descends scalars / lists / dicts.
- [x] `_rebuild_links` diffs old vs new outbound and patches `_inbound` mirrors atomically. On `_remove_path`, drops the deleted file's outbound and removes it from each former target's inbound; intentionally KEEPS `_inbound[deleted_path]` since sources still claim to link there (see TST-0001's `test_invalidate_after_delete_removes_record` for the rationale).
- [x] Renamed public API to `invalidate` per the DoD, with `update_path` kept as alias for any external callers.

## Notes
The renderer / wikilink resolver / auto-index pages were already using the index from TASK-0003 / TASK-0004; this task added the **graph** dimension on top — `links_from` / `links_to` — without touching the existing resolution behaviour. The cockpit's CONTEXT pane (TASK-0010) and FEAT-0004's backlinks panel both consume `links_to(active_note)` to build the "what points here" view.

The DoD calls for `[[Target#Heading]]` heading anchors as a future extension; not in scope here. Currently `[[X#H]]` is treated as `[[X#H]]` (target string), unresolvable unless something has that exact alias.

**First TST-* note in the project** — pattern established for future automated tests. System-wide infrastructure tests live under `docs/tests/`; feature-scoped tests under `docs/features/<slug>/plan/tests/` per LIFECYCLE.md.
