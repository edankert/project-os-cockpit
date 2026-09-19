---
type: "[[issue]]"
id: ISS-0258
aliases: ["ISS-0258"]
title: "A release can derive what it built and not what it broke — `features:` reaches the additive checks, and the invalidation leg has no field to travel along"
status: open
owner: user:edwin
created: 2026-08-29
updated: "2026-09-19"
severity: medium
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[TASK-0586-Your-Trainer-Scopes-Its-Release]]"]
reported_by: agent
question: "Should a release derive the checks its changes may have broken (a design for linking checks to source paths, then a release computing overlap from its diff), or should ADR-0040 record that a release derives only what it built and the hand-written table stays? Recommendation: record it as a deliberate boundary of ADR-0040 now, and reopen as a feature only if a second release needs the table."
---

# A release derives what it built, not what it broke

[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] decided that a release selects its features and its acceptance checks follow that selection. [[FEAT-0142-A-Release-Says-What-Is-In-It]] built it. Measured against a real release for the first time on 2026-08-29 ([[TASK-0586-Your-Trainer-Scopes-Its-Release]]), it derives **13 of 32**.

`your-trainer`'s `REL-0013` needs 32 of its 625 acceptance checks. They come from three different relations:

| leg | count | the relation | derivable from `features:`? |
|---|---|---|---|
| authored for the feature, never walked | 13 | check `covers:` → feature → release `features:` | **yes** |
| invalidated by the diff | 15 | the changed files overlap the check's subject | no |
| invalidated by the toolchain move | 4 | targetSdk 36 changes window behaviour app-wide | no |

**`features:` answers "what did this release build?". Nineteen of the thirty-two answer "what did this release break?"** — checks whose subject the diff overlaps without this release owning the feature they cover. `TST-0065` "Device-Wide License" is the clearest: nothing in `REL-0013` *builds* it, and the release contradicts it outright, because PRO became a single seat.

That relation runs through `area:` (this repo has 16 of them) and through which files the diff touched. **No field on either note carries it**, so no query can. The hand-written table in `REL-0013` is not laziness; it is the only place that information exists.

## Why this is not "just add a field"

The obvious move — `invalidates:` on the release — is the hand-written table with YAML syntax. The relation is *file paths → check subject*, and the release note is the wrong end to author it from: it changes with every diff, and a person maintaining it by hand is doing the same work with more ceremony.

[[FEAT-0138-Coverage-Is-Observed-Not-Declared]] is the shape that worked for the adjacent problem: the *test* declares what it covers, and a run emits the fact, so a stale declaration cannot survive. The analogue here would be the check declaring the source it is about — paths, or a `[[SUR-####]]` surface — and the release computing the overlap from its own diff. That is a design question, not a field.

## Done when

- [ ] A release can state its check scope from the note without a hand-written table, or the limit is recorded as a deliberate boundary of [[ADR-0040]] rather than a gap.

## Checked against the code, 2026-09-19: a question for Edwin

**What a user notices:** a release page can list the checks for the features the release built, but not the checks its changes may have broken. Someone preparing a release still has to write that second list by hand in the release note.

Evidence: `src/project_os_cockpit/publication.py:711-718` is the only reader of `invalidated_by:`, and it serves the feature panel, not the release scope. Its comment says the field is "Empty in every repo today". In `../your-trainer`, 658 check notes carry `invalidated_by: {}`, all empty. Nothing in `release_payload` (`publication.py:1286` onward) derives checks from a release's diff or from `area:`.

**Belongs to:** FEAT-0142 (A release says what is in it) and ADR-0040. **Next:** Edwin decides between a design for "what did this release break" and a recorded boundary in ADR-0040.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
