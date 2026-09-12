---
type: "[[requirement]]"
id: REQ-0062
aliases: ["REQ-0062"]
title: "A link that names a design's ID opens that design in the design bench, and opens the design's note only when the design has nothing to show"
status: superseded
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: "2026-09-12"
source: ["Edwin, 2026-09-11, in a your-health session: 'Create the feature/requirement/tasks etc ... in the cockpit project to open the design bench whenever a link names a design's ID. So the cockpit LLM can take over.'"]
priority: medium
scope: "links the desktop shell resolves by note ID"
acceptance:
  - "[x] A `cockpit://<project>/<ID>` link whose ID is a design with an artifact or variants opens `~design/<ID>` in that project, both when the link switches project and when that project is already on screen. — evidence: TST-0085 steps 1 and 2 in the running window (a switch from project-os-cockpit, and from FEAT-0107 within your-health), 2026-09-11. `tests/test_design_links.py` pins that `locateAndOpen` asks `designBenchTarget` first AND that all three routes still reach `locateAndOpen` with the link's ID — the second half added after the independent review found four one-line breaks to those routes passing every test"
  - "[x] A cross-repo `[[project#ID]]` link to such a design opens the design bench in that project too. — evidence: TST-0085 step 7 in the renderer harness — clicking `project-os-deck#DES-0001` in PHASE-028's frontmatter opened ~design/DES-0001 in project-os-deck, 2026-09-11"
  - "[x] A design that declares no artifact and no variants opens its note, as a link does today. A design that declares an artifact whose file is missing opens the bench, which reports the missing file. — evidence: TST-0085 step 5 (DES-0003 opened its note, in the window, with its banner in the harness); deep-link.test.mjs cases `a design with no asset and no variants opens its note` and `a declared asset whose file is missing opens the bench`"
  - "[x] Whether an ID is a design is decided by the project's design register, which the sidecar builds from `type: \"[[design]]\"`. The `DES-` prefix plays no part. — evidence: deep-link.test.mjs cases `a DES- ID the register does not list opens its note` and `a design whose ID has no DES- prefix opens the bench`; a prefix-matching mutant turned 5 cases red (TST-0084 adequacy)"
  - "[x] Everything that opens a design note by its path still opens the note: the ID chip in the bench header, the bench's `Read <ID> as a note` button, an owed design's row on the Intent landing, and a `cockpit://` link that names the note's file. — evidence: TST-0085 steps 3 and 4 in the running window, step 8 in the harness; tests/test_design_links.py pins that `navigateTo` never asks the rule; `cockpit://your-health/~design/DES-0002` still opens the bench"
  - "[x] A link that names any other ID opens its note exactly as before. So does a design's ID when the design register cannot be read. — evidence: TST-0085 step 6 in the running window (FEAT-0107 opened its note); in the harness, with /api/cockpit/designs made to fail by a network error and by HTTP 500, DES-0002 opened its note both times"
implements: "[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"
verifies: []
superseded_by: "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"
related: ["[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]", "[[FEAT-0042-Design-Bench]]", "[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[ISS-0041-Artifactless-Design-Is-Unreadable]]", "[[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]"]
tests: ["[[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]", "[[TST-0085-A-Link-To-A-Design-Shows-The-Design]]"]
tags: [requirement, desktop-shell, design, links]
reviewed_by: model:claude-opus-5
review_date: 2026-09-11
review_verdict: changes-requested
review_response: "All eleven findings acted on; the verdict stands as the reviewer recorded it. Findings 1, 7, 8 and 9 changed code: three guards now pin that every route still reaches locateAndOpen with the link's ID (the four one-line breaks the review found surviving are caught), both async reads check for a project switch after reading the reply rather than before, and a parked link is dropped — with a message — when the reader goes to a project the link never named (filed as ISS-0298 and added to TST-0085 as step 10). Findings 2, 3, 5 and 10 were wrong statements in notes and are corrected: REQ-0062's approval paragraph, FEAT-0093's narrowed criterion, TST-0084's case count (nine, not eight), and the CHG's Back claim, which now says Back is unchanged across a project switch. Finding 4: TST-0085 gains step 9 for Overview, and TST-0084's command runs test_cross_repo_links.py. Finding 11 is recorded in the CHG's 'Not changed': cockpit focus still opens the note. Finding 6 is the one not applied, and deliberately: ADR-0038 says a test note declaring a command: never reaches passing and the gate is discharged by the command resolving, so TST-0084 stays active — moving it to passing would be a validator error. TST-0084 now says so. Suite after the changes: 2246 passed, 6 skipped, 1 failed (the known unrelated test_release_evidence case)."
review_response_date: 2026-09-11
---

