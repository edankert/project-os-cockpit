---
type: "[[task]]"
id: TASK-0408
title: "Provide remote terminals and framework launchers"
status: backlog
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
source: []
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: L
depends: ["[[TASK-0405-Define-Remote-Session-Architecture]]", "[[TASK-0406-Manage-SSH-Connection-Profiles]]"]
blocks: []
related: ["[[REQ-0005-Terminal-Local-Only]]", "[[ADR-0002-Terminal-Approach]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Provide remote terminals and framework launchers

**One session per remote workspace in v1**, matching the local shell: `desktop/src/ipc/terminal.ts` keys one PTY per workspace and the renderer reuses a single xterm. FEAT-0099's original scope line promised multiple concurrent remote sessions; it has been narrowed to match, because multi-session is a local capability first and touches the surface [[ISS-0154]] is about.

This leg **need not wait on the docs channel**: no PTY candidate involves a listener, so [[TASK-0405]] can answer it independently. The cheapest candidate is plain `ssh` inside the existing node-pty, optionally landing in `tmux -L cockpit new-session -A` on the remote — the same survivability trick the local design already uses, one hop away ([[ADR-0026]] fourth alternative).

## Definition of Done

- [ ] A remote interactive PTY opens in the selected remote project directory and preserves resize, scrollback, copy/paste, and terminal detach/reconnect semantics.
- [ ] The launcher UI discovers configured remote commands (including `claude` and `codex` when installed) and clearly distinguishes unavailable commands from commands it can start.
- [ ] Agent lifecycle instrumentation is adapted only after a remote session demonstrates accurate identity, work-note attribution, and disconnect behaviour.

## Steps

- [ ] Create a transport-neutral PTY session contract and implement the SSH transport.
- [ ] Add launcher discovery/configuration and remote environment diagnostics.
- [ ] Extend instrumentation with remote workspace/session identifiers; do not assume local transcript paths.
