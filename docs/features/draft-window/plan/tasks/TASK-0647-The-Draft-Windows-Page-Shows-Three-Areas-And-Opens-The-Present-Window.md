---
type: "[[task]]"
id: TASK-0647
aliases: ["TASK-0647"]
title: "The draft window's page shows three areas and opens the present window"
status: doing
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source: ["Edwin 2026-10-13, the three areas in [[project-os-dev#REFERENCE-COCKPIT-SIMPLIFICATION-SORT]], 'The screen this points to'"]
parent: "[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"
effort: "M"
due: ""
depends:
  - "[[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]"
blocks: []
related:
  - "[[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]]"
tests: []
---

# The draft window's page shows three areas and opens the present window

The draft window's page draws Needs you, Where we are and The AIs from the payload of [[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]. A row that needs an act opens the present window at that item. The page has no button that writes.

## Definition of Done

- [x] **Needs you** is one list across all projects. Each row shows the project, the subject's title before its ID, and exactly one verb, the verb the present window uses for that kind of owed thing.
- [ ] Choosing a Needs you row opens the present window, switched to the row's project and opened at that item. A row with no note behind it (unpushed commits, a release gate) opens the page where that act is done.
- [x] **Where we are** has a project picker. For the chosen project's active phase it answers four questions under four plain headings: what is done, what is happening now, what is next, what still stands between the phase and finished.
- [ ] Each item named in Where we are opens in the present window when chosen.
- [x] **The AIs** lists every project with one state word for its session: working, stuck, waiting for you, or no session. Choosing a row opens that project in the present window.
- [x] A count of zero is written as a sentence ("nothing is owed", "no active phase"), not as `0`.
- [x] A project the payload marks as not read is shown as not read in each area that would have listed it.
- [x] The page updates when the payload changes, without a reload by hand.
- [x] The functions that turn the payload into rows are pure and live in a file of their own with no imports and no exports, loaded as a plain script before the page's own script, the arrangement `desktop/src/renderer/deep-link.ts` uses.
- [x] `desktop/src/renderer/renderer.ts`, `index.html` and the present window's styles are unchanged by this task.

## Steps

- [x] Write the pure functions first: owed rows sorted and labelled, the four answers for a phase, the state word for a session, and the `cockpit://` link for a row.
- [x] Write the page: one HTML file, one stylesheet, one script. Reuse the existing colour variables (`base.css`) so the draft looks like part of the same application, and nothing else from the present window's page.
- [x] Wire the three kinds of row to the "open this link" channel.
- [ ] Look at it against real data from this machine's projects, in a copy of the application started for the purpose, and adjust the wording of rows that read badly.

## Notes

- Order for Needs you, as a default: an AI waiting on Edwin first, then what only he can do (decide, accept, push, deploy), then the rest; within a group, oldest first. Edwin's marks on the sorted table in [[project-os-dev#REFERENCE-COCKPIT-SIMPLIFICATION-SORT]] may change this, and the order lives in one pure function so it is cheap to change.
- This is a draft. Where a choice is open, take the simpler one and say so in the change note; do not build a setting for it.
- The draft filters nothing out. The sorted table proposes that some owed kinds go to a lead AI or leave the screen, and that needs a delegation policy that is not part of this feature.

## State on 2026-10-13

Built, and seen in a browser through the harness, not inside the application. The task stays `doing` until the unticked lines have been seen to hold in the running cockpit.

- **Where it is.** `desktop/src/renderer/home.html`, `home.css`, `home.ts`, and the pure functions in `home-model.ts`.
- **Differences from the list above.** The AIs area uses six words, not four: working, needs your answer, finished its turn, stuck, quiet, not open. They are the shell's own states (`busy`, `needs-input`, `waiting`, `error`, anything else, no sidecar). "Where we are" lists every active phase of the chosen project, the focus phase first, and adds a release in preparation as one row. "Left" lists the phase's unticked exit criteria.
- **Rows with no note.** Commits to push or deploy are one row per project and open the page the sidecar names for them (`~history`).
- **Not checked.** That choosing a row brings the present window forward at that item, and the look of the page inside the application's own window. The last step above asked for a copy of the application started for the purpose. The application takes a single-instance lock and shares its settings folder, so a second copy was not started; the page was looked at in a browser with payloads fetched read-only from the eight running sidecars.

## Second cut on 2026-10-13

Edwin found the page too text heavy and asked for a picture, with the text left to the present window. The page is now a board of marks and bars; [[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]] has his words and what the board draws. Three lines of the list above no longer describe the page as written: there is no project picker, the four answers are drawn and not headed, and a zero is drawn as nothing with the sentence kept for the case where nothing at all is owed. `home.html`, `home.css` and `home.ts` were rewritten; `home-model.ts` gained `homeVerbGlyph`, `homeBoard` and `homeVerbTotals`.
