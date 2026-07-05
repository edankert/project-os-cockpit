---
type: "[[task]]"
id: TASK-0113
aliases: ["TASK-0113"]
title: "Waiver/review-verdict badges + adequacy surfacing in note and index views"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "FEAT-0018"
---

# Waiver / review-verdict / adequacy badges

## Definition of Done
- [ ] Notes with non-empty `verification_waiver` frontmatter show an amber "waived" chip next to the status, in both the metadata strip and list/index rows — a waived terminal status must be visually distinct from a verified one.
- [ ] `review_verdict` renders as a chip: green for `approved`, red for `changes-requested`; `reviewed_by`/`review_date` stay in the generic metadata strip (already rendered — no work needed there).
- [ ] Test views distinguish TST notes with adequacy evidence (`adequacy` or `mutation_score` non-empty) from those without, so unguarded "guarding" tests stand out.
- [ ] Frontmatter-driven only; no server-side schema changes required.

## Notes
- The metadata strip already renders unknown non-empty frontmatter keys generically (`PRIMARY_META_KEYS` then remainder), so this task is about promotion to badges/chips, not about making the fields visible at all.
