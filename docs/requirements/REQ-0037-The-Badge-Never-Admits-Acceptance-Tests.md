---
type: "[[requirement]]"
id: REQ-0037
aliases: ["REQ-0037"]
title: "The obligation badge never admits acceptance tests — the merge must not put 669 self-re-arming rows in front of a person"
status: implemented
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "obligation registry"
implements: "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"
acceptance:
  - "[x] After the merge, the Tests badge in every repo reads what it read before it — measured per repo. `obligations.owed_items` returns 3 in this repo (TST-0024/0029/0030), the same three manual notes that were `ready` beforehand; zero of the 34 migrated notes reach it. The other repos are unmigrated and unchanged."
  - "[x] No acceptance test appears in `obligations.owed_items` in any repo, at any status. Held by construction — `_is_owed` is keyed on `ready` and these rest at `active` — and asserted rather than trusted."
  - "[x] A guard fails loudly if an acceptance test ever reaches a status the Run obligation counts. `ACCEPTANCE-STATUS` is a validator ERROR, in both the canonical and bundled validators, exempting only a note that declares a `command:` — which is a note that has been automated and whose status the runner owns."
covers: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0028-Work-Has-Three-Phases]]"]
---

# The badge never admits acceptance tests

[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] called acceptance rows *"the most self-re-arming population in the corpus"* and forbade per-check obligations. [[ADR-0030]] honoured it by giving checks their own type; [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] takes the type away and must honour it another way.

**It does so by construction, not by exemption.** `_is_owed` requires `status in ("ready",)` for a test; an acceptance test rests at `active`. The requirement exists because that construction is one careless status write away from failing, and the failure mode is 669 rows arriving on a badge at once.

**This is the single highest-risk invariant in the merge.** Everything else is recoverable by editing notes; this one is recoverable only after somebody has seen a number they cannot act on, which is the exact harm ADR-0027 exists to prevent.

## Acceptance criteria

- [x] **After the merge, the Tests badge reads what it read before it — measured per repo.** `obligations.owed_items(index)["tests"]` returns **1** (`TST-0024`), which is what the pre-merge code returned against the pre-merge corpus.

  *This criterion was ticked on 2026-08-18 while it was **false**, and the correction is the most important sentence in this note.* The badge had moved **1 → 3**, and not because of the acceptance notes: `obligations.SUBJECT_FIELDS["test"]` still named `verifies`/`features`/`requirements`, all three of which ADR-0032 deleted. So `subject_ids` resolved nothing for **77 of 77** tests, and `subject_is_in_flight` treats a subject-less note as live **by design** — which switched ADR-0028's in-flight quieting off for the entire test population. A rename missed in one table, disarming a rule two ADRs away, reported by nothing. Found by independent review; `covers` is now first in that tuple and `test_a_tests_subject_fields_track_the_link_rename` fails if a future rename does the same.
- [x] **No acceptance test appears in `obligations.owed_items`, at any status.** Held by construction: `obligations._is_owed` requires `status in ("ready",)` for a test and an acceptance test rests at `active`.
- [x] **A guard fails loudly if one ever reaches a status the `Run` obligation counts.** `ACCEPTANCE-STATUS` is a validator **ERROR** in both the canonical and the bundled validator, exempting only a note carrying a `command:` — which is a note that has been automated and whose status the runner owns.

## Advanced 2026-08-18

Satisfied, and the fleet clause is satisfied *narrowly*: two repos are unmigrated, so their badges are unchanged trivially. The claim this requirement actually needed to make — **a migration does not move the badge** — is demonstrated on the only repo that has run one, with 34 notes and a badge that did not move.
