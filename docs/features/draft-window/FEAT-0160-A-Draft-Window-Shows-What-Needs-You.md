---
type: "[[feature]]"
id: FEAT-0160
aliases: ["FEAT-0160"]
title: "A draft window shows what needs you, where work stands, the AIs"
status: doing
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source:
  - "Edwin 2026-10-13: 'a new window beside the present one, keep the sidecar ... can we do this as a draft solution for now and probably best to do this in the cockpit project for now. I agree that multiple sessions will require multiple branches one branch or copy per session ...'"
  - "[[project-os-dev#REFERENCE-COCKPIT-SIMPLIFICATION-SORT]], the sorted table of 2026-10-13 and its section 'Suggestion: a new window on the same sidecar'"
goal: "Edwin opens a second, draft window from the menu and sees three things for all his projects: what is owed to him, where a phase stands, and what each project's AI session is doing. Every act still happens in the present window, which the draft opens at the right page."
requirements: []
tasks:
  - "[[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]"
  - "[[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]]"
  - "[[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]]"
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related:
  - "[[FEAT-0152-Home-First]]"
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[DES-0016-Levels-Of-Abstraction]]"
  - "[[ADR-0020-Obligations-Live-With-Their-Subject]]"
  - "[[ADR-0025-An-Owed-Row-May-Appear-Twice]]"
  - "[[REQ-0026-Only-Human-Owned-Transitions]]"
  - "[[REFERENCE-CAPABILITY-REGISTER]]"
tags: [draft, window, needs-you, fleet]
---

# A draft window shows what needs you, where work stands and the AIs

**Planned, not built.** This is a draft: a second window Edwin can open and close, added beside the present cockpit window without changing it.

> **As asked (Edwin, 2026-10-13).** "a new window beside the present one, keep the sidecar ... can we do this as a draft solution for now and probably best to do this in the cockpit project for now. I agree that multiple sessions will require multiple branches one branch or copy per session ..."

## Goal

Edwin opens a draft window from the application menu while the present window keeps working. The draft window shows three areas and nothing else: what is owed to him across all projects, where a phase stands, and what each project's AI session is doing. It performs no act itself. A row that needs an act opens the present window at the page where that act is done.

The present window stays as it is and becomes "the record": the place for the navigator, the notes, the release test and every button that writes.

## How this relates to FEAT-0152 and the two designs

[[FEAT-0152-Home-First]] has the same goal: a first screen that shows only what a person needs. It reaches that goal inside the present window, by replacing the overview's first screen with a Home page for one project. It is at `backlog` and waits for Edwin to accept [[DES-0015-The-Cockpit-In-Layers]].

This feature is a draft of that goal in a separate window. It differs in three ways:

- **It is cut by who has to act.** The first area holds only what is owed to Edwin, the second holds status nobody acts on, and the third holds the AI sessions. FEAT-0152 cuts by layer of data for one project.
- **It covers every project at once.** FEAT-0152's Home page is for the project that is open.
- **It replaces nothing.** The overview, its tiles and every page of the present window are untouched. FEAT-0152 stays at `backlog` and is not superseded.

It is not built against either design. [[DES-0015-The-Cockpit-In-Layers]] and [[DES-0016-Levels-Of-Abstraction]] stay `proposed`, and the `design:` field above is empty on purpose. The basis is Edwin's decision of 2026-10-13, recorded in [[project-os-dev#REFERENCE-COCKPIT-SIMPLIFICATION-SORT]]. What Edwin learns from using the draft is input for the phase's open decisions, in particular D1 (does a home screen replace the overview or sit beside it), D8 and D14 (does the all-projects level get a screen of its own). The draft decides none of them.

## Scope

In scope:

- **A menu item that opens the draft window.** The present window stays open and keeps working. Closing the draft window changes nothing else.
- **Area 1, Needs you.** One list of what is owed across all projects. Each row names the project, the subject and one verb, the verb the cockpit already uses for that kind of owed thing (Decide, Accept, Approve, Triage, Run, Push and so on, from `src/project_os_cockpit/obligations.py`).
- **Area 2, Where we are.** For the active phase of a project Edwin chooses, four answers: what is done, what is happening now, what is next, and what still stands between the phase and finished.
- **Area 3, The AIs.** One row per project with its AI session's state: working, stuck, waiting for Edwin, or none.
- **A row that needs an act opens the present window at that item**, through the `cockpit://<project>/<note ID or path>` link the shell already handles.
- **A browser harness and unit tests** for the page's pure functions, and the capability register row.

