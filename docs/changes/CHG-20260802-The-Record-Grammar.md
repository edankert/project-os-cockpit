---
type: "[[change]]"
id: CHG-20260802-The-Record-Grammar
title: "Both panes adopt the record column's density: one-line rows, status said once at the head, and everything finished behind a single line"
status: merged
date: 2026-08-02
owner: user:edwin
component: [static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[FEAT-0057-The-Record-Grammar]]", "[[ISS-0083-Active-Nav-Row-Never-Highlights]]", "[[ISS-0084-Change-Ids-Print-Their-Description-Twice]]"]
---

# The record grammar

## What changed for anyone using the cockpit

The navigator and the context pane now look like the overview's record column, which is where this density already worked.

- **Rows are one line** — `FEAT-0056  Open work sorts first…  done` — at 27px instead of 60px. The type icon is gone; the ID was already type-coloured.
- **A group says its status once**, in its head: `PHASE-007 · Agent instrumentation · 19 · done`. Rows in a uniform group no longer repeat it — the tasks view printed "done" 261 times.
- **Everything finished sits behind one line**: `16 finished phases · 54 features`. Two clicks reach any note, and the group holding the note you are reading opens itself.
- **The context pane is a stack of cards** — `TASKS 5 · done` — with the body closed when every link in it is terminal.

Measured on this repo: the features navigator went from **~1440px to 286px**.

## What did not change

Nothing is filtered. A closed card still names the type and how many; the *filter* [[FEAT-0056]] removed rendered nothing at all, and that distinction is why a disclosure default is allowed where the filter was not. `contextGroupRows` still takes no collapse parameter.

## Also fixed

- **[[ISS-0083]]** — the navigator has never highlighted the open note: `refreshActiveNavRow` selected `li.nav-item`, but that class is on the `div` inside the `li`. Zero matches, silently.
- **[[ISS-0084]]** — change rows printed their description twice, because a change note's `id:` *is* its description. The ID column now shows `CHG-20260802` and lets the title do the describing. Display only; `id:` is untouched and links resolve on the full value.

## Paths

- `desktop/src/renderer/completed-work.ts` — `uniformStatus`, `groupHeadSummary`, `shortNoteId`
- `desktop/src/renderer/renderer.ts` — the one-line row, `renderSettledRollup`, `openGroupsContaining`, context cards
- `src/project_os_cockpit/static/cockpit.js` — the same, hand-written
- both stylesheets — `.nav-item-line`, `.nav-group-summary`, `.nav-rollup*`, `.ctx-card*`

`nav-item-line`, not `nav-item-compact`: that class already exists as the Library's file row and paints a file icon.

## Follow-up, same day — [[ISS-0085]]

The first pass reached **one** of the left pane's four row renderers. `pickItemRenderer` routes per group, so risks and designs (`stacked`) and requirements and plans under features (`nested`) kept the old two-line card at up to 90px — and the renderer that *was* rewritten still printed `item.subtitle`, which the server sends for every feature, design and risk.

All three now go through one `buildNavRow`, and the subtitle is gone from the left pane entirely. Measured after: every card **24–27px**, one class, **zero** subtitles, features navigator content at **97px**.

`navItemCompact` (the Library's file tree) is deliberately unchanged — a filename with a file icon, already one line, and not a lifecycle row.

## Second follow-up — [[ISS-0086]], and the overview

The roll-up was the wrong shape. `16 finished phases · 54 features` behind one closed line meant the features navigator's whole top level was **two rows**, and which phases exist left the page — as did the task status vocabulary and the issue severity ladder.

**Quantity lives in a group's body; structure lives in its head.** Collapsing bodies is right. Collapsing heads deletes the taxonomy.

The band is now `Completed · N` — the overview's exact wording since [[FEAT-0043]] — **open by default and persisted per mode**, with every finished group named beneath it as a one-line closed head.

The overview was corrected in the other direction at the same time:

- it now carries **phase IDs** (`PHASE-001 · MVP`), which it never had — the only surface in the cockpit that did not name its notes
- `.scope-name`'s `max-width: 55%` capped every name at **224px in a 424px row**, truncating 13 of 24 rows with ~200px unused. Name width is now 312px and truncation is down to genuine overflow.

And [[ISS-0084]]'s ID shortening reached the **seven** remaining call sites it had missed, including the review desk, which still rendered `CHG-20260802-Completed-Work-Collapses` in full.

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
