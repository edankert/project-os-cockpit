---
type: "[[task]]"
id: TASK-0248
aliases: ["TASK-0248"]
title: "Aggregate validator state for live workspaces in the main process"
status: done
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
- [x] The main process holds a per-workspace validation state: `{ state, errors, warnings, checked_at, source: 'live' }`
- [x] Populated from each running sidecar's `GET /api/cockpit/validation`, refreshed on its `cockpit:validation` SSE event — **no polling for live workspaces**
- [x] Exposed to the renderer over IPC, following `registerAgentsFleetIpc`'s shape
- [x] A workspace whose sidecar dies degrades to `unknown` rather than freezing on its last value
- [x] Zero new Python dependencies and no change to the sidecar

## Steps
- [x] Add `registerFleetHealthIpc()` beside `registerAgentsFleetIpc()` in `desktop/src/ipc/`
- [x] Resolve each workspace's sidecar via the existing `.cockpit/url` mechanism, and **reuse the janitor's root check** (`GET /api/cockpit/identity`, compare `root` against the workspace's realpath) — a url file can point at another workspace's port
- [x] Subscribe to `cockpit:validation` per live workspace; fall back to one fetch on subscribe so state is populated before the first event
- [x] Test: two fake sidecars, one drifting; assert the map, and assert a killed sidecar goes `unknown`

## Notes

This is deliberately the cheap half and it stands alone: it covers exactly the workspaces someone has open, needs no scheduling decisions, and adds no load — FEAT-0018 already built the endpoint and the event, and this only fans them in.

**Reuse the janitor's root check, do not re-derive it.** `main.ts`'s `janitorStaleUrls` exists because a `.cockpit/url` file can survive pointing at a port another workspace's sidecar has since taken, and it probes identity *and compares roots* for that reason. Fanning in validation state without that check would attribute one repo's drift to another — a wrong badge is worse than a grey one.

`checked_at` is carried from the sidecar rather than stamped on receipt: the distinction matters for the staleness marking [[TASK-0249]] needs, and re-stamping would make a cached report look fresh.

## Done 2026-07-30

`desktop/src/ipc/fleet-health.ts`. One row per discovered workspace: `{state, errors, warnings, checkedAt, source, detail?}`, fanned in from each live sidecar's `GET /api/cockpit/validation` and refreshed on its `cockpit:validation` SSE event. No polling — a 30 s reconcile only notices sidecars that appeared or vanished; the state itself is pushed.

**"Live" means either sidecar.** An in-app sidecar (`sidecarUrlFor`) or a standalone `project-os-cockpit` in a terminal, found through `.cockpit/url`. The `~agents` screen already treats both as live and it would be strange for this to disagree.

**The identity check is the part that matters, and it is guarded.** A `.cockpit/url` file survives an unclean exit pointing at a port another workspace's sidecar may claim next launch ([[ISS-0007]]) — which is why `main.ts` has a janitor for it. Without the root comparison, one repo's drift gets reported against another. `a .cockpit/url answering a DIFFERENT root is not trusted` asserts both halves: a wrong-root sidecar colours nothing, and the *same server* with a corrected root does colour it, so the assertion cannot pass because the fetch failed for an unrelated reason. Mutation-verified by deleting the comparison.

**A dead sidecar degrades to `unknown`, and drops its counts.** Keeping the last report would age silently into a lie about a repo nobody is watching. Mutation-verified by making `degrade` a no-op.

`checkedAt` is carried from the sidecar, never stamped on receipt — [[TASK-0249]]'s staleness marking reads it, and re-stamping would make a cached report look freshly checked.

### The test approach is a departure worth naming

Every other desktop guard in this repo greps TypeScript *source*. Both design-bench reviewers independently walked through one of those ([[ISS-0055]]'s closing observation): a rename and the guard still passes.

`desktop/tests/fleet-health.test.mjs` runs the **built** module against real HTTP servers via `node --test` — stdlib since Node 18, so no new dependency. `tests/test_desktop_node_suite.py` runs it from pytest so the repo keeps one test command; a suite nobody remembers to run is a suite that rots.

Two false starts worth recording, both mine: the fake sidecar's `server.close()` hung because undici keeps `fetch` sockets alive (`closeAllConnections()` fixes it), and the SSE case pushed before the subscriber's socket had attached, so it was asserting nothing. Both looked like product bugs first.
