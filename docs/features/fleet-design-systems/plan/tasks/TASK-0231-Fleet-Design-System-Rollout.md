---
type: "[[task]]"
id: TASK-0231
aliases: ["TASK-0231"]
title: "A design system note and living style guide for each project with a UX"
status: doing
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0044-Fleet-Design-Systems]]"]
parent: "[[FEAT-0044-Fleet-Design-Systems]]"
effort: "L"
depends: ["[[TASK-0230-Project-Stylesheet-Route]]"]
blocks: []
related: ["[[DES-0002-Cockpit-Design-System]]"]
tests: []
---

# Roll the design systems out

## Scope

Six projects, seven surfaces — the table in [[FEAT-0044]]. Four have a `draft` note to upgrade; two have nothing.

## Definition of Done

- [x] `edankert.com` and `obsidian-supernote-sync` gain a design note — evidence: `edankert.com@2f6bd10`, `obsidian-supernote-sync@0fecf82`
- [~] The four existing `draft` notes are brought to the same shape — **`your-applications.com` done** (`576b1d4`); **`your-health`, `your-sudoku` and `your-trainer` are blocked** by [[ISS-0059]]: they declare colour in Kotlin and Swift and contain no application CSS, so the route cannot reach them
- [x] Each note declares `stylesheets:` and carries an artifact that reads them — evidence: three notes declare real paths and render from them; `your-applications.com`'s hand-typed palette table was **deleted**, not maintained, and its stale "no single source" claim corrected (the family check has existed since [[ADR-0008]] and exits clean)
- [x] `obsidian-supernote-sync` is **one note, two sections**: the plugin inherits its host's theme tokens, the dashboard owns its palette
- [x] Each note states what its project's system actually is, including the gaps — evidence: the Obsidian plugin's system is that it declares **nothing** and defers to host theme tokens, which the note states as the rule rather than as a gap; the dashboard is Tailwind with two escapes and the note says its palette is mostly unreadable rather than inventing one
- [~] The your-* notes point at the family palette ([[ADR-0008]] upstream in `your-applications.com`) rather than restating its nine values
- [x] Each artifact is verified **rendering in a sandboxed frame**, not by reading it — evidence: edankert.com 64 swatches / 9 declared spacing tokens / 6 measured bars; your-applications.com 26 swatches; obsidian-supernote-sync exactly 2, which is what its two surfaces declare
- [~] Each note leaves `draft` only once its page renders — the three built pages render; the notes stay `draft` until Edwin has looked at them, which is the same bar [[DES-0002]] held itself to, matching what [[DES-0002]] required of itself

## Progress 2026-07-28

**Three of six done**, and the other three are blocked by something the survey could not have seen before the route existed ([[ISS-0059]]): `your-health`, `your-sudoku` and `your-trainer` declare colour in Kotlin and Swift and contain no application CSS. The route is CSS-only by deliberate narrowing, and that narrowing is what keeps it safe.

The survey that scoped [[FEAT-0044]] counted `.css` files per repo and found several in each — all vendored cockpit, venv or test-report noise. **Counting files answered "is there CSS here" when the question was "does this project's UI have CSS".**

**One artifact, copied verbatim.** `docs/__templates__/design-style-guide.html` is the canonical page; everything project-specific arrives at runtime from `stylesheets:`. Six hand-written pages would have been six things that drift; six identical copies cannot say different things about the same question.

## Notes

The shape is [[DES-0002]]'s, and so is the discipline: read from the implementation, state the gaps as gaps, and let the page be the checkable thing. Copying its *prose* would be the mistake — each project's principles are its own, and a system nobody follows is worse than none.
