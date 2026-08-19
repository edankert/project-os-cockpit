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
  - "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
requirements:
  - "[[REQ-0052-A-Verdict-Names-Its-Platform-Method-Author-And-Date]]"
  - "[[REQ-0053-The-Note-Holds-Nothing-Verdict-Shaped]]"
  - "[[REQ-0054-Absence-Is-The-Initial-State]]"
  - "[[REQ-0055-No-Surface-Writes-A-Verdict-Onto-A-Note]]"
  - "[[REQ-0056-One-Outcome-Vocabulary-And-The-Document-Matches-The-Data]]"
  - "[[REQ-0057-Coverage-Is-Observed-From-A-Run]]"
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
- Stage 2: the `@Covers` inversion and the CI emitter.

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

**Stage 2 — observed coverage.** [[FEAT-0138]]. The `@Covers` inversion and the CI emitter. Seed the mapping from `covered_by:` **before** deleting the field — measured, it holds nothing, so the real seed is `your-trainer`'s 203 prose annotations naming 54 JVM classes.

**Stage 3 — rendered views replace hand-maintained tables.** Not scoped here; conditional on [[FEAT-0130]] and belonging to `your-trainer`.

**One ordering constraint that is not a stage.** [[ADR-0030]] decision 6 holds: `SCHEMAS.md`, `TAXONOMY.md`, `TESTING.md`, `STATUSES.md`, the test template and `validate-docs.py` land in `~/Dev/repos/project-os` and sync down **before** any note changes downstream. And [[ISS-0209]] means the gate currently runs in no repo that holds a check — so until it is resolved, everything this phase builds is enforced here and nowhere the data lives. That is not a reason to wait; it is a reason not to claim the fleet is gated when it is not.

## Notes

- **This is the fourth schema change to the same corpus in four weeks.** [[ADR-0037]] says so in its own status section and so does this. The argument for going again is that the previous three all moved the same scalar between shapes without asking whether a scalar could hold the fact.
- **The measurements are fresh**, taken 2026-08-19 against all three repos, and they corrected the source proposal in four places: the stranded-row count (156 across four notes, not ~156 across four — the fourth is `TST-0014`, and [[ISS-0215]] undercounts at 140/three), the doc-drift location ([[ISS-0217]] — the drift is in the fleet repos, not here), the vocabulary count (four live vocabularies, not three), and the cost (87 TypeScript sites the proposal does not mention).

## Independent review — 2026-08-19, `changes-requested`

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
