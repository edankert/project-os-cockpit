---
type: "[[requirement]]"
id: REQ-0023
aliases: ["REQ-0023"]
title: "A design and the reasoning behind its revisions are project records, not transcript artifacts"
status: implemented
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-09-12
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
- [x] Each revision is a commit carrying its reason, **and** appears in the note's `## Revisions` log — **exercised 2026-07-28**, through `POST /api/design/capture`, not by hand. Two revisions of `DES-0002-style-guide.html`: `ad7d737` ("Read tokens declared inside @media, @supports and @layer…") and `b977783` ("Scan status and severity tokens for shell overrides too…"). Each commit contains **both** the artifact and the note's log entry, which is the property [[TASK-0220]] exists to hold — a log that can drift from git is worse than no log. The log reads newest-last and carries no sha, deliberately: an entry cannot name the commit that contains it.

- [x] Annotations and verdicts are Markdown in the note — **both halves exercised 2026-07-28.** *Verdict*: Edwin reviewed [[DES-0002]] through the desk and accepted it, writing `reviewed_by: user:edwin`, `review_date`, `review_verdict: accepted` and `design_revision: 6eb6888` into the frontmatter. *Annotation*: a document-lane comment via `POST /api/design/comment`, rendered in the note's `## Review` section as `- **(document)** · date · author — text`. Both are plain Markdown in the note and readable with the tool closed, which is this requirement's whole point.

- [x] No design state exists only in cockpit runtime or an external service — evidence: by inspection, every write path targets the note (`note_writes.py`: comments into the body, verdict/revision into frontmatter); the register, revisions and rationale are all *derived* — from `type: "[[design]]"` notes, from `git log`, and from the notes' own `implements:`/`related:` links. Nothing about a design is stored in `.cockpit/` or any service, and `git rm`-ing the runtime state directory (commit 8b88b46) did not affect any design surface

## Traceability
- Implements: [[FEAT-0042-Design-Bench]]
- Verified by: the design notes themselves, read without the cockpit running

## Checked against the bench's removal (2026-09-12)

[[FEAT-0042-Design-Bench]] is `superseded` by [[FEAT-0148-One-HTML-Viewer]], and the surface this requirement's evidence was gathered on no longer exists. **This requirement is not superseded, and all four criteria still hold** — two of them hold better. Checked one by one, which is the point of writing them as things a person can check:

1. **A design artifact beside its note, linked from what it specifies.** Holds, and is now the *exception* rather than the rule: most designs are pictures in the note, in `__attachments__/` beside it ([[REQ-0065-A-Design-Is-Markdown-First]]). Either way the design is a file in the repo next to the note that explains it.
2. **Each revision is a commit carrying its reason, and appears in the note's `## Revisions` log.** Holds. `POST /api/design/capture` wrote those entries and is gone; the log is Markdown in the note and an agent or a person appends it, which is how `your-health` DES-0002's tenth entry was written on 2026-09-12.
3. **Annotations and verdicts are Markdown in the note.** Holds, and holds *better*: the sixteen comments already written stay where they are, and the verdict is now the same Accept/Decline every other note type uses, writing the same frontmatter. What went is the anchoring UI, not the record.
4. **No design state exists only in cockpit runtime or an external service.** Holds, and holds better: five write endpoints were removed and nothing replaced them. There is less runtime to hide state in than when this was written.

This requirement is the clause that made the removal safe to do. A reader who wants to know why the bench could go without losing the record is reading it.
