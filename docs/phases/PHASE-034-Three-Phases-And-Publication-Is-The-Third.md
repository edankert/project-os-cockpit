---
type: "[[phase]]"
id: PHASE-034
aliases: ["PHASE-034"]
title: "Three phases, and publication is the third — what needs a person is routed to the phase that owns it, and asks only while that subject is in flight"
status: done
order: 34
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: changes-requested
goal: "Give the tool the phase it is missing. Publication becomes a first-class view over the whole ladder — commit, push, deploy, versioned release — and every obligation is routed to the phase that owns its subject and asks only while that subject is in flight, so what needs a person is smaller, sorted, and inspectable rather than one undifferentiated number."
features:
  - "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"
  - "[[FEAT-0102-Publication-Becomes-A-View]]"
  - "[[FEAT-0103-The-Gate-Is-Walkable]]"
  - "[[FEAT-0105-There-Is-Always-A-Release]]"
  - "[[FEAT-0106-The-Release-Page]]"
  - "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"
  - "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"
  - "[[FEAT-0109-A-Shipped-Release-Reports-What-It-Kept]]"
  - "[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]"
  - "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]"
  - "[[FEAT-0104-The-Suite-Is-The-Surface]]"
issues:
  - "[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]"
  - "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]"
  - "[[ISS-0179-Six-From-Reading-The-Release-View]]"
  - "[[ISS-0180-The-Release-Page-Printed-What-It-Should-Have-Rendered]]"
  - "[[ISS-0174-Publication-Showed-One-Item-Twice-And-A-Row-Nobody-Could-Click]]"
  - "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]"
  - "[[ISS-0176-Every-Prompt-In-The-Desktop-Shell-Is-Dead]]"
  - "[[ISS-0183-The-Canonical-Machine-Readable-File-Did-Not-Parse]]"
  - "[[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row]]"
  - "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]"
  - "[[ISS-0185-The-Mark-Control-Sits-Inside-Tasklists-Leftover-Box-And-The-Cycle-Makes-You-Walk-Past-States]]"
  - "[[ISS-0186-The-Mark-Glyphs-Are-Decorative-And-The-Dialog-Is-Too-Narrow-For-Six-Options]]"
  - "[[ISS-0187-The-Repaint-Loses-Your-Place-A-Refusal-Is-Silent-And-The-Dialog-Has-No-Save]]"
  - "[[ISS-0188-The-Scroll-Fix-Looked-Right-Passed-A-Guard-And-Did-Nothing]]"
requirements: []
tasks: []
depends: []
related: ["[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0022]]", "[[PHASE-030-Obligations-Go-Home]]", "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"]
tags: [surfaces, obligations, publication]
---

# Three phases, and publication is the third

## Where this came from

Edwin, using `../your-trainer` on 2026-08-16: *"The your-trainer application has created some acceptance-tests I need to execute but these are currently not very clearly visible … it seems like the items which need my attention are still a little bit invisible in the tool, hidden by all the other stuff which is mainly handled by the LLM."*

The review that followed measured the repo rather than reading its notes. What it found:

- **64** items on the badges — 26 requirements to approve, 22 issues to triage, 15 manual tests to run, 1 commit to push.
- **60** unchecked Tier 1/2 acceptance rows, which are the release gate, appearing in **no count, on no badge, in no digest, on no fleet card**. `obligations.py:139` says they surface in Tests. They do not.
- **8 of the 15** owed manual tests have no Run button and no explanation, because `manual_test_steps` stops at the first heading after the procedure heading — including a *sub*heading of the section it is reading ([[ISS-0172]]).
- **72 of 82** suite section headings name their features or issues in bare form; the parser reads only `[[wikilink]]` form and therefore reads none ([[ISS-0173]]).

**The first proposal was to admit the 60 to the obligation registry, and Edwin refused it**: *"I am not sure that if we implement that that acceptance tests and releases are then very much first class citicens of the tool yet. And I am also afraid that this could overwhelm my attention."*

He was right twice. The registry's own charter forbids it — [[ADR-0027]] excludes staleness because *"counting it is a badge that re-arms itself forever"*, and acceptance rows re-arm **in bulk, by the suite's own rule 3**. And the proposal answered a complaint about noise by taking the card from 64 to 124.

Then he named the structure: *"3 clear phases, the design phase (intent), the actual implementation phase (features, issues, TSTs?) and the publication phase."* Mapping the registry's five views onto those three leaves exactly two things unplaced — publication's obligations, homeless on `overview`, and `tests`, which straddles. Both were the defects already found. That is what [[ADR-0028]] records.

## Scope

- **[[ADR-0028]]** — the decision. Three phases; per-item obligation routing; the in-flight rule; `deferred` as the override; the discriminator is feature status, not phase.
- **[[FEAT-0101]]** — obligations route by the state of their subject. The structural change to the registry, the in-flight predicate for requirements and tests, and the collapsed line that makes the resulting quiet inspectable.
- **[[FEAT-0102]]** — publication becomes a view. The ladder as data, the nav mode, the release rung with `REL-*` notes and tags, and the acceptance gate attached where it belongs.
- **[[ISS-0172]]** — the step parser. Independent of everything above and landable first.
- **[[ISS-0173]]** — bare ids in the suite. Prerequisite for scoping the gate to what is in flight.

## Out of scope

