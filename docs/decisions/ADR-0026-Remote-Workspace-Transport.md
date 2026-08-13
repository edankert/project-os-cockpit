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
source: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "Edwin 2026-08-13, on review: remote workspaces get FULL WRITE PARITY, and SHARED/MULTI-USER hosts are in scope", "[[TASK-0414-The-Remote-Transport-Round]] — VS Code Remote-SSH and t3.code surveyed 2026-08-13"]
decision: "Pending TASK-0405's spike: use verified OpenSSH for all remote traffic. Write parity plus shared hosts eliminate an UNAUTHENTICATED local-forward to a remote loopback sidecar; four candidates survive, two of them borrowed from VS Code — a remote Unix socket forwarded over SSH, a loopback listener holding a per-connection key, an SSH stdio channel, and (for the PTY leg alone) plain ssh inside the existing node-pty."
context: "The cockpit needs VS Code Remote SSH-like access without changing REQ-0005's loopback-only shell boundary or adding a bespoke unauthenticated remote-execution service."
alternatives: ["Remote Unix domain socket forwarded over SSH (VS Code's multi-user mode)", "SSH local port forwarding to a remote loopback listener holding a per-connection key (VS Code's default)", "SSH stdio RPC/subsystem", "Plain ssh inside the existing node-pty for the PTY leg", "SSH local port forwarding to an unauthenticated remote loopback sidecar (eliminated 2026-08-13)", "Direct network HTTP/WebSocket service", "Mount the remote filesystem locally"]
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

**A remote mutation must be authorised by something other than the remote host's loopback interface.** Three shapes satisfy that, and TASK-0405's spike chooses between them:

1. **No listener** — an stdio/subsystem channel. Nothing on the remote host is bindable, so there is no co-tenant path to reach. Authorisation is the SSH connection itself, which is exactly the property being claimed. Cost: a framed protocol to design and build.
2. **A socket the OS protects** — the remote helper listens on a **Unix domain socket** instead of a TCP port, forwarded over SSH. The co-tenant is excluded by file permissions; there is no auth code in the path and no protocol to invent, because the existing HTTP/SSE design is unchanged. Cost: OpenSSH 6.7+, `AllowStreamLocalForwarding yes` on the remote `sshd`, Linux/macOS hosts only, and **no connection multiplexing**.
3. **A listener that authenticates** — a remote loopback listener holding a **per-connection key** that the client reads over the SSH channel it already has. [[REQ-0034]]'s substance applied to a loopback peer rather than only a LAN peer.

Shapes 2 and 3 were **borrowed, not invented** ([[TASK-0414-The-Remote-Transport-Round]]): 3 is VS Code Remote-SSH's default and 2 is its documented multi-user mode. That changes the reading of the eliminated option below — the unauthenticated forward is not unsound in shape, it is *one sentence of design short*, and the sentence is known.

Either way REQ-0034's substance is a **hard** dependency of FEAT-0099 rather than the soft one PLAN.md recorded — shape 2 satisfies it structurally rather than removing the obligation.

The **PTY leg may be decided separately** from the docs/filesystem leg. Neither PTY candidate involves a listener, so it carries none of the constraint above.

## Alternatives

- **Remote Unix domain socket forwarded over SSH — VS Code's multi-user mode.** The remote helper binds a socket file rather than a port; `ssh -L` forwards to it; the OS's file permissions do the excluding. Keeps the entire existing HTTP/SSE design, invents no protocol, and writes no authentication code — the cheapest of the safe options by a distance. VS Code exposes it as `Remote.SSH: Remote Server Listen On Socket` and recommends it for hosts "accessed by multiple users at the same time". **Its costs are specific and must be checked before choosing it:** OpenSSH 6.7+, `AllowStreamLocalForwarding yes` in the remote `sshd_config` (not universally the default, and not always the user's to change), Linux/macOS hosts only, and it **disables connection multiplexing** — which collides with the plan's open question about polling remote agent state over one shared connection.
- **Local forwarding to a remote loopback listener holding a per-connection key — VS Code's default.** *"The server is started with a randomly generated key, and any new connection to the server needs to provide the key. The key is stored on the remote's disk, readable only by the current user."* Portable, keeps multiplexing, reuses the HTTP/SSE design. Weaker than the socket against a root co-tenant, who can read any file; strong against the ordinary co-tenant that is the actual threat. Requires the sidecar to learn one check it does not have.
- **SSH stdio RPC/subsystem:** strongest single-channel boundary, no remote port, and the only option where a co-tenant has nothing to connect to *and* nothing to read. Needs a framed protocol and may make browser-compatible streaming/PTY multiplexing more involved. Note that neither surveyed tool chose this, which is evidence about its cost rather than its safety.
- **Local forwarding to an *unauthenticated* remote loopback sidecar: eliminated 2026-08-13.** It was the cheapest path and is the one a spike would drift into by default. With write parity on a shared host it grants every co-tenant the full mutation surface, `dispatch` included. Recorded here precisely so it is not re-derived as "the obvious approach" — and note that the two alternatives above are this option *plus one mechanism*, which is why it is eliminated rather than merely discouraged: the fix is small enough that shipping without it would be a choice, not an oversight.
- **Plain `ssh` inside the existing node-pty, for the PTY leg only:** `desktop/src/ipc/terminal.ts` already runs PTYs as node-pty children in the main process over IPC, with no listener anywhere; `pty.spawn('ssh', ['-tt', host, …])` — optionally landing in `tmux -L cockpit new-session -A` on the remote — reuses the existing backlog/attach/resize path and buys survivability across drops, which is the same trick the local design already uses (`terminal.ts:50-104`). Smallest diff of any option; decouples TASK-0408 from TASK-0405.
- **Direct network HTTP/WebSocket service:** rejected for v1 because it recreates authentication and terminal-exposure problems SSH already solves.
- **Mount the remote filesystem locally:** not sufficient — no remote terminal/agent execution, blurs local/remote identity, and shifts network/filesystem semantics into every existing code path.

## Consequences

- TASK-0405 produces the decision and a real-host proof before UI/protocol implementation begins, and its threat model must now include **a second local account on the remote host**, not only a LAN peer.
- Whichever shape wins, the remote bootstrap must pin `--bind 127.0.0.1` explicitly rather than inherit the CLI default, and must state what happens when the remote sidecar is a different version than the shell driving it.
- The transport abstraction must not bake in a single agent CLI; it carries terminal sessions and discovered launcher capabilities.
- **Remote file editing is not implied by browsing, but write parity means the cockpit's own write routes travel with the docs channel.** The question is no longer *whether* remote writes exist — Edwin decided they do — but what proves who is asking.
- [[REQ-0034]]'s statement needs a companion clause, or a successor, for the case its wording does not reach: a loopback peer on a host the user does not own alone.
- **Disconnect must kill the claim without killing the process.** VS Code keeps the remote server alive across a dropped client, with a three-hour default grace window (`remote.SSH.reconnectionGraceTime`). [[REQ-0035]]'s "transport loss revokes capabilities and clears live remote state" is right about the *claim*; read as also killing the remote process, it would end a running agent on a dropped Wi-Fi. The selected design states the grace policy explicitly.
- **The spike's remote host should be Linux, not a second Mac.** t3.code's own remote-target proposal picked WSL first because it exercises every boundary at once — different OS, path semantics, shell, transport. A Mac-to-Mac spike would pass while proving the least.
