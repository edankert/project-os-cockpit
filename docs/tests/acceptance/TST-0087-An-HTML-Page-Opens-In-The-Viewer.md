---
type: "[[test]]"
id: TST-0087
aliases: ["TST-0087"]
title: "An HTML page opens in the viewer, whatever kind of note references it, and nothing that mattered about the bench was lost silently"
status: active
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[FEAT-0148-One-HTML-Viewer]]"]
scope: feature
level: acceptance
entrypoint: ""
command: ""
last_verified: ""
covers: ["[[FEAT-0148-One-HTML-Viewer]]"]
issues: []
tasks: ["[[TASK-0613-A-Generic-HTML-Viewer]]", "[[TASK-0614-Links-Stop-Asking-For-The-Bench]]", "[[TASK-0615-Remove-The-Bench]]", "[[TASK-0616-Intent-After-The-Bench]]", "[[TASK-0617-Register-And-Deck]]"]
artifacts: []
last_run: ""
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]", "[[ADR-0042-What-May-Be-Framed]]", "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]", "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]", "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"]
tier: "1"
area: "the viewer"
tags: [test, acceptance, render]
---

<!-- `issues:` is empty on purpose: a check that names an ISS-* reads as a
     regression check ("this defect was fixed"), and this is a behaviour claim
     about a new surface. The issues this walk happens to close are in
     `related:` instead (ADR-0039 decision 4, `acceptance.section_of`). -->

# An HTML page opens in the viewer

## Purpose

Check that the replacement works and that the removal took nothing with it that a reader needed. Walked in the running desktop app; steps that were walked in a harness must say so.

## Procedure

1. Open a design that has an HTML page. **It opens in the viewer, framed, at the right width, in the current theme.**
2. From the viewer, get back to the note. **One click, and the note's ID is visible from the viewer.**
3. Reference an HTML page from a note that is **not** a design — a reference note, say. Open it. **It opens in the same viewer.**
4. Open a design with no HTML page — `DES-0003-Intent-Page-And-Claims-Board`. **Its note opens, with its content. No sentence tells you there is nothing to render.** (This is [[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]].)
5. Open `project-os-deck` DES-0002, which carries 10 `## Revisions` entries and 12 region-anchored comments. **Both sections read in the note, in full.**
5b. On a design note, press **Accept**, then on another press **Decline**. **Both work, from the note, like any other type** — this is what Edwin corrected the plan to protect. Check the frontmatter afterwards: the verdict is written and **`design_revision` is not** ([[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]).
5c. Open this repo's DES-0002, DES-0004 and DES-0009. **Each still carries the `design_revision` it had.** Nothing rewrote them.
6. Open the Intent landing. **Every design in the repo has a row, including ones with no HTML page. A row opens the note.**
7. Click a `cockpit://` link naming a design's ID, from another project. **It opens the design's note** — like every other ID, with no special case (Edwin, 2026-09-12). Same for a cross-repo `[[project#ID]]` link, and for either parked across a project switch.
8. Request each of the eight removed endpoints. **404 on all eight.**
9. Frame a page that lives in **another workspace** the shell has open. **It renders**, served by that workspace's own sidecar. Then request a path with `..` in it. **Refused.** Then read the frame's `sandbox` attribute. **No `allow-same-origin`** — that is the only boundary now ([[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]).
10. Run every detection command in `docs/reference/cockpit-capability-register.md`. **Each row's command does what its row says.**

## Evidence

Per step: date, window or browser, what was on screen. Step 8 is a `curl` and its output goes in the ledger verbatim.
