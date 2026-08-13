---
type: "[[task]]"
id: TASK-0405
title: "Define the remote-session transport and trust boundary"
status: backlog
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
source: []
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: M
depends: ["[[TASK-0414-The-Remote-Transport-Round]]"]
blocks: ["[[TASK-0406-Manage-SSH-Connection-Profiles]]", "[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0408-Provide-Remote-Terminals-And-Agent-Launchers]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
related: ["[[ADR-0026-Remote-Workspace-Transport]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[TASK-0414-The-Remote-Transport-Round]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Define the remote-session transport and trust boundary

**Narrowed 2026-08-13**, twice. Edwin's decisions — full write parity, shared/multi-user hosts in scope — eliminate an *unauthenticated* remote loopback sidecar. Then [[TASK-0414-The-Remote-Transport-Round]] found that VS Code ships both of the safe shapes, so the spike is a **comparison of three known designs, not a search**:

1. **Remote Unix socket forwarded over SSH** — file permissions exclude the co-tenant, no auth code, HTTP/SSE design unchanged. Needs OpenSSH 6.7+, `AllowStreamLocalForwarding yes`, Linux/macOS, and **gives up connection multiplexing**.
2. **Loopback listener + per-connection key** — VS Code's default; portable, keeps multiplexing, one guard to add, key readable by root.
3. **stdio channel** — nothing to connect to and nothing to read, at the cost of a framed protocol. Neither surveyed tool chose it.

**Do not spend the spike inventing a fourth.** The **PTY leg may be answered separately**: neither PTY candidate involves a listener, so it carries none of that constraint, and answering it early unblocks [[TASK-0408]] independently.

**The multiplexing question and the socket question are one question.** The plan asks how remote agent state reaches the rail without a held-open connection per remote workspace; the obvious answer was `ControlMaster` multiplexing over one connection — which option 1 disables. Resolve them together or the spike will answer each in a way that breaks the other.

**Spike against a Linux host, not a second Mac.** t3.code chose WSL as its first remote target deliberately, because it exercises OS, path semantics, shell and transport at once. A Mac-to-Mac spike passes while proving the least.

## Definition of Done

- [ ] [[ADR-0026-Remote-Workspace-Transport]] records the selected SSH transport, identity/host-key policy, remote process lifecycle, permitted channels, and explicitly rejected alternatives.
- [ ] A throwaway remote-host spike demonstrates an interactive PTY and docs request through the selected channel with no non-loopback listener.
- [ ] The resulting protocol has a versioned capability handshake and clean disconnect semantics.
- [ ] **The spike states what authorises a mutation** on a host with other accounts on it, and hands [[TASK-0413]] either a mechanism to build or a structural property to prove.
- [ ] **The agent-state question is answered**: how a remote workspace's state reaches the rail without one held-open SSH connection per remote workspace — the local poller was built precisely to avoid that cost.

## Steps

- [ ] Work [[TASK-0414]]'s source-verification list first — the round read docs, not source, and three of its five open items decide between the options above.
- [ ] Compare the three known designs on a real Linux host; record the eliminated unauthenticated variant so it is not re-derived as the obvious approach.
- [ ] Evaluate the PTY leg separately, including plain `ssh` inside the existing node-pty with `tmux` on the remote ([[ADR-0026]] fourth alternative).
- [ ] Specify the remote bootstrap command, environment allow-list, process ownership, and cleanup/reconnect policy.
- [ ] Threat-model forwarding, host-key changes, compromised remote hosts, local credential exposure, **and a second unprivileged account on the remote host**.