- **Any change to the existing view set.** The eight nav modes stay exactly as they are and `publication` is added — **unchanged plus one**. Nothing is renamed, merged or removed, and no note changes address; what routes between phases is the obligation *row*, never the note ([[ADR-0028]] decision 2). Recorded because the first draft of the analysis proposed folding `features`/`issues`/`tests` into a single "Work" mode to make the nav read as three phases: that is a regression on surfaces [[PHASE-030]] has just finished building, and `MODE_ALIASES` records what a mode-id change costs — a stale client asked for `tests`, silently got the features tree, and the view looked broken for 33 hours. The phases live in the routing, not in the button count.
- **Any widening of write paths.** `REQ-0026`/`REQ-0027` gate every mutating route and this phase adds none. Pushing stays a person's click; deploying stays named and refused.
- **Fixing your-trainer's record.** `PHASE-017`/`PHASE-018` read `planned` while their only features are `done`, and eight `REQ-*` notes there fail frontmatter parse. Both were found while measuring and both belong to that repo, not this one.
- **A `Releases` view.** Considered and rejected on the evidence — empty in 9 of 12 repos.

## What this phase must not do

**It must not make the number bigger.** The complaint is that what needs a person is buried. Every change here is measured against `your-trainer`'s badge total, and a change that raises it has failed regardless of what else it achieves.

**It must not make things vanish instead.** Derived silence that cannot be opened is the same invisibility problem wearing the opposite sign. Whatever the rule quiets stays on screen as a collapsed line carrying its reason.

## Exit criteria

- [x] `your-trainer` owes **≤ 35** with no release in preparation, down from 64, and every item the rule removed is reachable in one click from a line that says why it was removed — **31**, from 64. requirement 26→3, test 15→5, issue 22 unchanged, unpushed commit 1 unchanged; 31 owed + 33 suppressed = 64. The 33 render as `Quiet · 23 · PHASE-015, PHASE-018, PHASE-999` under Features and `Resting · no feature in flight` (10) under Tests, each row carrying its subject and that subject's status
- [x] A manual test whose procedure has subsections is runnable — the 8 currently unrunnable in `your-trainer` produce steps, and a test that genuinely has none says so on its row instead of silently omitting the button — 8 of 8 fixed; **every manual test in the fleet now parses** (0 of 65 unrunnable). TST-0018 yields 8 steps and TST-0013 yields 107, verified through a live sidecar. A genuinely step-less test now says so on its row instead of hiding the button
- [x] `missing_issue_refs()` reports a true count for `your-trainer` rather than 158 of 158, and the row → feature link is readable for the sections that name one — 158/158 → **73/158** on your-trainer (this repo 7 → 0), and all 60 blocking rows name a subject where 0 did
- [x] Publication is a view, and it is **non-empty in all 12 repos** — every repo reaches at least rung 1, and a repo with no remote says so rather than rendering blank — walked across the whole fleet; `articles` and `project-os-bench` reach `commit` alone and read as complete. `test_the_publication_view_renders_in_every_repo` FAILS on an unreadable repo rather than skipping it
- [x] The 60 unchecked Tier 1/2 rows are reachable from a surface that **names the number**, and ask for a person only while a release is `draft` — `Release gate · 60 unchecked · no release in preparation`, grouped into 17 areas led by Trainer Compatibility at 20. It asks for nobody today, correctly — your-trainer has no release in preparation
- [x] An obligation kind or note-less source with no routing rule **fails a test**, so per-item routing cannot become the place a kind goes missing quietly — `test_every_kind_routes_somewhere` walks the corpus, the declarations AND every note-less source
- [x] A repo with no `PHASE-*` notes routes obligations correctly — checked against the three that have none (`edankert.com`, `obsidian-supernote-sync`, `project-os`) — checked against all three (`edankert.com`, `obsidian-supernote-sync`, `project-os`); `test_a_repo_with_no_phases_routes_and_labels_without_inventing_one` pins that no empty or invented label appears
- [x] No write path widened: `REQ-0026`/`REQ-0027`'s guards re-checked and `test_every_note_mutating_endpoint_requires_loopback` still enumerates and passes — `test_every_note_mutating_endpoint_requires_loopback` still enumerates and passes; full suite green at **1351 passed, 2 skipped**
- [x] Every feature here carries linked `TST-*` notes at `passing` — [[FEAT-0100]] closed with `tests: []` and both of its blocking review findings were the class a linked test would have caught — TST-0025/0026 on FEAT-0101, TST-0027/0028 on FEAT-0102 — all four `passing`, three automated and one the manual fleet walk

## Notes

**Order.** [[ISS-0172]] and [[ISS-0173]] are independent bug fixes and can land immediately; neither waits on the ADR. [[FEAT-0101]] needs [[ADR-0028]] accepted, because per-item routing is the decision rather than an implementation detail. [[FEAT-0102]] needs the ADR and reads better after [[ISS-0173]], which is what makes the gate scopeable.

**[[ADR-0028]] is `proposed` and acceptance is Edwin's.** `STATUSES.md` assigns ADR acceptance to a human decision, and this phase is `active` with its central decision undecided — recorded here rather than assumed, because the same asymmetry was the finding at [[PHASE-030]]'s close.

**A view is a corpus; a phase is not.** The two are separate axes and do not partition each other. `issues` spans all three phases — this repo's own [[ISS-0168]] is a publication bug, [[ISS-0172]] is a test-surface bug — and `tests` spans two. Only `intent` and `publication` sit wholly in one phase.

An earlier draft filed issues and tests under implementation and Edwin refused it: *"I thought we agreed that TSTs, and issues were across design work and publication?"* Recorded because the correction is what makes the design coherent — spanning is the normal case, which is exactly why routing has to be decided per item rather than per note type. The registry has only ever had the corpus axis, so an obligation's phase was implicit in its type; that works for the corpora that do not span and silently fails for the ones that do, which is why `tests` had to straddle and publication had nowhere to live. One gap, seen twice.

**Triage is owed in every phase**, because its subject is the issue itself — nobody has read it yet. That is why it is the one obligation the rule does not shrink, and it follows from the model rather than being carved out of it.

## Closed 2026-08-16

