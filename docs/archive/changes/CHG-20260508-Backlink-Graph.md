---
type: "[[change]]"
id: CHG-20260508-Backlink-Graph
aliases: ["CHG-20260508-Backlink-Graph"]
title: "Backlink graph + first automated tests (TST-0001)"
status: merged
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[TASK-0007]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/index.py"
  - "tests/test_index.py"
  - "tests/fixtures/index_basic/"
  - "docs/tests/TST-0001-Index-Lookup-And-Backlinks.md"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0002]]", "[[REQ-0008]]", "[[TST-0001]]", "[[TASK-0008]]"]
---

# Backlink graph online

## Summary
Extends `Index` with the outbound + inbound link graph FEAT-0006 (cockpit) and FEAT-0004 (backlinks panel) both depend on. Outbound links are extracted from each note's frontmatter values *and* body; the inbound graph is the symmetric reverse. Renamed `update_path` → `invalidate` to match the cockpit task spec; the old name still works as an alias.

This is also the **first batch of automated tests** in the project (TST-0001) — 12 unit tests against a fixture docs tree, runs in <100 ms.

## Impact

### New `Index` API
- `Index.paths()` — sorted list of every indexed note path.
- `Index.by_id(target)` — returns the `Path` for an id / alias / filename / title (priority order matches `resolve()` but skips the URL projection).
- `Index.links_from(path)` — `frozenset[Path]` of notes the given note links to.
- `Index.links_to(path)` — `frozenset[Path]` of notes that link to the given note (the backlink view).
- `Index.invalidate(path)` — replaces `Index.update_path` (kept as alias). Re-reads + re-graphs a single path.

### Graph shape
- Two-pass build: first pass populates lookup tables; second pass resolves wikilinks. Single-pass would miss forward references.
- Frontmatter wikilinks walk recursively through scalars / lists / dicts so `related: ["[[FEAT-0001]]", "[[FEAT-0002]]"]` and `parent: "[[FEAT-0001]]"` both contribute.
- Body wikilinks via `wikilinks.WIKILINK_RE` (same regex the markdown extension uses).
- Self-links excluded.
- Unresolved wikilinks logged at DEBUG once per `(file, target)` pair — most "unresolved" hits in the actual docs tree are intentional placeholders in `__templates__/SCHEMAS.md`, illustrative `[[Foo]]` examples in task notes, etc., so WARNING was too loud.
- Delete preserves `_inbound[deleted_path]` (sources still claim to link there). See TST-0001 for the design rationale.

### Tests
- `tests/test_index.py` — 12 cases (lookup priority, link graph from body+frontmatter, inbound = reverse outbound, unresolved-doesn't-raise, invalidate after edit/delete/re-create, template notes indexed for resolution). All passing in 0.06s.
- `tests/fixtures/index_basic/` — small static fixture (3 real notes + a template stub) used by every test.
- `docs/tests/TST-0001-Index-Lookup-And-Backlinks.md` — the first formal `TST-*` note in the project. System-scoped (cross-feature shared infra).

### Build performance
- 92 notes in this repo's `docs/`: index builds in ~50 ms. 229 outbound edges, 56 inbound targets in the resulting graph.
- Test suite: 12 tests in 0.06s against the static fixture.

## Follow-ups
- [ ] [[TASK-0008]] — `.base` parser + DSL evaluator, the next cockpit task. Now unblocked.
- [ ] FEAT-0004 backlinks panel — can now consume `Index.links_to(active_note)` directly. Worth landing alongside TASK-0010 (cockpit shell) since both are project-os adapter polish.
- [ ] Heading-anchor wikilinks (`[[X#Heading]]`) are not yet supported — currently treated as opaque targets, unresolvable. Add when an actual use-case appears.
