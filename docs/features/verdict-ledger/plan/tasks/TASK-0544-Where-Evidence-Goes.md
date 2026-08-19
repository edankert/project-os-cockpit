---
type: "[[task]]"
id: TASK-0544
aliases: ["TASK-0544"]
title: "Decide where `evidence:` goes — the entry carries it, or its loss is stated as a loss"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The seventh field has no home, and nothing has said so

[[REQ-0053]] removes seven fields from the note. Six have a destination or a stated reason to disappear. **`evidence:` has neither** — the ledger entry schema in [[TASK-0527]] is `check`, `mark`, `date`, `by`, `method`, `reason`, and evidence is not in it.

This is not a small omission. [[ADR-0030]]'s honest tally of what one-note-per-check bought led with *"per-check evidence attachments"* — it is the first item on the list of things that were **genuinely unlocked** rather than merely improved. Deleting the field without replacing it would give that back.

## Definition of Done

- [ ] Decided, in [[ADR-0037]] rather than in a commit: the entry carries `evidence` (a list of paths or urls), **or** the capability is dropped and the ADR says so in its consequences.
- [ ] If it is carried: evidence attaches to the **event**, not to the check — a screenshot is proof of one walk on one platform on one date, which is the whole thesis applied to the field.
- [ ] `Item.evidence` (`acceptance.py:358`, read at `:801`) follows the decision.
- [ ] Measured first: how many notes carry a non-empty `evidence:` today, per repo. If it is zero everywhere the decision is cheap, and that should be known before it is made rather than after.

## Notes

Evidence on the event is the better shape and this task should probably confirm it rather than open it: a verdict without its evidence is the thing the whole phase is arguing against, and evidence on the *check* would be a standing claim of exactly the kind decision 3 rejects for `automation:`.
