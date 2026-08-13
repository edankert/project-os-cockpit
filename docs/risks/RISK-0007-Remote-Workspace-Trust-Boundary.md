---
type: "[[risk]]"
id: RISK-0007
aliases: ["RISK-0007"]
title: "Remote workspace trust boundary — on a host you do not own alone, loopback authorises strangers, and the cockpit's write surface includes agent dispatch"
status: open
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["Preflight risk scan for [[FEAT-0099-Remote-SSH-Workspaces]]", "Review 2026-08-13: full write parity + shared hosts turns the remote loopback gate into an authorisation boundary it was never designed to be"]
likelihood: medium
impact: high
mitigation: ["[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[TASK-0405-Define-Remote-Session-Architecture]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]", "[[TASK-0410-Verify-Remote-Connection-Safety-And-Recovery]]"]
related: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "[[REQ-0005-Terminal-Local-Only]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[RISK-0001-Terminal-Exposure]]", "[[RISK-0005-The-Write-Surface]]", "[[ADR-0026-Remote-Workspace-Transport]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"]
tags: [risk, security, remote]
---

# Remote workspace trust boundary

## Description

Remote development expands the trust boundary from one local user/process to a named remote host and every channel the cockpit opens to it. A permissive tunnel, automatic host-key replacement, agent forwarding, unbounded filesystem path, or stale reconnect can turn a familiar SSH workflow into credential disclosure or execution against the wrong machine/repository. A remote sidecar exposed on the LAN would recreate [[RISK-0001-Terminal-Exposure]] on the remote host.

## The sharper hazard, added 2026-08-13

Two decisions — **full write parity** for remote workspaces and **shared, multi-user hosts in scope** — combine into a hazard neither carries alone.

The sidecar's twenty mutating routes are guarded by one check, `_require_loopback()` (`src/project_os_cockpit/server.py:1578`). Bound to `127.0.0.1` on a shared host, it is reachable by **every other account on that host**, and their requests are loopback requests that the gate accepts. The surface that opens is not limited to note edits: it includes `POST /api/cockpit/dispatch`, which starts agent commands. The realistic worst case is therefore **unauthenticated command execution on the remote host, by a local peer who never authenticated over SSH**, in a repository the cockpit is actively writing.

The premise being violated is the one `REQ-0027` and [[REQ-0034]] never had to state: *loopback means the user*. REQ-0034 authenticates a **non-loopback** write and so does not reach a co-tenant, who is a loopback peer.

## Mitigation

- Require normal OpenSSH host-key verification and an explicit response to key change; use the user's SSH agent/config rather than persisting secrets.
- **Authorise remote mutations by something other than the remote loopback interface** — either an stdio channel with no listener to reach, or per-request proof on the mutating routes ([[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]). [[ADR-0026]] eliminates the unauthenticated-listener shape for this reason.
- Make every remote docs, filesystem, and PTY channel travel through the selected SSH connection; bind any remote helper to loopback or stdio only, pinning `--bind 127.0.0.1` explicitly rather than inheriting a default.
- Scope filesystem and terminal CWDs to the configured project root after canonical-path resolution; visibly identify host and root in every workspace surface.
- Treat transport loss as capability loss: invalidate live data and require a fresh verified connection.
- Test hostile paths, host-key changes, malformed remote responses, dropped tunnels, and remote listener exposure on a real host **from a second account on that host**, not only from a LAN peer.

## Triggers

- Any proposal to forward the local SSH agent, accept a new host key automatically, save passwords/keys, or run a remote helper on a non-loopback interface.
- **Any design in which the remote host's loopback interface is what authorises a write** — including "it's only reachable locally on that box".
- **A remote helper started on a host with other user accounts, before [[TASK-0413]] lands.**
- Any file API that can escape the selected remote root, or any remote write/edit API added beyond the selected transport contract.
- A remote session whose displayed host/root differs from the process/sidecar actually serving it.

## Closing condition

This risk closes on [[TST-0024-Remote-SSH-Workspace-Walk]] evidence from two real machines **including a second account on the remote host** attempting the mutating routes and the terminal — not on a design review, and not on a walk performed only as the connecting user.
