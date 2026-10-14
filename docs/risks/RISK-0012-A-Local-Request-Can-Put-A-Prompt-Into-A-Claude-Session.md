---
type: "[[risk]]"
id: RISK-0012
aliases: ["RISK-0012"]
title: "Any program on this Mac that can post JSON to a sidecar can put a prompt into a cockpit Claude session, read as the person's own words"
status: open
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]], risk scan 2026-10-14"]
likelihood: low
impact: high
mitigation:
  - "[[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]: loopback-only and JSON-only on every new route"
  - "[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]: the plugin submits only deliveries addressed to its own session"
  - "[[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]] (done 2026-10-14): POST /api/cockpit/deliveries requires the shell's secret"
related: ["[[RISK-0005-The-Write-Surface]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]", "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]", "[[REQ-0027-Every-Write-Guarded]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]"]
---

# A local request can put a prompt into a Claude session

## Description

After [[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]], a prompt reaches a cockpit Claude session through a sidecar route, `POST /api/cockpit/deliveries`. The body carries the prompt's full text, because some dispatches are free text: a selection, a review answer, an inbox triage. The plugin submits it with `asUser: true`, so the model reads it as the person's own words and acts on it with the session's permissions.

Until now, prompt text reached the terminal only over the app's internal IPC. The HTTP route `POST /api/cockpit/dispatch` carries a note ID and a verb, never text. So this is the first route that takes arbitrary text and turns it into a Claude turn.

**Who can use it.** Any process on this Mac running as the same user, and anything else that can make a JSON POST to `127.0.0.1`. That is not wider than today for a local process: the same user can already type into the cockpit's terminals with `tmux -L <socket> send-keys`. It would be wider for a web page, but the shared JSON reader refuses a request that is not `application/json`, so a page cannot post without a preflight the sidecar does not answer ([[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]).

**Where the impact is high.** On a shared host, every account there can reach a loopback sidecar ([[RISK-0007-Remote-Workspace-Trust-Boundary]]). Remote workspaces are out of [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]'s scope and not built.

## Mitigation

- Every new route requires loopback and a JSON body ([[REQ-0027-Every-Write-Guarded]]), and the enumerating test names them ([[RISK-0005-The-Write-Surface]]).
- The plugin submits only deliveries addressed to its own session ID.
- Hooks and the transcript still name the plugin as the prompt's origin, so the person's own hooks can tell it from typing.
- When [[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]] adds a secret the shell holds, `POST /api/cockpit/deliveries` should require it too. The secret is planned there because an answer route that approves commands has the same shape of hazard.
- **Built, 2026-10-14** (was planned the same day): [[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]] makes `POST /api/cockpit/deliveries` require the shell's secret (Edwin's decision). Only the shell's main process sends it. `cockpit dispatch` still works without it, because it posts a note ID and a verb to `/api/cockpit/dispatch`, never prompt text. The related hazard of a forged permission answer is [[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]. A delivery without the secret, or with it one character off, is refused and not added: `tests/test_answerable_approval_promises.py` ([[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]).

## Triggers

- A delivery appears in the sidecar that no window or `cockpit` command created.
- The cockpit is pointed at a workspace on a host other people log in to.
- ISS-0301's Content-Type refusal is removed or loosened.
