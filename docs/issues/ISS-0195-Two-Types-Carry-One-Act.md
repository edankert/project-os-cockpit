---
type: "[[issue]]"
id: ISS-0195
aliases: ["ISS-0195"]
title: "Two types carry one act — but for 9 of 22 manual `TST-*`, not for all 22: the ones naming a capability are checks wearing a test id, and the ones naming a change are not"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: docs
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ISS-0178-A-Test-Cannot-Be-Retired]]", "[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
---

# Two types carry one act

> [!warning] Revised 2026-08-18 after independent review returned `changes-requested`.
> The first draft asserted the thesis over all 22 manual `TST-*` notes and carried five wrong figures, one governance row the corpus falsifies, and one claim refuted by shipped code. The review is appended in full and its corrections are folded into the body below rather than left as an appendix — but **what was wrong is named at each point**, because a note whose errors are only recorded at the bottom is one somebody quotes from the top. The direction survived; the scope did not.

## How this surfaced

Edwin, 2026-08-18, on being shown that the Tests view leads with `Needs a run` (manual `TST-*`) and buries the acceptance tiers beneath it: *"I didn't realise that TSTs required my attention as well as CHKs … that means that we potentially use 2 different types for the same / similar functionality."*

The observation is correct and the corpus bears it out — for **part** of the population. This note records what the fleet actually holds. **No decision is proposed here** — the options are laid out and the adjudication is owed.

## What the fleet holds

Swept across the twelve `SNAPSHOT.yaml`-bearing repos under `~/Dev/repos/`, 2026-08-18, and re-derived independently. **117 `TST-*` notes and 669 `CHK-*` notes**, in four populations rather than the three the first draft named:

| | what it is | type | count |
|---|---|---|---|
| **A** | machine-verified: `command:` set, the runner writes the status ([[project-os-dev#ADR-0010]]) | `TST-*` | **54** with `command:`, 62 `kind: automated` |
| **B** | **human-walked procedure** — checkboxes, numbered steps or prose | `TST-*` | **22** `kind: manual`, **20** at `ready`, **362 parsed steps** |
| **C** | human-walked check, one note per check | `CHK-*` | **669** across three repos |
| **D** | **frozen per-release suites** — [[ADR-0030]] decision 5, `type: [[test]]` with non-`TST-*` ids | `test` | **3** in `your-trainer`, **377 steps** |

**D is larger than B and the first draft missed it entirely.** `ACCEPTANCE-CHECKLIST-2.1.1` (42 steps), `ACCEPTANCE-RUN-2.1.1` (35) and `ACCEPTANCE-TESTS-V2-1-0` (300) render as manual rows in the Tests view. Two `kind: hybrid` notes (cockpit TST-0027, `your-trainer` TST-0010) fit none of the four.

Per repo, the human-walked `TST-*` population:

| repo | `kind: manual` | at `ready` | automated | `command:` | `CHK-*` |
|---|---|---|---|---|---|
| your-trainer | **15** | **15** | 2 | 2 | **579** |
| project-os-cockpit | 5 | 3 | 17 | 42 | 34 |
| your-health | 2 | 2 | 6 | 6 | 0 |
| your-sudoku | 0 | 0 | 13 | 0 | 56 |
| yourtrainer-mcp | 0 | 0 | 15 | 0 | 0 |
| obsidian-supernote-sync | 0 | 0 | 5 | 0 | 0 |
| project-os-dev | 0 | 0 | 4 | 4 | 0 |

**`your-sudoku` is the control this table contains and the first draft did not read**: 56 checks, 13 automated tests, **zero** manual tests. B is 15-of-22 concentrated in one repo. That is evidence B is *migration residue in two repos* rather than a structural third type — and it is the single most important line in the table.

*Corrected: the first draft put 11 further `your-health` notes carrying neither `kind:` nor `command:` into row B. They are population A in substance — all `passing`, all with zero checkboxes, and **9 of the 11 name JVM/Robolectric suites or `./gradlew` in their bodies** (the other two carry no automation cue either way). Counting them as human-walked inflated the population by half.*

## The thesis holds for 9 of 22, and the line is capability versus change

*This is the review's central correction, and it is right.* "B and C are the same act" was asserted flatly over 22 notes. Split by what each note's frontmatter points at:

| | count | what they name |
|---|---|---|
| **capability** — checks wearing a test id | **9** | `your-trainer` TST-0001..0008 link only `FEAT-*`/`REQ-*` (`FEAT-0007`, `FEAT-0050`, `REQ-0001`…) — a standing capability, which is **exactly `CHK-*`'s `covers:` semantics**. `last_verified` 2026-01-27 / 2026-04. Titles like *"Bluetooth Connection Flow"*, *"Resistance Control"*. |
| **change** | **13** | cockpit TST-0011 (13 tasks), TST-0024 (9 tasks, 2 reqs), `your-trainer` TST-0011 (5 tasks, 4 issues), TST-0009 (2 tasks in `related:`), TST-0013 (4 tasks, 13 issues, 9 features). |

*The review put TST-0009 in the standing set and counted 8/14; measured against `related:` as well as the typed fields it names two `TASK-*` and belongs with the change-verifiers, so the split is 9/13. The distinction the review drew is unaffected and sharper than its own wording: the eight do not merely lack change links, they link **capabilities**, which is what a check links.*

`your-trainer`'s TST-0018 states its own retirement path in prose: *"Once TASK-0780 introduces the entitlement seam, the logic half moves into TST-0016 and what remains here is the environment half, which stays manual permanently."* **A check has no retirement path into an automated test; a change-verifying manual test does.** That is the principled difference the first draft flattened.

Against it: **149 of 669 checks name a `TASK-`/`ISS-` in `covers:`**, so checks are not purely standing behaviour either. The line is real and softer than a clean split.

## The same behaviour is walked twice, here, today

`docs/features/agent-hooks/plan/tests/TST-0011-Live-Session-Instrumentation.md` (`kind: manual`, `passing`, `last_verified: 2026-07-27`) is a 13-item checklist covering FEAT-0019/0020/0021/0022. Two of its items have their own `CHK-*` notes:

| TST-0011 item | check |
|---|---|
| 1. *"run `claude`, submit a prompt. Expect: rail dot flips to busy, activity strip appears…"* | **CHK-0021** — *"A session is visible while it runs: the workspace dot tracks its state, the activity strip fills, and the notes it touches show the agent chip"* |
| 7. *"a live-session banner… 'Agent sessions' renders as a column…"* | **CHK-0022** — *"The fleet view: open `~agents`. Expect: sessions across every workspace, with cost and queue state"* |

Two records of one behaviour, walked on two different days (2026-07-27 in the TST's `## Runs`; 2026-08-11 in each check's body), neither aware of the other. Note that this TST is in the **change**-naming half — so duplication is not confined to the nine.

`your-trainer` shows the second-order cost: its TST-0011 invents **its own tier vocabulary** — *"Tier A (release-gating) / Tier B (supporting)"* — inside a repo whose suite already means something specific and different by Tier 1/2/3.

## Governance, restated against what is implemented

*The first draft tabulated six differences and claimed none followed from what the two types are. Re-tested, three are defensible, one is falsified by the corpus, and one is refuted by shipped code.*

| | manual `TST-*` (B) | `CHK-*` (C) | verdict |
|---|---|---|---|
| obligation badge | `ready` + manual + **[[ADR-0028]]'s in-flight rule** — live total **6** (cockpit 1, `your-trainer` 5); the other 10 sit in a named `Resting · no feature in flight` group | never — [[ADR-0027]] / [[ADR-0030]] decision 3 | **defensible.** A manual TST rests when its subject reaches terminal; a check can never rest, which is *why* checks were exempted. The first draft cited ADR-0028 and never applied it, and so described a 20-row problem where the live surface has **6** |
| gates | **also gates releases** — `your-trainer`'s `REL-0012` (`released`) carries `tests_verified: [… TST-0011, TST-0014]`, and TST-0011's own body labels its A tier *"release-gating"* | the release gate | **the first draft's row was false.** There is no clean feature-gate-versus-release-gate split |
| re-arms by | time — but staleness is evaluated after the owed and resting buckets, so it can fire only on a `passing` manual test: **2 of 22** | change — `invalidated_by:` set on **54 of 669** (8%) | true in mechanism, **the exception on both sides**, not the rule |
| independent review | required at `passing` — engages on **2 of 22** | exempt — *"the review of a check is the walk"* | real but small. Separately: **TESTING.md and QUALITY.md disagree on what this gate keys on** — status versus note-touched; the validator implements TESTING.md's |
| terminal status | **none** — [[ISS-0178]] (`deferred`). This repo's TST-0029 is the live instance: subject deleted by FEAT-0107, retired in prose because the vocabulary has no word, and still counted among the 20 | `retired` | **the strongest row** |
| granularity | 362 steps across 22 notes; **180** checkboxes, and **16 of the 22 hold none at all** | one note per check | **the first draft's sharpest claim was its wrongest** — see below |

**"The boxes are addressable by nothing" is refuted by code that shipped.** `manual_test_steps()` parses all 362; `steps=` is on every row of the live Tests nav (`TST-0013 steps=107`, `TST-0011 steps=18`); `~tests/<TST>/run` opens a stepper; `POST /api/notes/test-run` → `note_writes.stamp_test_run()` writes a per-step result under `## Runs`. A surface counts them and a mark writes to them.

**What survives is narrower and real:** `_RUNS_HEADING_RE` occurs *only in the writer*. Nothing reads `## Runs` back, so per-step results are write-only prose and the note's own status is the sole state a run leaves behind. *"Which of TST-0013's 107 steps is currently unproven"* is unanswerable. That — not invisibility — is the defect.

*Two further figures corrected: `your-trainer`'s TST-0011 holds **18** steps, not the "~40" first written (off by 2.2×); and this repo emits **22** `[REVIEW]` warnings, of which only **2** are on `kind: manual` notes.*

## And the bridge between A and C is empty everywhere

[[ADR-0030]] defined `automation:` (`full`/`partial`/`manual`) and `covered_by:` so a check could say *a machine already covers me* — the field pair that would let automated tests absorb part of the manual burden, and the mechanism TESTING.md's Tier 2 → Tier 3 promotion rule depends on.

Measured across all three suites: **`automation: manual` on 669 of 669, `covered_by: []` on 669 of 669.** Meanwhile **203 of `your-trainer`'s 579 check bodies carry the migration's parenthesised annotation** (181 `(partially automated`, 22 `(automated`, zero `(fully automated`); **221** mention automation at all. ADR-0030 recorded 201 annotated rows pre-migration. *The first draft said 208, which is none of these figures.* The migration carried the annotation as text and did not populate the fields defined for it.

Consequence, live: the `~checks` filter bar offers no automation axis at all — the backend emits a single-valued axis and `buildCheckFilters` drops any axis with fewer than two values, deliberately. So the one question *"which of these does a machine already do?"* cannot be asked of the corpus that answers it in prose 203 times.

## The asymmetry that actually costs: a test can be automated in place, a check cannot be automated at all

*Edwin, 2026-08-18, after the review: "the issue I have with the 2 different types … is that it becomes very difficult to move a CHK to an automated test."* **This is the finding, and it inverts the review's own reasoning.** The review used *"a check has no retirement path into an automated test; a change-verifying manual test does"* as the argument for keeping the types apart. That asymmetry is not a justification — it is the defect, and it is one-directional.

**A manual `TST-*` automates in place.** Add `command:` to its frontmatter and `tools/scripts/run-tests.py` executes it and stamps its status from the exit code ([[project-os-dev#ADR-0010]]). Same id, same inbound references, same gates, no migration. `your-trainer`'s TST-0018 documents itself taking exactly that route: *"the logic half moves into TST-0016 and what remains here is the environment half, which stays manual permanently."*

**A `CHK-*` has no such path, at four levels:**

1. **No field.** `docs/__templates__/check.md` has no `command:`. A check cannot declare an executable.
2. **No runner.** `run-tests.py` filters on `^TST-\d+` filenames (line 79). A `CHK-*` is invisible to it by construction.
3. **No gate effect.** `Suite.blocking()` is `tier in GATING_TIERS and not settled`, and `settled` is `checked or reconciled or excepted`. **`automation:` and `covered_by:` are not in the predicate.** A check marked `automation: full` with a `covered_by:` naming a passing test still blocks the release until a human ticks it by hand.
4. **No writer.** `mark_check` writes `mark`/`verdict_date`/`verdict_reason`; `invalidate_check` writes `invalidated_by`. **Nothing writes `automation:`, `covered_by:`, `tier:` or `status: retired`** — so TESTING.md's documented Tier 2 → Tier 3 → remove path is prose with no action behind it, and `retired` is a status in the vocabulary that no code can reach. `sweep.py:346` hard-codes `covered_by: []`, so every check the sweep creates is born with the link empty.

The two fields ADR-0030 defined for exactly this reach only a facet in the checks view (suppressed at one value) and one stat on the release page. **Automating a check today costs the automation work and buys nothing.**

### What that costs, measured

**15 of the 60 checks currently blocking `your-trainer`'s release say in their own bodies that a machine already covers them.** A quarter of the blocking set. The sharpest is `CHK-0505`:

> Difficult to reproduce on real hardware without a misbehaving trainer. Exercised via `TrainerCompatibilityTestFailureModesTest.silentMode_completesWithScorecardAndNoAbortBanner` … *(automated.)*

Tier 1/2, unmarked, blocking a release — waiting for a person to do by hand the thing its own text says is hard to do by hand and is already automated. That is not a documentation problem; it is the gate asking for work that has been done.

And the data for the fix is already in the corpus: **203 of 579 bodies name their covering test in prose.** The link exists as text and was never moved into the field defined to hold it.

## Options

**The nine and the thirteen are answers to different questions, and no option should be applied to both** — and since the section above, **the deciding property is which type can be automated**, which reorders everything below.

1. **Write the boundary down.** Cheap, reversible, collides with nothing — but the first draft's premise was wrong: TESTING.md does not draw an *automated vs manual* split, it draws *formal test tracking vs the release checklist*, and warns that `level: acceptance` on a `TST-*` is a third thing again. The first draft also quoted `docs/tests/acceptance/README.md` as this repo's live rule; **that line sits under `## What the file said, kept verbatim`** — a preserved artefact of a deleted document, not a standing rule. What needs writing is narrower than the first draft claimed.
2. **Migrate B into C.** **Reject.** It breaks the inbound references (**61** in `tests:`/`verified_by:`/`tests_verified:`; 98 counting every frontmatter field — the review's own net gave 78, and all three agree the answer is *dozens*, including two release notes), and worse, it destroys the in-flight rule's application: checks carry no subject field and cannot rest, so **6 currently-badged rows become 22 permanently-unowed ones**. It loses the signal rather than tidying it.
3. **TST keeps the gate, CHK holds the walk.** **Coherent as a data model; the first draft's claim that it leaves "both gates intact" is not established.** A derived `passing` means a human `mark: x` transitively writes the status ADR-0010 reserves for a runner's exit code; it arms `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}` on every derived TST, asking for evidence that *is* the walk; and any one of TST-0013's 107 checks re-arming un-passes the roll-up, returning the self-re-arming population to the badge by proxy. Avoiding all three needs a fourth test status, against a vocabulary [[ADR-0008]] spent a measurement collapsing.
4. **Collapse into one type.** **Reject.** Reopening a one-day-old decision over 22 notes against 669 checks and 95 non-B tests, at the cost of five named collisions.
5. **The review's proposal** — *and it now points the wrong way in its first clause.* Migrating the nine capability-naming tests into checks moves them **from the type that has an automation path to the type that has none**, which is a loss for exactly the nine most likely to be automated one day. Its second and third clauses stand.
   - **Migrate the nine capability-naming tests** (`your-trainer` TST-0001..0008, 79 parsed steps; seven have nothing pointing at them in either direction, and TST-0007's single inbound reference from TASK-0302 is the only thing to rehome). They are checks in all but type.
   - **Leave the thirteen as tests**, and write the one sentence that separates them — *a manual `TST-*` names the change it verifies and retires when that change is settled; a `CHK-*` names standing behaviour and re-arms every release.* Derived from the corpus rather than invented, and it makes [[ISS-0178]] the next thing to fix rather than a standing excuse.
   - **Fix the two defects that are not about the type at all.** `## Runs` is write-only. `automation:`/`covered_by:` are empty on 669 of 669 while 203 bodies carry the annotation as text.

6. **Give the check type the automation path, and decide the type question afterwards.** Three changes, each small, each independently useful, and none of them touching the type boundary:
   - **Make `covered_by:` reach the gate.** A check whose `automation: full` and whose `covered_by:` names a `TST-*` that is `passing` is settled by that test rather than by a human tick. The direction is safe: a machine's exit code discharging a human's checkbox, not a human's mark writing a runner's status — so [[project-os-dev#ADR-0010]] is untouched. **Name the consequence honestly:** a failing covering test then un-settles the check, which puts a machine-driven population into the release gate. That is the gate, not a badge, so [[ADR-0027]] is untouched too — but it is a real change and should be decided, not discovered.
   - **Give it a writer and an action.** "Covered by `<TST>`" on the check page, setting `automation:` and `covered_by:` in one write and refused unless the id resolves to a test carrying a `command:` — the same shape as *Needs re-run*, which is already refused without a change id that resolves.
   - **Give `status: retired` a writer**, so TESTING.md's Tier 2 → Tier 3 → remove path is performable rather than described.

   The backfill is a script, not a migration: **203 bodies already name their covering test in prose.**

## What is owed

- [ ] A decision, as an `ADR-*`, amending or companioning [[ADR-0030]].
- [ ] Two spin-off findings the review surfaced and could not file under its read-only constraint, each deserving its own `ISS-*`: **TESTING.md and QUALITY.md disagree on what the independent-review gate keys on** (status versus note-touched; the validator implements TESTING.md's), and **`## Runs` is write-only** so a partly-walked procedure cannot report which steps stand.
- [ ] `automation:` / `covered_by:` unpopulated on 669 of 669 — a data-quality defect independent of the type question, which should not wait on it.

## Independent review

**`changes-requested`** — 2026-08-18, `model:claude-opus-5`, fresh context and a separate session: this pass started from this note, ADR-0030/0027/0028, the template instructions and the corpus, and never saw the authoring session's reasoning. Same model family as the likely author, recorded in `reviewed_by` as provenance; per [[project-os-dev#ADR-0013]] and QUALITY.md the gate is context, not family. Every figure below was re-derived from the twelve `SNAPSHOT.yaml` repos, the live sidecars on `:8765`/`:8766`, and the shipped code — not read back from the tables above.

The direction is sound and the observation that started it is correct and well evidenced: `your-trainer` does file acceptance checklists as tests, and 8 of them are checks in all but type. But three figures are wrong, one row of the governance table is falsified by the corpus, the sharpest claim in the note is refuted by code that shipped, the largest human-walked population in the fleet is missing, and the central thesis is asserted over 22 notes while holding for 8.

### Verified exactly

117 `TST-*` and 669 `CHK-*` (5+43+4+19+13+18+15 and 34+56+579). 54 with `command:`, 62 `kind: automated`, 22 `kind: manual`, 20 of those at `status: ready`. **Every cell of the per-repo table.** `automation: manual` on 669 of 669 and `covered_by: []` on 669 of 669. The `~checks` filter-bar suppression, exactly as described: the backend emits `automation -> [("manual", 34)]` and `buildCheckFilters` in `desktop/src/renderer/renderer.ts` drops any axis with `values.length < 2`, guarded by `tests/test_checks_view.py::test_a_facet_with_one_value_is_not_offered`. The TESTING.md quote and its line numbers. `your-trainer`'s TST-0011 Tier A/Tier B vocabulary colliding with that repo's Tier 1/2/3.

### Wrong, with the correct figure

- **"`your-trainer`'s TST-0011 holds ~40"** — it holds **18**: 18 `- [ ]` rows and 18 `###` sub-checks (B.1–B.4, A.1–A.14). Off by 2.2x.
- **"208 of `your-trainer`'s 579 check bodies say in prose that they are partly or fully automated"** — not reproducible under any definition. **203** carry the migration's parenthesised annotation (181 `(partially automated`, 22 `(automated`, **0** `(fully automated`); **221** bodies contain the word "automated" at all; 225 contain the substring "automat". ADR-0030 recorded **201** rows pre-migration. 208 is none of these.
- **"23 open warnings in this repo"** — the validator emits **22** `[REVIEW]` warnings, and only **2** are on `kind: manual` notes (TST-0011, TST-0026). The rest are 11 automated, 1 hybrid, 8 kind-less.
- **"171 checkboxes"** — right as a count of `- [ ]` rows, wrong as the unit. It misses 9 numbered checkbox items (`your-trainer` TST-0009 writes `1. [ ]`), so the checkbox count is **180**; and the cockpit's own `manual_test_steps()` parses **362 steps** across the same 22 notes, because 15 of the 22 hold **no checkboxes at all** and are prose procedures. The title's "22 notes … holding 171 invisible boxes" describes 7 notes, not 22.
- **[[ISS-0178]] "open"** — it is `status: deferred`.
- **The 11 notes carrying neither `kind:` nor `command:` are placed in row B.** All 11 are `your-health`, all at `status: passing`, all with zero checkboxes, and their bodies name JVM/Robolectric suites and `./gradlew :app:testDebugUnitTest` — TST-0001 opens *"Automated JVM/Robolectric tests (all passing) covering FEAT-0015"*. They are population **A** in substance.

### The central claim: true for 8 of 22, not 22 of 22

"B and C are the same act" is asserted flatly. Measured by outbound links, B is two things:

| | count | evidence |
|---|---|---|
| **standing behaviour, gates nothing** | **8** | `your-trainer` TST-0001..0008 — zero `tasks:`/`issues:`/`features:`/`requirements:` on all eight, and zero inbound `tests:` references on seven of them (TST-0007 carries one, from TASK-0302). `last_verified` 2026-01-27 / 2026-04. Checks wearing a TST id; the thesis holds completely. |
| **verifies a specific change** | **14** | cockpit TST-0011 (13 tasks), TST-0024 (9 tasks, 2 reqs), `your-trainer` TST-0011 (5 tasks, 4 issues), TST-0013 (4 tasks, 13 issues, 9 features), `your-health` TST-0012 (3 issues, 5 reqs). |

`your-trainer` TST-0018 states its own retirement path in prose: *"Once [[TASK-0780]] introduces the entitlement seam, the logic half moves into TST-0016 and what remains here is the environment half, which stays manual permanently."* **A check has no retirement path into an automated test; a change-verifying manual test does.** That is the distinction the note flattened, and it is the reason the boundary reads as principled even where the documents fail to state it.

Against my own counter: 149 of 669 checks name a `TASK-`/`ISS-` in `covers:`, so checks are not purely standing behaviour either. The line is real but softer than a clean split.

### The six governance rows, tested

1. **Badge — implemented, overstated.** The predicate is not `test @ ready`; it is `ready` + manual + **ADR-0028's in-flight rule** (`obligations._is_owed`, `SUBJECT_FIELDS`, `RESTING_STATES`). Live: `your-trainer`'s Tests badge reads **5**, and `GET /api/cockpit/nav?mode=tests` puts the other 10 in a named `Resting · no feature in flight` group. Fleet-wide the manual-TST badge total is **6** (1 + 5), not 20. **This is the note's largest omission**: it lists ADR-0028 in `related:` and never applies it, and the in-flight rule *is* a principled difference — a manual TST rests when its subject reaches terminal, a check never rests, which is exactly why ADR-0027 exempted checks. Defensible as written; the note's premise is a 5-row problem in `your-trainer`, not a 20-row one.
2. **Gate — falsified by the corpus.** `your-trainer`'s `REL-0012` (`status: released`) carries `tests_verified: ["[[ACCEPTANCE_CHECKLIST_v2.1.1]]", "[[TST-0011-AndroidBleHardeningAcceptance]]", "[[TST-0014-EdgeToEdgeInsetAcceptance]]"]`, and TST-0011's own body labels its A tier *"release-gating"*. A manual TST already gates a release. The clean feature-gate-versus-release-gate split the note needs for option 2's collision does not exist.
3. **Re-arming — true in mechanism, minority in population, on both sides.** `invalidated_by:` is set on **54 of 669** checks (8%), all in `your-trainer`. On the test side staleness is evaluated *after* the owed and resting buckets in `_tests_groups`, so it can only fire on a `passing` manual test — **2 of 22**. Presented as categorical; measured, both are the exception.
4. **Independent review — implemented, but not a B-vs-C difference.** `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}`: a `test`-type gate at one status, engaging on 2 of B's 22. Worth filing separately: **TESTING.md and QUALITY.md disagree on what it keys on** — TESTING.md says the gate is *"keyed on that status"*, QUALITY.md says *"any change that creates or updates a `TST-*`"*. The validator implements TESTING.md's. The note adopts one silently.
5. **Terminal status — true, and the strongest row.** [[ISS-0178]] is real, and this repo's TST-0029 is its live instance: `kind: manual`, `status: ready`, subject deleted by FEAT-0107, retired in prose because the vocabulary has no word — and counted among the note's "20 unwalked". Defensible.
6. **Granularity — the sharpest row and the wrongest.** `manual_test_steps()` parses all 362 steps; `steps=` is on **every row of the live Tests nav** (`TST-0013 steps=107`, `TST-0011 steps=18`, and `TST-0001 steps=5` despite holding no checkbox at all); `~tests/<TST>/run` opens a stepper; `POST /api/notes/test-run` → `note_writes.stamp_test_run()` writes a per-step result line under `## Runs`, which is exactly what this repo's TST-0011 `## Runs` section holds. So a surface counts them and a mark writes to them. What survives, precisely: **nothing reads `## Runs` back** — `_RUNS_HEADING_RE` occurs only in the writer — so per-step results are write-only prose and the note's own status is the sole state a run leaves behind. *"Which of TST-0013's 107 steps is currently unproven"* is unanswerable. *"Are they addressable by anything"* is answerable, and the answer is yes.

### What the note misses

- **The fleet's largest human-walked population.** `your-trainer` carries **3 `type: [[test]]` notes with non-`TST-*` ids** — `ACCEPTANCE-CHECKLIST-2.1.1`, `ACCEPTANCE-RUN-2.1.1`, `ACCEPTANCE-TESTS-V2-1-0`, ADR-0030 decision 5's frozen per-release suites. They render as manual rows in the Tests view carrying **42 + 35 + 300 = 377 steps**, more than the whole of B. A note enumerating the fleet in three rows omits the biggest one.
- **2 `kind: hybrid` notes** (cockpit TST-0027, `your-trainer` TST-0010) fit none of A/B/C.
- **The migration cost of option 2 is measurable and unmeasured**: **78 inbound `tests:` / `verified_by:` / `tests_verified:` references** point at the 22 manual TSTs (cockpit 37, `your-trainer` 27, `your-health` 14), including two release notes.
- **`your-sudoku` is the control the table contains and does not read**: 56 checks, 13 automated TSTs, **zero** manual TSTs. B is concentrated 15-of-22 in one repo. That is evidence B is migration residue in two repos, not a structural third type.
- **The validator's REVIEW promotion date, 2026-10-23**, turns those 22 warnings into errors. Only 2 are manual, so the type question does not move that deadline — but it is a dated consequence in the same area.

### The options

**1 — write it down.** Cheapest, reversible, collides with nothing. But its premise is wrong: TESTING.md does not draw an "automated vs manual" split. It draws *formal test tracking vs the release checklist*, and explicitly warns that `level: acceptance` on a `TST-*` is *"a third, different thing"*. The note also quotes `docs/tests/acceptance/README.md` line 63 as this repo's live rule; that line sits under `## What the file said, kept verbatim`, which the README introduces as *"the migrated document's own prose, unchanged"*. It is a preserved artefact of a deleted file, not a standing rule. What genuinely needs writing is narrower than option 1 states.

**2 — migrate B into C.** Breaks 78 inbound references and, worse, destroys the in-flight rule's application: checks carry no subject field and cannot rest, so 6 currently-badged rows become 22 permanently-unowed ones. It loses the signal rather than tidying it, and moves 14 change-verifying tests into a type ADR-0030 deliberately placed outside every gate. **Reject.**

**3 — TST keeps the gate, CHK holds the walk.** The note claims this leaves "both gates intact". It does not, and the collisions are ADR-0030's own. If a TST's status derives from its checks' marks, a human `mark: x` transitively writes `status: passing` — which is the status [[project-os-dev#ADR-0010]] reserves for a runner's exit code (**collision 2**), and which arms `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}` on every derived TST, undoing the check's review exemption one level up and asking for evidence that is by definition the walk already performed (**collision 1**). And any one of TST-0013's 107 checks re-arming un-passes the roll-up, returning the self-re-arming population to the Tests badge through a proxy (**collision 4**). Avoiding all three needs a fourth test status, against a vocabulary ADR-0008 spent a measurement collapsing from 64 values to 53. **Coherent as a data model; "both gates intact" is not established.**

**4 — collapse into one type.** Reopening a one-day-old decision over 22 notes against 669 checks and 95 non-B tests, at the cost of five named collisions plus 78 references. **Reject.**

### Recommended: a fifth, smaller than all four

1. **Migrate the 8** (`your-trainer` TST-0001..0008, **79 parsed steps**; 57 of them in the seven that are unreferenced in both directions). No outbound links, no change named, `ready` since 2026-01-27 / 2026-04. Seven have nothing pointing at them at all, so their migration is free and reversible; TST-0007's single inbound reference from TASK-0302 is the only thing to rehome.
2. **Leave the 14 as tests**, and write the rule that separates them — *a manual `TST-*` names the change it verifies and retires when that change is settled; a `CHK-*` names standing behaviour and re-arms every release*. One sentence, derived from the corpus rather than invented, and it makes [[ISS-0178]] the next thing to fix rather than a standing excuse.
3. **Fix the two defects that are not about the type at all.** `## Runs` is write-only, so a partly-walked 107-step test cannot report which steps stand — that is the true and much narrower content of the "invisible boxes" complaint. And `automation:`/`covered_by:` are empty on 669 of 669 while **203** bodies carry the annotation the migration copied as text. The note's last bullet says the second should not wait on the type question; the first should not either.

### What is owed before this can be adjudicated

- [ ] Correct the five figures above (`~40` → 18; `208` → 203/221; `23` → 22; `171` → 180 boxes / 362 steps; ISS-0178 `open` → `deferred`), and move the 11 `your-health` notes from row B to row A.
- [ ] Add the missing populations: 3 frozen release suites (377 steps), 2 `kind: hybrid`.
- [ ] Restate rows 1, 2, 3, 4 and 6 of the governance table against what is implemented, and drop row 2 or re-derive it — `REL-0012` falsifies it as written.
- [ ] Split B into its 8 and its 14 before any option is chosen; the options are answers to different questions for the two halves.

## Adjudicated

**2026-08-18, Edwin: option 4 with the direction normalised** — one type, ids renumbered into `TST-*`, and the verification link reduced to one encoding. His deciding argument is the one neither this note's first draft nor the review put at the centre: *"it becomes very difficult to move a CHK to an automated test."*

Recorded as [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] and [[ADR-0032-The-Verification-Link-Has-One-Direction]], both `proposed`; built as [[FEAT-0118-The-Test-Type-Absorbs-The-Check]], [[FEAT-0119-The-Merge-Migration]], [[FEAT-0120-The-Automation-Path]] and [[FEAT-0121-The-Verification-Link-Normalises]] under [[PHASE-035-Acceptance-Checks-Are-Notes]].

**The review's objections are not dismissed by that choice — they are answered in ADR-0031's collision table**, and its recommended fifth option is explicitly rejected in one clause: migrating the nine capability-naming tests *into* checks would move them from the type with an automation path to the type without one.

Four findings left this note as their own issues: [[ISS-0196-The-Review-Gate-Is-Described-Two-Ways]], [[ISS-0197-The-Runs-Section-Is-Write-Only]], [[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]] and [[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]]. This note stays `open` until the phase closes.
