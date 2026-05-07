---
type: "[[task]]"
id: TASK-0002
aliases: ["TASK-0002"]
title: "Implement Markdown → HTML render pipeline with frontmatter parsing"
status: backlog
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0001]]", "[[REQ-0001]]", "[[REQ-0003]]"]
fixes: []
effort: M
due: ""
depends: [TASK-0001]
blocks: [TASK-0003, TASK-0004]
related: []
tests: []
---

# Render pipeline

## Definition of Done
- [ ] `renderer.render(path) -> str` reads a `.md` file, splits frontmatter, runs Markdown → HTML, and returns a complete HTML document.
- [ ] Frontmatter rendered as a metadata strip in the HTML (status, owner, parent, source, tags).
- [ ] HTTP server route `GET /docs/<path>` returns the rendered HTML for a `.md` file.
- [ ] Path-traversal guard refuses paths outside the configured docs root (returns 403).
- [ ] `markdown` extensions enabled: `tables`, `fenced_code`, `toc`, `pymdownx.superfences`, `pymdownx.highlight`.
- [ ] Shared HTML template (header / sidebar / content / footer) with one CSS file.

## Steps
- [ ] CLI: parse `<docs-root>` positional + `--bind` / `--port` flags.
- [ ] HTTP server: subclass `ThreadingHTTPServer` with custom request handler.
- [ ] Renderer: load file via `python-frontmatter`, run Markdown, wrap in template.
- [ ] Template: minimal HTML5 with a brand-aligned CSS file under `src/docs_server/static/`.
- [ ] Path guard: `Path.resolve()` + `is_relative_to(docs_root)`.
- [ ] Smoke-test against this repo's own `docs/` — every page renders without errors.

## Notes
No wikilinks yet (TASK-0003), no live reload (TASK-0005/6). Just static-render-on-request with proper frontmatter handling.
