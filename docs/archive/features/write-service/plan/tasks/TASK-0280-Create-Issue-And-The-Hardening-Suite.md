---
type: "[[task]]"
id: TASK-0280
aliases: ["TASK-0280"]
title: "Issue creation from template with the next free id, and the mutation-grade hardening suite over all three verbs"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0059-The-Write-Service-Widens]]"]
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
effort: M
depends: ["[[TASK-0278-The-Transition-Table-As-Data]]"]
blocks: []
related: ["[[RISK-0005-The-Write-Surface]]"]
tests: []
---

# Create, and the hardening suite

## Definition of Done

- [x] `POST /api/notes/create` (type=issue): fills the issue template, id = index max + 1 (sync-snapshot's counter confirms at pre-commit, same number), status `triage` unless severity given, links carried from the payload.
- [x] Filename follows the corpus convention; the watcher picks the file up and SSE announces it — the pane updates without reload.
- [x] The hardening suite: every refusal exercised — non-loopback caller, agent-owned transition, unknown field, stale mtime, path traversal, duplicate id race. Each guard broken once to prove the suite bites (the PHASE-022 lesson, applied from day one).

## Done 2026-08-10

`create_issue` + `POST /api/notes/create`, `CREATABLE_TYPES = {"issue"}` as a constant rather than a parameter — FEAT-0059's Out of Scope says each further type earns its own review of what "next id" and "which template" mean, and a constant is what makes widening deliberate.

The id comes from the **index**, not the snapshot counter: `sync-snapshot.py` raises `counters` to the maximum observed id at pre-commit (ADR-0009), so the two agree by construction and a create does not depend on the snapshot being fresh.

`status: triage` unless a severity is given. Supplying one means the triage judgment has already been made, so the issue opens rather than queueing for one.

## The suite bit twice on its first run

The DoD asked for every refusal exercised, *"each guard broken once to prove the suite bites"*. It did better than that — it found two live defects before any guard was deliberately broken.

**1. The duplicate-id race was real.** Two creates against the same stale index compute the same id from different titles, so a *filename* existence check passes and two notes end up sharing an id. Collision is now detected on the **id** (`glob(f"{issue_id}-*.md")`), which is the thing that must be unique.

**2. [[ISS-0129]] — `/api/notes/check-toggle` had no loopback guard**, and writes note body text. Any peer able to reach the `0.0.0.0` render surface could tick or untick any checkbox in `docs/`, including the acceptance and exit criteria the validator reads as evidence. It predates `note_writes.py`, so it appeared in no list of write endpoints. [[REQ-0027]] had required loopback-only since 2026-08-03; nothing enforced it.

**Both were found because the suite enumerates the dispatch table instead of listing endpoints by hand.** A hand-written list would have been derived from `note_writes`' callers and would not have contained check-toggle. The three runtime-only exemptions are named individually, and each exemption *asserts the handler performs no note write* — so exempting a fourth is an edit somebody makes on purpose.
