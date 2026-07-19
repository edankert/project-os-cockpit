---
type: "[[task]]"
id: TASK-0083
aliases: ["TASK-0083"]
title: "In-workspace nav framework + Features-by-phase mode"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0010"
effort: ""
due: ""
depends: ["[[TASK-0080]]"]
blocks: ["[[TASK-0084]]"]
related: []
tests: []
---

# In-workspace nav framework + Features mode

## Definition of Done
- [ ] `#ws-nav` fetches `/api/cockpit/nav?mode=features` against
      the active sidecar after `sidecar:event` 'ready'.
- [ ] Renders the response's `groups[]` as collapsible phase
      headers, each containing feature rows.
- [ ] Each feature row carries:
      - ID (small mono, dimmed)
      - Title
      - Status chip (using cockpit.css `.status-chip` class —
        already styled via the base.css copy).
      - Type icon (book / chip / etc. — reuse mode-1 inline SVGs
        copied from `static/cockpit.js`).
- [ ] Click row → centre pane `navigateTo(rel)` (existing
      FEAT-0011 helper).
- [ ] Active note's row gets a left-edge accent + filled bg
      (mirrors cockpit-focus highlighting from mode 1).
- [ ] Requirements nest under their parent feature, collapsed by
      default (TASK-0030 behaviour).
- [ ] Browse panel from FEAT-0011's README mount is now redundant
      for non-README pages — removal happens in TASK-0086.

## Steps
- [ ] `desktop/src/renderer/ws-nav.ts` (new) — owns the nav fetch
      + render. Exports `mountNav(container, sidecarUrl)` and an
      `onNavigateRequest(cb)` hook.
- [ ] Call from `renderer.ts` on `sidecar:event` 'ready'.
- [ ] CSS: reuse the cockpit.css selectors where possible
      (`.cockpit-nav-group`, `.cockpit-nav-item`, etc. — they're
      already loaded from base/cockpit copies).

## Notes
Replicates mode 1's `cockpit.js`-driven left pane against the same
JSON contract. The first three nav modes (features / tasks /
issues) share a similar shape — the renderer code should be
parametric on mode so TASK-0084 can add the rest without rebuild.
