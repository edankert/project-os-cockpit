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
last_verified: 2026-09-12
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

## Walked 2026-09-12 (model:claude-opus-5)

1. **A design's page opens in the viewer, framed, in the theme** — `~view/designs/WALK-0001-page.html`, header naming the file, chip carrying the path. In the running window; screenshot taken.
2. **One click back to the note.** The viewer's `Read WALK-0001-Walking-The-Pictures` button returned to it. The button appears only when the reader arrived from a note; opened cold the viewer shows none rather than one that goes nowhere.
3. **A note that is not a design frames the same way** *(harness)*. From `TASK-0613`, a **task** note, `~view/designs/DES-0002-style-guide.html` framed the page and the way back read "Read TASK-0613-A-Generic-HTML-Viewer". The viewer reads a path and never asks a note's type; `tests/test_framing.py` fails if it consults the design register. Walked 2026-09-12 after independent review pointed out that this step had been argued from a unit test rather than observed.
4. **A design with no page opens its note with no apology** — DES-0003, 5,541 characters of content and **no banner at all** ([[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]).
5. **`project-os-deck` DES-0002 reads in full** — 10 revision entries and 15 comment lines, in the note, as Markdown.
5b. **Accept and Decline both work from the note** *(harness)*. On a design at `proposed`, Accept wrote `status: "accepted"`; set back to `proposed`, Decline wrote `status: "cancelled"` — the design's own vocabulary, through the generic path.

    **What the note's button writes is the status, and nothing else.** The step's wording asked for "the verdict is written", and the evidence first recorded here reported only a status without saying so. From the note's actuator row a design transitions exactly as an ADR or a task does — `stamp_transition` writes `status` and `updated`. A *verdict* (`reviewed_by`, `review_date`, `review_verdict`) is written by the review desk's decision path, `stamp_decision`, which records `approved` for a design since 2026-09-12. Corrected after independent review found the claim overstated. This is what Edwin corrected the plan to protect, and it was walked on a temporary design rather than a real one.
5c. **The three `design_revision` values are intact**: DES-0002 `6eb6888`, DES-0004 `55a743d`, DES-0009 `31eac79`. Nothing rewrote them.
6. **Every design has a row on Intent** — 13 rows in this repo, one of them a design with no page, and a click opens the note.
7. **A `cockpit://` link naming a design's ID opens the note**: `cockpit://your-health/DES-0002` landed on `designs/DES-0002-Recovery-And-Food.md`.
8. **All nine removed routes 404**, against a freshly started sidecar: the four `/api/design/*`, `/api/notes/choose-variant`, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/design-asset-at/` and `/design-asset/`. `/framed/` and `/api/cockpit/designs` still answer 200.
9. **A page in another workspace frames**, through that workspace's own sidecar; `..` is refused as in TST-0086 step 8; the sandbox has no same-origin flag, pinned by `tests/test_framing.py`.
10. **The register's detection commands were re-run** and found two live remnants, now removed — the note actuator's design-verdict branch and its fetch of `/api/cockpit/design-revisions/`.

**Where each step was walked.** Steps 1, 7 and 8 in the running window and against a real sidecar. Steps 2, 4, 5, 5b, 5c, 6 and 9 in the renderer harness on the built renderer. Step 3 was added to the harness list after the review found it argued rather than walked. **Step 10 is not a surface step**: it is a command sweep over the capability register's own detection commands, run at a shell, and it found two live remnants that the removal had missed. The harness was used because: the window was being driven by two other agent sessions during the walk, which moved it mid-sequence more than once, and a sequence read across a switch is not evidence.

**An unwelcome finding, worth keeping.** The first endpoint sweep reported 200s for routes that had been deleted. The sidecar had been running since before the change and Python never re-imports. Restarting it turned all nine into 404s. A stale sidecar has now produced a false reading twice in this project's history.