Every exit criterion ticked with evidence, both features `done`, both issues `fixed`, all seven tasks `done`, four `TST-*` at `passing`, [[ADR-0028]] accepted on Edwin's instruction to build. Full suite **1351 passed, 2 skipped**.

**Both of the phase's own prohibitions held.** The number went **down** — 64 to 31 — and nothing vanished: the 33 items the rule quieted are on screen in a collapsed group carrying the reason and one click from their rows.

### What the work found that the plan did not anticipate

1. **Four of the eight unrunnable tests had no procedure heading at all** — their whole body is sections of checkboxes, so no vocabulary could have reached them. A third rule (*the checkboxes are the procedure*) covers them, and every manual test in the fleet now parses.
2. **Two pre-existing parser defects**, invisible until the sections they live in started parsing: a `**bold**` lead-in matched the `*` bullet pattern, and every `- **Expected:** …` line was harvested as a step of its own.
3. **The first `RESTING_STATES` was hand-listed and wrong within the hour** — it named feature terminals and missed `implemented`, `retired`, `fixed`. Derived from `statuses.COMPLETED_STATUSES` now.
4. **A `draft` release three versions behind** in `your-trainer` (REL-0008 at 2.0.2, with 2.1.6 shipped) would have made the gate a permanently re-arming badge — the exact thing this phase exists to avoid. Named as a stale draft; it does not gate.
5. **A dead click since TASK-0373**: the acceptance suite's group url was `/tests/…`, which the renderer drops.
6. **Two surfaces were computing owed-ness with their own predicate** and the suite caught both the moment the rule changed, which is the registry's purpose working rather than failing.

### What is left, and it is the same gate as last time

**The independent review is unpaid at this commit.** `QUALITY.md` asks for a clean-context pass on any change creating a `TST-*` or a `CHG-*`, and this creates four and one. It is recorded rather than assumed away — which is what [[PHASE-030]]'s close got wrong twice — and it is Edwin's call whether to run it. Worth noting that the last one returned `changes-requested` with three of its five blocking findings being errors made in the close-out itself.

**Also standing:** the reconciled criterion on [[FEAT-0102]] — gate rows group by suite section, not by the *Manual Test Environment Breakdown* the criterion names, because that table exists in one repo's suite and has no counterpart in the template. If it earns a place it should be a template feature first.

**Not this repo's to fix, and still true:** `your-trainer` carries `PHASE-017`/`PHASE-018` at `planned` with only `done` features, eight `REQ-*` notes that fail frontmatter parse, and REL-0008's overtaken draft.


## Re-closed 2026-08-16, after a reopen the same day

Edwin, on the shipped result: *"Don't understand I still don't seem to be able to see and execute the current set of acceptance tests for the next release?"*

The phase closed with every exit criterion ticked and **the reported problem still standing**. That is the finding, and it is about the criteria rather than the work: *"reachable from a surface that names the number"* is satisfied by a count, and what was asked for was a way to see and walk the set. A criterion that can be met without the reporter being helped is a criterion written from the implementation's side.

[[FEAT-0103]] closes it — declare the release, list the checks, reach each one's section, walk them with a witness. Reopened rather than given its own phase: same goal line, and it is the half this phase left undone.

**Standing, unchanged:** the independent review is still unpaid, and now covers five `TST-*` notes and one `CHG-*`.


## Reopened again, 2026-08-16

Edwin, reading the walker: *"why do we need the walk button there, why not show the acceptance tests document and maybe a counter on how many checks are outstanding."*

He is right, and it means [[FEAT-0103]]'s stepper is the wrong answer to the question it was built for. The suite already renders 542 live checkboxes that already write; what it lacked was a band, an exception mark, and a release to gate. [[FEAT-0104]] and [[FEAT-0105]] replace the stepper with the document, and retire it rather than keeping two ways in.

**Three reopens in one day is itself a datum**, and the pattern in all three is the same: each close met its criteria and left the reported problem standing. The criteria were written from the implementation's side — *"reachable from a surface that names the number"*, *"a section can be walked"* — and both are satisfiable without the reporter being helped. What Edwin asked for each time was the same sentence: *see and close the acceptance tests for the next release.*


## Independent review, 2026-08-16 — `changes-requested`

Clean-context pass: the notes and the code, no access to the authoring session's reasoning. `reviewed_by: model:claude-opus-5` — same model family as the author, different session and different context (ADR-0013).

Edwin's verdict on the shipped surface: *"I don't understand the functionality … I thought I made it clear that on the publication pages that I want to see the acceptance-tests and be able to independently go through these, I don't need this walk functionality. also, why is there still this prepare button and what is this release gate doing in the left pane still."*

**All three of those are literally true of the code at this commit, and each was already written down as an unmet acceptance criterion on a feature marked `done` or left at `backlog`.** The phase did not miss them; it recorded them and shipped anyway.

### Blocking

1. **The walker was never retired, and it is still the only Walk affordance.** [[FEAT-0104]] criterion *"The stepper (`~walk`) is **removed**, not left beside this"* is unticked and `TASK-0437` is `backlog`. `~walk` is still routed (`renderer.ts:1252`), still built (`buildAcceptanceWalker`, `renderer.ts:7228`), and is still the `action` the registry hands the gate obligation (`obligations.py:524`). The replacement — the cycling mark in the document — is unbuilt (`TASK-0435` `backlog`), blocked by [[ISS-0175]]. So the retirement shipped as a note and the stepper shipped as code.

