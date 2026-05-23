---
type: "[[task]]"
id: TASK-0014
aliases: ["TASK-0014"]
title: "Cockpit SSE-driven pane re-fetch"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0013]]"]
blocks: []
related: ["[[FEAT-0002]]", "[[ADR-0004]]"]
tests: []
---

# Cockpit SSE-driven pane re-fetch

## Definition of Done
- [x] `cockpit.js` subscribes to `file-changed` events on `/_events` (the existing FEAT-0002 channel) inside `mountCockpitEventStream`.
- [x] On any `file-changed` event, the cockpit re-fetches all three panes (left via `loadLeftPane()`, centre + right via `navigateTo(current_url, {replace: true})`). Terminal iframe survives — no full `location.reload()`.
- [x] Bursts of `file-changed` events within 150 ms coalesce into a single re-fetch (debounce in `scheduleSoftReload`).
- [x] `sse-reload.js` bails when the cockpit shell is mounted (presence of `#cockpit-centre`) so its `location.reload()` doesn't fire alongside the soft refresh. Non-cockpit pages (notices, errors) still get the full reload.
- [x] Manual browser test: edit any note → centre + left + right re-render within ~200 ms, terminal session intact.

## Disposition
**v1 ships the always-refresh-all-three-panes path.** The original DoD's per-pane targeting (only re-fetch nav when a feature changed, only re-fetch context when the active note's link set was touched) is parked as v2 — for a 1388-note repo the always-refresh path is fast enough and avoids the complexity of file-type detection + outbound-set caching client-side. Originally deferred (the .base-driven plan in [[TASK-0011]] was superseded by [[ADR-0004]]); v1 shipped on 2026-05-23 to fix the embedded-terminal session getting torn down by sse-reload.js.

## Steps
- [ ] Determine "is this file a feature?" client-side cheaply — either via the file path heuristic (e.g. `features/.../FEAT-####-*.md`) OR by extending the SSE event payload with a `type` hint.
  - Lean toward the path heuristic for now; the event payload extension is a TASK-0011-style upgrade we can layer later if needed.
- [ ] Determine "is this file in the active note's outbound/backlink set?" — keep a snapshot of the most recent `context` payload's `linked` + `backlinks` URLs in JS state; compare on event.
- [ ] Implement coalescing: 100 ms debounce per pane key; if more events arrive in the window they're absorbed into a single re-fetch.
- [ ] Implement the inline error banner (a small `.cockpit-error` element with the server's message, hidden when the next fetch succeeds).
- [ ] Manual browser tests for the four event-kind scenarios above.

## Notes
This is the equivalent of the deferred TASK-0011 but pointed at the new code-driven endpoints. The event channel and the event payload haven't changed — TASK-0006's SSE infrastructure carries us directly.

**Coalescing budget**: 100 ms picks up the burst from a typical editor save. If the user saves twice quickly, the second save might arrive within 100 ms of the first and coalesce — fine, the second re-fetch sees both changes' final state anyway.

**Future**: when the cockpit grows interactive controls (column sort, filter input, the graph pane), they're all JS-only changes against the same JSON contract. SSE re-fetch logic stays — what changes is what each pane does with the fetched data.

The "active note's outbound/backlink set" snapshot in JS is a small client-side cache. It only needs to live as long as the page; no persistence. Keep it in a closure variable, not localStorage.
