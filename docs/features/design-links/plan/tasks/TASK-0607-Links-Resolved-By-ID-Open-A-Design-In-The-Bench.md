---
type: "[[task]]"
id: TASK-0607
aliases: ["TASK-0607"]
title: "A cockpit:// link or a cross-repo link that names a design opens the bench, because the one place that resolves a link by ID asks that function first"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
source: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
parent: "FEAT-0146"
effort: "S"
due: ""
depends: ["[[TASK-0606-The-Design-Register-Decides-Where-An-ID-Opens]]"]
blocks: []
related: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]", "[[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]", "[[ISS-0041-Artifactless-Design-Is-Unreadable]]"]
tests: ["[[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]", "[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"]
---

# Links resolved by ID open a design in the bench

After this task, `cockpit://your-health/DES-0002` shows DES-0002 on the design bench instead of its note. So does a cross-repo link such as `[[project-os-deck#DES-0001]]`. The change is in one function, `locateAndOpen` in `desktop/src/renderer/renderer.ts`, because every link resolved by ID passes through it.

## Definition of Done

- [x] `locateAndOpen` fetches `/api/cockpit/designs` from `sidecarBaseUrl` in the same call, and treats any failure as an empty list. It does not call `fetchDesignRegister()` and does not read `designRegister`, the cached list (see Notes).
- [x] When `designBenchTarget(noteId, designs)` returns a page, `locateAndOpen` opens it with `navigateTo` and stops. Otherwise it runs the existing `/api/cockpit/locate` lookup, unchanged.
- [x] Nothing else calls `designBenchTarget`. `navigateTo` does not change, and neither do the bench's ID chip (`buildDesignHeader`), its `Read <ID> as a note` button (`buildDesignFrame`), the note's banner (`buildDesignNoteBanner`) or the Intent landing's rows (`buildDesignRegisterList`).
- [x] The comments above `openCockpitLink` and `locateAndOpen` say that an ID naming a design with something to show opens the bench, and point at [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]].
- [x] `tests/test_design_links.py`, a source guard over `renderer.ts`, asserts three things:
  - [x] `locateAndOpen`'s body calls `designBenchTarget` before it fetches `/api/cockpit/locate`.
  - [x] `designBenchTarget` is called nowhere else in `renderer.ts`, and in particular not inside `navigateTo`.
  - [x] `locateAndOpen` neither calls `fetchDesignRegister(` nor reads `designRegister`.
- [x] The guard's docstring states its limit: it pins where the call is, not what the window shows, and [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] is the check of the window. Three edits each turn a test red, recorded in [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]'s `adequacy:`: deleting the call, moving it into `navigateTo`, and swapping the fresh fetch for `fetchDesignRegister()`.
- [x] `docs/reference/cockpit-capability-register.md` says, in the same commit as the code: on the `shell.windows` row, that a `cockpit://` link naming a design's ID opens the design bench; on the `shell.reader.render` row, that a cross-repo link to a design does the same. No API row changes, because no endpoint changes.
- [x] `npm run build` in `desktop/`. Then the full suite, run in the FOREGROUND with its output visible: `.venv/bin/python -m pytest -q -p no:cacheprovider`. The only failure allowed is the known unrelated one, `tests/test_release_evidence.py::test_both_corrupt_store_artifacts_are_reported_and_the_others_are_not`. Run twice in the foreground: 2241 passed, 6 skipped, 1 failed after this task; 2246 passed, 6 skipped, 1 failed after ISS-0296 and ISS-0297. The one failure both times was that known test.
- [x] [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] walked, every step. Its `last_verified:` and evidence are filled in. **Where each step was walked differs, and TST-0085 says which.** Steps 1, 2, 3, 4 and 6 were walked in the running window. Step 5 routed correctly there, but its banner was only checked in the renderer harness. Steps 7 and 8 were walked only in the harness, because Edwin was using the window at the time.
- [x] `cockpit://your-health/~design/DES-0002`, the bench address written as a path, still opens the bench.

## Steps

- [x] Write a small helper that fetches the register from the current sidecar and returns `[]` on any failure. Call it at the top of `locateAndOpen`.
- [x] Put the `designBenchTarget` check before the locate fetch.
- [x] Update the two comments.
- [x] Write `tests/test_design_links.py`, run it, break the code three ways, and put it back.
- [x] Update the two capability register rows.
- [x] Build, run the full suite in the foreground, restart the cockpit, and walk TST-0085.

## Notes

