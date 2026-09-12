---
type: "[[adr]]"
id: ADR-0043
aliases: ["ADR-0043"]
title: "How a note says 'render this HTML' rather than 'show this HTML as code' — the marker is not the code fence's language slot"
status: proposed
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'I think we should not use the src tag to identify html content, I think we need another tag to do this, I would say other people would have fixed this before, do some research online.'"]
decision: "PROPOSED, not decided. Option 2 — a marker in the fence's info string after the language (```html render) — is the recommendation; Edwin chooses."
context: "A note needs a way to say that a block of HTML is a thing to display, not a thing to read as source. Overloading the language slot (```html) makes every HTML example in every note render, and makes a syntax-highlighting hint carry a rendering instruction."
alternatives:
  - "Overload the language: ```html always renders"
  - "Info-string metadata after the language: ```html render"
  - "A generic directive: ::: render / ```{render}"
  - "Pandoc/Quarto/djot attribute syntax: {.render}"
consequences:
  - "Whatever is chosen becomes a project-os authoring convention, so it is upstream work in docs/__templates__ and tools/skills/"
  - "GitHub, Obsidian and any other Markdown reader must degrade to a readable code block, not to broken text"
supersedes: ""
superseded: ""
related:
  - "[[REQ-0065-A-Design-Is-Markdown-First]]"
  - "[[FEAT-0147-Pictures-Beside-The-Note]]"
  - "[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]"
tags: [adr, markdown, convention]
---

# How a note marks HTML to render

## Context

Once a design is Markdown first, a note sometimes needs to show a small rendered thing inline — a styled component, a state, a fragment of a page — without a separate HTML file. The note needs a way to distinguish *here is HTML to look at* from *here is HTML to read as source*, and the two appear in the same corpus: the cockpit's own notes are full of HTML examples that must stay examples.

The convention this project already has is the wrong shape. `## Variant <name>` makes a **heading's text** load-bearing: rename the heading and the render disappears. It is used on exactly one note fleet-wide (`DES-0009-The-Standing-Worker`), and `chosen_variant:` is set on none of 47 design notes (measured 2026-09-12). A convention with one user is not evidence of anything, so this decision is open rather than a migration.

Edwin's instruction was to look at how others have solved it. Three families exist.

## Options

1. **Overload the language slot — ` ```html ` always renders.** Nothing to invent. It also means every HTML example in every note becomes a live fragment, including examples of markup that is being discussed as text. The instruction to render and the hint for syntax highlighting become the same token, and they are not the same thing. Rejected on the corpus alone: this repo's notes contain HTML samples that must stay samples.

2. **Metadata in the fence's info string, after the language — ` ```html render `.** The info string after the language is free text in CommonMark and every parser hands it to the renderer. This is what Docusaurus does with ` ```jsx live `, and what remark-mdx-code-meta generalises. Degrades perfectly: GitHub, Obsidian and any editor see a fenced `html` block, highlight it as HTML, and ignore the trailing word. Costs: the marker is invisible to anything that does not know it, so a reader in Obsidian sees source where the cockpit shows a rendering.

3. **A generic directive — `:::render` (remark-directive) or ` ```{render} ` (MyST).** The most expressive: attributes, nesting, and one syntax for every future extension rather than a new convention each time. Costs: it is a whole extension to implement and to teach, and the MyST brace-in-the-language form is the variant known to break syntax highlighting on other readers. `:::`-style colon fences avoid that and render acceptably in plain Markdown editors.

4. **Pandoc/Quarto/djot attribute syntax — `{.render key=val}`.** Established and expressive. The brace-as-language form is the one with the known highlighting problem on GitHub; the attribute-block form is fine. Brings a syntax the project uses nowhere else.

## Decision

**Proposed: Option 2.** A marker in the info string after the language. It is the smallest change that keeps the language slot meaning "this is HTML" and adds a separate token meaning "show it". It degrades to a highlighted code block everywhere else, which matters because these notes are read in Obsidian and on GitHub as well as in the cockpit.

Option 3 is the better long-term answer if the project expects more than one kind of embedded thing. That is a real possibility and the reason this ADR is `proposed` rather than `accepted`: if Edwin expects diagrams, tables from data, or embedded views next, the directive pays for itself and Option 2 becomes a second convention to retire later.

The exact word (`render`, `live`, `show`, `preview`) is deliberately not decided here; pick it when the option is picked.

## Ambiguity in the request, recorded rather than resolved

Edwin's sentence was *"we should not use the src tag to identify html content, I think we need another tag to do this"*. It admits two readings and they lead to different work:

- **(a)** the fenced-block reading, above: do not let the fence's language (or an `src`-like attribute) be what says "render me"; use a separate marker. This is the reading this ADR takes, and the one his follow-up — *"other people would have fixed this before, do some research online"* — supports, because the prior art is all about fenced blocks.
- **(b)** a frontmatter reading: do not use the note's `asset:`/`source:` field to identify the HTML belonging to a note; use a differently-named field. That is a smaller change and lands in [[REQ-0065-A-Design-Is-Markdown-First]] instead.

Reading (a) is built. If (b) was meant, say so and the field rename moves into the upstream template task, where it is roughly an hour.

## Consequences

- Whatever is chosen is a **project-os authoring convention**, not a cockpit feature, so it lands in `docs/__templates__/design.md` and `tools/skills/design-authoring/SKILL.md` **upstream** in `~/Dev/repos/project-os`, and reaches this repo by sync.
- The renderer that honours the marker is local to the cockpit (`renderer.py` / `renderer.ts`), so the convention exists in the record even in repos whose notes nobody opens in the cockpit.
- `## Variant <name>` should be retired in the same pass. It has one user and it makes a heading's text a functional identifier. Retiring it means deleting the variant strip and `chosen_variant:`, which [[TASK-0615-Remove-The-Bench]] already does.

## Sources

- [remark-directive](https://github.com/remarkjs/remark-directive) — the generic-directive family.
- [MyST roles and directives](https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html) and [MyST directives](https://mystmd.org/guide/directives) — the ` ```{name} ` and `:::` colon-fence forms, and the note that colon fences render correctly in standard Markdown editors.
- Re-verify before implementing: the Docusaurus ` ```jsx live ` precedent and the Pandoc syntax-highlighting issue were researched in the calling session on 2026-09-12 and are **not** re-checked in this note. [[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]] confirms them.
