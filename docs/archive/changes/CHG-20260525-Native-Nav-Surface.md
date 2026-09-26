---
type: "[[change]]"
id: CHG-20260525-Native-Nav-Surface
aliases: ["CHG-20260525-Native-Nav-Surface"]
title: "Native nav surface: activity-bar rail with agent-state dots + in-workspace nav (5 modes) + right pane + SSE soft-reload"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0080]]", "[[TASK-0081]]", "[[TASK-0082]]", "[[TASK-0083]]", "[[TASK-0084]]", "[[TASK-0085]]", "[[TASK-0086]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/renderer/index.html (rail + ws-nav + right-pane DOM)"
  - "desktop/src/renderer/renderer.css (grid restructure, rail/dot/nav/right-pane styles, dead-CSS cleanup)"
  - "desktop/src/renderer/renderer.ts (rail render, ws-nav module, mode toggle, right pane, SSE soft-reload, tab heartbeat, browse-panel removal)"
  - "desktop/src/main.ts (agent-state poller wired up)"
  - "desktop/src/ipc/agent-state-poller.ts (new — fs polling + IPC fan-out)"
  - "desktop/src/ipc/workspaces.ts (getAllWorkspaces export)"
  - "desktop/src/preload.ts (workspaces.onAgentState exposed)"
  - "src/project_os_cockpit/server.py (CockpitState state_path, _persist_agent_state, _seed_agent_state_from_file)"
  - "tests/test_cockpit_state.py (+4 file-persistence cases)"
issues: []
features: ["[[FEAT-0010-Native-Nav-Right-Pane]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[FEAT-0011-Native-Center-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Native nav surface

## Summary

Closes FEAT-0010. The desktop shell now has the full IDE-style
4-column layout:

```
[ rail ]  [ ws-nav ]  [ centre + terminal ]  [ right pane ]
   52px      240px         1fr                    280px
```

- **Workspace rail** with per-workspace **agent-state dots** —
  the visible payoff of FEAT-0013. Green = busy, pulsing amber =
  waiting, grey = idle, red = error. Driven by a 5-s file poller
  reading each workspace's `.cockpit/agent-state.json`. Works for
  workspaces whose cockpits are running anywhere (mode 1 in another
  terminal, mode 3 in another desktop window, etc.).
- **In-workspace nav** with five modes (Features / Tasks / Issues /
  Library / Recent) toggled via a pill row. Persisted selection.
  Active-note highlight; click row → centre nav.
- **Right pane** showing `linked` (outbound) + `backlinks` (inbound)
  groups for the active note. Collapsible via a chevron; state
  persisted.
- **SSE soft-reload** — file-changed events trigger debounced
  re-fetches of nav, right pane, and centre. Tab-state heartbeat
  every 15 s + on every navigation.
- **Temporary Browse panel deleted** along with the dead
  `.frontmatter-card` v1 styles. ~120 lines net removed alongside
  the new code.

Test count: **158 → 162** (+4 from agent-state file persistence
tests in TASK-0081).

## What landed (per task)

**TASK-0080** — Activity-bar layout shell. `.app` grid reshaped to
`52px 240px 1fr 280px` (with a collapsed variant
`52px 240px 1fr 28px`). Old `.switcher` removed; rescan + terminal
toggles became icon-only buttons in the rail.

**TASK-0081** — Server persists agent-state to
`<project-root>/.cockpit/agent-state.json` on every transition AND
on lazy/active decay. `CockpitState.__init__` seeds from the file if
present so a restart doesn't blink the dot off. Tolerates missing
/ malformed JSON silently.

**TASK-0082** — Workspace rail polling. New
`desktop/src/ipc/agent-state-poller.ts` reads each discovered
workspace's state file every 5 s and fans diffs to the renderer via
the `workspaces:agent-state` IPC. Renderer maintains an in-memory
`Map<workspaceId, AgentStatePayload>` and paints colored dots
(`state-busy` / `state-waiting` / etc.) on each pill. `waiting`
gets a CSS pulse animation.

**TASK-0083** — In-workspace nav framework. Native renderer fetches
`/api/cockpit/nav?mode=features` against the active sidecar; renders
collapsible phase groups, feature rows with status chips, nested
requirements under each feature. Click → centre `navigateTo`; the
clicked row gains `is-active`.

**TASK-0084** — Mode toggle pill row (Features / Tasks / Issues /
Library / Recent). Selection persisted to `localStorage`. The same
generic renderer handles all five modes — server returns
mode-specific group shapes that the framework reads uniformly.

**TASK-0085** — Right pane. Fetches `/api/cockpit/context?this=<rel>`
on every `navigateTo`, renders `linked` and `backlinks` groups.
Collapsible chevron toggle persists open / closed state via
`localStorage`. Item clicks navigate the centre.

**TASK-0086** — SSE soft-reload + heartbeat + cleanup. Renderer
opens an `EventSource` against the active sidecar's `/_events`; on
`file-changed`, debounces 150 ms then re-fetches nav, right pane,
and centre (history `{replace: true}` so the reload doesn't
pollute back/forward). Tab-state heartbeat: 15 s interval +
on-nav, posting `{tab_id, url, following}` to
`/api/cockpit/tab-state`. Tab ID persisted to `localStorage`. The
temporary "Browse this workspace" panel from FEAT-0011 + the
hand-built `.frontmatter-card` v1 CSS are deleted.

## Smoke-test reality-check

End-to-end demo (in two terminals):

```sh
# Terminal A — start a mode-1 cockpit somewhere (writes .cockpit/url
# so the CLI discovers it).
cd ~/Dev/repos/project-os-cockpit && python -m project_os_cockpit ./docs

# Terminal B
cockpit signal busy --target FEAT-0010 --agent claude
#   → desktop rail pill for project-os-cockpit gets a green dot
#     within ~5 s
cockpit signal waiting --message "review my PR"
#   → flips to pulsing amber
# Open project-os-cockpit in the desktop shell — Features nav appears
# in the second column, FEAT-0010 row highlights when the centre
# loads that doc, right pane shows its linked + backlinks.
```

## Documentation Coverage
- features: covered (FEAT-0010 → `done`)
- requirements: not-applicable
- tasks: TASK-0080..0086 → `done`
- issues: not-applicable
- tests: TST-0009 carries forward (+4 added file-persistence cases
  in `test_cockpit_state.py`, already covered by its scope)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (FEAT-0010 → done, TASK-0080..0086 → done,
  features_done 5 → 6, tasks_done 79 → 86, focus cleared, test
  count 158 → 162)
