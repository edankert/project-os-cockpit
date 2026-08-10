---
type: "[[task]]"
id: TASK-0283
aliases: ["TASK-0283"]
title: "⌘N capture — title in, triage issue out, current note linked, under three seconds"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0061-Quick-Capture-And-Triage]]"]
parent: "[[FEAT-0061-Quick-Capture-And-Triage]]"
effort: S
depends: []
blocks: ["[[TASK-0284-The-Triage-Tray]]"]
related: ["[[TASK-0280-Create-Issue-And-The-Hardening-Suite]]"]
tests: []
---

# Capture

## Definition of Done

- [x] ⌘N anywhere in a workspace opens the capture; Enter files it; Esc costs nothing.
- [x] The issue lands at `triage` with `source:` naming the capture and `related:` the open note, and appears in the pane via the watcher without reload.
- [x] The dialog never blocks on the sidecar: a failed create keeps the text and says why.

## Done 2026-08-10

⌘N opens one field. Enter files an issue at `triage` through `POST /api/notes/create`, with `source:` naming the capture and `related:` carrying the open note. Esc costs nothing.

**It lands at `triage`, not `open`** — capture records that something was *noticed*; deciding what it is, is the judgment [[TASK-0284]]'s tray exists for.

**The text is never lost.** A failed create re-enables the field, says why in place, and returns focus. A capture that eats a thought on a bad request is worse than no capture, because the entire proposition is that it costs nothing to use — guarded by `test_capture_never_loses_the_text_on_failure`.

No reload after a successful file: the watcher sees the new note and the pane refreshes.
