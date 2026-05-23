---
type: "[[requirement]]"
id: REQ-0004
aliases: ["REQ-0004"]
title: "Real-time soft reload when source .md changes"
status: verified
phase: "[[PHASE-001-MVP]]"
implements: ["[[FEAT-0002]]"]
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
implemented_by: ["[[FEAT-0002]]"]
verified_by: []
---

# REQ-0004 — Live reload

Modifying any `.md` under the served docs root SHALL trigger a soft reload of the corresponding browser page within 1 second of the source file's `mtime` updating.

Pages whose source file did NOT change SHALL NOT reload (so the index page next to a content page stays put while the content page reloads).

## Rationale
The killer feature. Edit-and-see-result is the whole reason for a render-on-request server. Without live reload the user has to manually refresh after every edit, which kills the loop.

## Verification
- 2026-05-23: marked `verified` — FEAT-0002 Live-Reload is done; SSE soft-reload shipped (TASK-0006, CHG-20260508-SSE-Live-Reload).
