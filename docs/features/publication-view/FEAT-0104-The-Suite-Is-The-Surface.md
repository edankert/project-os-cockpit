---
type: "[[feature]]"
id: FEAT-0104
aliases: ["FEAT-0104"]
title: "The suite is the surface — the acceptance document is where checks are closed, the mark cycles to a release exception, and an exception with no justification is owed"
status: deferred
owner: user:edwin
created: 2026-08-16
updated: 2026-08-16
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: changes-requested
phase: "[[PHASE-999-Future]]"
source: ["Edwin 2026-08-16: 'why do we need the walk button there, why not show the acceptance tests document and maybe a counter on how many checks are outstanding, selecting this brings up the acceptance tests and allows to tick the boxes and at the top allows to select whether it is completed or not and a comment'", "Edwin 2026-08-16: 'it should allow to have un-checked items for a release'", "Edwin 2026-08-16, on the interaction: 'I actually like the cycling checkbox idea better'"]
goal: "Stop building a second place to walk checks. The acceptance document already renders 542 live checkboxes that already write; give it the band it lacks — which release these gate and how many are outstanding — let the mark cycle to a release exception carrying its justification, and make an exception nobody has justified a thing the registry asks for."
requirements: []
tasks: ["[[TASK-0434-The-Check-Map-And-The-Exception-Mark]]", "[[TASK-0437-The-Suite-Band-And-The-Stepper-Retires]]"]
deferred: ["[[TASK-0435-The-Cycling-Mark-And-Its-Paired-Write]]", "[[TASK-0436-An-Undocumented-Exception-Is-Owed]]"]
design: ""
release: ""
depends: ["[[FEAT-0103-The-Gate-Is-Walkable]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0103-The-Gate-Is-Walkable]]", "[[ISS-0141]]", "[[ISS-0139]]", "[[FEAT-0105-There-Is-Always-A-Release]]"]
tests: ["[[TST-0031-The-Exception-Mark-And-Its-Justification]]"]
---

# The suite is the surface

## Why this replaces what I built

[[FEAT-0103]] built a **stepper**, and Edwin asked the better question: *"why do we need the walk button there, why not show the acceptance tests document and maybe a counter on how many checks are outstanding."*

He is right, and it is less work. The rendered suite already carries **542 live checkboxes**, and `POST /api/notes/check-toggle` already writes them. Ticking was never the missing piece. What is missing is the **band** at the top — which release these gate, how many are outstanding — and a way to say *this one is not done and we are shipping anyway*.

That last is not a new idea either. `TESTING.md` line 113 has always said: *"A test may be marked as a release exception if it cannot be completed … Exceptions must be documented in the release note with justification."* It has never been implemented.

## The mark cycles

`[ ]` → `[x]` → `[!]` → `[ ]`, one click each. Edwin chose this over a separate affordance, and the objection I raised against it was weaker than I stated it.

**The real objection was the undo path**, not mis-clicking: correcting a mis-tick is the most ordinary act in the document, and the cycle routes it *through* the exception state. If entering `[!]` wrote a release-note entry, every correction would create and delete one; if it opened a prompt, correcting a tick would mean dismissing a dialog asking why you are shipping unverified.

**The resolution is not to gate the gesture but to make the incomplete state loud.** The mark writes immediately — screen and file never disagree, exactly as ticking behaves today. Clicking *past* `[!]` leaves nothing behind. *Stopping* there leaves an exception with no justification, which is an incomplete record and is **named and owed** until somebody writes the reason.

That is this project's grain: the validator files what it cannot fix rather than blocking, and [[ADR-0027]] counts what needs a person.

## The four marks, and why `[!]` is the heavy one

| mark | says | scope |
| --- | --- | --- |
| `[ ]` | outstanding | — |
| `[x]` | walked and passed | permanent |
| `[~]` | settled by decision — the surface was retired ([[ISS-0141]]) | permanent |
| `[!]` | **not done, and shipping anyway** | **this release only** |

