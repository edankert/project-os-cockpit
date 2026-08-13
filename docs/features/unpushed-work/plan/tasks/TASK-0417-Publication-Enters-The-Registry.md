---
type: "[[task]]"
id: TASK-0417
aliases: ["TASK-0417"]
title: "Publication enters the registry — the overview button carries the number and Needs you carries the row"
status: backlog
owner: unassigned
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

- [ ] Add the source; wire it to the git state [[TASK-0415]] restored.
- [ ] Extend the vocabulary (`KIND_NOUNS`, verb) server-side.
- [ ] Assert badge/group/landing agreement, and absence at zero.
