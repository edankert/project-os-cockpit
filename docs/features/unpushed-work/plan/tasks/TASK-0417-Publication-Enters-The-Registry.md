---
type: "[[task]]"
id: TASK-0417
aliases: ["TASK-0417"]
title: "Publication enters the registry — the overview button carries the number and Needs you carries the row"
status: doing
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13: 'add the git status to the needs you section' + 'an indication of having to push using a number on the overview icon'"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: ["[[TASK-0415-Git-State-For-Every-Workspace]]", "[[TASK-0416-Generalise-The-Note-Less-Obligation]]"]
blocks: ["[[TASK-0418-The-Push-Lives-With-The-Commits]]"]
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0025]]", "[[DES-0011-Publication-Is-An-Obligation]]"]
tests: []
---

# Publication enters the registry

Both halves of this already exist. `refreshObligationBadges()` paints `.mode-badge` on `.top-bar-btn[data-mode]` from `/api/cockpit/obligations`, and `overview` is one of the five views. `_needs_you_group()` builds the leading group for every view except `issues` and `tests`, which lead with their own. **Registering the obligation is what makes both appear; neither needs new UI.**

## Definition of Done

- [ ] Unpushed work is declared as a note-less obligation owned by `overview`, through [[TASK-0416]]'s path, with the verb `Push` and the noun `commit`/`commits`.
- [ ] The Overview button shows the count, and its hover names the kind — `3 · commits to push`, not `3 items here need a person`.
- [ ] The overview's `Needs you` group carries a row whose subject is the unpublished commits and whose destination is history ([[TASK-0418]]).
- [ ] **Absent at zero, everywhere.** Nothing to publish means no badge and no row — not a zero, not an empty group.
- [ ] The badge, the group and the landing page agree **by construction**, asserted in a test rather than checked by eye.
- [ ] The no-remote state is expressed as itself, not as a count: *nothing here is backed up* is not `0 commits to push`.
- [ ] **A deploy remote is counted, under its own kind** — `commits to deploy`, distinct from `commits to push` (Edwin, 2026-08-13). The breakdown reads both separately, the total includes both, and the deploy row **names** its action without offering it: [[ADR-0027]] test 3's *offer **or** name* clause exists for exactly this. The refusal must read as a decision, never as a control that failed.

## Steps

- [x] Add the source; wire it to the git state [[TASK-0415]] restored.
- [x] Extend the vocabulary (`KIND_NOUNS`, verb) server-side.
- [ ] Assert badge/group/landing agreement, and absence at zero.

## Found while building, 2026-08-13 — the row has no surface yet

The badge needed **no renderer change at all**, as predicted: registering the source made `/api/cockpit/obligations` report `overview: 6`, `breakdown: {"unpushed commit": 6}`, and the existing `refreshObligationBadges()` paints it. Measured on this repo: the Overview button reads **6**, hovering says *"6 commits to push"*.

The `Needs you` row did **not** come free, and the reason is worth recording because it was invisible from the notes:

- The leading `Needs you` group is a **navigator** group, built per nav mode.
- The overview is **not a nav mode** — `nav_payload` falls back to `features` when asked for one — because the overview is a dashboard, not a tree.
- The view **landings** that would carry it (`renderViewLanding`) exist for `~features`, `~issues` and `~tests` only. `landing_payload(index, "overview")` is correct and already returns the group with its six rows; **nothing fetches it.**

So the server half is complete and asserted, and the surfacing of the row is [[TASK-0418]]'s — where it belongs, since that task already owns the overview's history and the fate of [[FEAT-0098]]'s band. Recorded rather than quietly re-scoped: this task claimed a row that it cannot, by itself, put anywhere.
