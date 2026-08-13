---
type: "[[task]]"
id: TASK-0410
title: "Verify remote connection safety and recovery"
status: backlog
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
source: []
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: M
depends: ["[[TASK-0406-Manage-SSH-Connection-Profiles]]", "[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0408-Provide-Remote-Terminals-And-Agent-Launchers]]", "[[TASK-0409-Deliver-Remote-Repository-Browser]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]", "[[TASK-0412-Fleet-Surfaces-For-A-Remote-Workspace]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
blocks: []
related: ["[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[REQ-0035-Secure-Remote-Workspace-Connection]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Verify remote connection safety and recovery

## Definition of Done

- [ ] [[TST-0024-Remote-SSH-Workspace-Walk]] passes against a real remote host and covers connect, browse, docs, remote agent terminal, disconnect, reconnect, rejection, and no-LAN-listener evidence.
- [ ] **The walk is performed from a second, unprivileged account on the remote host** attempting the mutating routes and the terminal. A pass without that account is not a pass ([[RISK-0007]] closing condition).
- [ ] Automated tests cover host-key mismatch, path traversal/symlink escape, malformed remote capability data, remote command failure, stale-state clearing, **and an unreachable remote workspace never rendering as clean/idle/zero**.
- [ ] The residual risks and supported-host limitations are documented before any non-preview release — including which host classes are supported, now that shared hosts are in scope.

## Steps

- [ ] Build an isolated SSH test fixture and a manual two-machine acceptance environment **with a second user account on the remote side**.
- [ ] Add transport/PTY/filesystem adversarial tests and failure injection.
- [ ] Run the final risk review and record evidence.
