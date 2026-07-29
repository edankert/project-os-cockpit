---
type: "[[phase]]"
id: PHASE-010
aliases: ["PHASE-010"]
title: "Surface ownership"
status: done
order: 10
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
goal: "Every project-os note type gets one purpose surface that answers a question someone actually asks, and Library stops being the place types go when nobody decided where they belong. Library reduces to Pinned + the Docs tree — the files — and each type it was holding moves to the page that already owns its question."
features:
  - "[[FEAT-0046-Plans-On-The-Feature]]"
  - "[[FEAT-0047-Risks-On-The-Issues-Surface]]"
  - "[[FEAT-0048-Changes-On-The-Overview]]"
  - "[[FEAT-0049-Review-Desk-As-Record]]"
  - "[[FEAT-0050-Library-Reduction]]"
requirements:
  - "[[REQ-0025-No-Type-Loses-Its-Surface]]"
issues:
  - "[[ISS-0062-Most-Plans-Are-Invisible]]"
  - "[[ISS-0063-Dead-Stat-Tiles]]"
depends: ["[[PHASE-009-Design-Surfaces]]"]
related: ["[[FEAT-0040-Overview-Rework]]", "[[FEAT-0041-Review-Desk]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
tags: [ia, library]
---

# Surface ownership

## Goal

Library mode accumulated eight groups by a process nobody chose: each time a type appeared with no obvious home, it got a `rare:` group. Measured against this repo's own corpus, that produced one duplicate, two dead ends, and one group showing 42% of its own contents.

The phase's claim is narrow and checkable: **a type belongs on the page that answers the question the type is read for.** A plan is read while looking at its feature. A risk is read while looking at what's wrong. A change is read while looking at what happened. A test is read while judging whether something is done. None of those questions is "what document types exist", which is the only question Library's by-type groups answer.

## What the corpus actually showed

Not inferred — measured against `nav_payload(mode="library")` and the fleet:

| Group | Items | Finding |
|---|---|---|
| Design | 3 | Duplicate. Points at the same `~design/<id>` URLs the Design mode does; predates that mode ([[TASK-0212]] added it before [[FEAT-0043]] existed). |
| Decisions | 8 | Duplicate. The overview record column already renders **every** ADR — `buildRecordDisclosure` holds `sorted.slice(4)`, not a link out. `proposed` ADRs separately route to the desk. |
| Plans | 14 | **Of 33 `PLAN.md` files, 19 carry no frontmatter and are therefore invisible everywhere** — `features/` is a `DOC_TREE_EXCLUDED_ROOTS` root, so they reach neither the tree nor the group. [[ISS-0062]]. |
| Risks | 4 | Only surface risks have. The overview's Risks stat tile is passed no `navMode` and navigates nowhere. [[ISS-0063]]. |
| Tests | 21 | The desk's "Test runs" group shows only manual tests at `ready` — a queue slice, not the register. The Tests stat tile is dead the same way. |
| Workflows | 3 | The untouched template three, `status: draft`, unchanged since 2026-01-29. |
| Changes | 4 buckets | Genuine archive. The only group whose structure is load-bearing. |
| Docs tree | 10 + 2 | The thing Library is for. |

## Why workflows move rather than get dropped

The three here are dead, but the *type* is not, and the distinction decides the design. Across the 11 fleet repos with a `docs/workflows/`: eight carry only the untouched template three (`status: draft`, `updated: 2026-01-29`, byte-identical); three authored their own — `obsidian-supernote-sync` (5 bespoke, template three deleted), `your-trainer` (1 bespoke, template three deleted), `your-applications.com` (template three kept plus two real ones). **Every authored workflow is `status: active`; every template one is `draft`.** No exceptions.

So the type is alive where someone writes one, and designing the IA around this repo's dead instances would be reading local emptiness as evidence about the type. Workflows join the Docs tree — prose with an `entrypoints:` list and no lifecycle to track browses fine as files, and in the three repos that use them they land under a `workflows/` folder worth opening.

The template shipping three drafts nobody fills in is a real problem and **not this repo's**. It is the inverse of what [[FEAT-0043]] found: there, a file nobody could see was a file nobody maintained, and the fix was to surface `LLM_BRIEF.md`. Here they are visible and still unmaintained, because they are content nobody asked for. That fix is upstream deletion in `~/Dev/repos/project-os/`, not a cockpit surface.

## Scope

- Plans nest under their feature, found **by path** so untyped ones surface too.
- Risks join the Issues mode; the Risks stat tile gets a destination.
- Changes move to the overview history band — recent expanded, the existing week/month buckets collapsed beneath.
- The review desk gains two registers beside its queue: every acceptance test, and every reviewed item.
- Library drops the Design, Decisions, Plans, Risks, Tests, Changes and Workflows groups, keeping Pinned + Docs tree.

## Out of Scope

- **Removing the Library mode button.** At Pinned + Docs tree it is a file browser, and opening a file by name stays a real need. Whether it still earns a strip slot is a separate judgement, deliberately not bundled into a reachability change.
- **Retyping the 19 untyped `PLAN.md` files.** The fix makes them reachable without frontmatter; adding `type: [[plan]]` to 19 files is corpus maintenance that would hide whether the path-based lookup actually works.
- **Fixing the upstream workflow template.** Belongs to `~/Dev/repos/project-os/`.
- **A risks nav mode of its own.** Four notes do not earn a top-level surface; the point of this phase is fewer homes, not more.

## Exit Criteria

- [x] `nav_payload(mode="library")` returns exactly two group kinds — `pinned` and `docs-tree` — against this repo's corpus — evidence: `test_library_is_pins_and_the_tree`; live payload `groups: ['docs-tree']` (no pins set in this workspace); manual run step 6
- [x] Every `PLAN.md` on disk is reachable from its feature, including those with no frontmatter — evidence: `test_every_plan_on_disk_resolves_to_its_feature` asserts set equality against a `features/*/plan/PLAN.md` glob; manual run step 1 rendered 38 rows including three untyped plans
- [x] The Risks and Tests stat tiles both navigate somewhere — evidence: `test_the_dead_stat_tiles_gained_a_destination`; manual run step 3 clicked both — Risks → `issues`, Tests → `~review`. Reqs stays inert by decision (see Out of Scope) and `test_the_reqs_tile_stays_dead_on_purpose` records that so it does not read as an oversight
- [x] Changes are readable on the overview without opening Library, with the archive still reachable — evidence: manual run step 4 — Changes tile between Activity and Commits, 5 recent rows, 3 collapsed buckets, May 2026 nesting its week sub-buckets. A layout defect (`Changes97`) was found and fixed during this step
- [x] The desk lists every acceptance test and every reviewed item, not just the queue slice — evidence: `test_the_tests_register_holds_the_whole_corpus`, `test_the_reviewed_register_comes_from_note_frontmatter`; manual run step 5 — `Tests · 22/22` and `Reviewed · 62`
- [x] No note type present in this corpus became unreachable — evidence: [[REQ-0025]], all eight criteria ticked. The near-miss worth recording: `buildQuickCorpus` fetched `mode=library` as "the broadest single fetch", so the reduction would have quietly cut Cmd+P to pins and loose files — a populated palette with half the corpus unfindable. Caught during implementation, not by a test; it now enumerates five modes plus the registers and the changes payload

## Notes

Sequencing: the four moves ([[FEAT-0046]]..[[FEAT-0049]]) each land a destination, and [[FEAT-0050]] removes the Library groups last. That order is deliberate — removing a group before its replacement exists strands the notes, which is the exact failure [[REQ-0025]] gates against and the one the design bench hit twice in PHASE-009.

**Outstanding: the independent review pass.** QUALITY.md requires one for [[CHG-20260729-Surface-Ownership]] and for features reaching `done`; it has not run, and the validator's REVIEW warning on that CHG note is accurate rather than noise. The work was authored in one session, so a reviewer starting from the notes and the diff alone is what the gate asks for ([[ADR-0013]]).

**What the manual pass did and did not establish.** Structure and geometry over CDP — element presence, row counts, computed `display`, click destinations — against a restarted app on a fresh sidecar. It found a real defect the whole automated suite passed over (the Changes tile's count rendered as `Changes97`, because tile `h3`s are `display: block` and `margin-left: auto` does nothing there). It did **not** establish that the new surfaces look right; that is a human judgement and was not made.