2. **Two ways to prepare a release, one of them the modal [[FEAT-0106]] exists to remove.** `_publication_groups` still sets `prepare_release` on the release rung (`cockpit.py:4171`), which the renderer draws as a `Prepare release…` button calling `promptPrepareRelease()` (`renderer.ts:10215-10225`, `renderer.ts:7180`) — an `askForText` dialog raised from the left pane. [[FEAT-0106]]'s first criterion is *"Selecting the next-release row opens a page in the centre pane; **nothing pops a dialog**"*, unticked, on a feature at `done`. Worse, `tests/test_acceptance_walker.py:299` **asserts the button exists**, so the guard now pins the defect. [[ISS-0139]] is the standing name for this.

3. **A shipped release's page lists nothing.** `publication.release_payload` emits `contents["ids"]` for the frozen branch (`publication.py:378-383`) and `contents["rows"]` for the derived one (`publication.py:390-396`); `buildReleasePage` reads only `c.rows` (`renderer.ts:7002`). So `~release/REL-0001` renders *"What shipped — 27 feature(s)"* above an empty list. `test_a_shipped_release_reports_what_it_named` asserts `kind` and `count` only, so it passes with the bug present. This is exactly the half of Edwin's model that says *"previous releases should be available with the functionality that was in the release."*

4. **`~release/<id>` is unreachable from the UI.** The only emitters are `cockpit.py:4215` and `:4227`, both on the *next* release row. Released rows on the release rung carry `url: /docs/<rel>` (`cockpit.py:4128-4131`), i.e. the note. So the page built for named releases can only be reached by typing a URL.

5. **A shipped release's page shows today's gate.** `release_payload` computes `acceptance.gate_payload` unconditionally (`publication.py:398`) and the renderer draws the section whenever `gate.exists` (`renderer.ts:7027`), so `REL-0001` — `released` — displays *"Release gate · N unchecked"* about checks that did not exist when it shipped.

6. **The `[!]` escape hatch shipped without its accountability half.** `acceptance.py:92` admits `!` as a mark and `Item.settled` (`acceptance.py:179`) counts it as settled, so `blocking()` drops it. But `TASK-0436` (*an undocumented exception is owed*) is `backlog` and `obligations.NOTE_LESS` holds only `unpushed commit`, `undeployed commit`, `standing document`, `release gate`. Verified: a hand-written `- [!]` removes a check from the gate with no justification, no release-note entry, and nothing owed — the inverse of `TESTING.md` line 113. [[FEAT-0104]] reads `backlog`, which hides that the permissive half of it is live.

7. **[[TST-0031]] is `passing` and its title names behaviour that does not exist.** *"…an unjustified exception is owed"*. `tests/test_acceptance_exceptions.py` has five tests; none asserts an obligation, because there is none. The note says *"the assertions are its acceptance criteria"* — 3 of [[FEAT-0104]]'s 11 have an assertion.

8. **[[FEAT-0105]] and [[FEAT-0106]] are `done` with 0 of 8 and 0 of 9 acceptance criteria resolved.** Nothing catches this: the validator has `REQ-BOXES` for requirements and `PHASE-BOXES` for phases, and no equivalent for a feature's own criteria — and both features carry `requirements: []`, so `FEATURE-REQ` is inert too. Findings 1, 2 and part of 3 were all *already written* as unticked boxes. The close-out gate that would have caught the reopen does not exist.

### Coherence, which is the reporter's actual complaint

The Publication surface asks a reader to hold **nine** distinct concepts: rungs, the release gate, `Needs you`, `Quiet`/suppressed, obligations-with-verbs, the four suite marks, the `preparing` flag, the walker, and the release page. Two of the nine are the same fact under different names (`Quiet · N · PHASE-…` on Features against `Resting · no feature in flight` on Tests). Measured on this repo, `nav_payload(mode="publication")` returns six groups of which three say nothing is happening (`To commit` → *"nothing uncommitted"*, `Release gate · 0 unchecked · no release in preparation` → *"nothing blocking"*, `Next release · accumulating`), and **the same six commits appear twice** — six rows in `Needs you` and the same six in `To push · 6`, adjacent in one pane. [[ADR-0025]]'s *"shortcut list, not a second home"* was written for a row buried in a tree; here the structural home is the next group down. On `your-trainer` that is 84 rows for 42 commits.

**Publication is also the only badge-bearing view with no centre-pane landing.** It is absent from `VIEW_LANDING_RELS` (`renderer.ts:5341`) and from `MODES_WITH_VIRTUAL_LANDING` (`renderer.ts:3626`), so selecting it leaves the centre pane on whatever was last open, and opening a workspace in it lands on `README.md` (`renderer.ts:994`). That is precisely the defect [[FEAT-0092]] was built to fix for `features`/`issues`/`tests`; the ninth mode was added after it and did not join.

The acceptance suite now has **four** surfaces: the Tests navigator's tier groups (`cockpit.py:4004`), the Publication navigator's gate group (`cockpit.py:4225`), the release page's gate section (`renderer.ts:7027`), and the walker. `REL-*` notes have **two** navigators — Intent's `releases` group (ISS-0142) and Publication's release rung.

### Smaller, verified

- `acceptance.py` defines `Item.anchor` **twice** (lines 160 and 190); the first is dead.
- `acceptance.gate_payload` writes the key `"excepted"` twice in one dict literal (`acceptance.py:401-402`).
- `_publication_groups` carries the same comment twice (`cockpit.py:4141-4148`).
- Group-level `needs_human` / `owed_verb` are set by `_publication_groups` (`cockpit.py:4163-4165`) and **never read** by the renderer — the only reader is `buildNavRow`, on items (`renderer.ts:9734`).
- `stale_drafts` is returned by `release_payload` (`publication.py:409`) and declared in `ReleasePayload` (`renderer.ts:6892`); nothing renders it.
- `~prepare-release` is still routed (`renderer.ts:1248`) and nothing emits it.
- `Needs you` push rows carry `verb: "Push"` with no `action` (`obligations.py:424-432`), so they draw a label, not a button. The button is on `~history`, one further click.

