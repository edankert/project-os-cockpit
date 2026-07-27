---
type: "[[requirement]]"
id: REQ-0023
aliases: ["REQ-0023"]
title: "A design and the reasoning behind its revisions are project records, not transcript artifacts"
status: draft
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[REF-0001-Overview-Redesign-Dossier]]"]
priority: medium
scope: "Design artifacts, their revision history, the reason for each revision, and their review verdicts live in the repo beside the features they specify, and are readable without the tool that renders them."
acceptance:
  - "A design artifact is committed under docs/references/design/ and linked from every note it specifies via `design:`"
  - "Each revision of an artifact is a git commit carrying the reason for the change, not an untracked overwrite"
  - "Annotations and review verdicts are plain Markdown in the design note, readable and diffable without the cockpit"
  - "No design state is held only in the cockpit's runtime or in an external service"
implements: "[[FEAT-0042-Design-Bench]]"
verifies: []
related: ["[[REF-0001-Overview-Redesign-Dossier]]"]
tests: []
---

# Design is a project record

## Statement

A design, its revision history, the reasoning behind each revision, and its review verdicts **shall** live in the repository beside the features they specify, and **shall** remain readable without the tool that renders them.

## Rationale

The overview redesign went through six revisions in one session. The sixth is committed; the first five and every reason for changing between them exist only in a chat transcript. The design survived and the design process did not.

That is the same failure the project-os notes exist to prevent everywhere else, and [[REF-0001]] already half-solved it by committing the artifact rather than linking somebody's chat history. This requirement finishes the job: the *process* is the record, not just the output.

The "readable without the tool" clause is doing real work. If annotations lived in a cockpit database, or revisions in an external service, the record would depend on this specific application continuing to exist — which is the failure mode a link to a hosted artifact already demonstrated.

## Acceptance Criteria

- [ ] A design artifact is committed under `docs/references/design/` and linked via `design:` from every note it specifies — evidence: <path>
- [ ] Each revision is a commit carrying its reason — evidence: <git log>
- [ ] Annotations and verdicts are Markdown in the note — evidence: <path + the raw file>
- [ ] No design state exists only in cockpit runtime or an external service — evidence: <inspection>

## Traceability
- Implements: [[FEAT-0042-Design-Bench]]
- Verified by: the design notes themselves, read without the cockpit running
