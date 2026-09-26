---
type: "[[task]]"
id: TASK-0231
aliases: ["TASK-0231"]
title: "A design system note and living style guide for each project with a UX"
status: done
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-30
source: ["[[FEAT-0044-Fleet-Design-Systems]]"]
parent: "[[FEAT-0044-Fleet-Design-Systems]]"
effort: "L"
depends: ["[[TASK-0230-Project-Stylesheet-Route]]"]
blocks: []
related: ["[[DES-0002-Cockpit-Design-System]]"]
tests: []
---

# Roll the design systems out

## Scope

Six projects, seven surfaces — the table in [[FEAT-0044]]. Four have a `draft` note to upgrade; two have nothing.

## Definition of Done

- [x] `edankert.com` and `obsidian-supernote-sync` gain a design note — evidence: `edankert.com@2f6bd10`, `obsidian-supernote-sync@0fecf82`
- [x] The four existing `draft` notes are brought to the same shape — **all four done**. `your-applications.com` (`576b1d4`); the other three 2026-07-30 once [[ISS-0059]]'s read-time synthesis unblocked them
- [x] Each note declares `stylesheets:` and carries an artifact that reads them — evidence: three notes declare real paths and render from them; `your-applications.com`'s hand-typed palette table was **deleted**, not maintained, and its stale "no single source" claim corrected (the family check has existed since [[ADR-0008]] and exits clean)
- [x] `obsidian-supernote-sync` is **one note, two sections**: the plugin inherits its host's theme tokens, the dashboard owns its palette
- [x] Each note states what its project's system actually is, including the gaps — evidence: the Obsidian plugin's system is that it declares **nothing** and defers to host theme tokens, which the note states as the rule rather than as a gap; the dashboard is Tailwind with two escapes and the note says its palette is mostly unreadable rather than inventing one
- [x] The your-* notes point at the family palette ([[ADR-0008]] upstream in `your-applications.com`) rather than restating its nine values — done 2026-07-30; the restated table and its stale "no single source" claim are gone from all three
- [x] Each artifact is verified **rendering in a sandboxed frame**, not by reading it — evidence: edankert.com 64 swatches / 9 declared spacing tokens / 6 measured bars; your-applications.com 26 swatches; obsidian-supernote-sync exactly 2, which is what its two surfaces declare
- [~] Each note leaves `draft` only once its page renders — **all six pages now render**; the notes stay `draft` until Edwin has looked at them. Deliberately left: that is a human gate, not work, and the same bar [[DES-0002]] held itself to

## Progress 2026-07-28

**Three of six done**, and the other three are blocked by something the survey could not have seen before the route existed ([[ISS-0059]]): `your-health`, `your-sudoku` and `your-trainer` declare colour in Kotlin and Swift and contain no application CSS. The route is CSS-only by deliberate narrowing, and that narrowing is what keeps it safe.

The survey that scoped [[FEAT-0044]] counted `.css` files per repo and found several in each — all vendored cockpit, venv or test-report noise. **Counting files answered "is there CSS here" when the question was "does this project's UI have CSS".**

**One artifact, copied verbatim.** `docs/__templates__/design-style-guide.html` is the canonical page; everything project-specific arrives at runtime from `stylesheets:`. Six hand-written pages would have been six things that drift; six identical copies cannot say different things about the same question.

## Notes

The shape is [[DES-0002]]'s, and so is the discipline: read from the implementation, state the gaps as gaps, and let the page be the checkable thing. Copying its *prose* would be the mistake — each project's principles are its own, and a system nobody follows is worse than none.


## Done 2026-07-30 — the per-repo list [[PHASE-013]] asked for

| Repo | Surface | Page reads | Tokens | Note |
|---|---|---|---|---|
| project-os-cockpit | desktop app | `base.css`, `cockpit.css`, `renderer.css` | — | [[DES-0002]], the exemplar, `implemented` |
| your-applications.com | website | `public/css/style.css` | 26 swatches | `draft` |
| edankert.com | website | `public/css/style.css` | 64 swatches, 9 spacing, 6 bars | `draft` |
| obsidian-supernote-sync | plugin **+** dashboard | `obsidian-plugin/styles.css`, `web-dashboard/src/index.css` | 2 | one note, two sections; `draft` |
| your-health | Android app | `…/ui/theme/Color.kt` | **46 resolved, 0 unresolved** | `draft` |
| your-sudoku | iOS app | `ios/YourSudoku/App/Theme.swift` | **3 resolved, 4 unresolved** | `draft` |
| your-trainer | iOS app | `ios/YourTrainer/Utils/ZoneColorUtils.swift` | **1 resolved, 6 unresolved** | `draft` |

Six projects, seven surfaces — the whole table in [[FEAT-0044]]. Native-app figures measured 2026-07-30 against live sidecars on ports 8901–8903.

**Deliberately skipped, with the reason:** `yourtrainer-mcp` (its only CSS is the vendored cockpit and venv packages — no UX), `articles`, `project-os`, `project-os-dev`, `project-os-bench` (tooling, templates and prose; nothing renders).

### What the three blocked repos needed, and why the blocker is gone

[[ISS-0059]] was fixed after this note was written and the note was never updated — so it still read `blocked` for work that had been unblocked. `token_sources.synthesise_css` parses Kotlin and Swift **at read time**, per request, never writing a file: no generated artifact to drift, and the source itself never leaves the machine (only extracted `--name: value` pairs are emitted).

### The stale claim that survived in three notes

All three restated the six-value family palette and asserted it had *"no single source"* and that *"nothing checks that they agree"*. Both false since [[ADR-0008]]: `your-applications.com` is the upstream, `family-palette.yaml` names the tokens without duplicating their values, and `check-family-palette.py` parses each consumer's source. Run 2026-07-30 — `your-sudoku` 6 agree, `your-trainer` 8 agree, `your-health` excluded by design, **exit 0**.

The correction had been made in `your-applications.com`'s own note in July and not propagated. Worth naming: a fleet-wide claim corrected in one repo is still wrong in the other N.

### Found by doing it, not by reading it

- **[[ISS-0073]]** — filed and fixed. SwiftUI's `Color(red:green:blue:)` takes 0–1 doubles; the synthesiser matched only the `/ 255.0` spelling, so `your-trainer`'s `zoneRecovery` was reported as unreadable when `#999999` was sitting in the source. Small, but the unresolved path exists for colours with *no honest value*, and spending it on one that has a value teaches readers to skim past the ones that matter.
- **`your-trainer`'s zone ramp is not a designed scale.** Six of seven zone colours are SwiftUI system colours, so the ramp is whatever the platform's blue/green/yellow/orange/red/purple happen to be, and it moves with the OS and the appearance setting. That note's first principle is *"zone colour is data, not decoration — an ordered scale a user reads mid-effort"*. The prose already recorded a gap; the page makes the size of it unavoidable. Recorded in that repo, not fixed here — [[PHASE-013]] puts other repos' corpora out of scope.
- **`your-sudoku`'s four unresolved tokens are its four cell states** — the most semantically loaded colours in the app, all `Color.*.opacity(…)` derived from system colours, against a stated principle of *"state without colour"*.
