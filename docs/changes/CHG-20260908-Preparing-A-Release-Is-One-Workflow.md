---
type: "[[change]]"
id: CHG-20260908-Preparing-A-Release-Is-One-Workflow
aliases: ["CHG-20260908-Preparing-A-Release-Is-One-Workflow"]
title: "A release page now names its version and platform, abandons a draft that will not ship, settles the checks it owes without leaving the page, and says what it ships that nothing verifies"
status: merged
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
source: ["Edwin, 2026-09-08: 'suggest how the creation of releases can be made a little easier in the tool. I think it should probably be a new workflow: Create Release (Update and delete release should also be possible) — set the version — select: android or iOS — uncheck the required acceptance-tests for the release and add new checks if required (these might be LLM/Human actions?)'", "Edwin, 2026-09-08: 'Implement FEAT-0145 fully (make sure to up-stream + down-stream if required)'"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/publication.py", "src/project_os_cockpit/note_writes.py", "src/project_os_cockpit/server.py", "src/project_os_cockpit/agent_actions.py", "src/project_os_cockpit/statuses.py", "src/project_os_cockpit/templates.py", "src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/validate_docs_bundled.py", "src/project_os_cockpit/static/base.css", "src/project_os_cockpit/static/cockpit.css", "src/project_os_cockpit/static/cockpit.js", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "desktop/src/renderer/completed-work.ts", "tools/instructions/STATUSES.md", "tools/scripts/validate-docs.py", ".cursor/rules/statuses.mdc", "docs/reference/cockpit-capability-register.md", "tests/test_release_workflow.py", "tests/test_release_held_back.py", "tests/test_release_page.py"]
issues: []
features: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
requirements: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ISS-0290-A-Walker-Cannot-Mark-A-Check-Because-Nothing-Names-The-Platform]]", "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"]
---

# Preparing a release is one workflow

## Summary

The release page can now do the four things Edwin did by hand when he prepared `your-trainer` v2.2.0 on 2026-09-08: name the version and the platform of a release that already exists, abandon a draft that will not ship, settle the acceptance checks it owes without leaving the page, and read a list of what it ships that nothing verifies.

Before this, `release-prepare` created a release and `release-contents` added and removed features — and nothing else about a release could be written by the tool. Setting the version or the platform meant editing frontmatter in an editor, and the platform is the field the gate is graded on: with it unset, the gate read **635 checks owed on a repo with 67** ([[ISS-0288]]).

Four new endpoints, three new page sections, one new status, and one decision that narrows an earlier one.

## What a person sees

**Version and platform.** The release page carries a section with the version, a platform picker and Save. The picker offers the platforms the repo has evidence for — the ones with a ledger, and the ones its notes tag work with — plus an explicit *every platform*, which is what a release that has not said takes ([[DES-0012]] D4). Choosing a platform creates its working ledger, so the release can accept a verdict the moment it exists. The gate on screen re-grades against the chosen platform without a reload.

**Abandon.** A draft that will not ship gets a terminal status and a reason, and the note stays. `your-trainer`'s REL-0013 is the precedent: v2.1.7 was prepared, never shipped, and its note is the only record of why that version number was skipped. The version it held stays taken — creating a release with the same number is refused, and the refusal names the abandoned note. A true delete is offered only when the note was created today, nothing links to it, and no ledger is sealed against it; when any of those fails, the page says which.

**Settle what this release owes.** The checks that hold the release, grouped by area, each carrying its own procedure text, with three buttons: **N/A**, **Excuse** and **Blocked**. Tick several and settle them together under one reason. Each writes one ledger event with a reason, an author and a date. Rows covering a feature this release actually carries are marked, because on `your-trainer` (2026-09-08, REL-0017 open on Android) **9 of 52** are — the rest block the release without being about it.

**Coverage.** Features this release carries that no acceptance check names in `covers:`, and requirements with unticked criteria. Both computed from the record. A `Commission checks` button dispatches an agent to draft the missing `TST-*` notes into the working tree, for review as a diff — nothing enters the gate without a person's yes.

## The decision this rests on

[[ADR-0035]] removed every check-changing control from the release page in August, and it was right. [[ADR-0041]] narrows it rather than reversing it: **a release page may settle a check; it may never pass one.**

- `pass`, `partial` and `fail` are *attestations* — somebody walked a procedure. They stay on `~checks` and on the check's own note, and `POST /api/notes/release-settle` refuses all three **by name**.
- `na`, `excused` and `blocked` are *decisions about scope*. Nobody walked anything. `excused` is scoped to one release by construction — it lives in that release's working ledger and `seal` expires it — so the release is the only place the question has an answer at all.
- `question` is refused with its own reason: it is a judgment about the check's wording, made by somebody reading the wording.

