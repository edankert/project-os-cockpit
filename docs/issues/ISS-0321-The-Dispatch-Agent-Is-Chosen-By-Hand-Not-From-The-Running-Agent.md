---
type: "[[issue]]"
id: ISS-0321
aliases: ["ISS-0321"]
title: "Which agent a verb button dispatches to is a hand-set menu choice per project, instead of following the agent running in the project's terminal"
status: open
phase: ""
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["Edwin 2026-10-14, during TST-0095 step 10: 'That has to be automatic really ... it needs to be dependent on the current active agent in the project.'"]
reported_by: user:edwin
question: ""
severity: medium
component: desktop
parent: ""
related: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]", "[[ISS-0322-Codex-In-A-Cockpit-Terminal-Reports-Nothing-To-The-Sidecar]]", "[[ISS-0032]]"]
tests: []
---

# The dispatch agent is chosen by hand

To dispatch to Codex, a person right-clicks a note, opens **Agent**, and ticks **Codex**. The choice is stored per project in the window's `localStorage` (`cockpit:dispatch-agent:<workspace>`, `loadDispatchAgent` in `desktop/src/renderer/renderer.ts`). Nothing changes it when a different agent starts in that project's terminal. So after running `codex` in a terminal, the verb buttons still say they dispatch to Claude until the person changes the menu, and back again afterwards.

## What it should do

Edwin, 2026-10-14: the agent "needs to be dependent on the current active agent in the project". When a Claude or Codex session is running in the project's terminal, a dispatch goes to that agent. The menu choice matters only when no agent is running, to say which one to start.

## What already follows the running agent

When the cockpit knows a session is live, `routeFor` in `desktop/src/ipc/dispatch-queue.ts` already sends the prompt to it, whatever the menu says: a live Claude session gets a delivery, and a live Codex session gets the prompt pasted. Only the ledger's `agent` and the shell fallback's command (`<agent> '<prompt>'`) use the menu choice. The visible problem is twofold: the menu has to be set by hand, and the cockpit often does not know a session is running. That second part is [[ISS-0322-Codex-In-A-Cockpit-Terminal-Reports-Nothing-To-The-Sidecar]] for Codex, and the kill switch for both agents (TST-0095 step 9).

## Open question

How the cockpit should know which agent is running when no hook reports one. The terminal's tmux pane names its foreground program (`codex`, or Claude Code's version number, `2.1.299`). On 2026-10-14 Edwin declined a check of that kind for the kill-switch case ("Accept it, fix the check"); this request may change that.

## Fix, 2026-10-14

[[TASK-0660-A-Dispatch-Checks-What-Runs-In-The-Terminal-Before-Typing]] answers the open question: the cockpit reads the terminal's foreground program through tmux. A dispatch now goes to the agent that is running, whatever the Agent menu says, and the dispatch history names that agent. The menu decides only which agent a plain shell starts. The issue stays open until TST-0095 step 10 shows it in the running application.
