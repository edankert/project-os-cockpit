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
last_verified: ""
covers: ["[[FEAT-0147-Pictures-Beside-The-Note]]"]
issues: ["[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"]
tasks: ["[[TASK-0608-Pin-Image-Resolution-To-The-Note]]", "[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]", "[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]", "[[TASK-0611-Upstream-The-Markdown-First-Contract]]", "[[TASK-0612-Convert-The-Largest-Embedded-Artifact]]"]
artifacts: []
last_run: ""
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]", "[[REQ-0065-A-Design-Is-Markdown-First]]"]
tier: "1"
area: "notes and attachments"
tags: [test, acceptance, images]
---

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
