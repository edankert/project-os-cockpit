---
type: "[[issue]]"
id: ISS-0076
aliases: ["ISS-0076"]
title: "The overview's Phases section shows each phase's title and never its ID, so the one place that lists every phase cannot be cross-referenced with anything that names them"
status: fixed
severity: low
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'I meant the phase ID next to the phase title'"]
component: desktop-renderer
related: ["[[FEAT-0040-Overview-Rework]]"]
fixed_by: ["[[PHASE-019-Overview-Legibility]]"]
tests: []
---

# Phase rows do not show their phase ID

## What

The overview's Phases section renders each row as title, status, progress:

```
Downstream pilot        planned   0/1 · 0%
MVP                     done      8/8 · 100%
Project-os adapter      done      49/49 · 100%
```

`buildPhaseRow` already **has** the ID — `p.key` is `PHASE-003`, and it is used to route the title click to `~overview/PHASE-003` and to decide whether the row is drillable at all. It is simply never rendered.

## Why it matters more than a label usually would

Everything that *refers* to a phase refers to it by ID. `SNAPSHOT.yaml`'s `focus.phase` is `PHASE-018`. Every note's frontmatter carries `phase: "[[PHASE-013-Fleet-Surfaces]]"`. `docs/PHASES.md` is a table keyed on ID. The overview's own focus band shows `PHASE-018`.

So the Phases section is the one surface listing **every** phase, and the only one that cannot be matched against any of those without knowing the titles by heart.

## Expected

The ID sits beside the title, the way the focus band already shows it.

## Next Actions

- [x] Render `p.key` beside the title when it is a `PHASE-*`
- [x] Leave the sentinel and any non-`PHASE-*` key alone — the row guards on that shape already


## Fixed 2026-07-30

```
PHASE-019  Overview legibility — the page names what it is showing   active   (no items)
PHASE-003  Downstream pilot                                          planned  0/1 · 0%
PHASE-999  Future / Unphased                                         planned  0/3 · 0%
PHASE-001  MVP                                                       done     8/8 · 100%
```

All 20 rows, including the collapsed *Completed* group. Quiet styling — the title is what a person reads, the ID is what everything else refers to it by, so it is a cross-reference rather than a headline.

Guarded, and mutation-verified by dropping the class.

### A non-bug I nearly fixed

The first measurement showed the completed rows rendering `PHASE-001MVP` with a **0px** gap while open rows had 10px. It looked like an `.is-complete` override collapsing the spacing.

It was not. Completed phases live inside `.ov-completed-body[hidden]`, which is `display: none`, so every child measured zero and `innerText` fell back to `textContent` — which concatenates without separators. Expanding the section first: **10px on completed rows too**, identical to the rest.

Worth recording because the fix would have been plausible, small, and entirely wrong — a CSS rule to solve a measurement artefact. Measuring a hidden element and believing the numbers is its own failure mode.

### What this replaced

An earlier attempt put IDs on the phase strip's *feature groups*. Edwin reverted it on sight — wrong surface. That version is gone; nothing of it survives except this note recording that [[DES-0004]] spent the square's budget on state deliberately, and [[ISS-0068]] deleted a list for restating what the squares already draw.
