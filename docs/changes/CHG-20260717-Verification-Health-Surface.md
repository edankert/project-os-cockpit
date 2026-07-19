---
type: "[[change]]"
id: CHG-20260717-Verification-Health-Surface
aliases: ["CHG-20260717-Verification-Health-Surface"]
title: "Verification health surface — /api/cockpit/validation, health badge + drift panel, waiver/verdict/adequacy chips"
status: merged
owner: user:edwin
created: 2026-07-17
updated: 2026-07-18
source: []
commit: ""
pr: ""
impacts: ["server API", "mode-1 cockpit chrome", "metadata strip", "nav/context payloads"]
issues: []
features: ["[[FEAT-0018-Verification-Health-Surface]]"]
reviewed_by: "model:claude-opus"
review_date: 2026-07-18
review_verdict: approved
related: ["[[TST-0016]]"]
---

# Verification health surface (FEAT-0018, TASK-0111..0113)

## Summary
The cockpit now surfaces the project-os verification state while browsing. New `src/project_os_cockpit/validation.py` (`ValidationRunner`) locates the browsed repo's `tools/scripts/validate-docs.py` (fallback: the new bundled verbatim copy `src/project_os_cockpit/validate_docs_bundled.py`), runs it as a stdlib subprocess, parses `ERROR [CODE]` / `WARN [CODE]` lines into structured entries (code, message, ID, repo-relative path, resolver deep-link URL), caches the report, and re-runs on docs-tree watcher events or SNAPSHOT.yaml edits (own non-recursive observer) with a ~1 s debounce. `GET /api/cockpit/validation` serves the cached report (`{ok, state: ok|failing|unavailable, errors, warnings, checked_at}`, standard `X-Cockpit-Schema`); observable state changes fan out as a new `cockpit:validation` SSE event (additive — schema stays 3). The mode-1 chrome gains a top-bar health badge (green OK / red error count / grey unavailable, existing status tokens) whose click opens a drift panel listing each violation deep-linked to the offending note; panel open-state persists and survives soft reload. Frontmatter verification metadata is promoted to chips: amber `waived` next to the status (metadata strip + list rows via additive `waived`/`review_verdict`/`adequacy` item-payload flags), green/red `review_verdict`, and a dashed amber "no evidence" marker on TST rows lacking `adequacy`/`mutation_score`. Zero new Python dependencies; no validator check is reimplemented in cockpit code.

## Provenance
This change set was authored in a shared working tree alongside the (uncommitted) PHASE-007 batch and is intentionally left uncommitted — commit/PR stamping (`commit:` / `pr:` above) is deferred to the human who lands the batch. Independent review: see `reviewed_by` / `review_verdict` frontmatter.

## Impact
- New endpoint `GET /api/cockpit/validation` + new SSE event `cockpit:validation` (documented in docs/references/COCKPIT-API.md). The contract's schema-versioning table was amended in this change to codify existing practice: SSE event *additions* are additive (clients subscribe by name; `cockpit:agent-activity` and `cockpit:dispatch-request` already shipped at schema 3), while event removals/renames/data-shape changes remain breaking — so `SCHEMA_VERSION` stays 3.
- `src/project_os_cockpit/server.py`: `ValidationRunner` wiring on `DocsServer` and `_make_handler`, endpoint route/handler.
- `src/project_os_cockpit/cockpit.py`: `_verification_flags` — additive `waived` / `review_verdict` / `adequacy` fields on nav + context item payloads.
- `src/project_os_cockpit/templates.py`: `cockpit-health-slot` header slot; metadata-strip waiver/verdict chips.
- `src/project_os_cockpit/static/{cockpit.js, cockpit.css, base.css}`: badge, drift panel, `itemBadges` chips, styles (existing palette tokens only).
- New backlog scaffolds: [[FEAT-0028-Fleet-Health-Surface]] (desktop fleet-wide validator badges) and [[FEAT-0029-Cockpit-MCP-Server]] (MCP adapter over the documented HTTP API), both parked in [[PHASE-999]].

## Documentation Coverage (All Types Considered)
- features: updated — FEAT-0018 → `in-review` with status record; new FEAT-0028 / FEAT-0029 (backlog).
- requirements: not-applicable — no requirement-level contract change; feature acceptance criteria carry the spec.
- tasks: updated — TASK-0111..0113 → `done` with per-task Verification sections.
- issues: not-applicable — no defects raised or fixed.
- tests: new — [[TST-0016]] (`tests/test_validation.py`, 9 tests, passing, mutation-run adequacy evidence); schema-header matrix extended with the new endpoint.
- workflows: not-applicable.
- decisions: not-applicable — no architectural fork; validator-as-subprocess follows the FEAT-0018 plan note.
- risks: not-applicable — no new dependency, env var, path layout, or exposure (validator subprocess is stdlib, loopback-only surface unchanged); risk-scan triggers reviewed, none apply.
- changes: new — this note.
- snapshot: updated — statuses, counters (FEAT 29, TST 16, CHG 20260717), items (FEAT-0028/0029, TST-0016), metrics deltas for this change set (PHASE-007 recount stays with that batch's close-out).

## Follow-ups
- [ ] Stamp `commit:` here once the human lands the batch (this session must not commit; see Provenance).
- [ ] Human visual pass on the mode-1 UI (badge flip on live drift, drift-panel navigation, chip fixtures) — FEAT-0018 held `in-review` until done.
- [ ] Port the health badge to the desktop (mode-3) renderer; payload + SSE are renderer-agnostic (natural first slice of [[FEAT-0028-Fleet-Health-Surface]]).
- [ ] Keep `validate_docs_bundled.py` in sync with `tools/scripts/validate-docs.py` when the canonical validator changes (consider a sync-script check).
