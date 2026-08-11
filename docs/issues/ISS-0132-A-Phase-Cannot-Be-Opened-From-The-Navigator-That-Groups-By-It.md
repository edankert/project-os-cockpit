---
type: "[[issue]]"
id: ISS-0132
aliases: ["ISS-0132"]
title: "A phase cannot be opened from the navigator that groups by it — the server sends every phase group's `url` and the renderer never reads it"
status: fixed
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'I cannot select a phase in the features section (and see the phase note contents in the details pane).'"]
severity: medium
component: "cockpit-nav"
parent: ""
related: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[ISS-0131]]", "[[REL-0001-The-Human-Has-Levers]]"]
tests: []
---

# A phase cannot be opened from the navigator that groups by it

## Problem

The Features view groups every feature under its phase and prints the phase's ID and title as the group header. Clicking that header only folds the group. There is no way to reach the phase note — the note that carries the goal, the scope and the exit criteria — from the surface that is organised entirely around it.

**The data is already there.** The server populates `url` on every phase group:

```
group url: '/docs/phases/PHASE-028-Borrowed-Capability.md'
```

`NavGroupData.url` is declared in the renderer's own type (`renderer.ts:2954`). It is never read: `group.url` appears nowhere in `renderer.ts`. The payload has carried a working target all along and the client discards it.

**Why this matters more now.** [[REL-0001]] was re-scoped on 2026-08-11 to be defined by five phases reaching `done`, with exit criteria as the completion bar. The phase note is where those criteria live, so the release's own definition is currently unreachable from the view that lists its work.

## Repro

1. Open the Features view.
2. Click any phase group header, e.g. `PHASE-023 · Levers for the human`.
3. The group folds. The centre pane does not change.

## Expected

Selecting a phase group header opens the phase note in the centre pane, as selecting any feature row does. Folding stays available — the chevron already exists for it.

## Actual

The header is a `<summary>` whose only behaviour is toggling `<details>`. `group.url` is ignored.

## Evidence

- `desktop/src/renderer/renderer.ts:2954` — `url?: string` on `NavGroupData`.
- `desktop/src/renderer/renderer.ts:8752` — `summary.className = 'nav-group-header'`; no click handler, no `data-rel`.
- `grep -n "group\.url" desktop/src/renderer/renderer.ts` → no matches.
- Live payload 2026-08-11: every `mode=features` group carries a `/docs/phases/…` url.

## Next Actions

- [ ] Give the header a nav target from `group.url` via `extractRel`, without breaking the fold — the chevron toggles, the label navigates.
- [ ] Check the other modes whose groups carry a `url` (the tier groups point at `/tests/ACCEPTANCE_TESTS.md`) so this is fixed as a rule rather than for phases alone.

## Resolution — 2026-08-11

The group header's label now navigates via `extractRel(group.url)`; the chevron still folds. Binding the whole `<summary>` would have taken the fold away, so the handler sits on `.group-header-inner` and calls `preventDefault()` — without it the group folds underneath the reader as the note opens.

**Verified in the running app:** clicking `PHASE-028` opens `phases/PHASE-028-Borrowed-Capability.md` (`h1: Borrowed capability`) and the group's `open` state is `true` before *and* after the click. 27 headers render, all navigable, each titled `Open PHASE-0NN`.

Hover shows an underline and a pointer; the head is deliberately **not** given a permanent link colour — it is the group's name first and a target second, and eight phase names in link blue would read as a list of links rather than as the structure they are.

## Reopened and completed — 2026-08-11

The first fix opened the phase but got the *grammar* wrong, and Edwin caught both halves within minutes: *"the phase selection mechanism seems to be different from the feature selection. Also it does not show the phase as being selected."*

**Only the label navigated.** A click an inch to the right of the phase name hit the `<summary>` and folded the group — the same row doing two different things depending on which pixel was hit, where a feature row selects from anywhere on its card. Now the whole head opens the note and **the chevron alone folds**, which is the feature row's own arrangement: select from anywhere, with a separate control for the children.

**And the selected phase did not look selected.** `refreshActiveNavRow` sweeps `li[data-rel]`, and a group head is a `<summary>` — so it was invisible to the one function that marks what is current. The head now carries `data-rel` and the sweep marks it, with the same tint and left rule a selected row gets.

Walked in the running app: clicking the spacer well right of the label opens `PHASE-024` with the group still expanded; the chevron folds without navigating and leaves the document alone; selecting `FEAT-0063` afterwards moves the highlight off the head, so exactly one thing is ever marked current.

**The lesson worth keeping.** The first fix was verified — it opened the note, the group stayed open, a test passed — and was still wrong, because it was verified against *its own description* rather than against how the surface behaves everywhere else. Reachability was the bug; matching the grammar of the thing next to it was the requirement.
