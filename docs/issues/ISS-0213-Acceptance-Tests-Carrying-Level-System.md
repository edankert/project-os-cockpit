---
type: "[[issue]]"
id: ISS-0213
aliases: ["ISS-0213"]
title: "Five acceptance tests in your-trainer carry `level: system`, so they route to a flat group instead of under their tier"
status: deferred
owner: user:edwin
created: 2026-08-18
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
severity: medium
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]"]
---

# Edwin: *"are these really manual tests?"*

Yes — and that is not the interesting half of the answer.

## Measured

The five rows in `your-trainer`'s **Needs a walk**:

| id | `level:` | `command:` | file |
| --- | --- | --- | --- |
| TST-0011 | `system` | none | `tests/TST-0011-AndroidBleHardeningAcceptance.md` |
| TST-0012 | `system` | none | `tests/TST-0012-IosBleHardeningAcceptance.md` |
| TST-0013 | `system` | none | `tests/TST-0013-IosParityAcceptance.md` |
| TST-0015 | `system` | none | `tests/TST-0015-ProSeatSelectionAndHiddenRiders.md` |
| TST-0018 | `system` | none | `tests/TST-0018-EntitlementResolution.md` |

All five are `status: ready` with no `command:`, so under [[ADR-0034]] they are manual: a person runs them. That part of the surface is correct.

**Three of them are named `…Acceptance`.** They are acceptance tests that never got `level: acceptance`, because they predate the migration and live in `docs/tests/` rather than `docs/tests/acceptance/`. `_tests_groups` excludes `level: acceptance` and routes the rest into flat buckets — so the level, not the content, is what decides where a test appears.

## Why this is the phase's shape

The reader sees five acceptance tests in a flat list and 579 in tier sections, with nothing on screen explaining the difference. The answer is a frontmatter field neither list mentions.

**The fix is data, not code** — and that makes it the one item here that needs a judgement per note rather than a rule. `EntitlementResolution` and `ProSeatSelectionAndHiddenRiders` are not obviously acceptance tests just because they are manual and system-level.

## The judgement, made 2026-08-20

Two of the five had already been resolved before this was picked up: **TST-0015** and **TST-0018** now carry `level: acceptance` and `status: active`, and both render under their tier. The issue's table above is that far out of date.

The remaining three, each read rather than pattern-matched on its name:

| id | judgement | why |
|---|---|---|
| **TST-0011** Android BLE hardening | `acceptance` | *"Validate, on a real smart trainer… This is the gate (with TST-0012 for iOS) that closes TASK-0592/0593/0766, ISS-0256/0329, FEAT-0085, REQ-0185 and RISK-0008. Until every Tier-A row here passes, the branch stays unmerged."* A note that holds a branch shut is an acceptance gate by any reading. |
| **TST-0012** iOS BLE hardening | `acceptance` | The iOS half of the same gate, in the same words. |
| **TST-0013** iOS parity acceptance | `acceptance`, **with a caveat below** | *"Manual acceptance coverage for everything the iOS parity push implemented… so Edwin can verify each new rider-facing surface before the iOS release."* Gates a release. |

**The caveat on TST-0013 is worth more than the level.** It carries **107 checkbox rows** in one note (TST-0011 has 18, TST-0012 has 15). Under [[ADR-0030]] one note is one check, so calling it `level: acceptance` labels a 107-check document as a single acceptance check. The level is still right — the alternative is worse, since `system` routes it to a flat group that contradicts its own title — but the shape is the document-suite [[PHASE-035]] migrated away from, and it should eventually become notes. Noted rather than fixed here: that is a migration, not a field edit.

## RETRACTED 2026-08-20 — the measurement below is wrong and the change is reverted

**The relevel was applied and then undone.** Independent review found that the simulation proving *"zero gate impact"* used an instrument **structurally incapable of showing impact**.

`acceptance.load(docs)` was called **without an index**. Every live surface loads **with** one — `server.py`'s `/api/cockpit/acceptance`, and `publication.release_payload` through `gate_payload(index=index)` — and only the indexed loader resolves a `level: acceptance` note that lives outside `docs/tests/acceptance/`. All three of these do. So the before/after figures could not move, and did not, and were reported as evidence that nothing moved.

Re-measured on the same working tree, only the three `level:` lines differing:

| loader | items | blocking |
|---|---|---|
| **without** an index — what was measured | 579 | 57 → 57 |
| **with** an index — what the app uses | **581 → 584** | **59 → 62** |

