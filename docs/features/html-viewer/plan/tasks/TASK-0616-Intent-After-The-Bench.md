---
type: "[[task]]"
id: TASK-0616
aliases: ["TASK-0616"]
title: "The Intent landing keeps leading a reader to every design once there is no bench for its rows to open"
status: done
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

- [x] Every design in the repo is reachable from the Intent landing, as it is today.
- [x] A design row opens the design's **note**. A design that has an HTML page shows a way into the viewer from the note, not from the row.
- [x] Nothing on Intent is gated on a design having an `asset:` — a markdown-only design is a first-class row.
- [x] Intent's badge count still counts what it says it counts ([[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]] is the precedent for getting this wrong).
- [x] `/api/cockpit/designs` survives as the register — it is what builds these rows, and only the endpoints named in [[TASK-0615-Remove-The-Bench]] go.

## Steps

- [x] Find the Intent design rows (`desktop/src/renderer/renderer.ts`, the `intent` mode; `design: 'intent'` around line 4460 maps the old mode name).
- [x] Re-point, do not redesign. Intent's shape is [[FEAT-0043-Design-Top-Level-Surface]]'s and is not in question here.

## Notes

This lands **before** the removal so that designs are never unreachable, not even for one commit.

## Outcome (2026-09-12)

Two lines of behaviour and one of vocabulary.

**Every design row opens the design's note.** It used to branch: an owed design opened its note, where `Accept` is, and every other opened the bench. With the bench gone, the branch collapses — and it collapses in the direction FEAT-0092's criterion wanted, since now *every* row lands where the verbs are rather than only the owed ones. A design with a page offers it from the note's banner, so there is one place that knows where a design's page is instead of two that can disagree.

**`designShape` stopped reporting the normal shape as a lack.** It said `no artifact` for a design with no HTML page, which since [[REQ-0065-A-Design-Is-Markdown-First]] is the recommended form. A design is now described by what it has: `in the note`, `note and page`, or `page missing` — the third being a case the old wording hid behind the same apology as the first.

**Nothing else moved.** `/api/cockpit/designs` still builds the rows, the live/settled fold is untouched, and `owedIds` still marks the rows it always did; it simply no longer decides where a click goes.

Checked in the renderer harness on the built renderer: your-health's three designs listed with their new shapes, a click on DES-0002 landing on `designs/DES-0002-Recovery-And-Food.md`, this repo's twelve designs listed, and the landing still leading with what needs a person ("1 needs you here. DECIDE 1 ADR…").
