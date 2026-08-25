---
type: "[[task]]"
id: TASK-0578
aliases: ["TASK-0578"]
title: "Make the `observed-coverage` suite runnable off this machine — a 3.11-legal f-string, an in-repo corpus for the marks guard, and a checkout deep enough to hold the history a test reads"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-25
updated: 2026-08-25
source: ["[[ISS-0256]]"]
parent: "FEAT-0138"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: ["[[TST-0079]]"]
---

# Make the suite runnable off this machine

## Definition of Done
- [x] `migrate-acceptance-checks.py` parses under Python 3.11.
- [x] `test_acceptance_marks.py` reaches a corpus that exists on a clean runner, and stays non-vacuous.
- [x] `test_change_shape.py::test_it_answers_for_this_repos_own_work` has the git history it reads.
- [ ] `observed-coverage` is green on GitHub. *(Unticked until the run says so — the whole issue is that this cannot be verified from here.)*

## Steps
- [x] Hoist the nested f-string out of the expression at `migrate-acceptance-checks.py:169`.
- [x] Anchor the marks guard on this repo's own `docs/`; keep the fleet repos as enrichment.
- [x] `fetch-depth: 0` on the `observe` job's checkout.
- [x] Add [[TST-0079]] — the only one of the three that is otherwise silent.

## Evidence

Each fix was verified **under the condition that broke it**, because all three passed locally before and after — local green was never the question.

- **f-string** — a tokenizer scan calibrated against the offending line reports the repo clean; reinstating the line makes [[TST-0079]] fail.
- **Marks guard** — run with `HOME` pointed at an empty directory (no fleet, as on a runner): the pre-fix version fails exactly as CI did, the fix passes 38/38.
- **Shallow clone** — `change_shape_payload(root, "ISS-0135")` against a real `--depth 1` clone returns `files=0`, which is CI's `assert 0 > 0`; against a full clone, `files=14`.

## Notes

Homed under [[FEAT-0138]] because the subject is that feature's workflow, not because all three defects belong to it — the f-string is [[FEAT-0113]]'s migration script and the shape test is ISS-0135's. What they have in common is the run, and the run is FEAT-0138's.

The three are deliberately fixed in three different registers: the f-string is a **code** defect (the repo claims `>=3.11` and this is not 3.11), the marks guard is a **fixture** defect (it reached for a corpus that is not universally there), and the shallow clone is an **environment** defect (the test is right, the checkout was wrong). Only the first gets a regression test; see [[ISS-0256]] for why the other two do not.
