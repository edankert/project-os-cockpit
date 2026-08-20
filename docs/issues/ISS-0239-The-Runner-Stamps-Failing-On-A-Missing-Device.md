---
type: "[[issue]]"
id: ISS-0239
aliases: ["ISS-0239"]
title: "`run-tests.py` classifies `unrunnable` on exit 127 alone, so a missing device stamps `failing` — the exact conflation its own docstring exists to prevent, and it overwrote a green verdict"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
severity: high
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0010]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]"]
---

# The one case it was written to catch

Reproduced in `your-trainer`, 2026-08-19: running 67 automated checks with `--write` gave `passing=33 failing=36`. **All 36 "failures" were an absent device.**

```
> com.android.builder.testing.api.DeviceException: No connected devices!
BUILD FAILED in 1s
```

Its own module docstring names this:

> Stamping `failing` on a test that could not run conflates "the system is broken" with "my machine is missing a tool", and that is exactly the noise that teaches people to stop believing a status.

## Why it misses

Read at `tools/scripts/run-tests.py:107-115`. `unrunnable` is returned for exactly three things: a timeout, an `OSError`, and **exit code 127**.

```python
if proc.returncode == 127:
    return "unrunnable", 127, "command not found…"
return ("passing" if proc.returncode == 0 else "failing"), …
```

**127 is the shell's *command not found*.** Gradle is found, runs fine, and exits non-zero because the *device* is missing — so it falls to the `failing` branch. For any Android or iOS repo, instrumentation tests are the common case, not the edge one: the tool is present and the execution environment is not.

## The collateral, which is the worse half

`failing` **writes** — only `unrunnable` is skipped (`:143`). So the run flipped `TST-0017`, a pre-existing green note, from `passing` to `failing` and overwrote its `last_run`. **A non-result destroyed a real verdict**, and the newer timestamp made it look like the more current one.

## Suggested fix

1. **Classify as `unrunnable` when the runner cannot reach an execution environment.** `No connected devices!` is one signature; the general shape recurs for a missing simulator, an unreachable emulator and an absent API key, so a small pattern set beats a special case.
2. **And, independently of the classifier: never let a non-`passing` result overwrite an existing `passing` with a newer `last_run`.** Signature-matching will always be incomplete; this holds whatever it misses. A verdict is evidence, and a run that produced no evidence must not be able to delete one.

Rule 2 is the load-bearing half — 1 reduces how often the question arises, 2 makes the answer safe when it does.

## Done when

- [ ] A missing device is `unrunnable`, proved on the captured Gradle output.
- [ ] A non-result cannot overwrite a `passing` verdict, proved by a test that tries.

## Dissolved 2026-08-20, not fixed — [[ADR-0038]]

**There is no verdict in the note for a non-result to destroy.** `run-tests.py` reports and does not write: `fm_set` and the timestamp import are deleted, so the collateral this issue is really about cannot recur by any classifier's mistake. `tests/test_runner_writes_nothing.py` asserts the note is **byte-identical** after a run — not merely that `status` is unchanged, because stamping also wrote `last_run`, `exit_code` and `updated`, and a status-only guard would pass while three fields were still being rewritten.

**Suggested fix 2 is withdrawn.** *"Never let a non-`passing` result overwrite an existing `passing`"* reads well and, taken literally, blocks the runner from recording a genuine regression — which is the one thing [[project-os-dev#ADR-0010]] existed to do. Only `failing` ever had teeth against it, so the rule would have had exactly the effect of turning every real failure into a held write.

**Suggested fix 1 is still worth having and is not done.** A missing device landing in `failing` is now only a wrong line in a report, so it is a reporting defect rather than a data-loss one. A classifier was written this session and reverted on Edwin's instruction; the captured Gradle output and its 14 passing tests are in the session scratchpad if the report is worth correcting.

**One correction to this note's own account**: `TST-0017` in `your-trainer` still carries `exit_code: 1` and `updated: 2026-08-19` over a passing run, uncommitted. The migration ([[TASK-0562]]) removes both fields wherever it is executed there; it has not been executed against that repo's working tree because it carries other people's in-flight work.
