---
type: "[[test]]"
id: TST-0022
aliases: ["TST-0022"]
title: "Surface ownership — every moved type is reachable, and Library is reduced"
status: passing
covers: ["[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[FEAT-0046-Plans-On-The-Feature]]", "[[FEAT-0047-Risks-On-The-Issues-Surface]]", "[[FEAT-0048-Changes-On-The-Overview]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[FEAT-0050-Library-Reduction]]", "[[ISS-0062-Most-Plans-Are-Invisible]]", "[[ISS-0063-Dead-Stat-Tiles]]"]
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-08-13
source: ["[[PHASE-010-Surface-Ownership]]"]
path: "tests/test_surface_ownership.py"
command: ".venv/bin/pytest tests/test_surface_ownership.py -q"
last_run: "2026-08-13T18:28Z"
exit_code: 0
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
last_verified: "2026-08-10"
---

# TST-0022 — Surface ownership

## Intent

[[REQ-0025]] gates [[FEAT-0050]] on a property nothing else in the toolchain checks: that removing a type's Library group did not make the type unreachable. The validator reads the corpus, not the UI. The existing payload tests assert group *shape*, which passes just as happily on a group that lost its contents.

This suite asserts reachability by **count against the corpus**, so a regression that silently drops rows fails rather than rendering a plausible shorter list — the exact failure mode of [[ISS-0062]], where a type-based lookup returned 14 convincing rows out of 33.

## Coverage

1. **Plans, by count.** Every feature's `plan/PLAN.md` resolves through the path-based lookup. Asserted against a **filesystem glob**, not a literal: the corpus was 33 plans / 14 typed when [[ISS-0062]] was filed and is 38 / 19 now that this phase added five features, so a frozen number would fail on the next feature created. A revert to `notes_by_type("plan")` fails here because the typed subset is smaller than the glob.
2. **Plans, untyped.** A feature whose plan has no frontmatter still yields a child row. Asserted on a real untyped plan from the corpus, not a fixture.
3. **Risks in the Issues mode.** The `issues` payload contains every `[[risk]]` record, and a corpus with no risks produces a payload byte-identical to the pre-change one.
4. **Changes payload.** `changes_payload` bucket labels and membership match what `_changes_subgroups` produced under Library, and the recent split does not lose an item — the union of recent + buckets equals the CHG record set.
5. **Tests register.** `review_queue_payload["registers"]["tests"]` has one entry per `[[test]]` note (22 here), while the `runs` queue group stays gated to manual-and-`ready` (1 here). Both counts are asserted so collapsing one into the other fails.
6. **Reviewed register.** One entry per note carrying a **non-empty** `review_verdict`, sorted most-recent-first. Two edge cases asserted in opposite directions: a note with a verdict but no `review_date` still lists (sorted last); a note declaring `review_verdict: ""` does **not**, because an empty verdict is the absence of one and counting it would overstate how much of the corpus has been reviewed. **No count is quoted, deliberately** — this one moved three times in two days (six, then 12 at `bed48ea`, then 10) because every review, including the review of this note, changes both populations. The test counts from the index; a figure written here is stale before it is read.
7. **Library reduction.** `nav_payload(mode="library")` group keys are a subset of `{pinned, docs-tree}`.
8. **Auto-discovery survives** — asserted by `test_library_auto_discovery_still_works_for_vault_types` in **`tests/test_cockpit.py`**, not in this file. A synthetic corpus with ≥5 notes of an unknown type still gets its `by-type:` group, so the reduction removes canonical-type groups without removing the discovery mechanism. Attribution corrected in round three: this register named a test that does not live here, which is the same error item 9 was corrected for one round earlier.
9. **Workflows in the tree.** Asserted by a **pair**, and only the pair carries the property. `test_workflows_browse_in_the_docs_tree` (this file) checks the `workflows/` folder *label* against the real corpus — and passes even with `workflow` removed from `DOC_TREE_INLINE_TYPES`, because `docs/workflows/README.md` is untyped and creates the folder unaided. `test_workflows_join_the_docs_tree` (`test_cockpit.py`) builds a synthetic corpus with a typed WF note and no README, so it catches that. Recorded this way after independent review found the original wording crediting the corpus test with the stronger claim.
10. **Desk section naming and order** ([[ISS-0064]]). Exactly one section heading is `Reviewed`, and the pane order is Queue → Reviewed → Tests. Source-level, because both registers are appended at the tail of one function — the order is positional, so the next append in the obvious place reshuffles it with nothing failing. That is how ISS-0064 happened.
11. **The advisory tally is gone** ([[ADR-0007]] settled, [[TASK-0247]]). Renderer *and* stylesheet, since a stylesheet keeping selectors for a deleted block is how CSS rots. Deliberately does **not** assert the payload: `outcomes`/`reviewed` still ship and `test_queue_reports_the_advisory_phase_tally` still guards them — the recording survives the surface.

