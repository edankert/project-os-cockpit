---
type: "[[plan]]"
title: "Overview rework — delivery plan"
status: draft
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
implements: ["[[FEAT-0040-Overview-Rework]]"]
related: ["[[FEAT-0041-Review-Desk]]"]
---

# Overview rework — delivery plan

## Delivery sequence

1. **TASK-0199** — sidecar payload additions (`cockpit.py`): focus block + note date, issue severity in `_slim`, `/api/cockpit/commits`, `SCHEMA_VERSION` bump + schema-header coverage. The data pipe everything below consumes.
2. **TASK-0200** — overview stage (`renderer.ts`): focus band, mix-bar stat tiles (Requirements restored), Waiting-on-you, full-width sparkbar + commits panel; donuts and the note feed retire.
3. **TASK-0201** — phase accordion + Completed band (renderer-only; same `phases[]` payload).
4. **TASK-0202** — phase-detail rework: header fraction/gates chip, health band, next-action feature rows, exit-criteria summary + evidence chips, Remaining list, scoped-activity ID column.
5. **TASK-0203** — record column on both overview scopes; linked/backlinks demote to disclosures on the phase scope.
6. **TASK-0204** — retire the Active/Recent mode buttons (UI-only); phase-less default falls back to Overview.
7. **TASK-0212** — design-input references: in-repo dossier convention (reference-note wrappers, `design:` frontmatter links), attachment strip, Library "Design" group, Library-card ordering; seeded with the overview-redesign dossier. Queue-vs-record: this is the library half of the durable record (the ~review queue is the doorbell; FEAT-0041's TASK-0211 owns the verification half).

## Dependencies

- **Hard:** TASK-0200/0202/0203 need TASK-0199's payload fields (focus, severity, commits). TASK-0204 should land with or after TASK-0200 so the commits panel exists before Recent's button disappears.
- **Soft:** TASK-0201 is independent of the sidecar work (client-side sort/group over the existing payload). FEAT-0041's TASK-0210 decorates TASK-0200's Waiting-on-you rows — coordinate the row markup. TASK-0212's Library-card ordering lands best with or after TASK-0203; its convention half (files + wrappers + `design:` links) is independent.

## Open questions

- Weekly deltas on the stat tiles: approximate client-side from `activity.recent`, or add an exact per-type weekly count to the payload? Dossier allows either; decide in TASK-0199 vs TASK-0200.
- Exit-criteria evidence chips: client-side ID regex first, or go straight to parsing in `_exit_criteria_from_body`? Dossier recommends regex first, sidecar parse as the durable form.
