---
type: "[[task]]"
id: TASK-0166
aliases: ["TASK-0166"]
title: "Generic role-based text context menu — Cut/Copy/Paste/Select All everywhere"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0037"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0166 — generic text context menu

Main-process handler on `webContents "context-menu"`: when `params.isEditable` → Cut/Copy/Paste/Select All (role-based, plus spellcheck suggestions and macOS Look Up for free); when `params.selectionText` → Copy/Select All. Existing custom menus (nav rows, doc links, rail, cards) keep priority — they call preventDefault in the renderer, so the generic handler must skip events the renderer already claimed (coordinate via a data flag or the existing `menu:show-context` path). Covers doc text, palette input, settings fields, attention panel. Verification: right-click in a settings input → full edit menu; on selected doc text → Copy; on a nav row → the existing custom menu, unchanged.
