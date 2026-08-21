---
type: "[[feature]]"
id: FEAT-0142
aliases: ["FEAT-0142"]
title: "A release says what is in it — the derived set becomes an editable scope, so a feature can be held back without hand-writing the note's frontmatter"
status: done
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: changes-requested
review_response: "Fifth pass 2026-08-21: F1 - the release ITEM page carried a live mark control on every check row, which is ADR-0035's subject and this feature's own 'no write path to a check appears on the release page'. Fixed and the guard widened to name the shared row builder; both mutants fail it."
review_response_date: 2026-08-21
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["user:edwin"]
goal: "A person preparing a release can move a feature out of it, or hold one for the next one, from the release page — and the record says which features were CHOSEN rather than which happened to be finished."
requirements: []
tasks:
  - "[[TASK-0576-An-Exclusion-Says-Why-And-What-It-Cost]]"
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[FEAT-0072-The-Release-Surface]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0028-Publication-Is-The-Third-Phase]]"]
tags: [feature]
---

# A release names its contents by choice, not by timing

## Goal

Edwin, 2026-08-20: *"we still have not implemented a way to include/exclude features in a release."*

Confirmed absent. `publication.py` has exactly two modes and no third:

| release state | contents | who chose |
|---|---|---|
| unreleased | `kind: "derived"` — every unshipped feature since the last tag (`unreleased_payload`) | **nobody** |
| released | `kind: "frozen"` — the note's own `features:` list | whoever hand-wrote the frontmatter |

So the only way a feature leaves a release is for a person to open the note and edit YAML, and the only moment the choice is recorded is the moment the release ships. Before that, *"what is in it"* is a statement about **when work finished**, not about what anybody decided.

## Why this is a feature and not an issue

Nothing is broken. The derived set is the right default and should stay the default — it is what makes a release page useful in a repo where nobody has curated anything. What is missing is the **act of deciding**, and there is no note for it anywhere: [[ISS-0181]] covers four other things the release surface cannot do, [[ISS-0206]] is about checks rather than features, and the release-surface feature was scoped to reporting.

## Scope

**In:**

- Hold a feature back from the release being prepared, and put a held one back in.
- Persist the decision where it survives a re-render and a restart — the release note is the obvious home, since that is already the frozen record.
- The page distinguishes **derived** rows from **chosen** rows, so a reader can tell a default from a decision.
- A held-back feature has somewhere to go: the next release, or explicitly nowhere yet.

**Out:**

- Anything that writes an acceptance verdict. [[ADR-0035]] holds: a release page reports, it does not record — and this feature must not become the exception that reopens it. Scope selection is a fact about the *release*, which the release note already owns; a check's verdict is a fact about a check.
- Reordering, grouping or annotating the contents list.
- Issues and requirements. Features first; the same mechanism can widen later if it earns it.

## The mechanism (Edwin, 2026-08-20)

> *"If we can just have all the features available for the release in the release document at first with a checkbox all new features checked and then the user can uncheck/check some of them if they need to be included, the acceptance tests for the release can then be adjusted based on the selected features."*

**A checkbox list in the release document.** Every available feature is a row; a new one arrives checked; a person unchecks what is not going in.

This fits the grain of the system better than a control that lives only in the UI. [[ADR-0009]] makes notes the authored source of state, this codebase already parses checkboxes out of note bodies — phase exit criteria, and the release note's own *still owed* boxes — and a list in the document renders in Obsidian **and** the cockpit, is hand-editable, and shows up in a diff. Defaulting new features to checked also makes the whole feature additive: a repo that never touches it keeps exactly today's behaviour.

Two properties it must have, or it rots into the thing it replaced:

- **Reconciled on render, never written once.** A feature completed after the list was authored appears on it, checked, without anybody re-running anything; an unchecked one is never silently dropped. The release note in this fleet has already drifted once for exactly this reason — it was hand-maintained and nothing reconciled it.
- **One source, not two.** `publication.py` reads `features:` from frontmatter for a shipped release. The checkbox list is the **working** state; `features:` is written **at the seal**. Two live representations of one fact is how two surfaces come to disagree, and [[ADR-0035]]'s frozen-record guarantee depends on the frozen one having a single moment of authorship.

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

