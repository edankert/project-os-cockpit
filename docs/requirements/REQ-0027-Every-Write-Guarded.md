---
type: "[[requirement]]"
id: REQ-0027
aliases: ["REQ-0027"]
title: "Every cockpit write is loopback-only, precondition-guarded, format-preserving, and announced"
status: "approved"
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-03"
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
