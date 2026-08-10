---
type: "[[task]]"
id: TASK-0372
aliases: ["TASK-0372"]
title: "The manual test runner moves from the desk to the Tests view, unchanged in what it writes"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
parent: "[[FEAT-0086-Tests-Becomes-A-View]]"
effort: M
due: ""
depends: ["[[TASK-0371-The-Tests-View-And-Its-Register]]"]
blocks: []
related: ["[[TST-0021-Review-Desk]]", "[[TST-0011-Overview-And-Review-Desk]]"]
tests: ["[[TST-0021-Review-Desk]]"]
---

# The runner moves

## Definition of Done
- [x] The stepper runs from the Tests view: steps parsed from the note, Pass/Fail/Skip, evidence — the navigator lists the tests, a test note carries a `Run ▸ N steps` button, and the run happens at `~tests/<TST>/run`
- [x] `stamp_test_run` writes exactly what it writes today — `status`, `last_run`, the `## Runs` entry — with the same allow-list, mtime precondition and loopback check — evidence: `test_a_run_writes_what_it_always_wrote`, a real POST through the real handler asserting the note is untouched line for line outside the four fields the run owns
- [x] A fail still drafts its `ISS-*` — **it did not, and now it does**; see below
- [x] `~review/<TST>/run` deep links migrate to the new route — evidence: `test_the_run_route_moved_and_the_old_one_redirects`
- [x] No write path changed; the diff is routing and placement only — with one disclosure, below

## Steps
- [x] Move `buildTestRunner` and its route; leave `note_writes` untouched
- [x] Add the redirect from the old route
- [x] Re-run the round-trip assertion: a stamped note is byte-identical outside its allow-listed fields

## Notes
The runner is the desk's one piece of genuine machinery and the reason its removal is a move rather than a deletion. Everything guarding it lives server-side and must not be touched by a renderer change — if this task ends up editing `note_writes.py`, something has gone wrong.

[[TST-0011]] exercises the desk and will need its steps updated for the new location.

## Done 2026-08-10

### The promise that had no implementation

*"A fail still drafts its `ISS-*`"* presumes it did. **It did not.**

`note_writes.draft_issue_body` was written for TASK-0209 and shapes a failing step into an issue — title, the step, what the note expected, what was observed. Its only caller in the tree was `test_failing_step_drafts_an_issue_for_confirmation`, which calls it directly. `stamp_test_run` returned `id`, `outcome` and `last_run`, and never mentioned it.

Two records said otherwise, in the two places a reader would look:

- [[TST-0021]]: *"A failing step produces an issue draft — returned as data for the user to confirm, never filed automatically."*
- The run summary itself, on screen after a failing run: *"An issue draft will be offered for the first failing step — filing it stays your call."*

Both were true of the function and false of the system, for a month. It is the shape this session keeps finding — a surface asserting something nobody had read next to the behaviour — and the only reason it surfaced here is that moving a thing means reading it.

**Made true rather than deleted**, because the design was right and the wiring was missing. `POST /api/notes/test-run` now returns `issue_draft` on a completed failing run; the run stops on an offer instead of navigating away; the button seeds [[FEAT-0059]]'s capture box with the server's title and body, and a person presses Enter. Never filed automatically — allocating an id is a documentation decision LIFECYCLE puts in preflight, which is what `draft_issue_body`'s own docstring said all along.

### The disclosure: `note_writes.py` is not byte-identical

The Notes section says *"if this task ends up editing `note_writes.py`, something has gone wrong"*. It has two changed lines, and neither is a write path:

1. `draft_issue_body`'s body text said *"from the review desk"*. The runner is not on the desk any more, so every issue drafted from a failing run would have named a surface that no longer exists.
2. Its docstring, recording that it is now wired to the endpoint's **response**.

The draft assembly itself is in `server.py::_serve_test_run`, deliberately: it shapes a response and writes nothing, so putting it inside `stamp_test_run` would have moved the constraint this task was given. `stamp_test_run`'s body and return value are unchanged.

### What moved, and what did not

**Moved:** the route (`~tests/<TST>/run`), the entry points (the verification panel's `Run ▸`, the scope's *Validate this scope*, the desk queue's run rows), and the left pane during a run — the Tests navigator rather than the queue, so the run happens inside the view that owns the subject ([[ADR-0020]]).

**New, because the DoD needs it:** a `Run ▸ N steps` button on a manual test note. It is deliberately **not** an entry in the actuator row: that row is `/api/notes/actions`, which is the human-owned status transitions and nothing else ([[REQ-0026]]). Starting a run sets no status — recording it does, afterwards — so an entry there would put a non-transition in the one place whose whole meaning is transitions. The button appears only when the server reports parsable steps, using the same `manual_test_steps` parse the runner uses, so it can never open a stepper with nothing in it.

**Deleted:** `renderReviewPage`'s `opts.run` branch. Once the redirect intercepts `~review/<id>/run` nothing can reach it, and a second unreachable copy of the runner's entry point is how a "moved" surface stays in two places. `test_the_run_route_moved_and_the_old_one_redirects` fails if `opts.run` comes back.

**Unchanged:** `/api/cockpit/review/<id>` still serves the runner its detail. The endpoint is not the desk — it resolves any note id and adds the test fields — and FEAT-0008's API-stability rule is explicit that retiring a UI route does not retire an endpoint. [[TASK-0378]] takes the route; this survives it.

### Verification

`901 passed, 2 skipped`; `validate-docs: OK`; desktop `tsc --noEmit` clean and `dist/` rebuilt. Five new assertions, four of them driving a real HTTP server rather than reading source — the lesson [[ISS-0055]] closed on, and the reason the write-path claim in the DoD can be made at all.

Adequacy by mutation, each applied and reverted:

| mutation | killed by |
|---|---|
| never attach the draft | `test_a_failing_run_returns_the_draft_it_always_promised` |
| attach it to an aborted run too | `test_only_a_completed_failure_carries_a_draft[-True-fail]` |
| append the run log at the body end rather than the end of `## Runs` | `test_a_run_writes_what_it_always_wrote` |

The second of those found a defect **in my own test first**: the aborted case sent a *passing* step, so `first_fail` was `None` whatever the code did and the mutation survived. The parametrisation now sends a failing step in a run the person walked out of, which is the case the guard exists for.

### Corrected records

[[TST-0021]] gained a dated correction rather than a rewrite: the claim about the issue draft was true when written about the function and became false about the system the moment nothing called it. That is worth keeping visible.

The Notes section above says [[TST-0011]] "exercises the desk". It does not. TST-0011 is the agent-hook instrumentation demo, and its `## Checklist` is the corpus the step parser was taught to read; it carries no desk steps at all. TST-0021 is the desk's test and is where the correction went. The plan's sentence stays as written — a task note records what was planned, not what it would be tidier to have planned.
