---
type: "[[change]]"
id: CHG-20260812-Plan-Remote-SSH-Workspaces
title: "Plan Remote SSH Workspaces"
status: draft
owner: user:edwin
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["User request 2026-08-12", "Review + decisions 2026-08-13"]
commit: ""
pr: ""
impacts: ["desktop workspace lifecycle and rail identity", "the sidecar's mutation authorisation model", "every fleet surface that reads a workspace root locally"]
issues: []
features: ["[[FEAT-0099-Remote-SSH-Workspaces]]"]
related: ["[[PHASE-033-The-Workspace-Is-Not-Always-Local]]", "[[ADR-0026-Remote-Workspace-Transport]]", "[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[REQ-0036-Remote-Development-Workflow]]", "[[RISK-0007-Remote-Workspace-Trust-Boundary]]", "[[TST-0024-Remote-SSH-Workspace-Walk]]", "[[REQ-0005-Terminal-Local-Only]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[RISK-0001-Terminal-Exposure]]"]
---

# Plan Remote SSH Workspaces

## Summary

Added the documentation-first backlog for authenticated remote SSH workspaces: a remote project-os sidecar, remote repository browsing, and interactive agent terminals that remain inside SSH rather than exposing the existing terminal over the LAN.

**Revised 2026-08-13** after a review against the code, and three decisions from Edwin: **full write parity** for remote workspaces, **shared/multi-user hosts in scope**, and **a remote workspace is a full fleet member**. The work now has its own phase, [[PHASE-033-The-Workspace-Is-Not-Always-Local]].

## What the review changed

- **The security question moved from later to now.** Attaching the remote docs sidecar attaches twenty mutating routes guarded only by `_require_loopback()` (`src/project_os_cockpit/server.py:1578`), `POST /api/cockpit/dispatch` among them. On a shared host every other account passes that gate. [[ADR-0026]] eliminates the unauthenticated-remote-listener alternative on that basis, [[REQ-0035]] gains a co-tenant criterion, [[RISK-0007]] gains the trigger, and [[TASK-0413]] is new.
- **[[REQ-0034]] moved from a soft dependency to a hard one**, and its wording was found not to reach this case: it authenticates a *non-loopback* write, and a co-tenant writes over loopback. The premise both it and REQ-0027 rest on — *loopback means the user* — is false for the first time here.
- **Three tasks added:** [[TASK-0411]] (get the sidecar onto the remote host and keep it version-matched), [[TASK-0412]] (fleet surfaces reach the remote host or say they cannot), [[TASK-0413]] (authorise remote writes without loopback).
- **Two scope items narrowed:** multiple concurrent remote PTY sessions (the shell keys one PTY per workspace and shares one xterm — the surface [[ISS-0154]] is about), and pushing from a remote workspace (refused for this phase).
- **One trap recorded before it was built:** `loadStored()` drops any workspace whose root does not stat, so a naively modelled remote workspace would delete itself on the first offline launch ([[TASK-0406]]).
- **[[TST-0024]]'s `last_verified` cleared** — it had been set to the authoring date for a walk that was never run, starting a staleness clock from a run that did not happen — and the walk gained the co-tenant, fleet-surface and offline-relaunch steps.

## Impact

- Desktop workspace lifecycle and rail identity.
- Existing local-only terminal/security contract ([[REQ-0005-Terminal-Local-Only]], [[RISK-0001-Terminal-Exposure]]) — unchanged, and explicitly out of scope.
- The sidecar's write-authorisation model, which this is the first work to place on a host the user may not own alone.
- Future authenticated non-loopback access work ([[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]), now a hard dependency shared with [[PHASE-029]].

## Documentation Coverage (All Types Considered)

- features: updated
- requirements: updated
- tasks: new
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: updated
- risks: updated
- changes: updated
- snapshot: updated
- phases: new

## Follow-ups

- [ ] Decide [[ADR-0026-Remote-Workspace-Transport]] from a real-host transport spike before implementation ([[TASK-0405]]).
- [ ] Settle whether [[PHASE-033]] shares [[PHASE-029]]'s authenticated write path or builds its own — one question, one mechanism.
- [ ] Re-open [[RISK-0007-Remote-Workspace-Trust-Boundary]] during implementation and close it only with [[TST-0024-Remote-SSH-Workspace-Walk]] evidence including the second-account step.

## Note

No code was written for this. The whole of FEAT-0099 remains `backlog`, and [[PHASE-033]] is `planned`.
