---
type: glossary
id: GLOSSARY
status: active
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
tags: [glossary]
---

# Glossary

## Project-os terms (inherited)

These are defined upstream in `~/Dev/repos/project-os/`; the canonical definitions live there. Listed here only for cross-reference within this repo.

- **Project-os repo** — any repo with `SNAPSHOT.yaml` at the root and `tools/instructions/` + `docs/__templates__/` synced from the upstream template.
- **SNAPSHOT.yaml** — canonical machine-readable state file for an LLM session.
- **Note (item) types** — `FEAT`, `TASK`, `REQ`, `ISS`, `RISK`, `REL`, `ADR`, `TST`, `CHG`, `WF`, `PHASE`.

## project-os-cockpit-specific

- **Renderer** — the function that takes a `.md` file path and returns rendered HTML. Stateless; reads frontmatter and body fresh each request.
- **Index (in-memory)** — the precomputed map from titles / IDs / aliases to file paths, built at startup and updated by the file watcher. Used by the wikilink resolver.
- **SSE channel** — Server-Sent Events stream that pushes file-change notifications to connected browsers.
- **Terminal panel** — optional iframe-embedded terminal pointing at a localhost-bound `ttyd` (or eventually xterm.js) process. Used to run Claude Code / Codex alongside the docs viewer.
- **Downstream consumer** — a project-os repo (e.g. `~/Dev/repos/your-applications.com/`) that runs `project-os-cockpit` against its own `docs/` via a shim under its `tools/project-os-cockpit/`.
- **Upstream sync** — the mechanism by which a downstream repo pulls template-owned files (`tools/instructions/`, `tools/skills/`, `docs/__templates__/`, `docs/__bases__/`) from the canonical `project-os` repo.
