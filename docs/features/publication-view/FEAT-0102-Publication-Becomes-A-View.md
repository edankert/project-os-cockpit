---
type: "[[feature]]"
id: FEAT-0102
aliases: ["FEAT-0102"]
title: "Publication becomes a view — the whole ladder from commit to versioned release in one place, with the acceptance gate attached to the rung that has one"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: changes-requested
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'I think a full release nav mode however this depends a little on what we call a release, there are probably multiple types of releases, from committing, pushing, deploying and actual versioned releases … should they all be shown in this release view together with a history?'", "Edwin 2026-08-16, choosing the name: 'Publication'", "Edwin 2026-08-16, on the deploy rung: 'named and refused, as today'"]
goal: "Give publication the surface it has never had: one view holding every rung a repo can reach — the commits, what is unpushed, what is undeployed and named-not-offered, the versioned releases and their tags — and the acceptance gate attached to the release rung, so a person can see how far their work has travelled and what stands between it and shipping."
requirements: []
tasks: ["[[TASK-0426-The-Ladder-As-Data]]", "[[TASK-0427-The-Publication-View]]", "[[TASK-0428-The-Release-Rung]]", "[[TASK-0429-The-Gate-Is-A-Campaign]]"]
design: ""
release: ""
depends: ["[[ADR-0028-Work-Has-Three-Phases]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0022]]", "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[DES-0011-Publication-Is-An-Obligation]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: ["[[TST-0027-The-Ladder-Is-Non-Empty-In-Every-Repo]]", "[[TST-0028-The-Release-Gate-Names-Its-Number]]"]
---

# Publication becomes a view

## Why a view, and why not "Releases"

Edwin asked for a release nav mode, and attached the right question to it: *"there are probably multiple types of releases, from committing, pushing, deploying and actual versioned releases."* The fleet answers it. There is no single release — there is a **ladder**, and it narrows as it climbs:

| rung | who acts | repos | live 2026-08-16 |
| --- | --- | --- | --- |
| commit | agent, at close-out | **12 / 12** | — |
| push | the human, from the cockpit | 8 | 7 commits across 4 repos |
| deploy | the human, elsewhere — named, refused | 2 | your-applications.com at **34** |
| versioned release | the human, gated on acceptance | 3 | your-trainer 11 + 12 tags |

A `Releases` mode would be **empty in 9 of 12 repos** — a permanent blank button, the failure `CLAUDE.md` records twice. The ladder is universal: every repo commits.

And three of its four rungs already exist. `history_payload` returns `remote_kind`, `unpublished_count`, `publication_known` and a per-commit `unpublished` flag; since [[ISS-0168]] the Push button sits next to the commits it publishes; [[FEAT-0100]] put both publication obligations in the registry. What is missing is the fourth rung — `git_state.py` mentions "tag" once, in a comment — and a **home**: `~history` is a route, not a mode, which is why it reads as a side-trip rather than a place.

So this is not a new surface bolted on. It is the third phase [[ADR-0028]] names, built by finishing the one that already holds most of it.

## What this builds

**1. The ladder as data** ([[TASK-0426]]) — one payload answering *how far has this work travelled*, for every repo, degrading by rung rather than going blank.

**2. The view** ([[TASK-0427]]) — `publication` as a nav mode. `~history` keeps working; it becomes an address inside the mode rather than a destination of its own.

**3. The release rung** ([[TASK-0428]]) — `REL-*` notes and tags, which nothing currently reads. A `draft` release is *"prepared and verified, not yet live"* (`STATUSES.md`) and is the signal that a release is in preparation.

**4. The gate as a campaign** ([[TASK-0429]]) — the acceptance suite, attached to the release rung, counted as **one** obligation rather than sixty.

## The gate, and why it is one row

`your-trainer` has 60 unchecked Tier 1/2 rows. They are not 60 tasks: they cluster into 17 sections, and **two of those carry 33** — Trainer Compatibility (20) and Monetization & Licensing (13). Top five carry 45 of 60. That is roughly two sittings, most of it with a trainer plugged in.

The suite's own *Manual Test Environment Breakdown* already says what each needs at hand — trainer hardware ~24, HRM ~9, Strava ~6, Play Billing ~2 — and no surface reads it. So the campaign groups by environment, and the unit a person sees is the **sitting**, not the checkbox.

Under [[ADR-0028]] it asks only while a release is `draft`. With none in preparation, 60 unchecked rows is the resting state of a checklist that unchecks itself whenever code changes, and it asks for nothing.

## Acceptance criteria

- [x] `publication` is a nav mode and is **non-empty in all 12 repos** — a repo with no remote reaches rung 1 and says so, rather than rendering blank — `test_the_publication_view_renders_in_every_repo` sweeps the discovered fleet and FAILS on an unreadable repo rather than skipping it; `articles` (no remote) renders `Committed · 18` alone and reads as complete
- [x] Every rung a repo can reach is shown, and one it cannot is absent rather than shown at zero — `test_a_repo_with_no_remote_omits_the_rung_rather_than_zeroing_it`; `unreachable` is reported by name so a surface can say *this repo does not deploy*
- [x] `~history` keeps working — stored preferences and deep links resolve, per the `MODE_ALIASES` lesson — route untouched — `publication` is an added mode, nothing renamed; `test_every_nav_url_is_routable_by_extract_rel` covers the new group urls
- [x] Unpushed commits carry the Push action already built; **undeployed commits are named and refused**, with the reason on screen, and no path from this view can push a deploy remote ([[ADR-0027]] admission test 3, and Edwin's explicit call) — `test_a_deploy_remote_is_named_and_never_offered` + `test_no_route_from_this_view_can_push_a_deploy_remote`, which enumerates the way the loopback guard does
- [x] `REL-*` notes and git tags appear on the release rung; a repo with neither shows the rung as unreached rather than empty — `test_a_tag_with_no_note_and_a_note_with_no_tag_are_both_shown`; `test_no_releases_and_no_tags_leaves_the_rung_unreached`
- [x] The acceptance gate is attached to the release rung and **names its number** — `your-trainer` reads 60, not `306/347` requiring arithmetic — walked live: `Release gate · 60 unchecked · no release in preparation`
- [x] The gate is **one** obligation when a release is `draft`, and **zero** otherwise. It never contributes 60 to any count — `test_a_draft_release_with_unchecked_checks_owes_exactly_one`; and `test_the_badge_rises_by_at_most_one` asserts a BOUND rather than a spot value
- [~] Gate rows group by the environment the suite's own table describes, so the unit is the sitting — **NOT delivered as written.** Rows group by suite SECTION (`test_rows_group_by_area_so_the_unit_is_the_sitting`), which achieves the criterion's PURPOSE — the unit is the sitting, and `your-trainer`'s 60 render as 17 areas led by Trainer Compatibility at 20 — but not by the mechanism it names. The *Manual Test Environment Breakdown* is a prose table in one repo's suite with no counterpart in the template, so reading it would have been a parser for a convention exactly one project has. Section grouping is derivable everywhere. Reconciled rather than ticked, because the criterion said *environment* and this is not that; if the environment table earns a place it should be a template feature first.
- [x] Opening a gate row reaches the suite at that section — `test_a_row_reaches_the_suite`; and the url is `/docs/<rel>` after fixing a dead click this work exposed
- [x] No write path widened; `test_every_note_mutating_endpoint_requires_loopback` still enumerates and passes — `test_every_note_mutating_endpoint_requires_loopback` still enumerates and passes; the full suite is green at 1351

## Notes

**Reads better after [[ISS-0173]].** Until bare ids are read, all 60 blocking rows resolve to zero refs, so the row → feature link that scopes the gate does not exist as far as any code can tell. Buildable either way; designed against the wrong corpus if [[ISS-0173]] is skipped.

**Not in scope: making the cockpit cut a release.** Publishing is a person's act ([[ADR-0022]]). This view shows how far work has travelled and what blocks the next rung. The one action it offers is the push that already exists.

## Delivered 2026-08-16

**Non-empty in all 12 repos**, which is the claim the view rests on and the reason it is not called `Releases`:

```
articles                 commit:18
edankert.com             commit:0 | deploy:?(refused)
obsidian-supernote-sync  commit:0 | push:0
project-os               commit:0 | push:2
project-os-bench         commit:0
project-os-cockpit       commit:12 | push:0 | release:1
project-os-dev           commit:0 | push:0
your-applications.com    commit:0 | deploy:34(refused) | release:1
your-health              commit:1 | push:3
your-sudoku              commit:0 | push:1
your-trainer             commit:42 | push:1 | release:11
yourtrainer-mcp          commit:0 | push:0
```

### A draft release three versions behind, found by running against the fleet

`your-trainer` carries **REL-0008 at `draft`, version 2.0.2**, while 2.0.5, 2.1.0 and 2.1.6 have all shipped since. The first implementation gated on it and said *"60 checks stand between 2.0.2 and shipping"* — about a version three releases in the past, and it would have said it **forever**, which is precisely the self-re-arming badge [[ADR-0027]] refuses and this whole phase exists to avoid producing.

`preparing()` now ignores a draft a shipped version has overtaken, and `stale_drafts()` names it instead — visible, not gating. It renders as its own group: *"Draft overtaken · REL-0008 2.0.2"*. Caught only because the ladder was walked against twelve real repositories rather than against fixtures.

### Two corrections from seeing it rendered

1. **The commit rung offered a verb.** Committing is the agent's job — close-out commits its own work ([[FEAT-0055]]) — and [[ADR-0027]]'s first admission test is that a *person* must discharge an obligation. The rung is state, not a debt, and now carries no verb.
2. **A rung at zero still asked.** `To push` claimed `needs_human` with nothing to push. Absent-at-zero applies to the *ask* as well as to the row.

### A pre-existing dead click, exposed

The acceptance suite's group header linked to `/tests/ACCEPTANCE_TESTS.md`. The renderer's `extractRel` accepts only `/docs/…` or `~…`, so the link did nothing — and it had been that way in `_acceptance_tier_groups` since TASK-0373, invisible because an empty tier is skipped before its url is ever used. TASK-0429's gate group renders at zero, so it surfaced. Both fixed.

### The gate

One obligation while a release is `draft`, zero otherwise, and **60 is a number it states rather than a number any badge sums**. Seven mutations run; six defeated a guard. The seventh — removing the `exists` check inside `_gate_rows` — is an **equivalent mutant**: a repo with no suite reports `blocked: False` anyway, so both branches agree. The check that actually decides whether the gate renders lives in `cockpit.py` and *is* guarded (`test_no_suite_says_never_instantiated_not_nothing_blocking`); its mutation fails. Recorded as equivalent rather than counted as a pass.
