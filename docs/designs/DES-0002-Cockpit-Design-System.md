---
type: "[[design]]"
id: DES-0002
aliases: ["DES-0002"]
title: "Cockpit design system"
role: system
status: implemented
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["src/project_os_cockpit/static/base.css", "src/project_os_cockpit/static/cockpit.css", "[[DES-0001-Overview-Redesign]]"]
asset: "DES-0002-style-guide.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[DES-0001-Overview-Redesign]]", "[[TST-0019-Status-Vocabulary-Parity]]", "[[ISS-0023-Status-Vocabulary-Drift]]", "[[REQ-0022-Overview-State-Above-History]]"]
---

# Cockpit design system

Values below are **read from the implementation** (`base.css`, `cockpit.css`), not invented. Where the code has no answer, this note says so rather than inventing one — an aspirational system the code does not follow is worse than an honest gap, because it makes the parity check meaningless from day one.

**No `viewport:` — this is a document, not a surface.** It declared `900` before the page existed, describing the height [[REQ-0022]] asserts rather than a width the artifact is drawn at; that made the bench frame a scrolling reference page inside a 900px window and offer device widths for it. Absence is the honest declaration, and the surface reads it: no framing, no viewport chooser, the page simply shown ([[ISS-0045]]).

The living style-guide page is `DES-0002-style-guide.html`, delivered by [[TASK-0228]]. **It reads every value from the real stylesheets as it renders** — `base.css`, `cockpit.css`, and the shell stylesheet exposed by [[TASK-0227]] — so no colour, size or spacing figure is typed into it. Band *membership* is read the same way, from the `[data-status]` rules.

## Principles

- **Quiet-first.** Design for the state the corpus is actually in. Work is bursty and `doing` clears within a session, so the common case is a project with nothing in flight — a surface that only looks good when busy is a surface that usually looks broken.
- **State before history.** Above the fold answers "where is this now", not "what happened". Activity and commits are the only sections allowed to scroll ([[REQ-0022]]).
- **One vocabulary, one source.** Status colour comes from `statuses.py` and reaches CSS through generation, never retyping. This is the project's founding scar ([[ISS-0023]]) and the reason [[TST-0019]] exists.
- **Never colour-alone.** A status is a coloured dot *and* a word. The corpus is read by someone scanning quickly on a tablet across a room; colour is the accelerant, never the message.

## Palette

Semantic roles, defined for both schemes. The cockpit is read in daylight and at night, so dark is a designed scheme rather than an inversion.

| Role | Meaning | Light | Dark |
|---|---|---|---|
| `--bg` | page ground | `hsl(0 0% 99%)` | `hsl(0 0% 11%)` |
| `--surface` | raised panel, card | `hsl(0 0% 96%)` | `hsl(0 0% 14%)` |
| `--border` | hairline separation | `hsl(0 0% 86%)` | — |
| `--border-strong` | deliberate division | `hsl(0 0% 76%)` | — |
| `--text` | primary ink | `hsl(0 0% 13%)` | `hsl(0 0% 87%)` |
| `--text-muted` | secondary ink | `hsl(0 0% 38%)` | `hsl(0 0% 65%)` |
| `--text-faint` | tertiary, metadata | `hsl(0 0% 55%)` | `hsl(0 0% 50%)` |
| `--accent-link` | interactive | `hsl(212 48% 42%)` | — |
| `--accent-focus` | keyboard focus | `hsl(212 60% 50%)` | — |

> **The table above documents `base.css`. The desktop shell draws with `renderer.css`, and they disagree** — `--bg` and `--border` are overridden with different values, and `--text`/`--text-muted`/`--text-faint`/`--accent-link` have parallel names (`--fg`/`--fg-muted`/`--fg-faint`/`--accent`) in the shell. Found by the style-guide page on its first render and recorded as [[ISS-0042]]. Until that is resolved, read this table as the browser cockpit's palette; the page shows what the desktop app actually draws.

**Neutrals are true greys** (`hsl(0 0% n)`), deliberately: the accent is the only chroma on the page, so status colour reads as signal rather than decoration.

### Status and severity — the load-bearing roles

Seven status **bands**, not per-status colours. Membership lives in `statuses.py`; the bands are what CSS knows about, which is why adding a status value never touches a stylesheet.

`--status-active` `hsl(140 32% 38%)` · `--status-pending` `hsl(220 14% 48%)` · `--status-done` `hsl(160 28% 38%)` · `--status-archived` `hsl(0 0% 48%)` · `--status-blocked` `hsl(5 48% 46%)` · `--status-reference` `hsl(180 24% 40%)` · `--status-default` `hsl(0 0% 45%)`

Four severity steps: `critical` `hsl(5 60% 46%)` · `high` `hsl(20 60% 46%)` · `medium` `hsl(45 55% 42%)` · `low` `hsl(0 0% 50%)`.

Severity runs red→orange→amber→grey, a ramp; status bands are categorical hues. **Do not reuse a severity colour for a status band or vice versa** — they answer different questions and a reader who learns one mapping will misread the other.

