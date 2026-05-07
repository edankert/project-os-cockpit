---
type: architecture
id: ARCH
status: draft
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
tags: [architecture]
---

# Architecture

## High level

```
   ┌──────────────────────────────────────────────────────────────────┐
   │  project-os-cockpit (Python)                                            │
   │                                                                  │
   │   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐ │
   │   │  HTTP server   │    │  File watcher  │    │  SSE channel   │ │
   │   │  (stdlib)      │    │  (watchdog)    │    │                │ │
   │   └───────┬────────┘    └────────┬───────┘    └────────▲───────┘ │
   │           │                      │                     │         │
   │           ▼                      ▼                     │         │
   │   ┌──────────────────────────────────────────────────────────┐   │
   │   │  Renderer                                                │   │
   │   │  • frontmatter parser   • markdown → HTML                │   │
   │   │  • [[wikilink]] resolver   • template wrap (header etc.) │   │
   │   │  • backlinks index   • auto-index generators             │   │
   │   └──────────────────────────────────────────────────────────┘   │
   │                                                                  │
   └───────────────────────────────┬──────────────────────────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
      Mac browser (LAN)     Tablet browser (LAN)   Local terminal panel
                                                   (ttyd or xterm.js,
                                                    bound to 127.0.0.1)
```

## Components

### HTTP server
Stdlib `http.server` (`ThreadingHTTPServer`) is sufficient. Routes:
- `GET /` — landing page (links to indexes by type).
- `GET /docs/...` — render the `.md` file at that path. If a directory, render its `README.md` or auto-generate an index.
- `GET /index/<type>` — auto-generated index pages (features by status, tasks by parent, etc.).
- `GET /events` — SSE channel: file-change notifications for the live-reload script.
- `GET /static/...` — CSS, JS, fonts.

### Renderer
Pipeline:
1. Read `.md` file
2. Split frontmatter (YAML) from body
3. Resolve `[[wikilinks]]` via the index built at startup
4. Run Markdown → HTML (`markdown` + `pymdownx.superfences`, `tables`, `toc`, `fenced_code`)
5. Wrap in shared template (header, sidebar with frontmatter metadata, content, backlinks panel, footer)

### File watcher
`watchdog` observes the configured `docs/` root. Changes invalidate any cached index entries and broadcast on the SSE channel.

### SSE channel
Long-lived HTTP response. Each connected browser holds an open connection. On file change, push `event: file-changed\ndata: <path>\n\n`. Client-side script soft-reloads if the changed path matches the page's source.

### Terminal panel (optional)
Two implementation options — see `docs/decisions/ADR-0002-Terminal-Approach.md`. v1 plan is `ttyd` invoked separately and embedded via `<iframe src="http://127.0.0.1:7681/">`. The renderer's template detects whether the request came from a loopback connection and shows / hides the iframe accordingly so tablet sessions see only the docs content.

## Project-os ID resolution

The `[[wikilink]]` resolver does two passes:

1. **Direct title match** — look up the link target against the file-title index.
2. **ID match** — if the target matches `^(TASK|FEAT|REQ|ISS|RISK|REL|ADR|TST|CHG|WF|PHASE)-[0-9]+`, look it up against the ID index built from each file's frontmatter `id` and `aliases`.

Frontmatter `aliases` are also indexed, so `[[FEAT-0008]]`, `[[Your Trainer manual content]]`, and a custom alias all resolve to the same file.

## Deployment shape

- Local-dev (this repo): run from source with `python -m project_os_cockpit` against any project-os repo's `docs/`.
- Downstream project-os repo: a thin shim under `tools/project-os-cockpit/` (a `Makefile` target, a `dev.sh` wrapper, or a `pipx`-installed entrypoint) that points at the same source checkout. Per-repo configuration (port, terminal on/off) lives in the shim, not in this upstream.

See `docs/features/downstream-pilot/FEAT-0005-Downstream-Pilot.md` for the deployment plan.