`newly blocking: ['TST-0011', 'TST-0012', 'TST-0013']`. **TST-0013 became one blocking check standing over 107 checkbox rows.**

Edwin authorised applying it on the strength of the false claim, so the edit was **reverted** rather than kept and re-argued: 581 items and 59 blocking restored, all three back at `level: system`, the files clean in git.

**Two things in the record were wrong and are named rather than tidied away.** The commit message on `d693f7b` says the write was *"refused by the sandbox"*; it was refused, and then applied thirteen minutes later once Edwin granted access, and the message was never amended. And the earlier version of this section presented the index-less figures as *"simulated on a throwaway copy rather than reasoned about"* — the care was real and it was spent on the wrong instrument, which is the more dangerous shape: a measurement that cannot fail looks exactly like a measurement that passed.

**The judgement about the level is unchanged.** These three are acceptance tests by their own words. What is now known is that acting on it costs three blocking checks — and for TST-0013, one blocking check over 107 rows, which argues for splitting it before relevelling it, not for relevelling it as it stands.

## The original measurement, kept as the record of the error

> **Everything from here to the end of `Applied 2026-08-20` is FALSE and describes a state that no longer exists on disk.** It is kept because the shape of the error is the useful part — a measurement that could not fail, read as one that passed — and deleting it would leave the retraction above arguing with nothing. The present tense below is the present tense it was written in; **"Zero gate impact" is wrong (it is three checks), and "Applied" is wrong (it was reverted).** Re-review 2026-08-20 flagged that quarantining without marking is the same defect one level up.

## Measured before recommending it

> ⛔ **SUPERSEDED AND FALSE.** *"Zero gate impact"* below is wrong — it is **three** checks — and the measurement that produced it could not have detected a change. Retained as the record of the error; see the retraction above. Marked here in its own first line because a heading is a landing target: a reader arriving by link or scroll never sees a banner further up.

Relevelling all three was simulated on a **throwaway copy** of `your-trainer/docs` rather than reasoned about:

```
BEFORE: items=579 blocking=57
AFTER : items=579 blocking=57
newly blocking: []
```

**Zero gate impact.** `acceptance.load` reads the acceptance *directory*, and all three live in `docs/tests/`, so the change moves them in the navigator — out of the flat `Needs you` group and under their tier — and touches nothing the release gate counts. That is exactly the second criterion below and nothing else.

## Applied 2026-08-20

> ⛔ **SUPERSEDED AND FALSE — and this section is not "the original measurement" either**, so it sat under a heading that did not cover it. The edit described below **was reverted**; all three notes are back at `level: system` and clean against `your-trainer` HEAD. *"The prediction held exactly"* is the error restated, and *"left uncommitted pending Edwin's review"* describes a state that no longer exists on disk.

The edit is three lines, `level: system` → `level: acceptance`, in:

- `your-trainer/docs/tests/TST-0011-AndroidBleHardeningAcceptance.md`
- `your-trainer/docs/tests/TST-0012-IosBleHardeningAcceptance.md`
- `your-trainer/docs/tests/TST-0013-IosParityAcceptance.md`

Applied on Edwin's confirmation. **The prediction held exactly**: `579` items and `57` blocking before and after, and all three moved out of the flat `Needs you` group to render as children of their tier — which is the second criterion below, and nothing else moved.

Left **uncommitted in `your-trainer`** pending Edwin's review: a change to that repo's record should be his commit, not a side effect of work in the cockpit.

## Done when

- [x] Each of the five is assigned a `level:` deliberately, with the reasoning recorded.
- [ ] **Decide, on the true cost**, whether TST-0011/0012 are relevelled — three blocking checks enter `your-trainer`'s gate.
- [ ] **TST-0013 is not relevelled as it stands**: 107 checkbox rows behind one blocking check is the document-suite shape [[PHASE-035]] migrated away from. Split first.
- [x] No test's *group* contradicts its own name — verified for TST-0015/0018; the other three keep the contradiction until the above is settled.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: changes-requested.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

**The retraction is accurate and the revert is real.** Verified independently: all three notes are back at `level: system` and clean against `your-trainer` HEAD; the suite is 581 items / 59 blocking again. The two-loader table is right, `newly blocking: ['TST-0011','TST-0012','TST-0013']` reproduces, the stale `d693f7b` message is named, the status is back to `open`, and the *"Done when"* now requires splitting `TST-0013` first. Naming the instrument rather than the arithmetic is the correct diagnosis.

