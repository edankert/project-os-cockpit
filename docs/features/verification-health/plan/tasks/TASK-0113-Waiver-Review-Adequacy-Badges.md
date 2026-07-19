---
type: "[[task]]"
id: TASK-0113
aliases: ["TASK-0113"]
title: "Waiver/review-verdict badges + adequacy surfacing in note and index views"
status: done
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-17
parent: "FEAT-0018"
tests: ["[[TST-0016]]"]
---

# Waiver / review-verdict / adequacy badges

## Definition of Done
- [x] Notes with non-empty `verification_waiver` frontmatter show an amber "waived" chip next to the status, in both the metadata strip and list/index rows — a waived terminal status must be visually distinct from a verified one.
- [x] `review_verdict` renders as a chip: green for `approved`, red for `changes-requested`; `reviewed_by`/`review_date` stay in the generic metadata strip (already rendered — no work needed there).
- [x] Test views distinguish TST notes with adequacy evidence (`adequacy` or `mutation_score` non-empty) from those without, so unguarded "guarding" tests stand out.
- [x] Frontmatter-driven only; no server-side schema changes required.

## Notes
- The metadata strip already renders unknown non-empty frontmatter keys generically (`PRIMARY_META_KEYS` then remainder), so this task is about promotion to badges/chips, not about making the fields visible at all.

## Verification (2026-07-17)
- Metadata strip (templates.py): amber `waiver-chip` appended next to the status chip when `verification_waiver` is non-empty, the waiver row keeps its reason text behind the chip, and `review_verdict` renders as a green/red `verdict-chip` (`data-verdict` CSS). List rows: additive `waived` / `review_verdict` / `adequacy` flags from `cockpit.py _verification_flags` ride every nav/context item payload (schema-compatible per COCKPIT-API.md — additive fields, no bump) and render via `itemBadges` in `static/cockpit.js`; TST rows without adequacy evidence get a dashed amber "no evidence" chip. Chip styles live in `static/base.css` using the existing `--warn-*` and status tokens.
- Flag emission covered by [[TST-0016]] (`test_validation_flags_on_nav_items`: waived/verdict on features, adequacy true/false on TST items); against this repo's live nav payload all 15 TST items carry `adequacy: false` (none record evidence yet — the intended standout). Visual pass pending human review with the parent feature.
