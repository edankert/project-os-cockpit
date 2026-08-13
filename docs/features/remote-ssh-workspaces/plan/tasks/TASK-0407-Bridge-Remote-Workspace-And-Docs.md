---
type: "[[task]]"
id: TASK-0407
title: "Bridge a remote project-os workspace and docs sidecar"
status: backlog
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
source: []
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: L
depends: ["[[TASK-0405-Define-Remote-Session-Architecture]]", "[[TASK-0406-Manage-SSH-Connection-Profiles]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
blocks: ["[[TASK-0409-Deliver-Remote-Repository-Browser]]", "[[TASK-0412-Fleet-Surfaces-For-A-Remote-Workspace]]"]
related: ["[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[REQ-0036-Remote-Development-Workflow]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Bridge a remote project-os workspace and docs sidecar

**Attaching the sidecar attaches its write routes.** The sidecar is not a read surface: twenty mutating routes ride the same origin, guarded only by `_require_loopback()`. This task therefore depends on [[TASK-0413]] — the bridge may not be built on the assumption that "browsing is read-only". Delivery and version-matching of the remote sidecar are [[TASK-0411]]'s; fleet surfaces beyond the rail and renderer are [[TASK-0412]]'s.

## Definition of Done

- [ ] Selecting a profile discovers or validates a remote project root containing `SNAPSHOT.yaml` and starts/attaches to its remote sidecar over the selected SSH channel.
- [ ] The rail, note renderer, link graph, watcher state, and session state are scoped by remote workspace identity and cannot be confused with a same-named local repository.
- [ ] Loss of the tunnel changes the workspace to disconnected and removes stale live/agent claims until a fresh connection succeeds.

## Steps

- [ ] Define remote workspace identity and sidecar capability negotiation.
- [ ] Implement remote bootstrap, tunnel/stdio lifecycle, and cleanup.
- [ ] Map sidecar events and docs requests into the desktop renderer with reconnect support.
