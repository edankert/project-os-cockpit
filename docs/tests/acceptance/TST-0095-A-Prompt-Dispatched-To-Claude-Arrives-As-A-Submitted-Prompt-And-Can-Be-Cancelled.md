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
tasks: ["[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]", "[[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]", "[[TASK-0658-A-Waiting-Prompt-Survives-The-Person-Pressing-Esc]]", "[[TASK-0659-A-Prompt-Held-After-Esc-Says-Claude-Is-Waiting-For-You]]", "[[TASK-0660-A-Dispatch-Checks-What-Runs-In-The-Terminal-Before-Typing]]", "[[TASK-0661-Every-Project-Uses-One-Codex-Hook-Command]]"]
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
8. In a plain terminal outside the cockpit, in the project's folder, run `~/Dev/repos/project-os-cockpit/.venv/bin/cockpit dispatch <the note's ID>`. (`cockpit` alone is on the PATH only inside a cockpit terminal.)
9. Exit Claude. Quit the application, start it from a terminal with `COCKPIT_NO_INSTRUMENT=1`, open a new terminal in the same project, run `claude`, and press the verb button.
10. Exit Claude, quit, and start the application normally. In a project's new terminal run `codex`, wait for its prompt, and press a verb button. The Agent menu does not need to say Codex.

## Expect

- In step 2 the prompt box never fills with the prompt character by character. The prompt appears in the transcript as a message, under a line Claude Code draws, "Prompt from the project-os-cockpit plugin", and Claude starts on it. Claude reads it as your words: its answer does not mention a plugin sending a message.
- In step 3 the newest dispatch names this session, and its time is when Claude started the turn, not earlier.
- In step 4 the row says "Waiting for Claude to finish its turn". Nothing is typed into the terminal. If you press Esc while it waits, the session shows "interrupted — waiting for your input", and the row says "Waiting for you: Claude was stopped, so this follows your next message to it". Type anything; when that turn ends, the prompt starts (TASK-0658, TASK-0659).
- In step 5 the waiting prompt starts as soon as Claude finishes, the row leaves the list, and the status line says "Delivered".
- In step 6 the row disappears when cancelled, and the status line says "Cancelled".
- In step 7 the cancelled prompt never appears in the session.
- In step 8 the prompt arrives in the cockpit's Claude session as in step 2, not typed.
- In step 9 the cockpit sees no Claude session: under the kill switch the plugin is not loaded, and the external hook stops too. Since TASK-0660 it checks what runs in the terminal before typing, finds Claude, and types nothing. The status line says "Claude is running in this terminal but the cockpit cannot reach it — queued", and the prompt waits in the queue list, where its `×` removes it. (Before TASK-0660 the cockpit typed `claude '<prompt>'` into Claude's prompt box. Edwin first accepted that, then chose the terminal check on 2026-10-14 with ISS-0322's fix.)
- In step 10 the prompt is pasted into Codex and submitted with a separate Return, even when Codex has not been prompted yet and so has not reported to the cockpit (TASK-0660). The note's dispatch history names `codex`, whatever the Agent menu says. The first Codex start after TASK-0661 shows Codex's hook review once; trust the hooks, and later Codex starts in any project do not ask again.

## Run on 2026-10-14: passed, all ten steps

Edwin ran it in project-os-deck after the application was rebuilt and restarted at 15:20 (local), in a new Claude session (`94462501`), started 15:41.

- Steps 1 and 2 passed. Implement on TASK-0084 at 14:44:46.76 UTC; the plugin submitted it and the turn started at 14:44:47.64. The prompt appeared under "Prompt from the project-os-cockpit plugin", and Claude worked on it as its own request.
- Step 3 passed (Edwin: "yep"). The ledger entry is on session `94462501`, timed 14:44:47.636, `delivered_by: submit`, with the turn's ID.
- Step 4 waited as it should: the second Implement, at 14:48:06, was held as `waiting`. Then Edwin pressed Esc, on the agent's suggestion. The plugin submitted the waiting prompt at 14:49:03, and Claude Code refused it ("the session was stopped and nobody has sent input since"), so it was recorded as `dropped`. That is a defect, fixed by [[TASK-0658-A-Waiting-Prompt-Survives-The-Person-Pressing-Esc]]. Steps 4 and 5 are to be run again in a session started after that fix.

Second session, after the fix: Claude session `864823b6`, started 14:54:58 UTC, in project-os-deck. The fix was committed at 14:50.

- Steps 1 to 3 passed again (Edwin: "I have done steps 3/4"). Implement on TASK-0084 at 14:55:14.56 UTC. The ledger entry is on session `864823b6`, timed 14:55:14.598, `delivered_by: submit`, delivery `d562989c0091`, with the turn's ID.
- Step 4 passed. Edwin pressed Implement again at 14:55:21.52, while Claude was working on the first prompt. The sidecar holds it as delivery `3582b92ac54c`, state `waiting`, and the session is `busy`. This time the long question was the first dispatched prompt itself, not a separate one.
- Step 5 did not run as written, because the running turn was stopped. Claude's transcript records `[Request interrupted by user]` at 14:55:28.95, seven seconds after the second Implement. The shell sends no Esc to a Claude session, so the stop came from the keyboard. From then on the plugin held the waiting prompt, as TASK-0658 makes it do. At 14:58:47 it was still `waiting`, and Edwin reported it as "stalled". Two things on screen were wrong while it was held. The row still said "Waiting for Claude to finish its turn", though Claude was waiting for Edwin. The sidecar still showed the session as `busy`, because Claude Code fires no `Stop` hook for a turn stopped with Esc.
- Step 5 then passed, through the path TASK-0658 added. Edwin typed "stop here, don't continue" at 15:02:10.37. When that turn ended, the plugin submitted the held prompt, and its turn started at 15:02:18.02. The ledger entry is on session `864823b6`, timed 15:02:18.056, `delivered_by: submit`, delivery `3582b92ac54c`. The queue was empty afterwards. Edwin: "it went through after I typed something". The two wrong things on screen are fixed by [[TASK-0659-A-Prompt-Held-After-Esc-Says-Claude-Is-Waiting-For-You]]; seeing them needs a session started after that fix and the window reloaded.

Third session, after TASK-0659 and a full restart of the application at 16:18 local: Claude session `922ebef6`, started 15:25:41 UTC, in project-os-deck.

- Implement on TASK-0084 was submitted, and its turn started at 15:26:42.09. Edwin pressed Implement again at 15:26:51.40; the sidecar held it as delivery `93762972b3b4`, `waiting`. Edwin then pressed Esc.
- At 15:26:54.92 the plugin's `Interrupt` arrived. The sidecar set the session to `needs-input` with "interrupted — waiting for your input", and marked the waiting prompt `waiting_for: you`. Both were unchanged at 15:28:18. Edwin confirmed the window showed both: the agent strip said "interrupted — waiting for your input", and the queue row said "Waiting for you: Claude was stopped, so this follows your next message to it" (Edwin: "1. yes").
- Edwin typed "stop this current step" at 15:30:02.64. When that turn ended, the held prompt was submitted, and its turn started at 15:30:08.37. The ledger entry is on session `922ebef6`, timed 15:30:08.414, `delivered_by: submit`, delivery `93762972b3b4`, and the queue was empty at 15:30:51. Steps 4 and 5 pass, including the Esc path.
- Step 6 passed. Implement at 15:31:58 started a turn at once (delivery `1569ce516380`, `delivered_by: submit`), and that turn was the long work. A second Implement while it ran was held, and Edwin cancelled it from the queue list. The sidecar recorded delivery `6b4bf2a6e33c` as cancelled at 15:32:12.77, and the session's dispatch history has it with `cancelled: true`. Edwin: "cancelled it, row disappeared and status said Cancelled".
- Step 7 passed. Claude's turn ended at 15:32:23.8. At 15:32:37 the session was idle and the queue empty. The session's prompts after 15:31 are the Implement at 15:31:58, Edwin's own "cancel" at 15:32:04 and a background task's notice at 15:32:19; the cancelled prompt is not among them.
- Step 8 passed. `cockpit` is not on the PATH of a plain macOS terminal, so Edwin ran `~/Dev/repos/project-os-cockpit/.venv/bin/cockpit dispatch TASK-0084` from `project-os-deck`. The request was recorded at 15:35:24.63 UTC. The plugin submitted the prompt, and its turn started at 15:35:31.96 (delivery `c50f1d9ab12a`, `delivered_by: submit`). Edwin: "it arrived as a submitted prompt". The prompt said "Read docs/ first" instead of naming the note's file; that is [[ISS-0320-A-Cockpit-Dispatch-From-The-Command-Line-Loses-The-Notes-Path]], which predates this feature.
- Step 9 failed, because the check's premise is wrong. The application was restarted at 16:40 local with `COCKPIT_NO_INSTRUMENT=1` (pid 58393; the variable confirmed in its environment). Edwin opened a new terminal in project-os-deck (tmux session created 16:41:36), ran `claude`, and pressed Implement on TASK-0083. The deck sidecar had no live session and no delivery. The cockpit took the terminal for a plain shell and typed `claude 'Work on TASK-0083. …'` into it, so the text landed in Claude's prompt box. The provenance line said "dispatched implement → pending delivery". Cause: the external hook (`external-hook/agent-state-hook.py`) returns at once when `COCKPIT_NO_INSTRUMENT` is set, and a cockpit terminal inherits it from the application. It also registers no `SessionStart`, so a session that has had no prompt yet is invisible even without the kill switch. The parenthesis under Expect, step 9, says this relies on the external hook; under the kill switch that hook is silent by design. Edwin, asked whether the cockpit should check what runs in the terminal before typing, chose to accept the behaviour and correct this check instead ("Accept it, fix the check"). The expected result for step 9 is rewritten to match, and against it step 9 passes: nothing went through the plugin, and the typed fallback appeared in Claude's prompt box.
- Step 10 failed, for a cause outside FEAT-0158. The application was restarted normally at 16:47 local (pid 60884, no kill switch). Edwin opened a new terminal in project-os-deck (tmux session created 16:48:11), ran `codex`, set the dispatch agent to Codex in the note's Agent menu, and pressed Implement on TASK-0083. The deck sidecar had no Codex session, so the cockpit took the terminal for a plain shell and typed `codex 'Work on TASK-0083. …'`. Edwin said "yes, it was submitted", but at 16:58 the line was still in Codex's composer: Codex showed "Context 0% used", had written no session record, and the process held none open. So no turn ran. The expected path, a pasted prompt and a separate Return, needs the cockpit to know Codex is running. No Codex event reached the sidecar. `codex` was launched through the cockpit's wrapper with its ten `-c hooks.*` flags, and `hook-env` names the right sidecar. Codex's log shows a hook review at 16:48:39. The cause is [[ISS-0322-Codex-In-A-Cockpit-Terminal-Reports-Nothing-To-The-Sidecar]].
- Edwin, on choosing Codex from the Agent menu: "That has to be automatic really ... it needs to be dependent on the current active agent in the project." Filed as [[ISS-0321-The-Dispatch-Agent-Is-Chosen-By-Hand-Not-From-The-Running-Agent]].

After TASK-0660 and TASK-0661, the application restarted at 17:19 local with `COCKPIT_NO_INSTRUMENT=1` (pid 74579, rebuilt from the committed code):

- Step 9 passed against the rewritten expectation. Edwin opened a new deck terminal (tmux session created 17:20:15), ran `claude`, and pressed Implement on TASK-0005. Nothing was typed: Claude's prompt box showed only its placeholder. The status line said the dispatch was queued (Edwin: "nothing was typed, the status line said it was queued"). The shell's saved queue held TASK-0005, `implement`.
- Step 10 passed. The application restarted normally at 17:23:02 local (pid 75997). Edwin opened a new deck terminal (tmux session created 17:23:38), ran `codex`, trusted the cockpit's hooks in Codex's review (written at 17:23:50), and pressed Implement on TASK-0005 without prompting Codex. The prompt arrived as Codex's message with no `codex '…'` wrapper, and Codex started on it (Edwin: "it was pasted and submitted, codex is working on it"). The ledger entry is timed 16:24:15.088 UTC, `agent: codex` although the Agent menu was never touched after step 9, `delivered_by: typed`. Codex's first hooks then reached the sidecar through the shared forwarder: session `01a13b3a…`, `busy`, from 16:24:15.88.
- Not yet shown: that one trust covers every project. All ten hooks in the running Codex use `instrument/codex-hook-forward.sh`. A recomputation of Codex's trust hash, which matched deck's old per-project commands exactly, matches none of the ten entries written at 17:23:50, for the shared command or any other; the cause is unknown. The direct check is to start Codex in a second project: it should not ask to review the hooks. Edwin tried it in your-applications.com, and Codex still asked (Edwin: "it still marked the hooks to review"). That Codex (pid 81506, 17:38:39) ran the old per-project command from a launcher no one had rewritten, in a terminal carrying your-trainer's instrument folder; see TASK-0661's "Gap found" section. To be repeated in a restarted terminal. Edwin restarted the your-applications.com terminal (tmux session created 17:42:32) and Codex asked once more (Edwin: "I restarted the terminal and was still asked"). Its command line (pid 83932) is byte-identical to deck's (pid 76443). The trust Codex then saved for `session_start` is `sha256:b80249ad…`, the same hash it saved at 17:23 from deck, so both projects' hooks hash alike. The 17:38 Codex, running the old command, had overwritten that entry with `sha256:fecd101e…` when Edwin trusted it, and that is why 17:42 asked. A third Codex start, in a terminal opened after the fix, should not ask.
- It did not. Edwin restarted the your-trainer terminal and ran `codex` (pid 84754, 17:44:02, the shared command in all ten hooks): "your-trainer didn't ask, it went straight to the prompt". Codex's `config.toml` was not written after 17:42:39. One trust covers every project.

**All ten steps pass.** Recorded in `docs/releases/ledgers/WORKING-macos.json` (TST-0095, pass, macOS, Edwin).

## Not this check

- Cancelling in the moment between the plugin's submit and the turn's start. It lasts too short a time to hit by hand; the plugin's tests and the sidecar's tests cover it ([[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]).
- "Too late to cancel": a person cannot reliably press Cancel in that moment either. The sidecar's tests cover the answer, and the shell's tests cover the message.
