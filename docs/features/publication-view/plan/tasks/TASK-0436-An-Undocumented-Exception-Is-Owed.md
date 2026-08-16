---
type: "[[task]]"
id: TASK-0436
aliases: ["TASK-0436"]
title: "An undocumented exception is owed — `[!]` with no justification is counted and named until somebody writes the reason"
status: deferred
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-999-Future]]"
source: ["The safeguard that lets the mark cycle freely — TESTING.md line 113 requires the justification, so its absence is a real debt rather than a UI problem"]
parent: ""
origin: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: M
depends: ["[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[TASK-0435-The-Cycling-Mark-And-Its-Paired-Write]]"]
blocks: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]"]
tests: ["[[TST-0031-The-Exception-Mark-And-Its-Justification]]"]
---

# An undocumented exception is owed

## What

A new obligation kind: an acceptance check marked `[!]` whose release note carries no justification for it. Verb `Justify`, view `publication`.

This is what makes the cycling mark safe. The gesture is not gated, so a person can land on `[!]` and walk away; the record is then incomplete in a way `TESTING.md` explicitly forbids — *"Exceptions must be documented in the release note with justification."* Rather than preventing the state, the registry **names** it.

## It passes ADR-0027's four admission tests

1. **A person must discharge it** — only a human can say why unverified work is shipping.
2. **It has a subject a surface can show** — the check, in the suite.
3. **It is discharged by an action the cockpit offers** — the justification field, `Justify`.
4. **It is countable and never unknown** — it is the count of `[!]` marks with no matching entry.

## Definition of done

- [ ] Declared in the registry as a note-less obligation with a noun and the verb `Justify`
- [ ] Counted as the number of `[!]` checks with no entry in the preparing release note — one walk, count from the rows
- [ ] Zero when every exception is justified, and **absent at zero**
- [ ] Zero when no release is `preparing`, because `[!]` cannot be set then
- [ ] The row reaches the check it is about
- [ ] It does **not** make the gate blocking — an exception is a decision to ship; an unjustified one is an incomplete record, and those are different failures
- [ ] Covered by the registry's completeness test like every other kind


## Blocked 2026-08-16

Waiting on [[ISS-0175]]. The interaction is keyed on which rendered checkbox is which check, and that correspondence does not hold: `your-trainer` parses 579 checks and renders 542 inputs. A control wired to DOM position would write to the wrong check, which is worse than no control.


## Deferred 2026-08-16, with [[FEAT-0104]]

[[ISS-0175]] is fixed and its cause is known, but the half that blocks this is not a cockpit bug: where a task list opens with no blank line those checks have **no checkbox to click**, so no interaction can be keyed on them. The remedy is a blank line in the suite, which belongs to the repo that owns it.


## Re-homed to [[PHASE-999]] on 2026-08-16

[[PHASE-034]] closed and this is parked, not resolved — `deferred` is not a resolved status, so carrying it inside a closing phase would fire `PHASE-CHILDREN` and, worse, would let a closed phase claim work it did not do. The sentinel is where work without a concrete delivery phase lives. Its origin and its reasoning stay above.
