---
type: "[[issue]]"
id: ISS-0295
aliases: ["ISS-0295"]
title: "In Design, Publication and the landing views, any file change in the project moves the reader off the note they have open and onto the view's landing page"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-10
updated: 2026-09-10
source: ["Found 2026-09-10 while verifying ISS-0293 through the debugging port: a design note opened by link was replaced by ~design seconds after the note's file was edited"]
severity: high
component: desktop-renderer
parent: ""
related: ["[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[ISS-0040]]"]
tests: []
---

# A file change moves the reader off the open note

## Problem

With the left pane in Design mode, any file changing anywhere in the project moves the reader from the note they are reading to the Design landing page. Agents write files continuously, so a note opened in that mode stays on screen only until the next write. Publication mode and the landing views (Issues, Tests and the rest of `VIEW_LANDING_RELS`) have the same shape.

## Repro

1. Put the left pane in Design mode and open any ordinary note, for example `docs/design/recovery-and-food-feedback/README.md` in your-health.
2. `touch` any file under the project's `docs/`.
3. Within a second the centre pane shows `~design` instead of the note.

Measured through the debugging port on 2026-09-10: `currentRel` read `design/recovery-and-food-feedback/README.md`, then `~design` four seconds after a `touch`.

## Expected

A file change refreshes what is on screen and leaves the reader where they are. `scheduleSoftReload` already says so in its own comment: "A file changing under an open document is not a reason to move them to the top of it."

## Actual

`scheduleSoftReload` calls `loadWsNav()` to refresh the left pane, and `loadWsNav` also lands the current mode on its page. In Design mode that landing runs whenever `currentRel` does not start with `~design`, which is true of every ordinary note. The soft reload's own `navigateTo(currentRel)` and the landing race, and the landing can win.

## Next Actions

- [x] `loadWsNav` takes `{ land: false }`, and the soft reload passes it: a file change refreshes the list without landing. A pending landing suppression is left for the arrival it was set for.
- [x] Seen working in the window: after a `touch` of the open note, `currentRel` still read `design/recovery-and-food-feedback/README.md` and its six images were still loaded.
- [x] Guarded by `tests/test_desktop_note_mounts.py::test_a_file_change_refreshes_the_list_without_landing`. Two existing source guards named the old form and were rewritten to state the same rule for the new one: `test_cross_repo_links.py` still requires the suppression to decide every landing, and `test_checks_view.py` finds `loadWsNav` by its name rather than its empty parameter list.
