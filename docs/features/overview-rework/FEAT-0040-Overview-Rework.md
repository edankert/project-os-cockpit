---
type: "[[feature]]"
id: FEAT-0040
aliases: ["FEAT-0040"]
title: "Overview rework — state-first project & phase dashboards"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
goal: "The overview surfaces (project + phase drill-down) are rebuilt around state-before-history: a quiet-first focus band, stat tiles with status mix-bars (Requirements tile restored), a liveness-sorted phase accordion with a Completed band, a Waiting-on-you list of durable human-shaped states, full-width activity sparkbar + git-anchored commits panel, and a Decisions/Verification/Library record column in the right pane — with the Active and Recent nav-mode buttons retired."
requirements: ["[[REQ-0022-Overview-State-Above-History]]"]
tests: ["[[TST-0020-Overview-Payloads]]"]
tasks: ["[[TASK-0199]]", "[[TASK-0200]]", "[[TASK-0201]]", "[[TASK-0202]]", "[[TASK-0203]]", "[[TASK-0204]]", "[[TASK-0212]]"]
related: ["[[FEAT-0017-Overview-Dashboard]]", "[[FEAT-0023-Overview-Scopes]]", "[[FEAT-0036-Live-Work-Views]]", "[[FEAT-0038-Console-Progress-Rail]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0041-Review-Desk]]", "[[ADR-0006-Retire-Delivered-Band]]"]
design: ["[[DES-0001-Overview-Redesign]]"]
---

# Overview rework — state-first project & phase dashboards

## Why

Design review 2026-07-26 (approved dossier: https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be, plates A–D + states audit + data-source table). The current overview (FEAT-0017) and phase drill-down (FEAT-0023) spend their scarce real estate on repetition and history: the hero repeats six numbers the donuts restate, done phases shout as loudly as the live one, the one narrative feed starts below the fold, the right pane is dead space on the screen with the most state to summarise, and SNAPSHOT's `focus:` block — the single most contextual fact — appears nowhere. The dossier's states audit adds the governing constraint: this repo's work is bursty, so the overview is mostly viewed in the quiet between sessions — the durable states are the human-shaped ones (open issues, in-review stalls, ready-never-executed tests, parked items, open risks, done-but-unclosed phases), and quiet is the primary design state.

