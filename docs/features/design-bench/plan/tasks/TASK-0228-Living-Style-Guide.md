---
type: "[[task]]"
id: TASK-0228
aliases: ["TASK-0228"]
title: "The living style guide — DES-0002's artifact, read from the real CSS"
status: done
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

- [x] No colour, size or spacing value is typed into the page — every one is read from a live stylesheet — evidence: the page enumerates custom properties from `document.styleSheets` and renders each swatch from its computed value; 106 swatches, 0 unresolved, measured in a browser
- [x] Both schemes render, side by side rather than behind a toggle, since the note's claim is that dark is *designed* rather than inverted — evidence: light and dark probes, no toggle; verified `--bg` light `#f7f7f8` / dark `#1b1d1f`
- [x] The status bands and the severity ramp are adjacent, so the do-not-reuse rule is visible — evidence: four panels in one row (status light/dark, severity light/dark)
- [x] Every widget in DES-0002's table appears, in the states that must be distinct without colour — evidence: 7 status chips (one per band, taken from the CSS), rail dots, stat tile, list row, empty-state card
- [x] The two recorded gaps (no type scale, no spacing scale) are stated on the page, with the measured reality beside them — evidence: both rendered as callouts beside the live measurements
- [x] With the shell stylesheet unavailable (mode-1), the page says the widget section needs the desktop shell instead of rendering unstyled markup — evidence: `shellPresent` gates the gallery; the degraded branch states why rather than rendering unstyled markup
- [x] Renders inside the design bench at the declared 900px viewport — evidence: `viewport: 900` on DES-0002; served at `/design-asset/designs/DES-0002-style-guide.html` (200)
- [x] DES-0002 gains `asset:` and leaves `draft`; its Conformance section is updated to say why token parity is now vacuous for it — evidence: `asset: "DES-0002-style-guide.html"`, `status: implemented`; Conformance rewritten to say why token parity is vacuous for the artifact and what it still guards
- [x] Verified in `desktop/harness/design-harness.html` against the real bundle — measured, not asserted — evidence: measured in a real browser against the sidecar serving all three stylesheets

## Steps

- [x] Enumerate custom properties from `document.styleSheets` and render swatches from computed values
- [x] Compose the widget gallery using the shell's real class names
- [x] State the two gaps with their measurements
- [x] Degrade honestly when the shell stylesheet is absent
- [x] Update DES-0002 (`asset`, `status`, Conformance)

## Result

**It found something on its first render**, which is the whole argument for reading the implementation rather than restating it: `renderer.css` redefines **10 tokens** over `base.css` — `--bg` and `--border` with different values, and a parallel vocabulary (`--fg`, `--fg-muted`, `--fg-faint`, `--accent`) for roles `base.css` already names. DES-0002's palette table documents `base.css`; the desktop app draws with `renderer.css`. Filed as [[ISS-0042]] and flagged in the note. A hand-typed swatch page would have reproduced the table and shown nothing.

Band **membership** is read from CSS too — `base.css` states it as `.status-chip[data-status="x"] { color: var(--status-y) }`, so the page reports *43 statuses across 6 bands* without a list existing anywhere in it.

Three defects fixed during verification, all found by rendering rather than reading:

- `const top` is a **SyntaxError** — `top` is a non-configurable `window` property, so the whole script died silently. `node --check` passed it, because Node has no `window`. The page now carries that warning where the name was, and the audit that found it checks every top-level declaration against the window namespace.
- `0px` topped the spacing distribution at **154 uses** — a reset, not a spacing decision, saying nothing about density. Excluded.
- Three tokens (`--nav-width`, `--right-width`, `--pane-header-height`) are declared on components rather than `:root`, so they do not resolve against a page-level probe. They are **named as scoped** rather than rendered as six broken swatches.

The spacing figures differ from the prose in DES-0002 because the page counts through the CSSOM (shorthands expanded, resets excluded) while the note quoted a text count. The page's number is the live one; the note's is a snapshot, which is exactly the asymmetry this task existed to create.

## Notes

**Use the real class names, not lookalikes.** A gallery that reimplements a chip is a fifth restatement wearing a different hat: it would keep looking right while the real chip changed. The markup is necessarily approximate — it is composed here rather than built by `renderer.ts` — and that limit belongs on the page, honestly stated, rather than hidden.

The widget section is the part worth the most care. Five components whose stated property is *"distinguishable without colour"* is a claim this page can either prove or expose, and exposing it would be a genuinely useful result.
