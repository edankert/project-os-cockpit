---
type: "[[risk]]"
id: RISK-0013
aliases: ["RISK-0013"]
title: "Once a cockpit click approves a Claude permission prompt, anything that can make that click, or forge the request behind it, can run a command in a Claude session"
status: open
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]], risk scan item 3", "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], risk scan 2026-10-14"]
likelihood: low
impact: high
mitigation:
  - "[[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]: the answer route requires a secret only the shell's main process holds, given to the sidecar on standard input"
  - "[[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]: the plugin only turns an ask into an answer, never changes an allow or a deny, and offers only a command short enough to show in full"
  - "[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]: the renderer never holds the secret; the main process sets the actor"
  - "[[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]: tests that fail when any of these guards is removed"
related: ["[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[RISK-0005-The-Write-Surface]]", "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[REQ-0027-Every-Write-Guarded]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
---

# Approving in the cockpit runs a command

## Description

After [[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], pressing Approve on a Needs you card lets a Claude session run the tool it asked for, often a Bash command. Before, an answer in the cockpit changed only a record. So whatever can produce an accepted answer can now run a command with the session's permissions.

**Why this is a new note and not part of RISK-0012.** [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]] is about putting words into a session; the model still decides what to do and its permission prompts still apply. This risk is about removing the permission prompt itself. The mitigation is shared (the same secret guards both routes), so RISK-0012 gains a line pointing here instead of absorbing it.

**Who could produce an accepted answer, and what stops each.**

- **A script in a page the cockpit's viewer frames** ([[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]). Stopped by the secret: the page cannot read it, and the custom header forces a preflight the sidecar does not answer.
- **The agent itself, through any tool it is allowed that can reach localhost** (`curl` to the sidecar). Stopped by the secret, as long as the agent cannot read it. It is not in any environment variable, file, argument or terminal the agent can reach; it reaches the sidecar on standard input.
- **Any other program running as the same user.** Same as the agent.
- **A delegated principal** ([[ADR-0009-The-Principal-Is-A-Role]]). Edwin decided on 2026-10-14 that `agent:principal` may answer. No path that holds the secret answers as it, so today it cannot. A future path that does must be decided on its own.

**What the secret does not stop.**

- **Driving the cockpit window itself.** A program that can click in the window, or that connects to the app's Chrome debugging port when the app is started with `--remote-debugging-port` (as it has been for development, on port 9222), can press Approve as the person does. The secret proves the request came from the shell, not that a person pressed the button.
- **Typing into the terminal.** The same user can already answer a terminal permission prompt with `tmux -L <socket> send-keys`. That predates this feature and is unchanged by it. The secret makes the HTTP path no weaker than that one; it does not make the machine safe from a hostile same-user process.
- **Approving the wrong thing.** A person who approves a command they did not read runs it. The card shows the input in full and the plugin does not offer an input it cannot show, but the click is still the person's.

## Mitigation

- The answer route requires the shell's secret, checked with a constant-time comparison after loopback and the JSON content type ([[REQ-0027-Every-Write-Guarded]]).
- The secret is made per sidecar spawn, held only in the shell's main process, and given to the sidecar on standard input, closed after one line.
- The renderer never holds it. The main process sets the actor to the macOS account's person.
- The plugin calls `next(e)` first and changes only an `ask`, so a refusal by the person's own rules or PreToolUse hooks is final. A fault in the hook leaves the verdict beneath.
- The plugin offers only real calls, never a question or plan approval, never a call whose organization ceiling is `ask`, and never an input over 16 KB.
- A wait of 0 turns cockpit answering off for a workspace.
- **Built 2026-10-14.** The secret: [[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]. The plugin's rules, plus one the live run added: an ask is offered only in manual (`default`) or `acceptEdits` mode, where a person would be asked anyway ([[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]). The main process as the only answerer, with the person's account as actor: [[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]. Each guard is shown to fail its test when removed, and a real PreToolUse deny was checked in a live session: [[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]] (`tests/test_answerable_approval_promises.py`, `desktop/plugin/claude-code/tests/approval.test.ts`).

## Triggers

- An approval is `granted` in `.cockpit/approvals.json` with no matching click in the window.
- The secret appears in any file, environment, log or response (the leak test in TASK-0667 fails).
- The app is run day to day with `--remote-debugging-port` while cockpit answering is on.
- A second answer path is built ([[FEAT-0079-Supervision-From-A-Phone]], a delegation runner).
