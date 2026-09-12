---
type: "[[task]]"
id: TASK-0610
aliases: ["TASK-0610"]
title: "A note marks a block of HTML as something to render, with a marker that is not the code fence's language"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'I think we should not use the src tag to identify html content, I think we need another tag to do this'", "[[ADR-0043-How-A-Note-Marks-HTML-To-Render]]"]
parent: "[[FEAT-0147-Pictures-Beside-The-Note]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0043-How-A-Note-Marks-HTML-To-Render]]", "[[REQ-0065-A-Design-Is-Markdown-First]]"]
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [task, markdown, convention]
---

# A note marks a block of HTML to render

## Blocked, and the answer moved

**Do not start.** [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is with Edwin as of 2026-09-12 and the research changed its recommendation, so this task will be rewritten with it rather than amended.

What changed: Obsidian renders raw HTML in a note **natively**, and the cockpit's renderer passes raw HTML through too. So a fenced ` ```html render ` marker — the first recommendation — would render in the cockpit and show as **source** in Obsidian. Edwin, 2026-09-12: *"we cannot have the source be visible in obsidian that doesn't make any sense."* No core Obsidian plugin renders fenced HTML; the HTML plugins that exist open `.html` files. The likely decision is therefore **no marker at all** — raw HTML is the notation — with four authoring constraints: no blank lines inside an HTML block, no Markdown inside HTML elements, scripts never run, and no style isolation. The Definition of Done below is the *first* version's and is kept only so the change is visible.

## Definition of Done

- [ ] [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is `accepted` with one option chosen by Edwin, and the two prior-art claims it inherits are re-verified first (see Steps).
- [ ] A fenced HTML block carrying the marker renders as a live fragment in the note, in the browser cockpit and in the desktop shell.
- [ ] A fenced HTML block **without** the marker still renders as highlighted source. A test pins this, using one of this repo's existing notes that contains an HTML example.
- [ ] The rendered fragment is sandboxed at least as tightly as the current variant strip: no `allow-same-origin`, and no `allow-scripts` unless the note opts in.
- [ ] The convention is written into the upstream template and skill (rolled into [[TASK-0611-Upstream-The-Markdown-First-Contract]] if that has not landed, otherwise a follow-up upstream commit).

## Steps

- [ ] **Re-verify the research before the ADR is accepted.** The calling session found the prior art; this note does not re-check it. Confirm: Docusaurus's ` ```jsx live ` and remark-mdx-code-meta as the info-string precedent; the Pandoc brace-as-language highlighting problem (pandoc issue 8174). The directive family is confirmed — [remark-directive](https://github.com/remarkjs/remark-directive) and [MyST](https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html), whose colon-fence form renders acceptably in plain Markdown editors.
- [ ] Implement in `src/project_os_cockpit/renderer.py` and whatever the desktop renderer needs.
- [ ] Retire `## Variant <name>`: it makes a heading's text a functional identifier, it has one user fleet-wide, and `chosen_variant:` is set on none of 47 design notes (measured 2026-09-12). The strip itself is deleted by [[TASK-0615-Remove-The-Bench]]; this task removes the convention from the documentation.

## Notes

Independent of the rest of the feature. If it slips, nothing is blocked — which is the argument for doing it last rather than first, and it is now genuinely blocked, which makes that ordering free.
