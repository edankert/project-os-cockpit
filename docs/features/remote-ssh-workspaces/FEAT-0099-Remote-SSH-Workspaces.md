---
type: "[[feature]]"
id: FEAT-0099
aliases: ["FEAT-0099"]
title: "Remote SSH workspaces — repos, project-os context and agent terminals on another machine"
status: backlog
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["User request 2026-08-12: work against a remote repository in the cockpit as in VS Code Remote SSH, with project-os docs visible beside agent CLIs", "Edwin 2026-08-13 on review: full write parity; shared/multi-user hosts in scope; a remote workspace is a full fleet member; the PTY channel is the spike's to decide"]
goal: "Make an authenticated SSH-connected host feel like a cockpit workspace: browse its repository, read and write its project-os record, run interactive agent CLIs in remote terminals, and carry the fleet surfaces with it — without exposing a shell service on either LAN and without letting a co-tenant on the remote host inherit the write surface."
requirements: ["[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[REQ-0036-Remote-Development-Workflow]]"]
tasks: ["[[TASK-0405-Define-Remote-Session-Architecture]]", "[[TASK-0406-Manage-SSH-Connection-Profiles]]", "[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0408-Provide-Remote-Terminals-And-Agent-Launchers]]", "[[TASK-0409-Deliver-Remote-Repository-Browser]]", "[[TASK-0410-Verify-Remote-Connection-Safety-And-Recovery]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]", "[[TASK-0412-Fleet-Surfaces-For-A-Remote-Workspace]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
related: ["[[REQ-0005-Terminal-Local-Only]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[ADR-0002-Terminal-Approach]]", "[[RISK-0001-Terminal-Exposure]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[ADR-0026-Remote-Workspace-Transport]]", "[[ISS-0154-Existing-Terminals-Lose-Keyboard-Input-After-Workspace-Switch]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"]
tags: [feature, remote, security]
---

# Remote SSH workspaces

## Goal

The desktop cockpit can open a repository on a remote development host through SSH and present its project-os docs, directory tree, and interactive terminal sessions together. A user can launch an installed CLI such as `claude`, `codex`, or another configured framework in that remote terminal and work in the remote repository without moving credentials, source, or terminal exposure onto the LAN.

## Decisions taken 2026-08-13

Three answers from Edwin change the shape of the work, and are recorded here because each removes an option a later session would otherwise re-derive:

1. **Full write parity.** Anything doable to a local workspace is doable to a remote one. Remote writes are not deferred behind a later decision — which means the authorisation question is live now, not later.
2. **Shared, multi-user hosts are in scope.** Not only machines Edwin owns alone. With (1) this eliminates an unauthenticated remote loopback sidecar ([[ADR-0026]]) and makes [[TASK-0413]] a gate rather than a nicety.
3. **A remote workspace is a full fleet member.** Agent state, validator health, git, commits and instrumentation get remote paths — [[TASK-0412]], which is why this feature is larger than its first six tasks suggested.

The PTY channel remains the spike's to decide ([[TASK-0405]]), with a fourth candidate now recorded in [[ADR-0026]].

## Scope

- Named connection profiles using OpenSSH configuration, key-agent authentication, host-key verification, jump hosts, and per-profile remote project roots.
- A remote workspace rail entry whose status distinguishes disconnected, connecting, connected, and reconnecting, and whose label makes the host and remote root unambiguous. **A remote profile survives a launch while its host is unreachable** — today's store drops any workspace whose root does not stat (`desktop/src/ipc/workspaces.ts:196`).
- Remote repository navigation: directories, file metadata, text preview, git branch/status, and an explicit open-in-terminal action. Browsing itself is read-only; write parity is delivered through the record's own write routes, authorised per [[REQ-0035]].
- A sidecar on the remote host, reached only through an SSH tunnel or SSH stdio channel, so the existing docs renderer, live updates, and project-os graph describe the remote repository — including how that sidecar gets there and stays version-matched ([[TASK-0411]]).
- **One remote PTY session per remote workspace in v1**, with CWD set to the selected remote repository. Framework launchers are discovery-driven: show supported CLIs that are installed remotely, never install them or copy local credentials.
- Fleet-surface parity ([[TASK-0412]]): every surface that reads the workspace root locally either reaches the remote host or states that it cannot.
- Connection loss, host-key change, and remote-sidecar failure handling that preserves no false claim of a live session and offers a deliberate reconnect.

## Out of scope

- Binding the existing embedded terminal or any PTY bridge to a network interface. [[REQ-0005-Terminal-Local-Only]] remains true. The mode-3 terminal has no listener at all today (node-pty over IPC) and gains none here.
- Replacing SSH with a bespoke remote-execution protocol, storing passwords/private keys in the record, or forwarding the local SSH agent by default.
- A cloud relay, multi-user collaboration, or access from an untrusted browser.
- **Multiple concurrent terminal sessions per workspace.** The shell keys one PTY per workspace (`desktop/src/ipc/terminal.ts`) and the renderer reuses a single xterm — which is the surface [[ISS-0154]] is about. Multi-session is a local capability first, and a separate piece of work; the original scope line promising it for remote only has been narrowed to match [[TASK-0408]].
- **Pushing from a remote workspace.** A remote fleet member would otherwise inherit the roll-up's push action and publish from a machine the user is not sitting at. Refused for this phase; re-openable with its own decision.
- Automatic framework installation, autonomous execution, or deploy behaviour.

## Acceptance

- A user can select a verified SSH profile, choose a remote directory containing `SNAPSHOT.yaml`, and see that remote repository's project-os notes beside its remote terminal within one desktop workspace.
- Starting `claude`, `codex`, or another discovered launcher runs on the remote host in the selected project directory; the terminal supports normal interactive use, resize, scrollback, copy and paste.
- The remote docs service and terminal endpoints are reachable only through the authenticated SSH connection; neither binds to a LAN interface as a consequence of this feature.
- **A second local account on the remote host cannot write a note, dispatch an agent, or open a cockpit terminal** against the connected workspace.
- **Every fleet surface either reports the remote workspace correctly or says it cannot reach it** — no clean git status because `git -C` failed, no zero-error validator result because the validator never ran, no absent agent state rendered as idle.
- An untrusted/new host key, unavailable host, or dropped connection does not reconnect silently or continue displaying stale remote state as current; **and a remote workspace is still configured after a launch while its host was unreachable.**
- Local workspaces and their loopback-only terminal behaviour remain unchanged.

## Links

- Phase: [[PHASE-033-The-Workspace-Is-Not-Always-Local]]
- Requirements: [[REQ-0035-Secure-Remote-Workspace-Connection]], [[REQ-0036-Remote-Development-Workflow]]
- Transport decision to make before implementation: [[ADR-0026-Remote-Workspace-Transport]]
- Threat model: [[RISK-0007-Remote-Workspace-Trust-Boundary]]
- Adjacent requirement whose wording does not reach a co-tenant: [[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]
