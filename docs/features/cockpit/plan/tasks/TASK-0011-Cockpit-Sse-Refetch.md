---
type: "[[task]]"
id: TASK-0011
aliases: ["TASK-0011"]
title: "Cockpit SSE-driven re-fetch"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: S
due: ""
depends: [TASK-0010]
blocks: []
related: ["[[FEAT-0002]]"]
tests: []
---

# Cockpit SSE-driven re-fetch

> **Deferred (2026-05-08).** [[ADR-0004]] moved the cockpit off `.base`-driven panes; the SSE wiring for the new code-driven cockpit is [[TASK-0014]]. The frontmatter-vs-body-vs-base event-kind discrimination captured below is parked for the future `.base`-rendering use case.

## Definition of Done
- [ ] FEAT-0002's SSE channel emits a typed event payload: `{kind: "frontmatter" | "body" | "base", path: "..."}`. (Coordinate with FEAT-0002 — if the channel currently emits a simpler shape, this task extends it.)
- [ ] `cockpit.js` subscribes to `/_events` (the existing SSE endpoint) and dispatches:
  - `kind: "frontmatter"` on any path → re-fetch every mounted pane (frontmatter is what the evaluator reads). Coalesce bursts within 50 ms into one re-fetch per pane.
  - `kind: "body"` on the active note → soft-reload only the centre pane (this is FEAT-0002's existing behaviour — preserve it).
  - `kind: "body"` on a non-active note → no-op (no pane depends on body content).
  - `kind: "base"` (a `.base` file changed) → re-fetch any pane mounting that base path.
- [ ] Watcher (`docs_server.watcher`) emits `frontmatter` vs `body` correctly: parse the changed file, diff its frontmatter against the previous `Index.get(path)` snapshot, emit `frontmatter` if any frontmatter key changed (including additions/removals), `body` otherwise.
- [ ] After every re-fetch, the pane preserves UI state: which tab is active, which groups are collapsed, scroll position. State lives in a per-pane object keyed by base path, not in the DOM.
- [ ] Re-fetch failures (e.g. `.base` parse error post-edit) show an inline error banner on the affected pane with the server's 422 message, instead of blanking the pane.
- [ ] Manual browser test: edit a frontmatter `status:` in your editor → both side panes update within 1 second without a full reload. Edit a `.base` file's `views[]` → that pane re-renders with the new view set. Edit a non-active note's body → nothing happens.

## Steps
- [ ] Extend the watcher event payload in `docs_server.watcher` to include `kind`.
- [ ] Implement frontmatter-vs-body diff in the watcher (use the previous `Index.get(path)` snapshot).
- [ ] Add `/_events` subscription handling in `cockpit.js` (use the browser's `EventSource` — already used by FEAT-0002's reload script).
- [ ] Implement the per-pane state preservation (`activeTab`, `collapsedGroups`, `scrollTop` survive a re-fetch).
- [ ] Implement coalescing (debounce 50 ms — short enough to feel instant, long enough to absorb a save-burst from a typing editor).
- [ ] Implement the inline error banner.
- [ ] Manual browser tests for the four event-kind scenarios.

## Notes
The 50ms coalescing window is empirical — start there, tune if it feels laggy.

This task closes the loop between Obsidian's "edit frontmatter, see Bases dashboard update" experience and the cockpit's web equivalent.
