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
issues:
  - "[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]"
  - "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]"
  - "[[ISS-0174-Publication-Showed-One-Item-Twice-And-A-Row-Nobody-Could-Click]]"
  - "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]"
  - "[[ISS-0176-Every-Prompt-In-The-Desktop-Shell-Is-Dead]]"
requirements: []
tasks: []
depends: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0022]]", "[[PHASE-030-Obligations-Go-Home]]", "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"]
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
