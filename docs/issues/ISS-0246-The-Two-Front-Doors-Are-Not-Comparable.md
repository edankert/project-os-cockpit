---
type: "[[issue]]"
id: ISS-0246
aliases: ["ISS-0246"]
title: "The browser cockpit has two views and the desktop shell has twelve — `both front doors` has been applied as a rule to a pair that was never comparable, and every finding of the form `the browser is missing X` is one instance of that"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["measured while closing TASK-0511, 2026-08-20"]
severity: high
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0230-The-Browser-Cockpit-Has-No-Surface-Row]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[ADR-0010-Two-Front-Doors]]", "[[TASK-0511-A-Picker-Writes-Features-And-Phases]]"]
tests: []
---

# The rule assumes a symmetry that has never existed

## Measured 2026-08-20

Virtual pages (`~name` routes) implemented in each front door:

| front door | pages |
|---|---|
| `desktop/src/renderer/renderer.ts` | **12** — `~agents`, `~checks`, `~design`, `~features`, `~history`, `~inbox`, `~issues`, `~overview`, `~publication`, `~release`, `~review`, `~tests` |
| `src/project_os_cockpit/static/cockpit.js` | **2** — `~note`, `~root` |

The browser cockpit renders **notes and a navigator**. Every view this phase has been about — the tests view, the checks page, the release page, the design view — exists in the desktop shell alone.

## Why this matters now

[[PHASE-029]] states the rule: *"the browser cockpit and the desktop shell answer the same questions, and differ only where a difference was decided."* [[ISS-0230]] applied it and was fixed — correctly, for a **row renderer** that both files genuinely have.

But the rule has since been reached for repeatedly on things only one door has. [[TASK-0511]] closed with *"the browser cockpit does not have this control"* as a follow-up, on the assumption that adding it was a small matter of a second call site. **It is not**: the control lives on a release page the browser cockpit does not have, and building it means building the twelfth view rather than the picker.

So the obligation has been carried, note to note, in a form nobody can discharge — and each time it is deferred it reads as an omission rather than as the decision it actually needs.

## The question this is really asking

**Was two front doors decided, or did it happen?** [[ADR-0010]] is `proposed` and [[PHASE-029]] is `planned` — the decision that would say which pages the browser cockpit owes has never been taken. Three possibilities, and they are genuinely different:

1. **The browser cockpit is a reader.** Notes and navigation, deliberately — a tablet on the Wi-Fi reads the record; the desktop shell does the work. Then *both front doors* applies to the navigator and to nothing else, and the eleven missing pages are not debt.
2. **It is a full second front door**, and eleven views are owed. That is a body of work, not a follow-up line, and it should be phased as one.
3. **Somewhere between**, named page by page.

Until that is decided, *"the browser cockpit is missing X"* will keep being filed, and keep being true, and keep not being actionable.

## Done when

- [ ] The decision is taken — [[ADR-0010]] accepted, amended or declined, saying which pages the browser cockpit owes.
- [ ] Notes that carry a *both front doors* obligation are re-read against it: [[TASK-0511]]'s follow-up is the live one.
- [ ] Whatever is decided, the rule stops being quoted at pairs where only one side has the surface.