Out of scope for this draft:

- Consoles (terminals) in the draft window.
- Several AI sessions in one project.
- A copy or branch per session.
- The runner (a lead AI that starts and supervises sessions) and its loop.
- Any change to a write path of the sidecar (the Python server each project runs).
- Any change to the pages of the present window.
- Rebuilding any act in the draft window. No button in it writes to a note, a ledger or git.
- "Where we are" for a feature or a release. The draft answers it for a phase only; see "Assumptions".

## Later steps, recorded and not planned here

Edwin agreed on 2026-10-13 that several sessions in one project will need one branch or copy of the repository per session, because two sessions writing to one working copy overwrite each other. That is a later step with its own feature. The order suggested in [[project-os-dev#REFERENCE-COCKPIT-SIMPLIFICATION-SORT]] is: this draft window first, then consoles per session with a copy per writing session, then the runner's loop. None of it is work in this feature, and no task here prepares for it.

## Acceptance

Worded for a draft. Each line is a claim a reviewer can refute.

- Edwin opens the draft window from the application menu while the present window is open, and the present window keeps working: its pages, its console and its live updates behave as before.
- The first area lists what is owed across every project the shell discovers, one row per owed thing, each with exactly one verb.
- Choosing a row in the first area brings the present window to the front, switched to that row's project and opened at that item.
- The second area, for a project Edwin chooses, answers four questions about that project's active phase: what is done, what is happening now, what is next, and what still stands between it and finished.
- The third area lists each project with its AI session's state.
- A project the draft window could not read is named as not read. It is never shown as owing nothing.
- The draft window writes nothing: no request it makes changes a note, a ledger, the snapshot or git.
- The capability register has a row for the draft window.

The acceptance check is [[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]]. It is at `draft` until the window exists.

## Assumptions

Each is the reading the request most directly supports. Edwin can dispute any of them.

- **"Where we are" covers a phase only in this draft.** The decision names a phase, a feature or a release. The acceptance Edwin was given names "the active phase of a chosen project", so the draft does the phase and leaves feature and release for after he has used it.
- **"The active phase" is the phase in the project's `focus.phase`.** Where that is empty, the page offers the project's phases at `active` to choose from. Where there is none, it says so in a sentence.
- **"Keep the sidecar" means the same sidecar processes the present window uses**, one per project. The draft window starts none of its own and does not change how they are started.
- **No requirement note.** The criteria above are a draft's criteria and may not outlive it. If the draft is kept, the ones that should last become `REQ-*` notes then.

## Open questions

None blocks the first task. Each has a default the implementation takes unless Edwin says otherwise.

1. **A project whose sidecar is not running.** The shell keeps some projects "cold" (no sidecar until opened). Default: the draft window reads them the way the rail's health marks already do (`ipc/fleet-health.ts`), and names any project it could not read. It does not start sidecars for all projects just to fill the list.
2. **Where the present window opens when several copies exist.** File, New Window makes a full second copy of the present window. Default: the link goes to the window the shell treats as its main window, as every `cockpit://` link does today.
3. **A new read-only route on the sidecar.** Default: compose the three areas from routes that exist (`/api/cockpit/obligations`, `/api/cockpit/landing`, `/api/cockpit/stats`, `/api/cockpit/state`). If an area cannot be answered from them, a new read-only route is inside the scope, with its own test and its own register row. A write route is not.

## Impact analysis

Checked on 2026-10-13 against the notes this feature's area is constrained by. No contradiction was found. Two tensions are recorded for Edwin.

- **[[REQ-0026-Only-Human-Owned-Transitions]] and REQ-0029 (a delegate is told apart from the person).** No conflict. The draft window performs no transition; the act stays on the note in the present window.
- **[[ADR-0025-An-Owed-Row-May-Appear-Twice]].** No conflict. The first area is a shortcut list, and each row leads to the view that owns it.
- **[[ADR-0020-Obligations-Live-With-Their-Subject]]. Tension.** That decision retired the review desk, a single queue of everything owed, and put each owed thing in the view that owns its subject. The first area is again one list of everything owed, now across projects. It holds no button and no state of its own, so the decision's rule 2 (the act stays on the note) holds. If the draft later becomes the default screen, ADR-0020 needs an amendment, and that is Edwin's decision.
- **[[PHASE-045-The-Cockpit-In-Layers]], Out of Scope. Tension, resolved by Edwin's decision.** The phase excluded "the panel and window architecture". A second window is a new window. Edwin asked for it on 2026-10-13, and the phase note now says so. The panes of the present window are still out of scope.
- **The phase's open decisions D1 to D16.** None is decided by this feature.

## Risk scan

Run against the triggers in `tools/instructions/LIFECYCLE.md`, "Risk scan triggers", on 2026-10-13. No trigger applies, so no `RISK-*` note is filed.

- New external dependency or version constraint: none. The window uses Electron, already a dependency.
- New required environment variable or configuration surface: none. One menu item is added.
- Directory layout or artifact path change: new source files under `desktop/src/` only; no path that a script or another repository reads is moved.
- Runtime increase or new long-running step: the draft window asks every project's sidecar for data while it is open. It should reuse the short cache `ipc/agents-fleet.ts` and `ipc/fleet-health.ts` already keep and ask nothing while closed. This is a design note for [[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]], not a risk note.
- Security, credential or licence exposure: none new. The window only reads. [[ISS-0301]] (a page can post to the sidecar's write routes on the loopback address) is unchanged by a window that makes no write request.

## Verification

Not run yet; nothing is built.

## Links

- Phase: [[PHASE-045-The-Cockpit-In-Layers]].
- Plan: `plan/PLAN.md`.
- Tasks: [[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]], [[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]], [[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]].
- Acceptance check: [[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]].
- The decision and the sorted table behind it: [[project-os-dev#REFERENCE-COCKPIT-SIMPLIFICATION-SORT]].
- Register: [[REFERENCE-CAPABILITY-REGISTER]], rule 1.

## State on 2026-10-13

The draft is built and has not been run inside the application. It was typechecked, unit-tested against a build made outside the repository, and looked at in a browser with real payloads. What was and was not checked is in [[CHG-20261013-A-Draft-Home-Window-Opens-Beside-The-Present-One]]. The three tasks stay `doing` until Edwin has rebuilt and restarted the cockpit and run [[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]]. Nothing is committed.

## Second cut, 2026-10-13: a picture, and on top

Edwin tried the first cut the same evening and said: "It is too much text heavy instead we should be using diagrams or images to make this understable just by looking at, the text can be in the main application when opening the note. also if we want this as separate navigation window then the window should stay on top."

So the window was redrawn as a board and made a small window that stays in front.

- **One row per project.** The projects that want a person come first: by the agent's state, then by how much is owed, then by name.
- **The agent is one mark,** different in shape and colour for each state: working, needs your answer, stuck, finished its turn, quiet, not open.
- **Each thing owed is one mark,** shaped by its verb: Decide, Accept, Approve, Run, Confirm, Triage, Push, Deploy. Commits to push are one mark with their number. More than eight marks of one kind become "+n".
- **Each active phase is one bar:** a mark per feature (done, in progress, not started), a divider, then a dot per exit criterion (ticked or not). More than eighteen features are drawn as one bar to scale with "done/total". The focus phase's number is bold. A release in preparation is a pill with its version and the number of checks still open.
- **The top line is the key and the totals at once:** each mark, how many of it are on the board, and its one word. The foot line is the key to the bars.
- **The words are in tooltips and in the present window.** Every mark names its subject when hovered and opens it in the present window when chosen. The window itself shows project names, phase numbers and counts, and no sentences, except "not read" for a project that could not be read.
- **It stays on top.** The window is 560 by 660 points by default and floats above ordinary windows, including other applications' windows. Floating only above the cockpit is a small change if that is what Edwin meant.

What this drops from the first cut: the project picker, the lists of feature titles, the sentences under "Left", and the three-column layout. The model functions behind them remain and are still tested.

Checked the same way as the first cut, plus in place: the build was redone, all 187 node tests pass in the repository, and the cockpit was restarted. The board was looked at in a browser with the fixture and with payloads captured from eight projects. It has still not been looked at inside the application by anyone but Edwin.