### What the reviewer would build instead

One page per release, reached from a navigator that lists releases. `~release/next` and `~release/<id>` already exist and already carry contents + gate; make the release rung link to them, render `ids` as well as `rows`, snapshot the gate for shipped releases, and let the suite document itself be where checks are ticked. Then delete: `~walk`, `buildAcceptanceWalker`, `/api/notes/walk-check`, the `release-gate` navigator group, `prepare_release` + `promptPrepareRelease` + `~prepare-release`, and the `Needs you` group on this one view. That is the surface Edwin described — *what do we need to do for a release, what tests need to pass, what documentation needs to be updated* — and it is strictly less code than what is here.

**Not built at all, and named in his model:** *"what documentation needs to be updated"*. Nothing in `publication.py`, `acceptance.py` or `release_payload` reads documentation state for a release.


## Reopened once more, and re-closed the same day

Edwin read the rebuilt view and found six things, all real and all fixed in [[ISS-0179]] — the sharpest being that **the ordering was exactly inverted**: the next release filed under Completed while shipped ones sorted as open work, because a row carried its feature's own status and a next release is by definition full of `done` features.

Two of the six were not about this phase at all. **Every table in the desktop app has been unstyled since the native panes landed** — `base.css` styles `.content table` and `#doc-view` never carries that class. And a feature link rendered broken because the note was renamed and the citation was not; a wikilink whose **id** resolves now resolves, tried last so an exact match always wins.

And Edwin caught the one I would not have: *"if you remove it then it should no longer be included in the badge."* The publication obligations were still routed to a view that no longer shows them. A count on a button that opens a view not containing what it counts is worse than no count.

## Closed 2026-08-16 — the third close, and what the first two got wrong

Nine features, seven issues, one ADR, twenty-four tasks, ten test notes, and **Edwin asked the same question at the beginning and at the end**: *see and go through the acceptance tests for a release.*

Two closes were declared before this one. Both met their exit criteria. Both left the reported problem standing. The independent review found why, and it is the most useful sentence this phase produced:

> **Every one of Edwin's three complaints is already written down in this repo as an unticked acceptance criterion on a feature that was closed anyway.**

[[FEAT-0105]] reached `done` at **0 of 8** criteria. [[FEAT-0106]] at **0 of 9**. The criteria said *"the stepper is removed"* and *"nothing pops a dialog"*; the stepper shipped and the dialog was dead. Nothing catches this: the validator has `REQ-BOXES` for requirements and `PHASE-BOXES` for phases and **no equivalent for a feature's own acceptance criteria** — the single systemic finding of the whole phase, and it is unfixed. Filed nowhere yet because it belongs upstream.

### The shape of the mistake, three times over

A replacement was added and the thing it replaced was left running: the walker beside the document, the gate group beside the release page, the header button beside the row action. That is why the surface grew every round while the answer never arrived — and why the fix, when it came, **deleted more than it added**.

### What finally worked

Reading. `your-trainer` has kept Edwin's whole model by hand for twelve releases — `tests_verified:` naming the suite snapshot each shipped against, `## Known issues (shipping with)` in half the notes, seven platform artifacts named for their release — and **nothing read any of it**. [[FEAT-0107]] is mostly three sections on a page.

### Re-homed to [[PHASE-999]], not finished

Five items are parked in the sentinel with their reasoning intact. `deferred` is not a resolved status, and carrying them inside a closed phase would let it claim work it did not do.

### Standing, and named rather than assumed away

- **[[FEAT-0104]] deferred** at 6 unbuilt criteria. [[ISS-0175]]'s cause is now known — Markdown lazy continuation, not a parser bug — and its dangerous half is closed, but where a task list opens with no blank line those checks have no checkbox at all. That is a source-formatting question in the repo that owns the suite.
- **[[ISS-0177]] deferred, deliberately.** The `[!]` escape hatch is live without its accountability half; Edwin's call was to keep it and record the gap.
- **[[ISS-0178]] deferred, upstream.** A test has no terminal status, so a test whose subject is deleted cannot be retired at all.
- **Documentation state** — Edwin named it as part of his model and it is not built. It maps to `changes:`, empty in every repo in the fleet, and deriving it is a design question rather than a lookup.
- **The independent review's verdicts stand at `changes-requested`** on the phase and five features. They are not flipped: the author does not judge his own work, and what those verdicts describe is true of what was shipped at the time they were written.

## Reopened 2026-08-16 — the functionality review, and four features it produced

Edwin, after the third close: *"I asked for a functionality review, not for a code review, document these reported issues and then start an independent functionality review with a goal to come up with some new/novel ways to support this new release functionality."*

The review was run with an explicit brief **off** correctness and onto design — what a person does on release day and where the tool is absent, what the record already knows and could infer, what is risky and could be made visible. It read `../your-trainer`'s twelve real releases end to end, ran **this repo's own parser against all twelve git tags**, and returned ten proposals. Four features are opened from them. Everything below was re-measured here before being written down, and the review's own two errors are recorded rather than inherited.

### The finding that reframes the gate

`acceptance.parse` against `git show <tag>:docs/tests/ACCEPTANCE_TESTS.md`, twelve tags:

```
v1.1.0  1 blocking · v1.1.20 15 · v1.1.53 85 · v1.1.55 130
v2.0.0 22 · v2.0.5 47 · v2.1.0 47 · v2.1.6 47 · HEAD 60
```

**Twelve releases, twelve blocked ships.** *"Release blocked — 60 unchecked"* is not news; it is the steady state, and today's 60 is not even elevated. A sentence that has been correct and ignored twelve times is one the reader has learned to skip. That is [[FEAT-0108]], and its answer is the delta — 13 new, 47 chronic, 0 regressed — plus the 20 rows whose subject is `backlog` and which [[ADR-0028]] decision 3 already said should be quiet.

