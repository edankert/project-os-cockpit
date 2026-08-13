---
type: "[[task]]"
id: TASK-0411
title: "Deliver the remote sidecar and keep it version-matched"
status: backlog
owner: unassigned
created: 2026-08-13
updated: 2026-08-13
source: ["Review 2026-08-13: nothing in the plan said how the sidecar reaches the remote host, or what happens when it is a different version than the shell driving it", "[[TASK-0414-The-Remote-Transport-Round]]: VS Code keys the install directory by commit id and REFUSES a mismatch; t3.code probes for a compatible runtime and writes a launcher script"]
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: M
depends: ["[[TASK-0405-Define-Remote-Session-Architecture]]"]
blocks: ["[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0412-Fleet-Surfaces-For-A-Remote-Workspace]]"]
related: ["[[ADR-0026-Remote-Workspace-Transport]]", "[[RISK-0003-Python-Runtime-Floor]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Deliver the remote sidecar and keep it version-matched

The desktop shell bundles a Python runtime (`desktop/src/ipc/sidecar.ts:76`) specifically so a user never needs a system Python. A remote workspace reintroduces that requirement on a machine the installer never touched, and full fleet membership makes it mandatory rather than optional: `fleet_validate` is a Python entry point that must run **on the remote host** for a remote workspace's validator health to mean anything.

## What the survey settled (2026-08-13)

[[TASK-0414]] found VS Code's answers, and one of them **overrules what this task originally said**:

- **Version is identity, and a mismatch is refused.** The server installs under `~/.vscode-server` in a directory keyed by the client's commit id; a mismatched commit is refused, not negotiated. This task previously required "degrade explicitly with named unavailable capabilities" — that is the weaker choice and it is withdrawn. A shell and a sidecar of different versions are two programs guessing about each other's routes; refusing is simpler to build, simpler to explain, and cannot half-work.
- **Delivery is download-on-remote with a local-push fallback.** VS Code tries to fetch on the remote, and falls back to downloading locally and pushing when the remote has no outbound HTTPS — a case that is common on exactly the hardened hosts this feature targets. t3.code instead probes the remote for a compatible runtime and writes a launcher script under `~/.t3/ssh-launch/<host-key>/`.
- **There is an explicit uninstall.** VS Code ships *Uninstall VS Code Server from Host* — kill the processes, delete the tree. A tool that installs itself on someone else's machine and cannot remove itself is a tool people stop trusting.

## Definition of Done

- [ ] The remote sidecar's presence, version, and Python floor are detected before a workspace claims to be connected, and a missing or too-old install produces an actionable message rather than a failed health poll.
- [ ] There is one decided answer to how the code gets there — documented prerequisite, or shell-driven delivery over the existing SSH connection, or both with a fallback — with the security consequence of each stated (delivery writes executable content to the remote host).
- [ ] **A version mismatch between shell and remote sidecar is refused, with the mismatch named.** Not degraded, not negotiated. The install location is keyed by version so two versions can coexist rather than overwrite.
- [ ] **The cockpit can uninstall itself from a remote host** — stop the processes, remove what it installed — as a first-class action, not a documented `rm -rf`.
- [ ] The remote bootstrap pins `--bind 127.0.0.1` explicitly rather than inheriting the CLI default (or binds the socket, per [[ADR-0026]]), and the started process is owned, supervised, and cleaned up.

## Steps

- [ ] Decide prerequisite-vs-delivery and record it in [[ADR-0026]] or its own note.
- [ ] Specify the version handshake: sidecar version, Python version, and the refusal message a mismatch produces.
- [ ] Implement detection, version-keyed install, refusal, remote process lifecycle/cleanup, and uninstall.
- [ ] Cover the mismatch, missing-runtime, and no-outbound-HTTPS paths in the walk and in automated tests.