- **The three routes into `locateAndOpen`.** A `cockpit://` link to the project on screen (`openCockpitLink`). A cross-repo link to the project on screen (`jumpToCrossRepoNote`). A link of either kind that switched project: it is parked in `pendingCrossRepoJump` and consumed in the sidecar-ready handler, where `sidecarBaseUrl` already points at the arriving project. One change covers all three.
- **Why not the cached register.** `fetchDesignRegister()` keeps the last good list when a fetch fails. Right after a project switch, that list belongs to the project the reader left. A failed fetch would then send `DES-0002` to the wrong project's bench, which says "No design DES-0002". Opening the note, as today, is the right fallback.
- **Why not `navigateTo`.** Three controls open a design note by its path on purpose: the bench header's ID chip, the `Read <ID> as a note` button, and an owed design's landing row ([[ISS-0041-Artifactless-Design-Is-Unreadable]], [[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]). A rule in `navigateTo` would send each straight back to the bench, and the note would become unreachable.
- **If Edwin wants `cockpit://` links only.** The cross-repo route would carry a flag through `pendingCrossRepoJump` and into `locateAndOpen` that skips the rule. The plan includes cross-repo links because his sentence covers them.
- **Restarting the cockpit to test.** Stop it by its pid only, after `ps -p <pid>` shows the command you expect. Deck also runs as `Electron .`, and a pattern kill has taken down the wrong app before. To inspect the window, the 2026-09-10 session opened a debugging port; that is how the 19 images in DES-0002's page were counted.

## Outcome (2026-09-11)

`locateAndOpen` now starts with `designBenchTarget(noteId, await designsForLink())`. `designsForLink` fetches `/api/cockpit/designs` from the sidecar on screen and returns an empty list on any failure. Seen in the harness with the endpoint made to fail twice, once by a network error and once by HTTP 500: `DES-0002` opened its note both times.

The shared type the rule reads is named `LinkDesign` in `renderer.ts`. It has a name, rather than an inline object type, so that `tests/conftest.py`'s `js_function_body` can find where `designsForLink`'s body starts. An inline `{ … }` in a return type is read as the body.

**Two defects found by the walk, fixed in the same change.** Both were already in the tree before this task:

- [[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]: a link that switches project while the reader is in Overview left the left pane unloaded. A your-health session reported it in the cockpit's console, and the harness reproduced it.
- [[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]]: after a project switch, a design note was drawn without its banner. TST-0085 step 5 expects that banner.

## Handoff (2026-09-11)

**Both tasks of [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] are done and nothing is in flight.** `focus.task` is cleared for that reason; `focus.feature` still names FEAT-0146, because the feature is not closed.

**What is next, and it is Edwin's to decide, not a successor's to do:**

1. **Approve or amend [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]**, which is `draft` with all six criteria ticked and evidenced. On approval: REQ-0062 `implemented`, FEAT-0146 `done`, tick PHASE-005's reopened exit criterion and close the phase, then `bash tools/scripts/close-out-commit.sh` over the paths. **Nothing is committed yet**, and the commit must include the uncommitted 2026-09-10 work ([[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]], ISS-0293/0294/0295, [[CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names]]) because `renderer.ts` carries both changes.
2. **Answer the open question** in FEAT-0146: should an in-repo `[[DES-####]]` wikilink open the bench too? A yes is a third task, and a seventh criterion on REQ-0062.

**Asked and not answered.** Both questions were put to Edwin on 2026-09-11 and no answer had arrived when this was written. Nothing here assumes one.

**State of the tree:** full suite 2246 passed, 6 skipped, 1 failed — `tests/test_release_evidence.py::test_both_corrupt_store_artifacts_are_reported_and_the_others_are_not`, known, unrelated, and its own docstring says to delete that assertion now that your-trainer's REL-0007 file is repaired. Validator: 0 errors. Independent review: `changes-requested`, all eleven findings acted on, verdict left standing ([[project-os-dev#ADR-0011]]).

**The running cockpit window carries none of the three fixes** (ISS-0296, ISS-0297, ISS-0298). It was restarted by pid at 12:07 with the FEAT-0146 build, before they were written, and picks them up on the next restart.

## Notes — approaches tried and set aside

- **Walking every step in the running window: abandoned mid-walk.** Edwin was using it. A click on the workspace rail moved the window back to your-health 7 seconds after a link had moved it away, and a click on a design note's banner sent it to the bench — both read as renderer defects until `openWorkspace` and `navigateTo` were wrapped to record `new Error().stack`. Steps 7, 8 and step 5's banner were walked in a copy of `desktop/harness/live-harness.html` instead, given three workspaces and three sidecars, loaded in a separate hidden Electron instance on its own debugging port. That harness copy lived in a scratch directory and is not in the repo; making it a second harness file is a follow-up nobody has asked for.
- **Recording a `pass` in `docs/releases/ledgers/WORKING-macos.json`: not done, deliberately.** Three of TST-0085's steps were walked outside the running window, so this is not a person's pass in the window. The check stays owed on macos until someone records one.
- **Moving TST-0084 to `passing`** (independent review, finding 6): declined. [[ADR-0038-The-Suite-Is-The-Verdict]] says a note declaring a `command:` never holds `passing` and the gate is discharged by the command resolving; setting it would be a validator error.

> [!quote] Edwin, 2026-09-11 (the request this feature answers)
> Create the feature/requirement/tasks etc ... in the cockpit project to open the design bench whenever a link names a design's ID. So the cockpit LLM can take over.