## The three open questions, answered

**Q1 — where does the decision live before the release ships?** *Answered:* in the release document, as the checkbox list above, with `features:` written at the seal.

**Q3 — does excluding a feature change the gate?** *Answered by [[ADR-0040]], and not with a plain yes.* **Selection subtracts; it never divides.** Every check gates except one whose `covers:` names *only* deselected features. A check covering both a selected and a deselected feature still gates. A check with no `covers:`, or covering only an `ISS`/`REQ`/`PHASE`, is untouched by selection.

The measurement is why. in `your-trainer`'s **working tree** (not `HEAD` — see the basis note above), 2026-08-20 — 59 blocking checks: 39 cover a `FEAT`, 18 cover only `ISS`/`PHASE`, 2 carry no `covers:` at all. The 39 land on **nine** features, and **six of those nine (36 checks) are not in this release's 32-feature derived contents**. Scoping the gate *to* the selection would take it from 59 to about 23 on the first render, by nobody's decision, and would empty the `chronic` bucket whose whole purpose is to keep long-carried debt visible.

**Q2 — what does holding back mean when the feature is already `done`?** *Answered, and it is the sharpest constraint here.* Five of those six out-of-scope carriers are `done` — merged, in the binary, shipping regardless of what any list says. **A checkbox controls what a release is accountable for, never what it contains.** Dropping the checks of a `done` feature is shipping unverified code, not deferring code. Legitimate behind a flag or as accepted risk; an illegitimate convenience otherwise — so the page must distinguish *held for a later release* from *in the build, not verified here*.

## What this feature is NOT for

Edwin, same day: *"these are open because of multiple of reasons and happy to re-evaluate them for each release to see if we can resolve them but more than likely they will stay open for this release as well. (for instance I don't have the hardware to test those corner cases)"*

**That is not a scope decision and must not be expressed as one.** [[ADR-0037]] already built it, in the ledger's outcome vocabulary:

| outcome | clears | survives the seal | for |
|---|---|---|---|
| `na` | yes | **yes** | the check can never apply here — *no such surface on this platform* |
| `excused` | yes | **no** | not done this cycle, by decision — **owed again after the seal** |
| `blocked` | **no** | — | temporarily impossible by accident; blocks deliberately |

`excused` **is** re-evaluate-every-release, by construction. Using deselection for a hardware gap would put a fact about a check into a list about features, lose the reason, and make it permanent — the exact property `excused` was designed not to have.

**And it cannot be used in the repo that needs it.** `your-trainer` has **no `docs/releases/ledgers/` directory at all** — not one recorded verdict — and its checks still carry `mark:` in frontmatter. So its 59 blockers are unticked notes rather than considered decisions, and the tool has never had anywhere to put the reason. **That is a prerequisite for this feature being useful**, and it belongs to [[ISS-0209]].

## Acceptance

