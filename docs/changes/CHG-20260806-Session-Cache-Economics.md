---
type: "[[change]]"
id: CHG-20260806-Session-Cache-Economics
aliases: ["CHG-20260806-Session-Cache-Economics"]
title: "The strip says what a session weighs and whether its cache is still warm; a new endpoint says what re-writes have cost"
status: merged
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/session_cache.py", "src/project_os_cockpit/agent_hooks.py", "src/project_os_cockpit/server.py", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/index.html", "desktop/src/renderer/renderer.css"]
issues: ["ISS-0104"]
features: ["FEAT-0081"]
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-06
review_verdict: changes-requested
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]", "[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]"]
---

# The strip says what a session weighs and whether its cache is still warm

## Summary

Edwin asked whether prompt-cache staleness could be identified, highlighted, or automated away. The work began by **measuring rather than reasoning from the pricing table**, and the measurement changed what got built.

Across 42 transcripts under `~/.claude/projects/` (21,862 deduplicated assistant turns, 2026-08-06, reproducible with `python3 tools/scripts/scan-cache-economics.py`): cache **reads** account for ≈$5,340 of ≈$6,788 input-side spend; cache **writes** ≈$1,448. Of the writes, avoidable full-prefix re-writes cost ≈$336 — ≈$250 to TTL expiry after >60 min idle, ≈$86 to sub-hour invalidation. So **staleness — the cache lapsing on its own clock — is 3.7% of the input bill, and all avoidable re-writes together are 4.9%**, while the weight of the context itself is the 20× larger lever and appears nowhere in the UI (`ctx 62%` is fill against the window, not tokens, and not cost).

New module `session_cache.py` reads the transcript the tracker has stored a path to since FEAT-0019, and derives: prefix weight, cache age against the TTL the cache was written under, the cost of the next turn warm against cold, and a classification of every full-prefix re-write. Two entry points — a **bounded tail read** for the live badge (transcripts here reach 34MB and the strip re-renders on every snapshot) and a full streaming scan for the retrospective, both memoised against `(path, mtime, size)`.

Of the 14 sub-hour re-writes, **8 carried a different model than the preceding turn** — the cache is model-scoped, so switching model discards the whole prefix ([[ISS-0104]]). That is now named where it happens.

**One thing was deliberately not built.** A keep-warm ping costs 2× the full prefix *every ping*, against 2× *once* for letting the cache expire — so background re-warming is strictly more expensive than doing nothing, and `max_tokens: 0` pre-warming pays the same write. The obvious feature request would have raised the bill. It is recorded as an explicit non-goal in FEAT-0081 and in PHASE-007's scope, because it will be proposed again.

## Impact

- **New:** `GET /api/cockpit/session-cache` — retrospective per-workspace accounting, split by cause (`ttl-expiry` / `model-switch` / `other` / `session-start`). Costs are estimates from a per-family price table; the token counts beside them are exact.
- **Changed:** `/api/cockpit/state` gains an optional `cache` block for the session being shown. Absent when there is no transcript, no usage data, or an unreadable file — never an error.
- **Changed:** the agent strip gains two spans — prefix weight (`610k`) and cache standing (`warm` / `cooling 12m` / `cold · ~$6.10`, or `model switch · ~$6.05`). Only the cold and cooling states take colour; a badge that is always lit stops being read.
- **No behavioural change to ingestion, dispatch, or any existing surface.** Nothing in this change issues an API request.
- Cost figures render with `~` and two decimals throughout. They are derived from a hard-coded price table that drifts, and must not be read as billing.

## Documentation Coverage (All Types Considered)

- features: new — [[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]
- requirements: not-applicable
- tasks: new — TASK-0343, TASK-0344, TASK-0345
- issues: new — [[ISS-0104-Model-Switch-Discards-The-Warm-Cache]] (filed and fixed)
- tests: new — `tests/test_session_cache.py` (19), `tests/test_session_cache_surface.py` (7). No `TST-*` note: these are automated tests, and the feature gates on no manual verification.
- workflows: not-applicable
- decisions: not-applicable — the no-keep-warm rule is recorded in the feature and the phase rather than as an ADR, because it is arithmetic rather than a choice between options. Promote it if a second surface ever wants to warm a cache.
- risks: not-applicable — read-only file parsing of a path the tracker already stores; no new dependency, env var, or credential surface.
- changes: this note
- snapshot: updated — counters, `items.features/tasks/issues`, focus, PHASE-007 reopened and re-closed

## Follow-ups

- [ ] The retrospective endpoint has no surface. It was built because it is what turns an invisible cost into a number, but where it renders on the overview is deliberately unresolved until there is a number to look at (PLAN.md, open questions).
- [x] ~~Independent review is owed~~ — run 2026-08-06, returned `changes-requested`; the seven findings are fixed under TASK-0348…TASK-0353 and the figures above are the corrected ones.
- [ ] The price table in `session_cache.py` drifts with published pricing and nothing detects that. Cheap to correct, invisible when wrong.
- [ ] `warm` is a claim the reader cannot prove — entries can be evicted before their TTL, and 6 of the 14 measured sub-hour re-writes had no model change to explain them. The wording says "elapsed against the known TTL" rather than asserting presence; if that proves misleading in use, the honest fix is to weaken the word rather than the measurement.

## Independent review — 2026-08-06 (changes-requested)

Reviewed by `model:claude-opus-5` from a fresh session with no access to the authoring session's reasoning; authored by `model:claude-opus-5` (same model family, different context — ADR-0013). Suites re-run green: `pytest` 764 passed / 1 skipped, `validate-docs.sh` OK. Verdict is **changes-requested** on the findings below, filed as issues.

- [[ISS-0106]] (**high**) — Claude Code's `<synthetic>` API-error placeholders are read as real turns. Two of the ten model switches in the fleet retrospective are ECONNRESET artefacts whose real cause is TTL expiry with no model change, and the live badge will render `Switching <synthetic> → claude-opus-5`.
- [[ISS-0107]] — a model switch on the last turn suppresses the warm/cooling/cold word permanently, and paints a warm session in the cold colour.
- [[ISS-0108]] — an entry with no timestamp yields `state: cold` with a 56-year age; the Python reader has no `unknown`, which is the principle its own TypeScript half states.
- [[ISS-0109]] — the bounded tail read has no guard: replacing it with a full-file read leaves all 26 tests green, including the one whose docstring claims boundedness. Mutation table in the issue.
- [[ISS-0111]] — the quoted figures do not reproduce (sub-hour re-writes fell from 17 to 16 and model switches from 11 to 10 against data that only grows), no scan script was committed, and `$336 / $6,731` is 5.0%, not the ~3.5% quoted here.

What held up under attack: the dedupe, the cost multipliers, the mtime memoisation re-ageing on a cache hit, the TTL-before-model-switch classification order, and every degradation path (absent, empty, truncated, usage-free). The anti-feature reasoning is correct and worth the space it takes.