12. **Decisions have a payload of their own** ([[ISS-0065]]). Set-equality with `notes_by_type("adr")` ∪ `notes_by_type("decision")`, **and** every entry's `rel` must resolve on disk — an id-only version of this test passed a mutation that blanked every `rel`, which would empty the card exactly as ISS-0065 did.
13. **The record column does not harvest a nav mode** ([[ISS-0065]]). Source-level, and named as such: it asserts where `fillRecordColumn` looks, because a count test cannot catch this — the payload was well-formed and every test passed while the card was empty.
14. **The nav-harvest helper is gone.** `fetchRecordNotes` had three consumers depending on a nav mode's *contents*; it is deleted, and this fails if it returns.
15. **The cross-process route contract** ([[ISS-0065]] re-review). Each route literal must appear in **both** `server.py` and the renderer, plus one test that fetches `/api/cockpit/decisions` through the real handler on an ephemeral port. Nothing previously compared the two spellings: a typo on either side emptied a card silently.
16. **The quick palette covers every type-bearing mode.** The Cmd+P near-miss had prose and no test; `QUICK_CORPUS_MODES` plus the register and changes fetches are now asserted.
17. **The skip-set is not derived from the empty tuple** — `test_the_skip_set_is_not_derived_from_the_empty_tuple`. `_BY_TYPE_SKIP_IN_LIBRARY` used to be computed from `LIBRARY_RARE_TYPES`; emptying that tuple without rewriting the skip-set would let every canonical type clearing `_BY_TYPE_MIN_COUNT` reappear under a `by-type:` key — the whole reduction undone through the back door with nothing failing. Cited by name in [[REQ-0025]] criterion 8 and missing from this register until round three.
18. **The stat tiles** ([[ISS-0063]], which this note declares in `verifies:`). `test_every_stat_tile_has_a_destination` over the five live tiles, `test_the_reqs_tile_stays_dead_on_purpose` for the one deliberate exception, and `test_every_stat_tile_lands_where_its_type_lives` parametrised over all five. Source-level over `buildStatTile` call sites, so a call site that drops its `navMode` argument fails — while setting `navMode = undefined` *inside* the function does not (disclosed under Adequacy). Cited by name in [[REQ-0025]] criterion 2 and [[PHASE-010]] exit criterion 3, and absent from this register for three rounds.

    **Rewritten 2026-08-10 ([[TASK-0371]]).** The old assertion named the mode string — Risks→`issues`, Tests→`review` — and by that morning both were wrong: Tests still pointed at the review desk after the Tests view existed, and risks had left the Issues navigator for the constraints view ([[ISS-0128]]) while their tile went on pointing at it. A test that pins the mechanism passes happily while the destination rots. The replacement renders the mode the tile points at and requires the tile's own type to be in it, against the real corpus — the property, not the spelling.

## Evidence

```
$ .venv/bin/pytest tests/test_surface_ownership.py -q
27 passed in 0.82s

$ .venv/bin/pytest -q
559 passed, 1 skipped
```

Payloads confirmed end to end over HTTP against this repo's own corpus, on a sidecar started from `src/` — **snapshot taken 2026-07-30, after the ISS-0065 fix**:

