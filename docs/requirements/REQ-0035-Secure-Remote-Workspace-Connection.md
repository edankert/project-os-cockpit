---
type: "[[requirement]]"
id: REQ-0035
aliases: ["REQ-0035"]
title: "A remote workspace connection uses verified SSH identity, and no remote write is authorised by the remote host's loopback interface"
status: draft
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "Edwin 2026-08-13: full write parity for remote workspaces; shared/multi-user hosts in scope"]
priority: high
scope: "Every connection from the desktop cockpit to a remote project-os workspace, its docs sidecar, filesystem API, and PTY sessions"
acceptance: ["The remote host is authenticated through OpenSSH host-key verification and a mismatch cannot be silently accepted", "Private keys, passwords, agent credentials, and remote environment secrets are neither stored in project records nor copied to the remote host by default", "Remote docs and PTY services have no externally reachable listener; all traffic travels inside the authenticated SSH connection", "A mutating request is not authorised by originating on the remote host's loopback interface; a second local account on that host cannot write, dispatch, or open a terminal", "A disconnect or integrity failure revokes the connection's capabilities and clears live remote state until a fresh verification succeeds"]
implements: "[[FEAT-0099-Remote-SSH-Workspaces]]"
verifies: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
related: ["[[REQ-0005-Terminal-Local-Only]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[REQ-0027]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[ADR-0026-Remote-Workspace-Transport]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
tags: [requirement, security, remote]
---

# A remote workspace connection uses verified SSH identity, and loopback on the remote host authorises nothing

## Statement

The cockpit SHALL connect to a remote workspace only through an authenticated SSH transport with verified host identity. Remote docs, file, and terminal channels SHALL be tunnelled or carried through that SSH transport and SHALL NOT create a LAN-reachable shell or sidecar endpoint.

**A mutating request SHALL NOT be authorised by the fact that it arrives on the remote host's loopback interface.** Where a remote helper listens at all, its mutating routes SHALL require proof of identity that a co-tenant on that host cannot produce; where the transport is stdio, the absence of any listener satisfies this by construction.

## Why the second paragraph exists

`REQ-0027` and [[REQ-0034]] rest on an unstated premise: **loopback means the user.** True on a personal Mac; false on a shared development host, which Edwin put in scope on 2026-08-13 in the same breath as full write parity.

The sidecar guards twenty mutating routes with a single check, `_require_loopback()` (`src/project_os_cockpit/server.py:1578`) — note writes and decisions, approvals, inbox, design verdicts, and `POST /api/cockpit/dispatch`, which starts agent commands. Bind that on a shared host and every other account there passes the gate without ever authenticating over SSH. REQ-0034 does not reach the case: it authenticates a **non-loopback** write, and this write is a loopback write.

## Acceptance Criteria

- [ ] The remote host is authenticated through OpenSSH host-key verification and a mismatch cannot be silently accepted — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] Private keys, passwords, agent credentials, and remote environment secrets are neither stored in project records nor copied to the remote host by default — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] Remote docs and PTY services have no externally reachable listener; all traffic travels inside the authenticated SSH connection — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] **A second local account on the remote host cannot write a note, dispatch an agent, or open a cockpit terminal against the connected workspace** — the enumerated mutating-route set is covered, not a sample — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] A disconnect or integrity failure revokes the connection's capabilities and clears live remote state until a fresh verification succeeds — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]

## Traceability

- Implements: [[FEAT-0099-Remote-SSH-Workspaces]]
- Verified by: [[TST-0024-Remote-SSH-Workspace-Walk]]
- Constrains: [[ADR-0026-Remote-Workspace-Transport]] — the fourth criterion is what eliminated the unauthenticated-remote-listener alternative.
