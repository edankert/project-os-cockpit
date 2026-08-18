---
type: "[[test]]"
id: TST-0024
title: "Remote SSH workspace walk — verified host, docs, repository and agent terminal"
status: ready
covers: ["[[FEAT-0099-Remote-SSH-Workspaces]]", "[[REQ-0035-Secure-Remote-Workspace-Connection]]", "[[REQ-0036-Remote-Development-Workflow]]"]
owner: unassigned
created: 2026-08-12
updated: 2026-08-13
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
source: ["[[FEAT-0099-Remote-SSH-Workspaces]]"]
scope: system
kind: manual
level: system
entrypoint: "Two-machine desktop cockpit acceptance walk, with a second account on the remote host"
command: ""
# NOT a run. TEST-FIELDS refuses a manual test with an empty `last_verified:`,
# so a never-executed manual procedure cannot satisfy the schema without naming
# a date. This one is the authoring date, and it means "written", not "walked".
# Filed as [[ISS-0155-A-Never-Run-Manual-Test-Must-Assert-A-Verification-Date]];
# the validator is template-owned, so the fix is upstream, not here.
last_verified: "2026-08-12"
issues: []
tasks: ["[[TASK-0405-Define-Remote-Session-Architecture]]", "[[TASK-0406-Manage-SSH-Connection-Profiles]]", "[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0408-Provide-Remote-Terminals-And-Agent-Launchers]]", "[[TASK-0409-Deliver-Remote-Repository-Browser]]", "[[TASK-0410-Verify-Remote-Connection-Safety-And-Recovery]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]", "[[TASK-0412-Fleet-Surfaces-For-A-Remote-Workspace]]", "[[TASK-0413-Authorize-Remote-Writes-Without-Loopback]]"]
artifacts: []
evidence: ["Procedure recorded 2026-08-12 for planning review only; it has NOT been executed against a remote host. `last_verified` carries the authoring date because the schema refuses an empty one (ISS-0155), not because a walk happened. Treat this test as unverified until the witnesses below are filled."]
last_run: ""
adequacy: "Manual two-machine evidence is required because listener reachability, host-key prompts, SSH-agent use, and interactive agent-terminal behaviour are not equivalent to a mocked transport. Automated transport and path-boundary tests supplement this walk."
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[RISK-0007-Remote-Workspace-Trust-Boundary]]"]
---

# Remote SSH workspace walk

## Purpose

Verify that a real remote project-os repository can be used in the desktop cockpit without weakening the local-only terminal rule or losing the context-and-terminal workflow.

## Procedure

- [ ] Connect to a known SSH profile using a key held by the local SSH agent; verify the displayed host fingerprint and remote project root.
- [ ] Select a remote directory containing `SNAPSHOT.yaml`; verify its docs, navigator, workspace identity, and git state render as remote rather than local.
- [ ] Browse a nested repository directory and a text file; attempt an `..` path and a symlink escape and verify both are refused/identified according to the chosen policy.
- [ ] Open a terminal at that remote directory, resize it, use scrollback and clipboard, then launch an installed remote framework (`claude`, `codex`, or another configured command) and complete one harmless turn.
- [ ] Verify from an independent network peer that the remote helper/terminal port is not reachable outside SSH; verify that no credentials appear in profile data, docs, or logs.
- [ ] **From a second, unprivileged account on the remote host**, attempt each mutating route against the running sidecar (note create/decide, approve, dispatch, inbox) and attempt to open a cockpit terminal. Every attempt must be refused. This is the step the walk exists for — it is the only one that tests the boundary Edwin's 2026-08-13 decisions moved.
- [ ] Confirm the fleet surfaces: agent state, validator health, git/commits for the remote workspace. Then make the host unreachable mid-session and confirm none of them reports the absence as a local fact (no clean git status, no zero-error validator result, no idle agent state).
- [ ] Drop the SSH connection while the workspace and terminal are visible; verify the UI marks it disconnected and no longer reports live docs/agent state. Reconnect and verify a fresh state is established.
- [ ] Quit the app while the remote host is unreachable, relaunch, and verify the remote workspace is **still configured** and shows *not connected* rather than disappearing.
- [ ] Present a changed host key and verify it is refused until the user explicitly resolves it; it must not overwrite the known host automatically.

## Expected results

- Remote docs, repository context, and terminal operate together while the only remote access path is authenticated SSH.
- **A co-tenant on the remote host can reach nothing** — not a write, not a dispatch, not a terminal.
- The selected host/root and connection state are always visible and stale state cannot survive a dropped connection; an unreachable remote workspace is never rendered as healthy.
- The existing local terminal remains loopback-only and local workspaces continue to work unchanged.

## Evidence (fill after running)

**`last_verified` on this note is not evidence.** It is the authoring date, present only because `TEST-FIELDS` refuses an empty one ([[ISS-0155-A-Never-Run-Manual-Test-Must-Assert-A-Verification-Date]]). The walk has not been performed. Populate the following witnesses — that is what makes it verified.

- Remote host identity/fingerprint and project root:
- Listener inspection from remote peer:
- **Co-tenant refusal witness (second account, per route):**
- Terminal/agent session witness:
- Fleet-surface witness (connected, then unreachable):
- Disconnect/reconnect witness:
- Offline-relaunch witness:
- Host-key-change witness:

## Adequacy (who verifies this test?)

An independent reviewer should replay the walk with a separate remote host and inspect listener/process state rather than accepting screenshots alone. The co-tenant step in particular must be replayed by someone who did not build the authorisation path: it is the step whose passing is easiest to assume and hardest to notice missing.