ADR-0035's second objection — that a mark was offered at a distance from the procedure where nobody could be walking it — is paid rather than argued away: every settle row renders the check's own text, and the dialog renders the whole note.

## New and changed

**New endpoints**, all loopback-only like every other write path:

- `POST /api/notes/release-update` — `{release, version?, platform?}`. Refuses `create_release`'s refusals, because it calls them: the version shape, a version at or below the newest released one, a version another release already carries, and a platform name that could not be a ledger filename. Sending `platform: ""` means *every platform*, which is a choice; omitting the key leaves the field alone.
- `POST /api/notes/release-abandon` — `{release, reason, superseded_by?}`. Refuses without a reason. Sets `status: abandoned`, clears `preparing:`, appends a dated decision-record callout.
- `POST /api/notes/release-delete` — `{release}`. Three refusals, each routing the caller to abandon by name.
- `POST /api/notes/release-settle` — `{release, checks: [...], mark, reason}`. One `ledger.append` per check, platform resolved from the release. Atomic **per check, not per request**: settling twelve where the eighth is unknown records seven and reports the eighth, because a ledger is append-only and reporting the batch as a failure would be the only dishonest option.

**`GET /api/cockpit/release`** gains `platforms`, `platform`, `settle`, `coverage` and `delete_refusal`.

**New functions:** `publication.platform_candidates`, `publication.coverage_gaps`, `publication.settle_rows`; `note_writes.update_release`, `abandon_release`, `delete_release`, `delete_refusal`, `settle_checks`, `SETTLE_MARKS`.

**New status: `abandoned` on `[[release]]`.** This is the upstream half. `tools/instructions/STATUSES.md` and `tools/scripts/validate-docs.py` are template-owned, so the value was added in `~/Dev/repos/project-os/` first and mirrored here, along with `src/project_os_cockpit/validate_docs_bundled.py` — which `sync-project-os.sh` does **not** cover, because that script copies `tools/`. `.cursor/rules/statuses.mdc` is generated from `STATUSES.md` by `tools/scripts/generate-adapters.py` and carries the same two lines; the pre-commit hook refuses a commit whose adapters are stale, which is how that copy stayed honest. Downstream, `abandoned` joins the archived band in `statuses.py` and the terminal-status lists in `cockpit.py`, `templates.py`, `static/cockpit.js`, `renderer.ts` and `completed-work.ts`; `test_status_vocabulary.py` found each of those and is the reason none was missed.

**Agent verbs for a release.** `agent_actions.DEFAULT_ACTIONS` had no `release` key and `NOTE_TYPE_BY_PREFIX` had no `REL`, so a release verb could not have resolved even once it existed. Both are added, with `commission-checks`, `verify` and `close-out`.

## What did not change

- **No second store for "required checks".** The derivation plus the ledger is the store ([[ADR-0040]], [[ADR-0032]]).
- **No note is written by a settle.** [[REQ-0055]] is unchanged and guarded: a settle is an event.
- **The release filename is not renamed when the version changes.** `REL-0013-v2.1.7.md` is resolved by stem across the corpus, so renaming it would break every `[[REL-0013-v2.1.7]]` to buy a tidier path. The write reports that the two have parted rather than fixing one of them.
- **Cutting the build.** `release.sh` in the downstream repo still owns `versionCode`/`versionName` and the artifact.

## The guard that had to be rewritten

`tests/test_release_held_back.py::test_no_write_path_to_a_check_appears_on_the_release_page` asserted that no route to a check write appears in any release-page function, over a discovered set of surfaces, after seven passes of independent review had each defeated a looser version of it. It is now `test_no_attestation_path_to_a_check_appears_on_the_release_page`, and the narrowing is **structural rather than a hole punched in a list**:

- `walkOneCheck`, `/api/notes/mark-check`, `/api/notes/retire-check`, `gateMark(`, `markGateRow(`, `checkMark(`, `markCheckRow(`, `retireCheckRow(` and `paintCheckList(` stay forbidden. `mark-check` stays forbidden even though it could in principle be sent `excused`: it is the path that offers all seven marks.
- `askForMark` is admitted and **checked on its argument** — its `only:` list must be a non-empty subset of `{na, excused, blocked}` — the same treatment `buildCheckRow`'s `controls` argument already gets. A subset check catches `pass` however it is spelled; a ban with a carve-out would not.
- The endpoints a release surface posts to are asserted as a set.
- A second test pins the server half over `ledger.MARKS`, so a mark added to the vocabulary tomorrow is either declared a settle mark or refused — never quietly admitted because nobody updated a literal.

`tests/test_release_page.py::test_the_gate_is_built_before_what_is_in_the_release` also changed: it searched for *any* append above the gate, which made its claim "nothing at all" and was right until the page grew a second header control. It now names the allowed set. Edwin's argument is errands before inventory; naming a version and a platform is neither, so it belongs above the gate and the feature list still does not.

