---
type: "[[feature]]"
id: FEAT-0096
aliases: ["FEAT-0096"]
title: "A decision states its open questions as criteria — so it is answered one at a time with evidence rather than stamped in one click"
status: done
phase: "[[PHASE-032-The-Reasoning-Is-Recorded]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12 on ADR-0010: 'this is not as straight forward as simply accepting, it asks questions'"]
goal: "A decision note may carry an Acceptance section; its open questions become tickable criteria, each answered with evidence through machinery that already exists."
requirements: []
tasks:
  - "[[TASK-0399-Criteria-On-A-Decision]]"
  - "[[TASK-0400-ADR-0010-States-Its-Questions]]"
related: ["[[ADR-0010]]", "[[ISS-0152]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]

---

# A decision states its open questions

## Goal

[[ADR-0010]] offers three options, proposes the third, and leaves two live threads inside its own consequences. `Accept` stamps all of it at once. **The machinery to answer them one at a time already exists** — `criteria.py` parses an `## Acceptance` section, the tick carries evidence, and both are guarded — and it has never been pointed at a decision note.

This is the cheap half of [[PHASE-032]] and it is deliberately first: it needs no new write path, and it makes ADR-0010 decidable today.

## Out of scope

- **Requiring** an Acceptance section on decisions. Most ADRs are a genuine yes/no and would gain a ceremony that says nothing. This makes the section *available* and *meaningful*, not mandatory.
- **Blocking `Accept` until every question is ticked.** Tempting and wrong: a person may accept a decision while an open thread stands, and the record should show that rather than prevent it. The unticked criteria are the honest residue.

## Acceptance

- [x] `criteria.py` reads an `## Acceptance` section on an `adr`/`decision` note, and the cockpit offers the same tick-with-evidence controls it offers a feature.
- [x] [[ADR-0010]]'s two open threads are criteria on the note, in its own words rather than paraphrased.
- [x] Ticking one writes `— evidence: … (actor, date)` on that line and touches nothing else, exactly as it does for a feature.
- [x] Accepting the ADR with criteria unticked is **allowed** and leaves them visibly unticked.
- [x] The convention is stated where a person writing an ADR will find it, not only in this note.


## Evidence — 2026-08-12, and it needed no code

`criteria.py` parses an `## Acceptance` section on **any** note, and `stamp_tick` is not gated by type — so pointing both at a decision cost nothing but the convention. Driven on a clone before the convention was written: two criteria parsed off [[ADR-0010]], one ticked, and the line came back `- [x] **\`Recent\`'s two verdicts:** … — evidence: Dropped from both. (user:edwin, 2026-08-12)` with the other still open.

**That is the second time this phase found the machinery already there** — [[TASK-0394]]'s owed mark was the first. Both are the same lesson: the mechanism existed and had never been pointed at the case.
