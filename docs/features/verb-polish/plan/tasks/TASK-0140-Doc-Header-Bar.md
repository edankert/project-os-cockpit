---
type: "[[task]]"
id: TASK-0140
aliases: ["TASK-0140"]
title: "Doc header bar — note identity, path, verb buttons on every note"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0026-Verb-Polish]]"
effort: "M"
depends: []
blocks: []
related: ["[[TASK-0132]]"]
tests: ["[[TST-0011]]"]
---

# Doc header bar

## Definition of Done
- [x] Every rendered note shows a sticky header row: type icon + ID + title + status chip, the docs-relative path (click to copy), and the note's verb buttons (registry-driven, status-filtered, default verb emphasised) dispatching via the normal execute path.
- [x] The top-bar ▶ dispatch button is removed — the header replaces it.
- [x] Header absent on virtual pages (~overview, ~session) and notes without an ID show identity only (no verb buttons).

## Steps
- [x] `buildDocHeader(data)` prepended in `navigateTo`; sticky CSS inside the doc scroll container.
- [x] Remove `#top-bar-dispatch` + `paintDispatchButton` plumbing.
- [x] CSS.

## Notes
User request 2026-07-06 (items 2+3): "current active page name type and location visible at the top" + "buttons on the current active page to run the available agent tasks".
