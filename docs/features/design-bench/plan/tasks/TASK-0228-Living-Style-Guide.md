---
type: "[[task]]"
id: TASK-0228
aliases: ["TASK-0228"]
title: "The living style guide — DES-0002's artifact, read from the real CSS"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[DES-0002-Cockpit-Design-System]]", "user decision 2026-07-28"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "L"
depends: ["[[TASK-0227-Expose-Shell-Stylesheet]]"]
blocks: []
related: ["[[ISS-0023-Status-Vocabulary-Drift]]", "[[TST-0019-Status-Vocabulary-Parity]]", "[[TASK-0219-Design-Token-Parity]]", "[[REQ-0022-Overview-State-Above-History]]"]
tests: []
---

# The living style guide

[[DES-0002]] says of itself: *"`status: draft` and `asset: ""` are accurate: the living style-guide page does not exist yet."* This is that page. On landing, DES-0002 gains an `asset:` and can leave `draft`.

## The decision that shapes everything else

**The page reads the real CSS at render time.** It links `base.css`, `cockpit.css` and the shell stylesheet from [[TASK-0227]], enumerates custom properties from the live stylesheets, and renders each swatch from its computed value. No value is ever typed into the page.

Chosen (Edwin, 2026-07-28) over generating the page at build time and over hand-authoring it. The reason is the note's own founding principle — *one vocabulary, one source* ([[ISS-0023]]) — and the arithmetic behind it: the status palette is already stated in `base.css` and its membership in `statuses.py`, kept in agreement by [[TST-0019]]. A hand-typed swatch page would be the **fourth** statement of the same palette, and the one place with no check on it.

Read from the source, drift is not caught — it is **impossible**. That is a stronger property than any test, and it is why [[TASK-0219]]'s token-parity check will report nothing for this artifact: it declares no tokens to diverge.

**The trade-off, recorded because it is real:** revision-compare loses colour fidelity. Comparing an old revision of this page against the working copy renders both against *today's* CSS, so a palette change is invisible in compare. Structural changes still show. Accepted deliberately — the page's job is to be true now, and git already records what `base.css` was.

## What it covers

Everything [[DES-0002]] describes, in the note's own order:

| Section | Shown as | Source |
|---|---|---|
| Principles | Each principle stated with the surface that demonstrates it | prose |
| Palette | Swatches for the 9 semantic tokens, **both schemes side by side** | `base.css` |
| Status & severity | 7 status bands and 4 severity steps, adjacent, so *"do not reuse one family's colour for the other"* is visible rather than asserted | `base.css` |
| Typography | Specimens for sans and mono at 11/12/14, labelled with what each level is *for* | `cockpit.css` |
| Spacing | The measured distribution (8px×29, 6px×29, 14px×26 …) drawn as bars | `cockpit.css` |
| Icons | The mode-strip glyphs, with the rule and a counter-example | `renderer.ts` |
| Widgets | Live status chips, rail dots, stat tile + mix bar, list rows, cards | shell stylesheet |
| Motion | The rail-dot pulse and the ~8s chip decay, running | shell stylesheet |
| Accessibility floor | Focus rings, and every status shown as dot **and** word | all |

**The gaps are content.** The note records that there is no type scale and no spacing scale; the page states both plainly beside the real measurements. An invented scale would be worse than the gap, and DES-0002 argues that explicitly — a section that cannot be checked should say so rather than imply it can.

## Definition of Done

- [ ] No colour, size or spacing value is typed into the page — every one is read from a live stylesheet
- [ ] Both schemes render, side by side rather than behind a toggle, since the note's claim is that dark is *designed* rather than inverted
- [ ] The status bands and the severity ramp are adjacent, so the do-not-reuse rule is visible
- [ ] Every widget in DES-0002's table appears, in the states that must be distinct without colour
- [ ] The two recorded gaps (no type scale, no spacing scale) are stated on the page, with the measured reality beside them
- [ ] With the shell stylesheet unavailable (mode-1), the page says the widget section needs the desktop shell instead of rendering unstyled markup
- [ ] Renders inside the design bench at the declared 900px viewport
- [ ] DES-0002 gains `asset:` and leaves `draft`; its Conformance section is updated to say why token parity is now vacuous for it
- [ ] Verified in `desktop/harness/design-harness.html` against the real bundle — measured, not asserted

## Steps

- [ ] Enumerate custom properties from `document.styleSheets` and render swatches from computed values
- [ ] Compose the widget gallery using the shell's real class names
- [ ] State the two gaps with their measurements
- [ ] Degrade honestly when the shell stylesheet is absent
- [ ] Update DES-0002 (`asset`, `status`, Conformance)

## Notes

**Use the real class names, not lookalikes.** A gallery that reimplements a chip is a fifth restatement wearing a different hat: it would keep looking right while the real chip changed. The markup is necessarily approximate — it is composed here rather than built by `renderer.ts` — and that limit belongs on the page, honestly stated, rather than hidden.

The widget section is the part worth the most care. Five components whose stated property is *"distinguishable without colour"* is a claim this page can either prove or expose, and exposing it would be a genuinely useful result.
