---
type: "[[task]]"
id: TASK-0483
aliases: ["TASK-0483"]
title: "The *Covered by* action — one write, refused unless the id resolves to a runnable test"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0120-The-Automation-Path]]"]
parent: "[[FEAT-0120-The-Automation-Path]]"
effort: M
depends: ["[[TASK-0482-Covered-By-Reaches-The-Gate]]"]
blocks: []
related: []
tests: []
---

# The *Covered by* action

An action on the acceptance page that sets `automation:` and `covered_by:` in one write, alongside the six marks and *Needs re-run*. **Refused unless the id resolves to a test carrying a `command:`** — the same refusal shape *Needs re-run* already uses for a change id that does not resolve, and for the same reason: a link to something unrunnable records a claim nobody can check.

`automation:` follows from the shape of the claim rather than being asked for separately: naming one covering test that fully covers it is `full`; naming one that covers part is `partial` and requires the reason field, exactly as a `/` mark does.

Done when: the link is writable from the surface, unresolvable and non-runnable ids are refused with the replacement named, and the `automation` filter on `~checks` has more than one value for the first time.

## Not done

`covered_by:` now *reaches* the gate ([[TASK-0482-Covered-By-Reaches-The-Gate]]) and nothing yet *writes* it from the surface. The field is hand-editable and the gate reads it correctly; what is missing is the action and its refusal.

Deliberately left after the read path rather than built alongside it: the refusal it needs — *unless the id resolves to a test carrying a `command:`* — is only meaningful once the gate acts on the field, and building both at once would have shipped a control whose effect nobody had seen.

## Done 2026-08-18

`note_writes.cover_check` — one write setting `automation:` and `covered_by:`, with four refusals:

- **an id that does not resolve** — coverage nobody can open is an assertion, not evidence;
- **a note that is not a test**;
- **a test with no `command:`** — the load-bearing one. `_resolve_coverage` accepts only an executable test, so a link to a manual one would look like coverage on every surface and settle nothing: a claim written into the exact field the gate reads that the gate is built to ignore. The write is the only place that can be caught;
- **`partial` with no reason** — the same rule the `/` mark carries.

`covered_by:` is written with `quote=False`, because it is a YAML list and quoting it produces a string that parses back as one scalar — [[TASK-0445]]'s defect, where a release reported nothing it had verified.

**And it uncovered a live defect the migration had introduced.** `_require_check` demanded `note_type == "check"`, which after the merge is false for **every note in every repo** — so `mark_check` and `invalidate_check` refused the entire corpus and the mark dialog wrote nothing. Nothing caught it: every fixture in `test_check_verdicts.py` still builds the retired type, so both writers were only ever exercised against notes that no longer exist anywhere. The predicate now keys on `level: acceptance` (still accepting the retired type for unmigrated repos), and `test_the_write_path_addresses_the_merged_type` builds what the corpus actually holds.
