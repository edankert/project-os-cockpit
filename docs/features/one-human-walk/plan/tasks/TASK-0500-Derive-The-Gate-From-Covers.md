---
type: "[[task]]"
id: TASK-0500
aliases: ["TASK-0500"]
title: "One rule: an item may not reach terminal while a test covering it is unsettled"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0124-Gating-Is-Derived-From-Covers]]"]
parent: "[[FEAT-0124-Gating-Is-Derived-From-Covers]]"
effort: L
depends: ["[[TASK-0499-Backfill-The-Eighty-Three]]"]
blocks: []
related: []
tests: []
---

# Derive the gate from `covers:`

One predicate, read from the reverse index [[ADR-0032-The-Verification-Link-Has-One-Direction]] already builds, applied to every item type. A release is an item whose covered set is the **union of its contents'** — its features, its issues, and anything covering the release note itself.

**"Unsettled" needs one definition across both execution modes**: a test with a `command:` is settled when the runner says `passing`; one without is settled when its outcome is settled and no later invalidation has cleared it. That is the merge of two rules that exist separately today, and writing it once is the point of the task.

**Do not delete the tier rule here.** [[TASK-0501-Prove-The-Derived-Gate-Then-Retire-The-Tier-Rule]] does that, after the two are shown identical. Running both and comparing is the only way to learn the derived one is complete.

Done when: the derived gate computes for every item type, runs alongside the tier rule, and any disagreement is reported per item rather than as a count.

## Done 2026-08-18

`Suite.blocking_for(subjects)` is the general rule — *an item may not reach a terminal status while a test covering it is unsettled* — and `blocking()` is now literally its `subjects=None` case, so the release gate and the per-item gate are one predicate rather than two that happen to agree.

**"Unsettled" has one definition across both execution modes**, which is the merge this task existed for: a test with a `command:` is settled when the runner says `passing`; a walked one is settled when its `mark:` is `done`/`incomplete`/`canceled`. VERIFY asks that question now instead of demanding a status the walked population never holds — the `continue` that skipped acceptance tests was [[ADR-0031]]'s stopgap and is exactly the special case [[ADR-0034]] removes.

**Two guards earned their keep during this task.** The status-collection guard caught `_SETTLED_MARKS` being registered as statuses — it holds *verdicts*, and registering them would assert the opposite of the construction they exist to preserve. And a **constructed** two-note corpus caught `rel` being referenced out of scope in the new branch: the rule would have crashed rather than fired, and every real repo reported **0** findings, which is indistinguishable from a rule that works.
