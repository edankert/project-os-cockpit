---
type: "[[test]]"
id: TST-0082
aliases: ["TST-0082"]
title: "A release is prepared through one workflow — the version and platform move, an abandoned draft keeps its note and its number, a settle is an event and never a note, and the coverage sweep is reproducible"
status: active
covers: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]"]
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_release_workflow.py tests/test_release_held_back.py tests/test_release_page.py -q"
last_verified: ""
issues: []
tasks: ["[[TASK-0597]]", "[[TASK-0598]]", "[[TASK-0599]]", "[[TASK-0600]]", "[[TASK-0601]]", "[[TASK-0602]]", "[[TASK-0603]]", "[[TASK-0604]]"]
artifacts: []
related: ["[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]"]
---

# A release is prepared through one workflow

Automated, in `tests/test_release_workflow.py`, with two guards it had to rewrite living in `tests/test_release_held_back.py` and `tests/test_release_page.py`.

## What it pins

**That naming the platform moves the gate and touches no check.** Both halves, in one test, because either alone passes for the wrong reason. A release that says `ios` grades against the iOS ledger; one that says nothing takes the union, where a check clears only if every platform cleared it. Two ledgers is what it takes to see the difference, which is why [[ISS-0288]] survived: eleven of twelve fleet repos have at most one, and the union over one ledger is that ledger. The second half compares the check note's bytes before and after — [[REQ-0055]] says a verdict write never touches a note, and a *platform* write must not either.

**That the version refusals are one function.** `create_release` and `update_release` call `_refuse_bad_version`, so the shape rule, the newest-released ceiling and the collision refusal cannot come to disagree. Two implementations of one question is [[REQ-0059]]'s forbidden shape, and this one would drift silently: a refusal that differs between creating and editing is invisible until somebody edits.

**That an abandoned version is not silently reusable.** The whole reason abandoning keeps the file. `create_release` refuses a version an abandoned note already carries and names the note, so deliberate reuse is possible and accidental reuse is not.

**That a settle writes an event and never a note.** Guarded rather than reviewed: a surviving frontmatter write does not raise, it puts a scalar back where the migration removed one. The test compares the check note's text and reads the entry out of `ledger.working`.

**That a bulk settle is atomic per check, not per request.** Twelve checks where the eighth is unknown records seven and reports the eighth. A ledger is append-only, so the events before a refusal stand; reporting the batch as a failure would be the only dishonest option.

**That `blocked` settles and still blocks.** [[ADR-0041]]'s deliberately useless-looking control. The row stays in the owed list, and its reason comes back on the row — a settle that left the row identical would read as a button that did nothing.

**That the coverage sweep is mechanical.** A feature no check names is a gap; a feature carrying `acceptance_exception:` is not, because somebody wrote down why it needs none. Requirements come from `criteria.payload`, not a second parse.

## The two rewritten guards, and why a rewrite rather than a deletion

`test_no_attestation_path_to_a_check_appears_on_the_release_page` replaced a guard named for *write path* rather than *attestation*, and that guard asserted that no route to a check write appears in any release-page function, over a *discovered* set of surfaces, after seven passes of independent review had each defeated a looser version. [[ADR-0041]] narrows the claim from *no check write* to *no attestation*, and the narrowing is structural: `askForMark` is admitted and its `only:` list is asserted to be a non-empty subset of `{na, excused, blocked}`. A subset check catches `pass` however it is spelled; a spelling ban with a carve-out would not.

`test_the_gate_is_built_before_what_is_in_the_release` searched for *any* `wrap.append` above the gate, which made its claim "nothing at all" — true until the page grew a second header control. It now names the allowed set, so a third one is a deliberate edit to that list rather than a silent widening.

**That a terminal release refuses every write.** Added after a live walk, not before: the first cut refused only `released`, so an abandoned release could be deleted on the day it was abandoned. Thirty tests missed it because every one of them asked about a `draft`. The test now walks all three write paths against an abandoned release and checks each refusal names the status it hit.

## What it does not pin

The renderer's own behaviour beyond its source text. There is no DOM harness for the release page, so *the picker shows the current platform selected* and *the bulk bar disables with nothing ticked* are asserted by reading `renderer.ts` or not at all. That is the same limit every other surface in this repo has, and it is the reason the source-text guards above are written over regions rather than over windows.
