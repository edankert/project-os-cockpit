---
type: "[[task]]"
id: TASK-0254
aliases: ["TASK-0254"]
title: "Close-out files the validator errors it could not fix, as issues, without filing the same one twice"
status: done
phase: "[[PHASE-016-Errors-Become-Work]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0051-Validator-Errors-As-Session-Work]]"]
parent: "[[FEAT-0051-Validator-Errors-As-Session-Work]]"
effort: S
depends: []
blocks: []
related: ["[[ISS-0069-Review-Verdict-Vocabulary-Is-Unguarded]]"]
tests: []
---

# Close-out files what survives

## Definition of Done
- [x] The close-out procedure says: run the validator, fix what you can, and **file what you cannot as an `ISS-*`**
- [x] Each filed issue carries the error's code and message verbatim, and links the note it names
- [x] A recurring error **updates one issue** rather than minting a second each session
- [x] Closing the issue is what a fix looks like — no separate bookkeeping
- [x] Nothing files automatically in the background (Edwin's call, recorded in [[PHASE-016]])

## Steps
- [x] Extend the close-out step in `tools/instructions/LIFECYCLE.md` and `tools/skills/close-out/SKILL.md` — the sentence there already says "run `validate-docs.sh` and fix anything it reports", which has no answer for *cannot fix*
- [x] Define the dedup key: `(code, subject)`, where subject is the error's note ID or repo-relative path
- [x] Test: a guard asserting the instruction exists and the dedup key is stated, so the procedure cannot quietly lose the half that was added

## Notes

**Documentation, not code.** The promotion is a step an agent performs, which is why it belongs in the instruction it extends rather than in a background filer. Auto-filing was considered and declined: issues appearing without anyone asking is a worse failure than one occasionally missed.

**The honest limitation:** this depends on the agent doing the step. That is the same dependency every other close-out obligation has, and the same mitigation applies — the validator runs at pre-commit and in CI, so an unfixed error is loud whether or not anyone filed it. What filing adds is a place to record *why* it is still there.

The upstream half — whether the template should carry this rule for every repo — belongs with `project-os-dev` ISS-0027's family of close-out gaps, not here.

## Done 2026-07-30

The rule is in **`CLAUDE.md`**, not `tools/instructions/LIFECYCLE.md`. `tools/sync/MANIFEST.yaml` marks `tools/instructions/` and `tools/skills/` as `template`, so an edit there becomes divergence the next sync reports — the same constraint that kept [[ISS-0069]]'s check out of the validator.

> At close-out, every validator error is either **fixed or filed**. Anything still failing that you cannot or should not fix becomes an `ISS-*` carrying the `[CODE]` and message verbatim, deduped on `(code, subject)` — subject being the note ID, the repo-relative path, or `SNAPSHOT.yaml` for snapshot-level errors.

Two guards: one that the rule is present and keeps all three of its parts, and one that **`LIFECYCLE.md` still only says "fix"** — so when the template adopts the rule, the local copy is deleted rather than left to drift alongside it. A local override that outlives its reason is how two vocabularies start.

**Proposed upstream** so every repo can carry it, rather than this one having a private procedure indefinitely.
