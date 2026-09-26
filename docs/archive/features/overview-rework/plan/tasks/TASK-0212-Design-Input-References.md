---
type: "[[task]]"
id: TASK-0212
aliases: ["TASK-0212"]
title: "Design-input references — convention + surfaces: in-repo dossiers wrapped by reference notes, design: frontmatter links, attachment strip, Library Design group"
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
blocks: []
related: ["[[TASK-0203]]", "[[TASK-0031]]", "[[TASK-0019]]", "[[FEAT-0011-Native-Center-Pane]]", "[[FEAT-0041-Review-Desk]]"]
tests: []
---

# Design-input references — convention + surfaces

## Definition of Done

- [x] Convention documented and applied using ONLY existing machinery: design artifacts (dossiers, mockups) are committed in-repo under `docs/references/design/`, each wrapped by a reference note (the existing `[[reference]]` type — no new note types), and linked from FEAT/phase frontmatter via a `design:` link field.
- [x] The index treats `design:` as a curated link-bearing frontmatter field (TASK-0031 pattern), so the links resolve, backlinks flow, and the wrapped artifacts are reachable from the graph.
- [x] Surfaces: an attachment strip at the top of a note render when `design:` links exist; a "Design" group in Library mode; the record column's Library card (TASK-0203) lists design inputs first.
- [x] Seed content (executed at implementation time): the overview-redesign dossier itself — the source HTML from the 2026-07-26 design session is committed under `docs/references/design/`, wrapped by a reference note, and linked via `design:` from FEAT-0040, FEAT-0041, and PHASE-008.
- [x] Upstream follow-up recorded, not executed here: the convention (directory, reference-wrapper, `design:` field, surfaces) is upstreamable to the project-os template and valuable to all nine downstream repos — template-owned files stay untouched in this repo.

## Steps

- [x] Write the convention into the reference-note wrapper pattern (`docs/references/design/README` or the wrapping notes themselves) and add `design:` to the index's curated link fields.
- [x] Commit the dossier HTML + wrapping reference note; add the `design:` links to FEAT-0040/FEAT-0041/PHASE-008.
- [x] Renderer: attachment strip on note renders with `design:` links; Library "Design" group; Library-card ordering in the record column.
- [x] Record the upstream follow-up (template change request in ~/Dev/repos/project-os) and link it here when it has an upstream ID.

## Notes

This is founding ask #2 of the review desk discussion (Edwin, 2026-07-26): design input for the project must stay visible and never be lost. Today the dossier lives at an artifact URL (https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be) — live, but not repo-durable; committing the HTML with a reference wrapper makes the record survive independently of the artifact host. Queue-vs-record rule: proposals in the ~review queue may *carry* attachments transiently; this convention is where design input *lives* — the library, on the record.
