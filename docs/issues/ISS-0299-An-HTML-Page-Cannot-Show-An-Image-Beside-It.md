---
type: "[[issue]]"
id: ISS-0299
aliases: ["ISS-0299"]
title: "A design's HTML page cannot show an image stored beside it, so pictures get pasted in as base64 and one page reached 4.6 MB"
status: open
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12"]
severity: medium
component: sidecar-routes
parent: "[[FEAT-0147-Pictures-Beside-The-Note]]"
related:
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"
  - "[[FEAT-0042-Design-Bench]]"
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [issue, design, images]
---

# An HTML page cannot show an image beside it

A design's HTML page is served by a route that only hands out files a design note claims in its `asset:`. An image sitting in the same folder is not claimed by anything, so `<img src="photo.png">` inside the page returns 404. The only way to get a picture into the page is to paste it in as base64 text, and that is what has happened: `your-health`'s `DES-0002-recovery-and-food.html` is 4,607,604 bytes, of which 51 are inline PNGs.

> [!quote] As reported — 2026-09-12 (user:edwin)
> why embed the images, why not simply store the images on disk, also in most situations you would need an image to represent a design you cannot mock this up with a styled html file (although I do think styled html can be really useful), these images then should be quite straight forward to incorporate in the .md files.

## Repro

1. Put `shot.png` in `docs/designs/` beside a design note's HTML artifact.
2. Reference it from the artifact: `<img src="shot.png">`.
3. Open the design in the cockpit.
4. `GET /design-asset/designs/shot.png` returns 404.

## Expected

An HTML page in the record can reference a file that sits beside it, so a picture is a file on disk rather than a wall of base64 inside a document.

## Actual

`_serve_design_asset` (`src/project_os_cockpit/server.py:3375`) builds the set of files it will serve from `designs_payload(index)` — every design note's `asset:`, and nothing else. Anything not in that set is 404. The comment above it states the reason: *"Serving any file under docs/ by path would turn a render surface into a file browser."* Checked on 2026-09-12, that reason does not hold — `/docs/<rel>` (`server.py:4233`) has served every file under `docs/` by path, with no gate, for months, on a socket bound to `0.0.0.0`. So the allowlist was not protecting the files; it was deciding which of them the cockpit would present. [[ADR-0042-What-May-Be-Framed]] drops it.

## Evidence

- `src/project_os_cockpit/server.py:3375-3390` — the `claimed` set and the 404.
- `ls -la /Users/Edwin/Dev/repos/your-health/docs/designs/DES-0002-recovery-and-food.html` → 4607604 bytes, measured 2026-09-12.
- `grep -o "data:image/png;base64" …DES-0002-recovery-and-food.html | wc -l` → 51, measured 2026-09-12.
- Zero design artifacts in the fleet reference a relative image file; `find /Users/Edwin/Dev/repos -type d -name "__attachments__"` returns nothing, so the attachment convention `index.py:49` already accepts has never been used.
- `your-health` keeps 71 images under `docs/design/widgets-v2/` as plain siblings with no note claiming them (measured 2026-09-12), so the pattern people actually reach for is already "files on disk" — the cockpit just cannot show them from a page.

## Sibling search

No sibling found (searched `docs/issues/` for: image, asset, base64, embed, attachment, design-asset). [[ISS-0041-Artifactless-Design-Is-Unreadable]] is adjacent — a design with *no* artifact was unreachable — but it is about the note, not about what a page may reference.

## Next Actions

- [ ] [[ADR-0042-What-May-Be-Framed]] is accepted: any file inside the workspace's `docs/`, cross-repo included, with the sandbox as the boundary.
- [ ] [[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]] implements it.
- [ ] [[TASK-0612-Convert-The-Largest-Embedded-Artifact]] converts `your-health` DES-0002 as the proof.