**But the note is not free of the claim it retracts.** Beneath `## The original measurement, kept as the record of the error` — a heading with no body — sit two sections in the unqualified present tense:

- `## Measured before recommending it` still asserts **"Zero gate impact."**
- `## Applied 2026-08-20` still asserts *"Applied on Edwin's confirmation. **The prediction held exactly**"* and *"Left uncommitted in `your-trainer` pending Edwin's review"* — describing a state that no longer exists on disk, since the edit was reverted.

Quarantining the error as the record is right; leaving it in the present tense is the *"earlier correction left standing beside a later one"* pattern this phase has now hit repeatedly. `## Applied 2026-08-20` is also not *"the original measurement"*, so it sits under a heading that does not cover it. Mark both sections as superseded in their own first line, or fold the applied/reverted history into the retraction.

Minor: the retraction table's `items` column reads `581` for the indexed row; with an index the items go 581 → **584**. Only the `blocking` transition is shown.


## Re-review findings applied 2026-08-20 — and the numbers no longer reproduce

The second pass's three findings are fixed:

- `## Measured before recommending it` and `## Applied 2026-08-20` now carry **their own** superseded banner in their first line. The collective banner above them was not enough: **a heading is a landing target**, and a reader arriving by link or scroll never sees a warning further up. The second also sat under *"the original measurement"*, which it is not.
- The retraction table's `items` column showed only the starting value where `blocking` showed a transition. Now **581 → 584**, matching.

### The measurement no longer reproduces, and that is a finding rather than a correction

Re-simulated today on a throwaway copy with an **indexed** loader — the instrument whose absence caused this issue:

```
BEFORE items=625 blocking=103
AFTER  items=628 blocking=106      (relevelling the same three notes)
```

**The +3 transition reproduces exactly** — three notes relevelled, three items, three blocking — so the reviewer's finding about the table is right and the fix stands.

**The absolute numbers do not.** The note records 581 / 59; `your-trainer`'s working tree now measures **625 / 103**, a difference of **+44 in both columns**. That tree carries **692 modified files**.

So 581 / 59 was a true measurement of a corpus that no longer exists on that disk, and this note's figures — like [[FEAT-0131]]'s — describe a basis that has moved underneath them. **No attempt is made here to explain the 44**: identical deltas in both columns suggest 44 notes became acceptance-level and all of them block, but that is a hypothesis, and this phase has been burned four times by hypotheses stated as measurements.

Recorded rather than corrected, because writing `625` into the table would replace one basis-less number with another. **What the table needs is a basis, and what the repo needs is a commit** — the same conclusion FEAT-0131 reached from the other end.


## Deferred and re-homed to [[PHASE-999]], 2026-08-21

**The finding was this phase's. The remaining action is not.**

[[PHASE-037]]'s subject is *a surface answering the question its reader did not ask*, and this issue's finding is exactly that: a reader sees five acceptance tests in a flat list and 579 under tiers, with nothing on screen explaining the difference, and the answer is a frontmatter field neither list mentions. That was answered — [[TASK-0506]] and [[TASK-0507]] under [[FEAT-0127]], now `done`.

What is left is **three lines of data in another repo**, and every one of them waits on somebody who is not this phase:

1. **Relevelling `TST-0011`/`TST-0012` costs three blocking checks** in `your-trainer`'s gate. The judgement that they *are* acceptance checks is made and recorded above. Whether to pay that is Edwin's, on his repo.
2. **`TST-0013` must be split before it is relevelled** — 107 checkbox rows behind one blocking check is the document-suite shape [[PHASE-035]] migrated away from. That is a migration, not a field edit.
3. **The numbers in this note no longer reproduce and the repo is not committed.** 581/59 was a true measurement of a corpus that no longer exists on that disk; the working tree measures 625/103 against 692 modified files, and `git log --all -- 'docs/surfaces/*'` returns nothing there. *"What the table needs is a basis and what the repo needs is a commit"* — and the commit is not this repo's to make.

`deferred` alone would not resolve it: STATUSES.md is explicit that a deferred child does not clear its phase, and that the relationship rather than the status word must record where the work went. So `phase:` moves to [[PHASE-999]] and the issue is parked there with its judgement intact.

**Nothing here is closed over.** The reasoning table stands, the retraction stands, and the three notes remain at `level: system` in `your-trainer`, clean against its HEAD.
