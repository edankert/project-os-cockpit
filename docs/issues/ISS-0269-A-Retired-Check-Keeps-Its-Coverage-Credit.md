---
type: "[[issue]]"
id: ISS-0269
aliases: ["ISS-0269"]
title: "A retired check sheds the obligation and keeps the credit — `acceptance.load` drops it and the validator still counts it as covering its feature, so the two now disagree about what is verified"
status: open
owner: user:edwin
created: 2026-08-30
updated: "2026-09-27"
severity: medium
component: tooling
phase:
source: ["Independent review of 46d6593..c861414, 2026-08-30, model:claude-opus-5, fresh context"]
related: ["[[ISS-0265-A-Retired-Check-Still-Gates-The-Release]]", "[[TASK-0591-Retiring-Removes-The-Obligation]]", "[[FEAT-0143-The-Fleet-Runs-One-Validator]]"]
tests: []
reported_by: review
question: "Does a retired acceptance check still count as covering its feature? Options: (a) no, so the validator skips retired checks in `_features_covered_by_acceptance` and the feature is reported uncovered, matching the cockpit; (b) yes, so the cockpit shows retired checks as coverage. Recommendation: (a), fixed in the template's validator."
---

# One filter, and the second reader is in another file

## What happened

[[ISS-0265]] puts the retired filter in `acceptance.load` and gives the reason: the gate, the tiers and the facets all read `Suite.items`, and *"three filters is how two of them come to disagree ([[REQ-0059]])"*. That reasoning is right and the placement is right **within the package**. It is not the whole population of readers.

`tools/scripts/validate-docs.py` answers the same question from the notes directly and knows nothing about `status: retired`:

```python
>>> ni = {"TST-0001": ("x.md", {"level": "acceptance", "status": "retired",
...                             "covers": ["[[FEAT-0001]]"]})}
>>> vd._features_covered_by_acceptance(ni)
{'FEAT-0001'}
```

`grep -n retired tools/scripts/validate-docs.py` finds the value only in status vocabularies; no rule excludes it. So after this change a check that has left the release test still:

- satisfies `FEATURE-UNCOVERED` / `VERIFY-ACCEPTANCE` for the feature it is no longer tested for — retiring removes the obligation *and keeps the coverage credit*, which is the opposite of what a reader would predict from the note's own framing;
- fires `SURFACE-ORPHAN` when its `area:` names no surface, for a check nobody will ever test again;
- makes `_repo_has_an_acceptance_suite` true in a repo whose every check is retired, so the uncovered-feature rule keeps firing over an empty suite.

Meanwhile `publication.py`'s feature panel (*"which checks does this feature answer for"*) and `cockpit.py`'s per-surface counts both read `Suite.items`, so the cockpit says the feature has no checks while the validator says it is covered.

This matters more than a normal two-readers case because that validator is the artifact [[FEAT-0143]] just copied into four fleet repos: the disagreement ships everywhere the gate does.

## Two smaller consequences worth a decision, not necessarily a change

- **A shipped release's reported confidence moves.** `publication._confidence` is computed from the live suite for shipped releases too, so retiring a check retroactively changes the numbers on a sealed release page — in tension with `ADR-0035`, which `tests/test_release_contents.py` cites two tests earlier.
- **A retired check is no longer visible anywhere in the suite surfaces.** The note is still browsable as a document, which is probably enough; it is worth stating deliberately rather than discovering.

## Next Actions

- [ ] Decide whether a retired check covers its feature. Either answer is defensible; two answers is not.
- [ ] Whichever way it goes, put it in one place and have the other read it — the same argument ISS-0265 used for `Suite.items`, applied across the package/validator boundary.

## Checked against the code, 2026-09-19: a question for Edwin

**What a user notices:** after a check is retired, the cockpit's feature panel shows the feature has no checks, while `validate-docs.sh` still counts the retired check as covering it. So the "feature has no acceptance check" warning stays silent.

Evidence: `tools/scripts/validate-docs.py:602-621` (`_features_covered_by_acceptance`) filters on `level: acceptance` only and never reads `status`. `grep -n retired` in that file finds the word only in status vocabularies. The cockpit's side filters retired checks out (`src/project_os_cockpit/acceptance.py:1029-1045`, `_is_retired`). The validator is byte-identical to the template's, so the fix belongs upstream.

**Belongs to:** no cockpit feature; the fix is in the template's validator (project-os). **Next:** Edwin answers the question, then one change in the template makes the validator and the cockpit agree.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
