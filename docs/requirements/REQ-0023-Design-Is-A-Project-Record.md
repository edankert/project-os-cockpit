---
type: "[[requirement]]"
id: REQ-0023
aliases: ["REQ-0023"]
title: "A design and the reasoning behind its revisions are project records, not transcript artifacts"
status: implemented
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[DES-0001-Overview-Redesign]]"]
priority: medium
scope: "Design artifacts, their revision history, the reason for each revision, and their review verdicts live in the repo beside the features they specify, and are readable without the tool that renders them."
acceptance:
  - "A design artifact is committed under docs/designs/ beside its note, and linked from every note it specifies via `design:`"
  - "Each revision of an artifact is a git commit carrying the reason for the change, not an untracked overwrite"
  - "Annotations and review verdicts are plain Markdown in the design note, readable and diffable without the cockpit"
  - "No design state is held only in the cockpit's runtime or in an external service"
implements: "[[FEAT-0042-Design-Bench]]"
verifies: []
related: ["[[DES-0001-Overview-Redesign]]"]
tests: []
---

# Design is a project record

## Statement

A design, its revision history, the reasoning behind each revision, and its review verdicts **shall** live in the repository beside the features they specify, and **shall** remain readable without the tool that renders them.

## Rationale

The overview redesign went through six revisions in one session. The sixth is committed; the first five and every reason for changing between them exist only in a chat transcript. The design survived and the design process did not.

That is the same failure the project-os notes exist to prevent everywhere else, and [[DES-0001]] already half-solved it by committing the artifact rather than linking somebody's chat history. This requirement finishes the job: the *process* is the record, not just the output.

The clause covers the **process**, not only the comments. Two regenerated 139KB HTML files diff as a wall of noise, so the reasoning between revisions collapses to a commit subject — and git history is invisible to `validate-docs` and destroyable by a squash. Hence the revision log in the note ([[TASK-0220]]): it is the only readable, checkable record of *why* a design changed.

The "readable without the tool" clause is doing real work. If annotations lived in a cockpit database, or revisions in an external service, the record would depend on this specific application continuing to exist — which is the failure mode a link to a hosted artifact already demonstrated.

## Acceptance Criteria

- [x] A design artifact is committed under `docs/designs/` beside its note and linked via `design:` from every note it specifies — evidence: `docs/designs/overview-redesign-dossier.html` (DES-0001) and `docs/designs/DES-0002-style-guide.html`, both tracked in git beside their notes; `design:` links present on FEAT-0040, FEAT-0041, FEAT-0042 and FEAT-0043
- [~] Each revision is a commit carrying its reason, **and** appears in the note's `## Revisions` log — **mechanism delivered, not yet exercised.** `append_revision_log()` writes the log ([[TASK-0220]]) and `design_revisions_payload()` reads reasons from `git log --follow` ([[TASK-0216]]); both are tested. But no design has been through a real capture cycle yet, so **no note carries a `## Revisions` section today** — DES-0001 does not. Reconciled rather than ticked because ticking it would claim a corpus state that does not exist. Closing it is a [[PHASE-009]] exit criterion that needs Edwin: a design produced through the workflow with ≥2 revisions.
- [~] Annotations and verdicts are Markdown in the note — **mechanism delivered, not yet exercised.** `append_design_comment()`, `read_design_comments()` and `stamp_design_verdict()` write region-anchored Markdown into the note body and the review fields into its frontmatter ([[TASK-0217]], [[TASK-0218]]), all tested including the orphaned-region case. No real annotation exists in the corpus yet, for the same reason as above — it needs a human review pass.
- [x] No design state exists only in cockpit runtime or an external service — evidence: by inspection, every write path targets the note (`note_writes.py`: comments into the body, verdict/revision into frontmatter); the register, revisions and rationale are all *derived* — from `type: "[[design]]"` notes, from `git log`, and from the notes' own `implements:`/`related:` links. Nothing about a design is stored in `.cockpit/` or any service, and `git rm`-ing the runtime state directory (commit 8b88b46) did not affect any design surface

## Traceability
- Implements: [[FEAT-0042-Design-Bench]]
- Verified by: the design notes themselves, read without the cockpit running
