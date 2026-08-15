---
type: "[[feature]]"
id: FEAT-0100
aliases: ["FEAT-0100"]
title: "Unpushed work needs a person — publication joins the obligation registry, and the push moves next to the commits it publishes"
status: done
owner: user:edwin
created: 2026-08-13
updated: "2026-08-15"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-15
review_verdict: changes-requested
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13: 'let's add the git status to the needs you section instead and have the actual push solution in the overview history. Can we then have an indication of having to push using a number on the overview icon?'", "Edwin 2026-08-13: 'widen the registry's definition'"]
goal: "A person learns that work is unpublished the same way they learn everything else that needs them — a number on the view button, a row in Needs you — and publishes it from the surface that already draws the commits."
requirements: []
tasks: ["[[TASK-0415-Git-State-For-Every-Workspace]]", "[[TASK-0416-Generalise-The-Note-Less-Obligation]]", "[[TASK-0417-Publication-Enters-The-Registry]]", "[[TASK-0418-The-Push-Lives-With-The-Commits]]", "[[TASK-0419-Every-Card-Is-A-Full-Card]]", "[[TASK-0420-A-Dismissal-Means-Until-Something-Changes]]", "[[TASK-0421-An-Unknown-Count-Is-Unknown-On-Every-Surface]]", "[[TASK-0422-One-Walk-For-Publication]]"]
design: "[[DES-0011-Publication-Is-An-Obligation]]"
release: ""
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0025]]", "[[ADR-0022]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0098]]", "[[FEAT-0055]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]"]
tests: []
---

# Unpushed work needs a person

## Goal

**A person learns that work is unpublished the same way they learn everything else that needs them.** A number on the Overview button, a row in `Needs you`, and the push where the commits already are.

## Why this is a feature and not a fix

[[ISS-0156]] is the fix: the count is missing for the workspace you have open. Restoring it would repair three surfaces that were already the wrong shape — a band that exists only on the overview, a group you have to navigate to, and a tooltip line. None of them is where a person looks to find out what needs them.

The tool already answers that question, continuously, through the registry and its badges. Publication was outside it only because the registry counted judgments about the record. [[ADR-0027]] widened that on 2026-08-13; this is the widening's first subject, and the one that motivated it.

## Scope

- **The data, for every workspace, always** ([[TASK-0415]]) — closing [[ISS-0156]]. Nothing else here is truthful until this lands, because absent-at-zero makes an unknown count invisible.
- **The note-less obligation path, generalised** ([[TASK-0416]]) — standing documents and unpushed work through one walk that yields a count and its rows together, replacing two bolt-on special cases whose seam has already produced a badge that disagreed with its own group.
- **Publication registered as an obligation** ([[TASK-0417]]) — owned by the overview, with a noun and a verb, so the badge, the `Needs you` group and the landing page all read from one place.
- **The push, with the commits** ([[TASK-0418]]) — the overview history tile and `~history` mark which commits are unpublished and carry the action, plus the design artifact [[DES-0011]] needs before it can leave draft.
- **The card is whole whether or not you have opened the project** ([[TASK-0419]]) — the cold pass carries each repo's digest numbers, so an unopened project stops getting a headline with no second line.
- **A dismissal means *until something changes*** ([[TASK-0420]]) — the ✕ keys on a fingerprint of everything the card shows, and survives a restart.

