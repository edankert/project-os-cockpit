---
type: "[[issue]]"
id: ISS-0296
aliases: ["ISS-0296"]
title: "A link that switches project while the reader is in Overview opens its page, but the left pane is never loaded for the new project"
status: fixed
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
source: ["Reported 2026-09-11 by a your-health session in the cockpit's own console: 'When a link switches you into a project while you're on the Overview, the project opens but the left pane still says Pick a workspace from the rail on the left.' Reproduced the same day in the renderer harness while walking TST-0085."]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]", "[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
tests: ["[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"]
---

# A link that switches project in Overview leaves the left pane unloaded

## Problem

With the left pane in Overview mode, a `cockpit://` link or a cross-repo link to another project opens the page it names, but the left pane is not loaded for the arriving project. On a window that has not shown an overview yet, the pane says "Pick a workspace from the rail on the left." Otherwise it goes on listing the previous project's phases under the new project's name.

## Repro

1. Put the left pane in Overview mode, on project-os-cockpit.
2. Run `desktop/scripts/open-link.sh your-health FEAT-0107`.
3. The centre pane shows FEAT-0107. The left pane's header says "Your Health", and under "Scope → In flight" it lists PHASE-005 and PHASE-028, which are project-os-cockpit's phases.

Measured in the renderer harness on 2026-09-11: after the link, the left pane read "Your Health ⋮ SCOPE ⌂ Project IN FLIGHT PHASE-005 Desktop shell…".

## Expected

The left pane lists the arriving project's phases, the same as when the reader picks that project on the rail.

## Actual

In Overview mode, `loadWsNav` does nothing but land on `~overview`. The left pane's scope list (`renderOverviewScopePane`) is drawn as a side effect of rendering that page. A link that switches project parks its target and suppresses the arriving project's landing, so the link's page is not overwritten ([[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]). Suppressing the landing also suppresses the only thing that loads the left pane.

## Next Actions

- [x] When `loadWsNav` skips the Overview landing, it still fetches the project's phase list and draws the scope pane. The new `loadOverviewScopePane` drops a reply that arrives after the reader has switched project again.
- [x] Seen working in the renderer harness: after the link in the repro, the left pane read "Your Health ⋮ SCOPE ⌂ Project IN FLIGHT PHASE-0008 Feedback, Refresh & Energy 78% PHASE-0014 One Stat Registry…". Not yet seen in the running window, which was still on the build before this fix.
- [x] `tests/test_cross_repo_links.py::test_a_skipped_overview_landing_still_loads_the_left_pane`. Deleting the `else` branch turns it red, and so does deleting the stale-reply check. [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]'s `command:` runs that file, so the guard is named by a check rather than only by a file nobody lists.
- [x] Walked as step 9 of [[TST-0085-A-Link-To-A-Design-Shows-The-Design]], added for it. The independent review found that no step of that check put the left pane in Overview mode, so naming it as this issue's test was a claim nothing supported.
- [x] A second window the review found: `loadOverviewScopePane` compared the sidecar before reading the reply's body, so a switch during the read drew the project the reader had left — this issue's own symptom. The comparison now happens after the body is read.
