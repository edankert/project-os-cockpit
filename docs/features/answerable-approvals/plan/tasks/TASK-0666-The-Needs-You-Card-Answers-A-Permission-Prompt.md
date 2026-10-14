---
type: "[[task]]"
id: TASK-0666
aliases: ["TASK-0666"]
title: "The Needs you card shows a Claude permission prompt in full with Approve and Deny, sends the answer through the main process, and says when the terminal has the prompt instead"
status: done
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

- [x] The renderer reads `GET /api/cockpit/approvals` when a workspace attaches and updates on each `cockpit:approval` event. Each `open` or `handed-to-terminal` approval draws a Needs you entry, above the session's own `needs-input` entry, and that session's duplicate amber entry is not drawn twice.
- [x] The card shows the project, the agent and session, the tool, and the input in full: for Bash the whole command in a monospace block that scrolls rather than cuts, for a file tool the path. Nothing on the card is cut with an ellipsis.
- [x] Approve and Deny call a new IPC handler, `approval:answer(workspaceId, approvalId, decision)`, exposed in `preload.ts`. The main process posts `POST /api/cockpit/approve` with `X-Cockpit-Secret` and `actor: user:<macOS account name>`. The renderer never receives the secret.
- [x] While the request is in flight both buttons are disabled. On success the card leaves the list and the status line says "Approved Bash in <project>" or "Denied ...".
- [x] A `handed-to-terminal` card has no buttons and says "Answer in the terminal: the cockpit's 5 s wait ran out" (the workspace's own number). A 409 from a late click shows the same sentence.
- [x] A `closed` approval leaves the list.
- [x] Node tests that fail when: the renderer posts to `/api/cockpit/approve` itself; the IPC handler sends an actor the renderer chose; a handed-back card offers buttons; a long command is cut.
- [x] Seen in a browser or the live harness at a narrow and a wide width, with a long Bash command.

## Steps

- [x] The IPC handler and preload method.
- [x] The Needs you entry and the card.
- [x] Tests and a look at it.

## Notes

The sidecar's own HTML page (the tablet view on `0.0.0.0`) gets no buttons. It cannot hold the secret, and the answer route is loopback-only anyway. [[FEAT-0079-Supervision-From-A-Phone]] is where a remote answer would be designed.

## Built, 2026-10-14

**What a person notices:** when a Claude session in a cockpit terminal asks permission in manual or acceptEdits mode, a card appears at the top of the Needs you panel within a moment, whichever project is on screen. It shows the project, "Claude asks to run a command" (or "to use Write", or "A Claude subagent asks…"), the command or path in full in a block that wraps and scrolls, the session, and Approve and Deny. A click answers the session and the status line says "Approved Bash in <project>". When the wait has run out, the card keeps its text, loses its buttons and says "Answer in the terminal: the cockpit's 5 s wait ran out". The project's amber needs-input card is not drawn beside it.

- **Why a main-process watcher, not the renderer's event stream.** The renderer follows only the active workspace's sidecar, and other workspaces are polled every 5 s, which is as long as the whole wait. `desktop/src/ipc/approvals.ts` keeps one event stream per running sidecar (started when a sidecar is healthy, stopped when it exits, reconnecting while it lives), reads the live list on every connect, and sends `approval:changed` to every window.
- **The answer.** `approval:answer(workspaceId, approvalId, decision)` in the same module posts with `X-Cockpit-Secret` from `sidecarSecretFor` and `actor: user:<os.userInfo().username>`. Extra arguments are ignored, so the renderer cannot choose the actor. The renderer bundle contains neither the answer route nor the header name.
- **The card.** `approvalCardText` (pure, tested) and `buildApprovalRow` in `renderer.ts`, drawn by `paintAttention` above the other cards, outside the dismiss machinery: a pending decision has no ✕. `attentionEntries` skips a workspace's needs-input card while it has a live approval. Styles in `renderer.css`, `.ws-approval-*`.
- **The sidecar** now keeps each approval's `wait_ms`, so the handed-back sentence uses that workspace's own number.
- **Tests.** `desktop/tests/approval-card.test.mjs` (6): the card's words, a 15,000-character command kept whole and the stylesheet rule wrapping it, no buttons once handed back, the renderer never naming the route, the main process sending the secret and the person whatever a fourth argument says, and a stand-in sidecar's events reaching the windows. `attention-mixed-session.test.mjs` gained the amber-card case. Node suite 224 passed; pytest 2215 passed, 11 skipped, then the build-digest test passed after a rebuild.
- **Seen.** In a scratch copy of `desktop/harness/live-harness.html` with the bridge's `approvals` stubbed (deleted afterwards), in Chrome at 1400 and 760 px wide, dark and light: a long Bash command wraps inside its block and scrolls, the handed-back Write card shows its note and no buttons, and Approve disables both buttons and shows "Approved Bash in project-os-cockpit".

**Not done here: the debugging-port question.** The plan's open question (no buttons while the app runs with `--remote-debugging-port`) is still Edwin's. Nothing in this task depends on it.
