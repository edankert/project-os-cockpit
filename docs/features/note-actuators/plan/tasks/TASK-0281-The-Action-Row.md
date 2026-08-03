---
type: "[[task]]"
id: TASK-0281
aliases: ["TASK-0281"]
title: "The action row under the note title — drawn from the server's answer, confirming terminal moves, explaining disabled ones"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
parent: "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"
effort: M
depends: []
blocks: []
related: ["[[DES-0005-The-Actuator-Grammar]]"]
tests: []
---

# The action row

## Definition of Done

- Rendered from `GET /api/notes/actions` on note load; hidden entirely when the answer is empty.
- Terminal moves (Decline, Supersede) confirm once; forward moves do not.
- A disabled action shows its `reason` on hover — the button that explains, never the button that vanishes.
- A completed action refreshes via the existing SSE note-changed event, not an optimistic local mutation — the file is the truth.
- Guarded in the node suite; the vocabulary lives server-side only (asserted the ISS-0023 way).
