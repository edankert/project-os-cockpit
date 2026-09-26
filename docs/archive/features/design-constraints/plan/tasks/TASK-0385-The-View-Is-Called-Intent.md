---
type: "[[task]]"
id: TASK-0385
aliases: ["TASK-0385"]
title: "The view is called Intent — the label, the mode id and the stored preference, so the name Edwin agreed is the name on screen"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'I think FEAT-0084 is more to align browser and Electron application. Maybe good to change the Intent label and id now as part of the full implementation and testing of REL-0001.'"]
parent: "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
effort: S
depends: []
blocks: []
related: ["[[FEAT-0084]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[REL-0001-The-Human-Has-Levers]]", "[[TASK-0368]]"]
tests: []
---

# The view is called Intent

## Why this is not FEAT-0084's, after all

[[FEAT-0087]] reconciled its own naming criterion rather than ticking it, and parked the rename on [[FEAT-0084]]:

> *"the rename is a stored-preference migration of the [[TASK-0368]] kind and belongs with [[FEAT-0084]]'s view-vocabulary work, not bolted on here"*

Edwin read FEAT-0084 and disagreed: it is *"more to align browser and Electron application."* **He is right, and its own scope says so** — FEAT-0084 declares the view set once so both renderers consume one list, and its **Out** section is explicit:

> *"The label question beyond making it single-sourced. Whether `library` should read 'Project' or 'Library' is a naming decision for whoever picks; the point here is that it cannot be both."*

So FEAT-0084 makes names single-sourced; it does not choose them. **Intent was already chosen.** Parking a made decision behind a feature that explicitly declines to make decisions is how an agreed name stays off the screen indefinitely — and it had, until Edwin asked why the view still says Design.

## And the cost estimate was wrong twice

The reconciliation justified deferral with *"renaming a mode means migrating a stored preference in two front doors"*. Measured 2026-08-11:

1. **It is one front door, not two.** The browser cockpit's `NAV_MODES` is `library / features / issues / recent` — **mode 1 does not expose this view at all**. There is no second preference to migrate.
2. **The migration is existing machinery.** `RETIRED_NAV_MODES` + `RETIRED_MODE_FALLBACK` already rewrite a stored mode on load, and already carry four entries ([[TASK-0368]]'s `tasks` among them). Adding `design → intent` is two lines in a mechanism built for exactly this.

The estimate was not careless — it was made while the surface was being built, and it was never re-checked. Worth recording because a reconciled criterion is a *closed* decision, and this one closed on a number nobody measured.

## Definition of Done

- [x] The button reads **Intent**, with `aria-label` and `title` to match
- [x] The mode id is `intent` in the renderer's `NAV_MODES` and in the server's
- [x] A stored `cockpit:nav-mode` of `design` migrates to `intent` on load, via the existing retired-mode path
- [x] `?mode=design` still answers with the Intent view rather than **silently falling back to features** — the exact trap that made the Tests view look broken for 33 hours on 2026-08-11
- [x] `~design` still lands somewhere correct; `~design/<DES-id>` keeps framing a design artifact, because a design artifact is still a design
- [x] `MODE_FOR_VIEW` loses its `intent: 'design'` translation — the registry has always said `intent`, and that mapping existed only to bridge the gap this task closes
- [x] [[FEAT-0087]]'s naming criterion moves from `[~]` to `[x]`

## Out of scope

- Single-sourcing the view vocabulary across both renderers. That is [[FEAT-0084]]'s, and it stays [[PHASE-029]]'s — which Edwin confirmed is **not** part of [[REL-0001]].
- Renaming the `design` **note type**, `_design_groups`, or `~design/<id>`. The view is Intent; a design is still a design. Conflating the two is the one way this change can break something real.

## Done — 2026-08-11

Walked in the running app after a sidecar restart and a renderer reload:

| check | result |
|---|---|
| button | `data-mode="intent"`, title *"Intent — what this project is, and what it should look like"*, `aria-label="Intent"`, no `data-mode="design"` anywhere |
| icon | present, 4 paths — the compass, **not** the default glyph |
| click | stores `cockpit:nav-mode: "intent"`, lands on `What this project is · 8`, `Designs · 10 · 3 done`, `Decisions · 11` |
| badge | `3`, tooltip *"2 standing documents to confirm, 1 ADR to decide"* |
| migration | set `cockpit:nav-mode` to `design`, reloaded → rewritten to `intent`, Intent button active |
| server | `?mode=intent` → `intent`; `?mode=design` → `intent`; `?mode=bogus` → `features` |

**The icon, and a correction.** `modeIconMap` is keyed by `data-mode`, so renaming the id without renaming the key drops the lookup to `TYPE_ICONS._default` — a button that still works, still labels correctly, and silently wears the wrong glyph. I found it by reading and claimed nothing would have caught it. **That was wrong**: `test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it` already asserted `design: '<circle` for exactly this reason — *"no icon; the button renders blank"* — and it failed on this change. The guard was there; the suite caught it.

What the rename did need was for that guard, and eleven others across `test_design_bench.py`, `test_surface_ownership.py` and `test_parent_backlink.py`, to be moved to the new id rather than deleted. Each was updated to assert the same property about `intent`, plus two new ones: that `intent` is **not** in the retired list, and that `design` **is**, with a fallback target.

**The alias is the other half.** `nav_payload` maps an unknown mode to `DEFAULT_MODE` **without complaint** — the behaviour that made the Tests view look broken for 33 hours on this same day. A rename that dropped `design` would have done exactly that to every stored preference and bookmark carrying it. `MODE_ALIASES` keeps the old id answering, and the test asserts a genuinely unknown mode *still* falls back, so the alias is a rename and not a licence.

Routes are deliberately untouched: `~design` still lands the view and `~design/<DES-id>` still frames one artifact, because a design is still a design. The view was renamed; the note type was not.