### What the surface asserts that is not true

[[FEAT-0109]]. `REL-0012` names `TST-0011` under the heading *"Acceptance tests as executed"*. TST-0011 has **18 checkboxes, all unticked, and 18 blank evidence slots**. And `last_verified` equals `created` in **15 of the 16** TST notes carrying it — the field has never recorded a verification anywhere, which retires this project's earlier and weaker statement that *11 of 21 were verified before their features last moved*.

### The one with a consequence outside the documentation system

[[FEAT-0110]]. Eight release notes carry `## Post-Release Actions` with **37 unticked boxes**, and the release page — which already reads `## Known issues` from the same note — walks past the only section containing outstanding work. Four boxes are provably done, three provably open, one unknowable.

### What was already in the record and got invented again

[[FEAT-0111]]. [[ISS-0181]] items 1 and 2 asked for a mark meaning *intentionally left open* and a way to attach text. Both exist in `../your-trainer` — `[~]` and `[F]`, with `**<Verdict> <date>** — <reason> [[ISS-…]]`, and `✅ (<witness>)` used 22 times. This repo invented `[!]` for the same purpose in a form no suite writes. **Items 3 and 4 of [[ISS-0181]] are not addressed** and the issue stays open, re-homed here from [[PHASE-999]].

## Found in the fleet — needs filing elsewhere, not fixed here

Four defects in **other repos**, found by this review. They are recorded here because this work found them and because two of them are the evidence [[FEAT-0109]] and [[FEAT-0110]] stand on. **None is filed yet** — they belong in the repos that own them, and that is Edwin's call.

1. **Two of seven store artifacts do not parse.** `REL-0007-v2.0.0-play-store-descriptions.xml` and `REL-0009-v2.0.4-play-store-listing.xml`, both ending with leaked tool-call closing tags (`</release-notes></content></invoke>`) after the root element. The declared source of truth for store copy in ten locales, one of them the file the public 2.0 announcement was cut from.
2. **A warning is live 85 days after its fix shipped.** `../your-applications.com/public/your-trainer/compatibility.json` still reads `investigation_status: "investigating"` for two trainers. `REL-0010` (v2.0.5, 2026-05-23) says to retire it, in an unticked checkbox.
3. **The public release-notes page stops at v2.0.2**, *"Last updated: 2026-05-21"*. Three shipped releases absent — and that repo is the deploy-only one, so fixing it still does not publish it.
4. **`published` is instructed as a release status in four release notes** and is not one — `STATUSES.md` allows `draft`, `released`, `reverted`. A **template** defect, upstream.

## Standing questions this reopen does not answer

- **The gate under-reports by 53.** 54 checks carry a `RE-RUN (TASK-####: reason)` annotation and 53 are still ticked, so the honest blocking number is 113. [[TASK-0448]] puts it on the page with its number; whether stale evidence should *block* is a change to what shipping means and is deliberately left to Edwin.
- **`TESTING.md` rule 5 has never been executed** in twelve releases — 68 Tier 3 rows and 54 annotations survive a rule that says a verified release clears them.
- **A feature's acceptance criteria are still unguarded.** The validator has `REQ-BOXES` and `PHASE-BOXES` and no equivalent for a feature. This is the systemic finding of the first three closes, it is why [[FEAT-0105]] and [[FEAT-0106]] closed at zero ticked criteria, and it is still unfixed. The four features opened here carry criteria that nothing will check.
- **The review's ranking placed a run-plan generator and a fleet blast-radius panel above these four.** Both are real and neither is opened: the first needs ordering heuristics that would harden guesses into false precision, the second needs cross-repo write reasoning this phase has no decision for.

## Two corrections the review made to itself, recorded so they are not re-made

**`ACCEPTANCE_TESTS_v2.1.0.md` is not a snapshot.** It was first proposed for retirement as a hand-copy that git already holds. It shares **zero of its 300 check titles** with the living suite and says in its own header that it is a *delta* — an independent per-release suite with its own gate rules and a `# Pending — required before tag` section. Retiring it would have deleted a load-bearing artifact. The corrected reading is stronger: it is the shape [[FEAT-0108]] should eventually generate.

**`[~]` and `[F]` had been reported as never used.** True of `ACCEPTANCE_TESTS.md` at all twelve tags, which is what was measured; false of the corpus, where seven rows use them with a consistent grammar. [[FEAT-0111]] exists because the second measurement was taken.

## Closed 2026-08-16 — the fourth close, and the audit it ran on itself

Four features built, tested and walked. **1483 passed, 2 skipped** (from 1400); three new `TST-*`; **24 mutations, all killed**, each named in its task before the guard was written and each behind an apply-check.

### What a person will notice

| | before | after |
| --- | --- | --- |
| Next release | `Release gate · 60 unchecked` | `13 new · 27 chronic · 0 regressed · 20 quiet` |
| — and the history | — | *"12 releases, median 36 blocking at ship. This is 60."* |
| — stale evidence | counted as passed | **53**, named in their own group |
| A shipped release | `tests_verified` as links | `TST-0011 · 0/18 walked · 0 evidence · never verified` |
| — its artifacts | files to open | two of seven reported **corrupt**, with line numbers |
| — what it still owes | nothing read it | **37 boxes**, each with a verdict |
| A gate row | edit the file by hand | **Pass / Partial / Fail** with a required reason |

### The design correction this phase's work turned on

Applying [[ADR-0028]] decision 3 verbatim to acceptance rows quieted **60 of 60** and the gate disappeared. `RESTING_STATES` contains `done` and `fixed`, and nearly every acceptance row names a shipped feature or a fixed issue — which is the right answer for a requirement and precisely the wrong one for a regression check. The rule for this population is narrower and is now written down as `obligations.NOT_YET_BUILT`: *a screen that does not exist cannot be walked.* Everything else asks.

