---
type: "[[task]]"
id: TASK-0007
aliases: ["TASK-0007"]
title: "Note index + backlink graph (shared infrastructure)"
status: backlog
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
tests: []
---

# Note index + backlink graph

## Definition of Done
- [ ] `docs_server.index` exposes `Index` with: `paths()`, `get(path)`, `by_id(alias_or_id)`, `links_from(path)`, `links_to(path)`.
- [ ] On construction, walks the docs root, parses every `.md` (frontmatter + body), and builds:
  - `path → NoteRecord` (frontmatter dict, body string, computed type/id/aliases)
  - `id_alias → path` (covers both `id` and every entry in `aliases`)
  - `path → set[path]` for outbound links (resolved via id-alias map *and* filename map)
  - `path → set[path]` for inbound links (the reverse graph)
- [ ] Outbound link extraction recognises `[[Target]]` and `[[Target|Display]]` in body, *and* wikilinks inside frontmatter values (e.g. `parent: "[[FEAT-0001]]"`, `implements: ["[[FEAT-0006]]"]`).
- [ ] Unresolvable wikilinks are logged once with file + token, never raised.
- [ ] `Index.invalidate(path)` re-parses just that path and patches the graph (called by the watcher in FEAT-0002).
- [ ] Unit tests against a fixture docs tree assert: every fixture note is reachable, frontmatter wikilinks contribute to the graph, deletion + re-add via `invalidate` works.

## Steps
- [ ] Sketch the `NoteRecord` dataclass (path, frontmatter dict, body, type, id, aliases, outbound_links).
- [ ] Implement the walker (use `pathlib.Path.rglob("*.md")`; skip `.obsidian/`, `.trash/`, `__templates__/`).
- [ ] Implement the alias map (every note declares `aliases: ["<id>"]` per the project-os convention — see `tools/instructions/OBSIDIAN.md`).
- [ ] Implement outbound-link extraction. Regex over body for `[[...]]` tokens; recursive walk over frontmatter values for the same pattern.
- [ ] Build the reverse graph as a derived view of the outbound graph.
- [ ] Implement `invalidate(path)` and write a test that mutates a fixture file mid-test.
- [ ] Wire it into `__main__` for v0 (no CLI surface — just construct it at startup so we can confirm it loads against this repo's `docs/`).

## Notes
This task is also a prerequisite for FEAT-0004 (backlinks panel) — both features share the same data layer. Implement it here, link FEAT-0004 to consume it later.

The CONTEXT.base predicate `file.hasLink(this.file)` evaluates against this graph's reverse edges, so the index needs to surface inbound links cheaply (O(1) set lookup).
