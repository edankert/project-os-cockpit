---
type: "[[reference]]"
id: REF-COCKPIT-API
aliases: ["COCKPIT-API"]
title: "Cockpit HTTP API contract"
status: draft
owner: user:edwin
created: 2026-05-25
updated: 2026-07-17
related: ["[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0011-Native-Center-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]", "[[FEAT-0018-Verification-Health-Surface]]"]
---

# Cockpit HTTP API contract

The HTTP surface the Python cockpit sidecar exposes to its clients:

- The mode-1 browser cockpit JS (`src/project_os_cockpit/static/cockpit.js`).
- The mode-3 desktop renderer (`desktop/src/`).
- The in-terminal `cockpit` CLI (`src/project_os_cockpit/cli.py`).
- External agents that walk up to `.cockpit/url` and POST focus.

This document is the **contract**. Behaviour and shape changes here
are tracked via `cockpit.SCHEMA_VERSION` and matching CI gates
(TST-* notes per endpoint).

---

## Schema versioning

`cockpit.SCHEMA_VERSION` (in `src/project_os_cockpit/cockpit.py`) is
the integer the server stamps on every JSON response, in two places:

1. The `X-Cockpit-Schema` HTTP header (every JSON response, GET and POST).
2. The `schema_version` field inside the JSON body (where present —
   `nav_payload`, `context_payload`, and the new `/api/render`).

### When to bump it

| Change | Bump? |
|---|---|
| Add a new field to a response | No (additive — clients ignore unknown fields). |
| Add a new endpoint | No. |
| Remove a field, rename a field, change a field's type, change semantics of a status code | Yes. |
| Add a new SSE event type | No (additive — clients subscribe by name and ignore unknown events). |
| Remove or rename an SSE event, or change an existing event's data shape | Yes. |
| Tighten / relax path validation in a request shape | Yes (changes accept set). |

Bumping is one line:
`SCHEMA_VERSION: int = N` in `cockpit.py`. The TASK-0068 header
assertion test then fails for every endpoint until both ends agree;
fix by updating client cached-schema constants and the contract doc
in this file.

Current value: **3** (bumped when `cockpit:agent-state` was added in
FEAT-0013, before the add-vs-remove distinction above was codified).
Event *additions* since then have been additive at schema 3:
`cockpit:agent-activity` (FEAT-0019), `cockpit:dispatch-request`
(FEAT-0025), `cockpit:validation` (FEAT-0018).

---

## JSON endpoints

All JSON responses set `Content-Type: application/json; charset=utf-8`,
`X-Cockpit-Schema: <int>`, `Content-Length: <bytes>`,
`Cache-Control: no-cache`.

### `GET /healthz`
Liveness + identity probe used by the Electron shell's sidecar
lifecycle (`desktop/src/ipc/sidecar.ts`) to confirm "this is a
project-os-cockpit, not some random thing on this port" before
loading the URL.

**Response 200**
```json
{
  "ok": true,
  "service": "project-os-cockpit",
  "schema": 2,
  "docs_root": "/abs/path/to/docs",
  "desktop_mode": false
}
```

`desktop_mode` is `true` when `COCKPIT_DESKTOP=1` is in the sidecar's
environment. Used by the desktop shell to assert the sidecar was
spawned for desktop use.

**Consumers**: `desktop/src/ipc/sidecar.ts`.

---

### `GET /api/cockpit/nav`
Left-pane navigation payload. Shape varies by mode.

**Query parameters**
| Name | Type | Default | Meaning |
|---|---|---|---|
| `mode` | `features` \| `tasks` \| `issues` \| `recent` \| `library` | `features` | Which left-pane grouping to compute. |
| `platform` | string | unset → `"all"` | Filters items to a single `platform` frontmatter value. |
| `pinned` | comma-separated string | empty | IDs explicitly pinned by the user (library mode). |

**Response 200**
```json
{
  "schema_version": 2,
  "mode": "features",
  "platform": "all",
  "available_platforms": ["all", "ios", "web"],
  "groups": [
    {"label": "Phase 2 — Project-os adapter", "items": [...]},
    ...
  ]
}
```

`groups[].items` shape varies by mode. Each item carries at minimum
`{id, title, url, status}`; tasks/issues/features carry richer
type-specific fields.

**Consumers**: mode-1 `cockpit.js`, mode-3 `FEAT-0010` (planned).

---

### `GET /api/cockpit/context`
Right-pane context for an active note: outbound (`linked`) +
inbound-only (`backlinks`) + active metadata.

**Query parameters**
| Name | Type | Default | Meaning |
|---|---|---|---|
| `this` | string | unset → null `active` | Note ID/alias or docs-rel path. |
| `platform` | string | `"all"` | Same semantics as `nav`. |