`[!]` is the only mark that is a claim about *shipping*. It is the one that needs a justification, the one that goes in the release note, and the only one that **expires**: when the release ships, exceptions reset to `[ ]` and the check is owed again — `TESTING.md` rule 5's *"after a verified release … RE-RUN annotations are cleared"*, applied to the mark that carries the same per-release meaning.

## Acceptance criteria

- [~] The gate row opens the acceptance **document**, and states how many checks are outstanding — reconciled by [[FEAT-0107]] — there is no gate row now; the release PAGE carries the count and opens the suite
- [~] A band at the top of the suite names the release it gates and the outstanding count — reconciled — the release page carries this, and a band on the document would be a fourth surface for one subject
- [ ] The mark cycles `[ ]` → `[x]` → `[!]` → `[ ]`, and each click writes the mark **immediately** — **not built** — blocked by [[ISS-0175]]
- [ ] Landing on `[!]` opens a justification field inline; **Confirm** writes the release-note entry — **not built** — [[ISS-0175]]
- [ ] Clicking *past* `[!]` to `[ ]` writes no release-note entry and leaves none behind — **not built** — [[ISS-0175]]
- [ ] An `[!]` with no justification is **counted and named** by the registry until one exists — **not built**, and its permissive half IS live — filed as [[ISS-0177]] on Edwin's instruction to keep the hatch and record the gap
- [x] An exception is addressed by **section and ordinal** with a name check, like every other suite write ([[TASK-0430]]) — `acceptance.locate` / `rewrite_check` exist and are tested; nothing calls them yet
- [x] `[!]` does not block the gate — it is counted and named, the way `[~]` is, and reported separately from it — `test_an_exception_settles_without_being_walked`, and it is reported separately from `[~]`
- [ ] `[!]` is refused when no release is `preparing`: an exception is *from a release*, and with none there is nowhere for the justification to live — **not built** — [[ISS-0177]]
- [ ] Exceptions **expire on ship** — reset to `[ ]` when the release goes `released` — **not built**
- [x] The stepper (`~walk`) is **removed**, not left beside this. Two ways in is [[ISS-0139]] — done by [[TASK-0442]]
- [x] Every write stays loopback-only and enumerated — the walk-check route is deleted; the two that remain are enumerated

## Notes

**The check map ships from the server.** The rendered document's checkboxes are addressed by DOM position today; the suite's own addresses are section-and-ordinal. The mapping between them is computed by `acceptance.parse` and sent with the render payload, so the client owns no rule about the suite's shape — [[TASK-0357]]'s rule.


## Deferred 2026-08-16

**`deferred`, not `done`.** Four criteria are met, two are reconciled by [[FEAT-0107]] (the release page took the job the band was for), and **six are not built** because [[ISS-0175]] blocks them: the rendered document's checkbox order does not match the suite's, so a control keyed on it would write to the wrong check.

The uncomfortable part, found by review: **the permissive half of the `[!]` mark is live** while this feature reads `backlog`. Hand-write one and a check leaves the release gate with no justification and nothing owed. Edwin's call was to keep it and file the gap — [[ISS-0177]].

[[ISS-0175]] is now fixed — its cause was Markdown lazy continuation, and the dangerous half (a box carrying another row's text) is closed. But the half that blocks *this* feature is not a cockpit bug: in a suite where a task list opens with no blank line, those checks have **no checkbox to click**, so no interaction can be keyed on them. The remedy is a blank line in `your-trainer`'s document, which belongs to that repo.

So this is parked rather than abandoned, and rather than left `backlog` inside a closing phase. Two things stay true and are recorded where they will be found: [[ISS-0177]] — the `[!]` escape hatch is live without its accountability — and the reconciliation that [[FEAT-0107]]'s release page took the job the suite band was for.


## Re-homed to [[PHASE-999]] on 2026-08-16

[[PHASE-034]] closed and this is parked, not resolved — `deferred` is not a resolved status, so carrying it inside a closing phase would fire `PHASE-CHILDREN` and, worse, would let a closed phase claim work it did not do. The sentinel is where work without a concrete delivery phase lives. Its origin and its reasoning stay above.
