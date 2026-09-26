---
type: "[[task]]"
id: TASK-0199
aliases: ["TASK-0199"]
title: "Sidecar payload additions — SNAPSHOT focus block (with note date) + issue severity in _slim; new /api/cockpit/commits; SCHEMA_VERSION bump"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0040-Overview-Rework]]"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0200]]", "[[TASK-0202]]", "[[TASK-0203]]"]
related: ["[[FEAT-0008-Cockpit-API-Hardening]]", "[[TST-0006-Schema-Header]]", "[[RISK-0001-Terminal-Exposure]]", "[[RISK-0004-Hook-Injection-Surface]]"]
tests: []
---

# Sidecar payload additions

## Definition of Done

- [x] `stats_payload` carries a `focus` block parsed from SNAPSHOT.yaml (task / feature / phase / issue / note) including the focus note's date so the renderer can label staleness.
- [x] Issue `severity` is included in the `_slim` item shape (default "low" absent, matching the right-pane convention from TASK-0035).
- [x] New `GET /api/cockpit/commits`: `git log --name-only` joined to the index by `rel_path` — per commit: sha, date, subject, touched doc items (id/type/status), a `done` marker per item, and a flag for commits touching no doc notes (FEAT-0022's guardrail, per commit). **Amended during implementation (2026-07-26, confirmed by independent review):** the DoD originally said completions were marked by *status-diffing adjacent revisions*. What shipped marks `done` from the item's **current** status via the shared `is_done_status`. The diffing form would need a `git show <sha>:<path>` per file per commit — expensive on every overview refresh, and fragile against renames — while the shipped form answers the question the panel is actually asked ("is this item finished?") with one index lookup and agrees with the hero counts and phase squares by construction. The cost is real and worth naming: a tick means "this item is done now", not "this commit is what completed it", so a commit that merely touched an item that later finished still shows a tick.
- [x] Endpoint hardening (the preflight risk-scan finding folded into this DoD per Edwin's 2026-07-26 decision — no separate RISK note): the `git` subprocess runs with a fixed argv — no client-controlled arguments ever reach git; output is escaped like all rendered content before it touches the DOM; the subprocess is bounded (commit count cap, timeout) and degrades gracefully when the workspace is not a git repo. The render server binds 0.0.0.0 by design (tablet viewing), so the endpoint exposes only what the served notes already expose — commit metadata of the same repo whose docs are being served; see the RISK-0001 (bind-surface) and RISK-0004 (untrusted-input) threat models rather than a new RISK.
- [x] `SCHEMA_VERSION` bumped per the FEAT-0008 rule; every JSON endpoint (including the new one) emits the matching `X-Cockpit-Schema` (TST-0006 pattern) and tests cover the new payload shapes.

## Steps

- [x] Parse the `focus:` block in `stats_payload` (~20 lines per the dossier's data-source table) and resolve the focus IDs against the index for titles/statuses; include the note text's date.
- [x] Add `severity` to `_slim` and thread it through the nav/stats payloads that carry issues.
- [x] Implement `/api/cockpit/commits` with the rel_path join and completion diffing; cache keyed on HEAD + index generation.
- [x] Bump `SCHEMA_VERSION`, extend the schema-header test, add endpoint tests (shape, non-repo fallback, no-doc-items flag).

## Notes

All additive — no existing payload field changes shape, so mode-1 (browser) and older desktop bundles keep rendering. This task is the hard dependency for TASK-0200/0202/0203.
