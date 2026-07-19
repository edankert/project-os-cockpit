---
type: "[[feature]]"
id: FEAT-0010
aliases: ["FEAT-0010"]
title: "Native nav surface — workspace rail (with agent-state dots) + in-workspace nav + right pane"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Replace the current single-purpose workspace switcher + temporary Browse panel with the IDE-standard two-level nav: narrow workspace rail with per-workspace agent-state indicators, plus a primary in-workspace nav (Features / Tasks / Issues / Library / Recent) and a right context pane. Same data sources mode 1 uses (/api/cockpit/{nav,context}), plus the new agent-state signal from FEAT-0013."
related: ["[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0009-Native-Shell-Layout]]", "[[FEAT-0013-Agent-State-Signal]]", "[[FEAT-0006-Cockpit-Layout]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: []
release: ""
tests: []
---

# Native nav surface

## Goal

Two levels of navigation, both first-class:

1. **Workspace rail** (~52 px, far left). One icon-row per discovered
   workspace. Each row carries a status dot driven by the agent-state
   signal (FEAT-0013), so the user can tell at a glance which
   workspace's agent is busy, waiting for input, idle, or errored —
   without leaving the workspace they're currently in.
2. **In-workspace nav** (~240 px, beside the rail). The full mode-1
   left-pane experience: Features-by-phase, Tasks, Issues, Library
   (curated + Recent + Changes), with status palettes, pinning,
   requirement nesting, hybrid Changes buckets, type-aware icons,
   platform filter, focus highlighting, SSE soft-reload.

Plus the right pane: outbound + inbound-only + frontmatter card
(already exists in mode 1; lift to native via `/api/cockpit/context`).

The temporary "Browse this workspace" panel from FEAT-0011 goes away
when this lands.

## Layout

```
┌────┬──────────┬────────────────────────────┬──────────────┐
│ rail│ in-ws nav│  centre (doc-view, FEAT-0011) │  right pane │
│     │          │                              │              │
│ • A │ Features │                              │  outbound    │
│ ● B │  by phase│                              │  inbound     │
│ ◐ C │ Tasks    │                              │  frontmatter │
│ • D │ Issues   │                              │              │
│     │ Library  │                              │              │
│     │ Recent   │                              │              │
│     │          │                              │              │
│     │          ├──────────────────────────────┤              │
│     │          │  terminal panel (FEAT-0007)  │              │
└─────┴──────────┴──────────────────────────────┴──────────────┘
```

Workspace rail status glyphs:
- ● green: `busy`
- ◐ amber (pulsing): `waiting-for-input`
- ◌ grey: `idle` / no recent signal
- ● red: `error`
- (the currently-active workspace gets a left-edge accent + filled bg)

## Scope

### In scope

**Workspace rail:**
- Replaces the existing `.switcher` left pane. Same workspace data
  (discovered via FEAT-0007). Narrower, icon-first.
- For each workspace whose sidecar is currently spawned, subscribes
  to its `cockpit:agent-state` SSE (FEAT-0013) and paints the dot.
- Workspaces whose sidecar isn't running show no dot. (Future:
  spawn-on-demand polling, but explicit is fine for v1.)
- Hover = tooltip with full workspace name + last state message.
- Click = switch active workspace (existing flow).

**In-workspace nav** (the original FEAT-0010 scope, preserved):
- Modes via `/api/cockpit/nav?mode=`: `features` (by phase) /
  `tasks` / `issues` / `library` / `recent`.
- Status palettes; type-aware group icons; status chips.
- Pinning for library; platform filter (auto-discovered).
- Requirement nesting under features (collapsed by default).
- Hybrid Changes buckets (current week / last week / earlier this
  month / past months with weekly sub-buckets for dense months).
- Focus highlighting: when `cockpit:focus` SSE fires, scroll the
  matching nav row into view + accent it.
- SSE soft-reload: `file-changed` events trigger debounced
  re-fetch of the active mode.
- Tab-state heartbeat: POST `/api/cockpit/tab-state` every 15 s with
  a renderer-local `tab_id`.

**Right pane:**
- `/api/cockpit/context?this=<rel>` driven.
- Outbound (`linked`) + inbound-only (`backlinks`) sections.
- Frontmatter card (already comes pre-rendered from
  `/api/render.metadata_html` for the active note; the right pane
  shows context, not duplicate metadata, so this section just
  surfaces the linked + backlinked groups).
- Active note severity / status chip in the header.

### Out of scope

- Multi-window — handled in FEAT-0012.
- Cmd+P quick-switch — FEAT-0012.
- The OS notification when state flips to `waiting` — design lives in
  FEAT-0012 (UX wins); the data pipe lives in FEAT-0013. This feature
  surfaces the dot only.
- Drag-to-reorder workspaces in the rail. Pinning maybe; reorder no.
- Inline note editing.
- Title bar / breadcrumb chrome — FEAT-0009.

## Acceptance

- Pick a workspace from the rail → its in-workspace nav appears in the
  second column; centre pane mounts README (or last visited).
- In another terminal: `cd <other-workspace>/docs && cockpit signal
  busy --message "refactoring"` (assuming FEAT-0013 has shipped). The
  rail dot for that workspace goes green within ~1 s (SSE).
- `cockpit signal waiting` → the dot turns amber and pulses; hovering
  shows the message.
- Click a feature in the in-workspace nav → centre pane navigates
  (existing FEAT-0011 path); the feature's row highlights as active.
- Edit a `.md` in an editor → the in-workspace nav re-fetches and any
  changed feature's row reflects new status; centre pane re-renders
  if the active note changed.
- Open the same workspace in a second window (FEAT-0012, later) →
  both windows' rails show the same dots.

## Sequencing — dependency on FEAT-0013

FEAT-0013 must land before the rail's status indicators are wired up;
the rest of the rail (workspace list, click-to-switch, active accent)
can ship without it. So either:

1. Ship FEAT-0013 first, then FEAT-0010 in one piece.
2. Ship FEAT-0010 in two passes — workspace rail without dots + full
   in-workspace nav + right pane, then layer the dots on once
   FEAT-0013 is ready.

Recommend **(1)** — small feature, fast to ship, and FEAT-0010's PLAN
references FEAT-0013 endpoints directly. Less rework.

## Open questions

- Workspace icon: letter (first char of `project.name`) or full short
  label that fits? Letter is cleanest at 52 px; tooltip handles
  disambiguation. **Land-time decision.**
- Should the rail also show a separator under "open in another window"
  workspaces (FEAT-0012 multi-window) vs "discovered but not spawned"?
  Probably yes — different visual weight. **FEAT-0012 territory.**
- Rail position when collapsed: hide entirely, or show as a thin strip
  with no labels? **Land-time decision.**
- Per-workspace agent label (claude / codex / aider) — show alongside
  the dot or in tooltip only? Tooltip for v1.

## Links

- Consumes [[FEAT-0008-Cockpit-API-Hardening]] (frozen JSON contract).
- Consumes [[FEAT-0013-Agent-State-Signal]] (dot data source).
- Companion centre pane: [[FEAT-0011-Native-Center-Pane]] (done).
- Mode-1 nav this mirrors: [[FEAT-0006-Cockpit-Layout]].
- Hosting shell: [[FEAT-0007-Desktop-Shell]].
- Phase: [[PHASE-006-Native-Cockpit-UI]].
