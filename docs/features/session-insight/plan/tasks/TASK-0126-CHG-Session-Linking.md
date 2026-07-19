---
type: "[[task]]"
id: TASK-0126
aliases: ["TASK-0126"]
title: "CHG ↔ session linking — provenance enrichment"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0022-Session-Insight-And-Traceability]]"
effort: "S"
depends: ["[[TASK-0123]]"]
blocks: []
related: []
tests: []
---

# CHG ↔ session linking

## Definition of Done
- [ ] When a CHG note is created during (or shortly after) a live instrumented session, the session index records the association (session id + cost against the CHG id).
- [ ] The rendered CHG note shows "produced by session … (cost)" in its metadata area — cockpit-side enrichment; the note file is never modified.

## Steps
- [ ] Correlate watcher-created CHG paths with the live session window in the sidecar.
- [ ] Store on the session record; expose in `/api/render` enrichment for CHG notes.
- [ ] Render in the metadata strip; tests for the correlation window.

## Notes
Answers "which agent session produced this change and what did it cost" — durable provenance without touching note files.