The ADR is amended rather than re-decided; the principle did not change, its application did.

### The audit, and why it is recorded rather than quietly fixed

The four features were first set to `done` with **all 32 acceptance criteria unticked** — exactly what [[FEAT-0105]] (0 of 8) and [[FEAT-0106]] (0 of 9) did earlier in this same phase, and what the independent review called the phase's single systemic finding. It happened again because a blanket regex is faster than reading.

Caught before commit, by reading them one at a time. **Six were genuinely unbuilt and were built**: the age in days on an open box, the offered tick, the lazy-continuation refusal, `releases_since`, the historical line, and links on the quiet subjects. **Two are reconciled `[~]`** with the reason on the line — the badge-count criterion (the gate contributes one obligation, never sixty, so nothing could drop) and burden ordering ([[TASK-0449]], cancelled).

**The validator still has no `FEAT-BOXES` check.** That is unchanged from the previous close and remains the phase's systemic finding: `REQ-BOXES` and `PHASE-BOXES` exist and nothing guards a feature's own criteria. Three closes have now depended on somebody choosing to read them.

### One thing built and deleted

A burden-tag scanner, written for [[TASK-0449]] and removed the same hour: `ACCEPTANCE_TESTS.md` carries no burden tags in any repo, the scanner was **6-for-6 false positives** on `[Debug]` inside quoted workout names, and `TST-0013` — the one document that does carry them — has no tier headings, so `parse` returns zero items for it. The task's own scope note had predicted this: *"a heuristic that infers burden from prose would be wrong quietly."*

### Standing, and named rather than assumed away

- **Whether stale evidence should BLOCK.** 53 ticked rows carry a `RE-RUN` annotation, so the honest number is 113 rather than 60. It is on the page with its number; making it block changes what shipping means and is Edwin's.
- **`TESTING.md` rule 5 has never been executed** in twelve releases — 68 Tier 3 rows and 54 annotations survive a rule that says a verified release clears them.
- **[[ISS-0181]] items 3 and 4 stay open.** The save/reload interruption is a file-watch problem; completing a release needs a ship transition this phase did not build. [[FEAT-0110]] supplies only the *after*.
- **Four fleet defects are recorded and unfiled** — two corrupt store XMLs, the live `compatibility.json` warning, the public release-notes page three versions behind, and `published` instructed as a status that does not exist. They belong to `../your-trainer`, `../your-applications.com` and the upstream template.
- **The independent review gate is unpaid at this close.** `QUALITY.md` asks for a clean-context pass on any change creating a `TST-*` or `CHG-*`; this creates three and updates one. Edwin's call, and the last two passes both returned `changes-requested` with findings that were real.

## Reopened 2026-08-17 — the document is the surface, and its checkboxes are unsafe

Edwin, reading the shipped work: *"I thought we would have the checkboxes in the acceptance-tests.md to have 3 states and we would allow to add text there to make sure the ! state was documented?"*

He is right and [[FEAT-0111]] is not it. It put Pass/Partial/Fail on the **Publication page's gate rows**; the agreed design was the mark cycling **in the acceptance document itself**, which is [[FEAT-0104]] — deferred at six unbuilt criteria. A replacement was built beside the thing it was meant to replace, for the third time in this phase.

Reviewing it turned up [[ISS-0184]], which is worse than the missing feature and was **reproduced rather than reasoned**: clicking the checkbox at DOM index 257 in `../your-trainer`'s suite returns `ok` and writes to line 413 — a different check in a different section. 579 source boxes, 542 rendered ones, 37 task lists absorbed by lazy continuation. [[ISS-0175]] gave the *labelling* path a count-mismatch guard and the *write* path never got one; [[FEAT-0103]] refused to build the new walker on this endpoint for precisely this reason and wrote down why, and nobody applied that back.

**The vocabulary is settled by measurement.** Across every acceptance suite in the fleet: `x` 851, blank 152, `~` 7, `F` 1, and **`!` zero**. `[!]` exists only in this repo's parser and in this feature's own plan. Edwin: *"I have no problem using ~ instead."* So `!` stays readable and is never offered again, and the four marks mean:

| mark | walked? | result | blocks |
| --- | --- | --- | --- |
| `[ ]` | no | — | yes |
| `[x]` | yes | passed | no |
| `[~]` | yes | partial, shipping with it | no |
| `[F]` | yes | failed, tracked | yes |

`[ ]` and `[F]` both block and mean opposite things about whether anyone did the work — which is the whole reason `F` earns a place rather than collapsing into blank.

## Closed 2026-08-17 — the fifth close, and the blocker that was never the recorded one

Four things Edwin asked for, all built:

1. **The mark cycles in the document** — `[ ]` → `[x]` → `[~]` → `[F]` → `[ ]`, each click writing immediately.
2. **Both non-pass states carry text, and are refused without it** — *"we also needed a way to say that the test could not be executed but it should not holdup the release. With text box, also for F we also need a text box."*
3. **The address, not the position** — every row stamped with its check number; the write resolves it or refuses.
4. **`!` retired** — never offered again, still readable.

### The finding that mattered

[[FEAT-0104]] was deferred citing [[ISS-0175]], and that was the wrong blocker. The real one: **`pymdownx.tasklist` understands two marks.** A `[~]` or `[F]` row renders with *no input element at all* and its mark left as literal text, so an HTML checkbox can never hold four states and the whole document's alignment guard trips. `../your-trainer`'s seven hand-written marks have been unclickable since they were written.

The row's **list item** is stamped instead, at priority 26 — above `task-list` at 25, which is the entire trick, because below it the literals are already gone.

