---
type: "[[change]]"
id: CHG-20260507-Render-Pipeline-Online
aliases: ["CHG-20260507-Render-Pipeline-Online"]
title: "Render pipeline + HTTP server + theme tokens — docs-server now serves content"
status: merged
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: ["[[TASK-0002]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/server.py"
  - "src/docs_server/renderer.py"
  - "src/docs_server/templates.py"
  - "src/docs_server/static/base.css"
  - "src/docs_server/__main__.py"
  - "pyproject.toml"
issues: []
features: ["[[FEAT-0001]]"]
related: ["[[REQ-0001]]", "[[REQ-0003]]", "[[REQ-0006]]", "[[REQ-0012]]", "[[ADR-0003]]", "[[TASK-0003]]"]
---

# Render pipeline online

## Summary
docs-server now actually serves docs. `python -m docs_server <docs-root>` boots a `ThreadingHTTPServer` and renders any `.md` under the configured root as HTML on request — no build step. The server uses the `markdown` library with `tables`, `fenced_code`, `toc`, `pymdownx.superfences`, `pymdownx.highlight`; frontmatter is parsed with `python-frontmatter` and surfaced as a metadata strip with a status chip; the shared HTML shell follows [[REQ-0012]] (muted greyscale, dual themes, all colors as CSS custom properties).

## Impact

### New URL surface
- `GET /` → 302 to `/docs/`.
- `GET /docs/` → directory listing of the docs root (or `README.md` if present).
- `GET /docs/<rel-path>/` → directory listing or rendered README.
- `GET /docs/<rel-path>.md` → rendered HTML.
- `GET /docs/<rel-path>.<ext>` → raw bytes (handy for `.base`, images, etc.).
- `GET /_static/<file>` → packaged stylesheet/script.
- `..` traversal → 403; missing path → 404; favicon → 204.

### CLI
- `docs_root` positional (required).
- `--bind` (default `0.0.0.0`, [[REQ-0006]] — flip to `127.0.0.1` for loopback only).
- `--port` (default 8765).
- `-v` for verbose logging.

### Visual contract
- All UI colors live in CSS custom properties on `:root` and `[data-theme="dark"]` (per [[REQ-0012]] / [[ADR-0003]]).
- Theme bootstrap script in `<head>` resolves the right theme before stylesheet apply (no wrong-theme flash on first paint).
- Header includes a theme toggle that persists to `localStorage`.
- Status chip rules cover the full project-os taxonomy (`active`, `doing`, `next`, `in-progress`, `done`, `verified`, `passing`, `approved`, `accepted`, `merged`, `published`, `fixed`, `blocked`, `reopened`, `failing`, `backlog`, `planned`, `proposed`, `draft`, `todo`, `open`, `pending`, `triage`, `closed`, `obsolete`, `reference`).

### Server-startup robustness
- Custom `ThreadingHTTPServer` subclass bypasses the stdlib's reverse-DNS lookup at bind — the stdlib's `socket.getfqdn()` call can hang for tens of seconds on networks without DNS or in sandboxed environments. Skipping it makes startup deterministic and DNS-independent.

## Follow-ups
- [ ] [[TASK-0003]] — wikilink resolver. Both body wikilinks and frontmatter wikilink-shaped strings currently render as plain text; TASK-0003 turns them into resolved anchors.
- [ ] [[TASK-0004]] — auto-generated index pages.
- [ ] First `TST-*` acceptance tests should be retro-fitted; this task verified via 85-file render sweep + curl probe set, not via formal test notes.
- [ ] Consider adding `pygments` as an explicit dep when the renderer needs syntax highlighting; today it falls back to plain `<pre><code>` if pygments isn't installed.
