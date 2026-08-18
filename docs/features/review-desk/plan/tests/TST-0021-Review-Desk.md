---
type: "[[test]]"
id: TST-0021
aliases: ["TST-0021"]
title: "Review desk — queue without new states, guarded note write-back, manual-run logging"
status: passing
covers: ["[[FEAT-0041-Review-Desk]]", "[[TASK-0206-Review-Virtual-Page]]", "[[TASK-0207-Proposal-Set-Review]]", "[[TASK-0209-Manual-Test-Runner]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-08-13
source: ["[[TASK-0207-Proposal-Set-Review]]"]
path: "tests/test_review_desk.py"
command: ".venv/bin/pytest tests/test_review_desk.py -q"
automation: automated
last_verified: "2026-08-10"
reviewed_by: model:claude-fable-5
review_date: 2026-07-26
review_verdict: approved
last_run: "2026-08-13T18:28Z"
exit_code: 0

---

# TST-0021 — Review desk

## Intent

The desk is the first cockpit surface that *writes* notes. PHASE-007 drew the line at "the cockpit is a viewer"; ADR-0007 crosses it only far enough to record a decision a human made in the UI. Everything in this suite exists to keep that crossing narrow and to prove the two structural promises the desk was designed around.

## The two promises

**No new states.** Owner decision, 2026-07-26: the desk introduces no status anywhere. The tests assert the mechanism that makes that possible — proposal sets queue as runtime review requests while their notes stay at plain `backlog`, ADRs/requirements/tests queue on their existing intake states (`proposed`/`draft`/`ready`), acceptance stamps the existing independent-review fields, and rejection uses the existing `cancelled`. One test reads the feature note off disk after queueing it, specifically to prove the queue left it alone.

**Plan acceptance is not close-out review.** The same three frontmatter fields now carry two meanings, so the verdict values must stay distinguishable: the desk writes `plan-accepted` and *refuses* `approved`, which is close-out's vocabulary (QUALITY.md). Without that refusal, having one's plan approved would satisfy the gate that guards verification. This is asserted directly, and it is the single most important test in the file.

## Hardening (TASK-0207 DoD, folded in from the preflight risk scan)

- **Field allow-list** — asserted as a literal set, so widening it is a deliberate, reviewed change rather than a drive-by.
- **Guarded transitions** — a status outside `statuses.py` is refused; so is a real vocabulary member the endpoint has no business writing (`done`, `doing`, `implemented`).
- **Path canonicalisation** — unknown ids 404; traversal attempts (`../../etc/passwd`, absolute paths, empty) refuse before touching the filesystem.
- **Concurrency** — a stale `mtime` precondition returns 409 with nothing written, so a note edited underneath the reviewer is never silently clobbered.
- **Snapshot untouched** — ADR-0009: the endpoint writes notes, `sync-snapshot.py` propagates at pre-commit. A test writes a snapshot file and asserts it is byte-identical afterwards.

Non-loopback callers are refused in `server.py` (`_require_loopback`) rather than in the writer, so it is asserted at the handler level — `test_mutation_endpoints_reject_non_loopback_callers` checks all four mutation endpoints consult the guard and pins `_LOOPBACK_HOSTS`. Note the wording: this is a per-request peer-address check on the shared 0.0.0.0 socket, **not** a second loopback bind like the terminal endpoint's.

## Manual-run logging

Passing and failing runs stamp `status` + `last_run` (and `last_verified` only on a pass); an aborted run writes **no** status but still appends its partial log, because a half-finished run is not evidence either way. A second run appends rather than replacing, so `## Runs` reads as a chronological log. A failing step produces an issue draft — returned as data for the user to confirm, never filed automatically, since allocating an ID is a documentation decision that LIFECYCLE puts in preflight.

**Corrected 2026-08-10 ([[TASK-0372]]).** That last sentence was true of `draft_issue_body` and false of the system: the function existed, `test_failing_step_drafts_an_issue_for_confirmation` exercised it directly, and **nothing else in the tree called it** — `stamp_test_run` returned `id` / `outcome` / `last_run` and no draft, so no run ever produced one. The runner's own summary said one "will be offered" and none was. It is true now: `POST /api/notes/test-run` returns `issue_draft` on a completed failing run and the Tests view offers it, still never filing. Asserted end to end over HTTP by `test_a_failing_run_returns_the_draft_it_always_promised`, with `test_only_a_completed_failure_carries_a_draft` holding the two cases that must not produce one.

The runner itself moved to the Tests view in the same task. What it writes did not — `test_a_run_writes_what_it_always_wrote` re-runs the round trip against the real handler and asserts the note is untouched line for line outside `status` / `last_run` / `last_verified` / `updated`, with the new entry landing at the end of `## Runs` rather than the end of the body.

## The parser follows the corpus

One test earns its place by having caught a real defect. The step parser first accepted only `## Steps`, matching the template — but this repo's own [[TST-0011-Live-Session-Instrumentation]], the acceptance demo for the runner, heads its procedure `## Checklist` with inline `Expect:` clauses and bold lead-ins. The parser now accepts the corpus's spellings, which is the same lesson [[ADR-0006-Retire-Delivered-Band]] recorded: a surface follows what is written, not what a convention wishes were written.

## Running it

```
.venv/bin/python -m pytest tests/test_review_desk.py -q
```

## Result

Passing as of 2026-07-26 (30 tests). The end-to-end UI path — queue → proposal set → accept, and queue → run → stepper → record — was exercised against the built bundle in `desktop/harness/overview-harness.html`.

## Independent review (2026-07-26)

Authored by a Claude-family session (Opus); reviewed by model:claude-fable-5 — same model family, so this pass is harm reduction, not the different-family review QUALITY.md requires. A cross-vendor or human pass should be recorded before this note's verdict is treated as settled.

Verdict **changes-requested**. The suite is real and its manual-run/transition/traversal tests genuinely guard, but four claims in this note overstate what is asserted:

1. **Loopback is not tested anywhere.** The note says loopback enforcement "is asserted at the handler level" — no test in the repo touches `_require_loopback` or posts from a non-loopback peer, and TASK-0207's DoD lists "loopback-only binding" under *Endpoint tests*. It is also enforcement by peer-address check on the 0.0.0.0-bound socket (`server.py:1155-1163`), not a loopback *bind*.
2. **The allow-list test asserts a decorative constant.** `ALLOWED_FIELDS` (`note_writes.py:57`) is consumed by no implementation code — the payload-key rejection lives in independently duplicated literal sets in `server.py:1297` and `server.py:1333`, which the suite never exercises (no test goes through HTTP), and the writer also stamps `updated` (`note_writes.py:203,257`), which is outside the asserted set. Widening the real surface would not fail `test_only_allowed_fields_are_writable`.
3. **"Plan acceptance cannot satisfy the close-out gate" is only enforced against the literal string `approved`.** The mechanical gate (`tools/scripts/validate-docs.py:977-985`) accepts any verdict other than `changes-requested`/empty — a `plan-accepted` stamp on a `passing` TST or `merged` CHG (reachable, since review requests accept arbitrary item ids) silences the ADR-0011 review check. The desk-side refusal is tested; the gate it claims to protect is not actually protected.
4. **`_set_field` corrupts block-scalar frontmatter**: replacing `status: >` leaves the orphaned continuation line in place (verified against `note_writes._set_field`), producing invalid YAML. Not reachable on this template-shaped corpus today, but the "nested structures are left byte-identical" safety claim is broader than the code.

### Re-review (2026-07-26, second pass) — approved

All four findings verified fixed in the working tree, not taken on trust: (1) `test_mutation_endpoints_reject_non_loopback_callers` asserts the guard on all four mutation handlers (a source-level assertion plus a loopback sanity POST — honest about being a static check, since http.server cannot spoof a peer address) and `_serve_review_request` now requires loopback; (2) `server.py` consumes `note_writes.REVIEW_REQUEST_KEYS` / `TEST_RUN_REQUEST_KEYS` and a test pins that consumption, `updated` is declared in `ALLOWED_FIELDS` rather than written silently; (3) `stamp_review` refuses gate-bearing note types (`test`, `change`) with 403 — `test_desk_refuses_to_stamp_gate_bearing_notes` — closing the path by which a plan verdict could reach a note ADR-0011 reads; (4) block-scalar values now 409 instead of corrupting (`test_multi_line_frontmatter_values_are_refused_not_mangled`), and `plan-rejected` exists so a rejection no longer stamps an acceptance verdict. Suite re-run: 304 passed, 1 skipped; validate-docs OK.

Residual accuracy nits, not blocking: the Result line above still says "23 tests" (the file now holds 30); the phrase "Loopback-only binding" above should read "per-request loopback guard" (the note_writes docstring and TASK-0207 line 29 were corrected, this line and TASK-0207's test-list line were not); and this note's prose predates the gate-bearing and `plan-rejected` guards it now relies on. Same-family caveat stands: reviewed by model:claude-fable-5 against Claude-authored work — record a cross-vendor or human pass to make this independent per QUALITY.md.

## Runs

### 2026-08-10 — passing (by model:claude-opus-5)
- **pass** · Re-run for REL-0001 release verification: `.venv/bin/python -m pytest tests/test_review_desk.py -q` — 37 passed in 0.68s