# A link that names a design's ID opens the design bench

## Superseded 2026-09-12

By [[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]. The design bench is removed, so the rule this requirement states has nothing to open; a design's ID opens its note.

**The six criteria below stay ticked as written.** They were true, and verified, on the day they were ticked. A superseded requirement records what was required then — not what is required now.

## Approval

**Approved by Edwin on 2026-09-12** — *"approve REQ-0062 and close it out"* — and set to `implemented` in the same close-out, with all six criteria below ticked against evidence.

**The work was built before the approval, which is not the order this section used to ask for.** It said to approve before [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] moved to `doing`, and the validator said the same thing as a `REQ-PREMATURE` warning while the feature was built. Edwin asked on 2026-09-11 for the feature to be implemented and tested, and it was; approval then decided whether it closed, not whether it was written. Recorded here rather than tidied away, because the gate is only worth something if the times it was crossed are legible.

The six criteria restate Edwin's sentence as things a person can check. Criteria 2 and 3 are calls the plan made on his behalf, with the reasons under "Decisions this requirement records". One question is still open and is **not** covered here: whether an in-repo `[[DES-####]]` wikilink should open the bench too (see "Not covered"). It was put to Edwin on 2026-09-11, is unanswered, and would be a seventh criterion.

## Statement

When a link names a design by its ID, the desktop shell **shall** open that design in the design bench. The bench is the page `~design/<ID>`, which frames the design's artifact (its HTML page of mockups). The shell **shall** open the design's note instead only when the design declares nothing the bench can show.

"A link that names an ID" means a link the renderer resolves by ID. There are two kinds today: a `cockpit://<project>/<ID>` link, and a cross-repo `[[project#ID]]` link. Both reach the same function, `locateAndOpen` in `desktop/src/renderer/renderer.ts`.

## Why

Today `cockpit://your-health/DES-0002` opens `docs/designs/DES-0002-Recovery-And-Food.md`. For a design, that page shows the note's text and one button, "Open DES-0002 in the design bench". The mockups are only on the bench. An agent that sends a reader a link to a design means "look at this design", and the reader should not need a second click to see it.

## Acceptance Criteria

- [x] A `cockpit://<project>/<ID>` link whose ID is a design with an artifact or variants opens `~design/<ID>` in that project, both when the link switches project and when that project is already on screen. — evidence: TST-0085 steps 1 and 2 in the running window (a switch from project-os-cockpit, and from FEAT-0107 within your-health), 2026-09-11. `tests/test_design_links.py` pins that `locateAndOpen` asks `designBenchTarget` first AND that all three routes still reach `locateAndOpen` with the link's ID — the second half added after the independent review found four one-line breaks to those routes passing every test
- [x] A cross-repo `[[project#ID]]` link to such a design opens the design bench in that project too. — evidence: TST-0085 step 7 in the renderer harness — clicking `project-os-deck#DES-0001` in PHASE-028's frontmatter opened ~design/DES-0001 in project-os-deck, 2026-09-11
- [x] A design that declares no artifact and no variants opens its note, as a link does today. A design that declares an artifact whose file is missing opens the bench, which reports the missing file. — evidence: TST-0085 step 5 (DES-0003 opened its note, in the window, with its banner in the harness); deep-link.test.mjs cases `a design with no asset and no variants opens its note` and `a declared asset whose file is missing opens the bench`
- [x] Whether an ID is a design is decided by the project's design register, which the sidecar builds from `type: "[[design]]"`. The `DES-` prefix plays no part. — evidence: deep-link.test.mjs cases `a DES- ID the register does not list opens its note` and `a design whose ID has no DES- prefix opens the bench`; a prefix-matching mutant turned 5 cases red (TST-0084 adequacy)
- [x] Everything that opens a design note by its path still opens the note: the ID chip in the bench header, the bench's `Read <ID> as a note` button, an owed design's row on the Intent landing, and a `cockpit://` link that names the note's file. — evidence: TST-0085 steps 3 and 4 in the running window, step 8 in the harness; tests/test_design_links.py pins that `navigateTo` never asks the rule; `cockpit://your-health/~design/DES-0002` still opens the bench
- [x] A link that names any other ID opens its note exactly as before. So does a design's ID when the design register cannot be read. — evidence: TST-0085 step 6 in the running window (FEAT-0107 opened its note); in the harness, with /api/cockpit/designs made to fail by a network error and by HTTP 500, DES-0002 opened its note both times

## What a design "has to show"

The bench has something to show when the design note declares an `asset:` (an HTML page), or `## Variant <name>` sections that each carry an html block, or both. The design register reports these as `asset` and `variants` (`designs_payload` in `src/project_os_cockpit/cockpit.py`).

A design that declares neither is sent to its note. On the bench it would show only "declares no artifact yet — nothing to render" and a button back to the note. The cockpit's own DES-0003 is such a design today.

A design that declares an `asset:` whose file does not exist is sent to the bench. The bench says "Artifact not found: <path>", and that message is how the tool reports a broken path today. The note would hide the mistake, because its banner says only "This design has no artifact yet."

## Decisions this requirement records

**The design register decides whether an ID is a design, not the ID's prefix.** The register (`GET /api/cockpit/designs`) lists the notes whose frontmatter says `type: "[[design]]"`, so it reads the note's type, as Edwin preferred. It also answers the second question this rule needs, whether the design has anything to show, which neither the prefix nor a type alone can answer. The renderer already calls this endpoint for the Intent landing and the bench, so nothing changes in the sidecar. Two alternatives were weighed and rejected. The `DES-` prefix is a naming convention: a note of another type with a `DES-` ID would be sent to the bench, and it still cannot say whether there is an artifact. Adding `type` to `/api/cockpit/locate` is a one-line sidecar change, but the renderer would still need the register for the artifact question, so it costs a second request and changes an API that Deck shares.

**An owed design still opens in the bench.** your-health's DES-0002 is `proposed`, so the Intent landing counts it as owed, and its row there opens the note, where the Accept button is. That rule belongs to [[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]] and is about a row that names a verb: the landing says "Accept", so arriving at Accept keeps its promise. A link names no verb. It says "look at this design". The landing row keeps its rule, and the note is one click away from the bench.

**The note stays one click away, through a control that already exists.** The first chip in the bench header is the design's ID, and clicking it opens the note ([[ISS-0041-Artifactless-Design-Is-Unreadable]]). No new control is added. "Show details" is not the way back: it opens a sidebar with the design's revisions and the decisions behind it, not the note's text.

**Cross-repo links are included.** Edwin's words were "whenever a link names a design's ID", and a `[[project#DES-0002]]` link names one. It also runs through the same function as a `cockpit://` link, so leaving it out would take extra code. This narrows one criterion of [[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]], whose link "switches workspace and opens the note". For a design with something to show, the link now opens the bench. Every other ID keeps FEAT-0093's behaviour.

## Not covered

- **In-repo `[[DES-####]]` wikilinks. This is an open question for Edwin.** His sentence can be read to include them. They are left out for now because they are a different piece of work. The sidecar turns an in-repo wikilink into a plain link to the note's file, so the renderer receives a path, not an ID. The bench's ID chip, its `Read <ID> as a note` button and an owed design's landing row also open the note by its path, on purpose. A rule that sent every path belonging to a design to the bench would send those back to the bench too. Building it would mean the sidecar marks each wikilink with the ID it was written with, and the renderer sends only marked links through this rule. It would change what happens when a reader clicks a design link anywhere a note is shown: the body, the frontmatter strip, the context pane and the backlinks.
- **The search box and `cockpit focus`.** Neither is a link. `cockpit focus` arrives as a path the sidecar has already resolved.
- **The browser front door** (`python -m project_os_cockpit`, mode 1). It has no cross-repo link handling and no design bench, so there is nothing there to change.
- **A cold start.** If the cockpit is not running, `desktop/scripts/open-link.sh` starts it and the link is dropped. That is unchanged from [[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]].

## Traceability

- Implements: [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]
- Verified by: [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]] (the rule and its call site, automated) and [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] (the walk in the running window)

## Independent review (2026-09-11, model:claude-opus-5): changes requested

**Verdict: changes requested.** The six criteria describe what the code does. I found no input where a link opens the wrong page, and nothing that opens a design note by its path can reach the bench. Two things in this note need changing. The full findings, and what the review could and could not check, are in [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] under "Independent review". This was a fresh session with no access to the authoring session, run by the same model that walked TST-0085 (`model:claude-opus-5`).

- **The approval sentence contradicts the state (reproduced).** Line 32 says to approve this note "before FEAT-0146 moves to `doing`". FEAT-0146 is already `doing` and its tasks are `done`. The validator prints `WARN [REQ-PREMATURE]` for this note.
- **Criterion 1's evidence overstates the guard (reproduced).** It says the rule is "pinned by tests/test_design_links.py". Those tests pin that `locateAndOpen` asks the rule, not that links reach `locateAndOpen`. Four edits pass every automated test: deleting the parked jump's call (`renderer.ts:1059`), deleting the same-project cross-repo call (`:868`), rerouting the same-project `cockpit://` note branch (`:3792`), and passing `project` instead of `noteId` to the rule (`:889`). For criteria 1 and 2, only the TST-0085 walk shows that the links still reach the rule.