### Three numbers that came down, and only one was the document

| reading | cause | mine? |
| --- | --- | --- |
| 542 of 579 rendered | a mid-edit read of a file Edwin was writing at 08:58 | **yes** |
| 509 of 579 addressed | the address emitted from two places at once | **yes** |
| 70 of 579 unaddressed | a hand-rolled name split truncating any name with a colon | **yes** |
| 6 of 579 unaddressed | lists opening under a paragraph — the document's formatting | no |

[[ISS-0184]] was filed on the first of those and **withdrawn the same day**. The reproduction appeared to confirm it because it checked its answer against the same stale index table that produced the claim; a reproduction that only consults its own premise is not one. What survives is the latent fragility — the write path has no count guard where the labelling path does — and the fix was worth making anyway.

### Standing

- **[[ISS-0177]]'s residue**, narrower and named: a `[~]` **hand-written** with no reason still carries none and nothing asks. A source-level refusal cannot reach a text editor.
- **6 rows in `your-trainer`'s suite and 36 in its v2.1.0 delta** need a blank line in those files. The cockpit states the count and the remedy and changes nothing — reformatting the file the gate reads is not its call.
- **The independent review gate is unpaid at this close**, for the second phase close running.

## Re-closed 2026-08-17 — the affordance, from use

Edwin, the day the control shipped: *"The new checkbox is a little small and they seem to be inside another box? Also, maybe if we bring up a dialog, can we then have one dialog with all options?"*

Both right, and [[ISS-0185]] records that the box-in-a-box was **three** distinct mistakes stacked — tasklist's `label` left behind, the control mounted before a block element, and a border drawn around a glyph that is already an outline.

The second half retires a design Edwin himself preferred earlier (*"I actually like the cycling checkbox idea better"*), and the reason it inverted is worth keeping: a cycle is right for two or three states, and at four with two requiring justification the intermediate stops stop being steps toward anywhere. `[ ]` → `[F]` cost three writes and two prompts. It is one dialog and one write now.

## Re-closed 2026-08-17 — the vocabulary stopped being ours

Third mark vocabulary in two days, and the last one, because it is not this project's: [[ADR-0029]] adopts Minimal's alternate checkboxes. Six of its 22 values mean something to a release gate; the other sixteen parse as unrecognised and block, which fails safe.

| | blocks | needs a reason |
| --- | --- | --- |
| `[ ]` to-do | yes | — |
| `[x]` done | no | optional witness |
| `[/]` incomplete | no | **yes** |
| `[-]` canceled | no | **yes** |
| `[!]` important | **yes** | **yes** |
| `[?]` question | **yes** | **yes** |

`[!]` **reversed meaning** — a non-blocking release exception yesterday, a blocking failure today — and that was only safe because it was written in zero suites across twelve repos, verified before the decision rather than after. The exception *concept* moved to `[-]` and kept its field and its separate count.

One correction to my own proposal, made by reading rather than reasoning: I had `~` aliasing `[-]`. All seven live `~` rows say *"Partial pass"*, so it aliases `[/]`.

**Three blocking marks that mean three different things** — nobody looked, somebody looked and it broke, somebody looked and could not tell. That distinction is the reason for the vocabulary, and collapsing any pair would lose it.

## Re-closed 2026-08-17 — the control shows the mark

Second round of visual feedback ([[ISS-0186]]) and the simplest answer available: stop drawing glyphs and show the literal. `[ ]` `[x]` `[/]` `[-]` `[!]` `[?]` in the monospace face, and the dialog as one column at 44rem instead of six two-line buttons crammed into two.

Worth recording because it is the pattern of this whole phase in miniature — three of the six previous glyphs were symbol characters chosen for meaning and sized up for legibility, when the thing they represented was already a legible character. The record's own notation was the right notation.

## Re-closed 2026-08-17 — select, then Save

Third round on the same control ([[ISS-0187]]), and the one that made it usable: the repaint holds its scroll, a server refusal is shown instead of swallowed, and the dialog selects rather than commits so there is a `Save` to press.

Two things worth carrying out of it. **The reported "comment did not reach the file" was a symptom of the missing Save**, not a write bug — the write path was proved correct twice — but reproducing it anyway turned up a genuine silent-refusal defect that had never fired. And **two of six mutations survived first time, both because my guards were wrong rather than the code**: one compared two CSS rules including their selectors so they could never be equal, the other grepped for a string the surrounding prose also contained. A guard that can pass for a reason unrelated to the thing it names is not a guard, and that is now the third distinct way this session has produced one.

## Re-closed 2026-08-17 — the scroll fix that did nothing

[[ISS-0188]]. The previous close fixed this and it did not work: `applyScrollTarget` defers its scroll to `requestAnimationFrame`, so a synchronous restore around `navigateTo` ran a frame early and was overwritten by `scrollTop = 0`. The position is a parameter now, honoured inside the frame ahead of every other branch.

**The guard passed while the bug was live**, and that is the finding worth carrying out of this phase. It asserted that `repaintDoc` read `scrollTop`, that the read preceded the navigation and the write followed it — all true, all irrelevant, because the defect was about *when a callback runs* and the assertion was about the shape of the source.

Four guards this session could pass for a reason unrelated to what they name: two CSS rules compared including their selectors, a grep for a string the surrounding prose contained, a node checked as created rather than appended, and this. The last two are the same shape — **two ends and no middle**.

**And the underlying gap is named, not closed:** there is no way to behaviourally test the renderer in this repo. Every renderer test is a Python scan of `renderer.ts`; there is no DOM, no `requestAnimationFrame`, no JS test runner in `desktop/package.json`. All four rounds of feedback on this control were found by Edwin using it. A green suite should not be read as saying otherwise.
