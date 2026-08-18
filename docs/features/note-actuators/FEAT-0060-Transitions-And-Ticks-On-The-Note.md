---
type: "[[feature]]"
id: FEAT-0060
aliases: ["FEAT-0060"]
title: "The actuator row: a note's legal human actions as buttons under its title, and its criteria checkboxes made live"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0005-The-Actuator-Grammar]]"]
goal: "Render the actions FEAT-0059 serves: a quiet action row on the note in the centre pane, checkboxes that tick with an evidence prompt, and disabled-with-reason where a gate blocks — the renderer displaying, never deciding."
requirements: ["[[REQ-0026-Only-Human-Owned-Transitions]]"]
tasks:
  - "[[TASK-0281-The-Action-Row]]"
  - "[[TASK-0282-Live-Checkboxes]]"
release: ""
related: ["[[FEAT-0059-The-Write-Service-Widens]]"]

---

# Transitions and ticks on the note

## Goal

The centre pane's note header gains one quiet row, populated from `GET /api/notes/actions` — the renderer draws what the server says is legal and sends back the choice with the note's mtime. Criteria checkboxes become live: click, evidence prompt, the tick lands in the file, the pane re-renders from the watcher's event.

## The one hard rule

**No vocabulary in TypeScript.** The renderer knows how to draw a button and a disabled reason; which buttons exist is the server's answer. This is ISS-0023's lesson and PHASE-022's thrice-repeated drift, encoded structurally.

## Out of Scope

- Mode 1. The actuator row is mode 3 first; the browser cockpit is read-only until the mode-1 ADR (PHASE-026) settles its future — widening a LAN-visible surface's writes is exactly what RISK-0005 forbids doing casually.
- Any styling not already in the record grammar.

## Closed 2026-08-10

The note gained its actions: a row under the metadata strip drawn from `GET /api/notes/actions`, and criteria checkboxes that take evidence rather than a click.

**The vocabulary stayed server-side, and tried twice to come back.** The first cut of the row styled its affirmative button by reading `action.verb === 'Approve'`; tone now comes from `confirm`, which is `CONFIRM_ACTIONS`' decision. That is [[ISS-0023]] arriving one class name at a time, and the guard was widened to catch verbs once the code could pass it.

**Nothing is optimistic.** Both paths re-read the note from disk after a write. The tests assert the *absence* of a local mutation, not the presence of a refetch — the failure mode is showing a state the file does not have.
