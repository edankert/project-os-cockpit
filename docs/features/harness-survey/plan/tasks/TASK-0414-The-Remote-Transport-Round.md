---
type: "[[task]]"
id: TASK-0414
aliases: ["TASK-0414"]
title: "The remote-transport round — VS Code Remote-SSH, the VS Code Agent Host, and t3.code, surveyed against the one question PHASE-033 has to answer"
status: doing
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'can you do a full review of what the implementation in vscode looks like and possibly in t3.code as well?'"]
parent: "[[FEAT-0080-The-Harness-Survey]]"
effort: M
depends: []
blocks: ["[[TASK-0405-Define-Remote-Session-Architecture]]"]
related: ["[[TASK-0341-The-Not-Taken-List]]", "[[TASK-0342-The-T3-Backlog]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]", "[[ADR-0026-Remote-Workspace-Transport]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
tests: []
---

# The remote-transport round

**Trigger:** a phase about to build something adjacent — one of [[FEAT-0080]]'s three named triggers, and the strongest one. [[PHASE-033]] opens on a transport decision, and two tools have shipped that decision already.

## Method caveat — read first

[[TASK-0340]]'s method begins *read the code, not the marketing*. **This round read documentation and one issue thread, not source.** Every finding below is doc-derived and carries that weight: good enough to reshape the alternatives an ADR considers, **not** good enough to be implemented against. The verification list at the end names what must be read in source before [[TASK-0405]]'s spike commits to anything.

Recording this rather than quietly downgrading the method is the point of having a method.

## The question the round was run against

*What authorises a write to a remote host's helper, when the user does not own that host alone?* [[PHASE-033]] put shared hosts in scope with full write parity, which turned this from a design detail into the phase's gating question.

## What VS Code Remote-SSH does

- **The system `ssh` client does the security.** Host-key verification, `ProxyJump`, agent auth, `~/.ssh/config` — all delegated. Nothing bespoke.
- **Two SSH connections:** one to install-or-start the server, one to carry the tunnel it talks over.
- **The server listens on `localhost`, on a random TCP port**, forwarded to the client — the shape [[ADR-0026]] had eliminated. It is made safe by one sentence: *"The server is started with a randomly generated key, and any new connection to the server needs to provide the key. The key is stored on the remote's disk, readable only by the current user."*
- **A second, stronger mode for exactly our case:** `Remote.SSH: Remote Server Listen On Socket` switches the server to a **Unix domain socket** forwarded over SSH, recommended in the docs for hosts "accessed by multiple users at the same time". The co-tenant is excluded by file permissions, with no auth code in the path. Costs: OpenSSH 6.7+, `AllowStreamLocalForwarding yes` in the remote `sshd_config`, Linux/macOS hosts only, and **it disables connection multiplexing**.
- **Version is identity.** The server installs under `~/.vscode-server`, in a directory keyed by the client's commit id; a mismatch is **refused**, not degraded. Delivery is download-on-remote with a fallback to downloading locally and pushing (`remote.SSH.serverDownloadUrl` overrides). There is an explicit *Uninstall VS Code Server from Host* command.
- **Disconnect kills the claim, not the process.** The remote server survives a dropped client, with a **three-hour** default grace window (`remote.SSH.reconnectionGraceTime`, `--reconnection-grace-time`).

## What the VS Code Agent Host does

Newer, and closer to [[FEAT-0099]] than Remote-SSH is: `code agent host --tunnel`, *"starts a server on localhost and protects it with a connection token"*, AHP as JSON-RPC over WebSocket (message port locally), first-party adapters for **Copilot, Claude and Codex inside the host process**, and clients subscribing to URI-addressed channels for **sessions, chats, terminals and changesets** — an initial state snapshot followed by ordered actions, and on reconnect either the missed actions or a fresh snapshot.

That model gives durable terminals **without tmux**, because the host is the source of truth and replays what a client missed. It is the same problem our local tmux trick solves and the same problem [[ISS-0154]] is a symptom of.

## What t3.code does

- Three ways in: expose the desktop backend on an interface, `npx t3 serve` headless, or **the desktop app launches it over SSH** — probing the remote for compatible Node, writing a launcher to `~/.t3/ssh-launch/<host-key>/`, launching-or-reusing the remote server, and forwarding the remote loopback port back. Structurally identical to [[ADR-0026]]'s alternative 2, including the reuse-if-running behaviour `spawnSidecar()` already has.
- **Authorisation is a one-time pairing token exchanged for an authenticated session** (`t3 pair`, `t3 auth` to inspect and revoke), with *"treat pairing URLs and pairing tokens like passwords"*, and Tailscale / T3 Connect recommended for transport security.
- [`pingdotgg/t3code#671`](https://github.com/pingdotgg/t3code/issues/671), open and unanswered: a `BackendTarget` abstraction (`local`, `wsl:auto`, `wsl:<distro>`, future `ssh:<host>`) with a `BackendController` that resolves the target, bootstraps it, holds the connection, and **exposes capability flags** — `requiresLinuxWorkspacePaths`, `supportsNativeFolderPicker` — *"rather than scattering target-specific checks throughout code"*. They chose WSL first deliberately, because it exercises every boundary at once: different OS, path semantics, shell, transport.

## Verdicts

| Capability | Source | Verdict | Where it went |
| --- | --- | --- | --- |
| Per-connection key in a 0600 file on the remote | VS Code | **take** | [[ADR-0026]] alternative; [[TASK-0413]] |
| Unix socket forwarded over SSH, for multi-user hosts | VS Code | **take** | [[ADR-0026]] alternative; [[TASK-0413]] |
| Version-keyed install + refuse-on-mismatch | VS Code | **take** — replaces our "degrade explicitly" | [[TASK-0411]] |
| Download-on-remote with local-push fallback | VS Code | **take** | [[TASK-0411]] |
| An explicit uninstall/cleanup command | VS Code | **take** | [[TASK-0411]] |
| Server survives disconnect; grace window | VS Code | **take** | [[REQ-0035]], [[TASK-0408]] |
| Delegate host-key/ProxyJump to system `ssh` | VS Code | **take** — already our intent, now confirmed | [[TASK-0406]] |
| Capability flags on the target, not `if (remote)` in five surfaces | t3.code #671 | **take** | [[TASK-0412]] |
| Linux as the first remote target, not a second Mac | t3.code #671 | **take** | [[TASK-0405]] |
| Snapshot + ordered actions with replay-on-reconnect | Agent Host | **adapt** — the shape to copy if a channel protocol is built; not a reason to build one | [[TASK-0405]] |
| Pairing token exchanged for a long-lived session | t3.code | **decline** | [[TASK-0341]] |
| Hosted relay tunnels (T3 Connect, dev tunnels) | both | **decline** — already declined in round 1 | [[TASK-0341]] |
| Adopting AHP as our protocol | Agent Host | **decline** | [[TASK-0341]] |

## Did the governance thesis survive contact?

Yes, and more cleanly than round 1. Both tools solve *reaching* a remote machine; neither holds an opinion about whether the work done there was right. The decline of t3's pairing-session model is the sharpest example: [[REQ-0034]] had already rejected that shape in as many words — *"a surface that authenticates once and then writes freely is a session, and a session on a shared network is a shared session"* — a year-zero requirement out-reasoning a shipped product, which is what the thesis predicts.

## Definition of Done

- [x] Takes filed against the phase they belong to ([[PHASE-033]]), not listed here as prose.
- [x] Declines recorded with reasons in [[TASK-0341]].
- [x] The doc-not-source caveat recorded rather than glossed.
- [ ] The source-verification list below is worked through before [[TASK-0405]]'s spike commits.

## To verify in source before the spike commits

- [ ] How the VS Code connection key actually reaches the client — read over the SSH channel, or printed by the bootstrap command and captured from stdout? This determines whether our sidecar can do the same with the connection we already have.
- [ ] Whether the key is per-server-instance or per-connection, and what its lifetime is.
- [ ] What `AllowStreamLocalForwarding` defaults to on the distributions we would target — the socket mode is worthless if the default is `no` and the user cannot edit `sshd_config`.
- [ ] Whether socket mode's loss of multiplexing is intrinsic to `-L` socket forwarding or a client-side choice — [[PLAN]]'s agent-state question depends on the answer.
- [ ] t3's SSH launcher script: what it writes to the remote host, with what permissions, and whether the forwarded port is authenticated at all in that mode or relies on the tunnel alone.
