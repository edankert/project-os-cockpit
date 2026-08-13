---
type: "[[requirement]]"
id: REQ-0036
aliases: ["REQ-0036"]
title: "A remote project workspace is a full workspace — docs, repository context, agent sessions and fleet surfaces, or an honest statement that a surface cannot reach it"
status: draft
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "Edwin 2026-08-13: a remote workspace is a full fleet member"]
priority: high
scope: "The desktop cockpit workflow for a selected remote repository, including every fleet surface that today reads the workspace's local filesystem"
acceptance: ["A selected remote project root containing SNAPSHOT.yaml renders its project-os notes and graph as an independently identified workspace", "The user can browse the remote repository tree and text previews within the selected root and open a terminal at a selected directory", "The cockpit can start and interact with a remotely installed configured framework such as Claude Code or Codex without assuming it is installed", "Every fleet surface either reports a remote workspace correctly or states that it cannot reach it; none renders unreachability as a local fact", "Remote connection state and agent/session state are visible, stale state is removed on disconnect, and a remote workspace is not lost when the app starts while it is unreachable"]
implements: "[[FEAT-0099-Remote-SSH-Workspaces]]"
verifies: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
related: ["[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[FEAT-0022-Session-Insight-And-Traceability]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
tags: [requirement, remote]
---

# A remote project workspace keeps docs, repository context, agent sessions and fleet surfaces together

## Statement

For a connected remote project root, the desktop cockpit SHALL present the remote project-os record, repository navigation, and remote interactive terminals as one workspace, while making remote identity and connection state unmistakable.

**A remote workspace is a full fleet member.** Every surface that today derives a workspace's state from the local filesystem SHALL either derive it from the remote host, or say plainly that it cannot — and SHALL NOT render an unreachable remote workspace as a local fact.

## What "or say plainly that it cannot" covers

These surfaces read the workspace root, or run a command against it, on the machine the shell is running on:

- `desktop/src/ipc/agent-state-poller.ts` — polls `<root>/.cockpit/agent-state.json`. Its whole design avoids a live connection per workspace; a remote member needs polling multiplexed over one SSH connection, or a held-open subscription, and that choice belongs in the transport design.
- `desktop/src/ipc/fleet-health.ts:150` — reads `<root>/.cockpit/url`; `:346` spawns `python -m project_os_cockpit.fleet_validate` with the **local** interpreter.
- `desktop/src/ipc/git.ts:39` — `git -C <root>`, which backs the git panel, commits and contribution surfaces.
- `desktop/src/ipc/agent-instrument.ts` — generates a ZDOTDIR into local `userData` and injects it into the PTY env; it cannot instrument a remote shell without materialising files on the remote host.

The failure mode this criterion exists to prevent is a remote workspace that looks *healthy*: a clean git status because `git -C` failed, zero validator errors because the validator never ran, and no agent state read as idle.

## Acceptance Criteria

- [ ] A selected remote project root containing `SNAPSHOT.yaml` renders its project-os notes and graph as an independently identified workspace, distinguishable from a same-named local clone in every surface including deep links — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] The user can browse the remote repository tree and text previews within the selected root and open a terminal at a selected directory — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] The cockpit can start and interact with a remotely installed configured framework such as Claude Code or Codex without assuming it is installed — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] **Every fleet surface either reports the remote workspace correctly or states it cannot reach it**; none renders unreachability as a local fact — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]
- [ ] Remote connection state and agent/session state are visible, stale state is removed on disconnect, and **a remote workspace is still there after the app starts while the host is unreachable** — evidence: [[TST-0024-Remote-SSH-Workspace-Walk]]

## Traceability

- Implements: [[FEAT-0099-Remote-SSH-Workspaces]]
- Verified by: [[TST-0024-Remote-SSH-Workspace-Walk]]
