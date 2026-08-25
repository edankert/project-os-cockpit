---
type: "[[issue]]"
id: ISS-0256
aliases: ["ISS-0256"]
title: "The `observed-coverage` suite had never run anywhere but Edwin's machine — eight failures on its first CI run, every one a dependency on that machine"
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

`observed-coverage` failed on 2026-08-25, on its **first execution ever**. The workflow shipped inside the 197 commits this repo had accumulated without a push, so nothing had run it on a machine that was not Edwin's. **Eight failures**, and every one depends on something true only here: a newer interpreter, the fleet at `~/Dev/repos`, the upstream template repo, or a built Electron renderer.

*(The first fix pass addressed four of the eight. The other four were in the same CI log and were missed because the log was read through a `grep` window rather than from its `short test summary info` — the summary exists precisely so nobody has to guess where the list ends. Recorded because it is the same failure mode as the issue itself: trusting a partial view of a machine you are not standing on.)*

`validate-docs` passed in the same push, and `validate-docs.sh --as-committed` passed locally beforehand — so the repo's own defence against this class (LIFECYCLE steps 8–9) ran and did not see any of it. That is worth recording: `--as-committed` materialises `HEAD`, which catches *ignored and untracked* files, and none of these eight is that. It runs the local interpreter, on the local machine, with the fleet beside it and the renderer already built.

## The eight failures, by cause

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

**4. A guard asserting against the built renderer, with nothing built.** `test_digest_watermark.py` reads `desktop/dist/renderer/renderer.js` — deliberately the *bundle* and not the source, because a source assertion "could pass forever while the screen lied". `desktop/dist` is gitignored and CI never ran `npm run build`.

**5 and 6. Three guards asserting that a rule or a template landed upstream first.** `test_feature_uncovered.py` (×2) and `test_surface_type.py` read `~/Dev/repos/project-os` — the template repo, which on this machine sits beside its downstreams and on a runner does not exist at all.

**7 and 8. Two fleet-integration guards.** `test_tests_view.py` (×2) walk every reachable repo's surfaces, and their own docstring says why: *"this was invisible in the one it was written in… It was live in `your-trainer` from the first commit."* A runner has no fleet.

## Expected

`observed-coverage` passes on a clean runner.

## Actual

Eight failures, none reproducible here, on a workflow whose first run came 13 days after its code landed.

## Fix

[[TASK-0578]]. The principle throughout: **give the runner what the assertion needs**, and weaken an assertion only when supplying it would need a credential.

| # | Fix | Register |
|---|---|---|
| 1 | Hoist the nested f-string out of the expression | code |
| 2 | Anchor the marks guard on this repo's own `docs/`; fleet repos enrich | fixture |
| 3 | `fetch-depth: 0` on the checkout | environment |
| 4 | `setup-node` + `npm ci && npm run build` before the suite | environment |
| 5–6 | Check out the **public** `edankert/project-os` into `~/Dev/repos/project-os` | environment |
| 7–8 | Skip, with a reason naming what is missing | **weakened** |

Only 7–8 lose anything, and only because `your-trainer` and `your-sudoku` are **private**: a runner cannot clone them without a credential, and configuring one is not a change to make on someone's behalf. They now *skip with a stated reason* rather than fail — never quietly pass. Making them real in CI needs a deploy key or PAT as a repository secret; that is Edwin's call, and it is the only outstanding piece.

[[TST-0079]] guards cause 1, the only one that is *silent*: a version-conditional syntax error is invisible to every check running on a newer interpreter, `--as-committed` included.

## Evidence

- CI run 32893050702, `observed-coverage`, 2026-08-25T20:02:45Z — the first run; and 32895669686, which cleared causes 1–3 and showed the rest.
- `.github/workflows/observed-coverage.yml:41` — `python-version: "3.11"`; `pyproject.toml:10` — `requires-python = ">=3.11"`.
- Local interpreter: 3.13.13; no 3.11 is installed here, which shapes [[TST-0079]] into two halves — `compile()` where the floor runs, a token scan where it does not.
- `gh repo view`: `edankert/project-os` is **public**, `your-trainer` and `your-sudoku` are **private**. That single fact decides which failures could be fixed properly and which had to be weakened.