```
$ curl -s localhost:8899/api/cockpit/nav?mode=library   → groups: ['docs-tree']
$ curl -s localhost:8899/api/cockpit/nav?mode=issues    → critical 1, high 16, medium 40, low 8,
                                                          risk:high 1, risk:medium 2, risk:low 1
$ curl -s localhost:8899/api/cockpit/nav?mode=features  → 38 plan child rows
$ curl -s localhost:8899/api/cockpit/changes            → total 98, recent 6, buckets partition the rest
$ curl -s localhost:8899/api/cockpit/decisions          → total 8
$ curl -s localhost:8899/api/cockpit/review-queue       → tests 22, reviewed 76, queue 0
```

**These are a dated snapshot, not invariants, and three of them move on their own.** `reviewed` grew 62 → 76 during the reviews of this very note; `changes` grew as CHG notes landed; the issue counts grew with ISS-0062..0065. The tests assert against the live index rather than these figures — for the same reason coverage item 6 quotes no count at all. A reader comparing this block to a fresh run should expect drift and check the assertions instead.

## Adequacy

The count assertions are equalities against the live corpus rather than non-emptiness checks, which is what distinguishes this from the payload-shape tests already in `test_cockpit.py`. A group that renders but has lost half its rows passes those and fails these.

**Not covered by the automated suite:** that a rendered payload is actually *visible* in the UI. These tests assert the data reaches the payload; whether the renderer draws it is the manual pass below, and **both cockpit reachability bugs in PHASE-009 were renderer-side with correct payloads**.

The renderer is covered here only by `tsc` and by two source-parsing assertions (the stat-tile destinations). Neither runs the DOM. A tile that is built and never appended, a register appended to a detached node, a row whose click handler never fires — every one of those passes everything automated in this suite. The 2026-07-29 manual run bears that out: it found a layout defect (`Changes97`) that every automated assertion passed over.

**Still not covered, even after the manual run:** visual appearance beyond the one measured layout property. The pass asserted structure and geometry over CDP — element presence, counts, computed `display`, click destinations — not that the tile *looks* right. That remains a human judgement.

## Steps

Run against a restarted app on 2026-07-29 — see `## Runs`. The first attempt that day was abandoned: the shell command meant to launch a throwaway Electron instance failed (`timeout` is not present on macOS), so the CDP session attached to **Edwin's own running app** instead of a new one. Its sidecars had been up since 10:44 and served pre-change code, which is why the Changes tile read as absent. That window's `sidecarBaseUrl` and route were altered and then restored; the run was stopped rather than continued against a live instance, and the app was restarted before the real pass.

One thing that first attempt established by accident and worth keeping: against an **older sidecar with no `/api/cockpit/changes`**, the tile removes itself rather than rendering an empty box — TASK-0240's degradation requirement, observed rather than assumed.

1. Open the Features mode. Pick a feature whose plan has no frontmatter (e.g. `agent-verbs`). Confirm the plan row appears under it and opens.
2. Open the Issues mode. Confirm the four RISK notes appear, grouped by severity, distinguishable from issues.
3. On the overview, click the Risks tile — confirm it navigates to the constraints (Design) view and risks are there. Click the Tests tile — confirm it navigates to Tests and the register is there. *(Rewritten 2026-08-10, [[TASK-0378]]: both destinations moved, and the point of the step is that a tile lands where its type lives — not that it lands on a particular mode.)*
4. On the overview, find the Changes tile. Confirm recent changes are visible and an older bucket opens.
5. **The registers, at their new homes** *(rewritten 2026-08-10, [[TASK-0378]] — the desk they were on no longer has a button)*. Open **Tests**: confirm every `TST-*` is listed, grouped by verification state, and that the tier groups from `ACCEPTANCE_TESTS.md` follow them. Then on the project **overview**, read the right pane: confirm a `Reviewed` card reporting the verdict count and how many are still owed.
6. Open the Library mode. Confirm it shows Pinned and the Docs tree, that `workflows/` is in the tree, and that the pane is not empty.
7. **No two surfaces share a heading word, and nothing points at the desk** *(rewritten 2026-08-10, [[TASK-0378]])*. The original step read the desk's left pane top to bottom for the `Reviewed`-twice collision [[ISS-0064]] found. The desk has no button now, so the question moves with the registers: confirm the top bar offers **no Review button**, that a stored `cockpit:nav-mode` of `review` lands on the overview rather than nowhere, and that the overview's `Reviewed` card is the only surface using that word. The ledger link under it appears only when an agent request is genuinely open — confirm it is absent when the queue is empty.

    The original observation still stands and is why this step exists: step 5 checked both registers existed and was blind to what they were called or where they sat. A reachability check inherits the blind spots of the requirement it came from.

