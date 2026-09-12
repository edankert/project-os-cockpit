---
type: "[[issue]]"
id: ISS-0300
aliases: ["ISS-0300"]
title: "A design with no HTML page is told it 'declares no artifact yet — nothing to render', which will be the wrong message once Markdown is the default"
status: fixed
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12"]
severity: low
component: desktop-renderer
parent: "[[FEAT-0148-One-HTML-Viewer]]"
related:
  - "[[ISS-0041-Artifactless-Design-Is-Unreadable]]"
  - "[[REQ-0065-A-Design-Is-Markdown-First]]"
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [issue, design, wording]
---

# A design with no HTML page is told it has nothing to show

The design bench greets a design that carries no HTML artifact with `DES-0003 declares no artifact yet — nothing to render.` That sentence reads the absence of an HTML file as an unfinished design. Once Markdown with pictures is the normal way to present a design, the sentence is describing the common case as a gap — and the note it refuses to render may be complete, illustrated and accepted.

> [!quote] As reported — 2026-09-12 (user:edwin)
> Can we make showing these designs in .md files the default solution and only if we need more do we show these as html files?

## Repro

1. Open a design note that declares no `asset:` and no `## Variant` section — for example `DES-0003-Intent-Page-And-Claims-Board`.
2. The bench shows the sentence above, plus a `Read DES-0003 as a note` button.

## Expected

A design that is fully expressed in Markdown is shown, not apologised for.

## Actual

`desktop/src/renderer/renderer.ts:5669` sets the text. The button beside it was added by [[ISS-0041-Artifactless-Design-Is-Unreadable]] precisely because the empty state was a dead end, which is the same defect seen a year earlier and patched rather than fixed.

## Expected resolution

This is fixed by removal, not by rewording. When the bench goes ([[TASK-0615-Remove-The-Bench]]) a markdown-only design opens its note, which is where its content already is, and the empty state has no reason to exist. Filed as its own issue because it is a defect a reader can see today and because the removal must be checked against it rather than assumed to cover it.

## Sibling search

Sibling found: [[ISS-0041-Artifactless-Design-Is-Unreadable]], filed 2026-07-28, same surface, same cause — the bench treats "no HTML artifact" as "nothing here". This is the second issue of its kind, which is the harvest trigger in `tools/instructions/DECISIONS.md`. The rule that covers the family is stated in [[REQ-0065-A-Design-Is-Markdown-First]] rather than as a rule-ADR, because the family has exactly one member surface and that surface is being deleted; a rule-ADR governing a domain of one, about to become a domain of none, would be ceremony.

## Next Actions

- [ ] Check the removal against this issue rather than assuming it covers it ([[TASK-0615-Remove-The-Bench]]).

## Fixed (2026-09-12)

A design note with no `asset:` now carries **no banner at all**. Saying "This design has no artifact yet" was telling the reader that the normal, recommended shape was unfinished — and the pictures were usually right above the line saying so.

A design that *does* name a page says "This design has a page as well as this note" and offers to open it in the viewer. A design that names a page which is not there says so, with the path: that case was hidden behind the same apologetic wording before.

Checked in the renderer harness on the built renderer: this repo's DES-0003 (no asset) rendered with `.design-note-banner` absent, `your-health`'s DES-0002 showed the page banner, and its button opened `~view/designs/DES-0002-recovery-and-food.html`.
