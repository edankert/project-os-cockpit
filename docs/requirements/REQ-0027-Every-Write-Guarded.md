---
type: "[[requirement]]"
id: REQ-0027
aliases: ["REQ-0027"]
title: "Every cockpit write is loopback-only, precondition-guarded, format-preserving, and announced"
status: "implemented"
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-10"
source: ["[[RISK-0005-The-Write-Surface]]"]
priority: high
scope: "All note mutations, present and future — the standing terms of the viewer line's crossing"
specifies: ["[[FEAT-0059-The-Write-Service-Widens]]"]
acceptance:
  - "No write endpoint is reachable from a non-loopback peer; the 0.0.0.0 render surface stays read-only (RISK-0001's model, extended)"
  - "Every write carries an mtime precondition; a note changed since render refuses loudly and writes nothing"
  - "A write touches only its allow-listed fields or its one located line; the rest of the file is byte-identical (round-trip asserted)"
  - "Every applied write fires the SSE event that re-renders its surfaces — no optimistic UI, the file is the truth"
  - "SNAPSHOT.yaml is never written by the cockpit (ADR-0009)"
reviewed_by: "user:edwin"
review_date: "2026-08-03"
review_verdict: "plan-accepted"
---

# Every write guarded

`note_writes.py`'s existing discipline, promoted from module convention to requirement — so each new verb inherits the terms rather than renegotiating them, and the hardening suite has a contract to test against instead of a habit.

## Acceptance Criteria

- [x] No write endpoint is reachable from a non-loopback peer; the 0.0.0.0 render surface stays read-only — evidence: tests/test_human_transitions.py::test_every_note_mutating_endpoint_requires_loopback — enumerates the POST dispatch table; it found ISS-0129 on its first run (user:edwin, 2026-08-10)
- [~] Every write carries an mtime precondition; a note changed since render refuses loudly and writes nothing — partially — transition and tick carry it (two tests); create has nothing to precondition, it makes a new file; check-toggle still bypasses it, recorded in ISS-0129 and folded into TASK-0363 (user:edwin, 2026-08-10)
- [x] A write touches only its allow-listed fields or its one located line; the rest of the file is byte-identical — evidence: test_a_legal_transition_writes_only_status_and_updated and test_a_tick_preserves_indentation_and_touches_one_line — body compared byte-for-byte, one line changed (user:edwin, 2026-08-10)
- [x] Every applied write fires the SSE event that re-renders its surfaces — no optimistic UI, the file is the truth — evidence: every new verb writes through the filesystem, so the docs watcher emits file-changed exactly as an editor save does; no endpoint mutates a cache (user:edwin, 2026-08-10)
- [x] SNAPSHOT.yaml is never written by the cockpit — evidence: note_writes.py contains no reference to SNAPSHOT; ADR-0009 puts propagation in sync-snapshot.py at pre-commit (user:edwin, 2026-08-10)

## Unweakened by ADR-0010 — 2026-08-12

[[ADR-0010]] option 4 decided that parity across surfaces is the goal and that **authentication is its precondition** ([[REQ-0034]]).

**Nothing in that decision relaxes this requirement.** Until REQ-0034 is implemented and its acceptance is met, every clause here holds exactly as written: no write endpoint is reachable from a non-loopback peer, and the `0.0.0.0` render surface stays read-only.

Recorded here because this is the note a person will open when they wonder whether the rule still applies — and an ADR that says "eventually, differently" is the easiest thing in the world to read as "not any more".

When REQ-0034 lands, the loopback clause is **replaced** by proof-of-identity rather than deleted. The requirement that a write be authorised does not change; only what counts as authorisation does.
