---
type: "[[feature]]"
id: FEAT-0136
aliases: ["FEAT-0136"]
title: "The cockpit reads and writes the ledger — the read path, the write path and five endpoints move off the note's frontmatter"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
goal: "No cockpit surface reads a verdict from a note or writes one onto a note — recording a walk appends an event to the working ledger for its platform."
requirements: ["[[REQ-0055-No-Surface-Writes-A-Verdict-Onto-A-Note]]"]
tasks: ["[[TASK-0536-The-Read-Path-Moves-To-The-Ledger]]", "[[TASK-0537-The-Write-Path-Appends-An-Event]]", "[[TASK-0538-The-Renderer-And-The-Endpoints-Follow]]", "[[TASK-0545-Suite-At-Gets-A-Third-Shape]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]", "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"]
tags: [feature]
---

# The read path, the write path and a new file format, together

## Goal

This is the real cost of [[ADR-0037]] and the source proposal understates it. Measured 2026-08-19:

| surface | `mark` sites |
| --- | --- |
| `desktop/src/renderer/renderer.ts` | **87** |
| `src/project_os_cockpit/acceptance.py` | 65 |
| `note_writes.py` | 17 |
| `validate_docs_bundled.py` | 15 |
| `cockpit.py` | 9 |
| `server.py` | 6 |
| `renderer.py`, `templates.py`, `obligations.py`, `standing.py`, `fleet_validate.py` | 8 combined |

**The TypeScript renderer carries more mark references than any Python module**, and the proposal's "~9 cockpit modules" does not mention it.

## Scope

- **Read.** `acceptance.load` and `Item` take their verdict from the ledger for the current platform, not from frontmatter. `Item.settled` and `Suite.blocking*` follow.
- **Write.** `note_writes.mark_check` and `POST /api/notes/mark-check` append an event to the working ledger instead of setting a field. The name goes with the behaviour — it is not a note write any more.
- **The five acceptance endpoints** (`/api/notes/acceptance`, `/api/notes/acceptance-run`, `/api/notes/mark-check`, `/api/cockpit/acceptance`, `/api/cockpit/acceptance-debt`) and `COCKPIT-API.md`.
- The renderer's 87 sites, and the platform the UI is currently filtered to becoming an input to what a mark *means* rather than only to which rows show.

## What must not regress

- **[[FEAT-0126]]'s glyph.** A rendered mark is a check mark on every surface, whatever the file stores. The store is changing; the rendering rule is not.
- **[[ADR-0035]] / [[ISS-0210]].** A release page reports and does not record. The ledger makes this stronger, not weaker: the page has nothing to write into.
- **[[ADR-0027]].** 671 ledger entries must not become 671 badges. The release gate stays one aggregated row.

## Acceptance

- [x] No cockpit module reads `mark` from frontmatter; a guard test fails if one does.
- [x] Recording a walk appends one event and modifies no note.
- [x] Every acceptance endpoint states the platform its answer is about.
- [x] A sealed release's page renders identically before and after an unrelated working-ledger append.
- [x] `COCKPIT-API.md` matches the endpoints.
- [x] `suite_at` reads a historical ref correctly, proved on a real tag ([[TASK-0545]]) — the one read path where the moved verdict produces a **wrong answer** rather than an error.
