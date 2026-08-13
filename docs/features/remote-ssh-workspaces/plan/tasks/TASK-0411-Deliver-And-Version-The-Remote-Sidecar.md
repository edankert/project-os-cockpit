---
type: "[[task]]"
id: TASK-0411
title: "Deliver the remote sidecar and keep it version-matched"
status: backlog
owner: unassigned
created: 2026-08-13
updated: 2026-08-13
source: ["Review 2026-08-13: nothing in the plan said how the sidecar reaches the remote host, or what happens when it is a different version than the shell driving it"]
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

## Definition of Done

- [ ] The remote sidecar's presence, version, and Python floor are detected before a workspace claims to be connected, and a missing or too-old install produces an actionable message rather than a failed health poll.
- [ ] There is one decided answer to how the code gets there — documented prerequisite, or shell-driven delivery over the existing SSH connection — with the security consequence of each stated (delivery writes executable content to the remote host).
- [ ] A version mismatch between shell and remote sidecar is detected by the capability handshake [[ADR-0026]] already requires, and degrades explicitly: named unavailable capabilities, never a silently different surface.
- [ ] The remote bootstrap pins `--bind 127.0.0.1` explicitly rather than inheriting the CLI default, and the started process is owned, supervised, and cleaned up.

## Steps

- [ ] Decide prerequisite-vs-delivery and record it in [[ADR-0026]] or its own note.
- [ ] Specify the capability handshake payload: sidecar version, Python version, available routes, whether `fleet_validate` can run.
- [ ] Implement detection, the degraded-capability surface, and remote process lifecycle/cleanup.
- [ ] Cover the mismatch and missing-runtime paths in the walk and in automated tests.
