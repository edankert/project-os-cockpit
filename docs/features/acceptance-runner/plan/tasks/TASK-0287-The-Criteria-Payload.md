---
type: "[[task]]"
id: TASK-0287
aliases: ["TASK-0287"]
title: "The criteria payload — a feature's requirements' criteria with their resolved states, from the parse the validator already trusts"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# The criteria payload

## Definition of Done

- `GET /api/notes/acceptance?id=FEAT-…` returns each requirement's criteria with state (open / ticked / reconciled), witness and evidence where present.
- The parse is shared with or fixture-proven identical to REQ-BOXES — a criterion the validator counts is a criterion the runner walks, always.
- A feature with no criteria returns the nothing-to-accept answer, which FEAT-0065 counts as debt.

## Done — 2026-08-11

`GET /api/notes/acceptance?id=FEAT-…`, built on `src/project_os_cockpit/criteria.py`.

**The identity claim is proven, not asserted.** The DoD allowed "shared with **or fixture-proven identical to** REQ-BOXES". Sharing was not available: the validator is a standalone script under `tools/scripts/` with no package imports, so CI can run it from a bare checkout, and importing it into the package would invert that. So `criteria.py` restates it and `test_the_parse_is_identical_to_req_boxes_across_the_corpus` loads the real `validate-docs.py` and compares both parses **requirement by requirement over the whole live corpus** — stronger than fixtures, which only prove the cases someone thought of.

Why it matters concretely: if they diverged, a person could finish a run and still be refused at close-out by REQ-BOXES, or tick past a criterion the gate never saw.

**Two things the investigation got wrong on first reading, both corrected:**

1. **Requirements link by `specifies:` as well as `implements:`** — 20 and 25 uses respectively, and they mean different things. `implements:` names the one owning feature (ADR-0007, enforced by REQ-OWNER); `specifies:` names every feature the requirement constrains and is routinely plural (REQ-0026 specifies FEAT-0059 *and* FEAT-0060). Accepting a feature walks everything that constrains it, so both count. The first cut read only `implements:` and returned **zero** requirements for FEAT-0059.
2. **Criteria have two representations.** `acceptance:` in frontmatter is the criteria *of record*; the body's checkboxes are the *verification* record. REQ-BOXES compares them, and "criteria with no boxes" is its second error — exactly the state a runner exists to move out of. So when a requirement declares criteria and has no boxes, the payload surfaces the declared text as `open`. Otherwise FEAT-0063's own requirement (REQ-0028, four criteria, no boxes) would have presented as *nothing to accept*, which is the opposite of the truth.

**Three states, not two.** `- [~]` is a first-class answer: `STATUSES.md` gates on *"ticked-with-evidence OR reconciled"*, so a runner offering only pass/fail would have no way to record the honest third answer and would push people to tick things they did not do.

Witness and evidence are read back per criterion (REQ-0028) — `(user:edwin, 2026-08-10)` parses to a witness and a date, so a re-run shows who settled a criterion rather than presenting it as anonymous. Evidence splits on the **last** em dash, because criteria routinely contain one mid-sentence.

Live against the corpus: FEAT-0059 → 2 requirements, 8 ticked + 1 reconciled; FEAT-0063 → 4 open; FEAT-0073 → `nothing_to_accept`.
