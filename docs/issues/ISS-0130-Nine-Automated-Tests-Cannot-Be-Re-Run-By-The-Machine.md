---
type: "[[issue]]"
id: ISS-0130
aliases: ["ISS-0130"]
title: "Nine automated acceptance tests declare no entrypoint, so release verification cannot re-run them — the step that exists to catch stale evidence is the step that cannot reach them"
status: fixed
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-08-10
updated: "2026-08-13"
source: ["REL-0001 release verification, 2026-08-10 — running tools/skills/release-verification/SKILL.md step 7 against the corpus"]
severity: medium
component: "docs-system"
parent: ""
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# Nine automated tests cannot be re-run by the machine

## How this was found

Running the release-verification skill against [[REL-0001]], step 7: *"If `kind: automated` and `entrypoint` is set: run the entrypoint command and capture the result."*

Measured across the 23 `TST-*` notes in this repo:

| how the entrypoint is declared | count |
|---|---|
| `command:` in frontmatter | **1** (TST-0022) |
| a `pytest` line in a `## Running it` section | 5 |
| `path:` in frontmatter, resolvable to a module | 7 |
| **nothing at all** | **10** |

Of the ten, **TST-0011 is genuinely manual** and correctly has no command. The other **nine are automated pytest modules** — TST-0010, TST-0012 through TST-0018, and TST-0023 — every one of which runs green in `pytest -q` today, and none of which says how.

## Why it matters, precisely

The release gate's job is to catch **stale evidence**: a test that passed in May against code that changed in August. The skill's verdict table calls that `STALE` and step 7 re-runs it.

A test with no entrypoint cannot be re-run, so it can never move from `STALE` back to `CURRENT` by machine. Its `status: passing` and its `last_verified` date are then a claim nobody can refresh without first reverse-engineering which module verifies it — which is [[ISS-0066]]'s complaint (registers drifting by hand) one level down.

Nine of them carry dates between 2026-07-05 and 2026-08-02, against a codebase that changed substantially on 2026-08-10. They pass. Nothing here says they do not. The defect is that **the record cannot demonstrate it**, and the release verification is exactly the moment that distinction is supposed to bite.

## Not a gap: the three declaration styles

Three ways to say the same thing — `command:`, `path:`, and prose in `## Running it` — is itself worth fixing, and the resolver written for this run had to accept all three. `command:` is the one the template intends and the one `_is_manual_test` already treats as decisive ([[TASK-0371]]). The other two should converge on it.

## Next Actions

