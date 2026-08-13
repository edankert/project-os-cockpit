---
type: "[[issue]]"
id: ISS-0136
aliases: ["ISS-0136"]
title: "Five of nine committed design artifacts hard-code a dark palette, so a design read in a light cockpit renders in the wrong theme"
status: "fixed"
severity: low
owner: user:edwin
created: 2026-08-11
updated: "2026-08-13"
phase: "[[PHASE-025-Design-Before-Code]]"
features: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
tasks: []
related: ["[[DES-0009-The-Standing-Worker]]", "[[DES-0010-Desk-Shows-What-It-Owes]]", "[[REL-0001-The-Human-Has-Levers]]", "[[DES-0002]]", "[[PHASE-025-Design-Before-Code]]"]
tags: [issue, design, theming]
---

# Five design artifacts are dark-only

## What was observed

Walking [[REL-0001]]'s acceptance check *"a design renders its artifact… in this project's own tokens, in both light and dark"* on 2026-08-11: the cockpit frame re-themes correctly and [[DES-0010]] round-trips both ways, but switching the app to light leaves several artifacts rendering dark inside a light pane.

Measured across `docs/designs/*.html` — nine committed artifacts, of which **five declare a single dark palette** in `:root` and never mention `prefers-color-scheme` or `data-theme`:

| artifact | theme |
|---|---|
| DES-0002-style-guide.html | aware |
| DES-0004-attention-in-the-squares.html | aware |
| DES-0005-actuator-grammar.html | **dark only** |
| DES-0006-acceptance-desk.html | **dark only** |
| DES-0007-bench-closes-the-loop.html | **dark only** |
| DES-0008-returning-human.html | **dark only** |
| DES-0009-standing-worker.html | **dark only** |
| DES-0010-desk-shows-what-it-owes.html | aware |
| overview-redesign-dossier.html | aware |

## Why it is `low` and not lower

It is cosmetic and it is also exactly the surface whose job is to show what something will look like. A design artifact read in the wrong theme misreports contrast, which is the one thing a reader is looking at it to judge. The four that are aware prove the cost is a `@media (prefers-color-scheme: dark)` block, not a rewrite.

## The constraint that shapes the fix

**[[DES-0009]] must not be edited.** Its `design_revision: 31eac79` is the revision Edwin's acceptance is pinned to, and the whole point of that field is that a verdict given to one revision cannot silently cover another. Fixing its palette moves the sha out from under an accepted design. Either it stays as accepted and dark, or the fix is a **new revision offered for review** — which is the mechanism working, not an obstacle to it.

The other four carry no such pin and can be corrected directly.

## Why it is parked under [[PHASE-999]] rather than [[PHASE-025]]

The design bench phase is `done`, and filing this against it would reopen a closed phase for a cosmetic defect — `PHASE-CHILDREN` said so within a minute of the note being written. `CLAUDE.md`: *"do not open one for a single request, a single issue."* So it sits in the sentinel until somebody schedules it, and PHASE-025 stays in `related:` as where it came from.

## Where the palette should come from

[[DES-0002]] is the style guide and is itself theme-aware. The right fix is one shared token block the artifacts include rather than four hand-copied palettes — otherwise this recurs with the next artifact, which is how it got to five.

## Closed — 2026-08-13: five of nine is now one of ten, and that one is superseded

Re-measured across every committed artifact, counting `:root` colour declarations and light-mode guards:

| artifact | colour tokens | light-mode guard |
|---|---|---|
| `DES-0004-attention-in-the-squares` | 27 | **yes** |
| `DES-0010-desk-shows-what-it-owes` | 32 | **no** |
| the other eight | 0 | — |

So eight of ten declare no palette at all, `DES-0004` declares one and adapts, and a single artifact still hard-codes a dark scheme: **`DES-0010`, whose design is `superseded`** — the board it proposed for `~review` was retired by [[ADR-0020]] before anything was built from it.

The newest artifact, [[DES-0011]]'s, declares no palette by construction: it links the implementation's own `renderer.css` through `/_shell/`, so there is nothing to drift. That is the pattern this issue was arguing for, now demonstrated rather than proposed.

Closed on the measurement. If a superseded artifact rendering dark in light mode is still worth an hour, it wants a fresh note against `DES-0010` rather than this one, which was filed about a fleet-wide habit that no longer exists.

**Re-homed out of [[PHASE-999]] on closing — and nothing "delivered" this one.** It dissolved: the habit it described stopped happening, and the newest artifact demonstrates the alternative by construction. [[PHASE-025]] is where design artifacts became governed records, so it is where the record of a design-artifact convention belongs — not because that phase fixed this, but because a fixed issue in the parking lot renders as unplanned shipped work on the phase strip, and this is the phase whose subject it shares.