*(All seven met 2026-08-21. Five landed under [[FEAT-0129]]'s tasks, one was found already true and guarded, and the last is [[TASK-0576]].)*

- A feature can be unchecked in the release being prepared and re-checked, with no hand-editing of frontmatter, and the list is reconciled against the live derived set on every render.
- The choice survives a reload and a restart, and a feature completed after the list was authored appears on it, checked, without intervention.
- Unchecking a feature removes **only** checks whose `covers:` names no selected feature; a check with no `covers:` or covering an `ISS`/`REQ`/`PHASE` is unaffected. Guarded by a test built on the mixed case — a check covering one selected and one deselected feature — because that is the cell a subtraction rule gets wrong.
- Every exclusion carries a reason, and the page reads `N features held back · M checks no longer gating`. A total that fell says why it fell.
- `chronic` still counts an excluded check. It stops blocking; it does not stop being counted.
- A shipped release's contents remain frozen — [[ADR-0035]] is not weakened, and no write path to a check appears on the release page.
- Nothing ships before [[ADR-0040]] is accepted.

## Links

- Plan: `plan/PLAN.md`
- Server: `src/project_os_cockpit/publication.py` (`kind: "derived"` / `kind: "frozen"`)
- Client: `desktop/src/renderer/renderer.ts`, the release contents section

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

Scope, mechanism and the three answered questions are consistent with `ADR-0040` and with the code: `publication.release_payload` really does have exactly two modes and no third, and the `derived` contents count is 32 as stated. The acceptance criterion naming the mixed case — *a check covering one selected and one deselected feature* — is the right cell to guard, and the `excused`-not-deselected split is argued from `ADR-0037`'s actual vocabulary rather than asserted.

**Same single correction as `ADR-0040`**: *"On `your-trainer` at HEAD, 2026-08-20 — 59 blocking checks: 39 / 18 / 2 … six of those nine (36 checks)"* is a working-tree measurement. At HEAD it is 68 / 43 / 17 / 8, ten features, 40 out of scope. The conclusion is unaffected.

One live inconsistency to resolve before anything is built: the criterion *"Nothing ships before ADR-0040 is accepted"* now points at a note whose frontmatter says `accepted` and whose body says `Proposed`.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Basis blockquote present and its figures re-verified. The measurement it rests on reproduces exactly at the stated basis (59 / 39 / 18 / 2, nine features, 3-in / 6-out, `FEAT-0074` `backlog` with 20 = the whole `quiet` bucket, five of six `done`, ledgers in one of twelve repos), and the conclusion holds at HEAD too (40 of 43). Nothing further from me.

## Re-scoped 2026-08-20 — over half of this shipped under [[FEAT-0129]]

**This note says `backlog` with `tasks: []`, and it has been described as "a full build with no tasks" three times today. That is wrong**, and it was wrong because nobody re-read it against what landed.

[[FEAT-0129]] — *"A release names its own contents"* — closed `done` today, and it is substantially the same feature seen from the implementation side. Measured against this note's own criteria:

| criterion | state | where |
|---|---|---|
| 1 — uncheck/re-check, no hand-editing, reconciled on render | **built** | `note_writes.release_contents` (three refusals), `publication.contents_candidates` |
| 2 — survives reload/restart; a later-completed feature appears checked | **built** | contents live in the note; the derived set is reconciled per render |
| 3 — subtraction, guarded on the **mixed case** | **built** | `Suite.blocking_minus` under [[ADR-0040]]; `test_the_mixed_cell_still_gates` |
| 4 — every exclusion carries a **reason**; page reads `N features held back · M checks no longer gating` | **NOT built** | `publication.py:948` computes held-back; no reason field, no summary line |
| 5 — `chronic` still counts an excluded check | **MET, now guarded** | `delta()` reads `current.blocking()` — the *unsubtracted* list — while the gate reports `blocking_minus`. True by call-ordering; `test_a_deselected_check_stops_blocking_but_keeps_being_counted` now pins it |
| 6 — shipped contents frozen, no write path to a check | **built** | `test_a_shipped_release_is_immutable`, [[ADR-0035]] intact |
| 7 — nothing ships before [[ADR-0040]] is accepted | **met** | `status: "accepted"` |

**Five of seven are met. Two are not**, and they are the *reporting* half rather than the mechanism: an exclusion currently happens without recording **why**, and the page does not say what the selection cost. Criterion 5 is the sharper of the two — [[ADR-0028]]'s `chronic` count exists so a check that stops blocking does not also stop being visible, and a subtraction rule that quietly shrinks it would reintroduce exactly the overclaiming this phase spent itself removing.

### What this changes

This is not a feature waiting to start. It is a **feature two-thirds delivered under another note's tasks, never reconciled** — which is why it kept reading as untouched. The remaining work is small and specific, and it should be minted as two tasks against these two criteria rather than planned as a build.

It also raises whether FEAT-0142 and [[FEAT-0129]] should be one note. They are not duplicates — 0129 is *"a release can name contents"* and 0142 is *"and the record says why, and what it cost"* — but a reader meeting both cold cannot tell that, and this note's `backlog` status actively misleads. That is a judgement for Edwin, not a tidy-up to perform.


### Criterion 5 re-measured — met, and it was true by accident

Looked for rather than assumed. `delta()` computes `blocking = current.blocking()`, the **full** list, while the gate reports `blocking_minus(deselected)`. The two answer different questions, so a held-back check keeps appearing in `chronic` exactly as this criterion requires.

**Correct, and fragile.** Nothing expressed the dependency. Someone tidying `delta()` to *"use the same list as the gate"* would make the chronic bucket shrink whenever a feature is held back — silently, and in the flattering direction. `blocking_minus`'s own docstring names emptying that bucket as the reason [[ADR-0040]] rejected the divide reading, so the hazard was understood and unguarded.

Now guarded on the mechanism and behaviourally, and the mutant — `delta()` switched to `blocking_minus` — fails it.

**So six of seven are met.** The one genuinely outstanding criterion is 4: an exclusion records no **reason**, and the page never reads `N features held back · M checks no longer gating`. That is one task, not a build.


## Closed 2026-08-21 — the seventh criterion, and two things that were never reachable

[[TASK-0576]] delivered criterion 4: an exclusion records a **reason** in `held_back:` beside `features:` on the release note, the page reads `N feature(s) held back · M check(s) no longer gating`, and the two numbers arrive in one sentence because either alone is the shape this phase exists to remove.

**The count and its cost are read from different places on purpose.** The count is the held-back set; the cost is `len(blocking()) - len(blocking_minus(deselected))`, measured against the same suite the gate reports, so the page cannot show a number the gate never computed. A second traversal is how two surfaces come to disagree.

### Building the reporting half found that the mechanism half was not reachable

Criterion 1 was recorded as **built** on the strength of `note_writes.release_contents` existing with its three refusals. It does exist and it is correct. **Nothing could call the removal.** The renderer offers `Remove` only on `c.kind !== 'derived'`, `publication.release_payload` emitted `derived` for every unshipped release and `frozen` only after the seal, and no third kind was ever produced — so a feature could be added through the front door and never taken back out through it.

That is the sixth time in this phase that *a capability existed, was tested, and no front door reached it* — [[ISS-0249]] is the same finding about `retire_check` and `cover_check`, arrived at from the other end.

`contents.kind` is `chosen` now when a release names its contents, which is also the *"page distinguishes derived rows from chosen rows"* line in this note's own Scope, unbuilt until today.

**And the subtraction could not fire on the page a person opens.** `~release/next` passes the literal `"next"` as `release_id`; `index.by_id("next")` is `None`; `named` came back empty; nothing was ever held back. Fixed to read the resolved release, and guarded.

### What is NOT closed by this

The measurements in this note are `your-trainer`'s **working tree** on 2026-08-20 and that basis is stated in the blockquote above. [[ISS-0209]] still bounds what any of it proves, and `your-trainer` still has no `docs/releases/ledgers/` — so *"the honest alternative to deselecting is unavailable in the repo that needs it"* remains true. That is [[ISS-0209]]'s, not this feature's.

Whether this note and [[FEAT-0129]] should be one note is still Edwin's judgement and is deliberately not performed here.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved.** All seven criteria are met, and the two that were most at risk of being ticked on a pointer were verified by mutant.

- **Criterion 4 is built.** `note_writes.release_contents` refuses a removal with no reason (400). I disabled the refusal (`if False and action == "remove" …`): `test_a_removal_with_no_reason_is_refused` failed. The refusal is in the **write path** rather than the renderer, so the second front door gets it too, which is the right place under [[ISS-0230]].
- **The cost is the size of the subtraction, not a second count.** I replaced `"checks": len(unsubtracted) - len(blocking)` with `"checks": len(blocking)`: `test_the_cost_is_the_size_of_the_subtraction_not_a_second_count` and `test_nothing_held_back_reports_no_cost` both failed. The three-check fixture is what makes that mutant detectable, and the note says so explicitly — that is a fixture designed against a specific mutant, and it works.
- **Criterion 5 is pinned two ways and both halves are real.** The behavioural half builds a suite, deselects a feature, and asserts the row survives in `chronic`. The mechanism half is a source assertion, which is normally this repo's recorded pitfall — here it is justified, because `delta()` takes no deselection argument and the subtracting mutant cannot be written without new plumbing.
- **ADR-0035 is unweakened.** `test_no_write_path_to_a_check_appears_on_the_release_page` scans the held-back block for `askForMark`, `walkOneCheck` and `/api/notes/check`, and `gateMark`/`markGateRow` are absent from the whole renderer.

The renderer-side assertions are source-text rather than executed, which is a real limit — but the payload half (`release_payload`, `gate_payload`) is executed, and that is where the numbers are computed. Noted, not held against the note.

The open question this note raises — whether FEAT-0142 and [[FEAT-0129]] should be one note — is correctly left as Edwin's judgement rather than performed.

No changes requested.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved, confirming the first-pass verdict.** This note carries no first-pass finding and this commit added only a review section to it, so the pass here was a spot-check of the criterion the phase closes on rather than a full re-review.

Criterion 4 — *every exclusion records a reason, and the page says what the selection cost* — is built and reachable, verified in the code rather than from the note: `publication._held_back_reasons` / `_held_back_rows` read `held_back:` off the release note's own frontmatter and **report an exclusion with no recorded reason rather than hiding it**, `publication.py:1005` puts `held_back` on the payload, and `renderer.ts:7965` draws `${heldBack.length} feature(s) held back · ${cost} check(s) no longer gating`. `tests/test_release_held_back.py` and `tests/test_gate_subtraction.py` guard both halves.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** This is [[PHASE-037]]'s fifth exit criterion and the one closed on its last day, so I treated it as one of the two weakest and re-verified it rather than reading the earlier passes' verdicts.

The payload half is guarded behaviourally: `test_the_page_says_how_many_were_held_back_and_what_it_cost` asserts the held-back row, its **resolved title** and `gate.deselection` in one construction, so a payload that reported a count without a cost, or a raw id, fails. The renderer half is source-text — this repo's own recorded pitfall — but it is anchored on the data rather than on the sentence: rewriting the line to `${heldBack.length} excluded` fails `test_the_page_never_shows_a_smaller_number_alone`, and emptying `heldBack` while leaving the sentence in place fails **three** tests, including `test_no_write_path_to_a_check_appears_on_the_release_page`. `publication._held_back_rows` reports an exclusion with no reason rather than hiding it, and `renderer.ts:7965` draws the sentence the criterion quotes.

### What survived refutation

- **Finding A's restoration is verbatim and the tests are not vacuous.** I extracted both functions from `07602db` and from `c9d6a82` and diffed them: byte-identical. `tests/test_checks_view.py` is back to **22** `def test_` functions. Both guards kill mutants: flattening `for (const area of areas)` and deleting `checkPercent(area.items)` each fail `test_the_page_groups_by_surface_and_not_as_one_flat_list`; changing `(done.length / total)` to `(settled.length / total)` fails `test_a_stale_tick_is_not_drawn_as_done`.
- **Nothing else was lost anywhere in `f5ca55b..c9d6a82`.** I parsed every `tests/**/*.py` at all four commits and diffed the `def test_` sets file by file. The only removals in the whole range are the seven `covered_by:`/promotion tests at `07602db`, every one of them a test for the mechanism `REQ-0057` deleted, replaced in the same commit by seven guarding its absence; the two at `b635c39`, restored here. No test file was deleted at any point. Totals 1761 → 1829 → 1830 → **1835**.
- **Finding B's own tests are real.** Restoring the absence rule (`check not in passing and check not in failing`) fails `test_two_runs_covering_different_toolchains_do_not_retract_each_other` and `test_a_run_that_never_reached_the_test_leaves_it_alone`; deleting the skipped branch fails `test_disabling_the_covering_test_does_the_same` and the latter; folding skipped back into absence fails two. I also built the alternating-toolchain loop myself — `TST-0001` by a `.py` test, `TST-0002` by a `.kt` test, one platform, three full cycles — and counted **two** ledger entries, both `pass`, no retraction.
- **Finding C's test is real.** Restoring `and standing.by == args.by` fails `test_a_second_machine_saying_pass_adds_nothing` and nothing else.
- **Finding E's claim is true.** `validate_moved_verdict_fields` returns early unless `docs/releases/ledgers/` exists *and* holds a `*.json`, so the twelve `LEDGER_MOVED_FIELDS` are refused only in a ledger-keeping repo. The enumeration is right at its stated arity: all ten named fields are written by `note_text`, `covered_by` is not, and the twelfth (`merged_from`) is correctly absent from both lists.
- **Finding G is done.** The false closing clause is gone from `ISS-0213`'s `review_response`.
- **Suite, validator, CI step set.** `2060 passed, 3 skipped` (268s), `validate-docs: OK`, and `validate-docs.sh --as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c9d6a82`.

## Independent review — fourth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c9d6a82..9a75f11`; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all three earlier passes, recorded in `reviewed_by` as provenance rather than as a compliance token. Every count below was re-measured from the tree and every claim about behaviour was established by running the code, not by reading it. **This verdict supersedes the third pass's on this note.**
**Verdict: approved.** All seven criteria hold and criterion 5 — the one that is a construction rather than a rule, and therefore the fragile one — is now pinned both ways: `delta()` must read `current.blocking()` and must not call `blocking_minus`, and behaviourally a deselected check drops from the gate and stays in chronic. The mutant that switches `delta()` to `blocking_minus` fails it. Criterion 4's reporting half is delivered under [[TASK-0576]] and its guard is not merely text-shaped: rewriting the sentence to a bare count fails one test and emptying the held-back set while leaving the text fails three.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all four earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fourth pass's verdict on this note.**

**Verdict: changes-requested — on the universal sentence, not on what was built.** The held-back block itself is right and I checked it rather than read it: it draws the count and its cost in one line, every row carries its reason, an exclusion with no reason renders *"no reason recorded (hand-edited)"* instead of inventing one, and the block offers no verdict control. The criterion written above it is what fails.

### Finding 1 (high) — "no write path to a check appears on the release page" is false at `991838e`

`renderer.ts:7610`, inside `buildReleaseItemPage`, renders every acceptance-check row of `~release/<id>/<ITEM-ID>` with `s.appendChild(buildCheckRow(item))` and no `manual` argument — so `manual` defaults to `true` and each row gets a `checkMark(item)` button (click → `markCheckRow` → `walkOneCheck` → `askForMark` → `postJson('/api/notes/mark-check', …)`) **and** a `Retire` button (→ `retireCheckRow`). Both change a check. The page is routed at `renderer.ts:1249` off `~release/`, renders in `publication` nav mode, and its rows are real `GateItem`s from `publication.release_item_payload`. The code says it in its own voice at `renderer.ts:7608` — *"The mark control INLINE — the same one the view and the gate wear"* — while `retireCheckRow`'s docstring says the control *"lives on `~checks`, never on a release page ([[ADR-0035]])"*.

**Why the widened guard misses it, established by mutation rather than by reading.** Inserting `void askForMark({});` into each of the eight `subjects` functions fails the test **8/8**. Inserting `wrap.appendChild(buildCheckRow(item));` into the same eight — the exact call the release item page already makes — **passes 8/8**, including into `buildReleasePage`. The guard is one call deep; the live violation is one call deep.

### Finding 2 (medium) — the guard's docstring claims more than the guard does

It says *"The region is every release-page render function"* and *"Named rather than pattern-matched, so renaming one into existence outside this list is a visible edit here."* Constructed: a new `function buildReleaseChecksPanel(items: GateItem[])` calling `askForMark`, inserted before `renderReleasePage` → **17 passed**. `found == subjects` catches only the *disappearance* of one of the eight; a ninth is invisible, and the `^(?:async )?function` scan cannot see an arrow-function surface at all. The functions the release pages delegate row rendering to — `buildCheckRow`, `checkMark`, `gateGroup` — are not in the set, which is the mechanism of Finding 1.

**What is genuinely closed.** The 2600-character window is gone; comments are stripped, so the note recording `markGateRow`'s deletion no longer reads as a write path; the two file-wide `function gateMark` / `function markGateRow` assertions hold; and the anchor really is inside `buildReleasePage`'s region (`covered` is asserted, not assumed). The widening is a real improvement that does not reach the sentence it is cited under.

**Suite, validator, CI step set — observed, not reported.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK` (warnings only); `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`.
