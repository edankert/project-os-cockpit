---
type: "[[task]]"
id: TASK-0663
aliases: ["TASK-0663"]
title: "A `cockpit dispatch` request names the note's file and verb, an unknown ID is refused, and the request writes no history entry of its own"
status: done
phase: "[[PHASE-007]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[ISS-0320-A-Cockpit-Dispatch-From-The-Command-Line-Loses-The-Notes-Path]]", "Edwin 2026-10-14: 'fix ISS-0320 ... you found this, you prioritized this, you should fix this.'"]
parent: "[[FEAT-0025-Dispatch-Runtime]]"
effort: "XS"
due: ""
depends: []
blocks: []
related: ["[[TASK-0136]]", "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
tests: []
---

# A cockpit dispatch request names the note's file

The fix for [[ISS-0320-A-Cockpit-Dispatch-From-The-Command-Line-Loses-The-Notes-Path]], which says what was wrong and why.

## Definition of Done

- [x] `POST /api/cockpit/dispatch` with `enqueue` resolves the ID through the project's index and puts `rel` on the request; an unknown ID gets 404 and "no note with ID … in this project".
- [x] A request writes no dispatch-history entry; the delivery writes the one entry.
- [x] The window takes the request's `rel` (`dispatchRequestRel`), the quick switcher's list only as a fallback, and `dispatchToAgent` records the verb it used.
- [x] Tests fail without the fix.

## Result, 2026-10-14

- `server.py` `_serve_cockpit_dispatch`; `agent_hooks.py` `record_dispatch` (new `rel`, and an `enqueue` request returns before the ledger); `renderer.ts` `dispatchRequestRel`, `handleDispatchRequest`, `dispatchToAgent`.
- Tests: `test_a_cli_request_names_the_notes_file_and_writes_no_history_of_its_own` in `tests/test_dispatch_ledger.py` (with the ledger write put back, it fails); "a cockpit dispatch request uses the file the sidecar names" in `desktop/tests/delivery-row.test.mjs`.
- Suites: pytest 2173 passed, 11 skipped; desktop 215 passed.

Not seen in the running application: the sidecar change needs a restart of the cockpit, and the window a reload.
