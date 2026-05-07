---
type: "[[task]]"
id: TASK-0003
aliases: ["TASK-0003"]
title: "Implement [[wikilink]] resolver (titles + aliases + project-os IDs)"
status: backlog
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0001]]", "[[REQ-0002]]"]
fixes: []
effort: M
due: ""
depends: [TASK-0002]
blocks: [TASK-0004]
related: []
tests: []
---

# Wikilink resolver

## Definition of Done
- [ ] At server startup, walk the docs tree and build an in-memory index: title / `id` / `aliases` (from frontmatter) → file path.
- [ ] Renderer pre-processor finds `[[Target]]` and `[[Target|Display]]` patterns in Markdown body and rewrites them to standard Markdown links pointing at the resolved page URL.
- [ ] Project-os ID pattern (`TASK-####`, `FEAT-####`, `REQ-####`, etc.) matched against the ID index even when not present as a literal title.
- [ ] Unresolved targets render as a visual "broken link" (e.g. `<span class="broken-wikilink">[[Foo]]</span>`) so the author can see them.
- [ ] Indexer updates incrementally on file change (driven by the watcher landed in TASK-0005).

## Steps
- [ ] `index.py`: walk function returning `dict[str, Path]` keyed by every alias / title / ID for every `.md`.
- [ ] Renderer: insert wikilink preprocessor before the Markdown extension chain.
- [ ] Regex: `\[\[([^|\]]+)(?:\|([^\]]+))?\]\]` for the basic form; ID detection via `^(TASK|FEAT|REQ|ISS|RISK|REL|ADR|TST|CHG|WF|PHASE)-\d+$`.
- [ ] Resolution order: exact ID match → exact title match → exact alias match → unresolved.
- [ ] CSS for `.broken-wikilink`.

## Notes
This is the feature that turns "rendered Markdown" into "browseable knowledge base". Without it, every internal link in the project-os notes is dead text.
