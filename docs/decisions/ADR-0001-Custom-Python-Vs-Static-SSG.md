---
type: "[[decision]]"
id: ADR-0001
aliases: ["ADR-0001"]
title: "Custom Python doc-server vs Quartz/mkdocs"
status: accepted
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
deciders: [user:edwin]
related: ["[[FEAT-0001]]"]
---

# ADR-0001 — Custom Python doc-server vs Quartz/mkdocs

## Context
We need a way to render any project-os repo's `docs/` tree as linked HTML. Two broad shapes exist:

1. **Static-site generators** (Quartz, mkdocs, Hugo, Eleventy, etc.) — build markdown → HTML once into a `_site/` directory, serve statically.
2. **On-the-fly server** — render markdown → HTML at request time, no build step.

## Decision
Build a small custom Python on-the-fly server.

## Consequences

### Positive
- **No build step.** Edit a note, refresh, see result. Combined with [[FEAT-0002]] (live reload), the loop tightens to "edit → see in <1s without a refresh".
- **No Node toolchain.** Everything runs from a `python -m docs_server` command, on Python 3.11 which is already installed.
- **Total control over the project-os semantics.** Status badges, parent breadcrumbs, ID prefix conventions, backlinks — all of these are easier to add to a focused codebase than to coerce out of a general-purpose SSG.
- **Small.** The whole tool lands in ~500 lines of Python; the codebase fits in your head.
- **Live integration with project-os tooling.** SSE channel, file watcher, future tighter coupling with SNAPSHOT.yaml — all natural in a long-running process.

### Negative
- **We write it.** Quartz and mkdocs already exist; we'd have to reinvent some wheels (table of contents, syntax highlighting, dark mode).
- **No graph view out of the box.** Quartz ships a graph view; we'd build one if we want one.
- **No full-text search out of the box.** Same.
- **Single point of failure.** If the server isn't running, nothing renders. (An SSG produces static HTML that any web server can serve.)

## Alternatives considered

- **Quartz** — Obsidian-aware, mature, has graph view + full-text search. Rejected primarily for the build-step / Node-toolchain reason; the on-the-fly behaviour is the headline feature.
- **mkdocs (with material)** — popular, theme-rich. Doesn't natively understand Obsidian wikilinks; requires plugins. Build-step.
- **obsidian-export → static** — converts vault to plain markdown, then any SSG. Two-step pipeline; loses the "on-the-fly" property entirely.

## Status
Accepted. Reconsider if the custom codebase grows past ~1500 lines or if the project-os community gives us reason to share a renderer.
