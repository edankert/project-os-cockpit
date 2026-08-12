---
type: "[[architecture]]"
id: ARCH
owner: user:edwin
created: 2026-05-07
updated: 2026-08-12
tags: [architecture]
---

# Architecture

## High level

Two processes and a fleet. The Python **sidecar** reads one repo's `docs/` and answers questions about it; the Electron **shell** hosts one sidecar per repo and supplies everything a browser cannot — the terminal, git, the workspace rail, the agent instrumentation.

```
   ┌─ Electron shell (mode 3, Mac-local) ───────────────────────────────────┐
   │                                                                        │
   │  main.ts ──┬── ipc/workspaces  discovery: every SNAPSHOT.yaml under    │
   │            │                   ~/Dev/repos (10 today), one per repo    │
   │            ├── ipc/sidecar     spawn + supervise, one per workspace    │
   │            ├── ipc/terminal    xterm.js over a PTY (127.0.0.1 only)    │
   │            ├── ipc/git         status, ahead-count, push (deploy       │
   │            │                   remotes refused)                        │
   │            ├── ipc/agent-*     live sessions, focus, dispatch queue    │
   │            └── ipc/fleet-health validator verdict per repo             │
   │                                                                        │
   │  renderer.ts — the three panes, every view, ~15k lines                 │
   └───────────┬────────────────────────────────────────────────────────────┘
               │ HTTP, 127.0.0.1:876N — one sidecar per workspace
   ┌───────────▼─── project_os_cockpit (Python, 40 modules) ────────────────┐
   │                                                                        │
   │  server.py     ThreadingHTTPServer · 63 API routes · SSE               │
   │  index.py      the note index: ids, aliases, types, links              │
   │  renderer.py   markdown → HTML (wikilinks, callouts, checkbox source)  │
   │  cockpit.py    the payloads every view reads                           │
   │  note_writes.py  the ONLY write path — loopback-guarded                │
   │  statuses.py   the status vocabulary, single source                    │
   │  obligations.py  what is owed, of what kind, to which view             │
   │  agent_hooks.py  live agent sessions from Claude Code hooks            │
   └───────────┬────────────────────────────────────────────────────────────┘
               │ 0.0.0.0:876N — READ ONLY
        Tablet / phone on the LAN (mode 1, the browser front door)
```

**Two front doors, one sidecar.** Mode 1 is the render server's own HTML, bound `0.0.0.0` so a tablet can read. Mode 3 is the shell. What each may do is [[ADR-0010]]'s subject: parity is the goal and an authenticated write path ([[REQ-0034]]) is its precondition. Until then **every write is loopback-only** ([[REQ-0027]]).

## Components

### Sidecar — `src/project_os_cockpit/`, 40 modules

| module | what it owns |
|---|---|
| `server.py` | routing, SSE, and the loopback guard on every mutation |
| `index.py` | the in-memory note index — ids, aliases, types, link graph, rebuilt on change |
| `renderer.py` | markdown → HTML: wikilinks, cross-repo links, callouts, image embeds, checkbox source annotation |
| `cockpit.py` | the payload layer — nav, overview, context, landings, digests |
| `note_writes.py` | **the only path that edits a note**: transitions, ticks, verdicts, test runs, creation |
| `statuses.py` | the status vocabulary and its palette bands — one source, six consuming surfaces |
| `obligations.py` | the registry: what is owed, of what kind, and which view owns it |
| `acceptance.py` | the tier suite and the release gate |
| `agent_hooks.py` | live sessions, ingested from Claude Code hook payloads |
| `standing.py` | the manifest behind *"what this project is"* |
| `decisions.py`, `criteria.py` | a decision's options; a note's acceptance criteria |
| `validate_docs_bundled.py` | a verbatim copy of the validator, so a repo without one still gets a verdict |

### Shell — `desktop/src/`, 13 IPC modules

The renderer is one 15k-line module by design: it is loaded as a plain script alongside six others that publish globals, and the boundary that matters is the **bridge** (`preload.ts`), not file count. Everything privileged lives behind it.

### The write path

One function per verb in `note_writes.py`, each: resolve the note by id → check the caller is loopback → check an mtime precondition → edit **only** the frontmatter field or checkbox line in question → write. A route that touches `docs/` without `_require_loopback` fails the suite **by existing** — the guard is enumerated from the dispatch table rather than listed by hand ([[RISK-0005]]).

## Routes

63 API routes under seven prefixes — `/api/cockpit/*` (views and state), `/api/notes/*` (reads and the guarded writes), `/api/design/*`, `/api/inbox/*`, `/api/render/*`, `/api/terminal/*`, `/api/agent-hook`. Plus `GET /` and `GET /docs/...` for mode 1, `/static/...`, and `GET /_events` for the SSE channel.

*The route list that used to sit here named five routes and one of them (`/events`) was already wrong. It is not restated: `server.py`'s dispatch is the list, and a copy of it here would be stale within a week — which is what happened.*

## Project-os ID resolution

The `[[wikilink]]` resolver does two passes:

1. **Direct title match** against the file-title index.
2. **ID match** — `^(TASK|FEAT|REQ|ISS|RISK|REL|ADR|TST|CHG|WF|PHASE|DES)-[0-9A-Za-z-]+` against the id index.

Frontmatter `aliases` are indexed too, so `[[FEAT-0008]]` and a custom alias both resolve.

**Cross-repo:** `[[project-os-dev#ADR-0011]]` resolves to another *project* ([[ADR-0024]]). The sidecar cannot see another repo, so it emits the two parts as data and the shell — which holds the fleet — does the lookup and switches workspace.

## Deployment shape

- **From a terminal:** `python -m project_os_cockpit <repo>/docs` against any project-os repo.
- **From the shell:** it discovers every `SNAPSHOT.yaml`-bearing repo under the configured roots and spawns a sidecar per workspace, on its own port, loopback-bound.

**Nothing is installed into a downstream repo.** An earlier plan ([[PHASE-003]] / [[FEAT-0005]]) had each consumer carry a shim under `tools/project-os-cockpit/`; **that directory never existed in any repo**, and workspace discovery ([[PHASE-005]]) replaced the need before it was built.

## Scale, for calibration

~39k lines of source, 69 test modules, 1235 tests. Ten workspaces discovered on this machine.
