---
type: "[[task]]"
id: TASK-0662
aliases: ["TASK-0662"]
title: "FEAT-0158 review round 1: a prompt being submitted when its session ends is shown as unconfirmed, a late turn start still counts, and it is never recorded as cancelled"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["FEAT-0158 independent review, round 1, 2026-10-14 (two reviewers)"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "S"
due: ""
depends: []
blocks: []
related: []
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# Review round 1: an unconfirmed prompt is not called cancelled

Reviewer A refuted criteria 3 and 7, and the author reproduced it. The plugin claims a prompt and submits it; then the session ends, or the sidecar restarts, before the plugin reports the turn's start. `_hold_deliveries_locked` moved the `sending` prompt back to `held`. The plugin's report was then refused (409), so the dispatch history never recorded a turn that may have run, and a cancel was accepted, writing "cancelled, before it reached the session".

## What changes

1. A `sending` prompt whose session ends, or whose sidecar restarts, becomes `dropped` with the reason "the session ended before Claude confirmed its turn, so it may have run". A `waiting` one is held, as now.
2. A report that the turn started is accepted from that state too, and stamps the dispatch history as usual: a late confirmation wins.
3. Removing a `dropped` prompt with `×` writes "removed" to the note's dispatch history, with the reason, not "cancelled before it reached the session".
4. The plugin retries its report that the turn started, up to three times a second apart, when the sidecar does not answer. A refusal is final.
5. Only `waiting` and `sending` prompts count toward the 30-prompt cap, so prompts nobody will submit cannot block new dispatches (both reviewers).
6. Tests for two things only the manual check guarded: the plugin submits with `asUser: true`, and the fleet view's queue depth adds the sidecar's `deliveries_open`.
7. TST-0095 is recorded as `passing`, with its date and all eight tasks.

## Not changed, with the reason

- The plugin does not re-check for a running turn after its claim returns. `$.prompt.submit` waits for the session to be idle itself, so a turn the person starts in that moment delays the prompt; it does not overlap it.
- A submit that resolves without any main-loop `turn.start` reports the next main-loop turn as the prompt's. That was the design in TASK-0655, and no case of it has been seen.
- A launcher that does not `exec` its agent would show as a shell. The cockpit's Codex launcher does `exec`; a Codex run through `node` is shown as `node` and held.
- With two live Claude sessions, one in a cockpit terminal and one outside, a delivery goes to the session `/api/cockpit/state` names. That predates this feature.

## Definition of Done

- [x] A sidecar test: claim, then `SessionEnd`, gives `dropped` with the unconfirmed reason; a later `started` stamps the history; and a removal of a dropped prompt writes `removed`, never `cancelled`. The same for a sidecar restart.
- [x] A plugin test: the started report is sent again after a failed attempt, and `asUser: true` is passed.
- [x] A test for the fleet queue depth.
- [x] A renderer test for the history line of a removed prompt.
- [x] Suites pass.

## Result, 2026-10-14

- `agent_hooks.py`: `_hold_deliveries_locked` holds a `waiting` prompt and drops a `sending` one with `DELIVERY_REASON_UNCONFIRMED`; `move_delivery` accepts `started` from that state and clears the reason; `cancel_delivery` writes `removed` and the reason for a dropped prompt; the cap counts only prompts that can still be submitted (`_can_still_be_submitted`, which includes a prompt held until a plugin claims its session).
- `register.ts`: `reportStarted` tries three times, a second apart, when the sidecar does not answer.
- `agents-fleet.ts`: `buildRow` is exported for its test. `renderer.ts`: `dispatchProvenanceText` writes the history line, with a removed case.
- Tests: four in `tests/test_deliveries.py` (unconfirmed at session end, removal recorded as removed, sidecar restart mid-submit, the cap); the session-end test updated; with the old hold, four fail. Plugin: "the report of a turn start …" (fails with `asUser` unset, and with one try). `desktop/tests/fleet-queue-depth.test.mjs` (fails with the line removed). `delivery-row.test.mjs` gains the history-line test.