- [ ] Add `command:` to the nine automated notes that have none, resolving each to the module that actually verifies it
- [ ] Converge the three declaration styles on `command:`, leaving `path:` as documentation rather than an entrypoint
- [ ] Consider a validator check: an `automated` test at `passing` with no `command` cannot be re-verified, which is a warning of the [[project-os-dev#ADR-0011]] shape rather than an error
- [ ] Re-run the nine and stamp them, closing the gap the verification opened

## Re-homed — 2026-08-13, out of [[PHASE-030]]

[[PHASE-030]] closed and this was still open, so it had to be resolved or re-homed. It is re-homed, because it was never this phase's work: the phase's subject is *what needs a person and where it surfaces*, and this is about whether a machine can re-run a test. It landed here because its neighbours did — it was found by the release-verification pass over [[REL-0001]] while [[FEAT-0086]] was building the Tests view, and [[TASK-0373]] built the tier suite it complains about.

**Nothing currently schedules it**, which is what [[PHASE-999]] means, and saying so is more honest than parking it under a phase that has finished. The work is unchanged and still worth doing: nine automated tests that run green in `pytest -q` cannot say how, so the gate that exists to catch stale evidence cannot refresh them.

## Fixed — 2026-08-13

**Every non-manual test now declares its entrypoint, and the runner wrote every status.**

The measurement this note opened with was right about the shape and low about the size. It counted nine automated notes with nothing at all; the honest count is that **1 of 24 test notes carried a `command:`** — TST-0022, its own. Eleven declared `kind: automated` and no way to run. Ten more named their module in `path:` or in prose, neither of which `tools/scripts/run-tests.py` reads, so from the runner's side they were identical to the nine that said nothing.

| | before | after |
|---|---|---|
| notes carrying `command:` | 1 | 22 |
| automated notes the runner can execute | 1 | 22 |
| statuses written by a person | 22 | 0 |
| genuinely manual, correctly exempt | — | 2 |

### The statuses were not typed in, which is the whole point

`command:` was resolved for each note from **what that note already claimed** — its `path:` frontmatter or its `## Running it` prose — and then `run-tests.py --write` executed all 22 and stamped `status`, `last_run` and `exit_code` from the exit code. Per [[ADR-0010]] that is the only hand a status may be written by, and it is why this could not have been done by editing frontmatter: adding `command:` to a note flips it from manual to executable, at which point `TEST-FIELDS` requires a `last_run` the runner alone may supply.

```
passing=22  failing=0  unrunnable=0
```

**All 22 pass, and nothing here was ever broken.** That is the finding, not a disappointment: the claims were true and the record could not demonstrate them. Nine notes carried `last_verified` dates between 2026-07-05 and 2026-08-02 against a codebase that changed substantially on 2026-08-10, and no machine could have told you whether they still held.

### Two exemptions, both narrow and both named

`TST-0011` (live session instrumentation) and `TST-0024` (the remote-SSH walk for [[PHASE-033]]) are procedures a person performs. TST-0024 *cannot* be automated because the thing it walks is not built. Both keep `kind: manual` and no `command:`, and `test_the_known_manual_tests_stay_exempt` names them so a future sweep cannot hand them a fake entrypoint to satisfy the guard.

### The three declaration styles converged

`command:` is now the entrypoint and `path:` is documentation, which is what this note's *"Not a gap"* section asked for. `path:` was left in place rather than deleted — it is the human-readable answer to *"where does this live"*, and several notes use it to name more modules than the command runs.

### The check the note wanted, in the place it can live

The fourth action proposed a validator check. `tools/scripts/validate-docs.py` is **template-owned** and a downstream edit would be reported as divergence by the next sync, so the guard is `tests/test_test_entrypoints.py` instead — this repo's own suite, which gates pre-commit through the same run. Four guards, each mutation-checked against the defect it describes:

| guard | mutation | result |
|---|---|---|
| `test_every_automated_test_declares_an_entrypoint` | TST-0001 loses its `command:` — the pre-fix state | fails |
| `test_every_declared_entrypoint_names_files_that_exist` | an entrypoint names a moved module | fails |
| `test_a_manual_test_is_left_manual` | a note is exempt by omission rather than by saying so | fails |
| `test_the_known_manual_tests_stay_exempt` | TST-0011 is handed an entrypoint it cannot honour | fails |

The first keys off `cockpit._is_manual_test` rather than re-reading `kind:` itself, deliberately: a note the *product* calls automated and the *runner* cannot execute is exactly the disagreement worth failing on, and a second reading of the same field is how two answers drift apart. That is [[ISS-0066]]'s lesson, which this note called its own one level down.

### The sweep broke the freshness rule, and the sweep is what exposed it

Making 22 notes executable left every one of them carrying a `last_verified` from weeks earlier, beside a `last_run` from minutes earlier. `cockpit._test_last_verified` read `last_verified` **first, unconditionally**, so all 22 displayed the hand-typed date. The oldest was 2026-07-05 — 39 days, on a test that had just run green, climbing toward a 90-day threshold that would have called it stale while it passed daily.

The precedence was correct when written and its docstring says why: *"22 of 23 tests here carry `last_verified`… TST-0022 carries only `last_run`."* This issue inverted that population in one afternoon. Latent until today, because the one note with both fields had the same date in each.

Fixed by making the order depend on the kind rather than fixing the 22 notes: an **executable** test reads `last_run` first, because [[ADR-0010]] makes the runner the only hand that may write its status, so the runner's date is the only one describing what is on the note; a **manual** test reads `last_verified` first, because nothing runs it and the typed date is the whole record. The other field stays as fallback either way, so a note carrying one is never reported unverified.

Two more guards, both mutation-checked against restoring the unconditional order: `test_an_executable_test_reports_its_run_not_an_older_typed_date` and `test_a_manual_test_still_reports_its_typed_date`.

**Still true and still worth proposing upstream**: the validator check belongs in the template, so all twelve repos get it rather than this one. Filed as [[ISS-0163]].
