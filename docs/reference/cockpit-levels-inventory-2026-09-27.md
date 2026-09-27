---
type: "[[reference]]"
id: REFERENCE-COCKPIT-LEVELS-INVENTORY
aliases: ["REFERENCE-COCKPIT-LEVELS-INVENTORY"]
title: "What the cockpit can show today, and where each thing would live if the levels designs were built"
status: active
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
scope: "project"
source:
  - "Edwin 2026-09-27: 'I think some of the functionality would be removed if we would implement this, for instance the opportunity to read none project-os type tickets stored in the docs area'"
  - "Edwin 2026-09-27: 'on the fleet option, is there any way we can use the left Need you pane for this instead of a separate page? On the project view is this a kanban board ... On view can we use the left pane for the high level view and go down to the right for a more specific view or is this what is already intended?'"
  - "[[REFERENCE-CAPABILITY-REGISTER]] as it stood on 2026-09-27, read row by row; desktop/src/renderer/index.html (the seven view buttons, the left pane's Needs you panel); src/project_os_cockpit/cockpit.py (NAV_MODES, _library_groups)"
related:
  - "[[PHASE-045-The-Cockpit-In-Layers]]"
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[DES-0016-Levels-Of-Abstraction]]"
  - "[[REFERENCE-CAPABILITY-REGISTER]]"
  - "[[GLOSSARY]]"
  - "[[ADR-0028-Work-Has-Three-Phases]]"
tags: [reference, levels, inventory, navigation]
---

# What the cockpit shows today, and where it would go

## Purpose

This note is the check that the levels designs remove nothing by accident. It lists every navigation-relevant row of [[REFERENCE-CAPABILITY-REGISTER]] and says where each one lands under [[DES-0015-The-Cockpit-In-Layers]], under [[DES-0016-Levels-Of-Abstraction]], and under the proposal in the last column.

Edwin asked for it on 2026-09-27, after reading DES-0015 and noticing that the Library, where untyped Markdown under `docs/` is read, had no obvious home in it. He was right, and the table shows three more things with the same problem.

The words used here are the proposed vocabulary in [[GLOSSARY]], section "Proposed words for the levels". They are not agreed yet (PHASE-045, D11).

## The rule this note checks

**A level hides things; it never removes them.** Everything a person can reach today stays reachable within two clicks of the Project level, and anything moved says where it went. A workspace with no project-os notes, such as an Obsidian vault, opens on the Library instead of on an empty Project screen.

This is proposed as decision D12 in [[PHASE-045-The-Cockpit-In-Layers]]. Until it is decided, this note records the gaps and does not fix them.

## A correction to the first review

The first review of the designs, on 2026-09-27, said the navigator has nine views and that DES-0015 drops four of them. That was wrong. The server answers nine modes (`NAV_MODES` in `cockpit.py`), but the shell shows **seven buttons**: Overview, Intent, Features, Issues, Tests, Publication and Library. Tasks, Active and Recent are served and have no button. So DES-0015 removes two buttons that people use today, **Library and Publication**, and moves the Overview's contents under a fold.

## The proposed picture: levels run left to right across the panes

The shell already has four panes side by side. The proposal is that each pane shows one level, and going one level deeper means moving one pane to the right.

| pane, left to right | level it shows | what is there today |
| --- | --- | --- |
| the rail and the Needs you panel beneath the navigator | **Fleet**: which project needs me | the rail squares, and a Needs you panel that already has one card per project that waits on you (`shell.agents.attention`) |
| the navigator | **View**: the list of one kind of note, grouped by state | the navigator, one group per phase or severity |
| the centre | **Note**, once a row is picked. Before a pick it shows a summary of what the panes to its left have chosen: the **Project** level (the Overview page) when a project is picked, a picture of the whole view when a view is picked | the Overview page, or the note |
| the right pane | **Evidence** for the note in the centre | linked notes and backlinks (`shell.context.pane`) |
| a page reached from Evidence, or the terminal | **Trace**: the agent's turns and tool calls | the session page (`~session/<id>`), the terminal |

Two consequences follow, and both are proposals:

- **The navigator and the centre never show the same list.** DES-0015's Plate 3 draws the Build list in the navigator and again in the page. Under this picture the centre shows the selected note, or a summary picture of the whole view when nothing is selected. That is D15.
- **The Project level is a summary, not a pane of its own.** It is what the centre shows after a project is picked on the rail and before anything else is. So "deeper to the right" holds for the lists (projects, then notes, then evidence), and the centre's summary is the place a person lands on the way down.
- **The fleet needs no page of its own.** DES-0016 proposed a separate portfolio screen (its D8). The Needs you panel already lists projects across the fleet, fed by agent state, the record's owed count and unpushed commits. Growing it to show each project's owed counts by verb would give the Fleet level without a new page. That is D14.

## The inventory

Keyed by the register. "Gap" means the design leaves a person with no path to it, or does not mention it at all.

