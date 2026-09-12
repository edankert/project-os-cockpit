---
type: "[[test]]"
id: TST-0086
aliases: ["TST-0086"]
title: "A note shows the pictures beside it, and an HTML page shows the pictures beside it"
status: active
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[FEAT-0147-Pictures-Beside-The-Note]]"]
scope: feature
level: acceptance
entrypoint: ""
command: ""
last_verified: 2026-09-12
covers: ["[[FEAT-0147-Pictures-Beside-The-Note]]"]
issues: []
tasks: ["[[TASK-0608-Pin-Image-Resolution-To-The-Note]]", "[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]", "[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]", "[[TASK-0611-Upstream-The-Markdown-First-Contract]]", "[[TASK-0612-Convert-The-Largest-Embedded-Artifact]]"]
artifacts: []
last_run: ""
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]", "[[REQ-0065-A-Design-Is-Markdown-First]]", "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"]
tier: "1"
area: "notes and attachments"
tags: [test, acceptance, images]
---

<!-- `issues:` is empty on purpose: a check that names an ISS-* reads as a
     regression check ("this defect was fixed"), and this is a behaviour claim
     about a new surface. The issues this walk happens to close are in
     `related:` instead (ADR-0039 decision 4, `acceptance.section_of`). -->

# A note shows the pictures beside it

## Purpose

Check the thing Edwin asked for end to end: that an agent can put a picture in front of him by writing a file and a line of Markdown, and that a page in the record can show a picture from disk instead of carrying it as text.

Walked in the running desktop app and in the browser cockpit. A renderer harness does not count for the steps that say "in the window" — that is the gap [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] left behind and it should not be repeated.

## Procedure

1. Put `shot.png` in `docs/designs/__attachments__/` in this repo. Reference it from a design note by relative path, `![](__attachments__/shot.png)`. Open the note in the desktop app. **The picture is shown.**
2. Reference the same file as an Obsidian embed, `![[shot.png]]`. **The picture is shown** — this is the fallback, and it is kept because Obsidian writes this form when you paste an image.
2b. Open the same note **in Obsidian**. **Both references show the picture there too.** This step is why the convention is a relative path.
3. Open the same note in the browser cockpit (`python -m project_os_cockpit <repo>/docs`). **The picture is shown there too.**
4. Put a second `shot.png` in a different feature's folder. Open the first note again. **The near file wins, not the other one.**
5. Create a design note with no `asset:` and a status past `draft`. Run `bash tools/scripts/validate-docs.sh`. **No `DESIGN-ASSET` error.**
6. Open an HTML page in the record that carries `<img src="beside.png">` with `beside.png` next to it. **The image loads.**
7. Reference an image three directories down from the page, and one in a sibling folder. **Both load.** There is no depth limit and no allowlist ([[ADR-0042-What-May-Be-Framed]]).
8. Request `../../../etc/passwd` and a path with `..` in it from the frame. **Refused — outside `docs_root`.** This and the sandbox assertion are the only boundaries left, so they are the ones that get walked.
9. Open `your-health` DES-0002 after [[TASK-0612-Convert-The-Largest-Embedded-Artifact]]. **It looks the same as before, and `ls -la` shows the page under 100 KB.**
10. *(Blocked on [[ADR-0043-How-A-Note-Marks-HTML-To-Render]], which is still open with Edwin as of 2026-09-12.)* Put HTML in a note and check that it displays the way the settled ADR says, in the cockpit **and** in Obsidian. The first draft of this step assumed a fenced marker; the research since says that would render in the cockpit and show as source in Obsidian, which Edwin rejected. Rewrite this step with the ADR.

## Evidence

Record for each step: the date, whether it was the window or the browser, and what was on screen. A step walked in a harness says so.

## Walked 2026-09-12 (model:claude-opus-5)

**Venue, per step.** Steps 1, 2, 4, 5, 6, 7, 8, 9 and 10 were walked in the **running window**, restarted by pid onto the build under test; step 3 (the browser front door) was **not walked at all** and is recorded below as a gap. Nothing in this walk was re-done in the harness — the closing paragraph about the harness belongs to TST-0087, and saying it here was wrong.

The window walk used with a temporary design note (`WALK-0001`) carrying pictures in `docs/designs/__attachments__/`. The note and its files were deleted after the walk; what they proved is below.

1. **A picture in `__attachments__` by relative path** — shown, `naturalWidth` 240, served from `/docs/designs/__attachments__/WALK-shot.png`.
2. **The same file as an Obsidian embed `![[WALK-shot.png]]`**, and as a bare filename — both resolved to the same file. Three forms, one picture.
3. Not re-walked in the browser front door: the render path is the sidecar's and is the same code the window fetches. Recorded as a gap rather than claimed.
4. **The near file wins.** A second `WALK-shot.png` in `docs/features/html-viewer/__attachments__/` did not win against the one beside the note.
5. **No `DESIGN-ASSET` error** for `WALK-0001`, which sat at `proposed` with no `asset:` — the case that used to fail CI in every repo.
6. **A framed page showed a file beside it**: `~view/designs/WALK-0001-page.html` rendered both images, one from `__attachments__/` and one three directories down. Screenshot taken.
7. **No depth limit**: `/framed/` returned 200 for the file beside the page, the file three directories down, and one in a sibling feature's folder.
8. **Traversal refused**: `/framed/../../etc/passwd` → 404, and the percent-encoded form → 403.
9. **`your-health` DES-0002 after the conversion**: page 28,145 bytes, its plates loading from `__attachments__/`.
10. **HTML in a note** (ADR-0043): the raw `<div>` rendered, and the fenced ```` ```html ```` block stayed source, in the same note, in the window.

**Step 2b, in Obsidian, is not walked and is owed.** Nothing here drives Obsidian. The claim it would check — that a relative path and an Obsidian embed (the double-bracket form) both show — rests on Obsidian's documented behaviour, and it is the reason the relative path is the written convention.

**The window is shared.** Two other agent sessions drove it during this walk, once switching projects mid-step. Every reading above was taken inline with its action, so a switch between actions could not corrupt one. The multi-action sequences that *were* re-walked in the harness belong to [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]], and that note names them step by step.
