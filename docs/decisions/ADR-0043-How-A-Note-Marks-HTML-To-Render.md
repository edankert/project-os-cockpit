---
type: "[[adr]]"
id: ADR-0043
aliases: ["ADR-0043"]
title: "A note marks nothing: HTML written plainly in a note is rendered by Obsidian and by the cockpit already, and anything needing images or scripts is a file the viewer frames"
status: accepted
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'I think we should not use the src tag to identify html content, I think we need another tag to do this, I would say other people would have fixed this before, do some research online.'", "Edwin, 2026-09-12, on the constraint: 'using render after the html tag (option 2) is fine as long as it renders as html in obsidian or does nto show at all, we cannot have the source be visible in obsidian that doesn't make any sense.'", "Edwin, 2026-09-12, accepting the researched recommendation: 'q2: agree'"]
decision: "No marker and no new syntax. HTML written plainly in a note is the notation, because Obsidian and the cockpit both render it already. A fenced block stays what it looks like — source shown as source. HTML that needs images or scripts is not written in a note at all: it is a file, and the viewer frames it."
context: "A marker was wanted so a note could say 'render this' rather than 'show this as code'. Edwin's constraint killed every marker: a fenced block renders in the cockpit and shows as SOURCE in Obsidian, which he rejected outright. Research then found the marker unnecessary — Obsidian renders raw HTML natively, as does the cockpit's renderer."
alternatives:
  - "Info-string metadata after the language (```html render), as Docusaurus does with ```jsx live — rejected: shows as source in Obsidian, which is the constraint"
  - "Adopt a community plugin's fence (```html-block, 409 downloads; ```html-preview, 179) — rejected: a fringe dependency every reader must install, and each plugin invents its own tag"
  - "Our own fence plus a small fleet Obsidian plugin via registerMarkdownCodeBlockProcessor — rejected for now: it is the only option that also fixes style isolation, and is the way back if collisions bite"
  - "A generic directive (:::render) or Pandoc attributes ({.render}) — rejected: same source-in-Obsidian problem, more machinery"
consequences:
  - "Four authoring rules come with raw HTML and must be written into OBSIDIAN.md: no blank line inside an HTML block (it breaks the block in Obsidian and in Python-Markdown), no Markdown inside HTML elements (Obsidian does not parse it), scripts never run (Obsidian sanitises, the cockpit CSP blocks), and there is no style isolation — a <style> in a note restyles the page in both apps"
  - "An <img> with a RELATIVE src inside raw HTML does not display in Obsidian: path resolution happens only for wikilinks and Markdown image syntax. So pictures are Markdown embeds, never HTML tags"
  - "HTML with images or scripts belongs in a separate file framed by the viewer — which Obsidian cannot open without a community plugin, making it a cockpit-only artifact by nature"
  - "TASK-0610 changes from building a marker to writing these rules down; no parser or renderer change is needed"
supersedes: ""
superseded: ""
related:
  - "[[REQ-0065-A-Design-Is-Markdown-First]]"
  - "[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"
  - "[[FEAT-0147-Pictures-Beside-The-Note]]"
  - "[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]"
  - "[[ADR-0042-What-May-Be-Framed]]"
tags: [adr, markdown, convention]
---

# A note marks nothing

## Decision

**There is no marker.** HTML written plainly in a note is the notation. A fenced ```` ```html ```` block keeps meaning what it looks like: source, shown as source, in every reader.

Content decides where it lives:

| What it is | Where it goes | Renders in |
| --- | --- | --- |
| A picture | a Markdown embed, `![](__attachments__/plate-3.png)` | Obsidian, the cockpit, GitHub |
| Light structure or styling | raw HTML in the note | Obsidian, the cockpit |
| Anything with images or scripts | a separate `.html` file the viewer frames | the cockpit only |

## Why the marker died

Edwin set the constraint that decided it: *"we cannot have the source be visible in obsidian that doesn't make any sense."* Every marker fails it. A fenced block with metadata after the language — ```` ```html render ````, which is how Docusaurus spells `​```jsx live` — renders in the cockpit and shows as a code block in Obsidian, because nothing in Obsidian knows the word.

Then the research removed the need for one. **Obsidian renders raw HTML in a note natively**; its own help says "Obsidian supports HTML to allow you to display your notes the way you want", sanitising `<script>`. The cockpit's renderer passes raw HTML through in the same way — measured on 2026-09-09 by rendering a `<div>` and a fenced block through `render_markdown_text` and reading the output. Two renderers already agree on a notation. Inventing a third thing for them to disagree about buys nothing.

## The plugins, and why not one of them

Three Obsidian plugins render fenced HTML, and no two agree on the fence:

| Plugin | Fence | Isolation | Downloads |
| --- | --- | --- | --- |
| HTML Blocks | ```` ```html-block ```` | Shadow DOM per block, inline scripts in an isolated scope | 409 |
| HTML-Preview | ```` ```html-preview ```` | sandboxed iframe, `allow-scripts allow-forms` | 179 |
| Polyglot Renderer | its own | sandboxed iframe, scripts blocked | — |

HTML Blocks is the technically strongest: Shadow DOM is real style isolation, which is the one thing raw HTML does not give us. But adopting it means every person and every agent reading any of these repos installs a 409-download plugin, and the convention becomes a stranger's naming decision. The download counts are the argument: these are not standards, they are three parallel attempts at one.

## What comes back if this hurts

The pain this accepts is style collision: a `<style>` block in a note restyles the page around it, in Obsidian and in the cockpit alike. If that bites, the way back is **our own fence plus a small fleet plugin** — `registerMarkdownCodeBlockProcessor` is the documented Obsidian API all three plugins use, and a shadow-DOM renderer for one fence is a small thing to own. It is rejected today for maintenance, not for merit.

## Consequences for the work

[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]] stops being an implementation task. Nothing is parsed and nothing is rendered differently; what the task now does is write four rules into `OBSIDIAN.md` upstream, where an agent will read them:

1. **No blank line inside an HTML block.** Obsidian's help says a blank line breaks the block, and Python-Markdown treats it the same way.
2. **No Markdown inside HTML elements.** Obsidian does not parse it, deliberately.
3. **Scripts never run.** Obsidian sanitises them; the cockpit's CSP (`script-src 'self'`) blocks them.
4. **Pictures are Markdown embeds, never `<img>` tags.** A relative `src` inside raw HTML does not resolve in Obsidian — path resolution happens only for wikilinks and Markdown image syntax — so an HTML-embedded picture is broken in the place these notes are most often read.

Rule 4 also explains the artifact this phase exists to retire: `your-health`'s 4.6 MB design page carries 51 base64 PNGs, and base64 is the only way an image inside raw HTML survives Obsidian.
