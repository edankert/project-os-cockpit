---
type: roadmap
id: ROADMAP
status: draft
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
tags: [roadmap]
---

# Roadmap

The detailed plan lives in `docs/PHASES.md` and the per-feature notes under `docs/features/`. This file is a one-screen summary.

## Near-term — PHASE-001 MVP

- Markdown render server with frontmatter + `[[wikilink]]` resolution.
- Live reload via Server-Sent Events.
- Embedded local-only terminal (ttyd-driven, iframe-embedded).
- Validated by running against this repo's own `docs/`.

## Mid-term — PHASE-002 Project-os adapter

- ID resolution polish (TASK-####, FEAT-####, etc. with status badges).
- Auto-generated index pages by status / parent / type.
- Backlinks panel and basic graph (notes that link to / from this one).

## Longer-term — PHASE-003 Downstream pilot

- Deploy to `~/Dev/repos/your-applications.com/tools/docs-server/`.
- Harden the cross-repo invocation pattern (one upstream, many downstreams).
- Document the deployment shim so other project-os repos can adopt it cleanly.
