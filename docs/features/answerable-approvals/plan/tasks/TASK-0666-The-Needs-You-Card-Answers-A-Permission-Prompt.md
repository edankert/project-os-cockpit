---
type: "[[task]]"
id: TASK-0666
aliases: ["TASK-0666"]
title: "The Needs you card shows a Claude permission prompt in full with Approve and Deny, sends the answer through the main process, and says when the terminal has the prompt instead"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], candidate task 3", "plan/PLAN.md, 'How the secret reaches the renderer: it does not'"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "M"
due: ""
depends: ["[[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]", "[[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]"]
blocks: ["[[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]"]
related: ["[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]", "[[REQ-0026-Only-Human-Owned-Transitions]]"]
tests: []
---

# The Needs you card answers a permission prompt

The card does not exist yet: today's amber card is a session's `needs-input` state and has no buttons. After this task, each open approval has a card on the Needs you list showing which project and session asks, the tool, and the full command or file path, with Approve and Deny. A click answers the session. When the wait has run out, the card loses its buttons and says the terminal has the prompt.

## Definition of Done

- [ ] The renderer reads `GET /api/cockpit/approvals` when a workspace attaches and updates on each `cockpit:approval` event. Each `open` or `handed-to-terminal` approval draws a Needs you entry, above the session's own `needs-input` entry, and that session's duplicate amber entry is not drawn twice.
- [ ] The card shows the project, the agent and session, the tool, and the input in full: for Bash the whole command in a monospace block that scrolls rather than cuts, for a file tool the path. Nothing on the card is cut with an ellipsis.
- [ ] Approve and Deny call a new IPC handler, `approval:answer(workspaceId, approvalId, decision)`, exposed in `preload.ts`. The main process posts `POST /api/cockpit/approve` with `X-Cockpit-Secret` and `actor: user:<macOS account name>`. The renderer never receives the secret.
- [ ] While the request is in flight both buttons are disabled. On success the card leaves the list and the status line says "Approved Bash in <project>" or "Denied ...".
- [ ] A `handed-to-terminal` card has no buttons and says "Answer in the terminal: the cockpit's 5 s wait ran out" (the workspace's own number). A 409 from a late click shows the same sentence.
- [ ] A `closed` approval leaves the list.
- [ ] Node tests that fail when: the renderer posts to `/api/cockpit/approve` itself; the IPC handler sends an actor the renderer chose; a handed-back card offers buttons; a long command is cut.
- [ ] Seen in a browser or the live harness at a narrow and a wide width, with a long Bash command.

## Steps

- [ ] The IPC handler and preload method.
- [ ] The Needs you entry and the card.
- [ ] Tests and a look at it.

## Notes

The sidecar's own HTML page (the tablet view on `0.0.0.0`) gets no buttons. It cannot hold the secret, and the answer route is loopback-only anyway. [[FEAT-0079-Supervision-From-A-Phone]] is where a remote answer would be designed.