8. **Back on the project overview, read the right pane.** Confirm a `Decisions` card listing ADRs (with an `N older` disclosure when there are more than four) and a `Verification` card showing `passing/total`. Added after [[ISS-0065]] — the checklist had seven steps and none of them looked at the record column, which is why a phase that emptied it passed a full manual pass. The check was performed while fixing the issue; this is the version that gets re-run.

## Runs

### 2026-07-29 — PASS (6/6), driven over CDP against a restarted app

Sidecar `127.0.0.1:8765` from a clean restart; renderer from `dist/` at 18:47.

1. **Plan rows** — PASS. 38 `plan/PLAN.md` child rows across the Features mode, including untyped ones (`features/agent-verbs/`, `features/agent-hooks/`, `features/task-dispatch/` all present with no `data-status`). With Edwin's hide-completed setting on, 6 remain visible — `done` plans hide like any other completed item, which is correct rather than a miss. Child-toggle labels read `1 requirement`, `plan`, `1 requirement · plan`.
2. **Risks in Issues** — PASS. Groups `Risks · high` / `Risks · medium` / `Risks · low`, 4 risk rows, each carrying `data-type=risk` so the shield icon distinguishes them from issues.
3. **Tile click-through** — PASS. Risks tile → `issues`; Tests tile → `~review`. Tile strip reports `Features → · Tasks → · Reqs (dead) · Tests → · Issues → · Risks →`, with Reqs deliberately inert.
4. **Changes tile** — PASS. Present in the history band between Activity and Commits. 5 recent rows expanded, 3 collapsed top-level buckets (`Last week · 24`, `Earlier this month · 20`, `May 2026 · 48`), the May bucket nesting its own week sub-buckets.
5. **Desk registers** — PASS. `Tests · 22/22` (22 rows) and `Reviewed · 62` (62 rows), both rendered beneath the queue.
6. **Library** — PASS. `Docs tree` only, containing `reference/`, `references/` and `workflows/`.

**One defect found and fixed during the run.** The Changes tile's count rendered as `Changes97` — glued to the title, because tile `h3`s are `display: block` and the count's `margin-left: auto` does nothing there. Fixed with `.ov-changes h3 { display: flex; align-items: baseline; }`; re-verified `display: flex` and the count flush to the right edge (0px offset). This is exactly the class of defect the automated suite cannot see, which is why these steps exist.

**A second defect this run missed, and Edwin caught by looking** ([[ISS-0064]]). Step 5 asserted both registers were present and populated, which they were — and said nothing about their order, or about the pre-existing ADR-0007 tally a few rows above the Reviewed register also being headed `Reviewed`, with a different count (1 against 62). The step was derived from [[REQ-0025]], which asks whether a type is *reachable*; by that measure nothing was wrong. Legibility was never in its scope, and a checklist inherits the blind spots of the requirement it came from.

### 2026-07-29 (second run) — desk section order, PASS

After [[TASK-0246]]. Direct children of `.review-queue` in document order: `HEADING: Queue`, `meta review-queue-empty`, `TALLY: Outcomes · 1`, `REGISTER: Reviewed · 62`, `REGISTER: Tests · 22/22`. `reviewedHeadingCount: 1`.

### 2026-07-29 (third run) — tally removed, PASS

After [[TASK-0247]] and [[ADR-0007]] settling. `tallyPresent: false`; pane headings are exactly `Queue`, `Reviewed · 62`, `Tests · 22/22`.

