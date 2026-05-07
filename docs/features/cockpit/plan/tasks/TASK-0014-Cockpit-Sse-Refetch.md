---
type: "[[task]]"
id: TASK-0014
aliases: ["TASK-0014"]
title: "Cockpit SSE-driven pane re-fetch"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
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
- [ ] `cockpit.js` subscribes to `/_events` (the existing FEAT-0002 channel) using `EventSource`.
- [ ] On each `file-changed` event, the cockpit decides which pane(s) need a re-fetch:
  - **Always** re-fetch `/api/cockpit/nav` if the changed file is a feature note (`type: feature`, under any phase) — phase reassignment / status / goal changes there should reflect in the left pane.
  - **Always** re-fetch `/api/cockpit/context?this=<active>` if the changed file is the active note OR is referenced in the active note's current outbound/backlink set.
  - Otherwise, skip the re-fetch (typical noise — unrelated note edited).
- [ ] Bursts of `file-changed` events within 100 ms coalesce into a single re-fetch per pane.
- [ ] After a pane re-fetch, UI state preserved: which feature row is hovered (n/a for v1; just don't break it later), scroll position in the right pane, browser focus.
- [ ] Re-fetch failures (server temporarily down, JSON parse error, schema-version mismatch) show a quiet inline error banner on the affected pane and keep the previous render until the next successful fetch.
- [ ] Manual browser test:
  - Edit a feature note's `status` in your editor → left pane updates within ~200 ms, no full reload.
  - Edit the active note's body → centre pane re-renders (existing FEAT-0002 behaviour) AND right pane re-fetches if outbound links changed.
  - Edit a non-feature, non-active note → no pane re-fetch.

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
