---
type: "[[phase]]"
id: PHASE-038
aliases: ["PHASE-038"]
title: "A verdict is an event — the ledger holds what was actually verified, on which platform, for which release"
status: active
order: 38
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
reviewed_by: model:claude-opus-5
review_date: 2026-08-19
review_verdict: changes-requested
goal: "An acceptance verdict stops being a scalar field on a check note and becomes a dated, attributed, single-platform event in a per-release ledger — so a repo can say what was verified, by what method, on which platform, for which release, and every downstream question becomes a query instead of a maintained document."
features:
  - "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
  - "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
  - "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
  - "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
  - "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
requirements:
  - "[[REQ-0052-A-Verdict-Names-Its-Platform-Method-Author-And-Date]]"
  - "[[REQ-0053-The-Note-Holds-Nothing-Verdict-Shaped]]"
  - "[[REQ-0054-Absence-Is-The-Initial-State]]"
  - "[[REQ-0055-No-Surface-Writes-A-Verdict-Onto-A-Note]]"
  - "[[REQ-0056-One-Outcome-Vocabulary-And-The-Document-Matches-The-Data]]"
issues:
  - "[[ISS-0216-The-Suite-Parser-Splits-On-Physical-Lines]]"
  - "[[ISS-0217-The-Two-Repos-Holding-Every-Check-Describe-A-Retired-Type]]"
  - "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[PHASE-036-One-Human-Walk]]", "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[ISS-0215-One-Hundred-And-Forty-Rows-Outside-The-Suite]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
tags: [phase]
---

# A verdict is an event

## Goal

**An acceptance verdict is a fact about (check × platform × release).** It is stored as a scalar. This phase moves it into a per-release, single-platform ledger of dated events, leaves the note holding only intent, and turns the walk list, the release gate and the cross-platform burndown into queries over ledgers.

[[ADR-0037-A-Verdict-Is-An-Event]] carries the decision and the measurements. **Accepted 2026-08-19 by Edwin** — the gate [[ADR-0030]], [[ADR-0031]] and [[ADR-0034]] all used held for its day, and the phase was documented in full, amended twice and audited once while it read `proposed`. Two questions left open in the ADR were answered in the same instruction: `evidence` moves to the ledger as a sibling collection ([[TASK-0544]]), and `tests_verified:` becomes derived ([[TASK-0546]]). **This phase is now clear to start.**

## Why this is a phase

[[CLAUDE]]'s rule: a goal statable without listing its parts, and exit criteria that are not *"the tasks are done"*. Both hold. The goal is one sentence about where a verdict lives; the exit criteria are about what a query returns and what a gate reports, neither of which is a task list.

**And it is not a small request.** Six features, a new file format, a migration of 671 notes across three repos, and a read/write path spanning 87 TypeScript sites and six Python modules. This is the shape a phase exists for.

## Scope

- The ledger file: JSON schema, the working ledger, sealing at release cut, and immutability afterwards.
- The check note sheds `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by`, `evidence`.
- The four queries — walk list, release gate, cross-platform burndown, *was release R walked*.
- The cockpit's read path, write path and API surface.
- One outcome vocabulary, defined in one document that matches the data.
- The migration script for repos carrying scalar marks, and the splitter fix ([[ISS-0216]]) **before** any repo migrates again.
- ~~Stage 2: the `@Covers` inversion and the CI emitter.~~ **Descoped on close** — [[FEAT-0138]] and its tasks moved to [[PHASE-999]]. Struck rather than deleted: this phase's scope did include it, and a scope line that quietly disappears is a phase that looks like it always meant to stop here.

## Out of scope

- **Retiring `PARITY_MATRIX`.** [[ADR-0037]]'s limit section: the matrix's first failure mode is a surface with no row, which is [[FEAT-0130]]'s `SUR-*` work, not the ledger's. The retirement is `your-trainer`'s decision after [[FEAT-0130]] lands.
- **The tier rule.** [[ISS-0208]] owns it and is orthogonal — where a verdict is stored says nothing about which checks gate. The six unwalked Tier 3 checks still need Edwin's reading.
- **Getting the gate into the fleet repos.** [[ISS-0209]] is a validator migration per repo and is a precondition for the *benefit* landing anywhere but here — stated in *Sequencing* below rather than absorbed.
- **Migrating the 156 stranded checklist rows.** [[ISS-0215]]. They need a surface and a `covers:` per row first.
- **Behaviours with no check at all.** [[FEAT-0130]] and [[FEAT-0132]]. The ledger makes coverage legible, not complete.

