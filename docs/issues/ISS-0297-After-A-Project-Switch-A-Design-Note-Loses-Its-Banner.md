---
type: "[[issue]]"
id: ISS-0297
aliases: ["ISS-0297"]
title: "After a project switch, a design note is shown without its banner, because the renderer looks it up in the previous project's list of designs"
status: fixed
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
source: ["Found 2026-09-11 walking TST-0085 step 5 in the renderer harness: cockpit://project-os-cockpit/DES-0003, sent from your-health, opened DES-0003's note without the banner 'This design has no artifact yet.'"]
severity: low
component: desktop-renderer
parent: ""
related: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]", "[[ISS-0041-Artifactless-Design-Is-Unreadable]]", "[[ISS-0015]]"]
tests: ["[[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]", "[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"]
---

# After a project switch, a design note loses its banner

## Problem

A design note normally opens with a banner above its text: "This note describes a design" and a button to the design bench, or "This design has no artifact yet." After the reader switches project, the first design notes they open show no banner at all. If the two projects had a design note at the same path, it would show the other project's banner and a button to a bench that says "No design".

## Repro

1. In your-health, open the Intent view, so the renderer loads your-health's designs.
2. Run `desktop/scripts/open-link.sh project-os-cockpit DES-0003`.
3. DES-0003's note opens, with no banner.

Measured in the renderer harness on 2026-09-11: after step 2, `designRegister` still listed your-health's DES-0001 and DES-0002, and `.design-note-banner` was absent.

## Expected

DES-0003 opens with "This design has no artifact yet.", as it does when the window starts in project-os-cockpit. [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] step 5 expects that banner.

## Actual

`designRegister`, the renderer's cached list of the project's designs, is not cleared when the project changes. The note page fetches the list only when it is empty (`if (!designRegister.length) await fetchDesignRegister()`), then looks the note up in it by path. After a switch the list is the previous project's, so the lookup finds nothing and no banner is drawn.

`openWorkspace` already clears the other per-project caches (`checksData`, `stripLastPrompt`) for the same reason ([[ISS-0015]]). The design list was left out.

## Next Actions

- [x] `openWorkspace` clears `designRegister` along with the other per-project state.
- [x] Seen working in the renderer harness: after the repro's link, DES-0003's note opened with "This design has no artifact yet." Not yet seen in the running window, which was still on the build before this fix.
- [x] `tests/test_design_links.py::test_a_project_switch_forgets_the_previous_projects_designs`. Deleting the reset turns it red.
- [x] The remaining way to get the symptom, found by the independent review: the reset does not stop a `fetchDesignRegister()` already in flight from the previous project, whose reply refilled the list after the switch. That function now drops a reply from a sidecar that is no longer on screen. `test_a_reply_from_the_project_the_reader_left_never_lands` pins both this and the matching fix in `loadOverviewScopePane`.
