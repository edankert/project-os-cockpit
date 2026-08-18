---
type: "[[task]]"
id: TASK-0495
aliases: ["TASK-0495"]
title: "One verb for one act — the registry carries `Run` and `Walk` over the same type today"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
parent: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
effort: S
depends: ["[[TASK-0492-Retire-The-Manual-Run-Obligation]]"]
blocks: []
related: []
tests: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
---

# One verb

The registry carries both simultaneously: `test → Run` and `release gate → Walk`, over one type. Live on `your-trainer` as **`Run 5 tests`** and **`Walk 1 release gate`** on the same screen.

The split made sense while they were different types. Under [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] they are one type on a scale, so the surface has two words for one act separated by a field the reader cannot see — and it shows: the group called **`Needs a run`** contains only the NON-acceptance tests, while the population a person actually walks sits under `Tier 1/2/3` with no verb at all.

Pick one deliberately. *Walk* describes what a person does to a checklist; *Run* describes what a machine does to a command — which is an argument for `Walk` on the human side and `Run` staying with `command:`. Apply it to the registry verbs, the group headings and the buttons in one pass, or the two words simply move.

Done when: one verb names the human act everywhere, and `run` refers only to something a machine does.

## Done 2026-08-18

**`Walk`** is the human act; **`Run`** is what a machine does to a `command:`. That is the split the two words already carry in ordinary use and the one `command:` makes structural — and every note the `test` obligation reaches has no `command:` by definition, so `Run` was naming the one thing that cannot happen to it.

The registry verb, the group heading (`Needs a walk`) and the predicate text all changed in one pass. Live on `your-trainer` before this: *"Run 5 tests"* beside *"Walk 1 release gate"*, two words for one act on the same screen.

### Why it was left last

The vocabulary change is the one piece of FEAT-0123 that touches every surface at once — registry verbs, group headings, buttons — and it is the one with no measurement behind it: *walk* versus *run* is a naming judgement, where the other three tasks each had a number.

It is also now smaller than when it was written. `Needs a run` still contains only non-acceptance tests, but under [[ADR-0034-Three-Axes-Not-One-Word]] that is no longer a *different kind of test* — it is the same population filtered by execution. Renaming it is a one-line change once somebody picks the word.

**Recommendation on the record**: *walk* for the human act and *run* for what a machine does to a `command:`, which is the split the two words already carry in ordinary use and the one `command:` makes structural.

## Independent review — 2026-08-18, `model:claude-opus-5`, changes-requested

Third verification pass, fresh context, separate session; model shared with the author and recorded above as provenance ([[project-os-dev#ADR-0013]]).

**The verb landed.** Derived from the live payload rather than from the source text: `obligations.payload()` returns `verb='Walk'` for the `test` kind and `Walk` for the release gate, and no `Run` survives in the registry. `d1a8ad6` is the commit that made the change the second review found had silently no-opped; `a1279c2` had not.

**It is unguarded, which is the finding.** Reverting `"Walk"` to `"Run"` in `obligations.py` and running the **full** suite gives `1697 passed, 4 skipped` — **zero failures**. The second review already recorded that the matching heading rename was unguarded (*"reverting it to `Needs a run` leaves the whole suite green"*); the verb was corrected without closing that gap, so the exact defect this task exists to fix can return without anything failing. A test asserting the payload verb — the derivation this review used — would close it.

## Independent review — 2026-08-18, `model:claude-opus-5`, changes-requested (fourth pass)

Fresh context, separate session; model shared with the author and recorded above as provenance ([[project-os-dev#ADR-0013]]).

**The guard landed and is genuine.** `test_one_verb_names_the_human_act_across_every_owed_kind` was mutation-proven, not read: reverting `"Walk"` to `"Run"` in `obligations.py` makes it fail (`1 failed, 17 passed`), where the third pass recorded the same mutation passing 1697 tests. The section above, which ends *"It is unguarded, which is the finding"*, is no longer true and was left standing when the guard was added in the same commit — a reader of this note alone still concludes the fix is unguarded.

**It does not assert what its docstring says it asserts.** The docstring reads *"Asserted on the payload rather than the constant, because the payload is what the badge renders."* The body reads `obligations.OBLIGATIONS[kind].verb` — the registry, which is the constant. Demonstrated by a second, narrower mutation: making `badges_payload()` emit `"Run"` for the `test` kind while leaving the registry at `"Walk"` passes the **full** suite — `1698 passed, 4 skipped`, zero failures. The badge would render *"Run 5 tests"* — precisely the defect this task exists to remove — with nothing failing.

That is the gap the third pass asked to close (*"A test asserting the payload verb — the derivation this review used — would close it"*), answered with a registry assertion described as a payload assertion. It is not hypothetical: `obligations.py:1138` carries *"The verb is the registry's, never the surface's"*, so a surface deriving its own verb is a path this codebase has already had to rule out once.

**To clear this**: assert on `obligations.badges_payload(index)["verbs"]["test"]` (keeping the registry assertion beside it if useful), and correct the docstring or the section above so the note does not describe a guard that is not there.

## Guarded 2026-08-18 (fourth review)

The line above — *"It is unguarded, which is the finding"* — is no longer true, and left standing it read as an open defect in a task marked `done`.

`tests/test_obligations.py::test_one_verb_names_the_human_act_across_every_owed_kind` now asserts **`badges_payload(index)["verbs"]["test"] == "Walk"`**.

It took two attempts, and the first is worth recording because it is this task's own failure mode a second time. Version one carried the docstring *"Asserted on the payload rather than the constant, because the payload is what the badge renders"* — and asserted the constant. The fourth reviewer mutated `badges_payload` to emit `Run` for the `test` kind while leaving the registry at `Walk`: **1698 passed, zero failures**, with the badge rendering *"Run 5 tests"*. A description written ahead of the code, inside the guard against descriptions written ahead of the code.

Both mutations now fail: registry `Walk`→`Run`, and payload-only `Run` with the registry untouched.
