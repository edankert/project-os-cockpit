---
type: "[[phase]]"
id: PHASE-033
aliases: ["PHASE-033"]
title: "The workspace is not always local — a repo on another machine gets the whole cockpit, and the boundary that made loopback sufficient does not travel with it"
status: planned
order: 33
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
goal: "A project-os repository on another machine is a workspace like any other — same record, same terminals, same fleet surfaces — with the authorisation that made a local workspace safe rebuilt rather than assumed."
features: ["[[FEAT-0099-Remote-SSH-Workspaces]]"]
requirements: ["[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[REQ-0036-Remote-Development-Workflow]]"]
issues: []
related: ["[[ADR-0026-Remote-Workspace-Transport]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[REQ-0027]]", "[[REQ-0005-Terminal-Local-Only]]", "[[ADR-0010]]", "[[ISS-0154-Existing-Terminals-Lose-Keyboard-Input-After-Workspace-Switch]]", "[[TST-0024-Remote-SSH-Workspace-Walk]]"]
tags: [phase, security]
---

# The workspace is not always local

## Goal

**A project-os repository on another machine is a workspace like any other — same record, same terminals, same fleet surfaces — and the authorisation that made a local workspace safe is rebuilt rather than assumed.**

Every workspace this tool has ever opened has been a directory on the machine the user is sitting at. That assumption is not in one place; it is in the workspace identity (a sha1 of a local absolute path, `desktop/src/ipc/workspaces.ts:56`), in the pruning rule that silently drops a workspace whose path does not stat (`workspaces.ts:196`), in every fleet surface that reads `<root>/.cockpit/*` or runs `git -C <root>`, and — the one that matters — in `_require_loopback()`, which is the entire authorisation model for twenty mutating routes (`src/project_os_cockpit/server.py:1578`).

## Why a phase and not a task

Both tests in `CLAUDE.md` hold.

The goal above is one sentence and lists no parts. And the exit criteria are properties of the finished system — *no write is authorised by a remote loopback interface*, *no surface reports a remote absence as a local fact* — not a restatement of the task list. Two of them can be checked by a test that enumerates route sets and surfaces, which is what makes them criteria rather than a summary.

It also earns a phase on size and on gating: it re-opens a security question the project already answered once ([[ADR-0010]], [[REQ-0034]]), it spans the transport, the shell, every fleet surface and the Python sidecar, and its first task is a spike whose outcome changes the rest.

## The premise this phase breaks

`REQ-0027` and [[REQ-0034]] rest on a premise neither states: **loopback means the user.** On Edwin's Mac that is true, which is why `_require_loopback()` has been a sufficient authorisation model and why REQ-0034 frames the problem as *"a write from a **non-loopback** surface proves who is asking"*.

Remote workspaces are the first place the premise is false. Edwin's decisions on 2026-08-13 make that concrete: remote workspaces get **full write parity**, and **shared, multi-user hosts are in scope**. A sidecar bound to `127.0.0.1` on a shared host is reachable by every other account on it, and those requests are loopback requests. They would pass the only gate there is — including `POST /api/cockpit/dispatch`, which starts agent commands. On such a host the failure is not "someone edits my notes"; it is unauthenticated command execution by a local peer who never touched SSH.

So this phase's security work is not "keep SSH tidy". It is: **decide what authorises a write when loopback no longer identifies anybody**, and make the answer hold for a channel that did not exist when the question was first settled.

## Scope

- **[[FEAT-0099-Remote-SSH-Workspaces]]** — the whole capability: verified SSH profiles, a remote docs sidecar constrained to the SSH connection, a bounded remote repository browser, remote PTYs with framework launchers, and fleet-surface parity for a workspace that is not on this machine.
- **[[ADR-0026-Remote-Workspace-Transport]]** — the transport decision, which the two answers above have already narrowed to stdio or an authenticated remote listener. It is `proposed` and gates everything after the spike.
- **[[REQ-0035-Secure-Remote-Workspace-Connection]]** and **[[REQ-0036-Remote-Development-Workflow]]** — both `draft`; REQ-0035 needs the co-tenant clause before it is designed, not after.
- **[[RISK-0007-Remote-Workspace-Trust-Boundary]]** — open, and it closes on [[TST-0024-Remote-SSH-Workspace-Walk]] evidence from a real two-machine host with a second account, not on a walkthrough.

## Out of scope

- **Weakening [[REQ-0005-Terminal-Local-Only]].** The mode-3 terminal has no listener at all — it is node-pty over Electron IPC — and nothing here gives it one. The remote PTY is reached through SSH or not at all.
- **A cloud relay, multi-user collaboration, or an untrusted browser.** Unchanged from FEAT-0099.
- **Pushing from a remote workspace.** A remote fleet member would otherwise inherit the roll-up's push action and publish from a machine the user is not sitting at. Deliberately refused for this phase; re-openable with its own decision.
- **Automatic framework installation on the remote host.** Discovery only.

## Exit criteria

- [ ] **No cockpit write on a remote host is authorised by that host's loopback interface alone** — asserted over the enumerated mutating-route set (the property `test_every_note_mutating_endpoint_requires_loopback` already holds), not over the routes this phase happens to touch.
- [ ] **Every fleet surface either works against a remote workspace or says it cannot.** No surface reports a remote workspace's unreachability as a local fact: no empty git status, no zero-error validator result, no absent agent state rendered as *idle*.
- [ ] **A remote workspace survives being offline.** Quitting and relaunching while disconnected does not lose the profile, and the rail distinguishes *not connected* from *not there*.
- [ ] **The record says which machine a note lives on**, readable from the note and the workspace identity rather than inferred from which rail entry is highlighted. A remote repo and a same-named local clone cannot be confused by any surface, including deep links.
- [ ] **[[TST-0024-Remote-SSH-Workspace-Walk]] passes on two real machines, including a second user account on the remote host** attempting to reach the sidecar and the terminal. A pass without that account is not a pass.
- [ ] **[[RISK-0007]] closes on that evidence**, and [[REQ-0035]]/[[REQ-0036]] reach `implemented` with every criterion ticked or reconciled.

## Notes

- **Sequencing is gated, not parallel.** [[TASK-0405]]'s spike decides the transport; TASK-0406/0407/0411 depend on it. The one leg that can be decided independently is the PTY channel — neither candidate design has a listener — so TASK-0408 need not wait on the docs channel if the spike says so.
- **Two decisions were taken 2026-08-13 and are recorded in [[ADR-0026]] rather than left to the spike:** full write parity for remote workspaces, and shared/multi-user hosts in scope. Together they eliminate the ADR's cheapest alternative (a plain local-forward to a remote loopback sidecar) unless that sidecar authenticates.
- **[[ISS-0154]] is related, not owned.** It is a local terminal-focus bug, and the shared-xterm design it exposes is what FEAT-0099's multi-session ambition would have to change. Fix it on its own terms first; do not let a remote feature carry it.
- **This phase does not open with build work.** It opens with a decision (ADR-0026) and two `draft` requirements, in a repo whose relevant security decision ([[ADR-0010]]) is itself still `proposed`.
