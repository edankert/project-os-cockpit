---
type: "[[task]]"
id: TASK-0601
aliases: ["TASK-0601"]
title: "The owed checks are settled where they are owed — one endpoint writing `na`, `excused` or `blocked` with a reason, refusing `pass`, `partial` and `fail` by name"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "Edwin, 2026-09-08: 'uncheck the required acceptance-tests for the release'"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: M
due: ""
depends: ["[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"]
blocks: ["[[TASK-0602]]"]
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0254]]"]
tests: []
---

# The owed checks are settled where they are owed

[[ADR-0041]] is the authority for this task and nothing else in the feature needs it. The short form: `na`, `excused` and `blocked` are decisions about whether a check is in scope, the release is the only place that question has an answer, and none of the three can assert that anything passed.

## Definition of Done

- [x] `POST /api/notes/release-settle` takes `{release, checks: [...], mark, reason}` and appends **one `ledger.append` event per check**.
- [x] The platform is resolved **from the release**, not from the client. A client with no platform to send is [[ISS-0290]]'s defect, and `note_writes.verdict_platform` already implements the resolution order.
- [x] `mark` is restricted to `na`, `excused` and `blocked`. **`pass`, `partial` and `fail` are refused by name**, with a message citing [[ADR-0041]] and saying where they are recorded instead — `~checks`, or the check's own note.
- [x] `question` is refused too, with its own reason: it is a judgment about the check's wording, made by somebody reading the wording.
- [x] **A reason is required on all three**, and the refusal is the write path's own: `ledger.NEEDS_REASON` is `MARKS - {"pass"}` and `check_entry` enforces it. Do not add a second check in front of it that could drift.
- [x] The event carries `by` (the actor) and the date, so a settled check names who decided and when.
- [x] A release that has shipped is refused: its ledger is sealed and `ledger.append` refuses a sealed ledger already — surface that refusal rather than letting it read as a server error.
- [x] Bulk is one request, and it is **atomic per check, not per request**: settling twelve checks where the eighth is unknown records seven and reports the eighth. A partial write that reports itself is better than twelve refusals because of one typo.

## The guard this task must rewrite

`tests/test_release_held_back.py::test_no_write_path_to_a_check_appears_on_the_release_page` asserts that **no** route to a check write appears inside any release-page function. That claim is now too wide by exactly three marks.

**Rewrite it; do not delete it or add a hole to it.** Its docstring records that seven passes of independent review each defeated a looser version — a 2600-character window, a fixed function list, a forbidden-string list that missed `checkMark(item)`, and a `buildCheckRow` check that matched on spelling instead of arguments. The rewrite:

- The forbidden set becomes **attestation routes**: `walkOneCheck`, `/api/notes/mark-check`, `/api/notes/retire-check`, `gateMark(`, `markGateRow(`, `checkMark(`, `markCheckRow(`, `retireCheckRow(`, `paintCheckList(`, and every `buildCheckRow(...)` call that does not pass `controls` as a literal `false`.

  *(`askForMark` was on that list when this task was written and is **not** forbidden in the delivered guard. One dialog, one reason field, one set of refusals — a second dialog built for the release page is how the two surfaces would come to disagree about what `excused` means. So the call is admitted and checked **on its argument**: its `only:` list must be a non-empty subset of `{na, excused, blocked}`, the same treatment `buildCheckRow`'s `controls` already gets. A subset check catches `pass` however it is spelled; a spelling ban with a carve-out would not.)*
- `/api/notes/release-settle` is admitted, and a **new** assertion states the property that replaces the old one: the settle call site sends a mark from `{na, excused, blocked}` and the string `pass` does not appear as a mark anywhere in a release surface.
- The discovered-function-set assertion stays exactly as it is. It is the part that catches a tenth release surface appearing.

[[ISS-0254]] still owns the durable form — a rule over the call graph rather than over spellings — and this task makes that issue more valuable rather than less.

## Steps

- [x] Endpoint in `server.py`, beside `/api/notes/mark-check`.
- [x] Write path in `note_writes.py`, reusing `verdict_platform` and `ledger.append`.
- [x] Guard the three refusals separately: `pass` by name, no reason, sealed ledger.
- [x] Rewrite the ADR-0035 guard as above, and run it against the shipped renderer **before** the settle UI exists — it must still pass, or the rewrite has a hole in it that the new code will hide.

## Notes

**Nothing here touches a note.** [[REQ-0055]] is the rule and it is guarded rather than reviewed: the read path spans 87 sites in the renderer alone, and a surviving frontmatter write does not raise — it puts a scalar back where the migration removed one.
