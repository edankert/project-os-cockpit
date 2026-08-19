---
type: "[[feature]]"
id: FEAT-0137
aliases: ["FEAT-0137"]
title: "One outcome vocabulary, written down once — four vocabularies collapse to one, and a check stops the document drifting from the data again"
status: doing
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
goal: "There is one set of outcome values, it is defined in one document, that document matches the corpus, and a mechanical check keeps it that way."
requirements: ["[[REQ-0056-One-Outcome-Vocabulary-And-The-Document-Matches-The-Data]]"]
tasks: ["[[TASK-0539-Settle-The-Vocabulary-Upstream]]", "[[TASK-0540-A-Check-That-Reads-Both-The-Document-And-The-Data]]"]
related: ["[[ISS-0218-Taxonomy-Documents-A-Mark-Vocabulary-The-Data-Abandoned]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0200-Marks-Versus-Statuses]]", "[[ADR-0037-A-Verdict-Is-An-Event]]"]
tags: [feature]
---

# One vocabulary

## Goal

Four vocabularies are in play ([[ISS-0218]]): Minimal's characters (documented as current in all four repos), [[ADR-0034]]'s words (live in all 671 notes), the four words nothing has ever written, and [[ADR-0037]]'s event marks. Settle them in one pass.

| ADR-0034 word | ledger mark | gate | persists past the seal | live count, fleet-wide |
| --- | --- | --- | --- | --- |
| `done` | `pass` | clears | yes | 546 |
| `todo` | *(no entry)* | blocks | — | 124 |
| `incomplete` | `partial` | clears | yes | 1 |
| `canceled` | `na` | clears | **yes** | **0** |
| — | `excused` | clears | **no — expires** | new |
| — | `blocked` | **blocks** | no | new |
| `important` | `fail` | blocks | no | **0** |
| `question` | `question` | blocks | no | **0** |
| `rerun` | *(an invalidation event)* | — | — | **0** |

**The live vocabulary is three values.** Four of the seven are written nowhere in the fleet, which is the same standing [[ADR-0029]] had when it reversed the meaning of `[!]` — verified before deciding, not after. So this migration is 546 `pass` entries, 124 absences and one `partial`.

## The three judgements inside it

**"Not run" is three answers, not one**, and it came from Edwin asking how to record *unable to test* and *not tested* separately. Measured: `excused` → `mark: canceled` is the only non-gating route today, and *"not tested, and here is why"* is impossible — clearing a mark blanks `verdict_reason`. `na` persists, `excused` expires at the seal, `blocked` gates. See [[ADR-0037]] decisions 6 and 7.


**`question` is kept**, against the source proposal, which drops it by omission rather than by argument. [[ADR-0029]] made the distinction deliberately: `fail` says the behaviour is wrong, `question` says the **check** is wrong, and they route to different work. Collapsing them into `blocked` loses the only signal the corpus has that a check needs rewriting.

**`rerun` is retired three weeks after [[ADR-0034]] minted it** and called it *"the addition that earns the migration on its own"*. The ledger makes its argument moot rather than wrong — an invalidation is a dated event sitting after the pass it invalidates, so the two states are distinguishable by construction. Nothing is lost in the corpus, because nothing ever wrote it. Something is lost in the record, and this paragraph is where it is kept.

## The defect that must not recur

`TAXONOMY.md` has documented the wrong vocabulary in every repo, including upstream, for three weeks. **It failed nothing** — `acceptance.py` accepts both forms, correctly and deliberately — so the drift was invisible to every gate and only a reader could find it, and what they found was wrong. Tolerance in the reader and silence in the gate are the combination that produced it.

## Acceptance

- [ ] `TAXONOMY.md` documents one vocabulary, upstream first, synced down to all repos.
- [ ] Legacy values stay readable and are not presented as current.
- [ ] A check reads the documented vocabulary and the corpus and fails when a live value is undocumented.
- [ ] The check is proved by introducing an undocumented value and watching it fail.
