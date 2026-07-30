---
type: "[[task]]"
id: TASK-0252
aliases: ["TASK-0252"]
title: "Subscribe the renderer to cockpit:validation so the active repo's errors are live in the shell"
status: done
phase: "[[PHASE-016-Errors-Become-Work]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0051-Validator-Errors-As-Session-Work]]"]
parent: "[[FEAT-0051-Validator-Errors-As-Session-Work]]"
effort: S
depends: []
blocks: ["[[TASK-0253-Error-Rows-In-The-Session-Summary]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]"]
tests: []
---

# The errors reach the renderer

## Definition of Done
- [x] The desktop renderer holds the **full** validation report for the active workspace — errors with `code`, `message`, `id`, `rel`, `url` — not just a count
- [x] It is primed by one fetch when the sidecar becomes ready, and kept current by the `cockpit:validation` SSE event
- [x] Switching workspace replaces it rather than merging two repos' errors
- [x] No new endpoint and no change to the sidecar

## Steps
- [x] Add a `cockpit:validation` listener beside the four the renderer's `EventSource` already carries
- [x] Prime on sidecar-ready with a single `GET /api/cockpit/validation`
- [x] Clear on workspace switch and on sidecar exit
- [x] Test: the report is exposed in a form a guard can assert, and a stale repo's errors do not survive a switch

## Notes

Pure plumbing — every piece exists. [[FEAT-0018]] built the endpoint and the event; the renderer already opens an `EventSource` on the sidecar and listens to four other `cockpit:*` events on it. It simply never subscribed to this one, which is why the desktop shell has had no way to see its own repo's violations since that feature shipped.

The **fleet** state ([[FEAT-0028]]) deliberately carries counts only, and stays that way: this is one repo, live, over a connection that is already open.

## Done 2026-07-30

A `cockpit:validation` listener on the `EventSource` the renderer already holds, primed by one fetch on attach — the event only fires on **change**, so a repo failing since before we connected would otherwise never report.

Cleared at all three points where `sidecarBaseUrl` is dropped (workspace switch, sidecar failed, sidecar exited). Keeping the last report would put one repo's violations under another repo's session — [[FEAT-0028]]'s identity bug one scope down.

**Verified live:** creating a bad note produced `COUNTER` and `METRICS` in the renderer within the debounce window, over SSE, with `id`, `rel` and the deep-link `url` intact.
