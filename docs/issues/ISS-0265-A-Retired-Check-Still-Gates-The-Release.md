---
type: "[[issue]]"
id: ISS-0265
aliases: ["ISS-0265"]
title: "Retiring a check changes nothing — `status: retired` is written and never read, so the check keeps its row in the mark filters and goes on blocking the release"
status: fixed
owner: user:edwin
created: 2026-08-30
updated: 2026-08-30
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
severity: high
component: server
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
fixed_in: "[[TASK-0591-Retiring-Removes-The-Obligation]]"
source: ["Edwin, 2026-08-30: 'I still see TST-75 in the unclear list.' and 'A Retired check should not hold/gate the release.'"]
related: ["[[ISS-0249-The-Lever-That-Had-No-Handle]]", "[[ISS-0264-A-Write-Is-Not-Readable-By-The-Next-Request]]"]
---

# Retiring reported success and changed no outcome

## What happened

`../your-trainer` retired `TST-0075` through the write path, with a reason. The note was written correctly — `status: retired`, the verdict and its date preserved, the reason appended.

And nothing changed. The check kept its row under the **`unclear`** mark filter, stayed in the tier counts, and **went on blocking the release** — 104 blocking, `TST-0075` among them.

## Cause

`retire_check` has written `status: retired` since [[ISS-0249]]. `Item.status` is parsed and carries a comment naming the lifecycle — *"`draft` / `active` / `retired` — the LIFECYCLE. Never the verdict."* — and **no consumer ever read it**. Not `Suite.blocking`, not the tier grouping, not the facets.

So the lever [[ISS-0249]] built a handle for still did nothing at the end a reader can see. That is worse than an absent button: a control that reports success and changes no outcome teaches people to distrust the ones that work.

## The rule

Edwin, on being shown it: *"A Retired check should not hold/gate the release."*

`TESTING.md` already says the first half — *"Nothing removes a check. A check whose subject is gone goes `retired`"* — and the note is kept deliberately, because its `mark` and `verdict_date` are the record that the behaviour was once walked. That is the difference between retiring and deleting, and it stands.

**What must not survive is the obligation.** The record stays in the note; the row leaves the walk.

## Fix

One filter, in `acceptance.load`, dropping retired items before the `Suite` is built — rather than in each consumer, because the gate, the tiers and the facets all read `Suite.items` and three filters is how two of them come to disagree ([[REQ-0059]]).

Guarded both ways. The first test fails with the filter removed; the second builds the **same note with `status: active`** and asserts it still blocks, so the filter must key on the lifecycle rather than on the verdict — both fixtures carry `mark: question`, and only the retired one leaves.

## Independent review, 2026-08-30 — changes-requested

The strongest-guarded change in the set: both fixtures kill their mutants on both branches of `load`, and keying the filter on `mark` instead of `status` fails the second test exactly as the note says it must. Two findings. [[ISS-0269]] — `Suite.items` is not the whole population of readers: `tools/scripts/validate-docs.py` counts a retired check as covering its feature and knows nothing about the status, so retiring now removes the obligation *and keeps the coverage credit*, and that validator is the artifact FEAT-0143 copied into four repos. [[ISS-0270]] — the blocking figure was 101, not the `104` published here and in two other places, and not TASK-0591's `103`; retiring one check cannot move the gate by three.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
