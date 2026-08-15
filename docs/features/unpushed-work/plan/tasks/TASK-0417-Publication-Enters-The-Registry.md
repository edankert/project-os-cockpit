---
type: "[[task]]"
id: TASK-0417
aliases: ["TASK-0417"]
title: "Publication enters the registry — the overview button carries the number and Needs you carries the row"
status: done
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

- [x] Unpushed work is declared as a note-less obligation owned by `overview`, through [[TASK-0416]]'s path, with the verb `Push` and the noun `commit`/`commits`. — evidence: `note_less_sources()` reports `unpushed commit → verb Push, view overview` and `KIND_NOUNS['unpushed commit'] == ('commit', 'commits')`; `test_every_note_less_source_is_declared_and_enumerable` fails if any declared source loses its noun, verb or view (verified 2026-08-14)
- [x] The Overview button shows the count, and its hover names the kind — **amended 2026-08-14**: the delivered string is `6 commits to push`, composed by `refreshObligationBadges` as `${count} ${noun} to ${verb}` joined with `, `. The `·` in the original wording never existed; it was written from the badge's *visual* separator, not from the tooltip. The property — the hover names the KIND rather than saying "items" — holds, and `test_every_row_carries_its_verb_and_a_destination` asserts no label contains "item". Recorded rather than silently re-worded, per `QUALITY.md`.
- [~] The overview's `Needs you` group carries a row whose subject is the unpublished commits and whose destination is history ([[TASK-0418]]). — **not delivered as written, and it cannot be**: `overview` is not a nav mode, so `nav_payload(index, "overview")` falls back to `features` and no `Needs you` group is ever fetched for it. [[TASK-0418]] re-homed the row to the rail's attention panel, which is where Edwin asked for it. `landing_payload(index, "overview")` does return the group with its rows and nothing fetches it. [[FEAT-0100]]'s acceptance criterion 1 carries the same amendment; this is its source.
- [x] **Absent at zero, everywhere.** Nothing to publish means no badge and no row — not a zero, not an empty group. — evidence: `test_the_publication_obligation_is_exercised_non_vacuously` pushes the fixture repo and asserts the kind **disappears** from `counts_by_kind` rather than reporting `0` (2026-08-14)
- [x] The badge, the group and the landing page agree **by construction**, asserted in a test rather than checked by eye. — **this box was the independent review's finding 3, and it was ticked-worthy only on 2026-08-14.** Until then no test exercised the publication source non-vacuously: `owed_corpus` is a `tmp_path` copy with no `.git`, and `repo_index` reached publication only because this repo happened to have unpushed commits that day. Mutating `_publication_rows` to `return []` left 1281 tests passing. `test_the_publication_obligation_is_exercised_non_vacuously` builds a real repo with a forge-shaped remote and real unpushed commits, and asserts count == len(rows) == landing count; the same mutation now fails it.
- [x] The no-remote state is expressed as itself, not as a count: *nothing here is backed up* is not `0 commits to push`. — evidence: `buildPublicationBlock` renders `kind: 'none'` as *No remote — nothing here is backed up* with no button, and `remote_kind('') == 'none'` short-circuits before any count is taken
- [x] **A deploy remote is counted, under its own kind** — `commits to deploy`, distinct from `commits to push` (Edwin, 2026-08-13). The breakdown reads both separately, the total includes both, and the deploy row **names** its action without offering it: [[ADR-0027]] test 3's *offer **or** name* clause exists for exactly this. The refusal must read as a decision, never as a control that failed.

## Steps

- [x] Add the source; wire it to the git state [[TASK-0415]] restored.
- [x] Extend the vocabulary (`KIND_NOUNS`, verb) server-side.
- [x] Assert badge/group/landing agreement, and absence at zero. — `test_the_publication_obligation_is_exercised_non_vacuously` (2026-08-14); see the DoD box above for why this took until close-out.

## Found while building, 2026-08-13 — the row has no surface yet

The badge needed **no renderer change at all**, as predicted: registering the source made `/api/cockpit/obligations` report `overview: 6`, `breakdown: {"unpushed commit": 6}`, and the existing `refreshObligationBadges()` paints it. Measured on this repo: the Overview button reads **6**, hovering says *"6 commits to push"*.

The `Needs you` row did **not** come free, and the reason is worth recording because it was invisible from the notes:

- The leading `Needs you` group is a **navigator** group, built per nav mode.
- The overview is **not a nav mode** — `nav_payload` falls back to `features` when asked for one — because the overview is a dashboard, not a tree.
- The view **landings** that would carry it (`renderViewLanding`) exist for `~features`, `~issues` and `~tests` only. `landing_payload(index, "overview")` is correct and already returns the group with its six rows; **nothing fetches it.**

So the server half is complete and asserted, and the surfacing of the row is [[TASK-0418]]'s — where it belongs, since that task already owns the overview's history and the fate of [[FEAT-0098]]'s band. Recorded rather than quietly re-scoped: this task claimed a row that it cannot, by itself, put anywhere.
