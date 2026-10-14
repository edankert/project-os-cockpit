---
type: "[[task]]"
id: TASK-0659
aliases: ["TASK-0659"]
title: "After the person stops a Claude turn with Esc, the cockpit shows the session waiting for them, and a held prompt's row says it follows their next message"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]], second run of steps 4 and 5, 2026-10-14", "Edwin 2026-10-14: 'not sure but it doesn't seem to run the queued item ... it seems to be staleld'"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "S"
due: ""
depends: ["[[TASK-0658-A-Waiting-Prompt-Survives-The-Person-Pressing-Esc]]"]
blocks: []
related: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# A prompt held after Esc says Claude is waiting for you

Found in the second run of TST-0095 on 2026-10-14. Edwin stopped a Claude turn with Esc while a dispatched prompt was waiting. Since TASK-0658 the plugin holds that prompt until the person has sent Claude something and that turn has ended, which is correct. But the cockpit showed nothing of this, and Edwin read it as "stalled":

- The queue row still said "Waiting for Claude to finish its turn". Claude had finished; it was waiting for Edwin.
- The session still showed as `busy`, three minutes after the stop. Claude Code fires no `Stop` hook for a turn stopped with Esc, so the sidecar never heard that the turn ended.

The second problem predates FEAT-0158: every Claude session stopped with Esc has shown `busy` until its next event. It is fixed here because the same event fixes both, and the plugin that sends it is FEAT-0158's.

## What changes

1. The plugin tells the sidecar when a main-loop turn ends with `isAborted`. It posts an `Interrupt` event, the event a Codex session already sends when it is stopped.
2. The sidecar treats `Interrupt` from a Claude session as it does from Codex. The session shows "interrupted — waiting for your input" until the person's next prompt.
3. While a session is interrupted, each prompt waiting for it carries `waiting_for: "you"`, and the sidecar publishes that change. The person's next prompt removes it.
4. The queue row for such a prompt says "Waiting for you: Claude was stopped, so this follows your next message to it".

## Definition of Done

- [x] A plugin test: a main-loop turn that ends with `isAborted` posts one `Interrupt` event to the sidecar; one that ends normally posts none.
- [x] A sidecar test: an `Interrupt` from a Claude session sets it to `needs-input`, marks its waiting prompts `waiting_for: "you"` and publishes them, and the next `UserPromptSubmit` sets it `busy` and clears the mark. A prompt added while the session is interrupted starts marked.
- [x] A renderer test: a waiting prompt marked `waiting_for: "you"` gets the new row text.
- [x] `claude plugin validate` and `claude plugin test` pass; the Python and renderer suites pass.
- [x] The capability register is updated: the queue row and the session state now say something new.

## Result, 2026-10-14

- `register.ts`: a main-loop `turn.complete` with `isAborted` posts `{hook_event_name: "Interrupt"}` for the session, marked as the plugin's. Test: "a turn stopped with Esc tells the sidecar, and a finished one does not" in `tests/delivery.test.ts`. With the post removed it fails.
- `agent_hooks.py`: `Interrupt` is no longer Codex-only. The session goes to `needs-input` with "interrupted — waiting for your input" and stays there until the next `UserPromptSubmit`. `_mark_waiting_for_person_locked` sets or clears `waiting_for: "you"` on the session's waiting deliveries and queues each change for publishing; `add_delivery` sets it for a session already interrupted. Test: `test_a_claude_session_stopped_with_esc_waits_for_the_person` in `tests/test_deliveries.py`. With `Interrupt` made Codex-only again it fails.
- `renderer.ts`: `deliveryRowText` gives the new text for a waiting delivery with `waiting_for: "you"`. Test: `desktop/tests/delivery-row.test.mjs`.
- Suites: `claude plugin test` 22 passed; `claude plugin validate` passed with warnings; desktop node suite 203 passed; `.venv/bin/python -m pytest -q -p no:randomly` 2167 passed, 11 skipped (foreground).

Not seen in the running application yet. The plugin part needs a Claude session started after this change, and the row text needs the window reloaded from the new build.
