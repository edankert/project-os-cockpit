---
type: "[[feature]]"
id: FEAT-0065
aliases: ["FEAT-0065"]
title: "The acceptance-debt surface: which requirements have no verification, which criteria sit unticked, what was ticked without evidence"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["Review 2026-08-03: the overview says 23/23 tests passing and never says which requirements have no test at all"]
goal: "A record-column card answering the coverage questions the Verification card cannot: REQs with no verifying TST, criteria unresolved on non-terminal notes, ticks carrying no evidence — each count opening to its rows."
requirements: []
tasks:
  - "[[TASK-0294-The-Debt-Payload]]"
  - "[[TASK-0295-The-Record-Card]]"
  - "[[TASK-0296-Parity-With-The-Validator]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[FEAT-0018-Verification-Health-Surface]]"]

---

# Acceptance debt

## Goal

Three numbers that exist nowhere: unverified requirements (no TST names them in `verifies:`), unresolved criteria on live notes, evidence-free ticks. All derivable from frontmatter and the criteria parse the validator already does — this is a payload plus a record-grammar card, no new data.

## Out of Scope

- Enforcing anything. The surface makes debt visible; the gates stay where they are.
- Fleet-wide roll-up (a later fleet-surfaces item, if the per-repo card earns it).

## Acceptance

- [x] Three numbers that existed nowhere are computed and shown — `24 unverified · 4 unresolved · 0 evidence-free` on the overview ([[TASK-0294]], [[TASK-0295]])
- [x] All of it derives from frontmatter and the criteria parse already in use — a payload, not new data
- [x] The criteria parse has exactly one home, and the claim is proven against the real validator over the whole corpus rather than asserted ([[TASK-0296]])
- [x] Terminal requirements are not counted as debt — a cancelled requirement's open boxes are owed to nobody
- [x] Declared criteria with no boxes count at their declared size — zero boxes is "no verification record", not "nothing owed"
- [x] It is a **record card, not a badge** — the gap was invisible, which is the problem; it is not a deadline

## Verification

`tests/test_criteria.py` — 13 tests, five of them for the debt queries. The evidence-free query has a test proving a properly-evidenced tick is *not* counted, because the whole risk of that number is over-reporting a thing that looks like negligence.
