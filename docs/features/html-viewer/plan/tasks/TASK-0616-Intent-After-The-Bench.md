---
type: "[[task]]"
id: TASK-0616
aliases: ["TASK-0616"]
title: "The Intent landing keeps leading a reader to every design once there is no bench for its rows to open"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"]
parent: "[[FEAT-0148-One-HTML-Viewer]]"
effort: S
depends: ["[[TASK-0613-A-Generic-HTML-Viewer]]"]
blocks: ["[[TASK-0615-Remove-The-Bench]]"]
related: ["[[FEAT-0043-Design-Top-Level-Surface]]", "[[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]"]
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [task, intent]
---

# Intent after the bench

## Definition of Done

- [ ] Every design in the repo is reachable from the Intent landing, as it is today.
- [ ] A design row opens the design's **note**. A design that has an HTML page shows a way into the viewer from the note, not from the row.
- [ ] Nothing on Intent is gated on a design having an `asset:` — a markdown-only design is a first-class row.
- [ ] Intent's badge count still counts what it says it counts ([[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]] is the precedent for getting this wrong).
- [ ] `/api/cockpit/designs` survives as the register — it is what builds these rows, and only the endpoints named in [[TASK-0615-Remove-The-Bench]] go.

## Steps

- [ ] Find the Intent design rows (`desktop/src/renderer/renderer.ts`, the `intent` mode; `design: 'intent'` around line 4460 maps the old mode name).
- [ ] Re-point, do not redesign. Intent's shape is [[FEAT-0043-Design-Top-Level-Surface]]'s and is not in question here.

## Notes

This lands **before** the removal so that designs are never unreachable, not even for one commit.
