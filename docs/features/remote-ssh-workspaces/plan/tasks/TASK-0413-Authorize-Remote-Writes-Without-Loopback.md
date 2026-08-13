---
type: "[[task]]"
id: TASK-0413
title: "Authorise remote writes without the remote host's loopback interface"
status: backlog
owner: unassigned
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: full write parity, and shared/multi-user hosts in scope", "Review 2026-08-13: twenty mutating routes are guarded only by _require_loopback(), which a co-tenant on the remote host satisfies"]
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: L
depends: ["[[TASK-0405-Define-Remote-Session-Architecture]]"]
blocks: ["[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0412-Fleet-Surfaces-For-A-Remote-Workspace]]"]
related: ["[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[REQ-0027]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[ADR-0026-Remote-Workspace-Transport]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Authorise remote writes without the remote host's loopback interface

`_require_loopback()` (`src/project_os_cockpit/server.py:1578`) is the whole authorisation model for twenty mutating routes — note writes and decisions, approvals, inbox, design verdicts, and `POST /api/cockpit/dispatch`, which starts agent commands. It works because on a personal Mac, loopback means the user.

On a shared remote host it does not. Every other account there reaches `127.0.0.1` and passes the gate without authenticating over SSH. [[REQ-0034]] does not cover it: that requirement authenticates a **non-loopback** write, and a co-tenant's write is a loopback write.

## Definition of Done

- [ ] A mutating request against a remote workspace is authorised by something a co-tenant on the remote host cannot produce — or by the structural absence of any listener, if [[ADR-0026]]'s spike selects stdio, in which case this task records *why the property holds* and tests it rather than building a mechanism.
- [ ] The guarantee is enumerated, not sampled: the existing property `test_every_note_mutating_endpoint_requires_loopback` gains a remote sibling, so a new endpoint that forgets the check fails **by existing**.
- [ ] The local path is unchanged — a local write does not become harder because a remote one became possible ([[REQ-0034]]'s first bullet, which holds here too).
- [ ] Absence of proof is refusal. No fallback to "probably fine, it's the same box".
- [ ] Nothing that proves identity lands in the record, and a stolen artefact expires.
- [ ] The relationship to [[REQ-0034]] is settled in writing: this task either implements REQ-0034's mechanism for both cases, extends REQ-0034's statement to cover an untrusted loopback peer, or states why two mechanisms are correct. One question, one answer.

## Steps

- [ ] Wait for [[TASK-0405]] — stdio and authenticated-listener lead to different work here, and only one of them is a build.
- [ ] Settle the REQ-0034 relationship before building anything ([[PHASE-029]] owns the LAN half).
- [ ] Implement or prove, then extend the enumerating property test to the remote surface.
- [ ] Exercise it from a second account on a real remote host as part of [[TST-0024]].
