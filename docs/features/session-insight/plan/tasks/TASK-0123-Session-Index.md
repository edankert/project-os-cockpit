---
type: "[[task]]"
id: TASK-0123
aliases: ["TASK-0123"]
title: "Session index — per-workspace session metadata persistence"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0022-Session-Insight-And-Traceability]]"
effort: "M"
depends: ["[[TASK-0114]]"]
blocks: ["[[TASK-0124]]", "[[TASK-0125]]", "[[TASK-0126]]"]
related: []
tests: []
---

# Session index

## Definition of Done
- [ ] As hook events arrive, the sidecar records per-session metadata under `.cockpit/sessions.json`: session id, agent, start/end, prompts, files touched, cost snapshot, transcript path.
- [ ] Written atomically (temp+rename); bounded (most recent N sessions kept).
- [ ] Exposed via `GET /api/cockpit/sessions`; transcript files are read lazily and parsed defensively (metadata-only fallback on schema drift).

## Steps
- [ ] Session accumulator in `CockpitState` keyed by session_id; flush on `SessionEnd` and periodically while live.
- [ ] Atomic persistence + retention cap.
- [ ] `GET /api/cockpit/sessions` endpoint + tests.

## Notes
Transcript schemas are documented as version-unstable — never let a parse failure surface as an error.
