---
type: "[[issue]]"
id: ISS-0143
aliases: ["ISS-0143"]
title: "Tier 3's two verification checks are past their retirement trigger and nothing tracks it — 'they retire when the next release opens' is a promise living only in a comment"
status: fixed
severity: low
owner: user:edwin
created: 2026-08-11
updated: 2026-08-14
phase: "[[PHASE-011-Unproven-Claims]]"
features: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
tasks: []
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[ACCEPTANCE-TESTS]]", "[[ISS-0141]]", "[[CHG-20260814-One-Walk-For-Publication]]"]
tags: [issue, tests, housekeeping]
---

# The Tier 3 block is owed a retirement

## What is owed

`docs/tests/ACCEPTANCE_TESTS.md`'s Tier 3 block carries the contract's rule as a comment: *"Temporary. Promote to Tier 2 or remove after the next verified release."* [[REL-0001]] shipped on 2026-08-11, which **is** that trigger. Both items — 3.1 (the Tests view renders) and 3.2 (the old run-route deep link) — are still there.

Deferring them was deliberate and is written under the heading: the release that just shipped cites both items' evidence, and editing them out the same evening edits the record a shipped release points at. **The gap is not the deferral, it is that the deferral was recorded only in prose.** *"They retire when the next release opens"* is a sentence in a Markdown comment; nothing computes it, nothing surfaces it, and the next release will open without anyone being told.

Filed because independent review asked the obvious question — *where is this tracked?* — and the honest answer was nowhere.

## What closing this looks like

When the next `REL-*` note is drafted, and **before** its gate is read:

- **3.1** is covered by `tests/test_tests_view.py` and can simply be removed; its evidence stays in [[REL-0001]]'s record.
- **3.2** is reconciled as unwalkable by construction. Removing it is right; promoting it to Tier 2 would re-add a check no session can produce the precondition for.

Removing both takes the suite to 34 items, all Tier 1/2, which is the state the tier contract expects a project to return to between releases.

## The better fix, if anyone wants it

Tier 3's staleness is computable: the block is due for retirement whenever a `released` release note is newer than the suite's own `updated:`. That is one comparison, and it would put this obligation on a surface instead of in a comment — which is the whole argument [[FEAT-0089]] makes about obligations generally. Left as a note rather than done, because it is a new check on a document nobody has had a second release with yet.

---

## Fixed — 2026-08-14 ([[CHG-20260814-One-Walk-For-Publication]])

**Closed by paying the debt, not by building the tracker** — and the tracker is not merely unbuilt, it is unbuilt *as specified*, which is the more useful half of this close-out.

**The trigger had already fired.** The rule is *"promoted or removed after a verified release"*; [[REL-0001]] shipped on 2026-08-11. The deferral written above was about editing the suite the same evening a shipped release cited it, and *"they retire when the next release opens"* was one reading of the rule rather than the rule. Three days later removal costs nothing, so both items are out: **3.1 removed** because `tests/test_tests_view.py` already asserts what it looked at, **3.2 removed** because promoting a check no session can produce the precondition for would install a permanent unwalkable item. Their evidence is preserved verbatim under the suite's Tier 3 heading, and [[REL-0001]] carries one line recording the retirement with its own figures unchanged. The suite is 34 items, all Tier 1/2, gate still green.

**The comparison proposed above would not have caught this instance.** REL-0001's `date:` is 2026-08-11 and the suite's `updated:` was 2026-08-11 — *newer than* is false, so nothing would have fired on the very case that produced this issue. And `updated:` moves on **any** edit to the suite, so the first unrelated change would silence it permanently. The check needs its own field — when Tier 3 was last reconciled — compared against the newest `released` release, and its home is `acceptance.py`, which already parses these tiers for the Tests view. Recorded in the suite itself so the next person reaching for the obvious one-liner sees why it is wrong first.