**Response 200**
```json
{
  "schema_version": 2,
  "platform": "all",
  "active": {
    "id": "FEAT-0006",
    "title": "3-pane cockpit layout (code-driven)",
    "url": "/docs/features/cockpit/FEAT-0006-Cockpit-Layout.md"
  },
  "linked": [
    {"label": "Tasks", "items": [...]},
    ...
  ],
  "backlinks": [
    {"label": "Changes", "items": [...]},
    ...
  ]
}
```

`active` is `null` when `this` is missing / unresolvable. `linked` /
`backlinks` are always arrays (possibly empty).

**Consumers**: mode-1 `cockpit.js`, mode-3 `FEAT-0010` (planned).

---

### `GET /api/cockpit/state`
Bi-directional awareness snapshot (TASK-0053). Read by the `cockpit
state` / `cockpit history` CLI subcommands.

**Response 200**
```json
{
  "agent_focus": {
    "target": "FEAT-0006",
    "url": "/docs/features/cockpit/FEAT-0006-Cockpit-Layout.md",
    "ts": "2026-05-25T11:00:00.000+00:00"
  },
  "agent_state": {
    "state": "waiting",
    "target": "FEAT-0013",
    "agent": "claude",
    "message": "review my PR",
    "ts": "2026-05-25T17:30:00.000+00:00"
  },
  "user_view": {
    "url": "/docs/...",
    "ts": "2026-05-25T11:01:00.000+00:00"
  },
  "tabs": [
    {"tab_id": "...", "url": "...", "following": true, "last_seen": "..."}
  ],
  "history": [
    {"source": "agent-state", "state": "waiting", "ts": "...", "message": "..."},
    {"source": "agent", "url": "...", "ts": "...", "target": "..."},
    {"source": "user",  "url": "...", "ts": "...", "tab_id": "..."}
  ]
}
```

`agent_focus`, `agent_state`, and `user_view` are `null` when no
focus / no signal / no live tabs respectively. `tabs` excludes
entries whose `last_seen` is older than `_TAB_STALE_SECONDS`
(45 s). `agent_state` may surface a `decayed_from` field — see
the `POST /api/cockpit/agent-state` section below.

**Consumers**: `cockpit` CLI (`state` / `history`), mode-3
desktop renderer (planned, FEAT-0010).

---

### `GET /api/cockpit/validation` *(new in FEAT-0018)*
Docs-validator health report (TASK-0111). The server runs the
browsed repo's `tools/scripts/validate-docs.py` (fallback: the
bundled copy shipped inside the package) as a subprocess, caches
the parsed report, and re-runs it — debounced ~1 s — on watcher
events under `docs/` or on `SNAPSHOT.yaml` edits. The first
request after startup runs the validator synchronously.

**Response 200**
```json
{
  "schema_version": 3,
  "ok": false,
  "state": "failing",
  "errors": [
    {
      "code": "ITEM-STATUS",
      "message": "FEAT-0001 status drift: snapshot=backlog note=done (docs/features/x/FEAT-0001-X.md)",
      "id": "FEAT-0001",
      "rel": "docs/features/x/FEAT-0001-X.md",
      "url": "/docs/features/x/FEAT-0001-X.md"
    }
  ],
  "warnings": [
    {"code": "PATH-ALIAS", "message": "...", "id": null, "rel": null}
  ],
  "checked_at": "2026-07-17T21:13:10.178+00:00"
}
```

`state` is `ok` (exit 0), `failing` (exit 1), or `unavailable`
(exit 2 — e.g. no SNAPSHOT.yaml — or no locatable validator; a
`detail` string explains why). `ok` is `true` only for `state:
"ok"`. Per-entry `id` / `rel` are `null` when the message carries
neither; `url` is the resolver deep link when one resolves (errors
only). Always `200`; unavailability is data, not an HTTP error.

State changes (ok↔failing↔unavailable, or an error-set delta)
are announced via the `cockpit:validation` SSE event — clients
should listen rather than poll.

**Consumers**: mode-1 `cockpit.js` health badge + drift panel
(TASK-0112).

---

### `POST /api/cockpit/focus`
Agent-driven cockpit navigation. Broadcasts a `cockpit:focus` SSE
event to every connected tab; tabs in "follow agent" mode
navigate.

**Request body** (JSON)
```json
{"target": "FEAT-0006"}
```
`target` accepts: a note ID, a docs-rel path, a top-level project
file (`README.md` etc.), or a full cockpit URL (`/docs/...`).