Worth noting against the second run: the `Outcomes` rename was the right fix for the collision and the wrong fix for the underlying problem. Renaming made two sections legible; asking what the section was *for* made one of them unnecessary. Edwin's question ("there is nothing for me to select there") got further than the bug report did.

### 2026-08-10 — passing (by model:claude-opus-5)
- **pass** · Re-run for REL-0001 release verification: `.venv/bin/pytest tests/test_surface_ownership.py -q` — 44 passed in 2.94s

## Independent review — 2026-07-30, changes-requested

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea` with no access to the authoring session. I did not re-read this suite for plausibility; I broke the implementation twelve ways and recorded which mutations it caught.

**`status: passing` is earned for the automated part.** `.venv/bin/pytest tests/test_surface_ownership.py -q` → `20 passed in 0.26s`, reproduced. Full suite `552 passed`; `tsc` clean; validator clean. (The one full-suite failure I saw, `test_desktop_build_is_not_stale`, was an mtime artefact of my own `git checkout` and not a defect.)

**Mutations caught (10 of 12).** Reverting `_feature_plan` to a slug-matched `notes_by_type("plan")` lookup → 2 failures, so the ISS-0062 guard is real. Filtering the tests register to commanded tests → caught. Sourcing the reviewed register from `notes_by_type("change")` → caught. Dropping one item from the changes recent split → caught. Removing `navMode` from the Risks tile, from the Tests tile, and pointing the Risks tile at the wrong mode → all caught. Swapping the two register appends → caught. Re-adding `.review-tally` rules to the stylesheet → caught. Re-admitting a high-count type to `LIBRARY_RARE_TYPES`, and gutting the `_BY_TYPE_SKIP_IN_LIBRARY` literal → caught. Re-adding `workflows` to `DOC_TREE_EXCLUDED_ROOTS` → caught. The partition assertion is **not** tautological: rewriting `total` to be derived from the split leaves the third term (`len(list(notes_by_type("change")))`) still independent.

**Mutations missed (2), both worth recording rather than fixing blindly.** Setting `navMode = undefined` at the top of `buildStatTile` — the exact mechanism of ISS-0063 — passes all 20, because the assertions read the call sites, not the behaviour. That is disclosed in `## Adequacy` and I would not call it an overclaim, but the REQ-0025 criterion it backs says the tile "navigates there", which only the manual step establishes. And `test_the_reqs_tile_stays_dead_on_purpose` misses a destination added with a trailing comma (`mix.requirements, 'features',\n    )`), because its regex anchors on `,\s*'[a-z]+'\s*\)$`.

**Corrections needed in this note.**

1. **Coverage item 6 states a corpus fact that is false in the corpus this note ships with.** "six such notes exist, and counting them would report 68 reviewed where 62 were reviewed" — the index sees **12** records with `review_verdict: ""` at `bed48ea` (74, not 68), because this commit added five of them, including this note's own frontmatter. The *behaviour* asserted is correct and `test_an_empty_verdict_is_not_a_reviewed_item` guards it; only the numbers are stale. [[FEAT-0049]] carries the same "further six notes" sentence.
2. **Coverage item 9 overstates what its test checks.** "The Docs-tree group contains a `workflows` folder holding the WF notes" — `test_workflows_browse_in_the_docs_tree` asserts only the folder *label*, and passes against this corpus even with `workflow` removed from `DOC_TREE_INLINE_TYPES`, because `docs/workflows/README.md` is untyped and creates the folder on its own. The companion `test_workflows_join_the_docs_tree` in `test_cockpit.py` does catch it, so [[REQ-0025]]'s criterion 7 is properly evidenced by the pair — but this note should not credit the corpus test with the stronger property.
3. **Seven steps, described as six.** The `## Steps` list has seven; the first run heading reads `PASS (6/6)` and [[CHG-20260729-Surface-Ownership]] says "six manual steps". Step 7 is covered by the second and third runs, so the coverage is real; the count is not.
4. **The `## Evidence` curl block is a point-in-time record, not the committed state** — `total 96, recent 4` where the committed corpus is 98/6, and the manual run separately reports `Changes97`. Three different snapshots of a growing corpus is fine; label them as timestamped observations so a reader does not read them as assertions.

