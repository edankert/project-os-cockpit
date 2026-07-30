---
type: "[[task]]"
id: TASK-0248
aliases: ["TASK-0248"]
title: "Aggregate validator state for live workspaces in the main process"
status: backlog
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0028-Fleet-Health-Surface]]"]
parent: "[[FEAT-0028-Fleet-Health-Surface]]"
effort: S
depends: []
blocks: ["[[TASK-0250-Fleet-Badge-On-The-Rail]]", "[[TASK-0251-Fleet-Roll-Up]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[TASK-0150-Fleet-State-Proxy]]"]
tests: []
---

# TASK-0248 — Live-workspace validation aggregate

## Definition of Done
- [ ] The main process holds a per-workspace validation state: `{ state, errors, warnings, checked_at, source: 'live' }`
- [ ] Populated from each running sidecar's `GET /api/cockpit/validation`, refreshed on its `cockpit:validation` SSE event — **no polling for live workspaces**
- [ ] Exposed to the renderer over IPC, following `registerAgentsFleetIpc`'s shape
- [ ] A workspace whose sidecar dies degrades to `unknown` rather than freezing on its last value
- [ ] Zero new Python dependencies and no change to the sidecar

## Steps
- [ ] Add `registerFleetHealthIpc()` beside `registerAgentsFleetIpc()` in `desktop/src/ipc/`
- [ ] Resolve each workspace's sidecar via the existing `.cockpit/url` mechanism, and **reuse the janitor's root check** (`GET /api/cockpit/identity`, compare `root` against the workspace's realpath) — a url file can point at another workspace's port
- [ ] Subscribe to `cockpit:validation` per live workspace; fall back to one fetch on subscribe so state is populated before the first event
- [ ] Test: two fake sidecars, one drifting; assert the map, and assert a killed sidecar goes `unknown`

## Notes

This is deliberately the cheap half and it stands alone: it covers exactly the workspaces someone has open, needs no scheduling decisions, and adds no load — FEAT-0018 already built the endpoint and the event, and this only fans them in.

**Reuse the janitor's root check, do not re-derive it.** `main.ts`'s `janitorStaleUrls` exists because a `.cockpit/url` file can survive pointing at a port another workspace's sidecar has since taken, and it probes identity *and compares roots* for that reason. Fanning in validation state without that check would attribute one repo's drift to another — a wrong badge is worse than a grey one.

`checked_at` is carried from the sidecar rather than stamped on receipt: the distinction matters for the staleness marking [[TASK-0249]] needs, and re-stamping would make a cached report look fresh.
