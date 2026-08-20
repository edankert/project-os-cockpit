---
type: "[[issue]]"
id: ISS-0246
aliases: ["ISS-0246"]
title: "The browser cockpit has two views and the desktop shell has twelve — ADR-0010 decided parity and gated it on an authenticated write path that does not exist, and `both front doors` has been quoted since as though parity already applied"
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

## Corrected 2026-08-20 — the decision WAS taken, and I said it was not

This note first claimed *"[[ADR-0010]] is `proposed` … the decision has never been taken."* **It is `accepted`, `decided_option: "4"`, decided 2026-08-12** — and I asserted otherwise without opening it. Filing an issue about unread premises on an unread premise.

**Option 4 is *parity, gated on an authenticated write path*.** Edwin confirmed parity again on 2026-08-20 when asked, which is consistent rather than new. The ADR's own words: *"The browser cockpit is the reading surface **for now**, and that is a **stage rather than a property**."*

So the twelve-against-two gap is not an undecided question. It is **the decision's own precondition, unmet**:

> *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* — [[REL-0001]]'s acceptance pass drove every mutation endpoint over the real LAN: **ten of ten returned 403 while reads returned 200** ([[REQ-0027]], [[RISK-0005]]).

## What is actually owed, in order

1. **An authenticated write path.** Until a surface can prove *who* is asking, the loopback check cannot be replaced — only removed, which hands every device on the Wi-Fi the ability to transition notes and create files across twelve repos. This is the gate, and nothing below it can start.
2. **The eleven reading views**, which the ADR does **not** gate: `~overview`, `~features`, `~issues`, `~tests`, `~checks`, `~design`, `~history`, `~agents`, `~inbox`, `~publication`, `~review` answer questions without changing anything. These are owed now, and [[PHASE-029]] is `planned` and empty of them.
3. **The writing surfaces** — `~release` and the marks, ticks and pickers — after (1).

## What this issue keeps

The real defect stands, narrowed: ***both front doors* has been quoted as though parity already applied.** [[TASK-0511]] deferred its picker as a small follow-up when the picker's page does not exist there and, under the ADR, could not be written there yet even if it did. Each such deferral reads as an omission rather than as a precondition nobody has met.

## Done when

- [x] The decision is found and read. It exists; the error was mine.
- [ ] [[PHASE-029]] carries the eleven reading views as scoped work rather than an empty `planned`.
- [ ] Notes carrying a *both front doors* obligation say which stage they are waiting on — the eleven views, or the authenticated write path.
- [ ] `RISK-0005`'s ten-of-ten measurement is re-run before any write endpoint is offered on a LAN-reachable surface.

## Done when

- [ ] The decision is taken — [[ADR-0010]] accepted, amended or declined, saying which pages the browser cockpit owes.
- [ ] Notes that carry a *both front doors* obligation are re-read against it: [[TASK-0511]]'s follow-up is the live one.
- [ ] Whatever is decided, the rule stops being quoted at pairs where only one side has the surface.
