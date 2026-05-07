# docs-server

On-the-fly Markdown render server for project-os repos. Renders any `.md` note as a linked HTML page at request time — no build step, with frontmatter-aware metadata, `[[wikilink]]` resolution, project-os ID linking, and live reload.

## What it gives you

- Browse any project-os repo's `docs/` tree as HTML in a browser, on-demand. Edit a note in your editor and the page in your browser soft-reloads within a fraction of a second.
- `[[FEAT-0008]]` and `[[Target|Display]]` style links resolve correctly across the whole `docs/` tree, including the project-os ID conventions (`TASK-####`, `FEAT-####`, `REQ-####`, etc.).
- YAML frontmatter renders as a metadata strip per page (status, owner, parent, links).
- Auto-generated index pages by status, parent, or type.
- Backlinks panel showing which other notes link to the page you're viewing.
- Optional embedded local-only terminal panel for running an AI coding assistant (Claude Code / Codex) alongside the docs while editing in real time.

## Stack

- Python 3.11+
- `markdown` + selected `pymdownx` extensions for the renderer
- `python-frontmatter` for YAML frontmatter
- `watchdog` for file-change events
- Stdlib `http.server` for HTTP and a small SSE handler for Server-Sent Events
- Optional: [`ttyd`](https://github.com/tsl0922/ttyd) wrapping `claude` (or `codex`) for the terminal panel

No Node.js, no build step, no static-site generator.

## Run

```bash
# from this repo, point at any project-os repo
python -m docs_server /path/to/your/project-os/repo

# typical local-dev pairing — render server on LAN, terminal on localhost
python -m docs_server /path/to/repo --bind 0.0.0.0 --port 8765 \
  --terminal --terminal-bind 127.0.0.1 --terminal-port 7681
```

## Project-os layout

This repo is itself a project-os repo. See:

- `SNAPSHOT.yaml` — current state (focus, item statuses, counters)
- `docs/` — features, tasks, requirements, risks, ADRs, etc.
- `tools/instructions/`, `tools/skills/` — the project-os system rules (synced from `../project-os`)

To consume this tool from another project-os repo, see `docs/features/downstream-pilot/FEAT-0005-Downstream-Pilot.md`.

## License

MIT. See `LICENSE`.
