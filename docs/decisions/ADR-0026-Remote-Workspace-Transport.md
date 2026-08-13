---
type: "[[adr]]"
id: ADR-0026
aliases: ["ADR-0026"]
title: "Remote workspace transport — SSH is the boundary; the channel within it is now constrained by write parity and shared hosts"
status: proposed
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "Edwin 2026-08-13, on review: remote workspaces get FULL WRITE PARITY, and SHARED/MULTI-USER hosts are in scope"]
decision: "Pending TASK-0405's spike: use verified OpenSSH for all remote traffic. Write parity plus shared hosts eliminate a plain local-forward to an unauthenticated remote loopback sidecar — the surviving candidates are SSH stdio RPC, or a remote loopback listener whose mutating routes authenticate per request."
context: "The cockpit needs VS Code Remote SSH-like access without changing REQ-0005's loopback-only shell boundary or adding a bespoke unauthenticated remote-execution service."
alternatives: ["SSH stdio RPC/subsystem", "SSH local port forwarding to an authenticated remote loopback sidecar", "SSH local port forwarding to an unauthenticated remote loopback sidecar (eliminated 2026-08-13)", "Plain ssh inside the existing node-pty for the PTY leg", "Direct network HTTP/WebSocket service", "Mount the remote filesystem locally"]
consequences: ["The selected channel must preserve host-key verification, avoid secret persistence and agent forwarding by default, make remote process lifecycle/reconnection explicit, and authorise mutations by something other than the remote host's loopback interface."]
supersedes: ""
superseded: ""
related: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[ADR-0002-Terminal-Approach]]", "[[ADR-0010]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"]
tags: [adr, security, remote]
---

# Remote workspace transport

## Context

The remote experience needs three different streams: project-os/docs data and live updates, bounded repository navigation, and interactive PTY traffic. They must reach a known remote host with no new LAN-visible terminal or sidecar service. SSH provides mature identity, host-key verification, jump-host support, and the environment developers already use, but the channel shape affects integration, observability, and failure recovery.

**Two answers on 2026-08-13 changed what the channel has to carry.** Edwin decided that a remote workspace gets **full write parity** — anything doable to a local workspace is doable to a remote one — and that **shared, multi-user hosts are in scope**, not only single-user machines he owns.

That combination is not a preference; it removes an option. Tunnelling the docs sidecar is not a read path: the sidecar guards twenty mutating routes with exactly one check, `_require_loopback()` (`src/project_os_cockpit/server.py:1578`), covering note creation and decisions, approvals, inbox writes, design verdicts, and `POST /api/cockpit/dispatch`, which starts agent commands. A sidecar bound to `127.0.0.1` on a shared host is reachable by every other account on that host, and their requests *are* loopback requests. The gate passes them. On such a host the exposure is unauthenticated command execution by a local peer who never authenticated over SSH.

The premise underneath `REQ-0027` and [[REQ-0034]] — **loopback means the user** — is true on a personal Mac and false here. REQ-0034 frames the problem as authenticating a *non-loopback* write; a remote co-tenant is a loopback write, so REQ-0034 as written does not reach this case.

## Decision

**SSH is mandatory. Within it, the channel is undecided but no longer unconstrained.**

The selected design must have one explicit remote bootstrap/lifecycle contract and versioned capability negotiation. It cannot rely on a generic TCP listener, automatic host-key replacement, saved credentials, or default SSH-agent forwarding. To those, 2026-08-13 adds:

**A remote mutation must be authorised by something other than the remote host's loopback interface.** Two shapes satisfy that, and TASK-0405's spike chooses between them:

1. **No listener** — an stdio/subsystem channel. Nothing on the remote host is bindable, so there is no co-tenant path to reach. Authorisation is the SSH connection itself, which is exactly the property being claimed.
2. **A listener that authenticates** — a remote loopback sidecar whose mutating routes require per-request proof, i.e. [[REQ-0034]]'s substance applied to a loopback peer rather than only a LAN peer. This makes REQ-0034 a **hard** dependency of FEAT-0099 rather than the soft one PLAN.md recorded.

The **PTY leg may be decided separately** from the docs/filesystem leg. Neither PTY candidate involves a listener, so it carries none of the constraint above.

## Alternatives

- **SSH stdio RPC/subsystem:** strongest single-channel boundary, no remote port, and the only option where a co-tenant has nothing to connect to. Needs a framed protocol and may make browser-compatible streaming/PTY multiplexing more involved.
- **Local forwarding to an *authenticated* remote loopback sidecar:** reuses much of the existing HTTP/SSE design and keeps the remote listener OS-enforced local, but requires building per-request authentication into the sidecar first, plus careful port/lifecycle ownership and tunnel-loss detection.
- **Local forwarding to an *unauthenticated* remote loopback sidecar: eliminated 2026-08-13.** It was the cheapest path and is the one a spike would drift into by default. With write parity on a shared host it grants every co-tenant the full mutation surface, `dispatch` included. Recorded here precisely so it is not re-derived as "the obvious approach".
- **Plain `ssh` inside the existing node-pty, for the PTY leg only:** `desktop/src/ipc/terminal.ts` already runs PTYs as node-pty children in the main process over IPC, with no listener anywhere; `pty.spawn('ssh', ['-tt', host, …])` — optionally landing in `tmux -L cockpit new-session -A` on the remote — reuses the existing backlog/attach/resize path and buys survivability across drops, which is the same trick the local design already uses (`terminal.ts:50-104`). Smallest diff of any option; decouples TASK-0408 from TASK-0405.
- **Direct network HTTP/WebSocket service:** rejected for v1 because it recreates authentication and terminal-exposure problems SSH already solves.
- **Mount the remote filesystem locally:** not sufficient — no remote terminal/agent execution, blurs local/remote identity, and shifts network/filesystem semantics into every existing code path.

## Consequences

- TASK-0405 produces the decision and a real-host proof before UI/protocol implementation begins, and its threat model must now include **a second local account on the remote host**, not only a LAN peer.
- Whichever shape wins, the remote bootstrap must pin `--bind 127.0.0.1` explicitly rather than inherit the CLI default, and must state what happens when the remote sidecar is a different version than the shell driving it.
- The transport abstraction must not bake in a single agent CLI; it carries terminal sessions and discovered launcher capabilities.
- **Remote file editing is not implied by browsing, but write parity means the cockpit's own write routes travel with the docs channel.** The question is no longer *whether* remote writes exist — Edwin decided they do — but what proves who is asking.
- [[REQ-0034]]'s statement needs a companion clause, or a successor, for the case its wording does not reach: a loopback peer on a host the user does not own alone.