**The coverage gap that matters most.** Neither the 20 automated assertions nor any of the seven manual steps looks at the overview's right-hand **record column**. That is the surface [[REQ-0025]] criterion 5 makes a claim about, it is the only criterion with no test and no step, and it is the one that turned out false: `fillRecordColumn` sources its ADRs and tests from `mode=library`, which the reduction empties, so the Decisions and Verification cards are gone. A step 8 reading the project-scope overview's right pane top to bottom would have caught it in the same way step 7 caught the heading collision — and for the same reason, that a checklist derived from "is the type reachable" never asks "is every consumer of the payload I emptied still fed".

## Re-review — 2026-07-30, changes-requested upheld

Two of my four corrections landed. **The `passing` status is not cleared**, and the reason is not the code — the [[ISS-0065]] fix is real and I verified it over HTTP. It is that this note no longer describes the suite it names, and the checklist that exists specifically to catch renderer-side reachability still does not look at the surface that just broke.

**Done.** Coverage item 6's stale count is gone and replaced with an invariant plus an explanation of why no figure belongs there — a better fix than the one I asked for. The seven-step count is corrected in [[CHG-20260729-Surface-Ownership]], with the six-then-seven history noted; the `PASS (6/6)` heading is fair for a run that predates step 7.

**Still open, and each is why the status stays blocked:**

1. **`## Coverage` lists 11 items for a 24-assertion file.** The four [[ISS-0065]] guards — `test_decisions_have_a_payload_of_their_own`, `test_the_record_column_does_not_harvest_a_nav_mode`, `test_the_nav_harvest_helper_is_gone`, `test_the_quick_palette_covers_every_type_bearing_mode` — are described in [[ISS-0065]] and nowhere in the note that is supposed to be the register of what this suite covers. A test note whose Coverage section omits a fifth of its own assertions cannot be read as the handoff surface.
2. **`## Evidence` is now doubly stale** — it shows `20 passed` and `552 passed, 1 skipped` where the tree gives 24 and `556 passed, 1 skipped` (reproduced). Refresh it and label the curl block as a dated observation, the same treatment item 6 just received. Coverage item 5 still quotes "22 here" / "1 here" as literals and should get it too, for consistency.
3. **Coverage item 9 still overstates its test.** "The Docs-tree group contains a `workflows` folder holding the WF notes" — `test_workflows_browse_in_the_docs_tree` asserts the folder *label* only, and passes against this corpus with `workflow` removed from `DOC_TREE_INLINE_TYPES` because `docs/workflows/README.md` creates the folder unaided. The companion in `test_cockpit.py` carries the real property; this note should credit the pair, not the corpus test.
4. **No step 8.** This is the one that matters. The manual checklist has seven steps and none reads the overview's right-hand record column — the surface [[REQ-0025]] criterion 5 claims a property of, and the one that was silently empty through a full phase and a full review. The author *performed* that check while fixing [[ISS-0065]] (`Decisions 8 · all accepted`, `Verification 22/22`) but recorded it in the issue, so the checklist that gets re-run next time still has the hole. Write it down: read the project-scope overview's right pane top to bottom, confirm Decisions and Verification render with their counts.

**And a limit to record rather than fix.** The new renderer→sidecar wiring is guarded structurally, not behaviourally. Four realistic breakages pass all 24 assertions while emptying a card silently behind its `length > 0` guard: a payload emitting items without `rel`; an endpoint-path typo on either the renderer or the server side; `fetchDecisions` returning empty; `fetchTestsRegister` reading the wrong register key. Nothing asserts that `server.py`'s route string and `renderer.ts`'s fetch string agree — a new cross-process contract with no guard. Detail on [[ISS-0065]]. `## Adequacy` should say this in its own words; the section is otherwise the most honest part of the note and it should stay that way.

