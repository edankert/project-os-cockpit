---
type: "[[issue]]"
id: ISS-0256
aliases: ["ISS-0256"]
title: "The `observed-coverage` suite had never run anywhere but Edwin's machine — its first CI run was red on three separate dependencies on that machine"
status: fixed
phase:
owner: user:edwin
created: 2026-08-25
updated: 2026-08-25
source: ["ci-failure"]
severity: high
component: tooling
parent: ""
related: ["[[ISS-0255]]", "[[TASK-0578]]"]
tests: ["[[TST-0079]]"]
---

# The suite had never run anywhere but here

## Problem

`observed-coverage` failed on 2026-08-25, on its **first execution ever**. The workflow shipped inside the 197 commits this repo had accumulated without a push, so nothing had run it on a machine that was not Edwin's. Three failures, three unrelated causes, one shared shape: each depends on something true only here.

`validate-docs` passed in the same push, and `validate-docs.sh --as-committed` passed locally beforehand — so the repo's own defence against this class (LIFECYCLE steps 8–9) ran and did not see any of it. That is worth recording: `--as-committed` materialises `HEAD`, which catches *ignored and untracked* files, and none of these three is that. It runs the local interpreter, on the local machine, with the fleet present.

## The three causes

**1. A Python 3.12-only f-string, in a script CI cannot parse.** `tools/scripts/migrate-acceptance-checks.py:169`:

```python
f"covers: [{', '.join(f'\"[[{r}]]\"' for r in item.refs)}]",
```

A backslash inside an f-string *expression* is legal only from Python 3.12 (PEP 701). CI pins `3.11`, and `pyproject.toml` says `requires-python = ">=3.11"` — so CI is right and the code is wrong. The script does not fail at the call; it fails to **parse**, so `test_check_migration.py` sees `returncode 1` with a `SyntaxError` on stderr, twice. Landed in c9d6a82 on 2026-08-21 and green here ever since, because this machine runs 3.13.

**2. A test that reads `~/Dev/repos`.** `test_acceptance_marks.py` walks the real fleet:

```python
fleet = _Path.home() / "Dev" / "repos"
for repo in ("project-os-cockpit", "your-sudoku", "your-trainer"):
```

A runner has no fleet, so `marks` is empty and the test's own anti-vacuity guard fires — `no suite reachable — this guard would pass vacuously`. The guard did exactly its job: it refused to pass on nothing. What was missing is a corpus it can always reach. This repo's own `docs/` holds 34 acceptance items, which is enough.

**3. A test that needs git history, against a shallow clone.** `test_change_shape.py::test_it_answers_for_this_repos_own_work` asks `change_shape_payload(REPO, "ISS-0135")`, which greps the log for the commit carrying that note. `actions/checkout@v4` clones at depth 1, so the commit is not there and the shape comes back with `files == 0`. The test is right to use the real corpus — its docstring says the fixture cannot exercise scale — so the *checkout* is what has to change.

## Expected

`observed-coverage` passes on a clean runner.

## Actual

Three failures, none reproducible here, on a workflow whose first run was 13 days after its code landed.

## Fix

[[TASK-0578]]:

1. Hoist the nested f-string out of the expression — no backslash, no nesting.
2. Anchor the marks guard on this repo's own `docs/`, keeping the fleet repos as an optional enrichment.
3. `fetch-depth: 0` on the `observe` job's checkout.

[[TST-0079]] guards cause 1, which is the only one of the three that is silent: a version-conditional *syntax* error is invisible to every check that runs on a newer interpreter, including `--as-committed`.

Causes 2 and 3 are not guarded by a new test, deliberately — both are now structural (the corpus is in-repo, the checkout is deep), and a test asserting "this test does not read `$HOME`" would be a lint rule wearing a test's clothing. The suite passing on CI is the check.

## Evidence

- CI run 32893050702, `observed-coverage`, 2026-08-25T20:02:45Z — 4 failures across 3 files.
- `.github/workflows/observed-coverage.yml:41` — `python-version: "3.11"`; `pyproject.toml:10` — `requires-python = ">=3.11"`.
- Local interpreter: 3.13.13. No 3.11 is installed on this machine, which is why a tokenizer-based guard replaces "compile it under the floor version" — see [[TST-0079]].
