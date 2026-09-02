---
type: "[[task]]"
id: TASK-0233
aliases: ["TASK-0233"]
title: "Drop or paste anything onto the cockpit and it lands in the inbox"
status: done
phase: "[[PHASE-014-Project-Inbox]]"
owner: user:edwin
created: 2026-07-28
updated: "2026-09-02"
source: ["[[FEAT-0045-Project-Inbox]]"]
parent: "[[FEAT-0045-Project-Inbox]]"
effort: "L"
depends: ["[[TASK-0232-Inbox-Convention-And-Triage-Skill]]"]
blocks: []
related: ["[[TASK-0230-Project-Stylesheet-Route]]"]
tests: []
---

# Drop or paste into the inbox

## Why paste matters as much as drop

`⌘⇧⌃4` puts a screenshot straight on the macOS clipboard. Pasting into the cockpit then needs **no file on disk at all** — strictly fewer steps than saving and dragging, which is the stated goal. Drop and paste must land in the same place by the same path, or one of them becomes the good one and the other a trap.

## Definition of Done

- [x] Dropping a file anywhere on the window stores it in the active project's `inbox/` — evidence: the `ignored` branch of the drop handler now files instead of refusing; `test_a_dropped_file_lands_in_the_inbox`
- [x] Pasting an image from the clipboard does the same, with no file on disk — evidence: verified in the Electron app by dispatching a real `ClipboardEvent` — *"Stored in the inbox: 20260728-220024-pasted-shot.png"*
- [x] The existing drop behaviour still works: a project-os `.md` still navigates rather than being filed — evidence: the `navigate` branch is untouched; only the refusal branch changed
- [x] Names are dated and collision-free, and the original filename is preserved where there is one — evidence: `safe_name` + `unique_path`; `test_two_items_in_the_same_second_both_survive`
- [x] The write endpoint is **loopback-only**, size-limited, and **cannot write outside `inbox/`** — path traversal, absolute paths and symlinks all refused — evidence: `test_the_store_endpoint_is_loopback_only` asserts all three clauses, and deleting the guard from the endpoint fails it; traversal covered by `test_a_traversal_name_writes_inside_the_inbox_or_not_at_all`
- [x] The cockpit shows what is waiting and offers to open, reveal or discard each item — evidence: an Inbox mode with a count badge, thumbnails, and Discard; verified in the app — badge `1`, then gone after discarding
- [x] An empty inbox reads as resolved, not as a blank pane — evidence: *"Empty — everything has been triaged."*, seen in the app after discarding
- [x] Every guard test **fails when its guard is removed from the endpoint**, asserts the guarded effect did not happen, and asserts the refusal pre-empts the other branches — evidence: four mutations run; two killed a test. **Two did not** and that is recorded rather than hidden — see Result

## Result

**A limit that could never be reached.** `MAX_ITEM_BYTES` advertised 25 MB — raised to 250 MB on 2026-09-02, [[ISS-0274]] — while the shared JSON body reader capped every request at 2 MB — so ordinary Retina screenshots, which routinely exceed 2 MB, would have been refused by a limit nobody had written down. Found by testing the size guard rather than by reading it. The route now takes its own cap, and `test_an_ordinary_screenshot_is_not_refused` sends 3 MB, because a feature built for screenshots that rejects screenshots is not built.

**Two guards could not fire.** Removing the basename split in `safe_name`, and the cheap name check in `resolve_item`, each left every test green — the `_SAFE` substitution and the `relative_to` containment respectively refuse the same inputs. Both stay, and **both docstrings now say which line is the guard**, because a check that cannot fire under a comment implying it protects something is the defect this codebase has found four times ([[ISS-0024]], [[ISS-0049]], [[ISS-0056]], and the `/_project` route).

The properties themselves are tested independently of which layer provides them, so a future edit that removes the real guard still fails.

*(Superseded in part on 2026-09-02, [[ISS-0274]]. **A third guard could not fire, and this note did not catch it: the suffix allow-list.** It was described here and in the code as one of the things making the drop safe. It was not. `_SAFE` and the `relative_to` containment refuse a hostile name without it; nothing executes a file out of `inbox/`; and it admitted `.svg` — which can carry `<script>` and came back at the cockpit's own origin — while refusing `.zip`, which the server never opens. The list is gone from the write path. What it was reaching for now lives on the read: a type outside `INLINE_SUFFIXES` is served as `application/octet-stream` with `Content-Disposition: attachment`, and every response carries `default-src 'none'; sandbox`. The paragraph above is right about the pattern and counted three instances; this was the fourth, sitting in the same file.)*

**The pinned virtual-landing mode set earned its keep.** Adding `inbox` broke `test_the_boot_path_does_not_race_a_virtual_landing_mode` immediately — the set is pinned exactly so a new mode has to come to that test and say so, rather than silently inheriting [[ISS-0040]]'s race.

## Correction (ISS-0060) — drop never worked

Edwin, minutes after it shipped: *"drop anything there especially screenshots and images but that doesn't seem to work."*

**Electron 32 removed `File.path`.** The handler read it, got `undefined`, and returned — no error, no status, nothing in the console. Confirmed live in the app. That broke dropping a screenshot *and* dropping a `.md` to navigate, the second of which had been silently dead since the Electron upgrade because nothing checks it.

Fixed with `webUtils.getPathForFile`, which must be called in the **preload** — `webUtils` is not exposed to the renderer. And the path is now **optional**: filing needs the file's bytes, not its location, so requiring one for something that never needed it is what made this fail closed and silent.

**How I missed it:** I tested the store endpoint over HTTP and tested *paste* in the app with a synthetic `ClipboardEvent`. I never dispatched a `drop`. That is verifying the thing next to the thing that was asked for — the fifth instance today of the same failure ([[ISS-0043]], [[ISS-0046]], [[ISS-0047]], [[ISS-0058]]).

## Screenshot capture

`screencapture -i` straight into the project's inbox: the same drag-select as `⌘⇧4`, but the file lands in the project rather than on the Desktop. The step it removes is not the capture, it is the filing afterwards.

Its first version had a defect worth recording. It reported **any** missing file as `cancelled`, because `screencapture` exits 0 when the user presses Escape. But it exits **non-zero with a message** when it genuinely fails — verified: `could not create image from rect`, exit 1. So a macOS Screen Recording denial, the first thing anyone hits on a new machine, would have said the user cancelled something they never started. Three outcomes now, and the error names the permission and where to grant it.

## Notes

**This is the first endpoint that writes a file the user supplies.** Everything else writes notes through `note_writes.py`, which is a field allow-list on files that already exist. A binary write to a new path is a different risk, and the DoD's guard rule is [[ISS-0056]]'s three clauses, learned across four rewrites of one test.

The surfacing half is not decoration. On this surface, four defects this month were "a thing existed and nothing pointed at it" — and an inbox whose whole purpose is to be emptied fails completely if nobody can see it filling.
