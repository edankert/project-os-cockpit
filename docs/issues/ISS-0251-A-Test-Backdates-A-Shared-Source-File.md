---
type: "[[issue]]"
id: ISS-0251
aliases: ["ISS-0251"]
title: "A freshness test forward-dates a real source file in the working tree, so any other process running the suite at the same time gets a false staleness failure — the exact class of false bug report that test file exists to prevent"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["hit while running the suite alongside an independent-review agent, 2026-08-20"]
severity: low
component: tests
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0140-The-Shell-Goes-Stale-Silently]]"]
tests: []
---

# The test mutates the thing every other reader is reading

## Problem

`tests/test_runtime_freshness.py::test_source_newer_than_the_process_reads_as_stale` sets the mtime of the **real** `src/project_os_cockpit/cockpit.py` five seconds into the future, asserts the endpoint reports stale, then restores it:

```python
victim = Path(project_os_cockpit.__file__).resolve().parent / "cockpit.py"
before = victim.stat().st_mtime
future = time.time() + 5
os.utime(victim, (future, future))
```

The window is milliseconds and the restore is in a `finally`, so within one process it is safe. **Across processes it is not.** `/api/cockpit/runtime` computes staleness by comparing the process start against the newest `.py` in the package, so for the length of that window *every* running sidecar in this working tree reports stale — including the one `test_a_fresh_process_is_not_stale` has just spun up in a different pytest process.

**And the failure is a lie about staleness**, which is precisely what `ISS-0140` and that test file exist to remove. Its own docstring: *"Both times the expensive part was investigating a defect that did not exist."* It cost exactly that again today — two red tests in a 1977-test run, both passing in isolation, in a repo where a red suite is a stop signal.

## Repro

Executed 2026-08-20:

```
$ python -c "os.utime('src/project_os_cockpit/cockpit.py', (time.time()+5,)*2)"
$ .venv/bin/python -m pytest -q tests/test_runtime_freshness.py::test_a_fresh_process_is_not_stale
1 failed in 0.65s
$ # mtime restored
$ .venv/bin/python -m pytest -q tests/test_runtime_freshness.py::test_a_fresh_process_is_not_stale
1 passed in 0.64s
```

Three concurrent runs of the file alone did **not** reproduce it — they align in lockstep and their windows coincide. It appeared when a full-suite run overlapped a second full-suite run started at a different moment, which is what an independent-review agent does.

## Expected

Running the suite twice at once in one working tree gives the same answer as running it once.

## Actual

`test_a_fresh_process_is_not_stale` fails in the process that did not do the mutating, and the message says the sidecar is stale.

## Evidence

- The two failures observed: `test_a_fresh_process_is_not_stale` and `test_source_newer_than_the_process_reads_as_stale`, 2026-08-20, in a run overlapping a second suite. Both pass in isolation, immediately.
- The mechanism reproduced by hand, above — the collision needs no concurrency to demonstrate, only the mtime.

## Next Actions

- [ ] Decide the shape. The test's own reasoning is sound and should be preserved — *"what is asserted is a comparison between a process and a filesystem; mocking either side would test the arithmetic rather than the question."* So do not mock it. Two candidates that keep a real comparison:
  - **A file the test owns.** Write a throwaway `.py` into the package directory instead of touching `cockpit.py`, and delete it. Still shared, but the window belongs to a file nothing else asserts about — and a leftover is visible rather than silent.
  - **A staleness root the test can point somewhere else.** If the freshness scan took its package root as an argument, the test could build a temp package tree and the comparison would stay real while the blast radius became the temp directory.
- [ ] Whichever is chosen, **run two suites at once and watch it not fail** — the property is about concurrency, so a single-process pass proves nothing about it.


## Fixed 2026-08-20 — by moving the other side of the comparison

The staleness predicate is `newest .py under the package > this process's start`. **It has two sides and only one of them is shared.**

The test now moves `_PROCESS_STARTED_AT` — module state, private to this process — instead of the file's mtime. It exercises the identical predicate, in both directions (`0.0` → stale, `now + 60` → clear), and mutates nothing another reader can see. No `tmp_path` copy of the package was needed and no production signature changed.

The obvious repair — keep forward-dating the file, restore it faster — was rejected: it narrows the window without closing it, and a race that fires rarely is worse than one that fires often.

### Guarded, and the guard was wrong first

`test_the_freshness_test_does_not_touch_a_shared_file` asserts **no test in this file sets an mtime at all**, which is the property that matters given the file's subject.

Its first cut searched the source **text** for `os.utime(` and failed immediately — matching **its own docstring and its own assertion string**. That is the eighth over-broad text match this phase, and the second in which a guard was satisfied, or in this case defeated, by the prose explaining it.

It parses with `ast` now and looks for real call sites, which cannot see a mention.

### Both mutants executed

| mutant | result |
|---|---|
| reintroduce `os.utime` on a shared path | guard **fails** |
| `"sidecar_stale": False` in `server.py` | staleness test **fails** |

Run with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`, because same-second edits of equal length reuse the previous mutant's bytecode and report false catches — the failure mode that invalidated several earlier mutation results in this phase.
