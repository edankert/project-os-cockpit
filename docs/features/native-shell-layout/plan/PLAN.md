---
type: "[[plan]]"
id: PLAN-FEAT-0009
aliases: ["PLAN-FEAT-0009"]
title: "Plan: Native shell layout (chrome polish)"
status: active
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
implements: ["[[FEAT-0009-Native-Shell-Layout]]"]
related: ["[[FEAT-0010-Native-Nav-Right-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Plan — FEAT-0009 chrome polish

## What's already done elsewhere

The 3-pane / 4-pane grid + resizers + collapse states + theme tokens
all landed in TASK-0080 (FEAT-0010) and TASK-0085 (right pane
toggle). The OS-theme bridge (data-theme on `<html>`) is in TASK-0075.

What FEAT-0009 still needs is **chrome polish** — the "this looks
like a real macOS app" details.

## Delivery sequence

1. **[[TASK-0093]] — hiddenInset title bar.** `titleBarStyle:
   'hiddenInset'` on the `BrowserWindow`. Traffic lights inset into
   the top-left; we add padding so the rail doesn't overlap them.
   No custom title bar content in v1; the rail header takes that
   role.

2. **[[TASK-0094]] — Status bar (footer).** Thin strip at the
   bottom of the stage with: sidecar health (ready/spawning/exited),
   current note rel-path, latest agent-state. Mostly an information
   surface; doesn't change behaviour. *Backlog.*

3. **[[TASK-0095]] — Theme picker.** Dropdown in the rail (or status
   bar) to override the system theme: system / light / dark. Persists
   to localStorage; sets `data-theme` on `<html>`. *Backlog.*

4. **[[TASK-0096]] — Resizable column splitters.** Drag handles
   between rail / nav / centre / right. Persisted widths.
   Constraints. *Backlog — fixed widths fine for v1.*

## Sequencing notes

- TASK-0093 is the visible win. The others can be scope-trimmed
  indefinitely; they're polish, not new capability.

## Out of plan
- Custom traffic-light positioning beyond `hiddenInset` defaults.
- macOS native tabs.
- A real preferences pane.
