---
type: "[[change]]"
id: CHG-20261014-A-Prompt-Dispatched-To-Claude-Is-Submitted-Not-Typed
title: "A prompt dispatched to a Claude session is submitted by the cockpit plugin, never typed, counted as delivered when its turn starts, and can be cancelled until then"
status: merged
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]", "[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]", "[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]", "[[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]", "[[TASK-0658-A-Waiting-Prompt-Survives-The-Person-Pressing-Esc]]", "[[TASK-0659-A-Prompt-Held-After-Esc-Says-Claude-Is-Waiting-For-You]]", "[[TASK-0660-A-Dispatch-Checks-What-Runs-In-The-Terminal-Before-Typing]]", "[[TASK-0661-Every-Project-Uses-One-Codex-Hook-Command]]"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/agent_hooks.py", "src/project_os_cockpit/server.py", "desktop/plugin/claude-code/hooks/register.ts", "desktop/plugin/claude-code/tests/delivery.test.ts", "desktop/src/ipc/dispatch-queue.ts", "desktop/src/ipc/agents-fleet.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "desktop/tests/submitted-dispatch.test.mjs", "desktop/tests/delivery-row.test.mjs", "desktop/src/ipc/terminal.ts", "desktop/src/ipc/agent-instrument.ts", "desktop/tests/codex-hook-command.test.mjs", "desktop/tests/codex-dispatch.test.mjs", "desktop/tests/codex-shell-exit.test.mjs", "desktop/tests/claude-plugin-shell.test.mjs", "tests/test_deliveries.py", "tests/test_remote_peer_refusal.py", "docs/reference/cockpit-capability-register.md"]
platforms: [macos]
issues: []
features: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"]
---

# A prompt dispatched to Claude is submitted, not typed

## Summary

When you press a verb button such as "Work on" for a project whose terminal runs Claude, the cockpit no longer types the prompt into the terminal. The cockpit's server holds the prompt for that Claude session. The cockpit plugin inside the session submits it as soon as Claude is idle, as if you had typed it. The cockpit says "Delivered" only when Claude's turn has started, and the note's dispatch history records that moment.

Until the plugin takes it, the prompt can be cancelled from the queue list. Once the plugin has handed it to Claude, which takes about a tenth of a second, it cannot be withdrawn, and the cockpit says so and tells you to press Esc in the terminal.

Codex sessions, and terminals with no running agent, work as before.

## What a person notices

- **The prompt box no longer fills up by itself.** The prompt appears in the transcript under a line Claude Code draws, "Prompt from the project-os-cockpit plugin". Claude reads it as your own words.
- **A dispatch while Claude is busy waits in the cockpit, not in the terminal.** The `queued` chip counts it, and its row in the queue list says "Waiting for Claude to finish its turn". When the turn ends, the prompt starts, the row leaves the list, and the status line says "Delivered".
- **A prompt waiting when you press Esc follows your next message.** After Esc, Claude Code takes no prompt from a plugin until you send it something, so the plugin holds the prompt until your own next turn has ended. Meanwhile its row says "Waiting for you: Claude was stopped, so this follows your next message to it". The session shows "interrupted — waiting for your input" instead of busy, as a Codex session already did (TASK-0658, TASK-0659).
- **Each waiting row has a `×` that cancels it.** The status line says "Cancelled". "Clear all" cancels them all.
- **A prompt nothing will submit is shown, not hidden.** An example is a Claude session the cockpit has heard of through the external hook, but which runs without the cockpit plugin. The chip turns amber and says `1 not delivered`, and the row says why. Its `×` removes it.
- **A dispatch never types a shell command into a running agent.** Before typing, the cockpit asks tmux what runs in the project's terminal. Only a shell gets `<agent> '<prompt>'`. A running Codex gets the prompt pasted and a separate Return, even before Codex has reported to the cockpit; Codex runs its first hook only when its first turn starts. A Claude the cockpit cannot reach, as under the kill switch, is held in the queue with "Claude is running in this terminal but the cockpit cannot reach it". Any other program is held too (TASK-0660, ISS-0322).
- **The dispatch goes to the agent that is running**, whatever the Agent menu says. The menu only says which agent to start when none is running (ISS-0321).
- **Codex asks to review the cockpit's hooks once, not once per project.** Every project's hooks now run one identical command, so one trust covers them all. Before, trusting them in one project un-trusted them in the others. The first Codex start after this change asks once more (TASK-0661).
- **The note's dispatch history** shows the time Claude started the turn, or "cancelled" with the time.
- **The fleet view's queue depth** counts these prompts too.

## How it works

- The sidecar keeps a list of **deliveries**: one dispatched prompt each, addressed to one Claude session, with a state (held, waiting, sending, started, cancelled, dropped). Routes under `/api/cockpit/deliveries` add, list, claim, start, drop and cancel them; every one is loopback-only.
- The plugin asks for its own session's deliveries once a second. While no main-loop turn runs, it claims the oldest waiting one, submits it with `$.prompt.submit({ text, asUser: true })`, and reports the turn that starts with it.
- The shell's dispatch code routes a live Claude session to the sidecar, whatever its state, because the plugin waits for idle itself. If the sidecar does not take it, the prompt stays in the shell's queue. It is never typed instead.

## What was checked

- An interactive Claude Code 2.1.299 session with the plugin loaded, against a stand-in sidecar. A prompt sent while Claude was idle was claimed and started about 100 ms later. One sent during a turn was claimed only after that turn ended. The plugin's own submit hook did not see its own submission, which is why a prompt being submitted cannot be cancelled. Details are in TASK-0655.
- `python3 -m pytest -q -p no:randomly`, the desktop node suite, `claude plugin test`, `claude plugin validate` and `npx tsc --noEmit`. The counts are in the feature note's Verification section.

## What was not checked

- The queue list, its buttons and the status lines have not been seen in the running application. [[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]] is that check, and it is Edwin's to run after a rebuild and restart.
- The `cockpit dispatch` command is unchanged: its request still reaches the window, which dispatches it the same way.