Queue-vs-record framing (Edwin, 2026-07-26, shared with FEAT-0041): the ~review queue is the doorbell; the records live on the scope pages (verification — FEAT-0041's TASK-0211) and in the library (design input — TASK-0212 here); acting on a queue row writes into a durable home. This feature owns the record side's library half: design input committed in-repo, wrapped by reference notes, and surfaced wherever the work it shaped is read.

## Scope

1. **TASK-0199 — Sidecar payload additions** (`cockpit.py`). SNAPSHOT `focus:` block in `stats_payload` (task/feature/phase/issue/note plus the note's date for a staleness label); issue `severity` added to `_slim`; new `/api/cockpit/commits` endpoint (`git log --name-only` joined to the index by `rel_path` — items per commit, completions marked by status-diffing adjacent revisions, commits touching no doc notes flagged); `SCHEMA_VERSION` bump per the FEAT-0008 rule.
2. **TASK-0200 — Overview stage rework** (`renderer.ts`). Quiet-first focus band (resting state reads last-completed + note age; live state pulses); stat tiles with status mix-bars absorbing the donuts, Requirements tile restored (`hero.requirements` is computed but never rendered today); Waiting-on-you list limited to the audit's durable states, "All clear" when empty; full-width activity sparkbar + commits panel replacing the note feed and the donuts/histogram section.
3. **TASK-0201 — Phase section rework.** Liveness-sorted accordion (any phase row expands/collapses its square strip); the active phase row carries fraction/%/in-flight/attention meta; finished phases collapse into a "Completed" band — deliberately named Completed, NOT "Delivered": ADR-0006 retired that vocabulary and `test_delivered_band_is_retired` guards it; a pure UI grouping, no new status.
4. **TASK-0202 — Phase-detail (scoped) rework.** Header gains fraction/% and a gates chip; a one-line health band replaces the repeated six-tile hero; feature rows gain fractions + a next-action second line (doing/next child, open-issue flag) and done rows collapse to one line; exit criteria get an n/m summary bar + evidence chips (ID regex over criterion text joined to live status); a Remaining-work list (not-done items in scope, sorted doing → triage → backlog); scoped activity rows regain their ID column (dropped in TASK-0173's 3-column template).
5. **TASK-0203 — Record column.** The right pane on both overview scopes becomes Decisions (ADRs) / Verification (tests, waivers, validator) / Library (references) cards — phase-scoped on drill-down (the phase's acceptance tests; ADRs whose `related:` links reach it). Replaces pinned-only (project scope) and the raw linked/backlinks dump (phase scope; those demote to collapsed disclosures, preserving the FEAT-0023 pane contract rather than deleting it).
6. **TASK-0204 — Retire the Active and Recent nav modes (UI-only).** Remove the two mode buttons; phase-less projects' default mode falls back from Active to Overview (the Now board shows the same data); `nav?mode=active` and `mode=recent` stay server-side per the FEAT-0008 API stability rule. Partially supersedes FEAT-0036's Active-mode UI — FEAT-0036 stays done and records the supersession.
7. **TASK-0212 — Design-input references (convention + surfaces).** Design input becomes first-class using only existing machinery: dossiers committed under `docs/references/design/`, each wrapped by a reference note (existing type), linked from FEAT/phase frontmatter via a `design:` link field; surfaced as an attachment strip on note renders, a "Design" group in Library mode, and design inputs listed first in the record column's Library card. Seeded with the overview-redesign dossier itself; the convention is an upstreamable follow-up for the project-os template.

## Out of scope

- Any new status vocabulary or palette band (ADR-0006 guard stays green); no new colors beyond the four mix-bar steps derived from existing tokens (REQ-0012).
- Server-side removal or change of `nav?mode=active` / `mode=recent` payloads (FEAT-0008 stability rule; the Now board and strip work tab keep consuming them).
- The ~review surfaces — that is FEAT-0041; the only coupling is the Waiting-on-you rows it decorates (TASK-0210 over there).
- Right-pane Option B (collapse-by-default) and Option C (commits in the right pane) — the dossier evaluated three options; Option A (record column) is the approved choice.

## Upstream follow-up (recorded, not executed here)

The **design-input convention** from TASK-0212 is template-shaped, not cockpit-shaped: a `docs/references/design/` directory, reference-note wrappers, and a `design:` link field cost nothing to adopt and give every project-os repo a durable home for the thinking behind a feature. Three pieces belong upstream in `~/Dev/repos/project-os/`: the directory in the scaffold, `design` in the documented link-bearing frontmatter fields (TRACEABILITY.md), and a line in the feature/phase templates. The cockpit-side surfaces (attachment strip, Library group, record-column ordering) stay here — they are renderer features, not documentation rules. Nothing template-owned was edited in this repo; adopting it downstream is a `sync-project-os.sh` away once upstream carries it.

## Acceptance

- REQ-0022's criteria hold: state-only above the fold at 900 px, Requirements tile rendered, quiet state fully designed, history never above state.
- The phase accordion expands/collapses any row; done phases render one line each under a Completed band; the active phase carries fraction, %, and in-flight/attention meta.
- The phase drill-down answers how-far/what-gates/what's-left/what's-next without opening notes (header fraction + gates chip, health band, next-action rows, exit-criteria n/m + evidence chips, Remaining list).
- `/api/cockpit/commits` returns commit rows joined to index items with completions marked and no-doc-item commits flagged; all JSON endpoints carry the bumped `X-Cockpit-Schema`.
- With the Active/Recent buttons gone, a phase-less project lands on Overview and the mode strip shows six modes; `curl` of `nav?mode=active` and `mode=recent` still returns their payloads.
- Design-input references resolve end-to-end: the committed overview-redesign dossier is reachable from FEAT-0040/FEAT-0041/PHASE-008 `design:` links, appears in the note-render attachment strip, the Library "Design" group, and first in the record column's Library card.

## Impact analysis (2026-07-26, preflight)

- **FEAT-0017 / FEAT-0023 (both done):** their surfaces are reworked in place; the features stay done and are not reopened — this feature is the successor of record for those surfaces. FEAT-0023's select→detail→context pane contract is preserved: scope selection and centre dashboards are untouched, and the phase-scope right pane demotes linked/backlinks to disclosures rather than removing them.
- **REQ-0013 (cockpit layout):** its right-pane outbound/inbound-only contract governs the *active-note* right pane, which this feature does not touch; overview scopes were already contract-adjusted by FEAT-0023. No conflict; noted so the record column is not read as violating REQ-0013.
- **FEAT-0036 (live work views):** partial UI supersession — the Active mode *button* and phase-less default retire (TASK-0204); the status-diff layer (TASK-0162), strip work tab (TASK-0163), and Now board (TASK-0165) remain consumers of the same data. Recorded in FEAT-0036's note; feature stays done.
- **FEAT-0038 (progress rail):** absorbs Active's live-work job at the console; no contract change — related link only.
- **FEAT-0008 (API hardening):** compliance dependency, not a conflict — additive payload fields and the new commits endpoint require a `SCHEMA_VERSION` bump and schema-header coverage (TST-0006 pattern).
- **ADR-0006 / TST-0019:** the Completed band is a UI grouping, not vocabulary; `test_delivered_band_is_retired` and the parity test constrain naming and palette — by design, no conflict.
- **REQ-0012 (visual style):** mix-bars and accordion reuse existing tokens; no new semantic colors. No conflict.
- No contradicting requirement found among REQ-0001..REQ-0021 (REQ-0015's SNAPSHOT-driven home is strengthened by the focus band, not weakened).

## Risk scan (2026-07-26, preflight; resolution folded into DoDs per Edwin's decision)

`/api/cockpit/commits` shells out to `git log` from the sidecar — new subprocess surface on a request path and a mild information surface on the 0.0.0.0-bound render port (commit messages were not previously served). Per Edwin's 2026-07-26 decision no separate RISK note is filed; the hardening is part of TASK-0199's DoD: fixed argv (no client-controlled arguments reach git), output escaped like all rendered content, bounded subprocess with graceful non-repo fallback, and the explicit note that the render server binds 0.0.0.0 by design (tablet viewing) so the endpoint exposes only what the served notes already expose — assessed against the existing RISK-0001 (bind-surface) and RISK-0004 (untrusted-input) threat models. No new dependency, env var, or path change otherwise — negative result recorded.
