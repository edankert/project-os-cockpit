---
type: "[[task]]"
id: TASK-0485
aliases: ["TASK-0485"]
title: "Backfill `automation:` and `covered_by:` from the 203 bodies that already name their covering test"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0120-The-Automation-Path]]"]
parent: "[[FEAT-0120-The-Automation-Path]]"
effort: M
depends: ["[[TASK-0483-The-Covered-By-Action]]"]
blocks: []
related: []
tests: []
---

# Backfill automation from the prose

**203 of `your-trainer`'s 579 bodies carry the migration's parenthesised annotation** — 181 `(partially automated`, 22 `(automated`, zero `(fully automated` — and 221 mention automation at all, while `automation:` reads `manual` on 669 of 669 and `covered_by:` is `[]` on 669 of 669. The fact is in the corpus and in the wrong place; ADR-0030 defined the fields and the migration copied the annotation as text.

The annotations name real classes — `LicensingManagerTest`, `RiderCardTest`, `TrainerCompatibilityTestFailureModesTest`. **Those are JVM test classes, not `TST-*` ids**, so the backfill cannot simply write `covered_by:` and stop: either the class name is recorded in a form the gate can check, or a `TST-*` note is created for the class and named. Decide that before writing 203 notes, because the wrong choice is 203 notes of plausible-looking data the gate cannot use.

**Report what it could not resolve.** A backfill that silently skips is indistinguishable from one that found nothing.

Done when: every resolvable annotation is a field, the unresolvable ones are listed rather than skipped, and the blocking count on `your-trainer` is re-measured — 15 of its 60 blocking checks claim automation in prose today.

## Done 2026-08-18 — and the decision inside it, made and measured

*(This section read "Not done, and the decision inside it is unmade". It is made below.)*

**`automation:` is backfilled on all 203** — 181 `partial`, 22 `full` — so the `~checks` automation facet has three values instead of one and renders for the first time. A single-valued axis is dropped by design, which is why the one question this corpus answers 203 times could not be asked of it. The gate is unmoved at 60 blocking, because `automation:` is descriptive and only `covered_by:` settles anything.

**`covered_by:` is deliberately left empty, and this is the decision.** Measured: the 203 bodies name **54 distinct JVM test classes** and **not one names a `TST-*` id**; only 6 non-acceptance tests in that repo name a class at all, and none of their classes overlaps the 54. So there is nothing to link. The alternative was creating 54 `TST-*` notes whose `command:` is a gradle invocation nobody can run from here — 54 unverifiable claims written into the field the gate reads, which is exactly what `cover_check`'s refusal exists to prevent. **The refusal working is not the same as the task being blocked.**

SCHEMAS.md (inherited from [[ADR-0030]]) said `covered_by:` may name *"the `TST-*` notes **or test modules**"*. The module half is the part that cannot be checked, and after [[TASK-0482-Covered-By-Reaches-The-Gate]] made the field decide a gate, recording an uncheckable value in it stopped being harmless.

### Original note


The 203 annotations name **JVM test classes** (`LicensingManagerTest`, `TrainerCompatibilityTestFailureModesTest`), not `TST-*` ids. `_resolve_coverage` resolves ids through the index and nothing else, deliberately — *"anything else is a claim the gate cannot check"* — so writing those class names into `covered_by:` would produce 203 notes of plausible data the gate ignores.

The rule has to be chosen first: record the class in a checkable form, or create a `TST-*` per class and name that. Recorded in [[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]], which stays open.

It is also downstream of [[TASK-0480-The-Fleet-Migration]]: all 203 are in `your-trainer`.
