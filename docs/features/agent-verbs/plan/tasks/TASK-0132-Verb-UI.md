---
type: "[[task]]"
id: TASK-0132
aliases: ["TASK-0132"]
title: "Verb UI — Agent submenu, verb-aware dispatch button, agent preference"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0024-Agent-Verbs]]"
effort: "M"
depends: ["[[TASK-0131]]"]
blocks: []
related: ["[[TASK-0121]]"]
tests: []
---

# Verb UI

## Definition of Done
- [x] Context menu on nav rows / doc links / scoped-overview feature rows shows "Agent ▸" with the note type's verbs (from the registry) + Claude/Codex preference radios.
- [x] Top-bar ▶ appears on TASK/ISS/FEAT/REQ/PHASE/RISK notes; click fires the default verb, context-click opens the verb menu.
- [x] `dispatchToAgent` resolves the verb's prompt template with `{id}`/`{rel}`.

## Steps
- [x] Fetch `/api/cockpit/actions` on sidecar ready.
- [x] Renderer passes verbs into `showContextMenu`; main builds the submenu.
- [x] Extend `currentFrontmatterId` + ▶ handlers; scoped-feat contextmenu.
