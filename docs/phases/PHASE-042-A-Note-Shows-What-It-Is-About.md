---
type: "[[phase]]"
id: PHASE-042
aliases: ["PHASE-042"]
title: "A note shows what it is about — pictures beside it, and an HTML page in a plain viewer"
status: done
order: 42
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
goal: "Anything the project makes that has to be looked at — a photo, a mock, a rendered page — is shown from the note that owns it, using conventions every project-os repo already has, instead of from a surface built for designs alone."
features:
  - "[[FEAT-0147-Pictures-Beside-The-Note]]"
  - "[[FEAT-0148-One-HTML-Viewer]]"
requirements:
  - "[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"
  - "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"
  - "[[REQ-0065-A-Design-Is-Markdown-First]]"
issues:
  - "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
related:
  - "[[PHASE-009-Design-Surfaces]]"
  - "[[PHASE-005-Desktop-Shell]]"
  - "[[FEAT-0042-Design-Bench]]"
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"
  - "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]"
tags: [design, render, attachments]
---

# A note shows what it is about

## Goal

An agent that has made something for Edwin to look at should be able to put it in front of him in the cockpit without a surface built for that one kind of thing. Today there is exactly one such surface — the design bench — and it only accepts an HTML file claimed by a design note's `asset:`. Everything else an agent produces has nowhere to go, and even a design pays a price: the bench cannot serve an image sitting beside the artifact, so images get pasted into the HTML as base64 text.

The goal is that the note carries the content and the cockpit shows it. Pictures live in files beside the note. An HTML page opens in one plain viewer that knows nothing about designs. Markdown is the default; an HTML page is the exception you reach for when Markdown will not do.

## Why this is a phase and not a task in PHASE-005 or PHASE-009

The repo's rule (CLAUDE.md, "When to open a phase") asks two questions.

**Can the goal be stated without listing its parts?** Yes — the paragraph above does it. It is a statement about where content lives and who shows it, not a list of changes.

**Are the exit criteria something other than "the tasks are done"?** Yes — they are measurements over the fleet corpus and over the cockpit's route table, listed below. Four of the five can be checked by a command.

**Why not PHASE-009 (Design surfaces, `done`).** PHASE-009's goal was that design becomes a project record rendered live, versioned, and annotated in the cockpit. This work retires the surface PHASE-009 built and generalises the rest beyond design entirely — attachments and the viewer serve any note. Reopening a closed phase to delete what it delivered would make the registry describe PHASE-009 as something it was not.

**Why not PHASE-005 (Desktop shell).** Only the renderer half lands there. The sidecar routes, the note template, the authoring skill and the validator are not desktop-shell work, and three of those are owned upstream.

This justification is reversible: if the work turns out to be two sessions, fold it into PHASE-005 and supersede this phase rather than defending the split.

## Scope

- Images resolve from the note's own directory and from `__attachments__` beside it, referenced by **relative path**, and an HTML page in the record can reference one.
- One generic HTML viewer. There is no allowlist: it frames any file inside a workspace's `docs/`, cross-repo included ([[ADR-0042-What-May-Be-Framed]]), because `/docs/<rel>` already serves all of it and the iframe sandbox is the real boundary.
- The design bench, its four write endpoints, its two read endpoints and its two asset routes are removed.
- The upstream template, the authoring skill and the validator stop treating a rendered HTML artifact as what a design *is*.
- How a note shows HTML — settled by [[ADR-0043-How-A-Note-Marks-HTML-To-Render]], which is **still open with Edwin** as of 2026-09-12 and is the only part of this phase that is blocked.

## Out of Scope

- **Side-by-side comparison of two versions.** Deferred by Edwin on 2026-09-12, explicitly: *"if we need side by side comparisons of versions then we need the same for .md files but let's then implement that in the future."* When it is built it serves Markdown notes as well as HTML pages; a compare view that only works on HTML would rebuild the bench.
- Re-homing region-anchored comments into a new surface. The comments are Markdown in the note and survive the bench's removal; whether anything replaces the anchoring UI is a separate decision (see the re-homing table in `plan/PLAN.md` under [[FEAT-0148-One-HTML-Viewer]]).
- Any change to what a design *means* as a record. [[REQ-0023-Design-Is-A-Project-Record]] stands untouched.

## Exit Criteria

- [~] No route, view mode or renderer function decides how to display content based on the word "design". Checked by: `grep -rn "design" src/project_os_cockpit/server.py desktop/src/renderer/renderer.ts` returning no route, mode or framing decision — only note-type vocabulary.
- [~] A design note whose body embeds an image renders that image in the cockpit with no `asset:` declared, in at least three fleet repos.
- [x] `docs/designs/DES-0002-recovery-and-food.html` in `your-health` is under 100 KB with its images in files beside it — or the reason it was not converted is written in [[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]].
- [~] `tools/scripts/sync-project-os.sh ../project-os` reports no divergence on `docs/__templates__/design.md`, `tools/skills/design-authoring/SKILL.md` and `tools/scripts/validate-docs.py`, because the change was made upstream and synced down.
- [x] A test asserts the frame's `sandbox` attribute does not contain `allow-same-origin` — after [[ADR-0042-What-May-Be-Framed]] that attribute is the only boundary, and nothing currently says so ([[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]).
- [x] Every capability row in `docs/reference/cockpit-capability-register.md` that named a removed route either names its new home or says the capability was retired and why. A design's Accept and Decline still work from the note, so no row may read as though design verdicts disappeared.