*(Both added to Scope on 2026-08-14. They arrived mid-feature and were listed in `tasks:` without ever entering Scope or Acceptance — the independent review's finding 7 — which is how the only false claim in the set reached `done` unexamined. Recording them late is worse than having recorded them early and better than closing a second time without them.)*

## Out of scope

- **A push control on the rail square** — [[DES-0004]]'s channel budget, and a publishing action on a 44px target.
- **A push button beside the project name** — considered and dropped on 2026-08-13; recorded in [[DES-0011]] because it is the obvious idea and will be re-proposed.
- **Retiring the Agents-screen group** — it answers *which of my twelve repos*, which no per-project surface can.
- **Pushing anything automatically.** Unchanged and not negotiable here: [[FEAT-0055]]'s rule is that a person clicks it, and the deploy-remote refusal keeps its single home.

## Acceptance

- With unpushed commits on a backup remote, the Overview button carries the count, hovering names it (`3 · commits to push`, not "items"), the rail's attention card carries it, and the overview's registry counts it *(amended 2026-08-14: this read "the overview's `Needs you` group lists it", which was never true — `overview` is not a nav mode, so that payload falls back to `features` and nothing fetches the landing. TASK-0418 re-homed the row to the attention panel and the criterion was not updated, which QUALITY.md forbids.)*, and history offers the push beside the commits it would publish.
- The same three surfaces agree **by construction**, reading one walk — asserted, not observed.
- With no remote at all, the surfaces say *nothing here is backed up* rather than reporting a count of zero.
- With a deploy remote, the state is visible and the push is refused as a decision, not as a broken control.
- With nothing to publish, **every one of these surfaces is silent** — no zero badge, no empty group.
- The count is correct for a workspace with a live sidecar, which is the case that is wrong today.
- **Every attention card carries the same lines**, opened project or not — the cold pass supplies the digest where no sidecar is running, and a live sidecar still wins. *(Added 2026-08-14 with [[TASK-0419]]; see the note in Scope.)*
- **A dismissal lasts until something on that card changes, or you open the project — including across a restart.** *(Added 2026-08-14 with [[TASK-0420]]. This is the criterion whose absence let a false `done` through: nothing here judged the task, and the behaviour was the opposite of its promise.)*

## Independent review — 2026-08-14, `changes-requested`

Clean-context pass required by `QUALITY.md` and owed since close-out ([[PHASE-030]] line 119 records the debt). Reviewer started from this note, its six tasks and the diff `512e7e5..7127980`; it did not read the authoring session's reasoning and is not that session. Same model family as the author (`model:claude-opus-5`), which [[project-os-dev#ADR-0013]] does not gate on.

Five findings block, five are documentation. What was verified is listed after them, because three of the four tasks hold up under mutation and the verdict is about the other two.

### Blocking

1. **A dismissal does not survive a restart — TASK-0420's central promise, and it is false in shipped code.** `pruneDismissedAlerts` (`desktop/src/renderer/renderer.ts:11968`) drops every key whose workspace is not in `workspaces`. The module-level `refreshAttention()` at `renderer.ts:12431` runs at load; `workspaces` is `[]` at `renderer.ts:333` and is assigned only inside async functions (`690`, `3135`). So the first thing the renderer does after restoring the store is walk it with an empty workspace list and delete all of it, writing `{}` back to `localStorage`. Reproduced by extracting the compiled `pruneDismissedAlerts` from `desktop/dist/renderer/renderer.js` and running it against the module's own initial state: in-memory `{}`, persisted `{}`. The task's DoD asked for this **asserted rather than assumed**; the box is unticked and there is no test.
2. **Acceptance criterion 1 is false as written, and was never reconciled.** There is no overview `Needs you` group: `overview` is not in `NAV_MODES`, so `nav_payload(index, "overview")` falls back to `features` (`src/project_os_cockpit/cockpit.py:2980`), and the renderer's `VIEW_LANDING_RELS` covers `~features`, `~issues`, `~tests` only (`renderer.ts:5222`). `landing_payload(index, "overview")` does return the group with its rows — nothing fetches it. [[TASK-0417]] recorded exactly this and left the box unticked; [[TASK-0418]] re-homed the row to the rail attention panel. The criterion here still claims the original surface on a feature at `done`. `QUALITY.md`: *"Do not tick an acceptance criterion that the delivered system does not satisfy… amend/narrow/supersede it with recorded rationale."*
3. **"Asserted, not observed" does not hold for publication.** Mutating `_publication_rows` (`src/project_os_cockpit/obligations.py:340`) to return `[]` unconditionally leaves the whole Python suite green — 1258 passed, and the only two failures were `test_runtime_freshness`, an artefact of touching the file's mtime. No test exercises the publication source non-vacuously: `owed_corpus` (`tests/conftest.py:31`) is a `tmp_path` copy with no `.git`, so its publication rows are always empty, and the agreement assertions that do bite are carried entirely by the standing-document kind (a `+2` mutation in `counts_by_kind` fails six tests, all of them standing). `repo_index` reaches publication only because this repo happens to have unpushed commits today — the live-corpus vacuity trap `conftest.py`'s own docstring warns about.
4. **The third surface does not read the one walk.** The badge and History both come from `git_state.read()` (`obligations.py:_publication_rows`, `cockpit.py:5549`). The attention card — the surface that actually carries the row Edwin asked for — reads `fleetHealth`'s `ahead`, produced by `probeGitState` in `desktop/src/ipc/git.ts:56`, a second implementation in another language on its own 60s clock. That duplication is deliberate and defended for the **push**; the **count** on the card is a second derivation, so "the same three surfaces agree by construction, reading one walk" is not true of the set that shipped.
5. **An unknown count still renders as nothing owed** — the failure [[ADR-0027]] admission test 4 and [[TASK-0415]]'s opening paragraph name as the gate. Constructed a repo with a forge remote on a branch with no upstream: `git_state.read` correctly returns `kind='backup', ahead=None, commits=()`, honouring its own docstring (`git_state.py:14`, *"must never render as such"*). Then the badge is absent, `history_payload` reports `remote_kind: 'backup', unpublished_count: 0` so no publication block is emitted at all, and the card coerces `null → 0` (`renderer.ts:12094`) and skips. All three surfaces go silent, indistinguishable from up to date. The no-**remote** case keeps its own shape; the no-**upstream** case does not.

### Documentation

6. **Three of six tasks are `done` with every Definition-of-Done box unticked**: [[TASK-0417]] (8 unticked / 2 ticked), [[TASK-0419]] (9 / 0), [[TASK-0420]] (10 / 0). Twenty-seven boxes. [[TASK-0415]], [[TASK-0416]] and [[TASK-0418]] are fully ticked, so this is not a house style — from the notes alone a reader cannot tell what those three delivered, and in 0417's case the unticked box is the one this note ticks as acceptance.
7. **[[TASK-0419]] and [[TASK-0420]] are in `tasks:` but in neither Scope nor Acceptance.** They arrived mid-feature and no criterion here judges them — which is how the only false claim in the set reached `done` unexamined.
8. `src/project_os_cockpit/git_state.py:79` — the `commits` field comment says *"capped at MAX_COMMITS"*. There is no `MAX_COMMITS` in the repo, and the module docstring 35 lines above says the cap was written and removed the same hour. A stale comment on the exact invariant the feature turns on.
9. `tests: []` and `requirements: []`. No rule is broken — with no linked tests the feature gate is vacuous — but a feature this size closing with no `TST-*` is a gap beside comparable ones ([[FEAT-0056]] → [[TST-0023]]), and it is why finding 3 went unnoticed.
10. The criterion's literal `3 · commits to push` does not exist. `refreshObligationBadges` composes `${count} ${noun} to ${verb}` joined by `, ` (`renderer.ts:3700`) — "6 commits to push", no separator.

### Verified, by running it

- **[[TASK-0415]] holds, adequacy claim included.** Reverting the composition in `fleetHealth()` (`desktop/src/ipc/fleet-health.ts:493`) fails exactly four of the five cases in `desktop/tests/git-state.test.mjs` and leaves the pure-function one passing — the note's claim reproduces to the case.
- **[[TASK-0416]] holds.** `counts_by_kind`'s note-less count mutated to `+2` fails six tests across `test_view_landings.py` and `test_tests_view.py`, including both carve-out replacements the note names.
- **[[TASK-0418]] holds.** One push implementation, the deploy refusal in `buildPushControl` plus an independent server-side refusal at `git.ts:115`, per-commit marking by identity and a true total that outruns its window (`tests/test_history_payload.py:348`, `:423`). [[DES-0011]] is `accepted` with its artifact present.
- **Live numbers that re-derive today**: `your-applications.com` at **34** commits on a deploy remote (`production/master`, `root@76.13.51.7:…`), `your-trainer` at **23** uncommitted on the `docs/` + `SNAPSHOT.yaml` scope, this repo's Overview badge at **6** with `breakdown: {"unpushed commit": 6}`. Both surfaces that count uncommitted work use that same scope, so the note's two-numbers-behind-one-word concern is structurally closed.
- **Not re-derivable**, and no reproduction recorded: *"Intent's group came out 3 against a badge of 5"*, *"ten workspaces discovered and digests known: 1"* (twelve `SNAPSHOT.yaml` repos exist today), *"three cards to eight"*, *"61 owed items"*, *"7 commits not pushed twice on one page"*. Runtime observations, not defects — but nothing lets a later reader check them.
- **Suites run**: `bash tools/scripts/validate-docs.sh` → OK. `.venv/bin/pytest` → 1258 passed, 2 skipped (which includes the desktop node suite, run from `tests/test_desktop_node_suite.py`). `node --test desktop/tests/git-state.test.mjs` → 5 passed. Failures did appear on two runs, and none named a file this feature touched: `test_parent_backlink.py` on a tree another session was mid-commit on, and `test_coverage_registers.py` / `test_tests_view.py` on two `CHG-*` notes that session was editing concurrently.

Findings 1–5 are not yet filed as `ISS-*`; the review skill asks for that and for keeping the item out of terminal status, and both are left to the author rather than done unilaterally by the reviewer.

## Links

- Decision: [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]
- Design: [[DES-0011-Publication-Is-An-Obligation]]
- The defect that motivated it: [[ISS-0156]]
- Phase: [[PHASE-030-Obligations-Go-Home]]

## Reopened — 2026-08-14, out of `done`

Independent review returned **changes-requested** with five blocking findings, so this leaves terminal status until they clear. `done` on a feature whose dismissals did not survive a restart was a claim the record could not support.

**Fixed the same day:**

- **Dismissals survive a restart.** `pruneDismissedAlerts` ran at module load with `workspaces` still `[]` and deleted every restored key, persisting `{}`. This is the property Edwin asked for in so many words, and [[TASK-0420]]'s own DoD asked for it to be *"asserted rather than assumed"* — the box was never ticked and no test existed. Four now do, executing the real compiled function.
- **An unknown count is no longer a silent zero.** [[ADR-0027]]'s fourth admission test, which [[TASK-0415]]'s opening paragraph names as this obligation's gate. A branch with no upstream made `ahead` `None`, and all three surfaces rendered it as nothing owed. The registry now emits one row saying the count is unknown, `history_payload` returns `None` rather than `0`, and the band says *"No upstream set"* with no button — because nothing can say what pushing would send.
- **Acceptance criterion 1 amended** to what shipped.
- **A comment naming `MAX_COMMITS`**, a symbol that never existed, corrected.

**Filed rather than fixed:** [[ISS-0165]] — the attention card reads `probeGitState`, a second git walk, so *"one walk, agree by construction"* is untrue of the three surfaces that shipped. It needs the card to read the sidecar's payload rather than shelling out again, which is a change to how `fleetHealth` composes rather than a repair.

**Still owed before this returns to `done`:** the 27 unticked DoD boxes on [[TASK-0417]], [[TASK-0419]] and [[TASK-0420]] — three tasks are `done` with every box unticked, which is how the dismissal defect reached a terminal status unexamined. TASK-0419 and TASK-0420 are also in `tasks:` but in neither Scope nor Acceptance, so no criterion judged them at all.

## Returned to `done` — 2026-08-14, at PHASE-030's close-out

Edwin: *"Close off the phase 030."* This was the phase's only unresolved child, so the debt above had to clear first rather than be carried past a closing phase.

**The 27 boxes are resolved: 26 ticked with evidence, one marked `[~]`.** The `[~]` is [[TASK-0417]]'s *"the overview's `Needs you` group carries a row"* — not delivered, and not deliverable: `overview` is not a nav mode, so that payload falls back to `features` and nothing fetches it. [[TASK-0418]] re-homed the row to the rail's attention panel, which is where Edwin asked for it. Marked rather than ticked, and rather than quietly deleted.

**Finding 3 was still open and is now closed.** The review said no test exercised the publication source non-vacuously. Re-tested at close-out rather than assumed from the earlier repair: mutating `_publication_rows` to `return []` still left **1281 passing**, with exactly one failure — `test_an_unknown_publication_count_is_not_reported_as_zero`, which [[TASK-0421]] added for the *unknown* case and which says nothing about the counted one. `test_the_publication_obligation_is_exercised_non_vacuously` now builds a real repo with a forge-shaped remote and real unpushed commits and asserts count == len(rows) == landing count; the same mutation fails it.

**Two assertions [[TASK-0419]]'s DoD asked for did not exist at all** — the task had no test of any kind. Both were written here, and the first draft of the degradation test was too weak: narrowing `except Exception` to `except ValueError` left it green, because `Watermark._load` already swallows `OSError` and the missing-`docs/` case returns before anything can raise. A second test makes `digest_payload` actually raise.

**Finding 10** (the criterion's literal `3 · commits to push`, a string that never existed) is recorded as an amendment on [[TASK-0417]]'s box rather than silently reworded.

**Findings 4 and 9 are the ones this close-out does not claim.** Finding 4 — the attention card reading a second git walk — was filed as [[ISS-0165]] and is `fixed`: `fleet_git.py` is now the one walk. Finding 9 stands: `tests: []`, and this feature still links no `TST-*`. The guards are in the pytest suite rather than in a test note, which is this repo's habit for renderer work and is not what `QUALITY.md`'s gate reads. Left open and named rather than papered over — it is why finding 3 went unnoticed for a day.

## Second independent review — 2026-08-15, `changes-requested`

The pass [[PHASE-030]] recorded as unpaid at `d3ca1a8`. Clean context: this reviewer started from this note, its three re-ticked tasks, the phase note and the diffs `d754702..d3ca1a8`, never saw the authoring session's reasoning, and is not that session. Same model family as the author (`model:claude-opus-5`), which [[project-os-dev#ADR-0013]] does not gate on — context is the mechanism, and it is the part that is genuinely fresh here.

**Finding 3 is closed, and it reproduces.** Mutating `_publication_rows` (`obligations.py:336`) to `return []` fails `test_the_publication_obligation_is_exercised_non_vacuously` — 2 failed, 1284 passed, where the close-out reported 1281 green before the test existed. The claim was re-tested rather than trusted, and the re-test holds.

**What blocks:**

1. **The same vacuity survives on the sibling kind** — [[ISS-0169]]. `DEPLOY_OBLIGATION_KIND` (`undeployed commit`, verb `Deploy`) can be made to yield no rows with the **whole suite green** (1286 passed). It carries every unpublished commit on a deploy-only repo — `your-applications.com` at 34, which this review's own predecessor measured — so it is that project's entire publication badge. [[TASK-0417]]'s box for it is also the only one of that task's six with no evidence appended.
2. **A ticked box states evidence the code contradicts** — [[ISS-0170]]. [[TASK-0419]]'s *"No new subprocess per repo… calls `digest_payload` directly and **spawns nothing**"*. `_digest_counts` → `digest_payload` → `history_payload` → `subprocess.run(["git", …])` (`cockpit.py:5531`), and `fleet_validate.py:80` says so in its own docstring: *"one index build and one `git log` per repo per cold pass"*.
3. **"26 ticked with evidence" is not accurate.** Seven of the 26 carry no evidence text — TASK-0417's deploy box, and three steps each on TASK-0419 and TASK-0420. The DoD boxes proper are well evidenced; the sentence overstates the set.

**The `[~]` is honest, not evasive.** [[TASK-0417]]'s *"the overview's `Needs you` group carries a row"* states plainly that it was not delivered and cannot be, gives the mechanism, names where the row actually went, and cross-links this note's amended criterion 1. Verified independently: `NAV_MODES` (`cockpit.py:381`) does not contain `overview`, so `nav_payload` falls back to `features`. That is `QUALITY.md`'s amend-with-rationale, done in the open.

**Re-verified by running it**, at `d3ca1a8`: `.venv/bin/pytest` 1287 passed / 1 skipped; `bash tools/scripts/validate-docs.sh` OK; `cd desktop && npm run typecheck` clean; `node --test desktop/tests/*.mjs` 105 passed. TASK-0420's six DoD boxes were each checked against shipped code — `clearDismissalsFor` is called from `openWorkspace` (`renderer.ts:901`), the key is `${wsId}::${fingerprint}` through one `attentionFingerprint` (`renderer.ts:11875`), no age check survives in the path, and `attention-dismissal.test.mjs` executes the real compiled `pruneDismissedAlerts`. TASK-0417's amended badge string is right: `refreshObligationBadges` composes `${count} ${noun} to ${verb}` joined by `, ` (`renderer.ts:3693`).

**`tests: []` is not what blocks, and is harder to defend at a third close.** The prior review called it a gap rather than a rule violation and that reading still stands — but two of the three findings above are exactly the class a `TST-*` gate would have caught, and both were found by mutation rather than by reading. Finding 9's own sentence — *"it is why finding 3 went unnoticed"* — is now true twice.

**One structural note about this stamp.** `review_verdict: changes-requested` on a note at `status: done` is **invisible to the registry**: `_verdict_is_owed("changes-requested", "done")` is `False` by [[ISS-0121]]'s discriminator, and the validator's `REVIEW_SETTLED_STATUSES` covers `tests` only. So this verdict appears on no badge and in no `Needs you` group. Status is the author's to change and was deliberately not changed here — but a feature cannot honestly stay `done` on a verdict asking for work, and [[PHASE-030]] cannot stay `done` holding it (`PHASE-CHILDREN`).

## Second independent review — 2026-08-15, `changes-requested`

Run at Edwin's instruction rather than skipped, on the debt the close-out above recorded. It confirmed the close-out's central claim — finding 3 is closed, reproduced by mutation — and found that I had closed **one of two** kinds.

- **[[ISS-0169]]**, blocking: `undeployed commit` is a separate `NOTE_LESS` source with its own `rows` lambda, and nothing asserted it. Replacing that lambda with `lambda index: []` left the suite green at 1286 passed. Fixed by `test_the_deploy_publication_obligation_is_exercised_non_vacuously`, verified against that exact mutation.
- **[[ISS-0170]]**, documentation: [[TASK-0419]]'s "no new subprocess per repo" box carried evidence claiming the cold digest "spawns nothing". It spawns `git log`. The box's claim holds; my sentence under it did not.

Both fixed 2026-08-15. The `review_verdict` stamp is left at `changes-requested` deliberately: it records what the review found, and flipping it would be the author judging his own work, which is the thing the gate exists to prevent. A fresh pass would be needed to move it.

**Still not addressed, and named rather than absorbed:** `tests: []`. The reviewer's point stands — findings 1 and 3 are both the class a linked `TST-*` would have caught, and both were found by mutation rather than by reading.
