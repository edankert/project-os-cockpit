---
type: "[[test]]"
id: TST-0020
aliases: ["TST-0020"]
title: "Overview payloads — focus block, issue severity, commits join, and sidecar-owned status buckets"
status: active
covers: ["[[FEAT-0040-Overview-Rework]]", "[[TASK-0199-Sidecar-Payload-Additions]]", "[[TASK-0200-Overview-Stage-Rework]]", "[[REQ-0022-Overview-State-Above-History]]"]
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-08-13
source: ["[[TASK-0199-Sidecar-Payload-Additions]]"]
path: "tests/test_overview_payloads.py"
command: ".venv/bin/pytest tests/test_overview_payloads.py tests/test_status_vocabulary.py -q"
automation: automated
last_verified: "2026-08-10"
reviewed_by: model:claude-fable-5
review_date: 2026-07-26
review_verdict: approved

---

# TST-0020 — Overview payloads

## Intent

The overview rework moved three new facts into `stats_payload` and added one endpoint. Each is small; each is also the kind of thing that rots silently, because a missing field renders as an absent band rather than an error. This suite pins the shapes and — more importantly — the two judgement calls behind them.

## What it covers

**The focus block.** Resolution against the index (title, status, type, rel, done), the empty-slot case, and the note's leading date, which the renderer turns into a staleness label. One case is deliberate rather than defensive: a focus pointing at a deleted note degrades to the bare id instead of dropping the slot, because a dangling pointer is exactly the thing a reader should see.

**Issue severity.** Present on issue items, absent on every other type — the payload does not carry a field that means nothing for the note it describes.

**The commits join.** Commits resolve to items through the index by `rel_path`, completions are marked with the same per-type `is_done_status` the hero counts use, and a commit that touched no notes is flagged `undocumented` (FEAT-0022's guardrail, per commit). The hardening promises are asserted as behaviour: `limit` clamps rather than reaching git as a string, a non-repo workspace degrades to `available: false`, and files outside the docs tree never resolve to items.

**Status buckets — the ISS-0023 guard.** The bucketing lives in `tests/test_status_vocabulary.py` rather than here, and that placement is the point. TASK-0200's first implementation classified statuses into done/doing/attention/backlog inside `renderer.ts`, which would have made the renderer a ninth surface restating the vocabulary — the precise failure ISS-0023 was filed about. The bucketing moved into `stats_payload` (computed from `is_done_status` + `statuses.band_of`), and the parity suite now fails if `renderer.ts` grows a per-type done table again.

## Running it

```
.venv/bin/python -m pytest tests/test_overview_payloads.py tests/test_status_vocabulary.py -q
```

Both run in CI with the rest of the suite. The commits tests build a real git repository in a temp directory — they are skipped by nothing and require `git` on PATH, which the sidecar already assumes.

## Result

Passing as of 2026-07-26 (34 assertions across the two files' overview-related tests, inside a 296-test suite).

## Independent review (2026-07-26)

Authored by a Claude-family session (Opus); reviewed by model:claude-fable-5 — same family, so this is not the different-family review QUALITY.md requires; a cross-vendor or human pass should still be recorded.

Verdict **approved**: the suite runs green (re-run 2026-07-26, 296 passed / 1 skipped), the commits tests build real git repositories and would fail on a real regression (join, clamping, non-repo fallback, undocumented flag all exercised against behaviour), the focus-block edge cases are deliberate, and the bucket-parity test is a genuine cross-surface guard. One accuracy note for the record: this note honestly says completions are marked "with the same per-type `is_done_status`" — i.e. the item's *current* status — which is correct about the code but weaker than TASK-0199's DoD wording ("status-diffing adjacent revisions"); the discrepancy is the task note's problem, not this one's.

Second pass (same day): verdict stands. TASK-0199's DoD was amended to describe the current-status semantics honestly (with the cost named), which resolves the one discrepancy above; suite re-run at 304 passed / 1 skipped after the review-fix batch, this file unchanged and still green.

## Runs

### 2026-08-10 — passing (by model:claude-opus-5)
- **pass** · Re-run for REL-0001 release verification: `.venv/bin/python -m pytest tests/test_overview_payloads.py tests/test_status_vocabulary.py -q` — 37 passed in 0.45s
