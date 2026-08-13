---
type: "[[task]]"
id: TASK-0406
title: "Manage verified SSH connection profiles"
status: backlog
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
source: []
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: M
depends: ["[[TASK-0405-Define-Remote-Session-Architecture]]"]
blocks: ["[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0408-Provide-Remote-Terminals-And-Agent-Launchers]]"]
related: ["[[RISK-0007-Remote-Workspace-Trust-Boundary]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Manage verified SSH connection profiles

## Definition of Done

- [ ] Users can add, test, edit, and remove a profile containing host alias, user, port, jump-host policy, and remote project root without the profile persisting private-key material or passwords.
- [ ] OpenSSH config and agent authentication are used where available; host-key mismatch requires an explicit user decision and never silently replaces a known fingerprint.
- [ ] The profile view reports connection state and actionable failures without leaking connection secrets into logs, docs, or session history.
- [ ] **A remote profile survives a launch while its host is unreachable.** Today's store drops any workspace whose root does not stat (`desktop/src/ipc/workspaces.ts:196`, `loadStored()`), and workspace identity is a sha1 of a resolved *local* absolute path (`:56`). Both assume a local directory; a remote entry modelled naively as a `Workspace` is deleted on the first offline start, silently, taking the user's configuration with it.
- [ ] Remote workspace identity is stable, machine-independent, and visibly distinct from a same-named local clone — including in `cockpit://` deep links.

## Steps

- [ ] Define the profile persistence schema and migration/forget behaviour, including the identity scheme and the "unreachable ≠ gone" rule in `loadStored()`.
- [ ] Implement OpenSSH config discovery and connection preflight.
- [ ] Add host-key verification and user-facing failure states.
