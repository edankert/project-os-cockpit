---
type: "[[issue]]"
id: ISS-0071
aliases: ["ISS-0071"]
title: "Independent review of PHASE-011/012: three new guards pass while what they claim is broken, the design digest invalidates itself, ISS-0037 regressed the browser client, and the staleness correction is incomplete"
status: fixed
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["independent review of 74a2187..16f968b, 2026-07-30 (model:claude-opus-5, fresh context)"]
severity: high
component: docs-system
related: ["[[ISS-0070-Unanchored-Gitignore-Hid-A-Feature]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[ISS-0057-Staleness-Follows-The-Artifact-Only]]", "[[ISS-0069-Review-Verdict-Vocabulary-Is-Unguarded]]", "[[ISS-0037-Library-Root-File-Rows-Are-Dead-Clicks]]", "[[DES-0004-Attention-In-The-Squares]]", "[[TST-0022-Surface-Ownership]]"]
tests: []
---

# Review findings, PHASE-011/012

The `.gitignore` finding is [[ISS-0070]] and is fixed. Everything else the review raised is here, unfixed, so it is not lost. Verdicts recorded on the notes: `changes-requested` on CHG-20260730, PHASE-011, FEAT-0045, ISS-0037, ISS-0057, ISS-0068, ISS-0069; `approved` on PHASE-012, PHASE-013, FEAT-0018, ISS-0024, ISS-0066, ISS-0067.

## 1. Three guards pass while the thing they guard is broken

The recurring class in this repo, and I reintroduced it three times in one commit.

- **`test_unclosed_agrees_with_the_validators_gate`** restates the implementation. `unclosed` *is* `all(state in RESOLVED_STATES)`, and the test asserts exactly that, so it cannot fail. It never reads the validator. Reverting `unclosed` to the bucket-based first cut — the bug it was written for — leaves it green.
- **`test_blocked_is_computed_from_depends_not_from_a_status`** — the docstring claims a behavioural assertion the body never makes. `def _has_unresolved_dependency(rec): return False` passes all 594 tests. And the slice `src.split("def _needs_human")[1].split("def ")[1]` reads *`_has_unresolved_dependency`'s* body, so re-adding `if status == "blocked"` to `_needs_human` passes under the message "_needs_human is reading a blocked status again".
- **`test_review_verdicts_use_a_defined_value`** checks the *union* of the two vocabularies, so it never enforces the context split [[ISS-0069]] says it enforces. Stamping a CHG close-out note `review_verdict: "accepted"` passes.

## 2. `unclosed` is looser than PHASE-CHILDREN after all

The validator's `PHASE_RESOLVED` includes **`risk`**; the phase payload excludes risks entirely (none carry a phase, so DES-0004 put them out of scope — but the gate does not). Reproduced end to end: give `RISK-0001` `phase: PHASE-012` and the payload says `unclosed: true`; follow the pill and `PHASE-CHILDREN` errors. Also `_norm(st) != "done"` vs the validator's `CLOSED_PHASE_STATUSES = ("done", "superseded")`.

## 3. `design_note_digest` invalidates itself

It omits `status`, and `stamp_design_verdict` writes `status` on accept — so recording an accepting verdict changes the digest, which is the exact objection [[ISS-0057]] claims to answer. Measured: `75f3c3b31b1b` → `bf126afd62d7`, sole difference `status: draft → accepted`.

## 4. ISS-0037 regressed the browser client

`static/cockpit.js` has no `extractRel` — it fetches the raw href. Measured: `GET /README.md` → 200 with `<h1>project-os-cockpit</h1>` (correct **before** the change); `GET /~root/README.md` → 404. The server half is sound (traversal blocked, allowlist enforced, no docs fallthrough), but the guard greps `renderer.ts` only, so mode 1 lost a working link while mode 3 gained one.

## 5. The staleness correction is incomplete

The **accepted artifact** still says "9 were last verified 66–83 days ago" and "13 proven, 9 stale". DES-0004's `## Regions` and PHASE-011 still cite it — including an exit criterion demanding "a count against the 22 + 9 measured here", which cannot now be satisfied honestly. Separately, `_staleness_days`'s hand-rolled regex will not read inline-mapping YAML (`verification: {staleness_days: 30}`).

## 6. DES-0004's substance changed after its accepting verdict

The staleness correction was appended in `0e8008a`; the verdict was recorded in `4daa6c1`. No `## Revisions` entry, `design_revision` unchanged. That is precisely the failure ISS-0057 exists for, on the note specifying the fix — and undetected because **`note_moved` has no consumer anywhere**, which ISS-0057 itself disclosed.

## 7. `failing` has no mark and no dot

Enumerated through `_square_state`/`_needs_human`: `failing` is the one legal status that falls through to "not started". A failing test now renders identically to unstarted work — on a strip this change just added tests to, after deleting `appendAsyncWaitingRows`, whose `failing` branch at rank 0 was the overview's only surface for it. DES-0004's table has no row for the `blocked` band at all.

Relatedly, DES-0004's claim that "no precedence rule is needed" is **false**: `cancelled`/`superseded`/`retired`/`declined` are in both `BANDS["archived"]` and the per-type done sets, so the archived-before-done ordering in `_square_state` is load-bearing.

## 8. Smaller

