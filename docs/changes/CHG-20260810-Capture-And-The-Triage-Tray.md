---
type: "[[change]]"
id: CHG-20260810-Capture-And-The-Triage-Tray
title: "⌘N files a thought at triage, and the Issues navigator lifts triage above the severities — regrouping them, not adding them"
status: merged
reviewed_by: ""
review_date: ""
review_verdict: ""
date: 2026-08-10
owner: user:edwin
component: [cockpit-payload, desktop-renderer, note-writes]
related: ["[[FEAT-0061-Quick-Capture-And-Triage]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Capture and the triage tray

## What changed

**⌘N** opens one field. Enter files an issue at `triage`, with `source:` naming the capture and `related:` the note you were reading. Esc costs nothing, and a failed create keeps the text and says why in place.

**The Issues navigator gained `Needs triage`**, above the severities and absent when empty. Rows discharge through Accept-as-severity, **Defer** or Decline.

```
Needs triage · 8      ← was: nothing. `triage` was on no obligation surface
High · 1
Medium · 1
Low · 1
```

## The tray regroups; it does not add

The first cut lifted triage issues into the tray **and left them in their severity cards**. One item, two rows, one screen — [[ISS-0068]]'s failure happening inside a single surface rather than across two, and the thing that would have made the tray indefensible.

A count identity now asserts every issue appears exactly once across the whole Issues payload. That is what makes the tray a *regrouping* of items already in this navigator, which is the ground ADR-0020 allows it on.

## Severity rides the transition

Triaging an issue **is** deciding how bad it is, so accept-as-severity is one write rather than two. Narrow on purpose: only an issue leaving `triage`, only the four documented values, and anything else is **refused rather than ignored** — a silently-dropped field looks exactly like one that was applied.

`Defer` is offered per [[ADR-0020]]'s amendment: 39 issues sit at `triage` across the fleet with a median age of 56 days, and the only verbs were accept and decline, so *"real, but not now"* had nowhere to go.

## Two criteria reconciled, not ticked

`TASK-0284`'s sibling hints and dispatch-from-the-row are **not built**. Both are additions to the row rather than the tray; word-overlap needs a similarity source, and dispatch needs the row menu [[FEAT-0062]] is scoped around — whose fate [[ISS-0126]] has not decided. Recording them as done would be false, and the tray works without them.

## Paths

- `src/project_os_cockpit/note_writes.py` — `severity` on `stamp_transition`, `SEVERITIES`
- `src/project_os_cockpit/cockpit.py` — the `needs-triage` group in `_issues_groups`
- `src/project_os_cockpit/server.py` — severity passed through
- `desktop/src/renderer/renderer.ts` / `.css` — `openCapture`, ⌘N
- `tests/test_human_transitions.py` — 39 assertions across FEAT-0059/0060/0061

## Restart required

Mode 3 is a built bundle. Live after the desktop app restarts.
