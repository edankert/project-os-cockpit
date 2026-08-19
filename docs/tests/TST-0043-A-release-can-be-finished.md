---
type: "[[test]]"
id: TST-0043
aliases: ["TST-0043"]
title: "A release can be finished — two refusals that name their subjects, a frozen list, and commands it does not run"
status: active
covers: ["[[FEAT-0116-A-Release-Can-Be-Finished]]"]
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
last_verified: 2026-08-17
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
scope: feature
automated: true
command: ".venv/bin/pytest tests/test_release_finish.py -q"
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# A release can be finished

Automated, in `tests/test_release_finish.py`.

`HUMAN_TRANSITIONS` had no `release` key, which is why nothing anywhere could take a release from `draft` to `released` ([[ISS-0181]] item 4).

## What it pins

**That both refusals fire and name their subjects.** "Something is not ready" is a refusal nobody can act on.

**That a documented exception clears the gate refusal** — the escape TESTING.md has always allowed and nothing ever implemented.

**That an EMPTY `features:` is frozen from the derived set.** This is REL-0013's exact state, on disk in `../your-trainer` today. The populated-list version of this test passes whether or not the freeze works, which is why a mutation removing it survived until this case was written.

**That it runs no git** — asserted by the write succeeding in a directory that is not a repo.

**That a prose `tests_verified` entry reads as a claim**, asserted on the payload as well as the renderer: a guard on the client branch alone survived a mutation making the flag always false.

## Adequacy

Five mutations; all killed. Two survived first (the freeze and the claim flag) and are named above.
