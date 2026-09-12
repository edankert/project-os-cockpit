---
type: "[[change]]"
id: CHG-20260911-A-Link-That-Names-A-Design-Opens-The-Design-Bench
aliases: ["CHG-20260911-A-Link-That-Names-A-Design-Opens-The-Design-Bench"]
title: "A link that names a design's ID now opens the design bench, not the design's note; and a link that switches project no longer leaves the left pane or a design note's banner behind"
status: merged
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
source: ["Edwin, 2026-09-11, in a your-health session: 'Create the feature/requirement/tasks etc ... in the cockpit project to open the design bench whenever a link names a design's ID. So the cockpit LLM can take over.'"]
commit: "a6a33a6"
pr: ""
impacts: ["desktop/src/renderer/deep-link.ts", "desktop/src/renderer/renderer.ts", "desktop/tests/deep-link.test.mjs", "tests/test_design_links.py", "tests/test_cross_repo_links.py", "docs/reference/cockpit-capability-register.md"]
issues: ["[[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]", "[[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]", "[[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]]"]
features: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
requirements: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-09-11
review_verdict: changes-requested
review_response: "All eleven findings acted on; the verdict stands as the reviewer recorded it. Findings 1, 7, 8 and 9 changed code: three guards now pin that every route still reaches locateAndOpen with the link's ID (the four one-line breaks the review found surviving are caught), both async reads check for a project switch after reading the reply rather than before, and a parked link is dropped — with a message — when the reader goes to a project the link never named (filed as ISS-0298 and added to TST-0085 as step 10). Findings 2, 3, 5 and 10 were wrong statements in notes and are corrected: REQ-0062's approval paragraph, FEAT-0093's narrowed criterion, TST-0084's case count (nine, not eight), and the CHG's Back claim, which now says Back is unchanged across a project switch. Finding 4: TST-0085 gains step 9 for Overview, and TST-0084's command runs test_cross_repo_links.py. Finding 11 is recorded in the CHG's 'Not changed': cockpit focus still opens the note. Finding 6 is the one not applied, and deliberately: ADR-0038 says a test note declaring a command: never reaches passing and the gate is discharged by the command resolving, so TST-0084 stays active — moving it to passing would be a validator error. TST-0084 now says so. Suite after the changes: 2246 passed, 6 skipped, 1 failed (the known unrelated test_release_evidence case)."
review_response_date: 2026-09-11
related: ["[[TASK-0606-The-Design-Register-Decides-Where-An-ID-Opens]]", "[[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]]", "[[CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]"]
---

# A link that names a design opens the design bench

## Summary

`cockpit://your-health/DES-0002` now shows DES-0002 on the design bench: its HTML page with the mockups. Until now it opened the design's note, which for a design is text and one button, "Open DES-0002 in the design bench". A cross-repo link such as `[[project-os-deck#DES-0001]]` does the same.

A design that has nothing for the bench to show still opens its note. "Nothing to show" means the note declares no `asset:` and no `## Variant` sections, like the cockpit's own DES-0003.

```bash
desktop/scripts/open-link.sh your-health DES-0002             # the bench
desktop/scripts/open-link.sh project-os-cockpit DES-0003      # the note: nothing to show
desktop/scripts/open-link.sh your-health docs/designs/DES-0002-Recovery-And-Food.md   # the note: a path means the file
```

