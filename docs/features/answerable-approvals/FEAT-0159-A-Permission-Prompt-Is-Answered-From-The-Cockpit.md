---
type: "[[feature]]"
id: FEAT-0159
aliases: ["FEAT-0159"]
title: "A Claude Code permission prompt can be answered from the cockpit, by a person, and the answer never overrides a deny"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-08
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], the paragraph on permission prompts"
goal: "When a Claude session asks permission to use a tool, the person can approve or deny it with the cockpit's buttons, and that click is the session's answer; nobody else can answer it, and nothing the cockpit sends can turn a deny into an allow."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[FEAT-0076]]"
  - "[[FEAT-0079-Supervision-From-A-Phone]]"
  - "[[PHASE-031-The-Supervised-Week]]"
  - "[[RISK-0006-The-Unattended-Worker]]"
  - "[[REQ-0026-Only-Human-Owned-Transitions]]"
  - "[[REQ-0027-Every-Write-Guarded]]"
  - "[[ADR-0009-The-Principal-Is-A-Role]]"
---

# A permission prompt is answered from the cockpit

**Not started, and blocked.** Filed at `backlog` in the planned [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]. It is the phase's last feature. It cannot start until the answer route requires a secret the agent cannot read ([[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]], its open half).

## Goal

Today the cockpit shows an amber card when a Claude session asks for permission, but answering still means finding the terminal and typing (`approvals.py`, module docstring). After this feature, the card's approve and deny buttons are the answer. The plugin waits a bounded time for the person's click; if none comes, the terminal prompt appears exactly as it does today.

## Findings

- **The hook.** A `tool.check` hook calls `next(e)` first, so Claude Code's own rules and the user's PreToolUse hooks decide before the cockpit is asked. Only when the result is `ask` does the plugin post to the approvals store and wait. It returns `allow` or `deny` from the person's answer, or returns the original `ask` when the wait runs out. **It never changes a `deny`.** The mods documentation warns that a mod can approve calls the user's own PreToolUse hooks blocked; this rule is what prevents that, and it needs a test.
- **The wait.** A hook has a 10 s limit, but waiting inside a mods API call such as `$.http.fetch` does not count toward it. The wait should be short, so a person at the terminal is not kept from their own prompt. The length is an open question.
- **Why the answer route is not safe yet.** The answer endpoint (`server.py:2404`) accepts `approval_id`, `decision` and `actor` from the request body, and checks only that the request came from this machine. `approvals.answer` refuses an actor that starts with `agent:`, but the actor is whatever the request says. Today that costs little, because an answer changes only a record. Once an answer approves a Bash call, any loopback POST that claims to be `user:edwin` runs a command. Two ways to send one exist already: a script in a framed HTML page (ISS-0301), and the agent itself, through any tool it is already allowed that can reach localhost.
- **What the secret must be.** A value the shell holds and passes to the sidecar, which the sidecar requires on the answer route. It must not be in any environment variable or file the Claude session can read. Passing it in the sidecar's environment is not enough if a same-user process can read another process's environment; passing it on the sidecar's standard input at spawn avoids that question. The plugin does not need the secret: it reads the answer, it does not write it.
- **Who may answer.** [[REQ-0026-Only-Human-Owned-Transitions]] says the cockpit performs only human-owned transitions. `approvals.answer` lets `agent:principal` answer, because [[ADR-0009-The-Principal-Is-A-Role]] allows a delegation policy to give the principal role to an agent (`delegation.py`). For a record that was harmless. For an answer that runs a command it is not, so this is an open question.
- **What it unblocks.** [[FEAT-0076]] promises that nothing waits silently without bound, and every mechanism behind that promise watches the review queue. A permission prompt answered through the approvals store is a queue entry, so the stall alarm in [[PHASE-031-The-Supervised-Week]] can see it, which [[RISK-0006-The-Unattended-Worker]] needs. [[FEAT-0079-Supervision-From-A-Phone]] would answer through the same route and needs the same secret.

### Candidate tasks, minted when this feature starts

1. The shell's secret, given to the sidecar at spawn and required on the answer route; a request without it is refused. This closes the open half of ISS-0301 for this route.
2. The plugin's `tool.check` hook: `next(e)` first, wait only on `ask`, never change a `deny`, fall back on timeout.
3. The cockpit card's buttons send the answer with the secret; the card says when the wait ran out and the terminal has the prompt.
4. Tests: a PreToolUse `deny` survives a cockpit `allow`; an answer without the secret is refused; an `agent:` actor is refused.

## Open questions

1. **Does this route need the secret only on the answer endpoint, or on every write endpoint (ISS-0301's full fix)?** Recommendation: the answer endpoint first, because it is the one that runs commands; the rest under ISS-0301.
2. **May a delegated principal (`agent:principal`) answer a prompt that runs a command?** Recommendation: no. Only a click in the shell, carrying the shell's secret, answers.
3. **How long does the plugin wait before handing the prompt back to the terminal?** Suggestion: a few seconds, configurable per workspace.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Code: `src/project_os_cockpit/approvals.py`, `src/project_os_cockpit/server.py` (the approval answer route), `src/project_os_cockpit/delegation.py`
