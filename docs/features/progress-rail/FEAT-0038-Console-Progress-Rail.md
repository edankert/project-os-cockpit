---
type: "[[feature]]"
id: FEAT-0038
aliases: ["FEAT-0038"]
title: "Console progress rail — live work-blocks under the session strip + enriched progress panel"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
goal: "The coloured block notation becomes visible at the console: a thin always-visible rail under the collapsed session strip shows one type-coloured block per documented item the session touches, filling live as the agent completes them; the expanded panel's work tab becomes a rich, recency-ordered 'progress' list (block + id + title + from→to transition + relative time, active item pinned); the 'files' text expand button becomes a rotating chevron."
requirements: ["[[REQ-0021]]"]
tests: []
tasks: ["[[TASK-0188]]", "[[TASK-0189]]", "[[TASK-0190]]", "[[TASK-0191]]", "[[TASK-0192]]"]
related: ["[[FEAT-0036]]", "[[FEAT-0023]]", "[[FEAT-0022]]"]
---

# Console progress rail

## Why

User request 2026-07-22: the block notation (overview phase squares) has become the primary progress language — "I am actually on the overview page looking for these blocks to be filled in by the LLM as it completes the prompt … it could be nice to have this clearly shown in the collapsed bar above the console where it also shows the current console state and ctx." Plus: the strip's expand button is a literal "files" text label (should be an icon), and the current work tab is too thin — bare id + latest status, no titles, no transitions, no ordering.

## Design (chosen 2026-07-22 from three mocked options)

1. **Rail (TASK-0188)**: a second ~14px row inside the strip container, under the main line. One `.ov-phase-sq`-notation block per session work item (from `work_notes`), chronological left→right, type colour from the ID prefix (TASK/ISS/FEAT/REQ/RISK/TST/ADR/CHG…), outline = open, filled = done-equivalent, pulsing = the item the agent is touching now. Click → navigate to the note; hover → "ID Title (status)". Overflow: cap (~24) with a "+N" suffix. Hidden when the session has no documented items.
2. **Progress panel (TASK-0189)**: the expanded tab renders rich rows — block + id + title + `from → to` transition + relative time — ordered by last activity, the currently-active item pinned to top with a pulse. CHG notes included as they are created.
3. **Naming/affordance (TASK-0190)**: tab renamed `work` → `progress`; the "files" text expand button becomes a chevron (⌄, rotating when open), title "Session details".

## Mechanics (from the 2026-07-22 research pass — renderer-only, no sidecar changes)

- `cockpit:status-change` SSE already carries `{id, rel, type, title, from, to, ts}` — the renderer currently discards all but `id`/`to`; `workTransitions` should store `{from, to, ts, title}`.
- Session item list: `work_notes` (ordered by first touch). Note type derivable from the ID prefix — no server lookup needed.
- "Active now" heuristic: the most recently touched/transitioned work item while the session is live.
- Known gaps to close during implementation: no `--type-change` CSS colour exists yet (add one); no relative-time helper in the renderer (add one); items with no transition this session have no title client-side (fallback to bare id, or seed from `/api/cockpit/transitions`).