Dark-scheme lightness rises to 58–65% across both families. That is not an inversion: the same hue at the same lightness on a dark ground reads as murky, so each step was re-picked.

## Typography

- `--font-sans`: the system stack (`-apple-system`, `Segoe UI`, `Roboto`, …). Deliberate — the cockpit should look like the OS it runs in, not like a website. It also means zero font loading, which matters for a tool that renders on every keystroke.
- `--font-mono`: `ui-monospace`, `SF Mono`, `Menlo`. Used for IDs, paths, commands and the terminal — anything the reader might retype.

**No declared type scale.** Sizes are literal `px` in `cockpit.css`, clustering at 11/12/14. That is a gap, recorded rather than papered over. What the levels are *for* is settled even though the scale is not: 14 is body, 12 is secondary, 11 is metadata and chips.

## Spacing & density

**No spacing tokens exist.** Measured in `cockpit.css`: `8px` (29 uses), `6px` (29), `14px` (26), `12px` (18), `11px` (17), `4px` (14), `10px` (14).

That is not a scale, it is a distribution — 6/8/10/12/14 are all in heavy use with no consistent step. Honest reading: the cockpit is dense-by-design and its spacing was tuned per-surface by eye.

`--radius: 4px`, `--radius-lg: 6px` are the only geometry tokens.

**Target viewport: 900px height.** Not a breakpoint — the assertion [[REQ-0022]] makes, that every state section fits above the fold at that height. Measured at 721px for the four state sections, so there is real headroom.

## Icons

The cockpit is **near-iconless by default**, and that is a choice rather than an omission. Status is a coloured dot plus a word; navigation is text; the mode strip is the one place carrying glyphs.

**Rule: an icon may appear without a text label only when it is a persistent control whose position teaches its meaning** — the mode strip, the terminal toggle. Anything appearing conditionally, or in a list, carries a word. A chip is a word with a colour, never a glyph alone.

## Widgets

| Widget | Where | States that must be distinct **without colour** |
|---|---|---|
| status chip | everywhere a note appears | the word itself carries the state; colour is redundant by design |
| rail dot | agent sessions | idle / busy / needs-input / stalled — shape and fill, not hue alone |
| stat tile + mix bar | overview | proportion is length; the label states the fraction numerically |
| list row | nav, queue, remaining | selected / focused / visited — focus ring is `--accent-focus`, never colour-only |
| card | phase, scope, review | has a heading; an empty card states why it is empty rather than rendering blank |

**Empty states are a component, not an absence.** A section with nothing in it says what would appear there — a quiet-first surface is mostly empty, so empty is the *common* case and must read as deliberate.

## Motion

**Almost nothing animates, deliberately.** The exceptions: the rail dot pulses on needs-input, and the nav-row agent chip decays over ~8s.

Both are *attention* signals with a decay, not decoration. The rule: motion is allowed only to say "this changed while you were not looking", and it must stop on its own. A tool read at a glance across a room cannot afford ambient movement competing with the one thing that actually needs a look.

## Accessibility floor

- Status is never colour-alone — a word accompanies every coloured dot or chip.
- Keyboard focus is always visible, via `--accent-focus`, and never removed for aesthetics.
- Both schemes are designed, not derived; contrast is checked against the ground each is used on.
- The `attention` state does not decay ([[REQ-0018]]): something needing a human must not become invisible by waiting.

## Conformance

**Not checked.** [[TASK-0219]]'s parity checker has no caller outside its own tests and is silent by construction, and the claim that it guarded this note was withdrawn on 2026-07-28 ([[ISS-0049]] option 1). The palette table below is **unchecked prose**: it can drift from `base.css`, and nothing will say so.

What *is* guaranteed is stronger and lives elsewhere: the **style-guide page reads its values from the implementation as it renders**, so the swatches cannot drift by construction. Read the page for what the app actually draws; read the table as commentary.

**The artifact declares no tokens, so the parity check reports nothing for it — deliberately.** `design_tokens.py` compares a design's *declared* palette against the implementation, and a design that declares nothing is silent rather than failing. That is the correct outcome here: the page reads its values from the implementation as it renders, so divergence is not caught, it is impossible. A stronger property than the check, and the reason the check has nothing to say.

**Direction of authority is unchanged:** `statuses.py` is upstream. If this note and the implementation disagree, this note is wrong.

**Known limit: revision-compare loses colour fidelity for this artifact.** An old revision and the working copy both render against today's CSS, so a palette change is invisible in compare. Structural changes still show, and git records what `base.css` was. Accepted deliberately — the page's job is to be true now.

**Direction of authority: `statuses.py` is upstream.** If this note and the implementation disagree about a status colour, this note is wrong. That direction is stated because a parity check without one accumulates waivers instead of fixes.

Everything else here — spacing, type scale, icon rules — is currently **descriptive, not enforced**. Two of those sections record gaps (no spacing scale, no type scale) that a future task may close. Recording them as gaps is the point: this note's value is that it can be checked, and a section that cannot be checked yet should say so rather than imply it can.