Two defects in switching project were found while checking this, and are fixed here too. **A link that switched project while the left pane was in Overview left that pane unloaded** ([[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]). **After a switch, a design note was drawn without its banner** ([[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]).

## What a person sees

- A link naming a design with an artifact or variants opens `~design/<ID>` in that project, whether the link switches project or the project is already on screen. Within a project, Back returns to the page you were on. After a link that switched project, Back behaves as it did before this change: the history is one list of page paths shared by every workspace, so it asks the project now on screen for the previous page. That belongs to [[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]] and is untouched here.
- A link naming any other ID opens its note, as before.
- Everything that opens a design note by its path still opens the note. That covers the `DES-####` chip in the bench header, the bench's `Read <ID> as a note` button, an owed design's row on the Intent landing, and a link that names the note's file. The chip is the way from the bench to the note.
- If the project's design register cannot be read, a design's ID opens its note.
- A link that switches project in Overview mode now lists the arriving project's phases in the left pane. Before, the pane said "Pick a workspace", or listed the previous project's phases under the new name.
- A design note opened right after a project switch shows its banner again: "This note describes a design", or "This design has no artifact yet."

## What changed

- `desktop/src/renderer/deep-link.ts` gains `designBenchTarget(noteId, designs)`, a pure function. It returns `~design/<ID>` when the ID matches a register entry, ignoring case, and that entry declares an `asset` or at least one variant. Otherwise it returns `null`. The register decides whether an ID is a design, not the `DES-` prefix. It reads `asset`, not `has_asset`, so a declared artifact whose file is missing opens the bench, and the bench reports the missing file.
- `locateAndOpen` in `renderer.ts` asks that function first, with a register it fetches from the sidecar on screen through the new `designsForLink`. Every link resolved by ID passes through `locateAndOpen`: a `cockpit://` link, a cross-repo link, and either kind parked while the window switches project. `navigateTo` is unchanged, which is why nothing that opens a note by path is affected.
- `designsForLink` does not use the cached register (`fetchDesignRegister`), which keeps the last good list when a fetch fails. Right after a switch that list belongs to the project the reader left.
- `loadWsNav`, in Overview mode, draws the left pane through the new `loadOverviewScopePane` when it skips the landing for a link (ISS-0296).
- `openWorkspace` clears `designRegister` with the other per-project caches (ISS-0297).
- A parked link is now dropped when the reader goes to a project the link did not name, and the status bar says so ([[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]]). Before, whichever project reported ready next opened the link's page — the wrong project's note before this feature, and the wrong project's bench after it. Found by the independent review.
- `loadOverviewScopePane` and `fetchDesignRegister` each check that the sidecar they asked is still the sidecar on screen **after** reading the reply, not before. A switch during the read otherwise drew the project the reader had left, which is the symptom ISS-0296 and ISS-0297 exist to remove. Also from the review.
- `docs/reference/cockpit-capability-register.md`: the `shell.windows` and `shell.reader.render` rows say that a link naming a design opens the bench. No sidecar endpoint changed, so no API row changed, and Deck sees the same sidecar it did.

## Not changed

- An in-repo `[[DES-####]]` wikilink still opens the note. Whether it should open the bench is an open question for Edwin, recorded in [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]. The sidecar writes such a link as a path, so the renderer never sees the ID.
- The browser front door (`python -m project_os_cockpit`) has no cross-repo links and no bench, so it does not change.
- A link sent while the cockpit is not running still starts it and is dropped, as [[CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names]] records.
- `cockpit focus <ID>` still opens the note, including for a design. It is not a link: the sidecar has already resolved it to a path by the time the window sees it. Agents drive the window this way more often than with a `cockpit://` link, so if designs should follow the same rule there, that is a separate change.

## Verification

- Desktop node suite: `deep-link.test.mjs` runs 20 cases, 9 of them new. Four broken versions of the rule were each caught. The four sent every design to the bench, matched on the prefix, compared case-sensitively, or read `has_asset`.
- `tests/test_design_links.py`, 7 tests, pins where the rule is asked: in `locateAndOpen`, before the locate fetch, nowhere else, and with a fresh register. Deleting the call, moving it into `navigateTo`, and using the cached register were each caught. It also pins that all three routes still reach `locateAndOpen` with the link's ID, after the independent review found four one-line breaks to those routes passing every test. `tests/test_cross_repo_links.py` gains the ISS-0296 guard. 13 broken versions were tried in all and 13 caught; [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]] lists them.
- Full suite, in the foreground: 2246 passed, 6 skipped, 1 failed. The failure is `tests/test_release_evidence.py::test_both_corrupt_store_artifacts_are_reported_and_the_others_are_not`, known and unrelated. Its docstring says it fails once your-trainer's broken store file is repaired, which it now is.
- [[TST-0085-A-Link-To-A-Design-Shows-The-Design]], walked 2026-09-11. Steps 1, 2, 3, 4 and 6 were walked in the running window, restarted by its pid with this build. Edwin was using the window during the walk, so steps 7 and 8, and step 5's banner, were walked only in the renderer harness. All eight passed there on the final build. The note says which step was walked where.
- **The running window has not loaded the ISS-0296 and ISS-0297 fixes.** It was restarted before they were written. It picks them up the next time the cockpit restarts.

## Independent review (2026-09-11, model:claude-opus-5): changes requested

**Verdict: changes requested.** "What changed" matches the diff: `designBenchTarget`, the call at the top of `locateAndOpen`, `designsForLink`, the Overview branch of `loadWsNav` with `loadOverviewScopePane`, the `designRegister` reset in `openWorkspace`, and the two capability register rows. No sidecar file changed. The counts I could rerun are right: 20 node cases, 9 of them new, and 4 tests in `tests/test_design_links.py`. The full suite's 2243 was not rerun, because the full suite was outside the commands this review was allowed to run. The full findings are in [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] under "Independent review". This was a fresh session with no access to the authoring session, run by the same model that walked TST-0085 (`model:claude-opus-5`). Two findings concern this note:

- **"Back returns to the page you were on" is claimed for both kinds of link (not reproduced).** TST-0085 walks it only for a link within one project (step 2). The history is one list of page paths shared by every workspace. After a link that switches project, Back asks the new project's sidecar for the old project's page.
- **The Verification section says every broken version of the routing was caught (reproduced).** That is true of the ones listed. Four others pass every automated test: deleting the parked jump's call (`renderer.ts:1059`), deleting the same-project cross-repo call (`:868`), rerouting the same-project `cockpit://` note branch (`:3792`), and passing `project` instead of `noteId` to the rule (`:889`).