## Exit criteria

**All nine hold as of 2026-08-19.** Three did not when this was first marked, and each is annotated with what moved — the record of a criterion being *amended* rather than quietly met is the point of writing them down first.

- [x] **A verdict cannot be written without a platform, a method, an author and a date.** `ledger.check_entry` refuses at write time; `LEDGER-ENTRY` refuses at commit time.
- [x] **No acceptance note in any migrated repo carries the seven fields** — and no cockpit surface reads one. `LEDGER-FIELD` refuses them; the guard is behavioural (`test_a_note_cannot_change_a_verdict_in_a_repo_that_keeps_ledgers`), because a surviving frontmatter read returns something that looks exactly like a verdict.
- [x] **The release gate is a query over ledgers**, and the delta was measured for all three repos before any migrated: **0 on the earning platform** in every one.
- [x] **A check with no entry for a platform reports as owed there**, with no field declaring applicability.
- [x] **A sealed ledger cannot be modified**, `entries` and `evidence` both. [[ADR-0037]] decision 9a: the release note records the ledger's **git blob hash**, so the check is against the bytes — an edit is caught committed, uncommitted, rebased or restored from a backup. A sealed ledger no release vouches for is its own error, because an unvouched seal is exactly the state the old check could not tell from a good one. [[ISS-0220]] closed.
- [x] **A release's verified list is computed where there is a ledger to compute it from**, and the page names the platform it read. *Amended 2026-08-19:* this said `tests_verified:` must be **gone from the schema**, which contradicted [[TASK-0546]]'s decision to keep it as the fallback for pre-ledger releases. The criterion moved, not the decision — deleting the field would destroy the only verification record [[REL-0001]] has, and a criterion that trades a real record for a tidy schema is the wrong one. The field is the fallback; it is never the source where a ledger exists.
- [x] **A check can be excused from one release without being excused from the next.** *Unable to test*, *not tested this cycle* and *could not run it right now* are three recordable answers with three different effects on the gate, and the middle one expires when its ledger seals. **Reachable in the product since [[TASK-0547]]**: the release page seals the platform's ledger, so the expiry fires where a person can see it rather than only in a test.
- [x] **One outcome vocabulary in one document, and it is the one the data uses** — `TAXONOMY.md` here and upstream, verified by a check that reads the table's values *and both behaviour columns* against `ledger.MARKS`.
- [x] **The splitter is fixed and proved on a hard-wrapped bullet** before any repo migrated, and mutation-proven against three plausible wrong fixes.

## Sequencing

Three stages, from [[ADR-0037]]. Each is independently useful.

**Stage 1 — the honesty gain.** [[FEAT-0133]], [[FEAT-0134]], [[FEAT-0135]], [[FEAT-0136]], [[FEAT-0137]]. Ledger format, one release backfilled, manual entries only; the notes shed the fields; the read and write paths move. This is where the *(check × platform × release)* fact starts being stored at its own arity.

**Stage 2 — observed coverage.** [[FEAT-0138]], **re-homed to [[PHASE-999]] on close.** Stage 2 is a body of work rather than a leftover, and holding a finished phase open for it would make the phase's status say something false about what is done. Its seed is safe: [[TASK-0541]] extracted **278 checks naming 81 JVM classes** — half again what [[ADR-0037]] estimated — before [[TASK-0530]] removed the field they lived in.

**Stage 3 — rendered views replace hand-maintained tables.** Not scoped here; conditional on [[FEAT-0130]] and belonging to `your-trainer`.

**One ordering constraint that is not a stage.** [[ADR-0030]] decision 6 holds: `SCHEMAS.md`, `TAXONOMY.md`, `TESTING.md`, `STATUSES.md`, the test template and `validate-docs.py` land in `~/Dev/repos/project-os` and sync down **before** any note changes downstream. And [[ISS-0209]] means the gate currently runs in no repo that holds a check — so until it is resolved, everything this phase builds is enforced here and nowhere the data lives. That is not a reason to wait; it is a reason not to claim the fleet is gated when it is not.

