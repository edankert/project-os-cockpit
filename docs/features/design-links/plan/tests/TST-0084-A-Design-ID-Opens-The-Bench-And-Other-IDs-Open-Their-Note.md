---
type: "[[test]]"
id: TST-0084
aliases: ["TST-0084"]
title: "A design's ID opens the bench and every other ID opens its note: the rule runs in node, and a source guard pins where the renderer asks it"
status: retired
owner: user:edwin
created: 2026-09-11
updated: 2026-09-12
phase: "[[PHASE-005-Desktop-Shell]]"
source: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
scope: feature
level: unit
entrypoint: ""
command: ".venv/bin/python -m pytest tests/test_desktop_node_suite.py tests/test_cross_repo_links.py -q -p no:cacheprovider"
last_verified: ""
covers: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
issues: ["[[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]", "[[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]", "[[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]]"]
tasks: ["[[TASK-0606-The-Design-Register-Decides-Where-An-ID-Opens]]", "[[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]]"]
artifacts: []
last_run: ""
adequacy: "13 broken versions tried, 13 caught. Rule: sends every design to the bench (1 case red), matches on the DES- prefix (5 red), compares IDs case-sensitively (1 red), reads has_asset instead of asset (1 red). Call site: call deleted (3 red), call moved into navigateTo (3 red), cached register used in locateAndOpen or in designsForLink (1 red each). Six more after the independent review, which had found the first four of them surviving: the parked jump's call deleted (2 red), the same-project cross-repo call deleted (1), the same-project cockpit:// branch opening target.id as a path (1), the rule asked about project instead of noteId (1), the dropped-link check bypassed with if (false) (1), loadOverviewScopePane checking for a switch before reading the body (1)."
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"]
---


<!-- The command lost the rule's own source-guard file, deleted with the rule
     (TASK-0614). The four guards in it that did not belong to the rule
     moved into `tests/test_cross_repo_links.py` and are named here instead, so
     this retired check still says truthfully what runs.
     Retired 2026-09-12 with the rule it checked (TASK-0614): the design bench
     is gone, so a design ID opens its note like every other ID. Kept, not
     deleted — it records what was checked, and passed, on 2026-09-11. -->

# A design's ID opens the bench, and every other ID opens its note

## Purpose

Two automated halves check [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] without a window.

**The rule, in node.** `desktop/tests/deep-link.test.mjs` runs the built `deep-link.js` with an empty global scope and calls `designBenchTarget` with a hand-written register. It checks that the register decides, not the `DES-` prefix, and that a design with nothing to show gets `null`. The nine cases are listed in TASK-0606. `tests/test_desktop_node_suite.py` runs this file with the rest of the desktop's node suite.

**The call site, as source text.** A source-guard file (deleted 2026-09-12 with the rule) read `desktop/src/renderer/renderer.ts`. It checks that `locateAndOpen` asks `designBenchTarget` before it asks `/api/cockpit/locate`, that nothing else calls the function, and that `locateAndOpen` does not use the cached register. It also checks **the other half of the chain**, added after the independent review found it unpinned: that all three routes still reach `locateAndOpen` and that the rule is asked about the note's ID. Three more tests pin the fixes for [[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]], [[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]] and [[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]], which is why this note's `command:` now runs `tests/test_cross_repo_links.py` too: ISS-0296's guard lives there, beside the landing-suppression tests it belongs with.

**This note holds no verdict, and that is the rule rather than an omission.** It declares a `command:`, so by [[ADR-0038-The-Suite-Is-The-Verdict]] it never reaches `passing` and carries no `last_run:`. The suite is the verdict. It stays `active` when the feature closes. **Its limit:** it pins where the call is written, not what the window shows. A correct refactor that renames `locateAndOpen` will turn it red, and a bug in `navigateTo` will not. [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] is the check of the window.

## Procedure

- Build the desktop: `npm run build` in `desktop/`.
- Run the command above in the foreground and read the output.

## Expected results

- Every case in `deep-link.test.mjs` passes, the nine new ones included.
- The seven source guards pass, and so does `tests/test_cross_repo_links.py`.

## Adequacy (who verifies this test?)

Each broken version was built, the tests were run against it, and the real code was put back. The rule's mutants were applied to the built `deep-link.js`; the call site's to `renderer.ts`.

| Broken version | What turned red |
| --- | --- |
| The rule sends every design to the bench | `a design with no asset and no variants opens its note` |
| The rule matches on the `DES-` prefix, not the register | 5 cases, among them `a DES- ID the register does not list opens its note` and `a design whose ID has no DES- prefix opens the bench` |
| The rule compares IDs case-sensitively | `the ID matches whatever its case` |
| The rule reads `has_asset` instead of `asset` | `a declared asset whose file is missing opens the bench` |
| The call is deleted from `locateAndOpen` | all 3 call-site tests |
| The call is moved into `navigateTo` | all 3 call-site tests |
| `fetchDesignRegister()` replaces the fresh fetch, in `locateAndOpen` or inside the link's own helper | the fresh-register guard, each time |
| The parked jump's call to `locateAndOpen` is deleted | 2 tests, among them `test_every_route_that_resolves_a_link_by_id_goes_through_locate_and_open` |
| The same-project cross-repo call is deleted | the same test |
| The same-project `cockpit://` branch opens `target.id` as a path | the same test |
| The rule is asked about `project` instead of `noteId` (tsc accepts it: both are strings) | the same test |
| The dropped-link check is bypassed with `if (false)` | `test_a_parked_link_is_consumed_only_by_the_project_it_names` |
| `loadOverviewScopePane` checks for a switch before reading the reply's body | `test_a_reply_from_the_project_the_reader_left_never_lands` |

The first four of those six were found by the independent review, which built them against the code as it then stood and recorded that every one of them **survived**. They are caught now.

The source-guard file also carried the guard for [[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]] — deleting the reset from `openWorkspace` turned it red. That guard, and three others that did not belong to the design rule, moved into `tests/test_cross_repo_links.py` on 2026-09-12; the file that held them was deleted with the rule.