**On the two misses you asked about — neither should block, and I would not patch either.** Setting `navMode = undefined` inside `buildStatTile` is not a plausible accident; the plausible regression is dropping the argument at a call site, and that *is* caught. The trailing-comma hole is in a decision-marker assertion, and its worst case is a deliberately inert tile silently gaining a destination — an improvement-shaped bug. Both are correctly disclosed in `## Adequacy`. Patching them would mean writing assertions that claim more than they check, which is the failure this suite is otherwise unusually good at avoiding.

## Round three — 2026-07-30, changes-requested upheld

You asked me to judge the document and name items, so: **three named items, all in `## Coverage`, plus one in `## Evidence`.** Nothing about the code, the guards, or step 8 is in question — I re-ran the mutations and the new guards hold. This is solely that the register still does not describe its own file.

**Step 8 is right**, including the sentence explaining why it exists. Item 9 is now exactly right and sets the standard the items below fail: it says which half lives in which file. Item 6's "no count, deliberately" was the better fix and item 12's `rel`-resolution note earns its place.

**The named items.**

1. **Item 8 attributes a test in another file to this one — the same error item 9 was just corrected for.** "Auto-discovery survives. A synthetic corpus with ≥5 notes of an unknown type still gets its `by-type:` group" describes `test_library_auto_discovery_still_works_for_vault_types`, which is in `test_cockpit.py:504`. There is no auto-discovery test in `tests/test_surface_ownership.py`. Either label the file as item 9 does, or move the item.

2. **`test_the_skip_set_is_not_derived_from_the_empty_tuple` has no Coverage entry at all.** It is arguably the most consequential guard in the file — it is what stops the entire reduction being undone through the back door by emptying `LIBRARY_RARE_TYPES` without rewriting the skip-set — and [[REQ-0025]] criterion 8 cites it by name as "the back-door regression". Item 7 covers `test_library_is_pins_and_the_tree`; nothing covers this.

3. **The stat tiles are absent from all 16 items.** The two tile-destination parametrisations (under the name they carried until 2026-08-10 — see item 18) and `test_the_reqs_tile_stays_dead_on_purpose` are 3 of the 27 assertions. They cover [[ISS-0063]], which this note declares in `verifies:`, and they are cited by name in [[REQ-0025]] criterion 2 and [[PHASE-010]] exit criterion 3. A reader checking those criteria against this register finds nothing. This gap predates the [[ISS-0065]] work — my round-two finding named the four new guards as the omission and missed these, which is my error to own, not a new regression.

   Note when writing it: the honest entry says the assertions read the **call sites**, so a `buildStatTile` that stopped honouring `navMode` would pass — the limit already recorded in `## Adequacy`.

   (`test_a_feature_without_a_plan_gains_no_placeholder` is also undescribed; folding it into item 1 or 2 is enough.)

4. **`## Evidence`'s curl block is still unlabelled and is now further out of date.** The pytest figures are refreshed to 27/559, correctly. The block below them still reads `total 96, recent 4` and `reviewed register 62`; the corpus gives **98 / 6** and **76** — the reviewed count moved because this review stamped verdicts, which is the same mechanism item 6 already documents so well. Date the block as an observation, or drop the counts from it as item 6 does. Presenting it unlabelled beside a refreshed pytest run reads as current.

**Why this is worth a third round rather than a follow-up.** `status: passing` on this note is what [[REQ-0025]] and five features lean on, and `## Coverage` is the register a future reader checks a criterion against. Criterion 5 was ticked against nothing and survived a full phase; the mechanism was a claim with no register entry behind it. Items 2 and 3 are exactly that shape — two criteria in other notes cite tests this register does not list. Item 1 is the error you just corrected one item away. All four are edits, not work.

**Two limits I am explicitly not asking you to close.** The `registers.reviewed` swap and — see [[ISS-0065]] — `fetchDecisions` swallowing a good response, which is still undisclosed and belongs in the same paragraph. Both are renderer-side data handling that only a DOM test would catch, and `## Adequacy` is the right place for them. Closing them with source-string assertions would create guards that pass when the wiring is wrong-but-spelled-right, which is worse than the gap because it looks like coverage.

## Round four — 2026-07-30, approved

All four items closed, and I checked each by mutation or measurement rather than by reading.

