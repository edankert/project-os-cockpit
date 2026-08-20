---
type: "[[task]]"
id: TASK-0557
aliases: ["TASK-0557"]
title: "One preparing release per platform — `preparing()` returns one per platform, not one overall"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The decision, made operational

Edwin, 2026-08-19: *"Let's consider one release at the time only, multiple releases should use git branches anyway. We can potentially have multiple releases going on at the same time for different platforms."*

**Two concurrent releases on one platform are a branch, not a schema problem.** That decision is what keeps [[ADR-0037]]'s ledger intact: one working ledger per platform, and sealing assigns it to a release. If two releases were preparing on one platform, a verdict recorded today would belong to neither by construction.

## Definition of Done

- [x] `publication.preparing_by_platform()` returns the mapping; `preparing()` stays as the thin wrapper.
- [x] `RELEASE-PREPARING` — a validator **error**, in both copies.
- [x] A release with no `platform:` is keyed under `""` — the platform-less world every repo but `your-trainer` lives in.
- [x] Consumers read. All three call it where exactly one release is preparing, so *the* and *a* coincide and none needed changing; the wrapper keeps them correct while they move one at a time.

## Notes

Roughly six call sites. The single-value form should stay as a thin wrapper so they move one at a time — a rename that touches every consumer in one commit is how the last three regressions in this phase were introduced.

## Done 2026-08-20

`preparing_by_platform()` and `preparing_conflicts()` in `publication.py`; `RELEASE-PREPARING` as a validator **error** in both copies. `preparing()` is unchanged in behaviour — `REL-0013` in `your-trainer`, `None` here — because the wrapper picks from the same order `open_releases` already establishes.

**No conflict exists in the fleet today**, so every guard is on constructed input. Seven tests, three mutants run: ignoring the `preparing:` field, ignoring the overtaken-version rule, and collapsing every platform to one key.

### The rule is narrower than `draft`, twice over

**`preparing:` is frontmatter, not a status** (FEAT-0105 / TASK-0438) — `STATUSES.md` allows a release only draft / released / reverted and is template-owned. The first cut of the validator rule keyed on `status: draft` alone, which would have made **the validator and `publication.preparing` disagree about what *preparing* means** — [[REQ-0059]]'s one-question-two-implementations, and the third instance found in this phase after `_covers_an_issue` and `_verdict_is_owed`. Two open drafts nobody has declared for ship are an ordinary repo, not an error. Both now read the field, and a test asserts they agree.

**And a draft a shipped version overtook is not preparing.** `your-trainer` carries `REL-0008` at `draft`, version 2.0.2, with 2.1.6 shipped. Counting it would report a conflict that is not one — that exact corpus shape is a fixture.

### One predicate restated, and held to the original

The validator is stdlib-only and copied whole into every downstream repo, so it cannot import the package: `_release_version_key` restates `publication._version_key`. That is the same deliberate duplication `_acceptance_is_settled` and the command-target parser carry — and, like them, it now has a test holding the two to the same answers across seven inputs, because two copies of a predicate with nothing binding them is exactly what [[REQ-0059]] forbids.

### The fixtures were wrong first

They omitted `preparing:` entirely, so `preparing()` returned `None` and two assertions failed for a reason with nothing to do with platforms. A `draft` alone is *open*, not *prepared for ship* — the distinction this function's own docstring opens with, and I did not read it before writing the fixture.
