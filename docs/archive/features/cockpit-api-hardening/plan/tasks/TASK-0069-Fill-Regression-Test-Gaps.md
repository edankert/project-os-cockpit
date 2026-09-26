---
type: "[[task]]"
id: TASK-0069
aliases: ["TASK-0069"]
title: "Fill regression test gaps (focus POST, tab-state POST, SSE event shape)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0008"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# Fill regression test gaps

## Definition of Done
- [ ] `POST /api/cockpit/focus` has a test covering: happy path
      (note ID → resolved URL), 400 (missing target), 404
      (unresolvable target).
- [ ] `POST /api/cockpit/tab-state` has a test covering: happy
      path, 400 (missing tab_id/url), stale-tab pruning interaction
      with `/api/cockpit/state`.
- [ ] `GET /_events` SSE event shape covered: `cockpit:focus`
      event after a focus POST; `file-changed` event after a doc
      mutation under the watcher.
- [ ] Each new test paired with a TST-* note under
      `docs/features/cockpit-api-hardening/plan/tests/`.

## Steps
- [ ] Inventory gaps: walk every endpoint in TASK-0066's contract
      doc; check `tests/` for matching coverage; list misses.
- [ ] Implement focus + tab-state tests in
      `tests/test_cockpit_focus_and_tab_state.py` (or extend
      `test_cockpit_state.py`).
- [ ] Implement SSE shape test: connect to `/_events`, trigger a
      focus POST, read frames, assert event type + data payload.
      Mirror pattern from `test_cockpit_state.py`'s threaded
      server.
- [ ] Write TST-* notes.

## Notes
Some coverage exists already (`test_cockpit_state.py` records
agent-focus + tab-state at the `CockpitState` class level). This
task adds the HTTP-level tests so the wire contract is gated —
breaking the request/response shape fails CI even if the
in-memory class still works.
