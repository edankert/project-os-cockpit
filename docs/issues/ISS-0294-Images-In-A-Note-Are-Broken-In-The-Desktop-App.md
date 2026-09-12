---
type: "[[issue]]"
id: ISS-0294
aliases: ["ISS-0294"]
title: "Every image in a note body is a broken icon in the desktop app, because the sidecar writes root-relative paths and the window's page is a local file"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-10
updated: 2026-09-10
source: ["Found 2026-09-10 while verifying ISS-0293 with a screenshot of the window: your-health's design note with six mockups opened, and all six images were broken icons"]
severity: high
component: desktop-renderer
parent: ""
related: ["[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names]]"]
tests: []
---

# Images in a note are broken in the desktop app

## Problem

A note that embeds an image shows a broken icon in the desktop app. The same note in a browser shows the image. So a design note, whose mockups are the point of it, cannot be reviewed in the window at all.

## Repro

1. Open your-health in the desktop app.
2. Open `docs/design/recovery-and-food-feedback/README.md`, which embeds six PNGs as `![[1-recovery-legend.png]]` and so on.
3. Every image is a broken icon.

## Expected

The images show, as they do at `http://127.0.0.1:<port>/docs/design/recovery-and-food-feedback/README.md` in a browser.

## Actual

The sidecar renders `<img src="/docs/design/recovery-and-food-feedback/1-recovery-legend.png">`. In a browser that path resolves against the sidecar. In the desktop app the note's HTML is put into `index.html`, which is loaded from `file://`, so the same path resolves to `file:///docs/design/…` and nothing is there. Read from the window through the debugging port: `naturalWidth` is 0 and the resolved `src` is `file:///docs/design/recovery-and-food-feedback/1-recovery-legend.png`.

The window's own content security policy already allows images from `http://127.0.0.1:*`, so the images only need to be pointed at the sidecar.

## Next Actions

- [x] After a note's HTML is put into the doc pane, every image whose `src` starts with a single `/` is pointed at the active sidecar. `pointImagesAtSidecar` runs at all three places that mount a note: the centre pane, a check's procedure text and the review page.
- [x] Seen working in the window: all six mockups load, `naturalWidth` 1233 for each.
- [x] Guarded by `tests/test_desktop_note_mounts.py`, which counts every mount of `data.html` and fails on one that does not rewrite its images. Removing the rewrite from one mount turns it red.