**Item 1.** Coverage item 8 now names `test_library_auto_discovery_still_works_for_vault_types` in `tests/test_cockpit.py`. Confirmed it lives at `test_cockpit.py:504` and not in this file. Item 9's standard is now applied consistently, and every cross-file reference in the register (items 8, 9, 11) is attributed.

**Item 2.** Item 17 is accurate: gutting the `_BY_TYPE_SKIP_IN_LIBRARY` literal fails two tests.

**Item 3.** Item 18 is accurate in both directions, which is the part that matters — dropping `navMode` at the Risks call site fails, and the disclosed gap (setting it `undefined` inside `buildStatTile`) is real and correctly excluded from the claim.

**Item 4.** The Evidence block is re-measured and dated. I re-ran all six payloads against a live sidecar: five match exactly (`['docs-tree']`; 38 plan rows; changes 98/6; decisions 8; tests 22, reviewed 76, queue 0), and issues drifted by one — `medium` is 41 now, recorded as 40. That drift *is the label working*: the block says three of these move on their own and tells the reader to expect it, and it moved between the two measurements. I would not treat that as a defect.

**On your first question — keep the Evidence figures.** The trade is right, and the distinction that makes item 6 and this block both correct is what the numbers are *for*. Item 6's count was load-bearing: it was cited as the reason an assertion was right, so a stale figure there corrupts an argument. The Evidence figures are provenance — proof the payloads were exercised end to end, which prose genuinely cannot supply — so a stale figure costs a reader nothing once it is dated and flagged as drifting. Different jobs, different rules. Cutting them would remove the only evidence in the note that the HTTP surface was ever exercised.

**On your second question — no, and the shape of the rounds is the answer.** Round one found a live defect: eight ADRs unreachable, four notes asserting the opposite. Round two found a false claim in a code comment and a wrong measurement. Round three found three missing register entries gating a terminal status. Round four found nothing wrong with anything claimed. The instances shrank by roughly an order of magnitude each round. A review that keeps finding *equally large* problems is a treadmill; one that finds geometrically smaller ones is converging, and this one has converged.

Your format hypothesis is the more interesting finding, and I think it is half right. The register is not too large — 18 items is readable. The problem is that it **duplicates what the test file's docstrings already say**, so the two can drift, and only one of them is checked by anything. Every gap in rounds three and four was a drift between file and note, not a misunderstanding. That has a mechanical answer, and it is the move this phase already learned twice: guard the register, not the prose. One assertion — every test collected from `tests/test_surface_ownership.py` is either named in `## Coverage` or covered by an item that says which other file it lives in — would have caught items 2 and 3 without a human, and it is the check I ran by hand this round.

The evidence for that is not only your side. My round-two finding named the four ISS-0065 guards as the Coverage omission and **missed the stat tiles and the skip-set entirely**. So the register drifted, and the reviewer's own enumeration of the drift was itself incomplete. Two hand-maintained enumerations of the same file, both wrong in different places, is a strong argument that neither should be hand-maintained.

I am recommending that rather than filing it: it is not a defect in this work, and allocating an ID for a format improvement is a planning call, not a reviewer's. It would sit naturally as a small follow-up under verification tooling.

**One new observation, out of this phase's scope and not blocking.** Sweeping individual notes rather than types — which I only started doing in round three — turns up three task notes with no frontmatter at all: `TASK-0182`, `TASK-0183`, `TASK-0187`, under `features/*/plan/tasks/`. `notes_by_type("task")` misses them and `features/` is a `DOC_TREE_EXCLUDED_ROOTS` root, so they reach no surface — the exact [[ISS-0062]] mechanism, surviving for the task type. [[REQ-0025]] is written about types and 245 of 248 tasks are reachable, so nothing here is violated. But it is the same fix ([[ISS-0062]]'s "read the path, it already encodes the relationship") not yet applied to tasks, and it is worth someone's decision rather than rediscovery.

Nothing else. `status: passing` is earned: 27 assertions, mutation-verified across four rounds, with the two renderer-side limits named in `## Adequacy` rather than closed badly.
