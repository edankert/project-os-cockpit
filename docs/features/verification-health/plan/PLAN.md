# Plan: Verification health surface (FEAT-0018)

## Sequence
1. [[TASK-0111]] — server side first: validation endpoint + watcher-triggered re-run + SSE fan-out. No UI dependency; testable via curl.
2. [[TASK-0112]] — health badge + drift panel consuming the endpoint. Depends on TASK-0111.
3. [[TASK-0113]] — waiver/review/adequacy badges. Independent of TASK-0111/0112 (frontmatter-driven), can proceed in parallel.

## Design notes
- Reuse `tools/scripts/validate-docs.py` from the browsed repo when present (guaranteed after template sync); fall back to the copy shipped with the cockpit's own repo. Never reimplement checks in cockpit code — single source of validation logic.
- Validator runs are cheap (stdlib, one pass over docs/) but debounce watcher-triggered re-runs (e.g. 1s) so bulk edits do not thrash.
- Badge colours follow the existing status palette; do not invent new colour semantics.

## Verification
- TST note to be authored at implementation time (per test-authoring skill) covering: endpoint payload shape and schema header, badge flip on induced drift, deep-link navigation, and badge rendering for waiver/review/adequacy fixtures.