## What a live walk caught that the tests did not

The four endpoints were exercised against a real sidecar on a scratch repo before this landed, and that walk found a defect thirty tests had missed: **an abandoned release could be deleted outright.**

`_open_release` refused only `released`, and the delete's other guard is *created today* — so a release abandoned in the morning could be deleted in the afternoon, destroying precisely the record abandoning exists to keep. Every test asked about a `draft`, so none of them looked.

Fixed by naming all three terminal statuses in one table, each with its own sentence, because they are terminal for different reasons: *shipped* rewrites what it was measured against, *reverted* is the record of what was rolled back, *abandoned* is the record of why the number was skipped. `update_release`, `delete_release` and `settle_checks` all refuse them; `abandon_release` accepts an abandoned one so it can say *already abandoned*, which is a different fact. The release payload stopped offering the settle list and the coverage sweep on any of the three — a screen of buttons whose every press would be refused is worse than no screen.

Guarded by `test_an_abandoned_release_cannot_be_deleted_changed_or_settled`.

A second defect came out of re-reading the code the walk had exercised: **a settle consulted `verdict_platform` before the release's own `platform:`.** That resolver answers *which platform is being walked* by reading the first open release, which is right for somebody on `~checks` standing on no release in particular and wrong for a settle, which names one. With two drafts open, settling a check on the second would have written the event into the first one's ledger. The release's own platform now comes first, and `verdict_platform`'s remaining answer — the sole ledger, when there is exactly one — applies only when the release has said nothing. Guarded by `test_a_settle_uses_ITS_releases_platform_not_the_first_open_one`; a single-draft fixture passes either way, which is why it was wrong.

## What the independent review caught

A clean-context pass returned **`changes-requested`**, and its findings are the reason this note's numbers are what they are. The verdict stands as written; the response is recorded beside it on [[FEAT-0145]] and [[REQ-0061]] rather than replacing it ([[project-os-dev#ADR-0011]]).

The two that mattered most:

- **Five tests were failing and had been reported as passing.** Four were pinned counts and citations this work legitimately moved — the loopback-guard census (28 → 32 endpoints, 30 → 34 call sites), the mark-dialog loop, and a renamed test cited in a note. The fifth is more interesting: `test_tests_view`'s `marks <= ledger.MARKS` was a stronger claim than the sentence above it, and it was true only because **every acceptance check in this corpus had been walked**. `TST-0083` is the first unwalked one; `todo` is the absence of an event, not a mark, and the guard now says so.
- **The guard written for the platform-ordering fix did not guard it.** `publication.open_releases` sorts by version descending, so *the first open release* — the one `verdict_platform` reaches for — is the highest-versioned draft, and the fixture settled that one. The test passed on its own mutant. Swapped, with an assertion that the fixture still puts the other release first, and the mutant now fails.

Also from the review: an abandoned release **vanished from the publication navigator**, which defeats the whole argument for keeping the note — it now gets its own row; four numbers that did not reproduce, corrected in seven places across both repositories; and five notes naming fields the code does not have.

**A correction about how this was verified.** Three "suite green" reports during the work came from background runs whose output files were empty — the wrapper's exit code, read as pytest's. The numbers above are from a foreground run: **2233 passed, 6 skipped**, plus the desktop node suite.

## Impact

- Anyone preparing a release in the cockpit: four things that required an editor are controls, and the gate re-grades against the platform as soon as it is named.
- Any repo carrying a `[[release]]` note: `abandoned` is now a legal status, so a prepared-and-dropped release can stop being counted as open. **Nothing is migrated** — `your-trainer`'s REL-0013 is still `draft` and stays that way until somebody decides.
- Downstream fleet repos get the validator change through the ordinary template sync; none is performed by this commit.

## Documentation Coverage (All Types Considered)

- features: updated
- requirements: new
- tasks: new
- issues: not-applicable
- tests: new
- workflows: not-applicable
- decisions: new
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups

- [ ] Run `tools/scripts/release-to-project-os.sh` and the template sync so the fleet's vendored cockpit and validator carry this. Deliberately not done here: it writes into eleven other repositories, which is a separate decision ([[ISS-0277]] — nothing checks that chain).
- [ ] `buildReleasePage`, `holdFeatureBack` and `fillUnreleasedCard` still raise `askForText` modals for reasons predating this work. [[TASK-0600]]'s *nothing pops a dialog* is met for the controls added here and owed by those three.
- [ ] `TST-0083` is written and unwalked. The acceptance check for this feature is a walk a person performs; nothing here claims it has been.
- [ ] Nothing decides whether a rename-with-link-rewrite is worth building for a release whose version changed. Parked in `docs/features/release-workflow/plan/PLAN.md`.
