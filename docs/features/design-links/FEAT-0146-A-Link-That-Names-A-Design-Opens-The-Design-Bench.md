---
type: "[[feature]]"
id: FEAT-0146
aliases: ["FEAT-0146"]
title: "A link that names a design's ID opens the design bench, not the design's note"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: 2026-09-12
source: ["Edwin, 2026-09-11, in a your-health session: 'Create the feature/requirement/tasks etc ... in the cockpit project to open the design bench whenever a link names a design's ID. So the cockpit LLM can take over.'"]
goal: "A person or an agent who sends a link naming a design's ID puts that design's mockups in front of the reader, instead of a page of text with a button."
requirements: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
tasks: ["[[TASK-0606-The-Design-Register-Decides-Where-An-ID-Opens]]", "[[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]]"]
release: ""
acceptance_exception: ""
acceptance: "[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"
design: ""
related: ["[[FEAT-0007-Desktop-Shell]]", "[[FEAT-0042-Design-Bench]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]", "[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[ISS-0041-Artifactless-Design-Is-Unreadable]]", "[[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]", "[[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]", "[[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]", "[[CHG-20260911-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-09-11
review_verdict: changes-requested
review_response: "All eleven findings acted on; the verdict stands as the reviewer recorded it. Findings 1, 7, 8 and 9 changed code: three guards now pin that every route still reaches locateAndOpen with the link's ID (the four one-line breaks the review found surviving are caught), both async reads check for a project switch after reading the reply rather than before, and a parked link is dropped — with a message — when the reader goes to a project the link never named (filed as ISS-0298 and added to TST-0085 as step 10). Findings 2, 3, 5 and 10 were wrong statements in notes and are corrected: REQ-0062's approval paragraph, FEAT-0093's narrowed criterion, TST-0084's case count (nine, not eight), and the CHG's Back claim, which now says Back is unchanged across a project switch. Finding 4: TST-0085 gains step 9 for Overview, and TST-0084's command runs test_cross_repo_links.py. Finding 11 is recorded in the CHG's 'Not changed': cockpit focus still opens the note. Finding 6 is the one not applied, and deliberately: ADR-0038 says a test note declaring a command: never reaches passing and the gate is discharged by the command resolving, so TST-0084 stays active — moving it to passing would be a validator error. TST-0084 now says so. Suite after the changes: 2246 passed, 6 skipped, 1 failed (the known unrelated test_release_evidence case)."
review_response_date: 2026-09-11
---

# A link that names a design's ID opens the design bench

## Status (2026-09-12): done

**Done.** Edwin approved [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] on 2026-09-12 and asked for close-out, so the requirement is `implemented` and this feature is `done`. One thing is still open and is NOT part of this feature: whether an in-repo `[[DES-####]]` wikilink should open the bench too (the question below). It was asked on 2026-09-11 and is unanswered; if the answer is yes it becomes its own task.

**Built and verified.** Both tasks are done, the requirement's six criteria are ticked with evidence, and [[CHG-20260911-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] records the change. The feature stays `doing` until Edwin approves [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]], which is still `draft`. The second thing is his answer to the open question below. A yes to it adds a third task.

The walk found two defects in switching project, both already in the tree, and both are fixed with this feature: [[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]] and [[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]. The independent review found a third, [[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]], also older than this feature, and it is fixed here too.

**The independent review returned `changes-requested` and all eleven findings were acted on.** The verdict stands; `review_response:` in this note's frontmatter says what was done for each. The substantial one was finding 1: the guards pinned that `locateAndOpen` asks the rule, and nothing pinned that links still reach `locateAndOpen`. Four one-line breaks to those routes passed every test. They are pinned now, and caught.

## Goal

`cockpit://your-health/DES-0002` should show the reader the design itself: its HTML page with the mockups. Today it opens the design's note instead. For a design, the note page shows the note's text and one button, "Open DES-0002 in the design bench". The mockups are only on the bench, the page `~design/DES-0002`.

> [!quote] As requested — 2026-09-11 (user:edwin)
> Create the feature/requirement/tasks etc ... in the cockpit project to open the design bench whenever a link names a design's ID. So the cockpit LLM can take over.

This follows [[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]], fixed the day before, which made a `cockpit://` link open the page it names at all. The bench address already works as a link: `cockpit://your-health/~design/DES-0002` showed DES-0002 with all 19 of its images, checked through a debugging port on 2026-09-10. But nobody writing a link should need to know that address. The design's ID is what a person or an agent has.

## Scope

**In scope:**

- `cockpit://<project>/<ID>` links, whether the project is already on screen or the link switches to it.
- Cross-repo `[[project#ID]]` links. The renderer resolves them in the same function as a `cockpit://` link, `locateAndOpen`, so one edit changes both. See "Decisions" for why they are included.
- A design with no artifact and no variants still opening its note.

**Out of scope:**

- **In-repo `[[DES-####]]` wikilinks.** This is the open question below.
- **Opening a design note by its path.** That remains a request for the note. It covers the bench header's ID chip, the bench's `Read <ID> as a note` button, an owed design's row on the Intent landing, and a link such as `cockpit://your-health/docs/designs/DES-0002-Recovery-And-Food.md`.
- **The search box and `cockpit focus`.** Neither is a link. `cockpit focus` arrives as a path the sidecar has already resolved.
- **The browser front door** (`python -m project_os_cockpit`, mode 1). It has no cross-repo link handling and no design bench.
- **A cold start.** If the cockpit is not running, `desktop/scripts/open-link.sh` starts it and the link is dropped, as [[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]] records.
- **Any change to the bench itself.** The bench page, its header and its sidebar stay as they are.

## Acceptance

The criteria are in [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]. What a person sees:

- `desktop/scripts/open-link.sh your-health DES-0002` shows DES-0002 on the bench, with its page and images. It does so from another project and from your-health itself.
- `desktop/scripts/open-link.sh project-os-cockpit DES-0003` opens DES-0003's note, because DES-0003 declares no artifact and no variants.
- In the cockpit repo, clicking `project-os-deck#DES-0001` in PHASE-028's frontmatter strip switches to project-os-deck and shows DES-0001 on the bench.
- Clicking the ID chip in the bench header opens the note, and the note stays open.
- A link that names a feature, an issue or any other ID that is not a design opens its note, as before.

The walk is [[TST-0085-A-Link-To-A-Design-Shows-The-Design]]. The automated half is [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]].

## How it will work

Two tasks, in this order:

1. [[TASK-0606-The-Design-Register-Decides-Where-An-ID-Opens]] adds a pure function to `desktop/src/renderer/deep-link.ts`. Given a note ID and the project's design register, it returns `~design/<ID>` when the ID is a design with something to show, and nothing otherwise. It is tested in node like the link parser beside it.
2. [[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]] makes `locateAndOpen` in `renderer.ts` fetch the register from the project on screen and ask that function before it asks `/api/cockpit/locate` where the note lives. Every link resolved by ID passes through `locateAndOpen`, from three places: a `cockpit://` link to the project on screen, a cross-repo link to the project on screen, and a link of either kind parked while the window switches project.

`navigateTo` does not change. That is the reason nothing that opens a design note by its path is affected.

## Decisions made in planning

**The design register decides whether an ID is a design.** The register (`GET /api/cockpit/designs`) is the list of notes whose type is `[[design]]`, so it reads the note's type rather than the `DES-` prefix. It also carries `asset` and `variants`, which say whether the bench has anything to show. The renderer already calls it, so the sidecar does not change. The prefix was rejected because it is a naming convention that cannot say whether an artifact exists. Adding `type` to `/api/cockpit/locate` was rejected because the renderer would still need the register, so it adds a request and changes an API that Deck shares. [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] states this at more length.

**A design with nothing to show opens its note.** "Nothing to show" means no `asset:` and no variant sections. A declared `asset:` whose file is missing still opens the bench, because the bench's "Artifact not found" message is how the tool reports that mistake.

**An owed design opens in the bench too.** your-health's DES-0002 is `proposed`, and the Intent landing's row for an owed design deliberately opens the note, where Accept is ([[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]). That rule is for a row that promises a verb. A link promises nothing but the design, and the note is one click away.

**The way back to the note is the ID chip that already exists.** The bench header's first chip is the design's ID, and it opens the note ([[ISS-0041-Artifactless-Design-Is-Unreadable]]). No new control is added. If the walk shows the chip is too easy to miss, that is a follow-up, not part of this feature.

**Cross-repo links are included.** They name a design's ID, which is Edwin's condition, and they share the code path. This narrows one criterion of [[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]] ("switches workspace and opens the note") for designs with something to show. If Edwin wants `cockpit://` links only, the cross-repo path would carry a flag through `pendingCrossRepoJump` that skips the rule. That is a small change to TASK-0607.

## Open question

**Should an in-repo `[[DES-####]]` wikilink open the bench too?** Edwin's sentence can be read to include it, and it is not built until he answers. It is a different piece of work from this feature. The sidecar writes an in-repo wikilink as a plain link to the note's file, so the renderer receives a path and never sees the ID. Several controls open a design note by path on purpose (listed under "Out of scope"). A rule keyed on the path would send those back to the bench. The way to build it is for the sidecar to mark each wikilink with the ID it was written with, and for the renderer to send only marked links through this rule. It would change what a click on a design link does everywhere a note is shown: the body, the frontmatter strip, the context pane and the backlinks. If Edwin says yes, it becomes a third task under this feature and a seventh criterion on REQ-0062.

## Phase

Homed in [[PHASE-005-Desktop-Shell]], reopened for it. `cockpit://` links are in [[FEAT-0007-Desktop-Shell]]'s scope, and yesterday's link fix, [[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]], lives there. [[PHASE-009-Design-Surfaces]] was considered and not chosen: the bench does not change, only how the shell resolves a link. This repo's CLAUDE.md says a single request joins the standing phase for the surface it touches rather than opening a new phase. PHASE-005 closes again when this feature is done.

## Risk scan

No trigger applies. There is no new dependency, environment variable, configuration surface, or change to a path or directory layout. Each link that names an ID costs one extra request, for the design register, which is a few kilobytes in a repo with a dozen designs. There is no new exposure either. A `cockpit://` link could already open the same bench page by naming `~design/DES-0002` as a path ([[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]), and the bench frames the artifact in the same sandboxed iframe either way.

## Impact analysis

Checked on 2026-09-11 against the features, requirements and issues that share this surface:

- [[FEAT-0007-Desktop-Shell]] lists deep links in scope. No conflict.
- [[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]: one criterion is narrowed for designs, as described under "Decisions". FEAT-0093 has no requirement, so no `REQ-*` is contradicted. This is the one place a reader could reasonably disagree, and it is listed for Edwin.
- [[FEAT-0042-Design-Bench]] and [[REQ-0023-Design-Is-A-Project-Record]]: the bench is only a destination here and does not change.
- [[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]: its rule that an owed design's landing row opens the note is kept. That row opens the note by path, which this feature does not touch.
- [[ISS-0041-Artifactless-Design-Is-Unreadable]]: its ID chip and `Read <ID> as a note` button are relied on as the way back to the note, and must keep working. REQ-0062's fifth criterion pins that.
- [[PHASE-029-One-Tool-Two-Front-Doors]]: the browser front door has neither cross-repo links nor a bench, so no new difference between the two front doors appears.
- Deck (`~/Dev/repos/project-os-deck`) shares the sidecar. No sidecar API changes. The capability register rows `shell.windows` and `shell.reader.render` get new wording in the same commit as the code, as this repo's CLAUDE.md requires.

## Independent review (2026-09-11, model:claude-opus-5): changes requested

**Verdict: changes requested.** The behaviour holds up: I found no input that makes a link open the wrong page, and nothing that opens a design note by its path can reach the bench. What needs changing is how much the tests and notes claim. Four one-line breaks to the link routes pass every automated test, and five notes say something that is not true of the tree.

**Independence.** This was a fresh session, started from the notes and the working tree, with no access to the authoring session's reasoning and no memory of writing any of it. It was not independent of the model: TST-0085 records the walk as `model:claude-opus-5`, the same model as this reviewer. Every finding below is marked **reproduced** (a command I ran, with what it printed) or **not reproduced** (read from the code, not run).

**What I checked and found true.** `npm run build` succeeded. `node --test desktop/tests/deep-link.test.mjs` printed 20 tests, 20 passing, 9 of them for `designBenchTarget`. `pytest tests/test_design_links.py tests/test_cross_repo_links.py tests/test_desktop_node_suite.py` printed 22 passed. All seven broken versions listed in TST-0084 that touch `renderer.ts` turned the tests red when I made them, and so did the ISS-0296 and ISS-0297 deletions. Four of the rule's broken versions were caught, plus two of my own: one that ignores variants and one that spells the bench address the way the link wrote it. Nothing opens a design note by path through the rule. The ID chip (`renderer.ts:5779`), `Read <ID> as a note` (`:5635`), the owed-design row (`:5931`) and a `cockpit://` path (`:3791`) all call `navigateTo` with a path, and `navigateTo` never asks the rule. The sidecar is unchanged. The register reads `type: "[[design]]"` and emits `asset` whether the file exists or not (`cockpit.py:1211-1228`). The repos match the walk: your-health DES-0002 and project-os-deck DES-0001 declare an asset, the cockpit's DES-0003 has `asset: ""` and no variants, and PHASE-028 carries `[[project-os-deck#DES-0001]]`. The validator reports 0 errors.

**Not verified.** The full-suite count (2243 passed) was not rerun, because the full suite was outside the commands this review was allowed to run. None of the TST-0085 walk was repeated, because the review was told not to drive the running window.

### Findings

1. **Reproduced: the tests pin one half of the chain REQ-0062 cites them for.** `tests/test_design_links.py` pins that `locateAndOpen` asks the rule. Nothing pins that links still reach `locateAndOpen`, or that the rule gets the link's ID. Each of these four edits passes all of `tests/test_design_links.py` and `tests/test_cross_repo_links.py` (mutation script over a scratch copy of `renderer.ts`, each printed `SURVIVED`): deleting the parked jump's call at `renderer.ts:1059`; deleting the same-project cross-repo call at `:868`; turning the same-project `cockpit://` note branch at `:3792` into `navigateTo(target.id)`; passing `project` instead of `noteId` to `designBenchTarget` at `:889`, which tsc accepts because both are strings. Each one breaks REQ-0062 criterion 1 or 2 in the window. TST-0084's "7 broken versions tried, 7 caught" is true of the seven it lists, but criterion 1's evidence reads "pinned by tests/test_design_links.py" for a route only the TST-0085 walk covers. Either add a guard over the three call sites and the argument, or say in the evidence that the routes are covered by the walk alone.
2. **Reproduced: REQ-0062 contradicts the feature's state.** REQ-0062 line 32 says "Approve this note, or amend it first, before FEAT-0146 moves to `doing`." FEAT-0146 is `doing`, and both of its tasks are `done`. The validator prints `WARN [REQ-PREMATURE] REQ-0062 is still draft but FEAT-0146 is already being implemented`. The sentence should say what is true now: the work was built before approval, and approval is what moves it to `implemented`.
3. **Reproduced: FEAT-0093 still states the old behaviour.** `docs/features/cross-repo-links/FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away.md:41` is a ticked criterion on a `done` feature: "Clicking it **switches workspace and opens the note**". For a design with an artifact, that is no longer what happens. FEAT-0146 and REQ-0062 say they narrow this criterion, but FEAT-0093 does not mention it, so anyone reading FEAT-0093 learns the old behaviour.
4. **Reproduced: ISS-0296 names a test that never exercises it.** ISS-0296's `tests:` lists only TST-0085, and none of TST-0085's eight steps puts the left pane in Overview mode. Its automated guard, `tests/test_cross_repo_links.py::test_a_skipped_overview_landing_still_loads_the_left_pane`, is in no TST note either. TST-0084's `command:` runs only `test_desktop_node_suite.py` and `test_design_links.py`, and its `issues:` lists only ISS-0297. Add an Overview step to TST-0085, or bring the guard into TST-0084's command and `issues:`.
5. **Reproduced: TST-0084 miscounts the new cases.** TST-0084 line 36 says "The eight cases are listed in TASK-0606", and line 47 says "the eight new ones included". The node run prints 9 `designBenchTarget` cases, which is the number TASK-0606 and the CHG give.
6. **Reproduced by reading: the close-out plan skips TST-0084.** The steps written for after approval, in the status section above and in SNAPSHOT's focus note, move REQ-0062 to `implemented` and FEAT-0146 to `done`. They never move TST-0084 to `passing`. TST-0084 is `active`, with `last_verified` and `last_run` empty. QUALITY.md's verification gate needs REQ-0062's tests at `passing` first, and a TST reaching `passing` is a review gate of its own.
7. **Not reproduced: the ISS-0296 fix has a small stale window.** `loadOverviewScopePane` (`renderer.ts:18275-18276`) compares `base` with `sidecarBaseUrl` before `await r.json()`, not after it. Suppose the reader switches project while the reply's body is still being read. The previous project's phases are then written to `scopePhaseList` and drawn, which is ISS-0296's own symptom. The pane corrects itself on the arriving project's next landing or pane load. Moving the comparison below the `json()` await closes the window.
8. **Not reproduced: ISS-0297 can still happen after a switch.** The reset at `renderer.ts:995` does not stop a `fetchDesignRegister()` already in flight from the previous project. That function reads `sidecarBaseUrl` before its await and writes `designRegister` after it (`:5596-5604`). A reply that arrives after the switch refills the list with the old project's designs, and the banner is missing again. The reset did not create this race, but the race is now the one remaining way to get ISS-0297's symptom.
9. **Not reproduced: an older bug now lands on the bench.** Suppose the reader picks a third project on the rail while a link's switch is still in progress. `openWorkspace` does not clear `pendingCrossRepoJump`, so whichever workspace reports ready next consumes the parked link. `locateAndOpen` never checks its `project` argument against the workspace on screen. Before this feature, the reader got the wrong project's note or a "has no DES-0002" message. Now they can get the wrong project's bench.
10. **Not reproduced: the CHG claims Back works after both kinds of link.** CHG-20260911 line 41 says "Back returns to the page you were on" after a link that switches project too. TST-0085 walks Back only in the same project (step 2). The history is one list of page paths shared by every workspace (`pushHistory`, `renderer.ts:2934`). After a link that switched project, Back therefore asks the new project's sidecar for the old project's page. That behaviour belongs to FEAT-0093, not this feature, but the CHG sentence claims Back for both cases.
11. **Observation for Edwin, not a defect.** `cockpit focus <ID>` is out of scope, as the "Out of scope" section says. An agent that takes over the window with `cockpit focus DES-0002` will still show the note. Agents drive the window this way more often than with a `cockpit://` link.
