---
type: "[[task]]"
id: TASK-0658
aliases: ["TASK-0658"]
title: "A prompt waiting for a Claude session is held, not lost, when the person stops the running turn with Esc"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]], step 4, run on 2026-10-14"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "XS"
due: ""
depends: ["[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]"]
blocks: []
related: []
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# A waiting prompt survives the person pressing Esc

Found while Edwin ran TST-0095 on 2026-10-14. A prompt dispatched while Claude was busy waited, as it should. Edwin then pressed Esc to end the running turn. The plugin saw the turn end, took the session to be idle, and submitted the waiting prompt at once. Claude Code refused it: "the session was stopped and nobody has sent input since". After an interruption it takes no prompt from a plugin until the person sends input. The sidecar recorded the delivery as `dropped`, so the prompt was lost. The plugin is code FEAT-0158 wrote, so it is fixed here.

## Definition of Done

- [x] After a main-loop turn ends with `isAborted`, the plugin submits nothing until a turn it did not start has begun and ended.
- [x] A plugin test holds a waiting prompt after an aborted turn, through the person's next turn, and submits it once that turn ends. Removing the hold fails it.
- [x] `claude plugin validate` and `claude plugin test` pass.

## Result, 2026-10-14

`register.ts`: `DeliveryState.interrupted` is set when a main-loop `turn.complete` has `isAborted`, and cleared by a main-loop `turn.start` the plugin did not cause. `deliverOne` does nothing while it is set. Test: "a waiting prompt is held until the person has sent input and that turn ended" in `tests/delivery.test.ts`; with the line that sets the flag removed, it fails. `claude plugin test`: 21 passed. `claude plugin validate`: passed with warnings.

While the prompt is held, its row still says "Waiting for Claude to finish its turn". It does not say that Claude is waiting for the person; the plugin does not tell the sidecar why it is holding.

The plugin code is loaded when `claude` starts, so a session started before this change still has the old behaviour.
