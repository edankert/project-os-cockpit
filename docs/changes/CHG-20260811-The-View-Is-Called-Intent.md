---
type: "[[change]]"
id: CHG-20260811-Intent
title: "The design view is called Intent — the button, the mode id, the server's mode and the stored preference, with the old id aliased rather than dropped"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[TASK-0385-The-View-Is-Called-Intent]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[FEAT-0084]]", "[[PHASE-030-Obligations-Go-Home]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [change]
---

# The view is called Intent

**Intent was agreed on 2026-08-10 and the screen kept saying Design.** The obligation registry has used `intent` since FEAT-0089, which is why the badge tooltip already read correctly while the button beside it did not. [[TASK-0385]] closes the gap.

## What changed

| | before | after |
|---|---|---|
| button | `data-mode="design"`, `aria-label="Design"` | `data-mode="intent"`, `aria-label="Intent"` |
| title | *Design — what this is, and what it should look like* | *Intent — what this project is, and what it should look like* |
| renderer mode | `design` | `intent` |
| server mode | `design` | `intent`, with `design` aliased |
| stored preference | `cockpit:nav-mode: design` | migrated to `intent` on load |
| `MODE_FOR_VIEW` | `intent → design` | `intent → intent`, translation gone |

**Not renamed, deliberately:** the `design` note type, `_design_groups`, and the `~design` / `~design/<DES-id>` routes. The view is Intent; a design is still a design, and conflating the two is the one way this change could break something real.

## Contract

`/api/cockpit/nav?mode=design` still answers, with `mode: "intent"`. This is the point rather than a courtesy: `nav_payload` maps an unknown mode to `DEFAULT_MODE` **silently**, and that behaviour is what made the Tests view look broken for 33 hours earlier the same day — a client asked for `tests`, a server that predated the mode answered with the features tree, and nothing said the request was not understood. A rename that dropped `design` would do that to every stored preference and bookmark carrying it. A genuinely unknown mode still falls back, so the alias is a rename and not a licence.

## Why it was not FEAT-0084's after all

[[FEAT-0087]] reconciled its own naming criterion and parked the rename on [[FEAT-0084]] — *"a stored-preference migration… belongs with FEAT-0084's view-vocabulary work"*. Edwin read FEAT-0084 and disagreed: it is about aligning the browser and Electron front doors. **Its own Out section agrees** — *"the label question beyond making it single-sourced… is a naming decision for whoever picks"*. FEAT-0084 makes names single-sourced; it does not choose them, and Intent was already chosen. The decision had been parked behind a feature that declines to make decisions.

**Both halves of the cost estimate were wrong**, measured today:

- *"two front doors"* is one. The browser cockpit's `NAV_MODES` is `library / features / issues / recent` — mode 1 has never exposed this view.
- *"a stored-preference migration"* is `RETIRED_NAV_MODES`, existing machinery with four entries already. It took a fifth.

The estimate was made while the surface was being built and never re-checked. Recorded because **a reconciled criterion is a closed decision, and this one closed on a cost nobody measured** — the same shape as [[ISS-0131]]'s "eighteen boxes" argument earlier today, which was also true when written and false when acted on.

## Verification

Walked in the running app: the button carries the compass icon (4 paths, not the default glyph), clicking it stores `intent` and lands on `What this project is · 8 / Designs · 10 / Decisions · 11`, and the badge reads `3` with *"2 standing documents to confirm, 1 ADR to decide"*. Setting `cockpit:nav-mode` to `design` and reloading rewrites it to `intent` with the Intent button active. Server: `?mode=intent → intent`, `?mode=design → intent`, `?mode=bogus → features`.

Twelve existing guards across `test_design_bench.py`, `test_surface_ownership.py` and `test_parent_backlink.py` asserted the old id and were moved to the new one rather than deleted — including the icon guard, which **caught the icon-key miss** during this change. Two new assertions were added: `intent` must not be in the retired list, and `design` must be, with a fallback target.

## Scope note

PHASE-029 remains **out** of [[REL-0001]] — Edwin confirmed it on 2026-08-11. This change does not pull any of [[FEAT-0084]]'s single-sourcing work forward; it only settles a name that was already decided.
