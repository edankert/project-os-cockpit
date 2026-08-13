---
type: "[[issue]]"
id: ISS-0130
aliases: ["ISS-0130"]
title: "Nine automated acceptance tests declare no entrypoint, so release verification cannot re-run them — the step that exists to catch stale evidence is the step that cannot reach them"
status: open
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-13
source: ["REL-0001 release verification, 2026-08-10 — running tools/skills/release-verification/SKILL.md step 7 against the corpus"]
severity: medium
component: "docs-system"
parent: ""
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]"]
tests: []
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
- [ ] Consider a validator check: an `automated` test at `passing` with no `command` cannot be re-verified, which is a warning of the [[ADR-0011]] shape rather than an error
- [ ] Re-run the nine and stamp them, closing the gap the verification opened

## Re-homed — 2026-08-13, out of [[PHASE-030]]

[[PHASE-030]] closed and this was still open, so it had to be resolved or re-homed. It is re-homed, because it was never this phase's work: the phase's subject is *what needs a person and where it surfaces*, and this is about whether a machine can re-run a test. It landed here because its neighbours did — it was found by the release-verification pass over [[REL-0001]] while [[FEAT-0086]] was building the Tests view, and [[TASK-0373]] built the tier suite it complains about.

**Nothing currently schedules it**, which is what [[PHASE-999]] means, and saying so is more honest than parking it under a phase that has finished. The work is unchanged and still worth doing: nine automated tests that run green in `pytest -q` cannot say how, so the gate that exists to catch stale evidence cannot refresh them.
