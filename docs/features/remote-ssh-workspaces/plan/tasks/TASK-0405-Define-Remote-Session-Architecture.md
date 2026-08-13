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
depends: []
blocks: ["[[TASK-0406-Manage-SSH-Connection-Profiles]]", "[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0408-Provide-Remote-Terminals-And-Agent-Launchers]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
related: ["[[ADR-0026-Remote-Workspace-Transport]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Define the remote-session transport and trust boundary

**Narrowed 2026-08-13.** Edwin's decisions — full write parity, shared/multi-user hosts in scope — eliminate an unauthenticated remote loopback sidecar, so the spike compares **stdio** against **an authenticated remote listener**. The **PTY leg may be answered separately**: neither PTY candidate involves a listener, so it carries none of that constraint, and answering it early unblocks [[TASK-0408]] independently.

## Definition of Done

- [ ] [[ADR-0026-Remote-Workspace-Transport]] records the selected SSH transport, identity/host-key policy, remote process lifecycle, permitted channels, and explicitly rejected alternatives.
- [ ] A throwaway remote-host spike demonstrates an interactive PTY and docs request through the selected channel with no non-loopback listener.
- [ ] The resulting protocol has a versioned capability handshake and clean disconnect semantics.
- [ ] **The spike states what authorises a mutation** on a host with other accounts on it, and hands [[TASK-0413]] either a mechanism to build or a structural property to prove.
- [ ] **The agent-state question is answered**: how a remote workspace's state reaches the rail without one held-open SSH connection per remote workspace — the local poller was built precisely to avoid that cost.

## Steps

- [ ] Compare SSH stdio RPC against local forwarding to an **authenticated** remote loopback sidecar; record the eliminated unauthenticated variant so it is not re-derived as the obvious approach.
- [ ] Evaluate the PTY leg separately, including plain `ssh` inside the existing node-pty with `tmux` on the remote ([[ADR-0026]] fourth alternative).
- [ ] Specify the remote bootstrap command, environment allow-list, process ownership, and cleanup/reconnect policy.
- [ ] Threat-model forwarding, host-key changes, compromised remote hosts, local credential exposure, **and a second unprivileged account on the remote host**.
