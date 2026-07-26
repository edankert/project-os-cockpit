---
type: "[[issue]]"
id: ISS-0026
aliases: ["ISS-0026"]
title: "The bundled validator is guarded against local drift but not against upstream template lag — it was 10 lines behind project-os"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-25
updated: 2026-07-25
component: tooling
source: ["review:2026-07-25-fleet-state-audit"]
related: [ISS-0025]
tests: []
---

# Bundled validator has drifted

## Problem

`src/project_os_cockpit/validate_docs_bundled.py` is a **copy** of the template's `tools/scripts/validate-docs.py`, not a call into it. It carries its own `ALLOWED_STATUS`, its own `FEATURE_REQ_GATE_FROM = "2026-07-25"`, and its own `ITEM-STATUS` / `COUNTER` / `METRICS` / `REQ-*` / `FEATURE-REQ` check implementations.

So validator logic exists in **three** places across the fleet:

1. `project-os/tools/scripts/validate-docs.py` — the template original
2. each downstream repo's synced copy of it (10 repos)
3. this bundled copy inside the cockpit package, which then ships back into all 10 repos via `tools/cockpit/`

The bundled copy is **875 lines against the template's 885**. It is already behind, and nothing detects that.

## Repro

```bash
wc -l src/project_os_cockpit/validate_docs_bundled.py \
      ../project-os/tools/scripts/validate-docs.py
diff  src/project_os_cockpit/validate_docs_bundled.py \
      ../project-os/tools/scripts/validate-docs.py
```

## Correction (2026-07-25)

The original text of this issue claimed "no parity check" and "nothing detects that". **That was wrong**, and the correction matters because it changes what the real gap is.

`tests/test_status_vocabulary.py::test_bundled_validator_matches_the_canonical_one` already asserts byte-equality between `validate_docs_bundled.py` and this repo's `tools/scripts/validate-docs.py`. It was added by the CHG-20260717 follow-up precisely because the bundle had fallen behind ADR-0007.

What that test compares is **this repo's own** copy, not the upstream template's. So local drift was guarded; what was unguarded is **sync lag** — the cockpit's `tools/scripts/validate-docs.py` sitting 10 lines behind `project-os`, with the bundle faithfully matching the stale copy and the test passing throughout.

## Expected

The bundle tracks this repo's validator (already guaranteed), and this repo's validator does not silently fall behind the template.

## Actual (before the fix)

Both copies here were 10 lines behind `project-os/tools/scripts/validate-docs.py`, and the test passed because they agreed with each other.

## Impact

- **The cockpit's in-app validation can disagree with a repo's pre-commit and CI**, which run the template-synced validator. A user sees green in one surface and red in another with no indication which is authoritative.
- Sync lag is invisible: the local parity test passes while both copies are equally stale.
- It was about to get much worse. Upstream `project-os-dev` [[PHASE-0002]] retires `ITEM-STATUS`, `COUNTER` and `METRICS` entirely (ADR-0009), collapses `ALLOWED_STATUS` (ADR-0008), and re-severities every remaining check (ADR-0011). Each of those lands in the template; none reaches this file automatically.

## Options

1. **Import rather than bundle** — read the host repo's own `tools/scripts/validate-docs.py` at runtime. One copy per repo, always the version that repo's CI enforces. Cost: the cockpit must tolerate version skew across repos.
2. **Generate the bundle** from the template with a `--check` mode in CI that fails on divergence. Matches the existing `generate-adapters.py --check` idiom, so both the machinery and the convention already exist here.
3. **Keep both, add a parity test.** Cheapest and weakest — detects drift without preventing it.

Option 2 fits this repo's conventions best.

## Evidence

- `validate_docs_bundled.py:64` `ALLOWED_STATUS`, `:127` `FEATURE_REQ_GATE_FROM`, `:586` `ITEM-STATUS`, `:765` `COUNTER`, `:784` `METRICS`
- Template equivalents at `../project-os/tools/scripts/validate-docs.py:64`, `:127`, `:586`, `:775`, `:794`

## Resolution (2026-07-25)

- Both copies refreshed from the template as part of upstream PHASE-0002: `tools/scripts/validate-docs.py` re-synced, then `validate_docs_bundled.py` re-copied from it. The existing parity test caught the bundle the moment the first copy landed — the mechanism worked exactly as designed.
- The taxonomy collapse (ADR-0008), the retired `ITEM-STATUS`/`COUNTER`/`METRICS` checks and the grandfather ledger are all present in both copies.
- Full suite green: 253 passed, 1 skipped.

**Residual, deliberately not closed by this issue:** nothing yet detects *upstream* lag. `sync-project-os.py` reports a diverged template-owned file, but only when a sync is actually run. Option 2 from the list above — generate the bundle with a `--check` mode, matching the `generate-adapters.py --check` idiom — remains the right structural answer and is tracked upstream by `TASK-0074`.
