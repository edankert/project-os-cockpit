---
type: "[[plan]]"
title: "Plan — FEAT-0099 Remote SSH workspaces"
status: draft
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
source: []
implements: ["[[FEAT-0099-Remote-SSH-Workspaces]]"]
related: ["[[ADR-0026-Remote-Workspace-Transport]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"]
---

# Plan — FEAT-0099 Remote SSH workspaces

## Delivery sequence

1. **Decide the transport** ([[TASK-0405]]) before any remote UI: one authenticated connection, verified host identity, and an answer to *what authorises a mutation on a host with other accounts on it*. Two shapes survive Edwin's 2026-08-13 decisions — stdio (no listener), or a remote loopback listener whose mutating routes authenticate. The spike proves one on a real host.
2. **Authorise remote writes** ([[TASK-0413]]) — gated by 1, and a prerequisite of anything that carries the write routes. If the spike selects stdio this task is small (state why the property holds); if it selects a listener, this is where the proof mechanism is built.
3. **Connection profiles and lifecycle state** ([[TASK-0406]]), importing safe fields from `~/.ssh/config` while keeping private keys and secrets outside the record — and while surviving a launch with the host down.
4. **Get the sidecar onto the remote host and keep it matched** ([[TASK-0411]]): delivery, version negotiation, upgrade. The desktop bundles a Python runtime precisely so no user needs a system Python; the remote reintroduces that requirement and has to answer it explicitly.
5. **Bridge the remote workspace and docs** ([[TASK-0407]]): map the remote `SNAPSHOT.yaml` workspace into the rail with its own identity, and preserve the existing local workspace contract.
6. **Remote terminals and launcher discovery** ([[TASK-0408]]). The launcher API receives a command/CWD policy, not a hard-coded Claude or Codex implementation. This leg does not depend on the docs channel: no PTY candidate involves a listener, so it can start as soon as 1 names its PTY answer.
7. **Remote repository navigation and context actions** ([[TASK-0409]]).
8. **Fleet-surface parity** ([[TASK-0412]]): agent state, validator health, git/commits, instrumentation — reach the remote host or say so.
9. **Exercise real remote-host, failure, and security cases** ([[TASK-0410]]) before opening this capability beyond a developer preview, including from a second account on the remote host.

## Dependencies

- **Hard:** [[ADR-0026-Remote-Workspace-Transport]] accepted; [[REQ-0035-Secure-Remote-Workspace-Connection]] designed; **[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]'s substance** — full write parity on a shared host means a mutation needs proof that a co-tenant cannot produce, whether or not REQ-0034 itself lands first; a supported remote host with OpenSSH and Python/runtime prerequisites.
- **Soft:** reusable terminal abstraction from [[ADR-0002-Terminal-Approach]].

REQ-0034 moved from soft to hard on 2026-08-13. Its own wording covers a *non-loopback* write and so does not reach a remote co-tenant, who connects over loopback — the gap is recorded in [[REQ-0035]] and [[RISK-0007]]. It also currently gates [[PHASE-029]], which is `planned`, so the sequencing between the two phases needs a deliberate answer rather than a discovery.

## Open questions

- ~~Should the first transport use an SSH stdio RPC channel, local port forwarding to a remote loopback sidecar, or a constrained combination?~~ **Narrowed 2026-08-13**: an *unauthenticated* remote loopback sidecar is eliminated. The spike chooses between stdio and an authenticated listener, and may answer the PTY leg separately.
- ~~Is remote file editing v1 value?~~ **Answered 2026-08-13**: full write parity. The remaining question is not *whether* but *what proves who is asking*.
- Which remote operating systems and authentication arrangements are supported initially (macOS/Linux; ProxyJump; hardware-backed keys; VPN-only hosts)?
- How does a remote workspace's agent state reach the rail — polling multiplexed over one SSH connection, or a held-open subscription per remote workspace? The local poller exists specifically to avoid a live connection per workspace; the remote case inverts that trade and the answer belongs in [[TASK-0405]].
- Does [[PHASE-033]] wait on [[PHASE-029]]'s authenticated write path, share it, or build its own? Answering this early avoids two mechanisms for one question.
