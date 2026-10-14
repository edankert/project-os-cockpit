---
type: "[[change]]"
id: CHG-20261014-A-Permission-Prompt-Is-Answered-From-The-Cockpit
title: "A Claude permission prompt can be answered from the Needs you panel for a few seconds before the terminal shows it, and only the desktop shell can send the answer"
status: merged
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]", "[[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]", "[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]", "[[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/__main__.py", "src/project_os_cockpit/approvals.py", "src/project_os_cockpit/server.py", "desktop/plugin/claude-code/hooks/register.ts", "desktop/src/ipc/sidecar.ts", "desktop/src/ipc/approvals.ts", "desktop/src/ipc/dispatch-queue.ts", "desktop/src/main.ts", "desktop/src/preload.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "desktop/src/types.ts"]
platforms: [macos]
issues: ["[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"]
features: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]", "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"]
---

# A permission prompt is answered from the cockpit

## Summary

When a Claude session in a cockpit terminal asks permission to run a command or edit a file, a card now appears at the top of the Needs you panel, whichever project is on screen. It shows the request in full, with Approve and Deny. Clicking one is the session's answer, and the terminal never shows its own prompt. If nobody clicks within 5 seconds, the terminal shows its prompt exactly as before and the card says so.

Only the desktop shell can send that answer. The cockpit's server now requires a secret, made by the shell for each server it starts, before it accepts an answer or a prompt for a Claude session. A script in a page the viewer shows, or the agent itself through `curl`, gets 403.

Codex sessions, and Claude sessions in auto mode, work as before.

## What a person notices

- **A card for each permission prompt**, red-bordered, above the other Needs you cards. It names the project, says "Claude asks to run a command" (or "to use Write", or "A Claude subagent asks…"), shows the command or path in full in a block that wraps and scrolls, names the session, and has Approve and Deny.
- **Approve or Deny answers the session.** The command runs, or the model is told "Denied in the cockpit by user:edwin." The status line says "Approved Bash in project-os-cockpit".
- **A 5 second delay before the terminal's own prompt**, in manual or acceptEdits mode, while the cockpit waits for a click. When it runs out, the card loses its buttons and says "Answer in the terminal: the cockpit's 5 s wait ran out". A click after that is refused with the same sentence. The wait is `approvalWaitMs` on the project's entry in `workspaces.json` (0 turns the card off; the most is 30 s); a change applies when the project's server next starts.
- **The project's amber "needs your input" card is not drawn beside a permission card**, because it would say the same thing with less in it.
- **Nothing changes in auto mode, plan mode or don't-ask mode.** There the classifier or the mode decides, not a person, so the cockpit is not asked.

## How it works

- **The secret.** `spawnSidecar` makes 32 random bytes per server it starts and writes them, with the wait, as one JSON line on the server's standard input (`--secret-stdin`), then closes it. It is never in the command line, the environment, a file, a terminal or the renderer. `POST /api/cockpit/approve` and `POST /api/cockpit/deliveries` require it as `X-Cockpit-Secret`, after the loopback and JSON checks. A server started from a terminal has none and refuses both routes. A refusal now also closes the connection and says so (`Connection: close`), which every refusal made before reading the body needed ([[TASK-0668-A-Refused-Write-Closes-Its-Connection]]).
- **The plugin.** A `tool.check` hook asks Claude Code's own rules, mode and PreToolUse hooks first and returns any `allow` or `deny` unchanged. Only an `ask` in manual or acceptEdits mode, for a real tool call that is not a question or a plan, is offered: `POST /api/cockpit/approvals/ask`, a read every 250 ms, then `POST /api/cockpit/approvals/handed-back` when the wait runs out. The server decides under its lock, so a click that lands as the wait ends still counts.
- **The approvals store** gains the states `handed-to-terminal` and `closed`, keeps the command whole up to 16 KB (a longer one is not offered), and closes a record when its call runs, when the main-loop turn ends or the person sends the next prompt, or when the session ends.
- **The shell.** `desktop/src/ipc/approvals.ts` follows the event stream of every running server, not only the active one, and sends each change to every window. Its `approval:answer` handler posts the answer with the secret and `actor: user:<macOS account>`; the renderer names only the decision.

## What was checked

- **A real Claude session, Claude Code 2.1.300, against a stand-in server**, recorded in [[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]: granted within the wait (no terminal dialog), denied within the wait (the model read the reason), no click (the dialog appeared after 5.0 s and a late click got 409), refused with Esc (the record closed on the next prompt). The first run was in auto mode and showed every classified call waiting 5 s for nothing, which is why only manual and acceptEdits are offered.
- **A real PreToolUse hook that denies**, loaded with `--settings` from a scratch file, with a script granting every approval at once: the command did not run and the plugin offered nothing ([[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]).
- **Tests, each shown to fail with its guard removed:** `tests/test_shell_secret.py`, `tests/test_approval_ask.py`, `tests/test_answerable_approval_promises.py`, `desktop/tests/shell-secret.test.mjs` (a real spawned server), `desktop/tests/approval-card.test.mjs`, and `desktop/plugin/claude-code/tests/approval.test.ts`.
- **The card**, in a scratch copy of the live harness in Chrome at 1400 and 760 px, dark and light, with a long command.

## What was not checked

- **The card in the running application.** It needs a desktop rebuild and restart, which is Edwin's; [[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]] is that walk.
- **The debugging-port question** in the plan: with `--remote-debugging-port`, a local program can press Approve as a person does. Whether the card should then offer no buttons is Edwin's decision, not made here.
- **Claude Code 2.1.299**, the version CI pins. The live runs were on 2.1.300; CI runs the plugin tests on 2.1.299 when this is pushed.
