---
type: "[[issue]]"
id: ISS-0196
aliases: ["ISS-0196"]
title: "TESTING.md and QUALITY.md disagree on what the independent-review gate keys on — a status in one, a note being touched in the other, and the validator implements only the first"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: docs
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[ISS-0195-Two-Types-Carry-One-Act]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[TASK-0475-Level-Acceptance-Becomes-The-Discriminator]]"]
---

# The review gate is described two ways

Found by the independent review of [[ISS-0195-Two-Types-Carry-One-Act]], 2026-08-18, which could not file it under a read-only constraint.

**TESTING.md** says the independent-review gate is *keyed on that status* — a `TST-*` reaching `passing`. **QUALITY.md** says it applies to *any change that creates or updates a `TST-*`*. Those are different populations: the first is a subset of tests at one status, the second is every test any change touches.

**The validator implements TESTING.md's.** `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}` fires on status alone, which is why this repo shows 22 `[REVIEW]` warnings rather than one per touched note.

So an agent following QUALITY.md does more review than the gate asks for, and one following TESTING.md does exactly what it asks — and neither is wrong by its own document. The cost is invisible until somebody reconciles the two, which is what happened here.

## Why it matters now

[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] turns 669 checks into tests. Under TESTING.md's reading nothing changes, because acceptance tests rest at `active` and never reach `passing`. **Under QUALITY.md's reading, every one of the 669 is a `TST-*` that a change touched**, and the gate's population goes from 22 to hundreds.

The merge does not create this ambiguity, but it is the first thing that makes the difference expensive. Settle it in [[TASK-0475-Level-Acceptance-Becomes-The-Discriminator]] rather than carrying it into a corpus thirty times larger.

## Next actions

- [ ] Decide which reading is the rule — status, or note-touched — and make the losing document say the winner's sentence rather than a paraphrase of it.
- [ ] Both files are template-owned: upstream first.

## Fixed 2026-08-18

**The status reading is the rule**, and QUALITY.md now says so in the same terms TESTING.md and the validator already used: the gate is keyed on a `TST-*` reaching `passing`, a requirement reaching `implemented`, a feature reaching `done` — not on a note being touched.

The ambiguity was cheap until ADR-0031 and stopped being cheap the moment it landed: the note-touched reading would have made 669 migrated acceptance tests gate-bearing overnight. QUALITY.md carries a sentence recording that, so the next reader knows why one of two plausible readings won.
