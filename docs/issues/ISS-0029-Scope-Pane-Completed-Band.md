---
type: "[[issue]]"
id: ISS-0029
aliases: ["ISS-0029"]
title: "The left Scope pane never got plate C's In-flight/Completed split — five finished phases still shout as loudly as the live one"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
component: ui
source: ["user-report:2026-07-26"]
design: "[[REF-0001-Overview-Redesign-Dossier]]"
related: [ADR-0006]
tests: []
---

# Scope pane missed the Completed band

## Problem

[[REF-0001-Overview-Redesign-Dossier|The overview redesign dossier]], plate C pin 9, redraws the left **Scope** pane as:

```
Scope
⌂ Project
In flight
  Agent Instrumentation  100%
  Downstream Pilot        33%
  Future                  22%
Completed · 5
  Native Cockpit UI     ✓ 52
  Desktop Shell         ✓ 9
  …
```

What shipped is still plate A's flat list — one `Phases` heading, every phase in it, each with a progress bar:

```
Scope
⌂ Project
Phases
  Render Server         100%
  Project-OS Adapter    100%
  Downstream Pilot       33%
  …
```

## Why it was missed

The **centre pane** got the treatment: `buildPhaseSection()` splits live from complete and renders a `Completed · N phases · M items` accordion (TASK-0201), with `phaseIsComplete()` as the predicate. The **left pane** is built by a different function, `renderOverviewScopePane()`, which nobody revisited — so half the plate shipped.

The dossier's own critique names the cost precisely: *"five finished phases shouting as loudly as the live one"*. A 100% progress bar is the loudest a row in that list can be, and five of the eight rows were wearing one.

## Fix

`renderOverviewScopePane()` now mirrors the centre pane:

- **In flight** — non-complete phases, progress bar retained.
- **Completed · N** — collapsible band, closed by default, each row showing `✓ <item count>` instead of a full bar.
- `phaseIsComplete()` is **shared with the centre-pane accordion** rather than reimplemented. Two panes disagreeing about which phase is finished is exactly the class of drift this codebase keeps paying for (ISS-0023, ISS-0026, ISS-0028), and the cheapest way to not have it is one predicate.
- Open/closed state persists in `localStorage`, matching the accordion's per-session memory.

Consistent with [[ADR-0006-Retire-Delivered-Band|ADR-0006]]: "Completed" is a **view** over done phases, never a status.
