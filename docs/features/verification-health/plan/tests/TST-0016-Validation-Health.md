---
type: "[[test]]"
id: TST-0016
aliases: ["TST-0016"]
title: "Validation health — endpoint states, drift deep-links, SSE fan-out, badge flags"
status: passing
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-17
updated: 2026-07-18
scope: feature
kind: automated
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_validation.py"
features: ["[[FEAT-0018-Verification-Health-Surface]]"]
tasks: ["[[TASK-0111]]", "[[TASK-0113]]"]
adequacy: "2 mutation runs 2026-07-17, both killed: (1) suppress the first-run SSE publish in ValidationRunner._observable_changed → test_no_sse_when_result_unchanged fails; (2) remove the /api/cockpit/validation route from server.py → 5 tests fail (endpoint states + schema-header matrix). Suite restored green after each revert."
reviewed_by: "model:claude-opus"
review_date: 2026-07-18
review_verdict: approved
---

# TST-0016 — Validation health

## Purpose

Guard the FEAT-0018 server surface: the `/api/cockpit/validation` endpoint (TASK-0111), its watcher-driven debounced re-run + `cockpit:validation` SSE fan-out, and the verification badge flags on nav/context item payloads (TASK-0113).

## What it verifies

`tests/test_validation.py` (11 tests): report-line parsing (`ERROR [CODE] msg` / `WARN  [CODE] msg` with project-os ID + repo-relative-path extraction, explicit `None` when absent); validator locate order (browsed repo's `tools/scripts/validate-docs.py` preferred, bundled package copy as fallback); wire shapes for all three states — `ok` on a clean fixture repo, `failing` with an induced snapshot↔note status drift carrying a resolver deep-link `url` per error, `unavailable` (validator exit 2, no SNAPSHOT.yaml); ok→failing flip through `ValidationRunner.refresh()` serving the cached report; a docs `FileEvent` on the shared bus scheduling a debounced re-run whose state change arrives as a `cockpit:validation` SSE event; no duplicate SSE when the observable result is unchanged; a schedule() burst coalescing into exactly one validator run (timer-cancel debounce); `_verification_flags` riding nav items (`waived`, `review_verdict`, and `adequacy` presence/absence on `test` notes); and the metadata-strip chip render (`templates._metadata_strip_html`: waiver chip next to the status chip + on the waiver row with its reason text, `data-verdict` chip for `review_verdict`, no waiver chip without a waiver). `tests/test_schema_header.py` additionally asserts the endpoint emits `X-Cockpit-Schema`.

## Expected results

- All 11 tests pass; the schema-header matrix row for `/api/cockpit/validation` passes.

## Evidence

- 2026-07-17: `9 passed` in `tests/test_validation.py`; full suite `199 passed, 1 skipped` (the pre-existing dirty-tree skip in `test_release.py`).
- 2026-07-18: independent review requested two additional guards (debounce coalescing, metadata-strip chip render); `11 passed` in `tests/test_validation.py`, full suite `201 passed, 1 skipped`.
- 2026-07-17: manual smoke against this repo's own docs (`127.0.0.1:8931`): `GET /api/cockpit/validation` → `200`, `X-Cockpit-Schema: 3`, `{ok: true, state: "ok", errors: [], warnings: [PATH-ALIAS], checked_at, schema_version: 3}`; served cockpit HTML carries the `cockpit-health-slot` chrome slot; `?mode=library` nav payload carries `adequacy` flags on all 15 TST items.

## Adequacy (who verifies this test?)

See `adequacy` frontmatter — two deliberate mutations (SSE fan-out suppressed; endpoint route removed) each made the suite fail, so the tests demonstrably guard the behaviour they claim to.
