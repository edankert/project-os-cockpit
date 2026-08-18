# Plan — the surfaces report at the reader's granularity

[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]. Five features, eleven tasks, four issues, one decision ([[ADR-0035]]).

## Order, and why

**1. [[FEAT-0126]] — the glyph regression.** Smallest, and it is live: every mark picker in every repo currently reads `[done] Done — walked and passed`. No dependencies.

**2. [[FEAT-0125]] tasks 0502–0503 — the release control and the wall.** [[ISS-0210]] is the highest-severity item here: the page whose job is to report a release is not ready offers sixty controls that make it ready. The control goes first, the wall second.

**3. [[FEAT-0127]] — the tests view's two data defects.** `Verified` as the else-branch is a correctness bug that will outlive the corpus that revealed it. [[TASK-0507]] is deliberately last within this feature: it is a judgement per note, not a rule.

**4. [[FEAT-0128]] — the tests view's shape.** Presentation only. Safe to do after the rows are correct, and pointless before.

**5. [[FEAT-0129]] — composing a release.** New scope, and the only item that adds a write path. Last, and it unlocks [[TASK-0504]]'s better version and [[TASK-0512]].

## The through-line

Every task must leave the information reachable. Three of these collapse or remove something from a screen, and the failure mode for all three is identical: a count that no longer expands to its rows is work that has been hidden rather than organised. [[REQ-0047]] criterion 3 states it; [[TASK-0503]] and [[TASK-0508]] both carry it.

## What is deliberately not here

- **[[ISS-0208]]** (retire the tier rule) — open, and owns the gate question. Nothing in this phase changes which checks block.
- **[[ISS-0206]]** (a check cannot be scoped to a release) — [[FEAT-0129]] bears on it without resolving it. Choosing features narrows the gate honestly; a `release:` field on a check would encode something derivable.
- **[[ISS-0209]]** (the fleet validators) — unrelated, and a migration per repo.
