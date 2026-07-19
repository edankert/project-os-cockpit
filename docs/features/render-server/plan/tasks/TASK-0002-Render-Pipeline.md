---
type: "[[task]]"
id: TASK-0002
aliases: ["TASK-0002"]
title: "Implement Markdown → HTML render pipeline with frontmatter parsing"
status: done
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
parent: "[[FEAT-0001]]"
fixes: []
effort: M
due: ""
depends: ["[[TASK-0001]]"]
blocks: ["[[TASK-0003]]", "[[TASK-0004]]"]
related: []
tests: []
---

# Render pipeline

## Definition of Done
- [x] `renderer.render_markdown_file(path, rel_path)` reads a `.md` file, splits frontmatter, runs Markdown → HTML, and returns a complete HTML document.
- [x] Frontmatter rendered as a metadata strip (`<aside class="metadata-strip">`) showing status (as a chip), owner, parent, source, tags, plus all primary frontmatter keys.
- [x] HTTP route `GET /docs/<path>` returns rendered HTML for a `.md`; directory listings + README rendering for directory paths; raw-byte serving for non-`.md` files (so images and `.base` files are reachable).
- [x] Path-traversal guard returns 403 (URL-decoded `..` segments + `Path.resolve()` + relative-to check).
- [x] `markdown` extensions enabled: `tables`, `fenced_code`, `toc`, `pymdownx.superfences`, `pymdownx.highlight`. `tab_length=2` to match Obsidian's 2-space list-nesting convention.
- [x] Shared HTML template (header / breadcrumb / theme toggle / metadata strip / article) with one CSS file under `src/docs_server/static/base.css` — palette + theme tokens per [[REQ-0012]].

## Steps
- [x] CLI: positional `<docs-root>` + `--bind` (default `0.0.0.0`, [[REQ-0006]]) + `--port` (default 8765) + `-v` flags.
- [x] HTTP server: `ThreadingHTTPServer` subclass that bypasses the stdlib's reverse-DNS lookup at bind (avoids 30–90s startup hang on constrained networks).
- [x] Renderer: `python-frontmatter` for parsing, `markdown.Markdown` with the agreed extensions.
- [x] Templates: HTML5 shell with inline theme-bootstrap script (sets `data-theme` before stylesheet apply, no flash) + theme-toggle button persisting to `localStorage`.
- [x] Path guard: early `..`-segment reject + `Path.resolve()` + `relative_to(docs_root)` check.
- [x] Smoke-test against this repo's own `docs/` — all 85 `.md` files render without errors; `curl` probes confirm 302 root redirect, 200 dir/md/css, 403 traversal, 404 missing.

## Notes
No wikilinks yet (TASK-0003), no live reload (TASK-0005/6). Just static-render-on-request with proper frontmatter handling.

**Verification reality check:** No formal `TST-*` notes exist for this task. Verification was: 85-file render sweep + 7-endpoint `curl` probe set. Tier 1/2 acceptance test infrastructure is not yet in place anywhere in the repo; first formal TST notes likely land alongside the cockpit feature (FEAT-0006). Flag if unit tests should be retro-fitted before further FEAT-0001 work.

**Implementation deltas worth knowing:**
- The metadata strip surfaces *all* primary frontmatter keys (id, type, status, phase, owner, parent, implements, specifies, fixes, validates, blocks, depends, related, source, tags, created, updated, due, effort, priority, platform) in display order, plus any other keys at the end. `aliases` and `title` are intentionally hidden (housekeeping fields).
- Wikilink-shaped values (`[[FEAT-0001]]`, `[[FEAT-0001-Render-Server]]`) currently render as plain text in the metadata strip — TASK-0003 turns them into resolved anchors.
- Status chip CSS reuses currentColor for the border + text and pulls from CSS custom properties — adding a new status taxonomy entry is a one-line CSS rule, no JS change.
- The `getfqdn` bypass is a real bug avoidance in constrained environments (sandboxes, no-DNS LANs); not a hack.
