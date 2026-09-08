---
type: "[[feature]]"
id: FEAT-0145
aliases: ["FEAT-0145"]
title: "Preparing a release is one workflow: name the version, say which platform, settle the checks it owes — instead of four endpoints, a hand-written note and a rule nobody can see"
status: done
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
reviewed_by: model:claude-opus-5
review_date: 2026-09-08
review_verdict: changes-requested
review_response: "All six findings acted on; the verdict stands as written. (1) FIVE FAILING TESTS, all mine and all now green -- test_remote_peer_refusal's two pinned counts moved 28->32 and 30->34 for the four new loopback-guarded handlers, both with the deliberate-edit line the file asks for; test_acceptance_marks reads the dialog loop as `of offered`, which IS MARK_CHOICES wherever no `only:` is passed; TST-0082 no longer names a renamed test by a truncated prefix; and test_tests_view's `marks <= ledger.MARKS` was stronger than the sentence above it and true only because every check in this corpus had been walked -- TST-0083 is the first unwalked one, `todo` is the absence of an event rather than a mark, and the guard now says so. The reviewer also caught ME: I reported the suite green three times from BACKGROUND runs whose output files were empty, reading the wrapper's exit code as pytest's. The final numbers are from a foreground run: 2233 passed, 6 skipped, plus the node suite. (2) The platform-order guard did not guard -- `open_releases` sorts version-descending, so `the first open release` is the HIGHEST-versioned draft and the fixture settled that one. Swapped, plus an assertion that the fixture still puts the OTHER release first, and the mutant re-run fails as it must. (3) An abandoned release vanished from the publication navigator, which defeats the whole argument for keeping the note; it now gets its own row below the shipped ones, closed by default. (4) FOUR NUMBERS CORRECTED IN SEVEN PLACES: `eleven weeks` -> 23 days (REL-0013 created 2026-08-16), in this repo's validator, the bundled copy, statuses.py AND upstream; `since June` -> 2026-08-16; `67 rows / 17 areas / three of 67` -> the re-measured 52 rows / 15 areas / 9 covering a carried feature, gate 65 blocking; `29 new tests` -> 33. (5) Notes naming what the code lacks: PLAN.md and TASK-0600 said `platform_candidates` where the key is `platforms`; TASK-0601 still listed askForMark as forbidden, which ADR-0041 reversed; and REQ-0061 criterion 1 cited criterion 2's test -- so it now has its own, test_creating_a_release_writes_its_platform_and_scopes_the_gate, which asserts the CONTROL posts the platform, because the defect was in the caller and a write-path test passed throughout. (6) SURFACE-ORPHAN on TST-0083's `area: Publication` is one more row in a pre-existing population: this repo has zero SUR-* notes, so all ~20 areas warn. Not fixed, deliberately -- inventing the corpus's only surface note is a different piece of work. Surviving mutants left standing and stated: `_clean_platform`'s name refusal, `update_release` never stamping `preparing:`, `coverage_gaps`'s requirement dedupe, `settle_rows` dropping the quiet/resting filter, `abandon_release` with a narrower `closed` set. `wrap.prepend` above the gate and a non-release-named surface calling walkOneCheck are pre-existing; ISS-0254 owns the second."
review_response_date: 2026-09-08
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["Edwin, 2026-09-08, after preparing your-trainer's 2.2.0 by hand: 'suggest how the creation of releases can be made a little easier in the tool. I think it should probably be a new workflow: Create Release (Update and delete release should also be possible) — set the version — select: android or iOS — uncheck the required acceptance-tests for the release and add new checks if required (these might be LLM/Human actions?)'"]
goal: "A person who has decided to ship names a version and a platform, sees exactly which acceptance checks that release owes, settles the ones that do not apply, and commissions the ones that are missing — in one place, with every step recorded as an event that says who decided and why."
requirements: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]"]
tasks: ["[[TASK-0597]]", "[[TASK-0598]]", "[[TASK-0599]]", "[[TASK-0600]]", "[[TASK-0601]]", "[[TASK-0602]]", "[[TASK-0603]]", "[[TASK-0604]]"]
release: ""
acceptance_exception: ""
acceptance: ""
tests: ["[[TST-0082-A-Release-Is-Prepared-Through-One-Workflow]]"]
design: ""
related: ["[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ISS-0290-A-Walker-Cannot-Mark-A-Check-Because-Nothing-Names-The-Platform]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [feature, publication, release, workflow]
---

# Preparing a release is one workflow

## What happened, and it is the whole argument

On 2026-09-08 Edwin prepared `your-trainer` v2.2.0. Every step was a hand-edit or a diagnosis:

1. The release page offered no acceptance checks, because a release carries *done-but-unshipped* features and five implemented features had been left at `backlog`. Nothing said so; the list was simply empty.
2. The release note itself was written by hand — version, platform, the five features, four held-back entries with their reasons.
3. The gate then reported **635 checks owed** on a repo with 67, because the page never told the gate which platform the release ships ([[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]).

Three different surfaces, none of which said what was wrong. The tool has the pieces — `release-prepare`, `release-contents`, `release-verified`, `release-mark-released`, the ledger, the owed list — and no workflow that walks a person through them in the order a release actually happens.

## The shape Edwin asked for

> Create Release (Update and delete release should also be possible) — set the version — select: android or iOS — uncheck the required acceptance-tests for the release and add new checks if required (these might be LLM/Human actions?)

Read straight, that is four steps and a lifecycle. Below is what each costs against what exists today.

## Step 1 — Create, update, delete

**Create exists** (`POST /api/notes/release-prepare`) and already refuses the two things worth refusing: a second open release, and a version at or below the newest shipped one.

**Update is partial.** `release-contents` adds and removes features and makes a removal state its reason. Nothing sets the **version** or the **platform** after creation, and the platform is the field [[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]] just proved the gate depends on. Both need a write path with the same refusals as create.

**Delete does not exist at all, and should not be a delete.** `your-trainer`'s REL-0013 is the precedent: v2.1.7 was prepared, never shipped, and is still `draft` with `superseded_by: [[REL-0016-v2.1.8]]`. That is the right record — a release that was prepared and abandoned is a fact about the project, and erasing the file erases why the version number was skipped. So: **Abandon**, which sets a terminal status and requires a reason, and a true delete only for a note created minutes ago with nothing pointing at it.

## Step 2 — The platform is a choice, not a text field

*(Partly landed 2026-09-08 under [[ISS-0290-A-Walker-Cannot-Mark-A-Check-Because-Nothing-Names-The-Platform]]: `create_release` now takes a `platform:`, writes it, and creates the working ledger for it. What remains here is the picker and the ability to change the platform of a release that already exists.)*

`platform:` is free text today, and `_ships_on` already knows five spellings of "all platforms" because the corpus holds four of them. The workflow should offer the platforms **this repo has evidence for** — the ledger platforms plus the platforms its notes actually use — and let the answer be one of them or *every platform*, which is the union rule [[DES-0012-Tests-In-Two-Flows]] D4 already implements.

Naming the platform must immediately change the number on screen. That is [[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]'s fix, and this workflow is the surface that makes the consequence visible: pick `android` and the gate falls from the union to the Android ledger, in front of the person who picked it.

## Step 3 — Settling the checks the release owes

*(The precondition landed 2026-09-08 under [[ISS-0290-A-Walker-Cannot-Mark-A-Check-Because-Nothing-Names-The-Platform]]: a mark that names no platform now resolves one from the open release, so a walk can be recorded at all on a repo with more than one ledger. What remains is the bulk actions and the walk being one screen.)*

This is the step with a real design question in it, and the answer is **not** a checkbox list.

**Today, "required" is derived, not authored.** A check is owed when it covers a feature the release carries and the ledger has not cleared it. [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] chose that deliberately: a release selects its *features*, and the check set follows by subtraction, so nobody can quietly shrink the gate by unticking rows.

**"Unchecking a check for this release" already has a vocabulary** — the ledger's, from [[ADR-0037-A-Verdict-Is-An-Event]]. Three of its seven marks are exactly this, and the distinction between them is the thing a checkbox would destroy:

| mark | means | lifetime |
| --- | --- | --- |
| `na` | cannot apply on this platform, ever | permanent |
| `excused` | not walked this cycle, by decision | **this release only** |
| `blocked` | could not be run — the rig was down | still blocks, deliberately |

So the workflow does not need a new storage shape. It needs to put those three actions on the owed list, in bulk, each with the reason the write path already demands. "Uncheck this for 2.2.0" is `excused` with a reason; "this bike can never do ERG" is `na`; "the trainer is in the loft" is `blocked` and stays on the list, which is the point.

**What is genuinely missing is the walk itself being one screen** — the owed list, grouped by area, with the check's procedure readable beside the buttons, on the release page rather than a separate Tests view that has forgotten which release it is grading.

## Step 4 — "add new checks if required (LLM/Human actions?)"

Yes, and this is where an agent earns its place, because the question *"is anything this release ships not covered by a check?"* is exactly the sweep a person skips. `your-trainer` again: three of PHASE-021's claims — the per-rider preferences, the power source in History, the Pro grant a data-only bike does not earn — had no check, and only a deliberate read of thirty task notes against nine checks found them.

The honest split:

- **The tool computes the gap mechanically**: features the release carries whose `covers:` set is empty, and requirements with unticked criteria. Both are already in the index and neither needs a model.
- **An agent proposes checks for what is left**, drafting `TST-*` notes from the feature and task notes, in the repo's own voice. *(Corrected 2026-09-08 during implementation: this said `at mark: todo`, and a repo that keeps ledgers refuses `mark:` on a note — `LEDGER-FIELD`, [[ADR-0037]]. A drafted check carries no verdict field and is owed by construction, because its ledger holds no entry for it.)*
- **A person accepts, edits or rejects each one.** A check nobody read is a check nobody will walk, and a generated suite that grows on its own is worse than a short one somebody meant.

Every proposal arrives as a note in the working tree, reviewed as a diff. Nothing is written into a release's gate without a person's yes.

## Not in scope

- **Cutting the build.** `release.sh` in the downstream repo owns `versionCode`/`versionName` and the artifact, and it must stay owned there.
- **A second store for "required checks".** The derivation plus the ledger is the store; a per-release list of check ids would be the hand-maintained second copy [[ADR-0032-The-Verification-Link-Has-One-Direction]] exists to prevent.
- **Deleting shipped releases.** A released note is the record.

## Acceptance (sketch, for whoever picks this up)

- Creating a release from the workflow produces the same note a hand-write does, including `platform:`, and the gate on the next screen is scoped to it.
- Changing the platform of an open release changes the owed count without touching any check.
- Abandoning a draft leaves the note, its reason and its `superseded_by:`; the version it held is not silently reusable.
- Marking `excused` from the release page writes a ledger event with a reason and clears only this release.
- The coverage sweep names at least the features carrying no check, on a repo where that is true.

## Planned 2026-09-08 — eight tasks, one decision, one requirement

The sketch above is now [[REQ-0061-A-Release-Is-Written-Through-One-Workflow]], criterion for criterion. The delivery order is `plan/PLAN.md`.

| task | what lands |
| --- | --- |
| [[TASK-0597]] | `publication.platform_candidates` — the platforms this repo has evidence for |
| [[TASK-0598]] | `note_writes.update_release` — version and platform change after creation |
| [[TASK-0599]] | `note_writes.abandon_release`, and `abandoned` joins the release status vocabulary **upstream first** |
| [[TASK-0600]] | the picker, the Platform row and the Abandon control on the page |
| [[TASK-0601]] | `POST /api/notes/release-settle` — `na`/`excused`/`blocked`, refusing `pass`/`partial`/`fail` by name |
| [[TASK-0602]] | the owed list as one screen, grouped by area, procedure text beside the buttons |
| [[TASK-0603]] | `publication.coverage_gaps` — computed, no model |
| [[TASK-0604]] | the `commission-checks` verb, and `REL` in `NOTE_TYPE_BY_PREFIX` so it resolves |

**Step 3 needed a decision before it could be built.** [[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]] forbade every check-changing control on a release page, and it was right about the six marks it was written against. [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] narrows it for three: `na`, `excused` and `blocked` are decisions about scope rather than attestations that a procedure was walked, and `excused` has no meaning away from a release. ADR-0035 is amended, not superseded, and its argument is left as written.

**Homed in [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]], which reopens.** This is the direct successor to [[FEAT-0142]] — a release-page write path replacing a hand-edit — it amends that phase's own opening decision, and PHASE-037 was widened on 2026-08-20 from *what a surface says* to *whether anything recorded it*, which is exactly this work. A new phase was considered and fails both of `CLAUDE.md`'s tests: its goal would be this one feature's goal, and its exit criteria would restate the task list.

**Two things this feature will change that live outside it**, named here so nobody discovers them mid-task:

1. `abandoned` is a **template-owned** status value. It lands in `~/Dev/repos/project-os` and syncs down before any note here carries it ([[TASK-0599]]).
2. `tests/test_release_held_back.py::test_no_write_path_to_a_check_appears_on_the_release_page` asserts a claim [[ADR-0041]] makes too wide by three marks. It is **rewritten, not deleted** ([[TASK-0601]]) — seven passes of independent review defeated looser versions of that test, and a hole punched in it repeats every one of them.

## Independent review — 2026-09-08

`model:claude-opus-5`, `changes-requested`. Fresh context and a separate session, from the notes and the diff alone; the author's session was never read and was not asked anything. Same model family as the author, recorded above as provenance rather than as a compliance token ([[project-os-dev#ADR-0013]]). The working tree moved during the review — `renderer.css`, `note_writes.py`, `publication.py` and `tests/test_release_workflow.py` were all edited between 11:58 and 12:18 — so every finding below was re-run against the tree at 12:18 and holds there.

**The load-bearing refusal holds.** [[ADR-0041]] says *"if `release-settle` ever accepts `pass`, ADR-0035 is gone and nothing will say so"*, and I could not defeat it. `settle_checks` lower-cases the mark and tests it against `SETTLE_MARKS` before anything else runs; `record_verdict` is reached only past that gate; the renderer's only settle dialog is filtered by `only: ['na','excused','blocked']` and posts to `/api/notes/release-settle` alone. Admitting `pass` to `SETTLE_MARKS`, or deleting the whitelist branch, or adding `'pass'` to the renderer's `only:` list, or deleting the `only:` key, or planting a new release-named surface that calls `walkOneCheck` — each of the five was caught. The `test_the_settle_endpoint_refuses_every_attestation` derivation over `ledger.MARKS` rather than a literal is the right shape. Nine further mutants against the write paths were killed too: `abandoned` dropped from `_CLOSED_RELEASE`, `abandon_release` keeping `preparing:` or not demanding a reason, each of the three delete refusals, the duplicate-version refusal, `stale_stem`, `acceptance_exception` in the coverage sweep, and `covers_release`.

### 1. Five tests in this repo's suite fail on this tree, and all five are this change (reproduced)

`.venv/bin/python -m pytest tests/ -q` → `6 failed, 2224 passed` (one, `test_runtime_freshness`, is time-flaky and passes on re-run). The other five pass at `HEAD` in a clean worktree and fail here:

- `tests/test_remote_peer_refusal.py::test_every_guarded_endpoint_refuses_a_remote_peer` — `AssertionError: the dispatch split moved: 32 guarded / 5 open … assert (32, 5) == (28, 5)`. Four endpoints were added and the deliberate count was not. **This is the guard behind [[TST-0076]]**, *every mutation endpoint refuses a non-loopback peer* — the one test in the repo whose subject is exactly the property the four new handlers claim.
- `tests/test_remote_peer_refusal.py::test_no_guard_call_has_its_answer_discarded` — `expected 30 guard call sites, found 34`.
- `tests/test_acceptance_marks.py::test_every_choice_shows_its_mark_in_the_dialog` — `ValueError: substring not found`. It reads `renderer.ts` for `for (const choice of MARK_CHOICES)`, which this change rewrote to `for (const choice of offered)`.
- `tests/test_coverage_registers.py::test_every_test_named_in_a_note_exists[TST-0082-A-Release-Is-Prepared]` — `TST-0082 … names 1 test(s) that do not exist: ['test_no_write_path_']`. [[TST-0082]]'s own prose writes the old name elided as `test_no_write_path_…`, and the register reads the token.
- `tests/test_tests_view.py::test_a_reconciled_row_reads_settled_on_the_tests_view` — `assert marks <= ledger.MARKS` fails on `{'todo'}`. [[TST-0083]] is a new acceptance check with no ledger entry, so it emits `todo`, which is not a mark. Adding any unwalked acceptance check to this repo trips this; the guard and the new note disagree and one of them has to move.

`test_every_new_write_path_is_routed_and_loopback_guarded` in the new file asserts the loopback property over the four new handlers and passes — but it is a second, narrower implementation of what `test_remote_peer_refusal.py` already asserts over all of them, and the canonical one is red. A new local guard passing while the repo-wide one fails is the shape this repo's own close-out rule exists to catch.

### 2. `test_a_settle_uses_ITS_releases_platform_not_the_first_open_one` does not guard what it names (reproduced)

The change note describes a second defect found by re-reading the code — a settle consulting `verdict_platform` before the release's own `platform:` — and names this test as the guard. It is not one. Restoring the defect (`resolved = _clean_platform(platform) or verdict_platform(docs_root, index)` in `note_writes.settle_checks`) leaves the test green:

```
.venv/bin/python -m pytest tests/test_release_workflow.py::test_a_settle_uses_ITS_releases_platform_not_the_first_open_one -q
1 passed in 0.10s
```

`publication.open_releases` sorts `reverse=True` on the version key, so *the first open release* is the **highest-versioned** draft. The fixture makes the settled release `REL-0002` at `2.0.0` — the higher one — so `verdict_platform` returns `ios` under the bug as well. Swapping the two, so the settled release is the lower version (`REL-0001` at `1.1.0`, platform `ios`, beside a draft `REL-0002` at `2.0.0`, platform `android`), makes the mutant fail with `platform == 'android'` and the event landing in the wrong ledger — the exact sentence the docstring claims. The note's own diagnosis — *"a single-draft fixture passes either way, which is why it was wrong"* — applies unchanged to the two-draft fixture that replaced it.

The fix itself is correct. Only its guard is not.

### 3. An abandoned release is not listed anywhere in the Publication navigator (reproduced)

`cockpit.nav_payload(index, mode="publication")` builds three kinds of row: the next release from `open_releases` (`status == "draft"`), the shipped ones (`status == "released"`), and `stale_drafts` (`status == "draft"`). `abandoned` matches none. On a fixture with one draft release:

```
before: [('release-next', 'Preparing · 1.1.0')]
after : [('release-next', 'Next release')]
```

The note is on disk and the version stays taken, so [[REQ-0061]] criterion 3 is literally met. But this feature's whole argument for abandoning over deleting is that *the note is the only record of why a version number was skipped*, and after the write the surface whose subject is releases stops naming it. `REL-0013` is the worked example: abandon it and it leaves the publication pane. That is a smaller version of the defect `stale_drafts` was added to fix — *"named rather than dropped"*.

### 4. Numbers in the notes and in the code comments that do not reproduce

- **"eleven weeks"** — `src/project_os_cockpit/statuses.py:79`, `src/project_os_cockpit/validate_docs_bundled.py:155`, `tools/scripts/validate-docs.py:155` and the upstream `~/Dev/repos/project-os/tools/scripts/validate-docs.py:152` all say `your-trainer`'s REL-0013 sat at `draft` for eleven weeks. Its note has `created: 2026-08-16` and `preparing: "2026-08-16"`; today is 2026-09-08. That is **23 days**, a little over three weeks. The upstream copy is uncommitted, so it is still cheap to correct in both places.
- **"since June"** — `desktop/src/renderer/renderer.ts:9204`, `buildReleaseIdentity`'s docstring, on the same note. It has been in that state since **16 August**.
- **"67 rows … 17 areas … three of 67"** — `publication.settle_rows`' docstring, `buildSettleSection`'s docstring, [[ADR-0041]] and the change note. Reading `your-trainer`'s live payload today: `settle` holds **52 rows across 15 areas**, **9** of them covering a feature the release carries, against a gate of 65 blocking / 10 quiet / 3 resting. The *shape* claim survives — the two largest areas are 16 and 14, which is 30 of 52 — but the three figures a reader would check do not. Either re-measure, or say what the basis was (the release now carries `platform: android`, so a pre-ISS-0288 measurement would legitimately differ, and saying so is what the repo already does for its `your-trainer` working-tree figures elsewhere).
- **"29 new tests in tests/test_release_workflow.py"** — `SNAPSHOT.yaml` focus note. `grep -c '^def test_' tests/test_release_workflow.py` → **31**.

`"seven passes of independent review"` does check out: `git log -- tests/test_release_held_back.py` carries fourth-, fifth-, sixth- and seventh-pass commits, the last reading *"seventh pass APPROVED"*.

### 5. Notes that name things the code does not have

These are handoff-surface defects: I could not have built the code from these sentences, and a later reader will grep for the wrong string.

- `plan/PLAN.md` step 1 and [[TASK-0600]] (Definition of Done, first box, and the first Steps box) say the payload gains a **`platform_candidates`** key. It is called **`platforms`** — `publication.release_payload` emits `"platforms": platform_candidates(index)` and `ReleasePayload.platforms` is what the renderer reads. Three ticked boxes name a field that does not exist.
- [[TASK-0601]]'s *"The guard this task must rewrite"* still says the forbidden set *"becomes attestation routes: `askForMark`, `walkOneCheck`, …"*. The delivered test **admits** `askForMark` and checks it on its `only:` argument, which is what [[ADR-0041]]'s consequences section decided and what the change note describes. The task's boxes are ticked against the superseded plan.
- [[REQ-0061]] criterion 1 cites `test_changing_the_platform_moves_the_gate_and_touches_no_check` as its evidence. That is criterion 2's test. Criterion 1's actual guard is `test_setting_the_platform_writes_it_and_creates_its_ledger`.

### 6. New validator warning this change introduces

`bash tools/scripts/validate-docs.sh` exits OK, but now emits `WARN [SURFACE-ORPHAN] 1 check(s) name area: 'Publication' and no surface carries that title … (e.g. TST-0083)`. [[TST-0083]]'s `area:` has no `SUR-*` behind it, so its coverage reads as zero.

### 7. Surviving mutants (each planted, run, and reverted; `__pycache__` cleared between runs)

Against `tests/test_release_workflow.py`, `test_release_held_back.py`, `test_release_page.py`, `test_release_contents.py`, `test_release_lifecycle.py`, `test_release.py`, `test_release_preparing.py`, `test_ledger.py` — 171 tests, green at baseline.

| mutation | effect | survived |
| --- | --- | --- |
| `resolved = _clean_platform(platform) or verdict_platform(...)` | finding 2 — the settle lands in another release's ledger | yes |
| `settle_rows`: drop the `key in resting_keys` filter | quiet and resting checks get settle buttons, which the docstring says they must not | yes |
| `_clean_platform`: `if False:` in place of the name check | `Android 14` and `../evil` reach `ledger.working_path`; the refusal works, nothing asserts it | yes |
| `update_release`: never stamp `preparing:` | naming a version stops declaring intent to ship; the docstring says it must | yes |
| `coverage_gaps`: remove the requirement dedupe | one requirement over three features is listed three times | yes |
| `abandon_release`: `closed=frozenset({"released"})` | a `reverted` release can be abandoned | yes |
| a new **non-release-named** surface calling `walkOneCheck` | a check write reachable from the release page | yes — pre-existing, [[ISS-0254]] owns it |
| `wrap.prepend(...)` above the gate in `buildReleasePage` | a section renders above the gate | yes — the rewritten `test_the_gate_is_built_before_what_is_in_the_release` matches `wrap\.append\w*\(` only |

The last two are not regressions: the old guards had the same holes. The rewrite of the append-order test is a genuine improvement — it now covers the whole region above the gate rather than one window, and `wrap.appendChild(buildCoverageSection(d))` above the gate is caught. Naming `prepend`/`insertBefore` in the same regex would close it for a word.

### What I could not fault

The refusal architecture (finding block above). `_refuse_bad_version` shared by `create_release` and `update_release`, with the open-release refusal deliberately excluded and the reason written down. `delete_refusal` as one function the write path raises from and the payload reports, so the button and the write agree — including the terminal-status check restated in it precisely because the payload draws from it. `closed` being wider than `shipped` in `release_payload`, so the settle list and the coverage sweep both go empty on an abandoned release. The `abandoned` status landing upstream first and being mirrored into `tools/`, the bundled validator, `statuses.py`, `templates.py`, `cockpit.py`, `cockpit.js`, `renderer.ts` and `completed-work.ts` — I checked the upstream and downstream hunks are the same text, and `test_status_vocabulary.py` passes. `desktop` builds clean (`tsc`).
