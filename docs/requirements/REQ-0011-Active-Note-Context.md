---
type: "[[requirement]]"
id: REQ-0011
aliases: ["REQ-0011"]
title: "Bases referencing this.file re-evaluate when the active note changes"
status: retired
implements: ["[[FEAT-0006]]"]
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
source: []
priority: high
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[REQ-0009]]", "[[REQ-0010]]"]
tests: []
---

# REQ-0011 — Active-note context propagation

> **Retired (2026-05-08).** Superseded by [[REQ-0013]] — the active-note re-fetch behaviour is preserved (right pane re-fetches on nav) but the contract is no longer expressed in terms of `this.file` since `.base` files don't drive the cockpit. See [[ADR-0004]].

## Statement
A `.base` file whose filters reference `this.file` (the canonical pattern in `CONTEXT.base`: `file.hasLink(this.file)`) SHALL be re-evaluated whenever the centre-pane active note changes, with `this.file` bound to the new active note's path.

The re-evaluation SHALL happen without a full-page reload — the JSON API receives a `?this=<note-id>` query parameter and the JS client patches just the affected pane.

When no active note is set (e.g. the landing page or a 404), `this.file` SHALL evaluate to null and predicates depending on it SHALL short-circuit to false (returning an empty row set rather than an error).

## Acceptance Criteria
- Navigating from `/FEAT-0001` to `/FEAT-0002` causes any pane mounting `CONTEXT.base` to re-fetch with `?this=FEAT-0002` and update with no full-page reload.
- The right pane on a `/<unknown>` URL evaluates to empty (no error, no crash).
- A pane mounting a base that does *not* reference `this.file` (e.g. `NAV.base`) does NOT re-fetch on active-note change — only `this.file`-dependent panes do.
- The active note ID is in the URL path so refreshing the browser preserves the cockpit state.

## Rationale
The whole reason the right pane exists is to surface relationships of the currently-viewed note. Without `this.file` propagation, `CONTEXT.base` is meaningless. The constraint about non-`this.file` panes not re-fetching keeps NAV stable while the user clicks through notes.

## Traceability
- Implements: [[FEAT-0006]]
- Verified by: TASK-0010 (URL/state contract) + TASK-0011 (SSE-driven re-fetch with state preservation).
