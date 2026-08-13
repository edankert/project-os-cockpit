---
type: "[[task]]"
id: TASK-0412
title: "Carry the fleet surfaces to a remote workspace, or make them say they cannot"
status: backlog
owner: unassigned
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: a remote workspace is a full fleet member", "Review 2026-08-13: five surfaces read the workspace root on the local machine and would render a remote workspace as healthy-and-empty"]
parent: "[[FEAT-0099-Remote-SSH-Workspaces]]"
phase: "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
effort: L
depends: ["[[TASK-0407-Bridge-Remote-Workspace-And-Docs]]", "[[TASK-0411-Deliver-And-Version-The-Remote-Sidecar]]"]
blocks: []
related: ["[[REQ-0036-Remote-Development-Workflow]]", "[[FEAT-0028]]", "[[FEAT-0019]]"]
tests: ["[[TST-0024-Remote-SSH-Workspace-Walk]]"]
---

# Carry the fleet surfaces to a remote workspace, or make them say they cannot

Five surfaces derive a workspace's state from the machine the shell runs on. Against a remote workspace each fails **quietly and in the reassuring direction** — a clean git status because the command errored, zero validator errors because the validator never ran, no agent state read as idle. That is the failure this task exists to prevent; parity is the goal, honesty is the floor.

| Surface | Local assumption |
| --- | --- |
| `desktop/src/ipc/agent-state-poller.ts` | polls `<root>/.cockpit/agent-state.json` on local disk; designed expressly to avoid a live connection per workspace |
| `desktop/src/ipc/fleet-health.ts:150` | reads `<root>/.cockpit/url` |
| `desktop/src/ipc/fleet-health.ts:346` | spawns `python -m project_os_cockpit.fleet_validate` with the **local** interpreter |
| `desktop/src/ipc/git.ts:39` | `git -C <root>` — backs the git panel, commits, contribution grid |
| `desktop/src/ipc/agent-instrument.ts` | generates a ZDOTDIR into local `userData` and injects it into the PTY env |

## Definition of Done

- [ ] Each surface above either reads the remote host through the selected transport, or reports *cannot reach* in a form the UI renders distinctly from *nothing to report*.
- [ ] Agent state for a remote workspace reaches the rail without one held-open SSH connection per remote workspace, or with a stated reason why that cost is accepted.
- [ ] Remote validator health runs `fleet_validate` **on the remote host** ([[TASK-0411]]), and its absence is reported rather than counted as clean.
- [ ] Agent instrumentation either works on a remote shell — including what it writes to the remote host, which the feature's out-of-scope list must then acknowledge — or is explicitly unavailable there, with the session-insight surfaces saying so.
- [ ] No fleet roll-up action that publishes (push) is offered for a remote workspace ([[FEAT-0099]] out of scope).

## Steps

- [ ] Inventory every renderer surface that consumes these five sources and define the *unreachable* presentation once, centrally.
- [ ] Implement remote reads for agent state, git, and validator health over the selected channel.
- [ ] Decide instrumentation's remote story with its file-writing consequence stated.
- [ ] Add tests that assert an unreachable remote workspace never renders as clean/idle/zero.
