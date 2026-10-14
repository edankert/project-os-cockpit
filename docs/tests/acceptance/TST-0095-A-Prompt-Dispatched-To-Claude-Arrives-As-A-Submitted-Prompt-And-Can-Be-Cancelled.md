---
type: "[[test]]"
id: TST-0095
aliases: ["TST-0095"]
title: "A prompt dispatched to a Claude session arrives as a submitted prompt, counts as delivered when its turn starts, and can be cancelled until then"
status: active
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
scope: feature
level: acceptance
entrypoint: "A note's verb button, with a new cockpit terminal running `claude`"
command: ""
last_verified: ""
covers: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
issues: []
tasks: ["[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]", "[[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]"]
artifacts: []
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]", "[[TST-0011-Live-Session-Instrumentation]]"]
area: ""
after: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]"]
tags: [test, acceptance, cockpit-plugin, dispatch, claude-code]
---

# A prompt dispatched to Claude arrives as a submitted prompt and can be cancelled

## Purpose

Proves that a prompt dispatched from the cockpit to a Claude session is submitted by the cockpit plugin rather than typed. It also proves that the cockpit counts it as delivered only when the session's turn starts, that a person can cancel it until then, and that Codex dispatches are unchanged.

Set to `active` on 2026-10-14, when the feature started. All four tasks were built the same day; this check is Edwin's to run after a rebuild and restart.

## Setup

The desktop application rebuilt from these sources (`npm run build` in `desktop/`) and restarted. A project whose cockpit terminal is new (closed with the terminal's restart button after the restart), so it loads the plugin. A note in that project with a verb button, for example "Implement" or "Review" (the buttons depend on the note's status).

## Steps

1. In the project's terminal run `claude` and wait for the prompt. Press a note's verb button.
2. Watch the terminal's prompt box while the dispatch arrives, then read the first line of Claude's answer.
3. Open the note again and look at its dispatch history.
4. Ask Claude something that takes a minute, for example to read every task note in one feature. While it works, press the verb button again. Open the queue list from the `queued` chip in the agent strip.
5. Let Claude finish.
6. Ask Claude another long question. While it works, press the verb button and cancel the new row in the queue list.
7. Let Claude finish, and wait ten seconds.
8. Run `cockpit dispatch <the note's ID>` in a plain terminal outside the cockpit.
9. Exit Claude. Quit the application, start it from a terminal with `COCKPIT_NO_INSTRUMENT=1`, open a new terminal in the same project, run `claude`, and press the verb button.
10. Exit Claude, quit, and start the application normally. In a project's new terminal run `codex`, and press a verb button with Codex chosen as the agent.

## Expect

- In step 2 the prompt box never fills with the prompt character by character. The prompt appears in the transcript as a message, under a line Claude Code draws, "Prompt from the project-os-cockpit plugin", and Claude starts on it. Claude reads it as your words: its answer does not mention a plugin sending a message.
- In step 3 the newest dispatch names this session, and its time is when Claude started the turn, not earlier.
- In step 4 the row says "Waiting for Claude to finish its turn". Nothing is typed into the terminal.
- In step 5 the waiting prompt starts as soon as Claude finishes, the row leaves the list, and the status line says "Delivered".
- In step 6 the row disappears when cancelled, and the status line says "Cancelled".
- In step 7 the cancelled prompt never appears in the session.
- In step 8 the prompt arrives in the cockpit's Claude session as in step 2, not typed.
- In step 9 nothing is typed into the terminal. (This relies on the external hook in your `~/.claude/settings.json`, which tells the cockpit a Claude session is running. Without it, the cockpit sees no session at all under the kill switch, and falls back to running `claude '<prompt>'` in the shell, as it always has for a terminal with no session.) The chip turns amber and says `1 not delivered`, and the row says "Not delivered: this Claude session has no cockpit plugin". Its `×` removes it.
- In step 10 the prompt is pasted into Codex and submitted, as before this change.

## Run on 2026-10-14 (in progress)

Edwin ran it in project-os-deck after the application was rebuilt and restarted at 15:20 (local), in a new Claude session (`94462501`), started 15:41.

- Steps 1 and 2 passed. Implement on TASK-0084 at 14:44:46.76 UTC; the plugin submitted it and the turn started at 14:44:47.64. The prompt appeared under "Prompt from the project-os-cockpit plugin", and Claude worked on it as its own request.
- Step 3 passed (Edwin: "yep"). The ledger entry is on session `94462501`, timed 14:44:47.636, `delivered_by: submit`, with the turn's ID.
- Step 4 waited as it should: the second Implement, at 14:48:06, was held as `waiting`. Then Edwin pressed Esc, on the agent's suggestion. The plugin submitted the waiting prompt at 14:49:03, and Claude Code refused it ("the session was stopped and nobody has sent input since"), so it was recorded as `dropped`. That is a defect, fixed by [[TASK-0658-A-Waiting-Prompt-Survives-The-Person-Pressing-Esc]]. Steps 4 and 5 are to be run again in a session started after that fix.

## Not this check

- Cancelling in the moment between the plugin's submit and the turn's start. It lasts too short a time to hit by hand; the plugin's tests and the sidecar's tests cover it ([[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]).
- "Too late to cancel": a person cannot reliably press Cancel in that moment either. The sidecar's tests cover the answer, and the shell's tests cover the message.
