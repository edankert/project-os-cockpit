---
type: "[[issue]]"
id: ISS-0298
aliases: ["ISS-0298"]
title: "A link whose project switch is still in flight is opened by whichever project arrives first, so picking another project on the rail lands the link in a project it never named"
status: fixed
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
source: ["Independent review of FEAT-0146, 2026-09-11, finding 9: 'openWorkspace does not clear pendingCrossRepoJump, so whichever workspace reports ready next consumes the parked link.'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]", "[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]"]
tests: ["[[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]", "[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"]
---

# A parked link opens in whichever project arrives first

## Problem

A link to a project that is not on screen is parked while the window switches. Nothing says which project may consume it. If the reader picks a third project on the rail before the switch finishes, that project's sidecar reports ready first and opens the link's page — in a project the link never named.

This is not a hypothetical race. It happened during the TST-0085 walk on 2026-09-11: a click on the rail moved the window back to your-health 7 seconds after a link had moved it to project-os-cockpit.

## Repro

1. With project-os-cockpit on screen, run `desktop/scripts/open-link.sh your-health FEAT-0107`.
2. Before your-health finishes starting, click a third project on the rail.
3. That third project opens, and the link's note is looked up there. The reader sees that project's FEAT-0107, or "has no FEAT-0107".

## Expected

Only the project the link names opens the link's page. If the reader has gone elsewhere, the link is dropped and said so, rather than applied to the wrong project.

## Actual

`openWorkspace` does not clear `pendingCrossRepoJump`, and the sidecar-ready handler consumes the parked jump for whichever workspace is active when it fires. `locateAndOpen` never compares its `project` argument with the workspace on screen.

The defect predates [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] — it arrived with the parked jump in [[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]] and widened when [[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]] parked `cockpit://` links the same way. What this feature changes is the landing: the wrong project's *bench* rather than the wrong project's note.

## Next Actions

- [x] The ready handler consumes a parked link only when the arriving workspace is the project the link names, matched against its project id and its workspace id. Otherwise the link is dropped and the reader is told, because a link that silently does nothing looks the same as one that failed.
- [x] `tests/test_design_links.py::test_a_parked_link_is_consumed_only_by_the_project_it_names` pins it, and [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]'s `command:` runs it. Walked as step 10 of [[TST-0085-A-Link-To-A-Design-Shows-The-Design]], added for it, in the renderer harness: the third project opened on its own overview, the bench did not open there, and the status bar read "DES-0002 was not opened: you switched to another project."
- [ ] Not yet seen in the running window. The race needs a third project picked during a switch, and Edwin was using the window. The window also runs a build older than this fix.
