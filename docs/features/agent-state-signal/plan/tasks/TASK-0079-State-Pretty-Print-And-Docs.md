---
type: "[[task]]"
id: TASK-0079
aliases: ["TASK-0079"]
title: "Pretty-print agent_state in `cockpit state` + COCKPIT-API.md updates"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0013"
effort: ""
due: ""
depends: ["[[TASK-0078]]"]
blocks: []
related: []
tests: []
---

# Pretty-print + contract doc

## Definition of Done
- [ ] `_print_state_pretty` in `cli.py` shows the new block:
      ```
      agent state : busy  (target: FEAT-0010, agent: claude)  @ 2026-05-25T17:00:00Z
      ```
      Missing fields elided cleanly. Line absent when no state
      recorded.
- [ ] `docs/references/COCKPIT-API.md`:
      - New section for `POST /api/cockpit/agent-state` (request
        shape, response, status codes, consumers).
      - Add `cockpit:agent-state` row to the SSE event table.
      - Update the schema-versioning section: SCHEMA_VERSION is now
        **3**; reason = "new SSE event name `cockpit:agent-state`".
      - Update `GET /api/cockpit/state` response example to include
        the `agent_state` block.
      - Decay rule documented at the bottom of the new section.
- [ ] Re-run the suite. TST-0006's parametrised header test now
      asserts `X-Cockpit-Schema: 3` on every endpoint — the test
      reads the constant, so it should keep passing without edits.
- [ ] Add `TST-0009` note describing the new test file.

## Steps
- [ ] Extend `_print_state_pretty`.
- [ ] Patch `docs/references/COCKPIT-API.md`.
- [ ] Write `docs/features/agent-state-signal/plan/tests/TST-0009-Agent-State.md`.
- [ ] Run full pytest; confirm everything green.

## Notes
Close-out gate. Once this lands, `cockpit signal busy` →
`cockpit state` from another terminal shows the state, and a
browser open on `/api/cockpit/state` shows the structured field.
