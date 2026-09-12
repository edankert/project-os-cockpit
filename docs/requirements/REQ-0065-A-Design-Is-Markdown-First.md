---
type: "[[requirement]]"
id: REQ-0065
aliases: ["REQ-0065"]
title: "A design is a Markdown note with pictures by default; an HTML page is what an agent reaches for when Markdown will not do, and nothing errors when there is no HTML page"
status: draft
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'Can we make showing these designs in .md files the default solution and only if we need more do we show these as html files?'"]
priority: high
scope: "The authoring contract for designs: the note template, the design-authoring skill, and the validator rule that today requires an HTML artifact. All three are template-owned and change upstream."
acceptance:
  - "[ ] `validate-docs.py` no longer errors on a design note that is not `draft` and declares no `asset:`; the check that replaces DESIGN-ASSET is stated and the change is made in `~/Dev/repos/project-os` — evidence: <upstream path:line>"
  - "[ ] `docs/__templates__/design.md` upstream presents the note's own body, with images, as how a design is normally expressed, and `asset:` as optional — evidence: <upstream path>"
  - "[ ] `tools/skills/design-authoring/SKILL.md` upstream no longer opens with 'The artifact is HTML, and self-contained' as the contract; it says Markdown with pictures first and names when an HTML page is worth it — evidence: <upstream path>"
  - "[ ] HTML inside a note is displayed as [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] settles, and the convention is written into `tools/instructions/OBSIDIAN.md` upstream. STILL OPEN with Edwin as of 2026-09-12 — do not build against this criterion until the ADR is settled — evidence: <test path, upstream path>"
  - "[ ] `tools/scripts/sync-project-os.sh ../project-os` reports no divergence on those three files after the change is synced down — evidence: <command output>"
implements: "[[FEAT-0147-Pictures-Beside-The-Note]]"
verifies: []
related:
  - "[[ADR-0043-How-A-Note-Marks-HTML-To-Render]]"
  - "[[REQ-0023-Design-Is-A-Project-Record]]"
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [requirement, design, upstream]
---

# A design is Markdown first

## Approval

Not yet approved. The criterion to look at hardest is the first, because it is a **hard blocker on everything else in [[PHASE-042-A-Note-Shows-What-It-Is-About]]**, and it changes a gate in every repo in the fleet.

`tools/scripts/validate-docs.py:1773` raises an **error**, not a warning:

> `<ID> is 'proposed' and declares no asset:; a design offered for review needs a rendered artifact (draft is exempt)`

Under the current contract that is correct — a design *was* a rendered artifact, and a note claiming to be reviewable with nothing to review was a real defect. Under markdown-first it is exactly backwards: the first design written the new way fails CI, in this repo and in every repo that syncs the validator. So the validator must be amended upstream **before** any markdown-only design is written, and that is the ordering constraint the phase note records.

What replaces the rule is a decision this requirement asks for rather than assumes. The honest replacement is *"a design that is past `draft` must have something to look at"* — either an `asset:`, or an image reference in its body. That keeps the original intent (nothing is offered for review that shows nothing) without mandating the file type. `DESIGN-ORPHAN`, the warning for an unclaimed `.html` under `docs/designs/`, needs the same look: once pages and images live beside notes, unclaimed files are ordinary.

## Statement

A design **shall** be expressible as a Markdown note with images beside it, with no HTML artifact, and nothing in the template, the authoring skill or the validator **shall** treat that as incomplete. An HTML page **shall** remain available for what Markdown cannot express, and the authoring guidance **shall** say when that is.

## Rationale

Edwin, 2026-09-12: *"Can we make showing these designs in .md files the default solution and only if we need more do we show these as html files? do not consider the actual project produced content yet but having this should allow the llm to present this information in the cockpit if needed."*

There is a second argument he did not have to make, and it is the strongest one. **Obsidian cannot open a standalone `.html` file without a community plugin.** So an HTML page is, by its nature, a cockpit-only artifact: it is invisible in the app Edwin reads these repos in, invisible on GitHub except as source, and readable only while this application exists. A Markdown note with images beside it is readable in all three. That makes markdown-first not merely a convenience but the form that satisfies [[REQ-0023-Design-Is-A-Project-Record]]'s "readable without the tool that renders them" clause, which an HTML artifact only ever satisfied in the weak sense of being a file you could double-click.

The last clause is the point of the whole requirement. What he wants is for an agent to be able to put something in front of him. Markdown with pictures is the form an agent can produce in one file write, that a person can read in Obsidian or on GitHub, that diffs, and that survives this application. An HTML page is none of those — two regenerated pages diff as a wall of noise, which the design-authoring skill already admits.

Three documents currently tell every agent the opposite, and all three are template-owned, so this is upstream work by definition:

- `docs/__templates__/design.md` has `asset:` as a standing field with a `## Regions` section built around `data-design-region`.
- `tools/skills/design-authoring/SKILL.md` has a section headed *"The artifact is HTML, and self-contained"*.
- `tools/scripts/validate-docs.py` errors when there is no artifact.

Leaving any of them unchanged means agents keep authoring for the surface being removed.

## Acceptance Criteria

- [ ] The validator stops requiring an HTML artifact, and what replaces the rule is stated — evidence: <path>
- [ ] The design template presents the note body, with images, as normal — evidence: <path>
- [ ] The authoring skill says Markdown first, and names when HTML is worth it — evidence: <path>
- [ ] HTML in a note is displayed as ADR-0043 settles, and the convention is in OBSIDIAN.md — **open** — evidence: <path>
- [ ] A sync reports no divergence on those files — evidence: <path>

## Traceability

- Implements: [[FEAT-0147-Pictures-Beside-The-Note]]
- Verified by: [[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]