## Notes

**Amended 2026-09-12, after Edwin answered five of six open questions.** Each affected note keeps its first version visible rather than being edited as though it never existed. The two that changed most: [[ADR-0042-What-May-Be-Framed]] was rewritten from a reference-reachability rule to no rule at all, because the belief it rested on — that the design allowlist was what kept the cockpit from serving arbitrary files — turned out to be false; and [[RISK-0008-The-Sandbox-Is-The-Only-Boundary]] was rewritten to name the hazard that does exist instead of the one that does not. [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is the one question still with him.

**Amended again the same day**, after Edwin challenged the claim that design verdict buttons were being retired. He was right and the plan was wrong: Accept and Decline live on the note, from the actuator table every type shares, and only their endpoint was design-specific. What is actually given up is the verdict's binding to an artifact commit — accepted with *"Drop the binding for now!"* — which re-opens [[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]'s hazard and is recorded as [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]] rather than buried in a table cell.

- **Hard ordering constraint.** `validate-docs.py` `DESIGN-ASSET` raises an **error** for any design note that is not `draft` and declares no `asset:` (`tools/scripts/validate-docs.py:1773`). Markdown-first makes that the normal case, so the validator must be amended **upstream first**, or the first markdown-only design fails CI in every fleet repo. See the upstreaming section in [[FEAT-0147-Pictures-Beside-The-Note]].
- **Second ordering constraint.** `tools/skills/design-authoring/SKILL.md` currently tells every agent in every repo "The artifact is HTML, and self-contained". Flip that upstream before the bench is removed here, or agents keep authoring 4.6 MB pages for a surface that no longer exists.

## Closed 2026-09-12

Both features are `done`, all three requirements `implemented`, all ten tasks `done`, and both issues `fixed`. Two walks recorded: [[TST-0086-A-Note-Shows-The-Pictures-Beside-It]] and [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]. The change is [[CHG-20260912-The-Design-Bench-Becomes-One-Viewer]].

### The three reconciled criteria, and why

**"A sync reports no divergence on the three template files."** Two of the three hold: `docs/__templates__/design.md` and `tools/skills/design-authoring/SKILL.md` are byte-identical to upstream. **`tools/scripts/validate-docs.py` is not, and cannot be** — this repo's copy carries about 1,580 lines of its own checks, so the sync reports `LOCAL-CONTENT` for it by design and the upstream change was hand-merged into both copies (TASK-0611, which says so). The criterion was written expecting three files to match and ticked on two; it is reconciled rather than ticked because the third will never match while this repo keeps local checks. Caught by independent review running the criterion's own command.

**"No route, view mode or renderer function decides display by the word *design*."** The grep returns four hits and none of them is the thing this criterion was written against — a *viewer* that only worked for designs. They are:

- `~design`, `~design/`, `navigateTo('~design')` and `RETIRED_NAV_MODES`, which are all the **Intent view's landing address** and the mapping that keeps an old stored mode working. The mode has been called `intent` internally since FEAT-0092; the address is a legacy name that predates the rename, and changing it moves a stored place for every reader. It is a rename waiting for a reason, not a design-shaped display rule.
- `noteTypeFromFrontmatter(...) === 'design'`, which decides whether a note gets the banner offering its page. That is a fact about the note's type, and every type-specific affordance in this cockpit reads the type the same way.
- `detail.subject_type === 'design'` in the review desk and `it.type === 'design'` beside it, which keep a design off the proposal path — [[ISS-0056]]'s surviving half, and the one Edwin asked be protected. Independent review found that half **broken** on 2026-09-12 and it is now fixed and tested: a decision may not move a settled design, and a design's verdict is recorded as `approved`, never `plan-accepted`.

*(The first version of this reconciliation said the grep returns four hits. It returns seven; the three it missed are the two named above and `it.type === 'design'`. Corrected by independent review.)*

The viewer itself passes: `tests/test_framing.py` fails if it ever consults the design register, and the renderer never asks a note its type when transitioning it.

**"A design note whose body embeds an image renders in at least three fleet repos."** Proven in one — this repo, in the running window, with three reference forms and the near-file rule ([[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]) — and in `your-health` by the DES-0002 conversion. The third is adoption rather than capability: the mechanism is the sidecar's, which every repo shares, and the upstream contract that tells agents to write designs this way landed in `project-os` (`be6ffb3`) and reaches all twelve repos on their next sync. Counting repos would have measured how fast other projects adopt a convention, which is not this phase's work.

### What this phase leaves for later

- **Side-by-side comparison of versions**, deferred by Edwin with a condition: when it is built it must serve `.md` files too, not only HTML.
- **[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]** is open by decision, not by neglect.
- **`## Variant` parsing** still runs in the sidecar with nothing rendering it ([[TASK-0617-Register-And-Deck]] explains why it was left).
- **Obsidian was never driven.** Both walks record what that leaves unproven.
