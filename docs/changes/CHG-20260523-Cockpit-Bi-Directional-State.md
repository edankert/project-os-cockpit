---
type: "[[change]]"
id: CHG-20260523-Cockpit-Bi-Directional-State
aliases: ["CHG-20260523-Cockpit-Bi-Directional-State"]
title: "Cockpit: bi-directional awareness — agent can read what the user is looking at"
status: merged
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: ["[[TASK-0053]]", "[[TASK-0054]]", "[[TASK-0055]]", "[[TASK-0056]]", "[[TASK-0057]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/server.py"
  - "src/project_os_cockpit/cli.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "tests/test_cockpit_state.py"
  - "tools/instructions/COCKPIT.md"
  - "tools/instructions/LIFECYCLE.md"
  - "tools/skills/cockpit-driving/SKILL.md"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260509-Cockpit-LLM-Drives-Cockpit]]"]
---

# Cockpit: bi-directional awareness

## Summary
Closes the loop on agent ↔ cockpit interaction. Previously the agent could **drive** the cockpit (`cockpit focus <id>`); now the agent can **read** what the user is currently viewing (`cockpit state`, `cockpit history`). The cockpit JS pings the server on every navigation + every 15 s, so the snapshot reflects reality without polling pressure.

## Implementation

### Server (`server.py`)
- New `CockpitState` class: lock-guarded in-memory store of `{agent_focus, tabs, history}`. Tabs are pruned on every snapshot read when `last_seen` exceeds `_TAB_STALE_SECONDS` (45 s). History is a bounded deque (`_HISTORY_MAX` = 50), newest first, tagging each event with `source: "agent" | "user"`. Heartbeats with the same URL don't pollute history — only real nav events do.
- `_utc_now_iso()` bumped to millisecond precision so events within the same second order correctly.
- `DocsServer` instantiates one `CockpitState`; `_make_handler` accepts it and exposes it to routes via closure.
- New routes:
  - `GET /api/cockpit/state` — returns the snapshot (`agent_focus`, `user_view`, `tabs[]`, `history[]`).
  - `POST /api/cockpit/tab-state` — tab heartbeat `{tab_id, url, following}`; updates `tabs`, records into `history` only on URL change.
- `POST /api/cockpit/focus` now also records into `agent_focus` + `history` before publishing the SSE event.

### CLI (`cli.py`)
- New `_get_json(base, path)` helper mirroring `_post_json`.
- New subcommands:
  - `cockpit state [--json]` — compact human summary by default; raw JSON with `--json`.
  - `cockpit history [--limit N] [--json]` — recent nav events, default 10.
- Both subcommands use the existing discovery (`COCKPIT_URL` env → `.cockpit/url` walk-up).

### Cockpit JS (`cockpit.js`)
- Per-tab UUID stored in `sessionStorage` (`TAB_ID_KEY`); fresh per tab, persistent across reload.
- `postTabState()` POSTs `{tab_id, url, following}` to `/api/cockpit/tab-state` on:
  - boot, navigateTo success, follow-toggle change
  - 15 s heartbeat (`TAB_HEARTBEAT_MS`)
  - `pagehide` (best-effort, `keepalive: true`)
- All failures swallowed silently — the cockpit must keep working when the server is down.

### LLM directives
- `tools/instructions/COCKPIT.md` — new sections "`cockpit state` and `cockpit history`" + "Reading the user's view" (when to read, how to interpret divergence, respecting Following=OFF).
- `tools/skills/cockpit-driving/SKILL.md` — pattern reorganised into 4 numbered steps with new step 0 "Read state".
- `tools/instructions/LIFECYCLE.md` — preflight step 7 references the optional state-check.

### Tests
- `tests/test_cockpit_state.py` — 8 cases: initial empty snapshot, agent-focus recording, heartbeat-vs-nav history dedupe, user_view picks most-recent tab, stale-tab pruning, history bound, following round-trip, **plus the TASK-0057 regression** (pipelined POST→GET on one keep-alive socket).
- 76 passing / 1 skipped (was 68 / 1; +8).

## What this unlocks
The agent can now:
- Align with the user's context before starting work ("you're on FEAT-0006; I'll work on its TASK-0030").
- Re-orient after long-running steps without asking.
- Detect divergence ("you moved to ADR-0004 while I was working — should I pivot?").

Sets the stage for v2 extensions discussed in design: `cockpit ask` (interactive prompts), `cockpit comment` (status banners), `cockpit refine` (collaborative note refinement), `cockpit query` (read-only index lookup).

## Hotfix: TASK-0057 — HTTP/1.1 keep-alive desync on unknown POSTs

Shortly after rollout, the cockpit pages went **completely unstyled** for any tab still connected to a pre-restart server. Root cause: the cockpit's new JS heartbeats POST `/api/cockpit/tab-state` every 15 s. On a server that didn't yet know that route, the 404 path returned without reading the request body. The undrained body bytes desynced the HTTP/1.1 keep-alive socket — the next request on the same TCP connection got a request line prefixed by `{"tab_id":…}` and the server rejected it as `501 Unsupported method`. Innocent follow-up `GET`s for `cockpit.css`, `cockpit.js`, `favicon.ico` all failed → unstyled page.

Fix in `server.py::_route_post`: added `_drain_request_body()` and call it before the unknown-route `NOT_FOUND` response. Regression test (`TST-0003`) pipelines a bad `POST` + a `GET /_static/cockpit.css` on one keep-alive socket; previously the second response came back `501`, now it's `200 OK` with the CSS.

General lesson for stdlib `http.server`: any POST handler that early-returns without reading `Content-Length` desyncs the connection. Worth keeping in mind for future endpoints.

## Action required
Restart any cockpit server already running for this repo to pick up the new endpoints (the 8771 instance, in particular). After restart, hard-refresh the browser tabs so the new JS loads and starts heartbeating.

## Documentation Coverage (All Types Considered)
- features: covered (FEAT-0006 still in-progress)
- requirements: not-applicable
- tasks: new (TASK-0053..0057); back-filled TASK-0048..0052 to the snapshot
- issues: not-applicable
- tests: new (`tests/test_cockpit_state.py` — including TST-0003 regression)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 47→57, TST 2→3, focus.task → TASK-0057)
