---
type: "[[task]]"
id: TASK-0142
aliases: ["TASK-0142"]
title: "Settings panel — enable the rail button, external-hook toggle"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-09-25
parent: "[[FEAT-0027-External-Session-Signal]]"
effort: "S"
depends: []
blocks: []
related: []
tests: ["[[TST-0011]]"]

---

# Settings panel

## Definition of Done
- [x] Rail settings button opens a popover; the external-hook toggle shows an honest description of what is written where and reflects/persists the app setting.
- [x] Toggling installs/uninstalls the hook and reports the result inline.

## Verification

CDP: the rail settings button opens `#settings-popover` with the external-hook toggle and an honest description naming `~/.claude/settings.json` + the backup/removal behavior; the toggle drives `settings.set` and reports the result inline (backend in `app-settings.ts`).

## Waiver retired, 2026-09-25

This note was closed on 2026-07-20 under a waiver of [[TST-0011]], the manual live-agent checklist. Edwin ran that checklist live on 2026-09-25 and all 13 rows passed, so the waiver is retired and the gate is met by the test itself.