**Response 200**
```json
{"ok": true, "url": "/docs/features/cockpit/FEAT-0006-Cockpit-Layout.md"}
```

**Response 400** — missing `target`. **Response 404** — target
unresolvable.

**Consumers**: `cockpit focus` CLI; external agents.

---

### `POST /api/cockpit/agent-state` *(new in FEAT-0013)*
Agent declares its current state — `busy`, `waiting` (for input),
`done`, `error`, or `idle`. The cockpit fans this out as a
`cockpit:agent-state` SSE event so connected clients (the desktop
shell's workspace rail in FEAT-0010, future browser surfaces, OS
notifications in FEAT-0012) update without polling.

**Request body** (JSON)
```json
{
  "state":   "waiting",
  "target":  "FEAT-0013",
  "agent":   "claude",
  "message": "review my PR"
}
```

| Field | Required | Type | Notes |
|---|---|---|---|
| `state` | yes | string | One of `busy` / `waiting` / `done` / `error` / `idle`. Anything else → 400. Case-insensitive. |
| `target` | no | string | Note ID / docs-rel path the agent is working on or blocked by. |
| `agent` | no | string | Agent name — `claude`, `codex`, `aider`, … (freeform). |
| `message` | no | string | Short human-readable reason (most useful with `waiting` and `error`). |

**Response 200**: `{"ok": true}`. **Response 400** — missing /
unknown `state`, or malformed JSON.

**Auto-decay.** Stored `busy` / `waiting` states age out to `idle`
after `COCKPIT_AGENT_STATE_DECAY_SECONDS` (default 600). The
cockpit's background timer publishes one synthetic
`cockpit:agent-state` SSE event when the flip happens so subscribers
update without polling. Explicit terminal states (`done`, `error`)
do **not** decay. The snapshot's `agent_state` includes
`decayed_from: "<prior state>"` when the value has been lazily
flipped on read.

**Consumers**: workspace rail (FEAT-0010), OS notifications
(FEAT-0012), `cockpit state` CLI, anything subscribed to
`/_events`.

---

### `POST /api/notes/check-toggle` *(new in FEAT-0011)*
Toggle a task-list checkbox in a source `.md` file. Used by the
native renderer (FEAT-0011 / TASK-0074) to write back interactive
checkbox clicks.

**Request body** (JSON)
```json
{"path": "features/sample.md", "index": 2, "checked": true}
```
- `path` — docs-root-relative path (a leading `docs/` is tolerated).
- `index` — zero-based ordinal of the checkbox within the rendered
  HTML; the server walks the source in pymdownx.tasklist order.
- `checked` — desired state (`true` → `- [x]`, `false` → `- [ ]`).

**Response 200**: `{"ok": true}`. Concurrent toggles on the same
file are serialised via a per-file `threading.Lock`. The watcher
emits a `file-changed` SSE after each successful write so clients
stay in sync.

**Response 400** — missing `path` / `index` / `checked`, or
non-int `index`. **Response 403** — path traversal. **Response
404** — file missing, not a `.md`, or `index` out of range.

**Consumers**: mode-3 native centre pane (FEAT-0011). Mode-1
cockpit JS currently renders checkboxes as `disabled`; if mode-1
ever lifts that, it can reuse this endpoint.

---

### `POST /api/cockpit/tab-state`
Per-tab heartbeat (TASK-0053 / TASK-0055). Each open cockpit tab
POSTs every 15 s and after each in-tab navigation.

**Request body** (JSON)
```json
{"tab_id": "<uuid>", "url": "/docs/...", "following": true}
```

**Response 200**: `{"ok": true}`. **Response 400** — missing
`tab_id` or `url`.

**Consumers**: mode-1 `cockpit.js`. (Mode-3 will plug into this in
FEAT-0010.)

---

### `GET /api/render?path=<rel-path>` *(new in FEAT-0008)*
Rendered Markdown HTML fragment + metadata, for the native centre
pane in FEAT-0011. **Lands in TASK-0067.**

**Query parameters**
| Name | Type | Required | Meaning |
|---|---|---|---|
| `path` | string | yes | Docs-root-relative path (`features/cockpit/FEAT-0006-…md`). A leading `docs/` is tolerated. |

**Response 200**
```json
{
  "schema_version": 2,
  "rel_path": "features/cockpit/FEAT-0006-Cockpit-Layout.md",
  "title": "3-pane cockpit layout (code-driven)",
  "frontmatter": {"type": "[[feature]]", "id": "FEAT-0006", ...},
  "metadata_html": "<details class=\"metadata-strip\" open>...<a href=\"/docs/...\">FEAT-0007</a>...</details>",
  "html": "<h2>Goal</h2><p>...</p>...",
  "linked": [...],
  "backlinks": [...]
}
```