## Notes

- **This is the fourth schema change to the same corpus in four weeks.** [[ADR-0037]] says so in its own status section and so does this. The argument for going again is that the previous three all moved the same scalar between shapes without asking whether a scalar could hold the fact.
- **The measurements are fresh**, taken 2026-08-19 against all three repos, and they corrected the source proposal in four places: the stranded-row count (156 across four notes, not ~156 across four — the fourth is `TST-0014`, and [[ISS-0215]] undercounts at 140/three), the doc-drift location ([[ISS-0217]] — the drift is in the fleet repos, not here), the vocabulary count (four live vocabularies, not three), and the cost (87 TypeScript sites the proposal does not mention).

## Independent review, first pass — 2026-08-19, `changes-requested` (Stage 1 up to `f036c81`)

Reviewed by `model:claude-opus-5` from the notes and `git diff 46cdaaa..HEAD` alone, in a session that did not author any of this work and never saw its reasoning ([[project-os-dev#ADR-0013]]: fresh context is the gate, model family is not). Same model family as the author, recorded in `reviewed_by` as provenance. `.venv/bin/pytest -q` → 1735 passed, 3 skipped; `bash tools/scripts/validate-docs.sh` → OK. Both green, which is why the findings below are about what the green does not cover.

Findings are ranked; each was reproduced rather than reasoned about. Items the task list already records as not started ([[TASK-0530]], [[TASK-0531]], [[TASK-0535]]/[[TASK-0536]] partials, [[TASK-0538]], [[TASK-0545]], [[TASK-0546]], the upstream `TAXONOMY.md` copy, concurrent appends, and the unmigrated fleet repos) are excluded.

### 1. The measured delta is taken against a smaller corpus than the gate it protects

`tools/scripts/backfill-ledger.py` calls `acceptance.load(docs)` **with no index**. Every production gate calls `acceptance.load(docs_root, index)`, and the indexed branch collects every `[[test]]` at `level: acceptance` **anywhere** under `docs/`, where the un-indexed branch reads `docs/tests/acceptance/` only. In `your-trainer` that is **581 checks / 62 blocking** against the script's **579 / 60**. The headline *"60 → 60 (+0)"* is a statement about a population the release gate does not use.

Reproduced on a two-note fixture: one `mark: done`, `tier: 1`, `level: acceptance` note outside `docs/tests/acceptance/` gets no ledger entry, and `apply_ledger` then overwrites its `done` with `todo`. The script prints `GATE DELTA 0 blocking -> 0 blocking (+0)` while the cockpit's own gate goes **0 → 1 blocking** and a recorded pass is destroyed. In `your-trainer` today the two invisible notes are `TST-0015`/`TST-0018` and both happen to be `mark: todo`, so nothing is lost — by luck, not design, and they are exactly the pair [[ISS-0219]] is about. The discrepancy is already visible inside [[TASK-0529]] and unremarked: its DoD says *"`your-trainer` (581)"* and its result table says *"checks 579"*.

This is the phase's exit criterion 3 and [[REQ-0054]] criterion 7. The number that gates the migration does not measure the gate.

### 2. A non-persisting mark in a sealed ledger destroys the persisting verdict underneath it

[[ADR-0037]] decision 7: `pass` *"persists into the next cycle's view **until an invalidation event supersedes**"* it. An `excused` is not an invalidation, yet `ledger.resolve` pops the check outright when the ledger holding the `excused` seals. Reproduced: `pass` in a sealed `REL-0001`, `excused` in a sealed `REL-0002` → `verdicts()` is `{}`. Same for a sealed `fail`/`blocked`/`question` sitting on a pass.

The gate consequence is benign (owed either way). The **burndown** consequence is not: `ledger.burndown` selects A-`pass` rows, so excusing a check on Android for one release silently removes a genuine iOS parity gap from the report built to replace `PARITY_MATRIX`'s rotting rows. No test stacks a non-persisting mark on a persisting one — `test_an_excused_check_expires_when_its_ledger_seals` excuses a check with nothing under it. Whichever semantics is intended, the ADR text and the code currently disagree and nothing records the choice.

### 3. Three of the four `close_row()` call sites are unguarded

Mutation-tested: deleting `close_row()` from the fence branch, from the tier-heading branch, or from the section-heading branch each leaves `tests/test_row_wrapping.py` 11/11 green (and the wider acceptance tests green for the section case). `test_a_fence_closes_the_row` and `test_a_heading_closes_the_row` pass because the row is closed later by a different mechanism, so neither guards the behaviour it is named for. A distinguishing input exists and is untested: an indented line *after* a closing fence is dropped today and would be folded into the row if the fence call were removed.

### 4. The continuation rule folds structure it was written to exclude

`_CONTINUATION_RE` excludes only `-`/`*`/`+`. Measured: `  1. Open the app.` folds into the row (`"Do the thing. 1. Open the app. 2. Tap the button."`), and so do an indented table (`"| col | col | | --- | --- |"`), an indented `## heading` and an indented `> quote`. The docstring's own justification — *"a nested `- plain` is a sub-point … folding it into the parent's prose would invent a sentence nobody wrote"* — applies verbatim to an ordered sub-item. `_LAZY_WRAP_RE` already treats `#` and `>` as structure; `_CONTINUATION_RE` does not.

Not reachable in any committed suite: old and new `parse()` produce identical output over all 137 committed revisions of the suite file across the three repos. But [[TASK-0531]]'s migration has not run and this is the parser it will run through, which is the ordering [[PLAN]] calls non-negotiable.

### 5. A ledger whose filename does not match `_LEDGER_NAME_RE` still disappears from its own platform

`REL-12-ios.json` (two-digit release), `working-ios.json`, `ios.json`: `_platform_of` returns `""`, `load(docs, "ios")` skips the file, and `platforms(docs)` still reports `ios` from the field it loaded. Reproduced: `platforms() == ['ios']`, `verdicts(docs, 'ios') == {}`. With `apply_ledger` every check then falls to `todo` while a sealed ledger of passes sits in the directory. `validate_ledgers` never checks that a filename yields a platform, or that `platform` is present at all — so the validator is silent. This is the failure the `_platform_of` fix was celebrated for finding, reachable through a different door.

### 6. `validate_ledgers` has no test, and its immutability rule is weaker than the exit criterion

142 new lines and six new codes, in two byte-identical copies (`tools/scripts/validate-docs.py`, `src/project_os_cockpit/validate_docs_bundled.py`); `grep -rn "LEDGER-" tests/` returns nothing. [[TASK-0528]]'s evidence is a manual one-off. `LEDGER-SEALED` compares the working tree to `git show HEAD:<path>`, so editing a sealed ledger **and committing it** passes forever afterwards. Exit criterion 5 (*"a sealed ledger cannot be modified, proved by a test that tries — `entries` and `evidence` both"*) and [[REQ-0052]] criterion 4 are met by no test; `ledger.append`'s sealed guard is `# pragma: no cover`.

### 7. The drift check leaves the persistence column free

Mutation-tested: changing `TAXONOMY.md`'s `na` row from `yes, until invalidated` to `**no — expires with its release**` — the exact inversion [[ADR-0037]] calls *"the sharpest single argument in this ADR"* — leaves `tests/test_ledger.py` 38/38 green. The check compares the value set and the **gate** column only. [[REQ-0056]] criterion 3 is also worded *"reads the documented vocabulary **and the corpus**"*; the implemented check reads the document and `ledger.MARKS`, never the corpus.

### 8. "This repo has a ledger" is decided by a directory existing

`apply_ledger` returns its input only when `not found and not ledgers_dir.is_dir()`. An **empty** `docs/releases/ledgers/` — which `ledger.write()` creates via `mkdir(parents=True)` before writing, and which survives deleting the JSON — turns every verdict in the repo to `todo`. Reproduced. Fail-closed, but the docstring's stated mechanism (*"`verdicts()` returns `{}` and this returns its input"*) is not what the code does, and no surface prints a reason.

### 9. `mark_check` can still write a scalar into a note in a repo that has a ledger

The server routes on the presence of `platform` in the payload; nothing checks whether the repo has a ledger, and `mark_check` never receives `docs_root`. [[PLAN]] says *"Nothing is dual-written — a repo has a ledger or it does not"* — this repo has `WORKING-macos.json` **and** 34 notes carrying `mark:`, both live, and which one a reader sees depends on whether the caller passed `platform`. `walkOneCheck` in `renderer.ts` sends `id`/`number`/`name`/`verdict`/`reason`/`change` and no platform, so after [[TASK-0530]] strips the fields the first walk puts a scalar straight back. That is [[REQ-0055]]'s stated failure mode, and it is reachable without the 87-site renderer migration going wrong.

### 10. Smaller

- **Resolution is file order, not date order.** `pass @2026-08-19` then `fail @2020-01-01` resolves to `fail`; `_DATE_RE` also accepts `2026-13-45`. Safe through HTTP only because `record_verdict` does not expose `when`.
- **`record_verdict` defaults `by` to the literal `user:edwin`**, so [[REQ-0052]]'s *"names its author"* can be satisfied by a hardcoded stranger. `seal()` interpolates an unvalidated `release` into a filename while `platform` gets `_PLATFORM_RE`.
- **Seven `done` tasks carry 0 of N DoD boxes ticked** ([[TASK-0529]], [[TASK-0533]], [[TASK-0534]], [[TASK-0535]], [[TASK-0536]], [[TASK-0539]], [[TASK-0541]]) against 7/7, 4/4 and 4/4 on three others. Nothing checks it; `QUALITY.md`'s ticking discipline is written for requirements only.
- **[[TASK-0534]] is `done` with an unimplemented, unmentioned criterion**: *"a release with no platform reads every platform's ledger and is blocked by any of them"*. The actual behaviour is the opposite and permissive — `platform=""` reads no ledger and falls back to the note's `mark:`. Its title also claims the release gate reads a ledger; `publication.py:857` and `cockpit.py:2644` pass no platform, and no production caller anywhere does. `ledger.seal`, `ledger.burndown`, `ledger.owed` and `orphan_evidence` have no production caller at all.
- **[[ADR-0037]]'s measurement table** lists `automation:` as *"non-empty **203** of 671"*. Measured: non-empty on **669** of 671; 203 is the non-`manual` count in `your-trainer` (22 `full` + 181 `partial` against 376 `manual`). [[REQ-0053]] words it correctly; the table does not, in a table whose neighbouring rows are read literally.
- **`your-sudoku`'s "56 → 56 (+0)" is vacuous** — the script writes **0** entries there. The lossless claim rests on `your-trainer` (513) and this repo (34).
- `Ledger.to_json` computes `last=not self.evidence and False`, which is always `False`.

### What was checked and could not be refuted

`671` notes; `platform:` on 2; `verdict_date`/`verdict_reason`/`invalidated_by`/`covered_by`/`evidence` empty on all 671; **87** `renderer.ts` sites (lines matching `\bmark\b`, exact); `505` iOS against `60` Android, reproduced by re-running the script. `Item.number`'s fallback is genuinely guarded — reverting it fails `test_gate_delta::test_the_delta_against_your_trainers_real_tags` — and no positional consumer breaks (`_delta_key` is `(tier, name)`, `ages()` keys are computed within one run, `renderer.py` and `migrate-acceptance-checks.py` see only file-shape items). Adding `excused` to `PERSISTS` fails two tests; the `_platform_of` prefix anchoring is guarded; each `apply_ledger` property fails when inverted. Old and new `parse()` are output-identical over every committed revision of every suite file in all three repos: no row dropped, none duplicated.

## Independent review, second pass — 2026-08-19, `changes-requested` (the close: `f036c81..a9e51ad`)

Reviewed by `model:claude-opus-5` from the notes and the diff after `f036c81` alone — a separate session that authored none of this work, never saw the author's reasoning, and holds no memory of writing it ([[project-os-dev#ADR-0013]]: fresh context is the gate; model family is not, and is recorded in `reviewed_by` as provenance). **What is independent: the context and the session. What is not: the model family, which is the same as the author's.**

Run here: `.venv/bin/pytest -q` → **1 failed**, 1777 passed, 3 skipped. `bash tools/scripts/validate-docs.sh` → OK. `bash tools/scripts/validate-docs.sh --as-committed` → OK. Every finding below was reproduced, not reasoned about; each guard named was mutation-tested.

### 1. `strip-verdict-fields.py`'s safety property is inoperative — it compares the ledger against itself

*"No verdict may be removed that the ledger does not already carry"* is the script's stated whole reason for existing, and it **cannot fire**. The check reads `item.mark` off `A.load(docs, Index.build(docs))`, and `acceptance.load` now calls `apply_ledger` unconditionally ([[TASK-0538]], `df2b399`) — which replaces `item.mark` with the ledger's answer, or `"todo"` where there is no entry. `has_ledger()` at the top guarantees the repo has a ledger, so `mark not in EMPTY_MARKS` is never true and `would_lose` is always empty.

Reproduced: three notes at `mark: done`, a ledger containing **zero** entries, `--apply` →

```
  acceptance notes   3
  notes to strip     3
  ledger entries     0 — every non-empty mark is carried
strip: rewrote 3 note(s)
```

All three verdicts deleted, exit code 0, and the line printed asserts the property that was not checked. Deleting `if would_lose:` outright leaves the suite green: the script has **no test at all** (`grep -rn "strip" tests/` is empty).

The proof recorded in [[TASK-0531]] (*"a note whose id the ledger cannot know is refused by name"*) was true when taken, at `a101288`, where `load()` still read `if platform: items = apply_ledger(...)`. An adjacent change three commits later removed the guard's input and nothing re-ran the proof. **This repo's own migration was safe** — 34 marks, 34 entries, verified at `a979af9` — by the state of the code at the time, not by the check. [[PLAN]] names the fleet migration as the next step, and `your-trainer` holds 581 notes and 513 passes.

### 2. Exit criterion 5 is false — four reproduced bypasses of `LEDGER-SEALED`

Each run against `tools/scripts/validate-docs.py` on a fixture with a sealed, correctly-vouched ledger; all four report **no error**:

| edit | result |
| --- | --- |
| **delete the `sealed` key** and rewrite every entry | clean — the check is gated on `data["sealed"]`, a field inside the file it protects, so the protected file decides whether it is protected. The ledger also becomes `is_working`, so its marks stop expiring |
| **delete the ledger file** | clean — `_sealed_shas` is built from the notes and never walked; nothing checks that a vouched file exists. *Was release R walked?* becomes unanswerable, silently |
| **move it out of `docs/releases/ledgers/`** | clean, same reason |
| **rewrite LF → CRLF** | clean — `Path.read_text()` performs universal-newline translation, so the computed hash is not a hash of the bytes |

`entries` and `evidence` are covered *only* against edits that change the hash and leave `sealed` in place. [[REQ-0052]] criterion 4 (*"Sealed ledgers immutable, proved"*) and [[ISS-0220]]'s *"Done when"* item 1 are ticked against a property that does not hold. Renaming to another release id **is** caught (unvouched), which is the one direction that works.

### 3. The suite is red at `HEAD`, and the closing commit reports it green

`tests/test_coverage_registers.py::test_the_snapshot_phase_matches_the_note` fails: `SNAPSHOT.yaml` says `PHASE-038` for `FEAT-0138`, `TASK-0542`, `TASK-0543` and `REQ-0057` while their notes say `PHASE-999-Future`. `a9e51ad`'s message ends *"1777 passed"*. **Neither CI nor the pre-commit hook runs pytest** — `.github/workflows/validate-docs.yml` and `.git/hooks/pre-commit` run the validator, `sync-snapshot --check` and `generate-adapters --check` — so a manual run is the only place this surfaces, and the commit message is what a reader would otherwise rely on. That test was written after a previous instance of exactly this drift.

### 4. The re-homing is recorded in three places and missing from four

The *decision* is legitimate: Stage 2 was a named separate stage in [[ADR-0037]] and in this note's Sequencing from the day it opened, and the operating instruction was Stage 1 only. The *execution* is not, and `CLAUDE.md` documents the procedure verbatim (*"`sync-snapshot.py` propagates status but **not** `phase`"*).

- Done: the four notes' `phase:`, this note's `features:`/`requirements:`, `PHASES.md`'s PHASE-038 row.
- Not done: the four items' `phase:` in `SNAPSHOT.yaml`; `phases.PHASE-038.features`/`.requirements` in `SNAPSHOT.yaml`, which still list `FEAT-0138` and `REQ-0057`; `PHASES.md`'s **PHASE-999** row, which still lists only `FEAT-0029, TASK-0045, TASK-0065`; and `focus`, which still reads `phase: PHASE-038` / *"PHASE-038 STARTED"* on a phase that is `done`.
- This note's own **Scope** section still lists *"Stage 2: the `@Covers` inversion and the CI emitter"* as in scope, contradicting the Sequencing paragraph two screens below it.

### 5. [[ISS-0217]]'s fix propagated the defect [[ISS-0217]] is about

The synced `TAXONOMY.md` **adds** to both fleet repos a section that asserts the type [[ADR-0031]] retired is current:

> `## `check` versus `level: acceptance` on a test` — *"Both exist and they are not the same thing… A `[[check]]` is one line of a **manual walk** with a persistent human verdict. `TESTING.md` has always said the two coexist; the type boundary is what stops the release gate, the runner-status rule and the independent-review gate from being applied to the wrong population."*

Verified: absent from `your-trainer` and `your-sudoku` at `HEAD`, present on disk after the sync; present in this repo (`TAXONOMY.md:122`) and upstream (`project-os/tools/instructions/TAXONOMY.md:96`). It is a live assertion in the present tense, not the tombstone the issue's closing note describes. The [[ISS-0218]] drift check reads the mark table against `ledger.MARKS` and cannot see it. [[ISS-0217]] is `fixed` on the claim *"the instruction drift is closed in both"*; [[REQ-0056]] criterion 2 (*"legacy readable, not presented as current"*) is ticked against the same paragraph.

The rest of the sync claim holds: the other apparent deletions are replacements (`requirements:`/`features:` → `covers:`, [[ADR-0032]]) or a duplicated `## scope` heading, and the tier definitions [[DES-0012]] cites are intact.

### 6. `blob_sha` is correct and nothing holds it there

[[TASK-0548]], [[ISS-0220]] and `a9e51ad` all state that it *"matches `git hash-object` exactly, asserted against the real command"*. **No test in the repo invokes `git hash-object`.** The only assertion is `blob_sha(x) == out["sha"]`, where `out["sha"]` is `blob_sha(x)` — a tautology. Replacing `blob_sha` with a plain `sha1(text)` — not a git blob hash at all — leaves `test_ledger.py`, `test_ledger_validator.py`, `test_release.py` and `test_acceptance_marks.py` 112/112 green.

The value *is* right: verified independently against `git hash-object` on non-ASCII (`2b03fb7…`), on an empty file (`e69de29…`) and on a single byte (`2e65efe…`), all three exact. What is missing is the guard, and the formula now exists in three hand-written copies (`ledger.py`, `validate-docs.py`, the test's own `_blob()`) with nothing tying any of them to git.

### 7. Medium

- **`_set_block_list` corrupts frontmatter on two hand-authored YAML shapes.** A blank line inside an existing `ledgers:` block leaves an orphan `    sha: "…"` at top level; unindented list items (`ledgers:` / `- file: …`, valid YAML) are left behind entirely while a second `ledgers:` block is appended. Both produce an unparseable note. Not reachable through `seal_ledger` alone, and these notes are hand-editable by design. `_yaml_safe` also does not escape backslashes, so a value containing `\b` becomes a YAML escape.
- **The validator and the reader disagree about what a ledger is.** `_parse` raises when a ledger's `platform` field and its filename disagree; `validate_ledgers` never compares them. Reproduced: a `REL-0001-macos.json` copied to `REL-0001-ios.json` and vouched for by the note leaves the validator **clean** while `ledger.load()` raises for the whole repo — validator green, acceptance surface down. The new *"refused, not skipped"* rule in `load()` makes any stray `*.json` in that directory a hard failure of every read path, where it used to be skipped.
- **`seal_ledger` is two non-atomic writes.** Decision 9a's whole argument is that seal and vouch land in one commit; the implementation renames the ledger, then writes the note, with no rollback. A failure between them produces a sealed, unvouched ledger — the error state the same commit invented.
- **`POST /api/notes/seal-ledger` is undocumented** in `COCKPIT-API.md`, which gained two other endpoint sections in this diff, while [[REQ-0055]] criterion 5 (*"API reference matches"*) is ticked. `by` also became required on `mark-check` and the reference does not say so.

### 8. Judgments the brief asked for

**Criterion 6's amendment is a legitimate correction, and it overshoots its own argument.** The original criterion (*"`tests_verified:` is gone from the schema"*) contradicted [[ADR-0037]] *as accepted* — the ADR's own Consequences already said *"**[[REL-0001]] is not rewritten**"* — so it was wrong on the day it was written, which is not the [[ISS-0208]] pattern. But the two halves it reconciles were never actually in tension: removing `tests_verified: []` from `docs/__templates__/release.md` (where it still sits) was never the same act as deleting [[REL-0001]]'s thirteen entries. The amendment argues against a proposal nobody made, and the ADR still says *"The field leaves the release template and schema"* and was **not** amended — so the phase and the decision it derives from now contradict each other, with the phase closed on the phase's version.

**Criterion 8 was reworded and ticked without being listed as an amendment.** It read *"verified by a check that reads both, so `TAXONOMY.md` cannot drift from the corpus again"*; it now reads *"against `ledger.MARKS`"* — a constant in code, not the corpus. This note says *"each is annotated with what moved"* of the three; this is a fourth that moved, unannotated. [[REQ-0056]] criterion 3 has the same gap.

**Criterion 7's tick is honest as a code claim and untested as a product claim.** The Seal action exists, is loopback-guarded, and `seal_ledger` has three tests. It is offered only on a release that is not `released` and only with a platform selected — and [[REL-0001]] is the only release note in this repo and is `released`, so the button appears on nothing here. *"Reachable in the product"* is a reading of the code, not an observation of it.

**Criterion 3's summary overstates a row its own task note states honestly.** *"0 on the earning platform in every one"* — `your-sudoku` has **0 entries** and 56 `todo`, so it has no earning platform; [[TASK-0529]]'s table says so plainly and the summary flattens it.

### 9. Low

- [[PLAN]]'s *"Stage 1 — complete"* and *"Two things the review left standing"* both still present [[ISS-0220]] as open and `LEDGER-SEALED` as diffing against `HEAD`. Closed in the next commit; the plan of record was not updated.
- [[ISS-0217]] states `check.md` was *"deleted from both"*; it was already absent at `HEAD` in both, removed in `c00bd21a`. The ticked checklist item (*"confirm no `check.md` remains"*) is true; the fix line is not.
- [[TASK-0529]] carries `66` and `68` for the same count, and `505` and `507` for the same count, in paragraphs added by the correction notice.
- `ledger._is_date` and `resolve`'s date sort are unguarded — both mutations survive the full ledger/release/acceptance/migration suite. The validator's copy of `_is_date` **is** guarded (`2026-13-45`).
- `_sealed_shas` reads `ledgers:` from any note type while the error says *"no release note vouches"*; `_ledger_at` parses each blob twice (the `json.loads` result is unused); `subprocess` is now an unused import in `validate_ledgers`.

### What was checked and could not be refuted

`blob_sha` against real `git hash-object` on non-ASCII, empty and single-byte input — exact in all three. The 34 migrated notes: **zero** of the seven fields across all 34 (35 files, one is `README.md`). The coverage seed: 278 checks / 81 classes, independently recounted at 268/82 with a cruder regex over `your-trainer`'s 580 acceptance notes — same population, no contradiction. The fleet sync lost nothing local: the tier definitions are intact and the apparent deletions are [[ADR-0032]] replacements or a duplicated heading. Finding 2 of the first pass is **properly guarded** — reverting `resolve` to pop the standing verdict on a sealed non-persisting mark fails two tests, including the burndown one. `mark_check`'s ledger refusal, `has_ledger`'s file check, `seal`'s `_RELEASE_RE`, `record_verdict`'s author refusal, `LEDGER-NAME`, `LEDGER-FIELD`, both `LEDGER-SEALED` branches, the widened `_CONTINUATION_RE` and the union path in `apply_ledger` each fail at least one test when reverted. `validate-docs.sh --as-committed` passes the full CI step set. The `Index` parses `ledgers:` as a list of maps, so sealing a second platform does not drop the first platform's row.

**Findings are recorded here rather than as `ISS-*` notes**: finding 1 alone returns this phase to `active`, and allocating IDs from a review session concurrent with the author's is the failure mode that produced the truncated `id: TASK` notes in `8549ecc`. Filing is owed at the next close-out.
