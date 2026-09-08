---
type: "[[task]]"
id: TASK-0597
aliases: ["TASK-0597"]
title: "The platform a release could ship is offered, not typed — the ledgers and the notes say which platforms this repo has evidence for"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "Edwin, 2026-09-08: 'select: android or iOS'"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: S
due: ""
depends: []
blocks: ["[[TASK-0600]]"]
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tests: []
---

# The platform is offered, not typed

`platform:` is free text on a release note. A typo in it is not a cosmetic defect: the value becomes part of a ledger filename, it decides which checks the gate counts, and `_ships_on` already knows **five** spellings of *"every platform"* because the corpus contains four of them.

A text box for an id is how [[ISS-0142]] happened, and `release_contents` carries the server half of that lesson in a comment — *"the candidate list is the client half"*. The platform has no candidate list at all.

## Definition of Done

- [x] `publication.platform_candidates(index)` returns the platforms this repo has **evidence** for: the union of `ledger.platforms(docs_root)` and the non-empty `platform:` values on the repo's own notes.
- [x] The list carries an explicit **every platform** option, whose value is the empty string. `publication._EVERY_PLATFORM` already names the five spellings (`""`, `shared`, `cross`, `all`, `both`); the picker offers one of them and the union rule [[DES-0012]] D4 implements does the rest.
- [x] Every offered value matches `^[a-z0-9][a-z0-9_-]*$` — the expression `ledger.working_path` refuses on. **The picker never offers a value the write path will reject**; that is the whole reason for reading the corpus rather than hard-coding `android`/`ios`.
- [x] `release_payload` carries the candidates, so the page needs no second fetch.
- [x] A repo with no ledgers and no `platform:` anywhere gets the *every platform* option and nothing else — an empty picker is worse than no picker.

## Steps

- [x] Read the ledger platforms with `ledger.platforms(docs_root)`; it already returns a sorted set and skips the empty platform.
- [x] Walk the index for `platform:` values, lowercased and stripped. Both releases and features carry the field.
- [x] Merge, sort, and prepend the every-platform entry.
- [x] Add the key to `release_payload`'s return and to `ReleasePayload` in `renderer.ts`.

## Notes

**Read only.** This task writes nothing and decides nothing; it makes the choice offerable. The write path is [[TASK-0598]] and the control is [[TASK-0600]].

**Where the shape regex belongs.** `ledger._PLATFORM_RE` is the authority and it is private to that module. Stating the same expression in `publication` is a second copy of one rule — prefer exporting or reusing rather than restating it, and if a copy is unavoidable, say in a comment that `ledger.working_path` is the one that actually refuses.
