---
type: "[[task]]"
id: TASK-0610
aliases: ["TASK-0610"]
title: "A note shows HTML by containing it: no marker, no fenced-block convention, and the four authoring rules written where an agent reads them"
status: done
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


# A note marks nothing

**This task changed shape before it was built, and the note keeps both versions.** It was written to add a marker — a word after the language in a fenced block, so ` ```html render ` would render while ` ```html ` stayed source. [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] rejected every marker after research, on Edwin's constraint: *"we cannot have the source be visible in obsidian that doesn't make any sense."* A fenced block with a marker renders in the cockpit and shows as source in Obsidian, because nothing in Obsidian knows the word.

What replaced it: **nothing to build.** Obsidian renders raw HTML in a note natively, and so does this cockpit's renderer. The two already agree, so the work is to write the rules down and to pin the agreement with tests.

## Definition of Done

- [x] [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is `accepted`, deciding no marker. Edwin: *"q2: agree"*.
- [x] The four authoring rules are in `tools/instructions/OBSIDIAN.md`, upstream, under **HTML in a note** — landed with [[TASK-0611-Upstream-The-Markdown-First-Contract]] and synced down. No blank line inside a block; no Markdown inside elements; scripts never run; pictures are Markdown images, never `<img>` tags.
- [x] A test pins that raw HTML in a note body survives to the rendered output, and that a fenced ` ```html ` block is still shown as source (`tests/test_note_attachments.py`).
- [x] A test pins the cockpit half of the claim: the shell writes the sidecar's HTML into the document unaltered, and the page's CSP blocks inline scripts. ADR-0043 rests on that pair, so a change to either should be loud.
- [x] The style-isolation cost is recorded rather than solved: a `<style>` in a note restyles the page in both applications. The way back, if it bites, is our own fence plus a small fleet Obsidian plugin — ADR-0043 names it and `registerMarkdownCodeBlockProcessor` is the API.

## What was NOT built, from the first version of this task

The marker, a parser change, a renderer change, and the sandboxed fragment. The first version also required the rendered fragment to be *"sandboxed at least as tightly as the current variant strip"* — that requirement disappears with the variant strip itself, which [[TASK-0615-Remove-The-Bench]] removes.

## Notes

Obsidian cannot open a standalone `.html` file without a community plugin, which is the other half of why markdown-first is right: pictures in a note are readable everywhere, and an HTML page is a cockpit-only artifact by nature.
