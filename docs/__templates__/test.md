---
type: "[[test]]"
id: TST-0000
title: ""
status: ready
owner: unassigned
created: 2026-01-27
updated: 2026-01-27
source: []
scope: feature
level: system       # unit | integration | system | e2e | acceptance — what it EXERCISES.
                    # Who RUNS it is `command:` below, and nothing else (ADR-0034).
entrypoint: ""
command: ""          # runnable check; when set, `status` is written by the runner, never by hand (ADR-0010)
last_verified: ""    # manual tests only (no `command:`) — date the procedure was last performed; goes stale
covers: []           # THE verification link (ADR-0032): [[FEAT-...]] / [[ISS-...]] / [[REQ-...]]. One direction, one encoding.
issues: []           # context only — what this test VERIFIES goes in covers:
tasks: []
artifacts: []
last_run: ""
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
# --- level: acceptance only (ADR-0031) ---------------------------------
# Delete these on an executable test; they are meaningless there.
# THE VERDICT IS NOT HERE (ADR-0037). It is a dated event in
# docs/releases/ledgers/<release>-<platform>.json — a verdict is a fact
# about (check x platform x release) and a field cannot hold three.
tier: ""             # 1 feature check · 2 regression check · 3 verification check for one build
area: ""             # the human grouping — one walk's worth of related checks
after: []            # optional: checks that should have passed before this one is walked; orders the walk sheet and gates nothing (tools/instructions/TESTING.md, "The walk", rule 4)
---

# <Test>

## Purpose
<What does this test verify?>

> **Status is evidence, not intent.** `ready` means defined but not yet executed — that is the state a new test note is created in. A test with a `command:` has its `status` written by `tools/scripts/run-tests.py` from the exit code; hand-editing it is a validator error. A test without one is manual: keep `last_verified:` current, because a stale manual test stops satisfying the verification gate.

<!-- level: acceptance ONLY — delete these four headings on any other test, and delete Procedure/Expected results below on an acceptance check. The shape and the reason are stated once in tools/instructions/TESTING.md, "A check is walkable by a stranger". -->

## Setup
<The state the walk needs, and *the cheapest way to reach it*. If a developer toggle, a mock, or a bundled fixture produces the state, name it. This is the line that decides whether the check ever gets walked.>

## Steps
1. <Numbered, one action each, in the order a person performs them.>

## Expect
- <What must be observable, one line per assertion, in the words the surface uses. A code symbol may follow the observable name; it may not replace it.>

## Not this check
- <The boundary. What a reader might reasonably think this covers, and which check actually covers it.>

<!-- end of the acceptance-only block. Provenance — where the check came from, what migration moved it, which audit split it out — goes BELOW the procedure under its own heading, or into frontmatter. It is about the note, not about the walk. -->

## Procedure
- <step-by-step>

## Expected results
- <observable outcomes>

## Evidence (fill after running)
- <paths/log excerpts/screenshots/etc>

## Adequacy (who verifies this test?)
- <For automated tests guarding a fix: evidence the test fails when the fix is reverted/broken (mutation result, revert-run, or reasoning). A test that cannot fail does not guard.>
