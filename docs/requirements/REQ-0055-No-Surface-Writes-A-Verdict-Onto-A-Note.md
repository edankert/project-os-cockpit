---
type: "[[requirement]]"
id: REQ-0055
aliases: ["REQ-0055"]
title: "No cockpit surface reads a verdict from a note or writes one onto a note"
status: implemented
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
priority: high
scope: "cockpit read/write path"
implements: "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
acceptance:
  - "[x] No cockpit module reads `mark` from frontmatter; a guard test fails if one does."
  - "[x] Recording a walk appends exactly one ledger event and modifies no note."
  - "[x] Every acceptance endpoint states the platform its answer is about."
  - "[x] A rendered mark is still a check mark on every surface (REQ-0045 is not weakened by the store moving)."
  - "[x] `COCKPIT-API.md` matches the endpoints after the move."
covers: []
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[REQ-0045-Storage-Is-Words-Display-Is-Glyphs]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tags: [requirement]
---

# The store moves, and the guard is a test

## Statement

The cockpit **shall** take every acceptance verdict from the ledger for the platform in view, and **shall** record every verdict by appending an event. No acceptance write shall modify a note.

## Why a guard test rather than a review

The read path spans **87 sites in `desktop/src/renderer/renderer.ts`** and 65 in `acceptance.py`, plus five endpoints. A migration of that size leaves survivors, and a surviving frontmatter read does not fail — it returns a stale scalar that looks exactly like a verdict. The failure mode is silent and indistinguishable from success, which is the case a guard exists for.

## What this must not weaken

- **[[REQ-0045]]**: a rendered mark is a check mark, whatever the file stores. The store is changing; the rendering rule is not.
- **[[ADR-0035]]**: a release page reports and does not record. The ledger strengthens this — the page has nothing to write into.
- **[[ADR-0027]]**: 671 ledger entries must not become 671 badges. The gate stays one aggregated row.

## Acceptance criteria

- [x] No frontmatter verdict reads, guarded by a test.
- [x] A walk appends one event, touches no note.
- [x] Endpoints name their platform.
- [x] Glyph rendering unchanged.
- [x] API reference matches.