`metadata_html` carries the **pre-resolved** metadata strip — the same
HTML mode 1 emits via `templates._metadata_strip_html(frontmatter,
resolver)`. Wikilinks (`[[X]]`) and bare project-os IDs in
frontmatter values both become `<a>` tags; the status field renders
as a `.status-chip`. The desktop renderer mounts this HTML directly;
its `#doc-view` click handler intercepts the resulting anchors via
the same path as body links.

`linked` / `backlinks` mirror the `/api/cockpit/context` shape so the
renderer can fill the right pane in the same fetch.

**Response 400** — missing `path`. **Response 403** — path
traversal. **Response 404** — not a `.md` under docs root.

**Consumers**: mode-3 `FEAT-0011-Native-Center-Pane` (planned).

---

### `GET /api/terminal`
Embedded-terminal probe used by the mode-1 cockpit JS to decide
whether to render the bottom-panel iframe. In **desktop mode**
(`COCKPIT_DESKTOP=1`) always returns `enabled: false` — the
Electron shell mounts a native node-pty pane instead.

**Response 200**
```json
{"enabled": true, "url": "/_terminal/", "command": ["/bin/zsh"]}
```
or
```json
{"enabled": false, "reason": "<human-readable reason>"}
```

**Consumers**: mode-1 `cockpit.js` only. Mode-3 never calls this.

---

## SSE channel

### `GET /_events`
Long-lived `text/event-stream`. Heartbeat (`: heartbeat\n\n`) every
15 s. On connect, emits `: connected\n\n` (a comment, not a real
event). Real events:

| Event | Data shape | Source | Triggers |
|---|---|---|---|
| `file-changed` | plain text — the docs-root-relative path | Filesystem watcher | Any `.md` file in `docs/` touched. |
| `cockpit:focus` | JSON: `{"url": "...", "target": "..."}` | `POST /api/cockpit/focus` | Agent-driven nav. |
| `cockpit:agent-state` | JSON: `{state, ts, target?, agent?, message?, decayed_from?}` | `POST /api/cockpit/agent-state` or the decay timer | Agent declares state, or stored busy/waiting ages out. |
| `cockpit:validation` | JSON: the full `GET /api/cockpit/validation` payload | Debounced validator re-run (docs / SNAPSHOT.yaml watcher) | Validation state flips ok↔failing↔unavailable or the error set changes (FEAT-0018). |

New event types are additive (clients subscribe by name via
`EventSource.addEventListener` and never see unknown events);
removing or renaming an event, or changing an existing event's
data shape, is breaking and bumps the schema — see the
versioning table above.

**Consumers**: mode-1 `cockpit.js`, mode-3 `desktop/src/ipc/agent-focus.ts`
(filters `cockpit:focus`), mode-3 `FEAT-0010` (planned soft-reload via
`file-changed`).

---

## Discovery (mode 1 only)

### `.cockpit/url` file
On startup, mode 1 writes the cockpit's base URL to
`<project-root>/.cockpit/url`. The `cockpit` CLI walks up from CWD
to find it. **Suppressed in mode 3** — the Electron shell drives
focus over IPC, not via this file. Documented under TASK-0059 /
TST-0004.

---

## HTML routes (mode 1 only)

These exist for the browser cockpit and are **not** part of the
mode-3 contract. The Python tool keeps emitting them; the desktop
renderer never loads them after FEAT-0011 lands.

- `GET /` — landing page (`templates.home_page_html`).
- `GET /docs/<rel-path>` — rendered Markdown page (with cockpit shell).
- `GET /index/<plural>` — auto-index page (features, tasks, ...).
- `GET /<top-level-support-path>` — `README.md` / `ROADMAP.md` /
  `SECURITY.md`.
- `GET /_static/<file>` — packaged CSS / JS / assets.
- `GET /_terminal/*` — reverse-proxied ttyd (mode 1 only; 503 in
  desktop mode).

---

## Path traversal

Every path-bearing endpoint (`/docs/*`, `/api/render`, `_static/`,
top-level support files) rejects requests whose decoded path
contains `..` segments, and rejects requests whose resolved path
escapes the configured docs / project root. Returns `403` with an
HTML error body for mode-1 routes; JSON `{ok: false, error: ...}`
for `/api/render`.

---

## Pipelining + keep-alive

The server runs HTTP/1.1 with keep-alive. **Important:** any
unknown POST drains its body before responding (TASK-0057 / TST-0003)
to keep pipelined requests intact. Clients can therefore reuse a
single TCP connection across the entire cockpit interaction.