| register key | what it is | DES-0015 | DES-0016 | proposal |
| --- | --- | --- | --- | --- |
| `shell.workspaces.rail` | the rail of project squares | L0 Glance: the four facts on the square | A0 | Fleet, unchanged |
| `shell.agents.attention` | the Needs you panel in the left pane, one card per project that waits on you | **not mentioned** | **not mentioned**; a separate A0 page is drawn instead | **Fleet**: grows to show owed counts by verb, projects with nothing owed folded to one line (D14) |
| `shell.fleet.rollup`, `shell.pages.agents` | the `~agents` page: every workspace's agent, sessions, push | not mentioned | the A0 page would overlap it | stays as the Fleet level's full page, opened from the panel |
| `shell.agents.usage` | account usage bars at the sidebar foot | not mentioned | not mentioned | unchanged |
| `shell.nav.modes`: Overview | the Overview page: digest, unpushed commits, phase squares, validator report, contribution grid | replaced by Home; contents move under L4 Record as "All phases", "Counts", "History" | A1 | **Project** level; keeps the name Overview (D11). Every section it drops gets a named link on it |
| Overview's contribution grid | the weekly activity grid | **gap**: not mentioned | not mentioned | kept under the Overview's history link, or retired by decision, not by omission |
| `shell.nav.modes`: Intent | designs, ADRs, standing documents | renamed **Design**; the standing documents become the last fold | Design | **View**, keeps the name Intent, which Edwin agreed in TASK-0385 |
| `shell.nav.modes`: Features | features, requirements, tasks by phase | renamed **Build**; closed phases folded | Build | View, keeps the name Features, grouped by state |
| `shell.nav.modes`: Issues | issues by triage and severity | Issues; fixed folded | Issues | View, grouped by state |
| `shell.nav.modes`: Tests | the test corpus, release test, checks | renamed **Verify** | Verify | View, keeps the name Tests |
| `shell.nav.modes`: Publication | commit, push, deploy, release | **removed as a view**; split into Home's Shipping card and Verify (D2, reopens [[ADR-0028-Work-Has-Three-Phases]]) | as DES-0015 | open; D2 decides it. If removed, its ladder must be one click from the Overview |
| `shell.nav.modes`: Library | Docs tree (untyped Markdown under `docs/`, root files like the README), pinned notes, note types found in a vault | **gap**: moved to L4 Record, reached "on purpose from L3"; an untyped note has no L3 page, so only search reaches it | **gap**: not mentioned | **View**, kept as a button. A workspace with no project-os notes opens on it (D12) |
| `shell.nav.pins` | pinned notes | **gap**: lives in the Library, so it goes with it | not mentioned | stays in the Library view |
| `shell.nav.modes`: tasks, active, recent | served by the server, no button in the shell | not mentioned | not mentioned | unchanged; Recent is a candidate to replace the digest band's list |
| `shell.nav.needs-you` | the owed group first in each view ([[ADR-0025-An-Owed-Row-May-Appear-Twice]]) | kept | kept | kept, as the first state group of every view |
| `shell.nav.platform` | the platform filter over the navigator | **gap**: not mentioned | not mentioned | kept; the release test depends on it |
| `shell.nav.hide-completed` | collapse completed work | superseded by folding done work to a count | same | kept until the fold is built, then retired by decision |
| `shell.stage.tabs`, `find`, `quick-switch`, `capture` | tabs, find in page, ⌘P, file an issue from anywhere | search and capture kept | not mentioned | unchanged |
| `shell.reader.render` | a note rendered, frontmatter first | L3: header card, frontmatter folded | A3 card, A4 body | **Note**: a summary at the top, the body below, the frontmatter folded |
| `shell.reader.actuators` | the verbs on a note | kept | kept | unchanged |
| `shell.reader.viewer` | a design's HTML page framed | L4, and pictures first on a design's L3 | A4 | unchanged |
| `shell.context.pane` | right pane: linked notes and backlinks | kept, folded to groups with a state; option B slides it in "only for an artifact" | not placed | **Evidence**: linked notes, plus the ledger, commits and runs for the note in the centre. Option B's "only for an artifact" would hide backlinks, and is a gap |
| `shell.pages.history` | what changed and when | under L4 Record | A5 | one click from the Overview |
| `shell.validation` | the validator report | under L4 Record | A5 | Evidence for a note; the whole report one click from the Overview |
| `shell.pages.checks`, `release`, `release.settle`, `release.coverage`, `release-test` | the release pages and the release test | inside Verify's "This release" card | Verify | inside the Tests view, as today since [[FEAT-0155]] |
| `shell.pages.accept`, `shell.pages.test-run` | acceptance and test runners | from L3 | from A3 | from the Note, unchanged |
| `shell.pages.session` | one agent session | L4 | A6 Trace | **Trace**, reached from Evidence |
| `shell.pages.inbox` | the inbox tray and page | **gap**: not mentioned | not mentioned | unchanged; the tray sits in the left pane beside the Needs you panel |
| `shell.agents.strip` | the agent strip: state, cost, context, cache | dot, name and tool stay; cost, context and cache move to L4 | A6 | open: moving cost off the strip changes what is visible and is Edwin's call (D5) |
| `shell.agents.approvals`, `shell.agents.follow` | approvals, dispatch, follow the agent | **gap**: not mentioned | not mentioned | unchanged; Follow must land on the Note level |
| `shell.windows` | new window, deep links `cockpit://<project>/<path>` | not mentioned | not mentioned | every level needs an address a deep link can name |
| `shell.state.local` | the remembered nav mode and pane widths | not mentioned | not mentioned | a renamed or removed view must keep answering, the way `MODE_ALIASES` already does for `design` → `intent` |
| mode 1, the tablet HTML | the sidecar's own pages | out of scope | out of scope | out of scope |

## What the table says

- **Four gaps are real losses.** The Library (and the pins inside it), the Publication view, the platform filter and the right pane's backlinks under option B. All four are things people use today.
- **Six rows are simply not mentioned.** The Needs you panel, the inbox, approvals and follow, deep links, the remembered view, and the contribution grid. None is a loss by design; each is a place where an implementation would have had to guess.
- **The Needs you panel was overlooked by both designs**, and it is already a fleet-level surface. That is why the Fleet level is proposed there rather than on a new page.

## Maintenance

Re-read this against [[REFERENCE-CAPABILITY-REGISTER]] whenever a design in [[PHASE-045-The-Cockpit-In-Layers]] is revised. A register row that is missing here is a row nobody has placed yet.