- [[ISS-0068]]'s post-implementation counts do not reproduce at its own commit (390/349/8/7 against the recorded 406/354/6/20); dot and pill counts match. No method was recorded, which is why they cannot be checked.
- `SNAPSHOT.yaml` still gives FEAT-0018, ISS-0066, ISS-0067, ISS-0068 `phase: "[[PHASE-999-Future]]"` while the notes say PHASE-011/012. `sync-snapshot.py` does not propagate `phase:` and the validator does not check it — the same class as the dangling `PHASE-999-Unscheduled` link.
- `REVIEW_SETTLED_STATUSES` covers only `tests`/`changes`, and CHG-20260730 is not registered in `items.changes`, so **no `changes-requested` verdict from this review is visible to the validator**.
- `test_every_des_0004_state_is_reachable` checks presence only: swapping `deferred` ↔ `dropped` passes.

## Next Actions

- [x] Fix the three guards to assert behaviour, not shape. Each must fail when its own bug is reintroduced — demonstrate that, do not assume it
- [x] Decide whether `unclosed` should include risks (agree with the gate) or whether risks should be phaseable (change the corpus). Not both
- [x] Add `status` to the digest's excluded fields, and re-verify the accept path end to end
- [x] Restore the browser client's root-file link, and widen the guard to both renderers
- [x] Finish the staleness correction in the artifact, DES-0004's Regions, and PHASE-011's exit criterion — then re-record DES-0004's revision, since its substance moved after acceptance
- [x] Decide `failing`'s mark, and add the `blocked` band row to DES-0004's table
- [x] Add a "does a fresh clone validate?" check — the gap that let [[ISS-0070]] live
- [x] Propagate `phase:` in `sync-snapshot.py`, or have the validator compare it

## Notes

**PHASE-011 and PHASE-012 are not closed**, and this issue is why. Their work has shipped and their exit criteria are unticked; closing them over a `changes-requested` review would be the box-ticking those phases exist to make impossible.

The pattern worth carrying: every round of review in this repo has found the same class — a claim slightly wider than what was checked — and this round found me writing *guards* with that shape, which is worse than prose having it. [[ISS-0066]] argued that two hand-maintained enumerations of one file are an argument against hand-maintaining either; three self-referential guards in one commit is the same argument about tests that read source instead of running behaviour.


## Resolved 2026-07-30

Every finding addressed, each mutation-verified by reintroducing the bug it was written for.

**The three guards now fail on their own bugs.**

- `test_unclosed_agrees_with_the_validators_gate` is gone, replaced by two: one that **parses the validator's `PHASE_RESOLVED` and `CLOSED_PHASE_STATUSES` and asserts table equality**, and one that builds a probe phase and parks an unresolved note of *each policed type* on it — `task`, `issue`, `requirement`, `feature`, **`risk`** — asserting the close-out offer is withdrawn and restored each time. Dropping `risk` from the payload's table now fails both.
- The blocked guard is behavioural: a probe corpus where an unfinished item depends on an unresolved blocker must carry the dot, and must not once the blocker is `done`. The reviewer's exact mutation (`return False`) fails it. The source half was kept but **narrowed and correctly sliced** — it forbids comparing status to the `"blocked"` literal, not the legitimate `BANDS["blocked"]` membership that `failing` needs.
- The verdict guard enforces the split: desk values are legal only on `[[design]]` notes. Stamping a CHG note `accepted` now fails. A second assertion holds the two vocabularies disjoint, which is ADR-0007's actual guarantee.

**`unclosed` asks the gate, over the gate's population.** New `phase_close_blockers(index, phase_id)` walks every note naming the phase — not the strip's items, whose risk exclusion is a rendering decision. `superseded` now closes a phase too. Reproduced the reviewer's scenario: an open `RISK-0001` given `phase: PHASE-012` makes `unclosed` false and names `RISK-0001` as the blocker.

**Digest.** `status` and `superseded_by` added to the exclusions, and the test widened to stamp *every* field the accept path writes rather than just the verdict.

**Mode 1 restored.** `cockpit.js` translates `~root/X` → `/X`, which is what always worked there — the prefix is a rel-space disambiguator, not an HTTP path. Verified over HTTP: `/README.md` → "project-os-cockpit", `/docs/README.md` → "Docs structure". The guard now greps **both** clients.

**Staleness correction completed** in the accepted artifact (both places, and its test-strip render now shows 21 delivered + 1 unproven rather than "13 proven, 9 stale"), DES-0004's `## Regions`, its Approach paragraph, and PHASE-011's exit criterion.

**`failing` carries the dot**, via `BANDS["blocked"]` — a failing test is an outstanding human action in exactly the dot's sense, so it needs no new mark. Guarded by a per-type sweep over the **validator's `ALLOWED_STATUS`** table. Two earlier versions of that sweep were themselves wrong — one asked `is_done_status("test", "done")` and reported the whole done band; the next swept the full cross product and reported 46 impossible pairs like `("issue", "merged")`. A sweep over impossible inputs is noise, and noise gets suppressed.

**DES-0004's precedence claim corrected.** "No precedence rule is needed" was false: `cancelled`/`superseded`/`retired`/`declined` are in both `BANDS["archived"]` and the per-type done sets, so testing archived first is load-bearing. Reversing the order now fails `test_the_module_twins_agree_with_the_payload`. The `blocked` band row was added to the table, and a `## Revisions` entry records that the note's substance changed after its accepting verdict.

**Snapshot phase drift** fixed on five entries and guarded — the sync script is template-owned (ISS-0026), so the check lives here.

**Fresh-clone gap closed** by `test_every_docs_note_is_tracked_by_git`, verified against ISS-0070's exact shape (un-anchored pattern *plus a new note*). Its limit is disclosed in the test: it sees ignored-and-untracked files, not files already tracked when a pattern starts matching them.

**ISS-0068's counts** re-measured *with the method written down*, which the original lacked — that absence is why the reviewer could not tell a miscount from a different population.

600 passed, 1 skipped. `tsc` clean. Validator clean. A fresh clone validates clean.
