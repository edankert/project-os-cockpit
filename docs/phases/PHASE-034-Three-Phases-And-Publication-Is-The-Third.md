---
type: "[[phase]]"
id: PHASE-034
aliases: ["PHASE-034"]
title: "Three phases, and publication is the third — what needs a person is routed to the phase that owns it, and asks only while that subject is in flight"
status: active
order: 34
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
goal: "Give the tool the phase it is missing. Publication becomes a first-class view over the whole ladder — commit, push, deploy, versioned release — and every obligation is routed to the phase that owns its subject and asks only while that subject is in flight, so what needs a person is smaller, sorted, and inspectable rather than one undifferentiated number."
features:
  - "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"
  - "[[FEAT-0102-Publication-Becomes-A-View]]"
  - "[[FEAT-0103-The-Gate-Is-Walkable]]"
  - "[[FEAT-0104-The-Suite-Is-The-Surface]]"
  - "[[FEAT-0105-There-Is-Always-A-Release]]"
issues:
  - "[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]"
  - "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]"
  - "[[ISS-0174-Publication-Showed-One-Item-Twice-And-A-Row-Nobody-Could-Click]]"
  - "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]"
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
